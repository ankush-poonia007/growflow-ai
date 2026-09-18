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

from sqlalchemy import func, or_, select

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

    async def list_by_project(
        self,
        project_id: uuid.UUID | str,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[DomainEventModel]:
        stmt = (
            select(DomainEventModel)
            .where(DomainEventModel.project_instance_id == str(project_id))
            .order_by(DomainEventModel.occurred_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def list_by_group(
        self,
        group_id: uuid.UUID | str,
        project_ids: Sequence[uuid.UUID | str] = (),
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[DomainEventModel]:
        str_pids = [str(p) for p in project_ids]
        conditions = [DomainEventModel.group_id == str(group_id)]
        if str_pids:
            conditions.append(DomainEventModel.project_instance_id.in_(str_pids))

        stmt = (
            select(DomainEventModel)
            .where(or_(*conditions))
            .order_by(DomainEventModel.occurred_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def list_by_student(
        self,
        student_id: uuid.UUID | str,
        supervised_project_ids: Sequence[uuid.UUID | str] = (),
        supervised_group_ids: Sequence[uuid.UUID | str] = (),
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[DomainEventModel]:
        str_pids = [str(p) for p in supervised_project_ids]
        str_gids = [str(g) for g in supervised_group_ids]
        if not str_pids and not str_gids:
            return []

        conditions = []
        scope_filters = []
        if str_pids:
            scope_filters.append(DomainEventModel.project_instance_id.in_(str_pids))
            conditions.append(DomainEventModel.project_instance_id.in_(str_pids))
        if str_gids:
            scope_filters.append(DomainEventModel.group_id.in_(str_gids))

        conditions.append(
            (DomainEventModel.actor_id == str(student_id)) & or_(*scope_filters)
        )

        stmt = (
            select(DomainEventModel)
            .where(or_(*conditions))
            .order_by(DomainEventModel.occurred_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def list_by_mentor_portfolio(
        self,
        mentor_id: uuid.UUID | str,
        supervised_group_ids: Sequence[uuid.UUID | str] = (),
        supervised_project_ids: Sequence[uuid.UUID | str] = (),
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[DomainEventModel]:
        str_gids = [str(g) for g in supervised_group_ids]
        str_pids = [str(p) for p in supervised_project_ids]

        conditions = [DomainEventModel.actor_id == str(mentor_id)]
        if str_gids:
            conditions.append(DomainEventModel.group_id.in_(str_gids))
        if str_pids:
            conditions.append(DomainEventModel.project_instance_id.in_(str_pids))

        stmt = (
            select(DomainEventModel)
            .where(or_(*conditions))
            .order_by(DomainEventModel.occurred_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def get_counts_by_status(self) -> dict[str, int]:
        """Aggregate outbox counts by status (pending, published, failed, total)."""
        stmt = (
            select(DomainEventModel.status, func.count(DomainEventModel.id))
            .group_by(DomainEventModel.status)
        )
        res = await self._session.execute(stmt)
        counts = {status: count for status, count in res.all()}
        total = sum(counts.values())
        return {
            "pending": counts.get(OutboxStatus.PENDING.value, 0),
            "published": counts.get(OutboxStatus.PUBLISHED.value, 0),
            "failed": counts.get(OutboxStatus.FAILED.value, 0),
            "total": total,
        }

    async def list_platform_events(
        self,
        *,
        search: str | None = None,
        actor_role: str | None = None,
        event_type: str | None = None,
        resource_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[DomainEventModel]:
        """List platform-wide domain events with optional governance filtering and pagination."""
        stmt = select(DomainEventModel)
        if actor_role and actor_role.upper() != "ALL":
            stmt = stmt.where(DomainEventModel.actor_role == actor_role.upper())
        if event_type and event_type.upper() != "ALL":
            stmt = stmt.where(DomainEventModel.event_type == event_type)
        if resource_type and resource_type.upper() != "ALL":
            stmt = stmt.where(DomainEventModel.resource_type == resource_type.lower())
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    DomainEventModel.event_type.ilike(term),
                    DomainEventModel.resource_id.ilike(term),
                    DomainEventModel.actor_id.ilike(term),
                    DomainEventModel.correlation_id.ilike(term),
                )
            )
        stmt = stmt.order_by(DomainEventModel.occurred_at.desc()).offset(offset).limit(limit)
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def count_platform_events(
        self,
        *,
        search: str | None = None,
        actor_role: str | None = None,
        event_type: str | None = None,
        resource_type: str | None = None,
    ) -> int:
        """Count platform-wide domain events matching governance filters."""
        stmt = select(func.count(DomainEventModel.id))
        if actor_role and actor_role.upper() != "ALL":
            stmt = stmt.where(DomainEventModel.actor_role == actor_role.upper())
        if event_type and event_type.upper() != "ALL":
            stmt = stmt.where(DomainEventModel.event_type == event_type)
        if resource_type and resource_type.upper() != "ALL":
            stmt = stmt.where(DomainEventModel.resource_type == resource_type.lower())
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    DomainEventModel.event_type.ilike(term),
                    DomainEventModel.resource_id.ilike(term),
                    DomainEventModel.actor_id.ilike(term),
                    DomainEventModel.correlation_id.ilike(term),
                )
            )
        res = await self._session.execute(stmt)
        return res.scalar_one() or 0

    async def list_recent_failures(self, limit: int = 10) -> Sequence[DomainEventModel]:
        """Retrieve recent failed or erroneous domain events."""
        stmt = (
            select(DomainEventModel)
            .where(
                or_(
                    DomainEventModel.status == OutboxStatus.FAILED.value,
                    DomainEventModel.last_error.isnot(None),
                )
            )
            .order_by(DomainEventModel.occurred_at.desc())
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def list_recent_events(self, limit: int = 10) -> Sequence[DomainEventModel]:
        """Retrieve latest platform domain events."""
        stmt = (
            select(DomainEventModel)
            .order_by(DomainEventModel.occurred_at.desc())
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


