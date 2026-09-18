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
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    import uuid

    from backend.app.application.services.notification_service import NotificationService
    from backend.app.infrastructure.database.models.outbox import DomainEventModel
    from backend.app.infrastructure.repositories.outbox_repository import OutboxRepository

logger = get_logger("growflow.application.outbox_service")


class OutboxService:
    """Service providing transactional event enqueueing capabilities."""

    def __init__(
        self,
        outbox_repo: OutboxRepository,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._outbox_repo = outbox_repo
        self._notification_service = notification_service

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
        event = await self._outbox_repo.enqueue_event(
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

        if self._notification_service:
            try:
                await self._notification_service.handle_domain_event(event)
                await self._outbox_repo.mark_published(event.id)
            except Exception as exc:
                # Preserve business transaction behavior: record failure through mark_failed without silently swallowing
                logger.warning(
                    "Outbox notification processing failed for event %s: %s",
                    event.id,
                    str(exc),
                )
                await self._outbox_repo.mark_failed(event.id, error=str(exc))
        else:
            await self._outbox_repo.mark_published(event.id)

        return event

    enqueue = emit
