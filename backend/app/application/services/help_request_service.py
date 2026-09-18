"""
GrowFlow — Student Help Request Application Service (S30).

Coordinates student-initiated help requests and mentor communication lifecycle.
Enforces student authority: Students create requests in OPEN state; cannot fake mentor resolution.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
import uuid

from backend.app.infrastructure.database.models.workspace_extensions import ProjectHelpRequestModel
from backend.app.shared.events.domain_event import DomainEventType, EventVisibility
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
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
        HelpRequestRepository,
    )

logger = get_logger("growflow.application.help_request_service")


class HelpRequestService:
    """Service managing student help requests and mentor responses."""

    def __init__(
        self,
        project_repo: ProjectRepository,
        group_repo: GroupRepository,
        help_request_repo: HelpRequestRepository,
        outbox_service: OutboxService,
    ) -> None:
        self._project_repo = project_repo
        self._group_repo = group_repo
        self._help_request_repo = help_request_repo
        self._outbox_service = outbox_service

    async def _verify_project_access(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> ProjectInstanceModel:
        return await verify_project_read_access(
            self._project_repo, self._group_repo, project_id, current_user
        )

    def _format_help_request(self, req: ProjectHelpRequestModel) -> dict[str, Any]:
        return {
            "id": str(req.id),
            "project_instance_id": str(req.project_instance_id),
            "student_id": str(req.student_id),
            "subject": req.subject,
            "description": req.description,
            "category": req.category,
            "priority": req.priority,
            "status": req.status,
            "mentor_response": req.mentor_response,
            "resolved_at": req.resolved_at.isoformat() if req.resolved_at else None,
            "created_at": req.created_at.isoformat() if req.created_at else None,
            "updated_at": req.updated_at.isoformat() if req.updated_at else None,
        }

    async def list_help_requests(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> list[dict[str, Any]]:
        project = await self._verify_project_access(project_id, current_user)
        requests = await self._help_request_repo.list_by_project(project.id)
        return [self._format_help_request(r) for r in requests]

    async def get_help_request(
        self,
        project_id: uuid.UUID | str,
        request_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> dict[str, Any]:
        await self._verify_project_access(project_id, current_user)
        req = await self._help_request_repo.get_by_id(request_id)
        if not req or str(req.project_instance_id) != str(project_id):
            raise NotFoundException("Help request not found.", code="HELP_REQUEST_NOT_FOUND")
        return self._format_help_request(req)

    async def create_help_request(
        self,
        project_id: uuid.UUID | str,
        current_user: CurrentUser,
        subject: str,
        description: str,
        category: str = "TECHNICAL",
        priority: str = "MEDIUM",
    ) -> dict[str, Any]:
        project = await self._verify_project_access(project_id, current_user)
        if current_user.is_student and str(project.student_id) != str(current_user.user_id):
            raise AuthorizationException("Only the project owner can create help requests.", code="AUTH_FORBIDDEN_ACTION")

        model = ProjectHelpRequestModel(
            id=uuid.uuid4(),
            project_instance_id=str(project.id),
            student_id=str(current_user.user_id),
            subject=subject.strip(),
            description=description.strip(),
            category=category.upper(),
            priority=priority.upper(),
            status="OPEN",  # Enforced initial state
            mentor_response=None,
            resolved_at=None,
        )
        created = await self._help_request_repo.add(model)

        await self._outbox_service.enqueue(
            event_type=DomainEventType.HELP_REQUEST_CREATED,
            actor_role=current_user.role,
            resource_type="ProjectHelpRequest",
            resource_id=str(created.id),
            actor_id=current_user.user_id,
            project_instance_id=project.id,
            visibility=EventVisibility.MENTOR.value,
            metadata={"subject": created.subject, "priority": created.priority},
        )

        return self._format_help_request(created)

    async def list_mentor_help_requests(
        self,
        mentor_id: uuid.UUID | str,
        *,
        status: str | None = None,
        group_id: uuid.UUID | str | None = None,
    ) -> list[dict[str, Any]]:
        """List help requests from students supervised by the mentor."""
        mentor_groups = await self._group_repo.list_by_mentor(mentor_id)
        if group_id:
            mentor_groups = [g for g in mentor_groups if str(g.id) == str(group_id)]
        if not mentor_groups:
            return []

        # Find all project instances supervised by the mentor
        project_ids: set[str] = set()
        for g in mentor_groups:
            projs = await self._project_repo.list_by_group(g.id)
            for p in projs:
                project_ids.add(str(p.id))

        # Include individual projects of students enrolled in mentor's groups if group_id is not specified
        if not group_id:
            for g in mentor_groups:
                members = await self._group_repo.list_group_members(g.id, status="ACTIVE")
                for _, student in members:
                    student_projs = await self._project_repo.list_by_student(student.id)
                    for sp in student_projs:
                        if not sp.group_id:
                            project_ids.add(str(sp.id))

        if not project_ids:
            return []

        records = await self._help_request_repo.list_mentor_help_requests_detailed(
            list(project_ids), status=status
        )

        return [
            {
                "id": str(req.id),
                "project_instance_id": str(proj.id),
                "project_name": proj.name,
                "student_id": str(student.id),
                "student_name": student.full_name or student.email,
                "student_email": student.email,
                "group_id": str(grp.id) if grp else None,
                "group_name": grp.name if grp else None,
                "subject": req.subject,
                "description": req.description,
                "category": req.category,
                "priority": req.priority,
                "status": req.status,
                "mentor_response": req.mentor_response,
                "resolved_at": req.resolved_at.isoformat() if req.resolved_at else None,
                "created_at": req.created_at.isoformat() if req.created_at else None,
                "updated_at": req.updated_at.isoformat() if req.updated_at else None,
            }
            for req, proj, student, grp in records
        ]

    async def get_mentor_help_request(
        self,
        mentor_id: uuid.UUID | str,
        request_id: uuid.UUID | str,
    ) -> dict[str, Any]:
        """Retrieve a specific help request verifying mentor supervision."""
        record = await self._help_request_repo.get_detailed_by_id(request_id)
        if not record:
            raise NotFoundException("Help request not found.", code="HELP_REQUEST_NOT_FOUND")

        req, proj, student, grp = record

        # Verify supervision
        is_supervised = await is_mentor_supervising_project(self._group_repo, proj, mentor_id)
        if not is_supervised:
            raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")

        return {
            "id": str(req.id),
            "project_instance_id": str(proj.id),
            "project_name": proj.name,
            "student_id": str(student.id),
            "student_name": student.full_name or student.email,
            "student_email": student.email,
            "group_id": str(grp.id) if grp else None,
            "group_name": grp.name if grp else None,
            "subject": req.subject,
            "description": req.description,
            "category": req.category,
            "priority": req.priority,
            "status": req.status,
            "mentor_response": req.mentor_response,
            "resolved_at": req.resolved_at.isoformat() if req.resolved_at else None,
            "created_at": req.created_at.isoformat() if req.created_at else None,
            "updated_at": req.updated_at.isoformat() if req.updated_at else None,
        }

    async def respond_help_request(
        self,
        mentor_id: uuid.UUID | str,
        request_id: uuid.UUID | str,
        mentor_response: str,
        status: str = "RESOLVED",
    ) -> dict[str, Any]:
        """Respond to a student help request and update lifecycle status."""
        # Check access first
        detail = await self.get_mentor_help_request(mentor_id, request_id)

        target_status = status.upper()
        if target_status not in ("RESOLVED", "IN_PROGRESS", "OPEN"):
            raise BusinessRuleException(
                f"Invalid help request status: {status}", code="INVALID_STATUS"
            )

        updated = await self._help_request_repo.update_response(
            request_id=request_id,
            mentor_response=mentor_response.strip(),
            status=target_status,
        )
        if not updated:
            raise NotFoundException("Help request not found.", code="HELP_REQUEST_NOT_FOUND")

        await self._outbox_service.enqueue(
            event_type=DomainEventType.HELP_REQUEST_UPDATED,
            actor_role="MENTOR",
            resource_type="ProjectHelpRequest",
            resource_id=str(updated.id),
            actor_id=uuid.UUID(str(mentor_id)),
            project_instance_id=uuid.UUID(str(detail["project_instance_id"])),
            visibility=EventVisibility.STUDENT.value,
            metadata={"subject": updated.subject, "status": updated.status},
        )

        detail["status"] = updated.status
        detail["mentor_response"] = updated.mentor_response
        detail["resolved_at"] = updated.resolved_at.isoformat() if updated.resolved_at else None
        detail["updated_at"] = updated.updated_at.isoformat() if updated.updated_at else None
        return detail
