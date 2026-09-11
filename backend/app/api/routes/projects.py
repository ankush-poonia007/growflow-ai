"""
GrowFlow — Project Instance Route Endpoints.

Implements /api/v1/projects and lifecycle/overview sub-resources.

Architecture ref:
  6C § 13 — Project Instance APIs
  6C § 14 — Project Overview API
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, status

from backend.app.api.dependencies.auth import (  # noqa: TC001
    CurrentUserDep,
    RequireStudent,
)
from backend.app.api.dependencies.correlation import CorrelationIdDep  # noqa: TC001
from backend.app.api.dependencies.services import ProjectServiceDep  # noqa: TC001
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.project import (
    ProjectCreateSchema,
    ProjectHealthUpdateSchema,
    ProjectOverviewResponseSchema,
    ProjectPhaseTransitionSchema,
    ProjectResponseSchema,
    ProjectUpdateSchema,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    summary="Create Independent Student Project",
    response_model=ProjectResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    payload: ProjectCreateSchema,
    current_user: RequireStudent,
    project_service: ProjectServiceDep,
    correlation_id: CorrelationIdDep,
) -> JSONResponse:
    project = await project_service.create_project(
        student_id=current_user.user_id,
        name=payload.name,
        problem=payload.problem,
        proposed_solution=payload.proposed_solution,
        complexity=payload.complexity,
        technologies=payload.technologies,
        deadline=payload.deadline,
        group_id=UUID(payload.group_id) if payload.group_id else None,
        correlation_id=correlation_id,
    )
    data = ProjectResponseSchema(
        id=str(project.id),
        student_id=str(project.student_id),
        group_id=str(project.group_id) if project.group_id else None,
        project_definition_id=str(project.project_definition_id)
        if project.project_definition_id
        else None,
        source_definition_version_id=str(project.source_definition_version_id)
        if project.source_definition_version_id
        else None,
        name=project.name,
        problem=project.problem,
        proposed_solution=project.proposed_solution,
        complexity=project.complexity,
        current_phase=project.current_phase,
        health=project.health,
        progress_percentage=project.progress_percentage,
        status=project.status,
        deadline=project.deadline,
        started_at=project.started_at,
        completed_at=project.completed_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
    ).model_dump()
    return success_response(
        message="Project created successfully.",
        data=data,
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "",
    summary="List Projects for User",
    response_model=list[ProjectResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_projects(
    current_user: CurrentUserDep,
    project_service: ProjectServiceDep,
) -> JSONResponse:
    projects = await project_service.list_projects_for_user(current_user)
    data = [
        ProjectResponseSchema(
            id=str(p.id),
            student_id=str(p.student_id),
            group_id=str(p.group_id) if p.group_id else None,
            project_definition_id=str(p.project_definition_id) if p.project_definition_id else None,
            source_definition_version_id=str(p.source_definition_version_id)
            if p.source_definition_version_id
            else None,
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
    return success_response(message="Projects retrieved.", data=data)


@router.get(
    "/{project_id}",
    summary="Get Project Details",
    response_model=ProjectResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_project(
    project_id: UUID,
    current_user: CurrentUserDep,
    project_service: ProjectServiceDep,
) -> JSONResponse:
    project = await project_service.get_project(project_id, current_user)
    data = ProjectResponseSchema(
        id=str(project.id),
        student_id=str(project.student_id),
        group_id=str(project.group_id) if project.group_id else None,
        project_definition_id=str(project.project_definition_id)
        if project.project_definition_id
        else None,
        source_definition_version_id=str(project.source_definition_version_id)
        if project.source_definition_version_id
        else None,
        name=project.name,
        problem=project.problem,
        proposed_solution=project.proposed_solution,
        complexity=project.complexity,
        current_phase=project.current_phase,
        health=project.health,
        progress_percentage=project.progress_percentage,
        status=project.status,
        deadline=project.deadline,
        started_at=project.started_at,
        completed_at=project.completed_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
    ).model_dump()
    return success_response(message="Project retrieved.", data=data)


@router.patch(
    "/{project_id}",
    summary="Update Project Details",
    response_model=ProjectResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdateSchema,
    current_user: CurrentUserDep,
    project_service: ProjectServiceDep,
) -> JSONResponse:
    project = await project_service.update_project(
        project_id=project_id,
        current_user=current_user,
        name=payload.name,
        problem=payload.problem,
        proposed_solution=payload.proposed_solution,
        complexity=payload.complexity,
        deadline=payload.deadline,
    )
    data = ProjectResponseSchema(
        id=str(project.id),
        student_id=str(project.student_id),
        group_id=str(project.group_id) if project.group_id else None,
        project_definition_id=str(project.project_definition_id)
        if project.project_definition_id
        else None,
        source_definition_version_id=str(project.source_definition_version_id)
        if project.source_definition_version_id
        else None,
        name=project.name,
        problem=project.problem,
        proposed_solution=project.proposed_solution,
        complexity=project.complexity,
        current_phase=project.current_phase,
        health=project.health,
        progress_percentage=project.progress_percentage,
        status=project.status,
        deadline=project.deadline,
        started_at=project.started_at,
        completed_at=project.completed_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
    ).model_dump()
    return success_response(message="Project updated.", data=data)


@router.post(
    "/{project_id}/phase",
    summary="Transition Project Lifecycle Phase",
    response_model=ProjectResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def transition_project_phase(
    project_id: UUID,
    payload: ProjectPhaseTransitionSchema,
    current_user: CurrentUserDep,
    project_service: ProjectServiceDep,
    correlation_id: CorrelationIdDep,
) -> JSONResponse:
    project = await project_service.transition_phase(
        project_id=project_id,
        current_user=current_user,
        target_phase=payload.target_phase,
        reason=payload.reason,
        correlation_id=correlation_id,
    )
    data = ProjectResponseSchema(
        id=str(project.id),
        student_id=str(project.student_id),
        group_id=str(project.group_id) if project.group_id else None,
        project_definition_id=str(project.project_definition_id)
        if project.project_definition_id
        else None,
        source_definition_version_id=str(project.source_definition_version_id)
        if project.source_definition_version_id
        else None,
        name=project.name,
        problem=project.problem,
        proposed_solution=project.proposed_solution,
        complexity=project.complexity,
        current_phase=project.current_phase,
        health=project.health,
        progress_percentage=project.progress_percentage,
        status=project.status,
        deadline=project.deadline,
        started_at=project.started_at,
        completed_at=project.completed_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
    ).model_dump()
    return success_response(
        message=f"Project transitioned to phase '{project.current_phase}'.",
        data=data,
    )


@router.post(
    "/{project_id}/health",
    summary="Update Project Health Indicator",
    response_model=ProjectResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_project_health(
    project_id: UUID,
    payload: ProjectHealthUpdateSchema,
    current_user: CurrentUserDep,
    project_service: ProjectServiceDep,
    correlation_id: CorrelationIdDep,
) -> JSONResponse:
    project = await project_service.update_health(
        project_id=project_id,
        current_user=current_user,
        new_health=payload.health,
        reason=payload.reason,
        correlation_id=correlation_id,
    )
    data = ProjectResponseSchema(
        id=str(project.id),
        student_id=str(project.student_id),
        group_id=str(project.group_id) if project.group_id else None,
        project_definition_id=str(project.project_definition_id)
        if project.project_definition_id
        else None,
        source_definition_version_id=str(project.source_definition_version_id)
        if project.source_definition_version_id
        else None,
        name=project.name,
        problem=project.problem,
        proposed_solution=project.proposed_solution,
        complexity=project.complexity,
        current_phase=project.current_phase,
        health=project.health,
        progress_percentage=project.progress_percentage,
        status=project.status,
        deadline=project.deadline,
        started_at=project.started_at,
        completed_at=project.completed_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
    ).model_dump()
    return success_response(
        message=f"Project health updated to '{project.health}'.",
        data=data,
    )


@router.get(
    "/{project_id}/overview",
    summary="Get Aggregated Project Workspace Overview",
    response_model=ProjectOverviewResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_project_overview(
    project_id: UUID,
    current_user: CurrentUserDep,
    project_service: ProjectServiceDep,
) -> JSONResponse:
    data = await project_service.get_project_overview(project_id, current_user)
    return success_response(
        message="Project overview retrieved.",
        data=data,
    )
