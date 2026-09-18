"""
GrowFlow — Group Service Implementation.

Manages mentor-managed student cohorts, join codes, and student memberships.

Architecture ref:
  6A § 9 — Class-Based Architecture
  6B § 6 — Organization
  6C § 11 — Group APIs
  6H § 6 — GroupCreated, StudentJoinedGroup events
"""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from backend.app.domain.organization.models import GroupMembershipStatus, GroupStatus
from backend.app.shared.events.domain_event import DomainEventType
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    ConflictException,
    NotFoundException,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    import uuid

    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.domain.identity.models import CurrentUser
    from backend.app.infrastructure.database.models.organization import (
        GroupMembershipModel,
        GroupModel,
    )
    from backend.app.infrastructure.database.models.user import UserModel
    from backend.app.infrastructure.repositories.group_repository import GroupRepository


class GroupService:
    """Application service for managing student cohorts, join codes, and memberships."""

    def __init__(
        self,
        group_repo: GroupRepository,
        outbox_service: OutboxService,
    ) -> None:
        self._group_repo = group_repo
        self._outbox_service = outbox_service

    async def create_group(
        self,
        mentor_id: uuid.UUID,
        name: str,
        *,
        correlation_id: str = "",
    ) -> GroupModel:
        # Generate a unique 8-character uppercase join code
        for _ in range(5):
            code = secrets.token_hex(4).upper()
            existing = await self._group_repo.get_by_join_code(code)
            if existing is None:
                break
        else:
            code = f"GRP-{secrets.token_hex(4).upper()}"

        group = await self._group_repo.create_group(
            mentor_id=mentor_id,
            name=name,
            join_code=code,
            status=GroupStatus.ACTIVE.value,
        )

        await self._outbox_service.emit(
            event_type=DomainEventType.GROUP_CREATED.value,
            actor_role="MENTOR",
            resource_type="group",
            resource_id=str(group.id),
            actor_id=mentor_id,
            group_id=group.id,
            metadata={"group_name": group.name, "join_code": group.join_code},
            correlation_id=correlation_id,
        )
        return group

    async def get_group(
        self,
        group_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> GroupModel:
        group = await self._group_repo.get_by_id(group_id)
        if group is None:
            raise NotFoundException("Group not found.", code="GROUP_NOT_FOUND")

        # Authorization: mentor owner OR active student member OR admin
        if current_user.is_admin:
            return group

        if current_user.is_mentor and str(group.mentor_id) == str(current_user.user_id):
            return group

        if current_user.is_student:
            membership = await self._group_repo.get_active_membership_for_student(
                current_user.user_id, group_id
            )
            if membership is not None:
                return group

        raise AuthorizationException(
            "Access to this group is denied.", code="AUTH_FORBIDDEN_RESOURCE"
        )

    async def list_groups_for_user(
        self,
        current_user: CurrentUser,
    ) -> Sequence[GroupModel]:
        if current_user.is_mentor:
            return await self._group_repo.list_by_mentor(current_user.user_id)

        if current_user.is_student:
            group_pairs = await self._group_repo.list_groups_with_mentors_for_student(
                current_user.user_id, status=GroupMembershipStatus.ACTIVE.value
            )
            groups: list[GroupModel] = []
            for grp, mentor in group_pairs:
                setattr(grp, "mentor_name", mentor.full_name or mentor.email)
                groups.append(grp)
            return groups

        return []

    async def update_group(
        self,
        group_id: uuid.UUID,
        current_user: CurrentUser,
        *,
        name: str | None = None,
        status: str | None = None,
    ) -> GroupModel:
        group = await self.get_group(group_id, current_user)
        if not current_user.is_admin and str(group.mentor_id) != str(current_user.user_id):
            raise AuthorizationException(
                "Only the group mentor may update this group.", code="AUTH_FORBIDDEN_RESOURCE"
            )

        if name is not None:
            group.name = name.strip()
        if status is not None:
            group.status = status

        return group

    async def join_group(
        self,
        student_id: uuid.UUID,
        join_code: str,
        *,
        correlation_id: str = "",
    ) -> GroupMembershipModel:
        group = await self._group_repo.get_by_join_code(join_code.strip())
        if group is None:
            raise NotFoundException("Invalid group join code.", code="GROUP_NOT_FOUND")

        if group.status != GroupStatus.ACTIVE.value:
            raise BusinessRuleException(
                "Cannot join an inactive or archived group.", code="GROUP_NOT_ACTIVE"
            )

        # Check existing active membership
        existing = await self._group_repo.get_active_membership_for_student(student_id, group.id)
        if existing is not None:
            raise ConflictException(
                "Student is already an active member of this group.",
                code="GROUP_ALREADY_MEMBER",
            )

        membership = await self._group_repo.add_membership(
            group_id=group.id,
            student_id=student_id,
            status=GroupMembershipStatus.ACTIVE.value,
        )

        await self._outbox_service.emit(
            event_type=DomainEventType.STUDENT_JOINED_GROUP.value,
            actor_role="STUDENT",
            resource_type="group",
            resource_id=str(group.id),
            actor_id=student_id,
            group_id=group.id,
            metadata={"student_id": str(student_id), "join_code": join_code},
            correlation_id=correlation_id,
        )
        setattr(membership, "group_name", group.name)
        setattr(membership, "join_code", group.join_code)
        return membership

    async def list_group_students(
        self,
        group_id: uuid.UUID,
        current_user: CurrentUser,
    ) -> Sequence[tuple[GroupMembershipModel, UserModel]]:
        # Verifies authorization
        await self.get_group(group_id, current_user)
        return await self._group_repo.list_group_members(
            group_id, status=GroupMembershipStatus.ACTIVE.value
        )
