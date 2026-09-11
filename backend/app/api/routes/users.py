"""
GrowFlow — User & Preferences Route Endpoints.

Implements /api/v1/users/me and /api/v1/users/me/preferences per Phase 6C.

Architecture ref:
  6C § 10 — User and Profile APIs
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, status

from backend.app.api.dependencies.auth import CurrentUserDep  # noqa: TC001
from backend.app.api.dependencies.services import ProfileServiceDep  # noqa: TC001
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.profile import (
    UserPreferencesResponseSchema,
    UserPreferencesUpdateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    summary="Get Authenticated User Profile",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user_me(
    current_user: CurrentUserDep,
    profile_service: ProfileServiceDep,
) -> JSONResponse:
    user = await profile_service.get_user_self(current_user.user_id)
    payload = UserResponseSchema(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        status=user.status,
        avatar_url=user.avatar_url,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    ).model_dump()
    return success_response(message="User profile retrieved.", data=payload)


@router.patch(
    "/me",
    summary="Update Authenticated User Profile",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user_me(
    payload: UserUpdateSchema,
    current_user: CurrentUserDep,
    profile_service: ProfileServiceDep,
) -> JSONResponse:
    user = await profile_service.update_user_self(
        user_id=current_user.user_id,
        full_name=payload.full_name,
        avatar_url=payload.avatar_url,
    )
    data = UserResponseSchema(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        status=user.status,
        avatar_url=user.avatar_url,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    ).model_dump()
    return success_response(message="User profile updated.", data=data)


@router.get(
    "/me/preferences",
    summary="Get User Preferences",
    response_model=UserPreferencesResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_preferences(
    current_user: CurrentUserDep,
    profile_service: ProfileServiceDep,
) -> JSONResponse:
    prefs = await profile_service.get_or_create_preferences(current_user.user_id)
    data = UserPreferencesResponseSchema(
        user_id=str(prefs.user_id),
        email_notifications=prefs.email_notifications,
        timezone=prefs.timezone,
        preferences=prefs.preferences or {},
    ).model_dump()
    return success_response(message="User preferences retrieved.", data=data)


@router.patch(
    "/me/preferences",
    summary="Update User Preferences",
    response_model=UserPreferencesResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_preferences(
    payload: UserPreferencesUpdateSchema,
    current_user: CurrentUserDep,
    profile_service: ProfileServiceDep,
) -> JSONResponse:
    prefs = await profile_service.update_preferences(
        user_id=current_user.user_id,
        email_notifications=payload.email_notifications,
        timezone=payload.timezone,
        preferences=payload.preferences,
    )
    data = UserPreferencesResponseSchema(
        user_id=str(prefs.user_id),
        email_notifications=prefs.email_notifications,
        timezone=prefs.timezone,
        preferences=prefs.preferences or {},
    ).model_dump()
    return success_response(message="User preferences updated.", data=data)
