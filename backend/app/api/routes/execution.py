"""
GrowFlow — Execution Management Route Endpoints.

Implements S18–S26 execution endpoints under /api/v1/projects/{project_id}:
- /tasks, /tasks/{task_id}
- /milestones, /milestones/{milestone_id}
- /risks, /risks/{risk_id}
- /roadmap
- /documents, /documents/{document_id}, /documents/{document_id}/download

Architecture ref:
  6C § 13 — Project Instance APIs
  Gate 10 — Execution Management
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from backend.app.api.dependencies.auth import CurrentUserDep
from backend.app.api.dependencies.services import ExecutionServiceDep
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.execution import (
    DocumentCreatePayload,
    DocumentResponse,
    DocumentUpdatePayload,
    MilestoneCreatePayload,
    MilestoneResponse,
    MilestoneUpdatePayload,
    RiskCreatePayload,
    RiskResponse,
    RiskUpdatePayload,
    RoadmapResponse,
    TaskCreatePayload,
    TaskResponse,
    TaskUpdatePayload,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/projects/{project_id}", tags=["Execution Management"])


# ============================================================================
# Tasks Endpoints (S18 & S19)
# ============================================================================

@router.get(
    "/tasks",
    summary="List Project Tasks",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
)
async def list_tasks(
    project_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    status_filter: str | None = Query(None, alias="status"),
    priority: str | None = Query(None),
    milestone_id: str | None = Query(None),
    phase: str | None = Query(None),
    search: str | None = Query(None),
) -> JSONResponse:
    tasks = await execution_service.list_tasks(
        project_id,
        current_user,
        status=status_filter,
        priority=priority,
        milestone_id=milestone_id,
        phase=phase,
        search=search,
    )
    return success_response(
        message="Tasks retrieved successfully.",
        data=[t.model_dump(mode="json") for t in tasks],
    )


@router.post(
    "/tasks",
    summary="Create Project Task",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    project_id: UUID,
    payload: TaskCreatePayload,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    task = await execution_service.create_task(project_id, current_user, payload)
    return success_response(
        message="Task created successfully.",
        data=task.model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/tasks/{task_id}",
    summary="Get Task Details",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
async def get_task(
    project_id: UUID,
    task_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    task = await execution_service.get_task(project_id, task_id, current_user)
    return success_response(
        message="Task retrieved successfully.",
        data=task.model_dump(mode="json"),
    )


@router.patch(
    "/tasks/{task_id}",
    summary="Update Task",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
async def update_task(
    project_id: UUID,
    task_id: UUID,
    payload: TaskUpdatePayload,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    task = await execution_service.update_task(project_id, task_id, current_user, payload)
    return success_response(
        message="Task updated successfully.",
        data=task.model_dump(mode="json"),
    )


@router.delete(
    "/tasks/{task_id}",
    summary="Delete Task",
    status_code=status.HTTP_200_OK,
)
async def delete_task(
    project_id: UUID,
    task_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    await execution_service.delete_task(project_id, task_id, current_user)
    return success_response(message="Task deleted successfully.", data=None)


# ============================================================================
# Milestones Endpoints (S20 & S21)
# ============================================================================

@router.get(
    "/milestones",
    summary="List Project Milestones",
    response_model=list[MilestoneResponse],
    status_code=status.HTTP_200_OK,
)
async def list_milestones(
    project_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    milestones = await execution_service.list_milestones(project_id, current_user)
    return success_response(
        message="Milestones retrieved successfully.",
        data=[m.model_dump(mode="json") for m in milestones],
    )


@router.post(
    "/milestones",
    summary="Create Project Milestone",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_milestone(
    project_id: UUID,
    payload: MilestoneCreatePayload,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    milestone = await execution_service.create_milestone(project_id, current_user, payload)
    return success_response(
        message="Milestone created successfully.",
        data=milestone.model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/milestones/{milestone_id}",
    summary="Get Milestone Details",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
)
async def get_milestone(
    project_id: UUID,
    milestone_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    milestone = await execution_service.get_milestone(project_id, milestone_id, current_user)
    return success_response(
        message="Milestone retrieved successfully.",
        data=milestone.model_dump(mode="json"),
    )


@router.patch(
    "/milestones/{milestone_id}",
    summary="Update Milestone",
    response_model=MilestoneResponse,
    status_code=status.HTTP_200_OK,
)
async def update_milestone(
    project_id: UUID,
    milestone_id: UUID,
    payload: MilestoneUpdatePayload,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    milestone = await execution_service.update_milestone(
        project_id, milestone_id, current_user, payload
    )
    return success_response(
        message="Milestone updated successfully.",
        data=milestone.model_dump(mode="json"),
    )


# ============================================================================
# Risks Endpoints (S22 & S23)
# ============================================================================

@router.get(
    "/risks",
    summary="List Project Risks",
    response_model=list[RiskResponse],
    status_code=status.HTTP_200_OK,
)
async def list_risks(
    project_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    status_filter: str | None = Query(None, alias="status"),
    severity: str | None = Query(None),
    search: str | None = Query(None),
) -> JSONResponse:
    risks = await execution_service.list_risks(
        project_id, current_user, status=status_filter, severity=severity, search=search
    )
    return success_response(
        message="Risks retrieved successfully.",
        data=[r.model_dump(mode="json") for r in risks],
    )


@router.post(
    "/risks",
    summary="Create Project Risk",
    response_model=RiskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_risk(
    project_id: UUID,
    payload: RiskCreatePayload,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    risk = await execution_service.create_risk(project_id, current_user, payload)
    return success_response(
        message="Risk created successfully.",
        data=risk.model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/risks/{risk_id}",
    summary="Get Risk Details",
    response_model=RiskResponse,
    status_code=status.HTTP_200_OK,
)
async def get_risk(
    project_id: UUID,
    risk_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    risk = await execution_service.get_risk(project_id, risk_id, current_user)
    return success_response(
        message="Risk retrieved successfully.",
        data=risk.model_dump(mode="json"),
    )


@router.patch(
    "/risks/{risk_id}",
    summary="Update Risk",
    response_model=RiskResponse,
    status_code=status.HTTP_200_OK,
)
async def update_risk(
    project_id: UUID,
    risk_id: UUID,
    payload: RiskUpdatePayload,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    risk = await execution_service.update_risk(project_id, risk_id, current_user, payload)
    return success_response(
        message="Risk updated successfully.",
        data=risk.model_dump(mode="json"),
    )


@router.delete(
    "/risks/{risk_id}",
    summary="Delete Risk",
    status_code=status.HTTP_200_OK,
)
async def delete_risk(
    project_id: UUID,
    risk_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    await execution_service.delete_risk(project_id, risk_id, current_user)
    return success_response(message="Risk deleted successfully.", data=None)


# ============================================================================
# Roadmap Endpoint (S24)
# ============================================================================

@router.get(
    "/roadmap",
    summary="Get Execution Roadmap Projection",
    response_model=RoadmapResponse,
    status_code=status.HTTP_200_OK,
)
async def get_roadmap(
    project_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    roadmap = await execution_service.get_roadmap(project_id, current_user)
    return success_response(
        message="Roadmap projection generated successfully.",
        data=roadmap.model_dump(mode="json"),
    )


# ============================================================================
# Documents Endpoints (S25 & S26)
# ============================================================================

@router.get(
    "/documents",
    summary="List Project Documents",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_documents(
    project_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    doc_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
) -> JSONResponse:
    documents = await execution_service.list_documents(
        project_id, current_user, doc_type=doc_type, status=status_filter, search=search
    )
    return success_response(
        message="Documents retrieved successfully.",
        data=[d.model_dump(mode="json") for d in documents],
    )


@router.post(
    "/documents",
    summary="Create Project Document",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    project_id: UUID,
    payload: DocumentCreatePayload,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    document = await execution_service.create_document(project_id, current_user, payload)
    return success_response(
        message="Document created successfully.",
        data=document.model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/documents/{document_id}",
    summary="Get Document Details",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_document(
    project_id: UUID,
    document_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    document = await execution_service.get_document(project_id, document_id, current_user)
    return success_response(
        message="Document retrieved successfully.",
        data=document.model_dump(mode="json"),
    )


@router.patch(
    "/documents/{document_id}",
    summary="Update Document",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_document(
    project_id: UUID,
    document_id: UUID,
    payload: DocumentUpdatePayload,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> JSONResponse:
    document = await execution_service.update_document(
        project_id, document_id, current_user, payload
    )
    return success_response(
        message="Document updated successfully.",
        data=document.model_dump(mode="json"),
    )


@router.get(
    "/documents/{document_id}/download",
    summary="Download Raw Document Markdown",
    status_code=status.HTTP_200_OK,
)
async def download_raw_document(
    project_id: UUID,
    document_id: UUID,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> Response:
    filename, content = await execution_service.get_raw_document(
        project_id, document_id, current_user
    )
    return Response(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
