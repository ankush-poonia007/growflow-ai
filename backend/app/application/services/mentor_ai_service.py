"""
GrowFlow — Mentor AI Application Service (M09 & M36).

Provides scoped AI supervision capabilities:
- M09: Group AI Mentor strictly scoped to a single supervised Group.
- M36: Mentor AI strictly scoped to the Mentor's authorized portfolio.

Adheres strictly to the architectural constraints:
- Pre-model scope enforcement: only authorized context is compiled.
- Reuses existing AIProviderGateway.
- NEVER fabricates fake assistant text when keys are missing or provider fails.
- Zero silent operational mutations.
- Emits canonical domain events into transactional outbox.
"""

from __future__ import annotations

from datetime import UTC, datetime
import json
from typing import TYPE_CHECKING, Any
import uuid

from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.shared.events.domain_event import DomainEventType, EventVisibility
from backend.app.shared.exceptions import (
    AuthorizationException,
    NotFoundException,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.repositories.execution_repository import (
        DocumentRepository,
        MilestoneRepository,
        RiskRepository,
        TaskRepository,
    )
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository
    from backend.app.infrastructure.repositories.workspace_extension_repositories import (
        HelpRequestRepository,
    )

logger = get_logger("growflow.application.mentor_ai_service")


class MentorAIService:
    """Service managing Group AI Mentor (M09) and Mentor Portfolio AI (M36)."""

    def __init__(
        self,
        group_repo: GroupRepository,
        project_repo: ProjectRepository,
        task_repo: TaskRepository,
        milestone_repo: MilestoneRepository,
        risk_repo: RiskRepository,
        help_request_repo: HelpRequestRepository,
        outbox_service: OutboxService,
        document_repo: DocumentRepository | None = None,
        ai_gateway: AIProviderGateway | None = None,
    ) -> None:
        self._group_repo = group_repo
        self._project_repo = project_repo
        self._task_repo = task_repo
        self._milestone_repo = milestone_repo
        self._risk_repo = risk_repo
        self._help_request_repo = help_request_repo
        self._outbox_service = outbox_service
        self._document_repo = document_repo
        self._ai_gateway = ai_gateway or AIProviderGateway()

    async def _verify_group_supervision(
        self, group_id: uuid.UUID | str, current_user: CurrentUser
    ) -> Any:
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundException("Group not found.", code="GROUP_NOT_FOUND")

        if not current_user.is_admin:
            if not current_user.is_mentor or str(group.mentor_id) != str(current_user.user_id):
                raise AuthorizationException(
                    "Access denied. You do not supervise this group.",
                    code="AUTH_FORBIDDEN_RESOURCE",
                )
        return group

    async def get_group_ai_status(
        self, group_id: uuid.UUID | str, current_user: CurrentUser
    ) -> dict[str, Any]:
        group = await self._verify_group_supervision(group_id, current_user)
        return {
            "group_id": str(group.id),
            "group_name": group.name,
            "scope": "GROUP",
            "ai_available": self._ai_gateway.has_live_keys,
        }

    async def chat_group(
        self,
        group_id: uuid.UUID | str,
        current_user: CurrentUser,
        message: str,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        M09: Group AI Mentor consultation.
        Strictly scoped to a single group's context.
        """
        group = await self._verify_group_supervision(group_id, current_user)
        now_str = datetime.now(UTC).isoformat()

        # Build authorized group context BEFORE model invocation
        members = await self._group_repo.list_group_members(group.id)
        projects = await self._project_repo.list_by_group(group.id)

        student_summaries = [
            f"- {u.full_name or u.email} (Status: {m.status})"
            for m, u in members
        ]

        project_summaries = []
        for p in projects:
            tasks = await self._task_repo.list_by_project(p.id)
            milestones = await self._milestone_repo.list_by_project(p.id)
            risks = await self._risk_repo.list_by_project(p.id)
            help_reqs = await self._help_request_repo.list_by_project(p.id)

            project_summaries.append(
                f"Project '{p.name}': Phase={p.current_phase}, Health={p.health}, "
                f"Progress={p.progress_percentage}%, Tasks={len(tasks)}, "
                f"Milestones={len(milestones)}, Risks={len(risks)}, "
                f"Open Help Requests={len([h for h in help_reqs if h.status != 'RESOLVED'])}"
            )

        context_block = (
            f"Cohort Group: {group.name}\n"
            f"Join Code: {group.join_code}\n"
            f"Group Status: {group.status}\n"
            f"Enrolled Students ({len(student_summaries)}):\n"
            + ("\n".join(student_summaries) if student_summaries else "  None")
            + f"\nLinked Projects ({len(project_summaries)}):\n"
            + ("\n".join(project_summaries) if project_summaries else "  None")
        )

        system_prompt = (
            f"You are the GrowFlow AI Mentor assisting a mentor with their supervised cohort.\n"
            f"SCOPE: STRICTLY LIMITED TO THE SPECIFIED GROUP ONLY.\n\n"
            f"Authorized Group Context:\n"
            f"{context_block}\n\n"
            f"Guidelines:\n"
            f"1. You only have authority to supervise and discuss the students and projects in this cohort.\n"
            f"2. Never mention or infer information about other groups, mentors, or external projects.\n"
            f"3. Provide analytical, pedagogical, and actionable supervision insights for the mentor.\n"
            f"4. You are an advisory intelligence tool; you do not directly mutate project or group records."
        )

        # Truthful check for AI provider availability
        if not self._ai_gateway.has_live_keys:
            assistant_content = (
                "Group AI Mentor service is currently offline or not configured. "
                "OpenRouter provider keys are missing from server configuration. "
                "Please configure valid OPENROUTER_API_KEY credentials to enable live consultations."
            )
            sources: list[dict[str, Any]] = []
            ai_available = False
        else:
            prompt_content = message.strip()
            if history:
                history_text = "\n".join(
                    f"{h.get('role', 'user')}: {h.get('content', '')}"
                    for h in history[-6:]
                )
                prompt_content = f"Recent conversation:\n{history_text}\n\nUser: {prompt_content}"

            llm_response = await self._ai_gateway.execute_prompt(
                prompt=prompt_content,
                system_prompt=system_prompt,
                temperature=0.2,
            )

            if not llm_response:
                assistant_content = (
                    "AI Mentor provider reached a connection timeout or rate limit error. "
                    "Please try sending your message again shortly."
                )
                sources = []
            else:
                assistant_content = llm_response
                sources = [
                    {"title": f"Cohort: {group.name}", "section": "Supervised Roster & Projects"},
                ]
            ai_available = True

        # Enqueue canonical domain event into transactional outbox
        msg_id = uuid.uuid4()
        await self._outbox_service.enqueue(
            event_type=DomainEventType.AI_MENTOR_MESSAGE_SENT,
            actor_role=current_user.role,
            resource_type="GroupAIMessage",
            resource_id=str(msg_id),
            actor_id=current_user.user_id,
            group_id=group.id,
            visibility=EventVisibility.MENTOR.value,
            metadata={
                "group_id": str(group.id),
                "scope": "GROUP",
                "ai_available": ai_available,
            },
        )

        return {
            "group_id": str(group.id),
            "group_name": group.name,
            "scope": "GROUP",
            "user_message": {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": message.strip(),
                "created_at": now_str,
            },
            "assistant_message": {
                "id": str(msg_id),
                "role": "assistant",
                "content": assistant_content,
                "sources": sources,
                "created_at": now_str,
            },
            "ai_available": ai_available,
        }

    async def get_mentor_ai_status(
        self, current_user: CurrentUser
    ) -> dict[str, Any]:
        if not current_user.is_mentor and not current_user.is_admin:
            raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")

        return {
            "scope": "PORTFOLIO",
            "mentor_id": str(current_user.user_id),
            "ai_available": self._ai_gateway.has_live_keys,
        }

    async def chat_mentor(
        self,
        current_user: CurrentUser,
        message: str,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        M36: Mentor Portfolio AI consultation.
        Strictly scoped to the mentor's authorized portfolio of groups and projects.
        """
        if not current_user.is_mentor and not current_user.is_admin:
            raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")

        now_str = datetime.now(UTC).isoformat()

        # Build mentor's authorized portfolio context BEFORE model invocation
        mentor_groups = await self._group_repo.list_by_mentor(current_user.user_id)
        group_ids = [g.id for g in mentor_groups]

        group_summaries = []
        for g in mentor_groups:
            members = await self._group_repo.list_group_members(g.id)
            group_summaries.append(f"- Cohort '{g.name}' (Code: {g.join_code}, Enrolled: {len(members)})")

        if group_ids:
            records = await self._project_repo.list_supervised_projects(group_ids)
            project_summaries = [
                f"- Project '{p.name}' (Student: {u.full_name or u.email}, Phase: {p.current_phase}, Health: {p.health}, Progress: {p.progress_percentage}%)"
                for p, u, grp, pdef, pver in records
            ]
            at_risk_count = len([p for p, u, grp, pdef, pver in records if p.health in ("WARNING", "CRITICAL", "AT_RISK")])
        else:
            project_summaries = []
            at_risk_count = 0

        context_block = (
            f"Supervised Cohorts ({len(mentor_groups)}):\n"
            + ("\n".join(group_summaries) if group_summaries else "  None")
            + f"\n\nSupervised Projects ({len(project_summaries)} total, {at_risk_count} at risk):\n"
            + ("\n".join(project_summaries) if project_summaries else "  None")
        )

        system_prompt = (
            f"You are the GrowFlow AI Mentor assisting a mentor with their entire supervised portfolio.\n"
            f"SCOPE: STRICTLY LIMITED TO THIS MENTOR'S AUTHORIZED PORTFOLIO ONLY.\n\n"
            f"Authorized Portfolio Context:\n"
            f"{context_block}\n\n"
            f"Guidelines:\n"
            f"1. You only have access to cohorts and projects supervised by this mentor.\n"
            f"2. Never mention or leak data belonging to other mentors or unauthorized groups.\n"
            f"3. Provide strategic portfolio supervision insights, identifying at-risk projects and progress trends.\n"
            f"4. You are an advisory intelligence tool; you do not directly mutate database records."
        )

        # Truthful check for AI provider availability
        if not self._ai_gateway.has_live_keys:
            assistant_content = (
                "Mentor AI service is currently offline or not configured. "
                "OpenRouter provider keys are missing from server configuration. "
                "Please configure valid OPENROUTER_API_KEY credentials to enable live consultations."
            )
            sources: list[dict[str, Any]] = []
            ai_available = False
        else:
            prompt_content = message.strip()
            if history:
                history_text = "\n".join(
                    f"{h.get('role', 'user')}: {h.get('content', '')}"
                    for h in history[-6:]
                )
                prompt_content = f"Recent conversation:\n{history_text}\n\nUser: {prompt_content}"

            llm_response = await self._ai_gateway.execute_prompt(
                prompt=prompt_content,
                system_prompt=system_prompt,
                temperature=0.2,
            )

            if not llm_response:
                assistant_content = (
                    "AI Mentor provider reached a connection timeout or rate limit error. "
                    "Please try sending your message again shortly."
                )
                sources = []
            else:
                assistant_content = llm_response
                sources = [
                    {"title": "Mentor Portfolio Directory", "section": "Supervised Cohorts & Projects"},
                ]
            ai_available = True

        # Enqueue canonical domain event into transactional outbox
        msg_id = uuid.uuid4()
        await self._outbox_service.enqueue(
            event_type=DomainEventType.AI_MENTOR_MESSAGE_SENT,
            actor_role=current_user.role,
            resource_type="MentorPortfolioAIMessage",
            resource_id=str(msg_id),
            actor_id=current_user.user_id,
            visibility=EventVisibility.MENTOR.value,
            metadata={
                "scope": "PORTFOLIO",
                "mentor_id": str(current_user.user_id),
                "ai_available": ai_available,
            },
        )

        return {
            "scope": "PORTFOLIO",
            "mentor_id": str(current_user.user_id),
            "user_message": {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": message.strip(),
                "created_at": now_str,
            },
            "assistant_message": {
                "id": str(msg_id),
                "role": "assistant",
                "content": assistant_content,
                "sources": sources,
                "created_at": now_str,
            },
            "ai_available": ai_available,
        }
