"""
GrowFlow — Outbox Repository Implementation.

Provides persistence operations for transactional domain event records
in the domain_events table.

Architecture ref:
  6A § 7 — Repository Architecture
  6B § 29 — domain_events
  6B § 30 — Transactional outbox
  6H § 7  — Event contract fields
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
import uuid

from sqlalchemy import select

from backend.app.infrastructure.database.models.outbox import DomainEventModel
from backend.app.infrastructure.repositories.base import BaseRepository
from backend.app.shared.events.domain_event import (
    EventVisibility,
    OutboxStatus,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class OutboxRepository(BaseRepository[DomainEventModel]):
    """Repository managing domain events and transactional outbox state."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=DomainEventModel)

    async def enqueue_event(
        self,
        event_type: str,
        actor_role: str,
        resource_type: str,
        resource_id: str,
        *,
        actor_id: uuid.UUID | str | None = None,
        project_instance_id: uuid.UUID | str | None = None,
        group_id: uuid.UUID | str | None = None,
        visibility: str = EventVisibility.INTERNAL.value,
        metadata: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> DomainEventModel:
        event = DomainEventModel(
            id=uuid.uuid4(),
            event_type=event_type,
            actor_id=str(actor_id) if actor_id else None,
            actor_role=actor_role,
            resource_type=resource_type,
            resource_id=str(resource_id),
            project_instance_id=str(project_instance_id) if project_instance_id else None,
            group_id=str(group_id) if group_id else None,
            visibility=visibility,
            metadata_json=metadata or {},
            correlation_id=correlation_id,
            status=OutboxStatus.PENDING.value,
        )
        return await self.add(event)

    async def list_pending(self, limit: int = 50) -> Sequence[DomainEventModel]:
        result = await self._session.execute(
            select(DomainEventModel)
            .where(DomainEventModel.status == OutboxStatus.PENDING.value)
            .order_by(DomainEventModel.occurred_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_published(self, event_id: uuid.UUID | str) -> None:
        event = await self.get_by_id(event_id)
        if event:
            event.status = OutboxStatus.PUBLISHED.value
            event.published_at = datetime.now(UTC)
            await self._session.flush()

    async def mark_failed(self, event_id: uuid.UUID | str, error: str) -> None:
        event = await self.get_by_id(event_id)
        if event:
            event.status = OutboxStatus.FAILED.value
            event.attempt_count += 1
            event.last_error = error
            await self._session.flush()
