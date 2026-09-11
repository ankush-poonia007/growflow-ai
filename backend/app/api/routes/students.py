"""
GrowFlow — Student Profile Route Endpoints.

Implements /api/v1/students/me per Phase 6C.

Architecture ref:
  6C § 10 — User and Profile APIs (students/me)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, status

from backend.app.api.dependencies.auth import RequireStudent  # noqa: TC001
from backend.app.api.dependencies.services import ProfileServiceDep  # noqa: TC001
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.profile import (
    StudentProfileResponseSchema,
    StudentProfileUpdateSchema,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/students", tags=["Students"])


@router.get(
    "/me",
    summary="Get Student Profile and Skills",
    response_model=StudentProfileResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_student_me(
    current_user: RequireStudent,
    profile_service: ProfileServiceDep,
) -> JSONResponse:
    profile, technologies = await profile_service.get_or_create_student_profile(
        current_user.user_id
    )
    tech_data = [
        {
            "id": str(t.id),
            "technology_id": str(t.technology_id),
            "proficiency": t.proficiency,
            "relationship_type": t.relationship_type,
        }
        for t in technologies
    ]
    data = StudentProfileResponseSchema(
        user_id=str(profile.user_id),
        student_id=profile.student_id,
        bio=profile.bio,
        goals=profile.goals,
        interests=profile.interests,
        technologies=tech_data,
    ).model_dump()
    return success_response(message="Student profile retrieved.", data=data)


@router.patch(
    "/me",
    summary="Update Student Profile and Skills",
    response_model=StudentProfileResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_student_me(
    payload: StudentProfileUpdateSchema,
    current_user: RequireStudent,
    profile_service: ProfileServiceDep,
) -> JSONResponse:
    tech_dicts = None
    if payload.technologies is not None:
        tech_dicts = [t.model_dump() for t in payload.technologies]

    profile, technologies = await profile_service.update_student_profile(
        user_id=current_user.user_id,
        bio=payload.bio,
        goals=payload.goals,
        interests=payload.interests,
        technologies=tech_dicts,
    )
    tech_data = [
        {
            "id": str(t.id),
            "technology_id": str(t.technology_id),
            "proficiency": t.proficiency,
            "relationship_type": t.relationship_type,
        }
        for t in technologies
    ]
    data = StudentProfileResponseSchema(
        user_id=str(profile.user_id),
        student_id=profile.student_id,
        bio=profile.bio,
        goals=profile.goals,
        interests=profile.interests,
        technologies=tech_data,
    ).model_dump()
    return success_response(message="Student profile updated.", data=data)
