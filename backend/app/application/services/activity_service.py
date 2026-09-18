"""
GrowFlow — Project Activity Audit Trail Application Service (S28).

Queries chronological activity directly from the canonical `domain_events` table.
Does NOT create a secondary activity store or synthetic log table.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import uuid

from backend.app.application.services.authorization_helpers import (
    verify_project_read_access,
)
from backend.app.shared.exceptions import (
    AuthorizationException,
    NotFoundException,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.database.models.project import ProjectInstanceModel
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.outbox_repository import OutboxRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository

logger = get_logger("growflow.application.activity_service")


class ActivityService:
    """Service querying canonical project activity audit trail."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        group_repo: GroupRepository,
        outbox_repo: OutboxRepository,
    ) -> None:
        self._project_repo = project_repo
        self._group_repo = group_repo
        self._outbox_repo = outbox_repo

    async def _verify_project_access(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> ProjectInstanceModel:
        return await verify_project_read_access(
            self._project_repo, self._group_repo, project_id, current_user
        )

    def _format_event_description(self, event_type: str, metadata: dict[str, Any], actor_role: str) -> tuple[str, str]:
        """Produce human-readable title and summary from canonical domain event."""
        type_titles = {
            "ProjectCreated": ("Project Created", "Project workspace initialized."),
            "ProjectPhaseChanged": ("Phase Advanced", f"Phase updated to {metadata.get('new_phase', 'next phase')}."),
            "ProjectHealthChanged": ("Health Evaluation Updated", f"Project health status: {metadata.get('new_health', 'UPDATED')}."),
            "BlueprintGenerated": ("Blueprint Generated", "Architecture blueprint generated and ready for review."),
            "BlueprintApproved": ("Blueprint Approved", "Architecture blueprint reviewed, evaluated, and approved."),
            "TaskCreated": ("Task Created", f"Task '{metadata.get('title', 'New Task')}' added to board."),
            "TaskUpdated": ("Task Updated", f"Task '{metadata.get('title', 'Task')}' updated ({metadata.get('status', 'modified')})."),
            "TaskCompleted": ("Task Completed", f"Task '{metadata.get('title', 'Task')}' marked completed."),
            "MilestoneUpdated": ("Milestone Updated", f"Milestone '{metadata.get('title', 'Milestone')}' progress updated."),
            "RiskCreated": ("Risk Logged", f"Risk '{metadata.get('title', 'Risk')}' identified and tracked."),
            "RiskUpdated": ("Risk Updated", f"Risk '{metadata.get('title', 'Risk')}' mitigation status adjusted."),
            "DocumentCreated": ("Document Created", f"Document '{metadata.get('title', 'Doc')}' created."),
            "DocumentUpdated": ("Document Updated", f"Document '{metadata.get('title', 'Doc')}' content updated."),
            "GitHubConnected": ("GitHub Connected", f"Repository {metadata.get('repository_name', '')} linked."),
            "GitHubSynced": ("GitHub Synchronized", f"Repository commits synchronized ({metadata.get('commit_count', 0)} commits)."),
            "HelpRequestCreated": ("Help Request Submitted", f"Help request submitted: {metadata.get('subject', '')}."),
            "HelpRequestUpdated": ("Help Request Updated", "Help request details updated."),
            "HelpRequestResponded": ("Help Request Guidance", "Mentor guidance response provided."),
            "MentorNoteCreated": ("Mentor Note Posted", f"Mentor communication posted: {metadata.get('title', '')}."),
            "MentorNoteAcknowledged": ("Mentor Note Acknowledged", "Student acknowledged mentor feedback."),
            "ProjectChangeRequested": ("Change Proposed", f"Scope/tech change proposed: {metadata.get('change_title', '')}."),
            "ProjectChangeAnalyzed": ("Impact Analysis Complete", f"Change impact analysis evaluated for {metadata.get('change_title', '')}."),
            "ProjectChangeConfirmed": ("Change Confirmed", "Student confirmed impact analysis; blueprint regenerating."),
            "ProjectChangeCompleted": ("Regeneration Complete", f"Blueprint updated to version {metadata.get('resulting_version_number', '')}."),
            "AIMentorMessageSent": ("AI Mentor Consultation", "Discussion recorded with AI Mentor."),
            "GroupCreated": ("Cohort Initialized", f"Cohort group '{metadata.get('name', 'Cohort')}' initialized."),
            "StudentJoinedGroup": ("Student Enrolled", "Student enrolled in cohort."),
        }
        if event_type in type_titles:
            return type_titles[event_type]
        return (event_type, f"Action recorded by {actor_role}.")

    def _serialize_event(self, evt: Any) -> dict[str, Any]:
        """Serialize DomainEventModel into JSON-compatible dictionary."""
        title, desc = self._format_event_description(evt.event_type, evt.metadata_json or {}, evt.actor_role)
        return {
            "id": str(evt.id),
            "event_type": evt.event_type,
            "title": title,
            "description": desc,
            "actor_role": evt.actor_role,
            "actor_id": str(evt.actor_id) if evt.actor_id else None,
            "resource_type": evt.resource_type,
            "resource_id": str(evt.resource_id),
            "project_instance_id": str(evt.project_instance_id) if evt.project_instance_id else None,
            "group_id": str(evt.group_id) if evt.group_id else None,
            "occurred_at": evt.occurred_at.isoformat() if evt.occurred_at else None,
            "metadata": evt.metadata_json or {},
        }

    async def get_project_activity(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        project = await self._verify_project_access(project_id, current_user)
        events = await self._outbox_repo.list_by_project(project.id, limit=limit, offset=offset)
        return [self._serialize_event(evt) for evt in events]

    async def get_group_activity(
        self,
        group_id: uuid.UUID | str,
        current_user: CurrentUser,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundException("Group not found.", code="GROUP_NOT_FOUND")

        if not current_user.is_admin:
            if not current_user.is_mentor or str(group.mentor_id) != str(current_user.user_id):
                raise AuthorizationException(
                    "Access denied. You do not supervise this group.",
                    code="AUTH_FORBIDDEN_RESOURCE",
                )

        projects = await self._project_repo.list_by_group(group_id)
        project_ids = [p.id for p in projects]

        events = await self._outbox_repo.list_by_group(
            group_id=group_id,
            project_ids=project_ids,
            limit=limit,
            offset=offset,
        )
        return [self._serialize_event(evt) for evt in events]

    async def get_student_activity(
        self,
        student_id: uuid.UUID | str,
        current_user: CurrentUser,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        if not current_user.is_admin:
            if not current_user.is_mentor:
                raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")
            is_supervised = await self._group_repo.is_student_supervised_by_mentor(
                student_id=student_id,
                mentor_id=current_user.user_id,
            )
            if not is_supervised:
                raise AuthorizationException(
                    "Access denied. You do not supervise this student.",
                    code="AUTH_FORBIDDEN_RESOURCE",
                )

        mentor_groups = await self._group_repo.list_by_mentor(current_user.user_id)
        mentor_group_ids = [str(g.id) for g in mentor_groups]

        student_projects = await self._project_repo.list_by_student(student_id)
        supervised_project_ids = [
            p.id for p in student_projects if p.group_id and str(p.group_id) in mentor_group_ids
        ]

        events = await self._outbox_repo.list_by_student(
            student_id=student_id,
            supervised_project_ids=supervised_project_ids,
            supervised_group_ids=mentor_group_ids,
            limit=limit,
            offset=offset,
        )
        return [self._serialize_event(evt) for evt in events]

    async def get_mentor_activity(
        self,
        current_user: CurrentUser,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        if not current_user.is_mentor and not current_user.is_admin:
            raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")

        mentor_groups = await self._group_repo.list_by_mentor(current_user.user_id)
        mentor_group_ids = [g.id for g in mentor_groups]

        if mentor_group_ids:
            records = await self._project_repo.list_supervised_projects(mentor_group_ids)
            project_ids = [r[0].id for r in records]
        else:
            project_ids = []

        events = await self._outbox_repo.list_by_mentor_portfolio(
            mentor_id=current_user.user_id,
            supervised_group_ids=mentor_group_ids,
            supervised_project_ids=project_ids,
            limit=limit,
            offset=offset,
        )
        return [self._serialize_event(evt) for evt in events]

