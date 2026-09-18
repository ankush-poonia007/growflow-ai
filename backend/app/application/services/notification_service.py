"""
GrowFlow — Notification Application Service (Batch 08 / Gate 13).

Orchestrates user-facing notifications, recipient resolution, and atomic lifecycle states.
Enforces that notifications are created only from the 8 approved canonical domain events.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import uuid

from backend.app.shared.exceptions import NotFoundException
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Sequence

    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.database.models.notification import NotificationModel
    from backend.app.infrastructure.database.models.outbox import DomainEventModel
    from backend.app.infrastructure.repositories.group_repository import GroupRepository
    from backend.app.infrastructure.repositories.notification_repository import (
        NotificationRepository,
    )
    from backend.app.infrastructure.repositories.project_repository import (
        ProjectRepository,
    )

logger = get_logger("growflow.application.notification_service")

# Exactly the 8 approved canonical user-facing event types (Prompt § 3)
IN_SCOPE_NOTIFICATION_EVENTS: frozenset[str] = frozenset({
    "MentorNoteCreated",
    "MentorNoteAcknowledged",
    "HelpRequestCreated",
    "HelpRequestResponded",
    "BlueprintGenerated",
    "BlueprintApproved",
    "ProjectChangeRequested",
    "ProjectChangeCompleted",
})


class NotificationService:
    """Service managing user notifications and event-to-notification translations."""

    def __init__(
        self,
        notification_repo: NotificationRepository,
        project_repo: ProjectRepository,
        group_repo: GroupRepository,
    ) -> None:
        self._notification_repo = notification_repo
        self._project_repo = project_repo
        self._group_repo = group_repo

    async def get_user_notifications(
        self,
        current_user: CurrentUser,
        *,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False,
    ) -> Sequence[NotificationModel]:
        """List notifications belonging strictly to the authenticated user."""
        return await self._notification_repo.list_by_user(
            user_id=current_user.user_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
        )

    async def get_unread_count(self, current_user: CurrentUser) -> int:
        """Count unread notifications for authenticated user."""
        return await self._notification_repo.count_unread(current_user.user_id)

    async def mark_as_read(
        self,
        notification_id: uuid.UUID | str,
        current_user: CurrentUser,
    ) -> NotificationModel:
        """
        Mark a notification as read.
        Never leaks existence of cross-user notifications (raises 404 if not found for user).
        """
        notification = await self._notification_repo.mark_read(
            notification_id=notification_id,
            user_id=current_user.user_id,
        )
        if not notification:
            raise NotFoundException(
                "Notification not found.",
                code="NOTIFICATION_NOT_FOUND",
            )
        return notification

    async def mark_all_as_read(self, current_user: CurrentUser) -> int:
        """Mark all unread notifications for authenticated user as read."""
        return await self._notification_repo.mark_all_read(current_user.user_id)

    async def handle_domain_event(self, event: DomainEventModel) -> list[NotificationModel]:
        """
        Translates canonical domain event into persistent notifications
        if it is one of the 8 approved user-facing event types.
        """
        if event.event_type not in IN_SCOPE_NOTIFICATION_EVENTS:
            return []

        metadata = event.metadata_json or {}
        recipients: list[dict[str, Any]] = []

        # Recipient resolution logic
        if event.event_type == "MentorNoteCreated":
            # Recipient: Student owner of project
            student_id = None
            if event.project_instance_id:
                project = await self._project_repo.get_by_id(event.project_instance_id)
                if project:
                    student_id = str(project.student_id)
            if student_id:
                recipients.append({
                    "user_id": student_id,
                    "title": f"New Mentor Note: {metadata.get('title', 'Mentor Communication')}",
                    "message": "Your mentor posted a note on your project workspace.",
                    "category": "COMMUNICATION",
                    "link": f"/student/projects/{event.project_instance_id}/mentor-feedback" if event.project_instance_id else "/student/dashboard",
                })

        elif event.event_type == "MentorNoteAcknowledged":
            # Recipient: Authoring mentor or group mentor
            recipient_id = metadata.get("mentor_id")
            if not recipient_id and event.group_id:
                group = await self._group_repo.get_by_id(event.group_id)
                if group and group.mentor_id:
                    recipient_id = str(group.mentor_id)
            if not recipient_id and event.project_instance_id:
                project = await self._project_repo.get_by_id(event.project_instance_id)
                if project and project.group_id:
                    group = await self._group_repo.get_by_id(project.group_id)
                    if group and group.mentor_id:
                        recipient_id = str(group.mentor_id)
            if recipient_id:
                note_title = metadata.get("title", "Mentor Note")
                recipients.append({
                    "user_id": str(recipient_id),
                    "title": f"Mentor Note Acknowledged: {note_title}",
                    "message": f"Student acknowledged your feedback note '{note_title}'.",
                    "category": "COMMUNICATION",
                    "link": f"/mentor/projects/{event.project_instance_id}" if event.project_instance_id else "/mentor/overview",
                })

        elif event.event_type == "HelpRequestCreated":
            # Recipient: Supervising mentor of the cohort group
            recipient_id = None
            if event.group_id:
                group = await self._group_repo.get_by_id(event.group_id)
                if group and group.mentor_id:
                    recipient_id = str(group.mentor_id)
            if not recipient_id and event.project_instance_id:
                project = await self._project_repo.get_by_id(event.project_instance_id)
                if project and project.group_id:
                    group = await self._group_repo.get_by_id(project.group_id)
                    if group and group.mentor_id:
                        recipient_id = str(group.mentor_id)
            if recipient_id:
                subject = metadata.get("subject", "Assistance Requested")
                recipients.append({
                    "user_id": str(recipient_id),
                    "title": f"Help Request Submitted: {subject}",
                    "message": f"A student requested guidance on '{subject}'.",
                    "category": "SUPERVISION",
                    "link": "/mentor/reviews/help-requests",
                })

        elif event.event_type == "HelpRequestResponded":
            # Recipient: Student owner
            recipient_id = metadata.get("student_id")
            if not recipient_id and event.project_instance_id:
                project = await self._project_repo.get_by_id(event.project_instance_id)
                if project:
                    recipient_id = str(project.student_id)
            if recipient_id:
                subject = metadata.get("subject", "Help Request")
                recipients.append({
                    "user_id": str(recipient_id),
                    "title": f"Mentor Guidance: {subject}",
                    "message": f"Mentor provided guidance regarding your help request '{subject}'.",
                    "category": "SUPERVISION",
                    "link": f"/student/projects/{event.project_instance_id}/help" if event.project_instance_id else "/student/dashboard",
                })

        elif event.event_type == "BlueprintGenerated":
            # Recipient: Student owner
            recipient_id = None
            if event.project_instance_id:
                project = await self._project_repo.get_by_id(event.project_instance_id)
                if project:
                    recipient_id = str(project.student_id)
            if recipient_id:
                recipients.append({
                    "user_id": str(recipient_id),
                    "title": "Architecture Blueprint Synthesized",
                    "message": "Your system architecture blueprint has been generated and is ready for review.",
                    "category": "ACADEMIC",
                    "link": f"/student/projects/{event.project_instance_id}/blueprint" if event.project_instance_id else "/student/dashboard",
                })

        elif event.event_type == "BlueprintApproved":
            # Recipient: Student owner
            recipient_id = None
            if event.project_instance_id:
                project = await self._project_repo.get_by_id(event.project_instance_id)
                if project:
                    recipient_id = str(project.student_id)
            if recipient_id:
                recipients.append({
                    "user_id": str(recipient_id),
                    "title": "Architecture Blueprint Approved",
                    "message": "Your architecture blueprint has been reviewed, evaluated, and approved!",
                    "category": "ACADEMIC",
                    "link": f"/student/projects/{event.project_instance_id}/blueprint" if event.project_instance_id else "/student/dashboard",
                })

        elif event.event_type == "ProjectChangeRequested":
            # Recipient: Group mentor
            recipient_id = None
            if event.group_id:
                group = await self._group_repo.get_by_id(event.group_id)
                if group and group.mentor_id:
                    recipient_id = str(group.mentor_id)
            if not recipient_id and event.project_instance_id:
                project = await self._project_repo.get_by_id(event.project_instance_id)
                if project and project.group_id:
                    group = await self._group_repo.get_by_id(project.group_id)
                    if group and group.mentor_id:
                        recipient_id = str(group.mentor_id)
            if recipient_id:
                change_title = metadata.get("change_title", "Scope/Tech Change")
                recipients.append({
                    "user_id": str(recipient_id),
                    "title": f"Project Change Proposed: {change_title}",
                    "message": f"Student proposed project change '{change_title}' requiring impact review.",
                    "category": "TECHNICAL",
                    "link": "/mentor/reviews/changes",
                })

        elif event.event_type == "ProjectChangeCompleted":
            # Recipient 1: Student project owner
            # Recipient 2: Supervising mentor associated with student's project/group
            project = None
            if event.project_instance_id:
                project = await self._project_repo.get_by_id(event.project_instance_id)

            resulting_v = metadata.get("resulting_blueprint_version_number") or metadata.get("resulting_version_number") or ""
            version_str = f"v{resulting_v}" if resulting_v else "updated version"

            # 1. Student project owner
            if project and project.student_id:
                recipients.append({
                    "user_id": str(project.student_id),
                    "title": "Project Blueprint Regenerated",
                    "message": f"Project architecture successfully regenerated to {version_str}.",
                    "category": "TECHNICAL",
                    "link": f"/student/projects/{event.project_instance_id}/blueprint" if event.project_instance_id else "/student/dashboard",
                })

            # 2. Supervising mentor (canonical relationship only)
            mentor_id = None
            group_id = event.group_id or (project.group_id if project else None)
            if group_id:
                group = await self._group_repo.get_by_id(group_id)
                if group and group.mentor_id:
                    mentor_id = str(group.mentor_id)
            if not mentor_id and project and project.student_id:
                groups_with_mentors = await self._group_repo.list_groups_with_mentors_for_student(project.student_id)
                if groups_with_mentors:
                    mentor_id = str(groups_with_mentors[0][0].mentor_id)

            if mentor_id:
                recipients.append({
                    "user_id": str(mentor_id),
                    "title": "Project Change Completed",
                    "message": f"Project change completed and architecture regenerated to {version_str}.",
                    "category": "TECHNICAL",
                    "link": f"/mentor/projects/{event.project_instance_id}" if event.project_instance_id else "/mentor/overview",
                })

        if not recipients:
            logger.warning(
                "Unable to derive truthful recipient(s) for event %s (id=%s)",
                event.event_type,
                event.id,
            )
            return []

        created_notifications: list[NotificationModel] = []
        for recip in recipients:
            user_id = recip["user_id"]
            # Do not notify the actor about their own action for routine actions,
            # but for ProjectChangeCompleted both student owner and supervising mentor
            # receive their completion notification regardless of who triggered the change confirmation.
            if event.event_type != "ProjectChangeCompleted" and event.actor_id and str(event.actor_id) == str(user_id):
                continue

            notif = await self._notification_repo.create_notification(
                user_id=user_id,
                actor_id=event.actor_id,
                actor_role=event.actor_role,
                title=recip["title"],
                message=recip["message"],
                notification_type=event.event_type,
                category=recip["category"],
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                link=recip["link"],
                event_id=str(event.id),
            )
            created_notifications.append(notif)

        return created_notifications
