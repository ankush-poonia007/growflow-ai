"""
GrowFlow — Group Route Endpoints.

Implements /api/v1/groups, /api/v1/groups/{id}, /api/v1/groups/join, /api/v1/groups/{id}/students.

Architecture ref:
  6C § 11 — Group APIs
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, status

from backend.app.api.dependencies.auth import (  # noqa: TC001
    CurrentUserDep,
    RequireMentor,
    RequireStudent,
)
from backend.app.api.dependencies.correlation import CorrelationIdDep  # noqa: TC001
from backend.app.api.dependencies.services import GroupServiceDep  # noqa: TC001
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.group import (
    GroupCreateSchema,
    GroupJoinSchema,
    GroupMembershipResponseSchema,
    GroupResponseSchema,
    GroupStudentResponseSchema,
    GroupUpdateSchema,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post(
    "",
    summary="Create a Mentor Group",
    response_model=GroupResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_group(
    payload: GroupCreateSchema,
    current_user: RequireMentor,
    group_service: GroupServiceDep,
    correlation_id: CorrelationIdDep,
) -> JSONResponse:
    group = await group_service.create_group(
        mentor_id=current_user.user_id,
        name=payload.name,
        correlation_id=correlation_id,
    )
    data = GroupResponseSchema(
        id=str(group.id),
        mentor_id=str(group.mentor_id),
        name=group.name,
        join_code=group.join_code,
        status=group.status,
        created_at=group.created_at,
        updated_at=group.updated_at,
    ).model_dump()
    return success_response(
        message="Group created successfully.",
        data=data,
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "",
    summary="List Groups for Current User",
    response_model=list[GroupResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_groups(
    current_user: CurrentUserDep,
    group_service: GroupServiceDep,
) -> JSONResponse:
    groups = await group_service.list_groups_for_user(current_user)
    data = [
        GroupResponseSchema(
            id=str(g.id),
            mentor_id=str(g.mentor_id),
            name=g.name,
            join_code=g.join_code,
            status=g.status,
            created_at=g.created_at,
            updated_at=g.updated_at,
        ).model_dump()
        for g in groups
    ]
    return success_response(message="Groups retrieved.", data=data)


@router.get(
    "/{group_id}",
    summary="Get Group Details",
    response_model=GroupResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_group(
    group_id: UUID,
    current_user: CurrentUserDep,
    group_service: GroupServiceDep,
) -> JSONResponse:
    group = await group_service.get_group(group_id, current_user)
    data = GroupResponseSchema(
        id=str(group.id),
        mentor_id=str(group.mentor_id),
        name=group.name,
        join_code=group.join_code,
        status=group.status,
        created_at=group.created_at,
        updated_at=group.updated_at,
    ).model_dump()
    return success_response(message="Group details retrieved.", data=data)


@router.patch(
    "/{group_id}",
    summary="Update Group Details",
    response_model=GroupResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_group(
    group_id: UUID,
    payload: GroupUpdateSchema,
    current_user: RequireMentor,
    group_service: GroupServiceDep,
) -> JSONResponse:
    group = await group_service.update_group(
        group_id=group_id,
        current_user=current_user,
        name=payload.name,
        status=payload.status,
    )
    data = GroupResponseSchema(
        id=str(group.id),
        mentor_id=str(group.mentor_id),
        name=group.name,
        join_code=group.join_code,
        status=group.status,
        created_at=group.created_at,
        updated_at=group.updated_at,
    ).model_dump()
    return success_response(message="Group updated successfully.", data=data)


@router.post(
    "/join",
    summary="Student Join Group via Join Code",
    response_model=GroupMembershipResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def join_group(
    payload: GroupJoinSchema,
    current_user: RequireStudent,
    group_service: GroupServiceDep,
    correlation_id: CorrelationIdDep,
) -> JSONResponse:
    membership = await group_service.join_group(
        student_id=current_user.user_id,
        join_code=payload.join_code,
        correlation_id=correlation_id,
    )
    data = GroupMembershipResponseSchema(
        id=str(membership.id),
        group_id=str(membership.group_id),
        student_id=str(membership.student_id),
        status=membership.status,
        joined_at=membership.joined_at,
        left_at=membership.left_at,
    ).model_dump()
    return success_response(message="Joined group successfully.", data=data)


@router.get(
    "/{group_id}/students",
    summary="List Students in a Group",
    response_model=list[GroupStudentResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_group_students(
    group_id: UUID,
    current_user: CurrentUserDep,
    group_service: GroupServiceDep,
) -> JSONResponse:
    members = await group_service.list_group_students(group_id, current_user)
    data = [
        GroupStudentResponseSchema(
            student_id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            status=m.status,
            joined_at=m.joined_at,
        ).model_dump()
        for m, user in members
    ]
    return success_response(message="Group students retrieved.", data=data)
