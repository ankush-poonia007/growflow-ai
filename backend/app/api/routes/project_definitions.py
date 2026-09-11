"""
GrowFlow — Project Definition Route Endpoints.

Implements /api/v1/project-definitions and version/assign sub-resources.

Architecture ref:
  6C § 12 — Project Definition APIs
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, status

from backend.app.api.dependencies.auth import (  # noqa: TC001
    CurrentUserDep,
    RequireMentor,
)
from backend.app.api.dependencies.correlation import CorrelationIdDep  # noqa: TC001
from backend.app.api.dependencies.services import ProjectDefinitionServiceDep  # noqa: TC001
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.project import ProjectResponseSchema
from backend.app.api.schemas.project_definition import (
    ProjectDefinitionAssignSchema,
    ProjectDefinitionCreateSchema,
    ProjectDefinitionResponseSchema,
    ProjectDefinitionUpdateSchema,
    ProjectDefinitionVersionResponseSchema,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/project-definitions", tags=["Project Definitions"])


@router.post(
    "",
    summary="Create Project Definition",
    response_model=ProjectDefinitionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_definition(
    payload: ProjectDefinitionCreateSchema,
    current_user: RequireMentor,
    definition_service: ProjectDefinitionServiceDep,
    correlation_id: CorrelationIdDep,
) -> JSONResponse:
    definition, version = await definition_service.create_definition(
        mentor_id=current_user.user_id,
        name=payload.name,
        problem=payload.problem,
        proposed_solution=payload.proposed_solution,
        complexity=payload.complexity,
        description=payload.description,
        duration=payload.duration,
        constraints=payload.constraints,
        assumptions=payload.assumptions,
        technology_snapshot=payload.technology_snapshot,
        correlation_id=correlation_id,
    )
    v_data = ProjectDefinitionVersionResponseSchema(
        id=str(version.id),
        project_definition_id=str(version.project_definition_id),
        version_number=version.version_number,
        name=version.name,
        problem=version.problem,
        proposed_solution=version.proposed_solution,
        complexity=version.complexity,
        description=version.description,
        duration=version.duration,
        constraints=version.constraints,
        assumptions=version.assumptions,
        technology_snapshot=version.technology_snapshot or [],
        created_by=str(version.created_by),
        created_at=version.created_at,
    )
    data = ProjectDefinitionResponseSchema(
        id=str(definition.id),
        owner_mentor_id=str(definition.owner_mentor_id),
        name=definition.name,
        status=definition.status,
        current_version_id=str(version.id),
        current_version=v_data,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
    ).model_dump()
    return success_response(
        message="Project definition created.",
        data=data,
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "",
    summary="List Project Definitions",
    response_model=list[ProjectDefinitionResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_project_definitions(
    current_user: RequireMentor,
    definition_service: ProjectDefinitionServiceDep,
) -> JSONResponse:
    definitions = await definition_service.list_definitions(current_user.user_id)
    data = [
        ProjectDefinitionResponseSchema(
            id=str(d.id),
            owner_mentor_id=str(d.owner_mentor_id),
            name=d.name,
            status=d.status,
            current_version_id=str(d.current_version_id) if d.current_version_id else None,
            created_at=d.created_at,
            updated_at=d.updated_at,
        ).model_dump()
        for d in definitions
    ]
    return success_response(message="Project definitions retrieved.", data=data)


@router.get(
    "/{definition_id}",
    summary="Get Project Definition Details",
    response_model=ProjectDefinitionResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_project_definition(
    definition_id: UUID,
    current_user: CurrentUserDep,
    definition_service: ProjectDefinitionServiceDep,
) -> JSONResponse:
    definition, version = await definition_service.get_definition(definition_id, current_user)
    v_data = None
    if version:
        v_data = ProjectDefinitionVersionResponseSchema(
            id=str(version.id),
            project_definition_id=str(version.project_definition_id),
            version_number=version.version_number,
            name=version.name,
            problem=version.problem,
            proposed_solution=version.proposed_solution,
            complexity=version.complexity,
            description=version.description,
            duration=version.duration,
            constraints=version.constraints,
            assumptions=version.assumptions,
            technology_snapshot=version.technology_snapshot or [],
            created_by=str(version.created_by),
            created_at=version.created_at,
        )
    data = ProjectDefinitionResponseSchema(
        id=str(definition.id),
        owner_mentor_id=str(definition.owner_mentor_id),
        name=definition.name,
        status=definition.status,
        current_version_id=str(definition.current_version_id)
        if definition.current_version_id
        else None,
        current_version=v_data,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
    ).model_dump()
    return success_response(message="Project definition details retrieved.", data=data)


@router.patch(
    "/{definition_id}",
    summary="Update Project Definition and Snapshot Version",
    response_model=ProjectDefinitionResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_project_definition(
    definition_id: UUID,
    payload: ProjectDefinitionUpdateSchema,
    current_user: RequireMentor,
    definition_service: ProjectDefinitionServiceDep,
) -> JSONResponse:
    definition, version = await definition_service.update_definition(
        definition_id=definition_id,
        current_user=current_user,
        name=payload.name,
        problem=payload.problem,
        proposed_solution=payload.proposed_solution,
        complexity=payload.complexity,
        description=payload.description,
        duration=payload.duration,
        constraints=payload.constraints,
        assumptions=payload.assumptions,
        technology_snapshot=payload.technology_snapshot,
    )
    v_data = ProjectDefinitionVersionResponseSchema(
        id=str(version.id),
        project_definition_id=str(version.project_definition_id),
        version_number=version.version_number,
        name=version.name,
        problem=version.problem,
        proposed_solution=version.proposed_solution,
        complexity=version.complexity,
        description=version.description,
        duration=version.duration,
        constraints=version.constraints,
        assumptions=version.assumptions,
        technology_snapshot=version.technology_snapshot or [],
        created_by=str(version.created_by),
        created_at=version.created_at,
    )
    data = ProjectDefinitionResponseSchema(
        id=str(definition.id),
        owner_mentor_id=str(definition.owner_mentor_id),
        name=definition.name,
        status=definition.status,
        current_version_id=str(version.id),
        current_version=v_data,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
    ).model_dump()
    return success_response(message="Project definition updated.", data=data)


@router.post(
    "/{definition_id}/archive",
    summary="Archive Project Definition",
    response_model=ProjectDefinitionResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def archive_project_definition(
    definition_id: UUID,
    current_user: RequireMentor,
    definition_service: ProjectDefinitionServiceDep,
) -> JSONResponse:
    definition = await definition_service.archive_definition(definition_id, current_user)
    data = ProjectDefinitionResponseSchema(
        id=str(definition.id),
        owner_mentor_id=str(definition.owner_mentor_id),
        name=definition.name,
        status=definition.status,
        current_version_id=str(definition.current_version_id)
        if definition.current_version_id
        else None,
        created_at=definition.created_at,
        updated_at=definition.updated_at,
    ).model_dump()
    return success_response(message="Project definition archived.", data=data)


@router.get(
    "/{definition_id}/versions",
    summary="List Versions for Project Definition",
    response_model=list[ProjectDefinitionVersionResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_definition_versions(
    definition_id: UUID,
    current_user: CurrentUserDep,
    definition_service: ProjectDefinitionServiceDep,
) -> JSONResponse:
    versions = await definition_service.list_versions(definition_id, current_user)
    data = [
        ProjectDefinitionVersionResponseSchema(
            id=str(v.id),
            project_definition_id=str(v.project_definition_id),
            version_number=v.version_number,
            name=v.name,
            problem=v.problem,
            proposed_solution=v.proposed_solution,
            complexity=v.complexity,
            description=v.description,
            duration=v.duration,
            constraints=v.constraints,
            assumptions=v.assumptions,
            technology_snapshot=v.technology_snapshot or [],
            created_by=str(v.created_by),
            created_at=v.created_at,
        ).model_dump()
        for v in versions
    ]
    return success_response(message="Versions retrieved.", data=data)


@router.get(
    "/{definition_id}/versions/{version_id}",
    summary="Get Specific Definition Version",
    response_model=ProjectDefinitionVersionResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_definition_version(
    definition_id: UUID,
    version_id: UUID,
    current_user: CurrentUserDep,
    definition_service: ProjectDefinitionServiceDep,
) -> JSONResponse:
    v = await definition_service.get_version(definition_id, version_id, current_user)
    data = ProjectDefinitionVersionResponseSchema(
        id=str(v.id),
        project_definition_id=str(v.project_definition_id),
        version_number=v.version_number,
        name=v.name,
        problem=v.problem,
        proposed_solution=v.proposed_solution,
        complexity=v.complexity,
        description=v.description,
        duration=v.duration,
        constraints=v.constraints,
        assumptions=v.assumptions,
        technology_snapshot=v.technology_snapshot or [],
        created_by=str(v.created_by),
        created_at=v.created_at,
    ).model_dump()
    return success_response(message="Version details retrieved.", data=data)


@router.post(
    "/{definition_id}/assign",
    summary="Assign Project Definition to Student",
    response_model=ProjectResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def assign_project_definition(
    definition_id: UUID,
    payload: ProjectDefinitionAssignSchema,
    current_user: RequireMentor,
    definition_service: ProjectDefinitionServiceDep,
    correlation_id: CorrelationIdDep,
) -> JSONResponse:
    instance = await definition_service.assign_definition(
        definition_id=definition_id,
        mentor_user=current_user,
        student_id=UUID(payload.student_id),
        group_id=UUID(payload.group_id) if payload.group_id else None,
        deadline=payload.deadline,
        correlation_id=correlation_id,
    )
    data = ProjectResponseSchema(
        id=str(instance.id),
        student_id=str(instance.student_id),
        group_id=str(instance.group_id) if instance.group_id else None,
        project_definition_id=str(instance.project_definition_id)
        if instance.project_definition_id
        else None,
        source_definition_version_id=str(instance.source_definition_version_id)
        if instance.source_definition_version_id
        else None,
        name=instance.name,
        problem=instance.problem,
        proposed_solution=instance.proposed_solution,
        complexity=instance.complexity,
        current_phase=instance.current_phase,
        health=instance.health,
        progress_percentage=instance.progress_percentage,
        status=instance.status,
        deadline=instance.deadline,
        started_at=instance.started_at,
        completed_at=instance.completed_at,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
    ).model_dump()
    return success_response(
        message="Project assigned successfully.",
        data=data,
        status_code=status.HTTP_201_CREATED,
    )
