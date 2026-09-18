"""
GrowFlow — Mentor Feedback Application Service (S31).

Coordinates reading and acknowledging mentor communication.
Does NOT mutate tasks, milestones, or deadlines when notes are acknowledged.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import uuid

from backend.app.infrastructure.database.models.workspace_extensions import ProjectMentorNoteModel
from backend.app.shared.events.domain_event import DomainEventType, EventVisibility
from backend.app.shared.exceptions import (
    AuthorizationException,
    NotFoundException,
)
from backend.app.application.services.authorization_helpers import (
    is_mentor_supervising_project,
    verify_project_read_access,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.database.models.project import ProjectInstanceModel
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.project_repository import ProjectRepository
    from backend.app.infrastructure.repositories.workspace_extension_repositories import (
        MentorNoteRepository,
    )

logger = get_logger("growflow.application.mentor_feedback_service")


class MentorFeedbackService:
    """Service managing mentor feedback notes and student acknowledgments."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        group_repo: GroupRepository,
        mentor_note_repo: MentorNoteRepository,
        outbox_service: OutboxService,
    ) -> None:
        self._project_repo = project_repo
        self._group_repo = group_repo
        self._mentor_note_repo = mentor_note_repo
        self._outbox_service = outbox_service

    async def _verify_project_access(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> ProjectInstanceModel:
        return await verify_project_read_access(
            self._project_repo, self._group_repo, project_id, current_user
        )

    def _format_note(self, note: ProjectMentorNoteModel) -> dict[str, Any]:
        return {
            "id": str(note.id),
            "project_instance_id": str(note.project_instance_id),
            "mentor_id": str(note.mentor_id) if note.mentor_id else None,
            "title": note.title,
            "message": note.message,
            "note_type": note.note_type,
            "status": note.status,
            "related_resource_type": note.related_resource_type,
            "related_resource_id": str(note.related_resource_id) if note.related_resource_id else None,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "updated_at": note.updated_at.isoformat() if note.updated_at else None,
        }

    async def list_mentor_notes(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> list[dict[str, Any]]:
        project = await self._verify_project_access(project_id, current_user)
        notes = await self._mentor_note_repo.list_by_project(project.id)
        if current_user.is_student:
            notes = [n for n in notes if n.note_type != "INTERNAL"]
        return [self._format_note(n) for n in notes]

    async def acknowledge_note(
        self,
        project_id: uuid.UUID | str,
        note_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> dict[str, Any]:
        project = await self._verify_project_access(project_id, current_user)
        if current_user.is_student and str(project.student_id) != str(current_user.user_id):
            raise AuthorizationException("Only the project owner can acknowledge mentor notes.", code="AUTH_FORBIDDEN_ACTION")

        note = await self._mentor_note_repo.get_by_id(note_id)
        if not note or str(note.project_instance_id) != str(project.id):
            raise NotFoundException("Mentor note not found.", code="MENTOR_NOTE_NOT_FOUND")

        updated = await self._mentor_note_repo.mark_acknowledged(note.id)

        await self._outbox_service.enqueue(
            event_type=DomainEventType.MENTOR_NOTE_ACKNOWLEDGED,
            actor_role=current_user.role,
            resource_type="ProjectMentorNote",
            resource_id=str(note.id),
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            visibility=EventVisibility.MENTOR.value,
            metadata={"title": note.title},
        )

        return self._format_note(updated or note)

    async def create_mentor_note(
        self,
        mentor_id: uuid.UUID | str,
        project_id: uuid.UUID | str,
        title: str,
        message: str,
        note_type: str = "INFORMATIONAL",
        related_resource_type: str | None = None,
        related_resource_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a mentor note/feedback on a supervised project instance."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException(f"Project {project_id} not found.", code="PROJECT_NOT_FOUND")

        # Verify mentor supervises project
        is_supervised = await is_mentor_supervising_project(self._group_repo, project, mentor_id)
        if not is_supervised:
            raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")

        upper_type = note_type.upper()
        if upper_type not in ("INFORMATIONAL", "ACTIONABLE", "FEEDBACK", "INTERNAL"):
            upper_type = "INFORMATIONAL"

        note = ProjectMentorNoteModel(
            id=uuid.uuid4(),
            project_instance_id=str(project.id),
            mentor_id=str(mentor_id),
            title=title.strip(),
            message=message.strip(),
            note_type=upper_type,
            status="UNREAD",
            related_resource_type=related_resource_type,
            related_resource_id=str(related_resource_id) if related_resource_id else None,
        )
        created = await self._mentor_note_repo.add(note)

        await self._outbox_service.enqueue(
            event_type=DomainEventType.MENTOR_NOTE_CREATED,
            actor_role="MENTOR",
            resource_type="ProjectMentorNote",
            resource_id=str(created.id),
            actor_id=uuid.UUID(str(mentor_id)),
            project_instance_id=project.id,
            visibility=(
                EventVisibility.STUDENT.value if upper_type != "INTERNAL" else EventVisibility.MENTOR.value
            ),
            metadata={"title": created.title, "note_type": created.note_type},
        )

        return self._format_note(created)

    async def list_mentor_notes_for_project(
        self,
        mentor_id: uuid.UUID | str,
        project_id: uuid.UUID | str,
    ) -> list[dict[str, Any]]:
        """List all mentor notes on a project verifying mentor supervision."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException(f"Project {project_id} not found.", code="PROJECT_NOT_FOUND")

        # Verify mentor supervises project
        if project.group_id:
            group = await self._group_repo.get_by_id(project.group_id)
            if not group or str(group.mentor_id) != str(mentor_id):
                raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")
        else:
            is_supervised = await self._group_repo.is_student_supervised_by_mentor(
                project.student_id, mentor_id
            )
            if not is_supervised:
                raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")

        detailed_notes = await self._mentor_note_repo.list_by_project_detailed(project.id)
        result = []
        for n, mentor_user in detailed_notes:
            formatted = self._format_note(n)
            formatted["mentor_name"] = mentor_user.full_name or mentor_user.email if mentor_user else None
            result.append(formatted)
        return result
