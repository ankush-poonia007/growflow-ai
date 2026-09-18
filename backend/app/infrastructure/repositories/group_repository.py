"""
GrowFlow — Group Repository Implementation.

Provides persistence operations for groups and group_memberships.

Architecture ref:
  6A § 7 — Repository Architecture
  6B § 6.1 — groups
  6B § 6.2 — group_memberships
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import select

from backend.app.domain.organization.models import GroupMembershipStatus, GroupStatus
from backend.app.infrastructure.database.models.organization import (
    GroupMembershipModel,
    GroupModel,
)
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class GroupRepository(BaseRepository[GroupModel]):
    """Repository managing mentor groups and student group memberships."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=GroupModel)

    async def get_by_join_code(self, join_code: str) -> GroupModel | None:
        result = await self._session.execute(
            select(GroupModel).where(GroupModel.join_code == join_code.strip())
        )
        return result.scalar_one_or_none()

    async def list_by_mentor(
        self, mentor_id: uuid.UUID | str, status: str | None = None
    ) -> Sequence[GroupModel]:
        stmt = select(GroupModel).where(GroupModel.mentor_id == str(mentor_id))
        if status:
            stmt = stmt.where(GroupModel.status == status)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create_group(
        self,
        mentor_id: uuid.UUID | str,
        name: str,
        join_code: str,
        status: str = GroupStatus.ACTIVE.value,
    ) -> GroupModel:
        group = GroupModel(
            id=uuid.uuid4(),
            mentor_id=str(mentor_id),
            name=name.strip(),
            join_code=join_code.strip(),
            status=status,
        )
        return await self.add(group)

    async def get_membership(
        self, group_id: uuid.UUID | str, student_id: uuid.UUID | str
    ) -> GroupMembershipModel | None:
        result = await self._session.execute(
            select(GroupMembershipModel).where(
                GroupMembershipModel.group_id == str(group_id),
                GroupMembershipModel.student_id == str(student_id),
            )
        )
        return result.scalar_one_or_none()

    async def get_active_membership_for_student(
        self, student_id: uuid.UUID | str, group_id: uuid.UUID | str
    ) -> GroupMembershipModel | None:
        result = await self._session.execute(
            select(GroupMembershipModel).where(
                GroupMembershipModel.student_id == str(student_id),
                GroupMembershipModel.group_id == str(group_id),
                GroupMembershipModel.status == GroupMembershipStatus.ACTIVE.value,
            )
        )
        return result.scalar_one_or_none()

    async def list_student_memberships(
        self, student_id: uuid.UUID | str, status: str | None = None
    ) -> Sequence[GroupMembershipModel]:
        stmt = select(GroupMembershipModel).where(
            GroupMembershipModel.student_id == str(student_id)
        )
        if status:
            stmt = stmt.where(GroupMembershipModel.status == status)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_groups_with_mentors_for_student(
        self, student_id: uuid.UUID | str, status: str = GroupMembershipStatus.ACTIVE.value
    ) -> Sequence[tuple[GroupModel, UserModel]]:
        stmt = (
            select(GroupModel, UserModel)
            .join(GroupMembershipModel, GroupMembershipModel.group_id == GroupModel.id)
            .join(UserModel, UserModel.id == GroupModel.mentor_id)
            .where(
                GroupMembershipModel.student_id == str(student_id),
                GroupMembershipModel.status == status,
            )
            .order_by(GroupModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.all()  # type: ignore[return-value]

    async def list_group_members(
        self, group_id: uuid.UUID | str, status: str | None = None
    ) -> Sequence[tuple[GroupMembershipModel, UserModel]]:
        stmt = (
            select(GroupMembershipModel, UserModel)
            .join(UserModel, UserModel.id == GroupMembershipModel.student_id)
            .where(GroupMembershipModel.group_id == str(group_id))
        )
        if status:
            stmt = stmt.where(GroupMembershipModel.status == status)
        result = await self._session.execute(stmt)
        return result.all()  # type: ignore[return-value]

    async def add_membership(
        self,
        group_id: uuid.UUID | str,
        student_id: uuid.UUID | str,
        status: str = GroupMembershipStatus.ACTIVE.value,
    ) -> GroupMembershipModel:
        membership = await self.get_membership(group_id, student_id)
        if membership is not None:
            membership.status = status
            await self._session.flush()
            await self._session.refresh(membership)
            return membership

        new_membership = GroupMembershipModel(
            id=uuid.uuid4(),
            group_id=str(group_id),
            student_id=str(student_id),
            status=status,
        )
        self._session.add(new_membership)
        await self._session.flush()
        await self._session.refresh(new_membership)
        return new_membership

    async def list_supervised_students(
        self,
        mentor_id: uuid.UUID | str,
        *,
        group_id: uuid.UUID | str | None = None,
        search: str | None = None,
    ) -> Sequence[tuple[UserModel, GroupMembershipModel, GroupModel]]:
        """List students across groups supervised by the mentor with optional group and search filters."""
        stmt = (
            select(UserModel, GroupMembershipModel, GroupModel)
            .join(GroupMembershipModel, GroupMembershipModel.student_id == UserModel.id)
            .join(GroupModel, GroupModel.id == GroupMembershipModel.group_id)
            .where(
                GroupModel.mentor_id == str(mentor_id),
                GroupModel.status == GroupStatus.ACTIVE.value,
                GroupMembershipModel.status == GroupMembershipStatus.ACTIVE.value,
            )
        )
        if group_id:
            stmt = stmt.where(GroupModel.id == str(group_id))
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                UserModel.full_name.ilike(term) | UserModel.email.ilike(term)
            )
        stmt = stmt.order_by(UserModel.full_name.asc())
        result = await self._session.execute(stmt)
        return result.all()  # type: ignore[return-value]

    async def is_student_supervised_by_mentor(
        self,
        student_id: uuid.UUID | str,
        mentor_id: uuid.UUID | str,
    ) -> bool:
        """Check if a student is an active member in any active group supervised by the mentor."""
        stmt = (
            select(GroupMembershipModel.id)
            .join(GroupModel, GroupModel.id == GroupMembershipModel.group_id)
            .where(
                GroupMembershipModel.student_id == str(student_id),
                GroupMembershipModel.status == GroupMembershipStatus.ACTIVE.value,
                GroupModel.mentor_id == str(mentor_id),
                GroupModel.status == GroupStatus.ACTIVE.value,
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

