"""
GrowFlow — Organization SQLAlchemy ORM Models.

Defines ORM mappings for:
- groups
- group_memberships

Architecture ref:
  6B § 6.1 — groups
  6B § 6.2 — group_memberships
"""

from __future__ import annotations

from datetime import (  # noqa: TC003 — evaluated at runtime by SQLAlchemy mapper
    datetime,
)
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.domain.organization.models import (
    Group,
    GroupMembership,
    GroupMembershipStatus,
    GroupStatus,
)
from backend.app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class GroupModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for groups table."""

    __tablename__ = "groups"

    mentor_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    join_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=GroupStatus.ACTIVE.value,
        index=True,
        nullable=False,
    )

    def to_domain(self) -> Group:
        return Group(
            id=UUID(str(self.id)),
            mentor_id=UUID(self.mentor_id),
            name=self.name,
            join_code=self.join_code,
            status=GroupStatus(self.status),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class GroupMembershipModel(Base, UUIDPrimaryKeyMixin):
    """SQLAlchemy model for group_memberships table."""

    __tablename__ = "group_memberships"
    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "student_id",
            name="uq_group_student_membership",
        ),
    )

    group_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("groups.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=GroupMembershipStatus.ACTIVE.value,
        index=True,
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    left_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def to_domain(self) -> GroupMembership:
        return GroupMembership(
            id=UUID(str(self.id)),
            group_id=UUID(self.group_id),
            student_id=UUID(self.student_id),
            status=GroupMembershipStatus(self.status),
            joined_at=self.joined_at,
            left_at=self.left_at,
            created_at=self.created_at,
        )
