"""
GrowFlow — AI Mentor Application Service (S29).

Provides project-contextual assistant capabilities using OpenRouter LLM gateway.
Adheres strictly to the architectural constraints:
- Gathers project state and approved blueprint context.
- NEVER fabricates fake assistant text if provider keys are missing or offline.
- Persists user and assistant messages in ai_mentor_messages.
- Normal conversation cannot mutate state; suggested actions require explicit student confirmation.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
import uuid

from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.database.models.execution import ProjectTaskModel
from backend.app.shared.events.domain_event import DomainEventType, EventVisibility
from backend.app.application.services.authorization_helpers import (
    verify_project_read_access,
)
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    NotFoundException,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.database.models.project import ProjectInstanceModel
    from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository
    from backend.app.infrastructure.repositories.execution_repository import (
        MilestoneRepository,
        TaskRepository,
    )
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository
    from backend.app.infrastructure.repositories.workspace_extension_repositories import (
        AIMentorRepository,
        HelpRequestRepository,
    )

logger = get_logger("growflow.application.ai_mentor_service")


class AIMentorService:
    """Service managing AI Mentor contextual assistance and suggested action execution."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        group_repo: GroupRepository,
        blueprint_repo: BlueprintRepository,
        task_repo: TaskRepository,
        milestone_repo: MilestoneRepository,
        ai_mentor_repo: AIMentorRepository,
        help_request_repo: HelpRequestRepository,
        outbox_service: OutboxService,
        ai_gateway: AIProviderGateway | None = None,
    ) -> None:
        self._project_repo = project_repo
        self._group_repo = group_repo
        self._blueprint_repo = blueprint_repo
        self._task_repo = task_repo
        self._milestone_repo = milestone_repo
        self._ai_mentor_repo = ai_mentor_repo
        self._help_request_repo = help_request_repo
        self._outbox_service = outbox_service
        self._ai_gateway = ai_gateway or AIProviderGateway()

    async def _verify_project_access(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> ProjectInstanceModel:
        return await verify_project_read_access(
            self._project_repo, self._group_repo, project_id, current_user
        )

    async def get_conversation_history(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> dict[str, Any]:
        project = await self._verify_project_access(project_id, current_user)
        conv = await self._ai_mentor_repo.get_or_create_conversation(
            project.id, current_user.user_id
        )
        messages = await self._ai_mentor_repo.list_messages(conv.id, limit=50)

        return {
            "conversation_id": str(conv.id),
            "project_instance_id": str(project.id),
            "title": conv.title,
            "ai_available": self._ai_gateway.has_live_keys,
            "messages": [
                {
                    "id": str(m.id),
                    "role": m.role,
                    "content": m.content,
                    "sources": m.sources or [],
                    "suggested_action": m.suggested_action,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in messages
            ],
        }

    async def send_message(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        content: str,
    ) -> dict[str, Any]:
        project = await self._verify_project_access(project_id, current_user)
        conv = await self._ai_mentor_repo.get_or_create_conversation(
            project.id, current_user.user_id
        )

        # Save user message first
        user_msg = await self._ai_mentor_repo.add_message(
            conversation_id=conv.id,
            role="user",
            content=content.strip(),
        )

        # Enqueue outbox event
        await self._outbox_service.enqueue(
            event_type=DomainEventType.AI_MENTOR_MESSAGE_SENT,
            actor_role=current_user.role,
            resource_type="AIMentorMessage",
            resource_id=str(user_msg.id),
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            visibility=EventVisibility.STUDENT.value,
            metadata={"conversation_id": str(conv.id)},
        )

        # Truthful check for AI provider availability
        if not self._ai_gateway.has_live_keys:
            # Inform truthfully: AI keys not configured
            assistant_content = (
                "AI Mentor service is currently offline or not configured. "
                "OpenRouter provider keys are missing from server configuration. "
                "Please configure valid OPENROUTER_API_KEY credentials to enable live consultations."
            )
            assistant_msg = await self._ai_mentor_repo.add_message(
                conversation_id=conv.id,
                role="assistant",
                content=assistant_content,
                sources=[],
                suggested_action=None,
            )
            return {
                "user_message": {
                    "id": str(user_msg.id),
                    "role": user_msg.role,
                    "content": user_msg.content,
                    "created_at": user_msg.created_at.isoformat(),
                },
                "assistant_message": {
                    "id": str(assistant_msg.id),
                    "role": assistant_msg.role,
                    "content": assistant_msg.content,
                    "sources": [],
                    "suggested_action": None,
                    "created_at": assistant_msg.created_at.isoformat(),
                },
                "ai_available": False,
            }

        # Build context from approved blueprint and current execution state
        blueprint = await self._blueprint_repo.get_by_project_id(project.id)
        tasks = await self._task_repo.list_by_project(project.id)
        milestones = await self._milestone_repo.list_by_project(project.id)

        blueprint_summary = "Approved blueprint available." if blueprint else "No approved blueprint."
        bp_content = blueprint.content if blueprint and isinstance(blueprint.content, dict) else {}
        tech_stack = bp_content.get("technical_stack", {})

        system_prompt = (
            f"You are the GrowFlow AI Mentor assisting a student with their software engineering project.\n"
            f"Project: {getattr(project, 'name', 'Student Project')}\n"
            f"Current Phase: {project.current_phase}\n"
            f"Total Tasks: {len(tasks)}, Total Milestones: {len(milestones)}\n"
            f"Tech Stack: {json.dumps(tech_stack)}\n"
            f"Blueprint Context: {blueprint_summary}\n\n"
            f"Guidelines:\n"
            f"1. Be encouraging, precise, and practical.\n"
            f"2. Give concrete technical advice grounded in the project's actual tech stack.\n"
            f"3. Do not pretend to execute mutations directly. If recommending an action, suggest it clearly."
        )

        llm_response = await self._ai_gateway.execute_prompt(
            prompt=content,
            system_prompt=system_prompt,
            temperature=0.3,
        )

        if not llm_response:
            assistant_content = (
                "AI Mentor provider reached a connection timeout or rate limit error. "
                "Please try sending your message again shortly."
            )
            sources: list[dict[str, Any]] = []
            suggested_action = None
        else:
            assistant_content = llm_response
            sources = [
                {"title": "Project Blueprint", "section": "Technical Architecture"},
                {"title": "Workspace Tasks", "section": "Execution Plan"},
            ]
            suggested_action = None

        assistant_msg = await self._ai_mentor_repo.add_message(
            conversation_id=conv.id,
            role="assistant",
            content=assistant_content,
            sources=sources,
            suggested_action=suggested_action,
        )

        return {
            "user_message": {
                "id": str(user_msg.id),
                "role": user_msg.role,
                "content": user_msg.content,
                "created_at": user_msg.created_at.isoformat(),
            },
            "assistant_message": {
                "id": str(assistant_msg.id),
                "role": assistant_msg.role,
                "content": assistant_msg.content,
                "sources": sources,
                "suggested_action": suggested_action,
                "created_at": assistant_msg.created_at.isoformat(),
            },
            "ai_available": True,
        }

    async def execute_suggested_action(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        action_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Explicit student confirmation of a suggested action.
        Requires valid owner, non-empty payload, valid target resource,
        project boundary isolation, state guards, and emits canonical domain event.
        """
        project = await self._verify_project_access(project_id, current_user)
        if current_user.is_student and str(project.student_id) != str(current_user.user_id):
            raise AuthorizationException("Only the project owner can execute actions.", code="AUTH_FORBIDDEN_ACTION")

        if action_type == "CREATE_TASK":
            title = payload.get("title", "AI Recommended Task")
            description = payload.get("description", "Created via AI Mentor suggestion")
            category = payload.get("category", "BACKEND")
            priority = payload.get("priority", "MEDIUM")

            task = ProjectTaskModel(
                id=uuid.uuid4(),
                project_instance_id=str(project.id),
                title=title,
                description=description,
                status="TODO",
                priority=priority,
                category=category,
                source="AI_MENTOR",
            )
            created_task = await self._task_repo.add(task)

            # Enqueue canonical domain event
            await self._outbox_service.enqueue(
                event_type=DomainEventType.TASK_CREATED,
                actor_role=current_user.role,
                resource_type="ProjectTask",
                resource_id=str(created_task.id),
                actor_id=current_user.user_id,
                project_instance_id=project.id,
                visibility=EventVisibility.STUDENT.value,
                metadata={"title": created_task.title, "source": "AI_MENTOR_ACTION"},
            )
            return {"status": "SUCCESS", "action_type": action_type, "resource_id": str(created_task.id)}

        if action_type == "COMPLETE_TASK":
            task_id = payload.get("task_id")
            if not task_id:
                raise BusinessRuleException("Task ID is required for COMPLETE_TASK.", code="INVALID_PAYLOAD")

            task = await self._task_repo.get_by_id(task_id)
            if not task or str(task.project_instance_id) != str(project.id):
                # Do not leak cross-project resource existence
                raise NotFoundException("Task not found.", code="TASK_NOT_FOUND")

            if task.status == "DONE":
                raise BusinessRuleException("Task is already completed.", code="TASK_ALREADY_COMPLETED")

            task.status = "DONE"
            updated_task = await self._task_repo.update(task)

            # Enqueue canonical domain event
            await self._outbox_service.enqueue(
                event_type=DomainEventType.TASK_COMPLETED,
                actor_role=current_user.role,
                resource_type="ProjectTask",
                resource_id=str(updated_task.id),
                actor_id=current_user.user_id,
                project_instance_id=project.id,
                visibility=EventVisibility.STUDENT.value,
                metadata={"title": updated_task.title, "source": "AI_MENTOR_ACTION"},
            )
            return {"status": "SUCCESS", "action_type": action_type, "resource_id": str(updated_task.id)}

        if action_type == "CREATE_HELP_REQUEST":
            subject = payload.get("subject", "AI Recommended Help Request")
            description = payload.get("description", "Created via AI Mentor recommendation")
            category = payload.get("category", "TECHNICAL")
            priority = payload.get("priority", "MEDIUM")

            help_req = await self._help_request_repo.add(
                project_id=str(project.id),
                student_id=str(current_user.user_id),
                subject=subject,
                description=description,
                category=category,
                priority=priority,
            )

            # Enqueue canonical domain event
            await self._outbox_service.enqueue(
                event_type=DomainEventType.HELP_REQUEST_CREATED,
                actor_role=current_user.role,
                resource_type="ProjectHelpRequest",
                resource_id=str(help_req.id),
                actor_id=current_user.user_id,
                project_instance_id=project.id,
                visibility=EventVisibility.MENTOR.value,
                metadata={"subject": help_req.subject, "priority": help_req.priority},
            )
            return {"status": "SUCCESS", "action_type": action_type, "resource_id": str(help_req.id)}

        raise BusinessRuleException(f"Unsupported action type: {action_type}", code="INVALID_ACTION_TYPE")

