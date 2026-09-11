"""
GrowFlow — Outbox Service.

Encapsulates transactional domain event enqueueing within caller units of work.

Architecture ref:
  6A § 9  — Class-Based Architecture
  6B § 30 — Transactional outbox
  6H § 7  — Event contract
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.app.shared.events.domain_event import EventVisibility

if TYPE_CHECKING:
    import uuid

    from backend.app.infrastructure.database.models.outbox import DomainEventModel
    from backend.app.infrastructure.repositories.outbox_repository import OutboxRepository


class OutboxService:
    """Service providing transactional event enqueueing capabilities."""

    def __init__(self, outbox_repo: OutboxRepository) -> None:
        self._outbox_repo = outbox_repo

    async def emit(
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
        """Enqueue a domain event atomically in the current transaction session."""
        return await self._outbox_repo.enqueue_event(
            event_type=event_type,
            actor_role=actor_role,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
            project_instance_id=project_instance_id,
            group_id=group_id,
            visibility=visibility,
            metadata=metadata,
            correlation_id=correlation_id,
        )
