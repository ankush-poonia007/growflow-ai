"""
GrowFlow — Mentor Profile Route Endpoints.

Implements /api/v1/mentors/me per Phase 6C.

Architecture ref:
  6C § 10 — User and Profile APIs (mentors/me)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, status

from backend.app.api.dependencies.auth import RequireMentor  # noqa: TC001
from backend.app.api.dependencies.services import ProfileServiceDep  # noqa: TC001
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.profile import (
    MentorProfileResponseSchema,
    MentorProfileUpdateSchema,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/mentors", tags=["Mentors"])


@router.get(
    "/me",
    summary="Get Mentor Profile",
    response_model=MentorProfileResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_mentor_me(
    current_user: RequireMentor,
    profile_service: ProfileServiceDep,
) -> JSONResponse:
    profile = await profile_service.get_or_create_mentor_profile(current_user.user_id)
    data = MentorProfileResponseSchema(
        user_id=str(profile.user_id),
        mentor_id=profile.mentor_id,
        bio=profile.bio,
        specialization=profile.specialization,
    ).model_dump()
    return success_response(message="Mentor profile retrieved.", data=data)


@router.patch(
    "/me",
    summary="Update Mentor Profile",
    response_model=MentorProfileResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_mentor_me(
    payload: MentorProfileUpdateSchema,
    current_user: RequireMentor,
    profile_service: ProfileServiceDep,
) -> JSONResponse:
    profile = await profile_service.update_mentor_profile(
        user_id=current_user.user_id,
        bio=payload.bio,
        specialization=payload.specialization,
    )
    data = MentorProfileResponseSchema(
        user_id=str(profile.user_id),
        mentor_id=profile.mentor_id,
        bio=profile.bio,
        specialization=profile.specialization,
    ).model_dump()
    return success_response(message="Mentor profile updated.", data=data)
