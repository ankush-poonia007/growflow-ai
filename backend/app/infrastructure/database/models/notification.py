"""
GrowFlow — Notification ORM Model (Batch 08 / Gate 13).

Defines the canonical notifications table storing recipient-specific user notifications,
read/unread lifecycle states, and deep navigation links.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base, UUIDPrimaryKeyMixin


class NotificationModel(Base, UUIDPrimaryKeyMixin):
    """SQLAlchemy model for the notifications table."""

    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    actor_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    actor_role: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default=None,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        default="SYSTEM",
        nullable=False,
    )
    resource_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    resource_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        default=None,
    )
    link: Mapped[str] = mapped_column(
        String(500),
        default="",
        nullable=False,
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    event_id: Mapped[str | None] = mapped_column(
        String(36),
        unique=False,
        nullable=True,
        index=True,
    )

    __table_args__ = (
        Index("ix_notifications_user_unread", "user_id", "is_read", created_at.desc()),
        Index("ix_notifications_user_created", "user_id", created_at.desc()),
        UniqueConstraint("event_id", "user_id", name="uq_notifications_event_user"),
    )
