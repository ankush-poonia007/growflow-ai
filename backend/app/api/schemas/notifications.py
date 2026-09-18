"""
GrowFlow — Notification API Request & Response Schemas (Batch 08 / Gate 13).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NotificationResponseSchema(BaseModel):
    """Response schema for a user notification."""

    id: str
    user_id: str
    actor_id: str | None = None
    actor_role: str | None = None
    title: str
    message: str
    notification_type: str
    category: str
    resource_type: str | None = None
    resource_id: str | None = None
    link: str
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime


class UnreadCountResponseSchema(BaseModel):
    """Response schema for unread count badge."""

    unread_count: int


class MarkAllReadResponseSchema(BaseModel):
    """Response schema after marking all notifications read."""

    marked_count: int
