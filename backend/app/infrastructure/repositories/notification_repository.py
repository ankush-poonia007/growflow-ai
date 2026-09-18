"""
GrowFlow — Notification Repository Implementation (Batch 08 / Gate 13).

Provides persistence operations for recipient-specific user notifications,
supporting unread counts, pagination, and atomic read-status transitions.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import func, select, update

from backend.app.infrastructure.database.models.notification import NotificationModel
from backend.app.infrastructure.repositories.base import BaseRepository

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession


class NotificationRepository(BaseRepository[NotificationModel]):
    """Repository managing user notifications and read lifecycle states."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model_class=NotificationModel)

    async def create_notification(
        self,
        *,
        user_id: uuid.UUID | str,
        title: str,
        message: str,
        notification_type: str,
        category: str = "SYSTEM",
        actor_id: uuid.UUID | str | None = None,
        actor_role: str | None = None,
        resource_type: str | None = None,
        resource_id: uuid.UUID | str | None = None,
        link: str = "",
        event_id: uuid.UUID | str | None = None,
    ) -> NotificationModel:
        """
        Create a new notification with deduplication on event_id.
        If an event with event_id was already converted to a notification, returns the existing record.
        """
        if event_id:
            existing = await self.get_by_event_id(event_id, user_id=user_id)
            if existing:
                return existing

        notification = NotificationModel(
            id=uuid.uuid4(),
            user_id=str(user_id),
            actor_id=str(actor_id) if actor_id else None,
            actor_role=actor_role,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            link=link,
            is_read=False,
            read_at=None,
            event_id=str(event_id) if event_id else None,
        )
        return await self.add(notification)

    async def get_by_event_id(
        self,
        event_id: uuid.UUID | str,
        user_id: uuid.UUID | str | None = None,
    ) -> NotificationModel | None:
        """Find notification by originating domain event ID, optionally scoped to a recipient user."""
        stmt = select(NotificationModel).where(NotificationModel.event_id == str(event_id))
        if user_id is not None:
            stmt = stmt.where(NotificationModel.user_id == str(user_id))
        res = await self._session.execute(stmt)
        return res.scalars().first()

    async def list_by_user(
        self,
        user_id: uuid.UUID | str,
        *,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False,
    ) -> Sequence[NotificationModel]:
        """List notifications for user ordered newest first with optional unread filter."""
        stmt = select(NotificationModel).where(NotificationModel.user_id == str(user_id))
        if unread_only:
            stmt = stmt.where(NotificationModel.is_read.is_(False))
        stmt = stmt.order_by(NotificationModel.created_at.desc()).offset(offset).limit(limit)
        res = await self._session.execute(stmt)
        return res.scalars().all()

    async def count_unread(self, user_id: uuid.UUID | str) -> int:
        """Count unread notifications for a specific user."""
        stmt = (
            select(func.count())
            .select_from(NotificationModel)
            .where(
                NotificationModel.user_id == str(user_id),
                NotificationModel.is_read.is_(False),
            )
        )
        res = await self._session.execute(stmt)
        return res.scalar_one() or 0

    async def mark_read(
        self,
        notification_id: uuid.UUID | str,
        user_id: uuid.UUID | str,
    ) -> NotificationModel | None:
        """
        Mark a single notification as read.
        Enforces user_id ownership so cross-user mutation is impossible.
        Idempotent: if already read, leaves read_at intact and returns the model.
        """
        stmt = select(NotificationModel).where(
            NotificationModel.id == str(notification_id),
            NotificationModel.user_id == str(user_id),
        )
        res = await self._session.execute(stmt)
        notification = res.scalar_one_or_none()
        if not notification:
            return None

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(UTC)
            await self._session.flush()

        return notification

    async def mark_all_read(self, user_id: uuid.UUID | str) -> int:
        """
        Mark all unread notifications for a specific user as read.
        Returns the number of notifications marked read.
        """
        now = datetime.now(UTC)
        stmt = (
            update(NotificationModel)
            .where(
                NotificationModel.user_id == str(user_id),
                NotificationModel.is_read.is_(False),
            )
            .values(is_read=True, read_at=now)
        )
        res = await self._session.execute(stmt)
        await self._session.flush()
        return res.rowcount or 0
