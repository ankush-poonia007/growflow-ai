"""
GrowFlow — Authentication & Identity Endpoints.

Implements the canonical authenticated identity endpoint (/api/v1/auth/me)
and foundational role/resource-protected route boundaries.

Architecture ref:
  6C § 9  — Authentication APIs: GET /api/v1/auth/me
  6D § 14 — get_current_user context
  6D § 16 — Role-based access control
  6D § 17 — Resource authorization
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, status

from backend.app.api.dependencies.auth import (  # noqa: TC001 — FastAPI runtime dependency injection
    CurrentUserDep,
    RequireAdmin,
    RequireMentor,
    RequireStudent,
)
from backend.app.api.responses.base import success_response
from backend.app.domain.identity import verify_resource_ownership

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/me",
    summary="Get Authenticated User Identity",
    description="Returns the profile, application role, and status of the current authenticated user.",
    status_code=status.HTTP_200_OK,
)
async def get_current_user_profile(current_user: CurrentUserDep) -> JSONResponse:
    """Return the authenticated user's canonical identity."""
    return success_response(
        message="Authenticated user identity retrieved successfully.",
        data={
            "id": str(current_user.user_id),
            "email": current_user.email,
            "role": current_user.role.value,
            "status": current_user.status.value,
            "full_name": current_user.full_name,
        },
    )


@router.get(
    "/student-only",
    summary="Student Protected Resource",
    description="Foundational protected endpoint requiring STUDENT role.",
    status_code=status.HTTP_200_OK,
)
async def student_only_endpoint(current_user: RequireStudent) -> JSONResponse:
    """Protected route accessible only to users with STUDENT role."""
    return success_response(
        message="Student access granted.",
        data={"user_id": str(current_user.user_id), "role": current_user.role.value},
    )


@router.get(
    "/mentor-only",
    summary="Mentor Protected Resource",
    description="Foundational protected endpoint requiring MENTOR role.",
    status_code=status.HTTP_200_OK,
)
async def mentor_only_endpoint(current_user: RequireMentor) -> JSONResponse:
    """Protected route accessible only to users with MENTOR role."""
    return success_response(
        message="Mentor access granted.",
        data={"user_id": str(current_user.user_id), "role": current_user.role.value},
    )


@router.get(
    "/admin-only",
    summary="Admin Protected Resource",
    description="Foundational protected endpoint requiring ADMIN role.",
    status_code=status.HTTP_200_OK,
)
async def admin_only_endpoint(current_user: RequireAdmin) -> JSONResponse:
    """Protected route accessible only to users with ADMIN role."""
    return success_response(
        message="Admin access granted.",
        data={"user_id": str(current_user.user_id), "role": current_user.role.value},
    )


@router.get(
    "/resource/{owner_id}",
    summary="Resource Ownership Protected Resource",
    description="Foundational resource-protected endpoint verifying ownership boundary.",
    status_code=status.HTTP_200_OK,
)
async def resource_ownership_endpoint(
    owner_id: str,
    current_user: CurrentUserDep,
) -> JSONResponse:
    """Protected route verifying resource ownership against current user identity."""
    verify_resource_ownership(current_user, owner_id)
    return success_response(
        message="Resource access granted.",
        data={"resource_owner_id": owner_id, "requester_id": str(current_user.user_id)},
    )
