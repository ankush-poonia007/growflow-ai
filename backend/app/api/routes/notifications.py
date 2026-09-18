"""
GrowFlow — User Notifications Route Endpoints (Batch 08 / Gate 13).

Provides /api/v1/notifications endpoints for listing, unread counts,
and atomic read-state transitions adhering to Phase 8 Batch 3 specifications.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from fastapi import APIRouter, Path, Query, status

from backend.app.api.dependencies.auth import CurrentUserDep
from backend.app.api.dependencies.services import NotificationServiceDep
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.notifications import (
    MarkAllReadResponseSchema,
    NotificationResponseSchema,
    UnreadCountResponseSchema,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    summary="List Authenticated User Notifications",
    response_model=list[NotificationResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_notifications(
    current_user: CurrentUserDep,
    notification_service: NotificationServiceDep,
    limit: int = Query(20, ge=1, le=50, description="Max notifications to retrieve"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    unread_only: bool = Query(False, description="Filter for unread notifications only"),
) -> JSONResponse:
    """
    List newest notifications for authenticated caller with bounded pagination.
    Strictly isolated to current user's recipient ID.
    """
    notifications = await notification_service.get_user_notifications(
        current_user=current_user,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )
    payload = [
        NotificationResponseSchema(
            id=str(n.id),
            user_id=str(n.user_id),
            actor_id=str(n.actor_id) if n.actor_id else None,
            actor_role=n.actor_role,
            title=n.title,
            message=n.message,
            notification_type=n.notification_type,
            category=n.category,
            resource_type=n.resource_type,
            resource_id=str(n.resource_id) if n.resource_id else None,
            link=n.link,
            is_read=n.is_read,
            read_at=n.read_at,
            created_at=n.created_at,
        ).model_dump()
        for n in notifications
    ]
    return success_response(message="Notifications retrieved.", data=payload)


@router.get(
    "/unread-count",
    summary="Get Unread Notification Count",
    response_model=UnreadCountResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_unread_count(
    current_user: CurrentUserDep,
    notification_service: NotificationServiceDep,
) -> JSONResponse:
    """
    Lightweight query returning the number of unread notifications for header badging.
    """
    count = await notification_service.get_unread_count(current_user)
    payload = UnreadCountResponseSchema(unread_count=count).model_dump()
    return success_response(message="Unread notification count retrieved.", data=payload)


@router.patch(
    "/{id}/read",
    summary="Mark Notification As Read",
    response_model=NotificationResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def mark_notification_read(
    current_user: CurrentUserDep,
    notification_service: NotificationServiceDep,
    id: uuid.UUID = Path(..., description="Notification ID to mark read"),
) -> JSONResponse:
    """
    Idempotently transition notification to read status.
    Enforces that notification belongs to authenticated user (raises 404 otherwise).
    """
    notification = await notification_service.mark_as_read(id, current_user)
    payload = NotificationResponseSchema(
        id=str(notification.id),
        user_id=str(notification.user_id),
        actor_id=str(notification.actor_id) if notification.actor_id else None,
        actor_role=notification.actor_role,
        title=notification.title,
        message=notification.message,
        notification_type=notification.notification_type,
        category=notification.category,
        resource_type=notification.resource_type,
        resource_id=str(notification.resource_id) if notification.resource_id else None,
        link=notification.link,
        is_read=notification.is_read,
        read_at=notification.read_at,
        created_at=notification.created_at,
    ).model_dump()
    return success_response(message="Notification marked as read.", data=payload)


@router.post(
    "/mark-all-read",
    summary="Mark All Notifications As Read",
    response_model=MarkAllReadResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def mark_all_notifications_read(
    current_user: CurrentUserDep,
    notification_service: NotificationServiceDep,
) -> JSONResponse:
    """
    Mark all unread notifications for authenticated caller as read.
    """
    marked_count = await notification_service.mark_all_as_read(current_user)
    payload = MarkAllReadResponseSchema(marked_count=marked_count).model_dump()
    return success_response(message="All notifications marked as read.", data=payload)
