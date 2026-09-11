"""
GrowFlow — Transactional Outbox / Domain Event SQLAlchemy ORM Model.

Defines the ORM mapping for the domain_events table.
Supports atomic domain event persistence within database business transactions.

Architecture ref:
  6B § 29 — domain_events
  6B § 30 — Transactional outbox
  6H § 7  — Event contract fields
  6H § 13 — Outbox storage
"""

from __future__ import annotations

from datetime import (  # noqa: TC003 — evaluated at runtime by SQLAlchemy mapper
    datetime,
)
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base, UUIDPrimaryKeyMixin
from backend.app.shared.events.domain_event import (
    DomainEvent,
    EventVisibility,
    OutboxStatus,
)

JSON_TYPE = JSON().with_variant(postgresql.JSONB(), "postgresql")


class DomainEventModel(Base, UUIDPrimaryKeyMixin):
    """SQLAlchemy model for domain_events table."""

    __tablename__ = "domain_events"

    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    actor_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    actor_role: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False)
    project_instance_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        default=None,
    )
    group_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("groups.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        default=None,
    )
    visibility: Mapped[str] = mapped_column(
        String(50),
        default=EventVisibility.INTERNAL.value,
        nullable=False,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON_TYPE,
        default=dict,
        nullable=False,
    )
    correlation_id: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=OutboxStatus.PENDING.value,
        index=True,
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    def to_domain(self) -> DomainEvent:
        return DomainEvent(
            id=UUID(str(self.id)),
            event_type=self.event_type,
            actor_id=UUID(self.actor_id) if self.actor_id else None,
            actor_role=self.actor_role,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
            project_instance_id=UUID(self.project_instance_id)
            if self.project_instance_id
            else None,
            group_id=UUID(self.group_id) if self.group_id else None,
            visibility=EventVisibility(self.visibility),
            metadata=self.metadata_json or {},
            correlation_id=self.correlation_id,
            status=OutboxStatus(self.status),
            occurred_at=self.occurred_at,
            published_at=self.published_at,
            attempt_count=self.attempt_count,
            last_error=self.last_error,
        )
