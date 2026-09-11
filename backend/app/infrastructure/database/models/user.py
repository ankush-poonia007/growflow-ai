"""
GrowFlow — User ORM Model.

SQLAlchemy ORM model for the users table.
Represents canonical application identity and links to Supabase Auth UUID.

Architecture ref:
  6B § 5.1 — Canonical application identity record
  6D § 3-4 — Supabase Auth User UUID -> GrowFlow users.id
  6D § 7   — Roles: ADMIN, MENTOR, STUDENT
  6D § 8   — Account statuses: ACTIVE, INACTIVE, SUSPENDED
"""

from __future__ import annotations

from datetime import (  # noqa: TC003 — evaluated at runtime by SQLAlchemy mapper
    datetime,
)
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.domain.identity.models import AccountStatus, CurrentUser, UserRole
from backend.app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    SQLAlchemy model representing the canonical users table.

    Links 1-to-1 with Supabase Auth User UUID via the id column.
    Stores application-authoritative role and lifecycle status.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="",
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=UserRole.STUDENT.value,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=AccountStatus.ACTIVE.value,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        default=None,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    def to_current_user(self) -> CurrentUser:
        """Convert ORM record into immutable domain CurrentUser representation."""
        return CurrentUser(
            user_id=UUID(str(self.id)),
            email=self.email,
            role=UserRole(self.role),
            status=AccountStatus(self.status),
            full_name=self.full_name or "",
        )

    def __repr__(self) -> str:
        return f"<UserModel id={self.id} email={self.email} role={self.role} status={self.status}>"
