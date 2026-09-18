"""
GrowFlow — Group Route Endpoints.

Implements /api/v1/groups, /api/v1/groups/{id}, /api/v1/groups/join, /api/v1/groups/{id}/students.

Architecture ref:
  6C § 11 — Group APIs
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Query, status

from backend.app.api.dependencies.auth import (  # noqa: TC001
    CurrentUserDep,
    RequireMentor,
    RequireStudent,
)
from backend.app.api.dependencies.correlation import CorrelationIdDep  # noqa: TC001
from backend.app.api.dependencies.services import (  # noqa: TC001
    ActivityServiceDep,
    GroupServiceDep,
    MentorAIServiceDep,
    ProjectServiceDep,
)
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.group import (
    GroupCreateSchema,
    GroupJoinSchema,
    GroupMembershipResponseSchema,
    GroupResponseSchema,
    GroupStudentResponseSchema,
    GroupUpdateSchema,
)
from backend.app.api.schemas.mentor_supervision import (
    MentorAIChatPayload,
    MentorAIChatResponse,
    MentorAIStatusResponse,
)
from backend.app.api.schemas.project import ProjectResponseSchema


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
            mentor_name=getattr(g, "mentor_name", None),
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
    res = await group_service.join_group(
        student_id=current_user.user_id,
        join_code=payload.join_code,
        correlation_id=correlation_id,
    )
    if isinstance(res, tuple):
        membership, group = res
        group_name = getattr(group, "name", None)
        join_code = getattr(group, "join_code", None)
    else:
        membership = res
        group_name = getattr(membership, "group_name", None)
        join_code = getattr(membership, "join_code", None)

    data = GroupMembershipResponseSchema(
        id=str(membership.id),
        group_id=str(membership.group_id),
        student_id=str(membership.student_id),
        status=membership.status,
        joined_at=membership.joined_at,
        left_at=membership.left_at,
        group_name=group_name,
        join_code=join_code,
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


@router.get(
    "/{group_id}/projects",
    summary="List Projects in a Group",
    response_model=list[ProjectResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_group_projects(
    group_id: UUID,
    current_user: CurrentUserDep,
    project_service: ProjectServiceDep,
) -> JSONResponse:
    projects = await project_service.list_group_projects(group_id, current_user)
    data = [
        ProjectResponseSchema(
            id=str(p.id),
            student_id=str(p.student_id),
            group_id=str(p.group_id) if p.group_id else None,
            project_definition_id=str(p.project_definition_id) if p.project_definition_id else None,
            source_definition_version_id=str(p.source_definition_version_id) if p.source_definition_version_id else None,
            name=p.name,
            problem=p.problem,
            proposed_solution=p.proposed_solution,
            complexity=p.complexity,
            current_phase=p.current_phase,
            health=p.health,
            progress_percentage=p.progress_percentage,
            status=p.status,
            deadline=p.deadline,
            started_at=p.started_at,
            completed_at=p.completed_at,
            created_at=p.created_at,
            updated_at=p.updated_at,
        ).model_dump()
        for p in projects
    ]
    return success_response(message="Group projects retrieved.", data=data)


# ============================================================================
# M08: Supervised Group Activity
# ============================================================================
@router.get(
    "/{group_id}/activity",
    summary="List Supervised Group Activity (M08)",
    status_code=status.HTTP_200_OK,
)
async def list_group_activity(
    group_id: UUID,
    current_user: RequireMentor,
    activity_service: ActivityServiceDep,
    limit: int = Query(50, ge=1, le=100, description="Max events to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> JSONResponse:
    activity = await activity_service.get_group_activity(
        group_id=group_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return success_response(
        message="Group activity retrieved.",
        data=activity,
    )


# ============================================================================
# M09: Group AI Mentor Status & Chat
# ============================================================================
@router.get(
    "/{group_id}/ai/status",
    summary="Get Group AI Mentor Availability Status (M09)",
    response_model=MentorAIStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_group_ai_status(
    group_id: UUID,
    current_user: RequireMentor,
    mentor_ai_service: MentorAIServiceDep,
) -> JSONResponse:
    status_info = await mentor_ai_service.get_group_ai_status(
        group_id=group_id,
        current_user=current_user,
    )
    return success_response(
        message="Group AI status retrieved.",
        data=status_info,
    )


@router.post(
    "/{group_id}/ai/chat",
    summary="Consult Group AI Mentor (M09)",
    response_model=MentorAIChatResponse,
    status_code=status.HTTP_200_OK,
)
async def chat_group_ai(
    group_id: UUID,
    payload: MentorAIChatPayload,
    current_user: RequireMentor,
    mentor_ai_service: MentorAIServiceDep,
) -> JSONResponse:
    result = await mentor_ai_service.chat_group(
        group_id=group_id,
        current_user=current_user,
        message=payload.message,
        history=payload.history,
    )
    return success_response(
        message="Group AI consultation response received.",
        data=result,
    )


