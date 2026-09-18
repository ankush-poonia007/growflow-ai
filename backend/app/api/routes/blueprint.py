"""
GrowFlow — Student Project Blueprint Route Endpoints.

Implements /api/v1/projects/{project_id}/blueprint endpoints:
- GET /status — check active status & progress
- POST /generate — start persistent generation
- POST /retry — targeted recovery or full retry
- GET /content — retrieve structured blueprint document sections
- POST /approve — authoritatively approve blueprint
- GET /events — SSE stream for generation status

Architecture ref:
  6C § 13 — Project Instance APIs
  6N § 18 — AI Provider Gateway
  6N § 20 — Blueprint Agent Graph
  6N § 21 — AI Output Authority Boundary
  Gate 09 — AI Blueprint & Agent System
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import StreamingResponse

from backend.app.api.dependencies.auth import RequireStudent
from backend.app.api.dependencies.services import BlueprintServiceDep
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.blueprint import (
    BlueprintApproveResponse,
    BlueprintContentResponse,
    BlueprintGeneratePayload,
    BlueprintGenerationProgressSchema,
    BlueprintRetryPayload,
    BlueprintStatusResponse,
)
from backend.app.api.schemas.workspace import (
    BlueprintDocumentSchema,
    BlueprintSectionDetailSchema,
)
from backend.app.domain.blueprint.models import CANONICAL_BLUEPRINT_SECTION_ORDER

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/projects/{project_id}/blueprint", tags=["Blueprint"])


def _to_status_schema(bp) -> BlueprintStatusResponse:
    feedback_dict = None
    if bp.qa_feedback:
        feedback_dict = {
            "status": bp.qa_feedback.status.value,
            "score": bp.qa_feedback.score,
            "summary": bp.qa_feedback.summary,
            "evaluated_criteria": bp.qa_feedback.evaluated_criteria,
            "issues": [
                {
                    "section": i.section,
                    "severity": i.severity,
                    "description": i.description,
                    "recommendation": i.recommendation,
                }
                for i in bp.qa_feedback.issues
            ],
            "recommendations": bp.qa_feedback.recommendations,
        }

    completed_sections = [
        k.value
        for k in CANONICAL_BLUEPRINT_SECTION_ORDER
        if bp.content and k.value in bp.content
    ]
    failed_sections = [bp.failed_output_key] if bp.failed_output_key else []
    in_prog = bp.current_step if getattr(bp.status, "value", str(bp.status)) == "GENERATING" else None

    progress_schema = BlueprintGenerationProgressSchema(
        completed_sections=completed_sections,
        total_sections=len(CANONICAL_BLUEPRINT_SECTION_ORDER),
        in_progress_section=in_prog,
        failed_sections=failed_sections,
    )

    bp_status_val = bp.status.value if hasattr(bp.status, "value") else str(bp.status)
    qa_status_val = bp.qa_status.value if hasattr(bp.qa_status, "value") else str(bp.qa_status)

    return BlueprintStatusResponse(
        id=bp.id,
        blueprint_id=bp.id,
        project_instance_id=bp.project_instance_id,
        project_id=bp.project_instance_id,
        student_id=bp.student_id,
        status=bp_status_val,
        current_step=bp.current_step,
        progress_percent=bp.progress_percent,
        current_stage=len(completed_sections),
        generation_progress=progress_schema,
        error_message=bp.error_message,
        failed_output_key=bp.failed_output_key,
        qa_status=qa_status_val,
        qa_score=bp.qa_score,
        qa_feedback=feedback_dict,
        approved_at=bp.approved_at,
        created_at=bp.created_at,
        updated_at=bp.updated_at,
    )


@router.get("/status")
async def get_blueprint_status(
    project_id: UUID,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
) -> JSONResponse:
    """Retrieve current blueprint generation, QA, and approval status."""
    bp = await service.get_status(project_id, current_user)
    data = _to_status_schema(bp)
    return success_response(
        message="Blueprint status retrieved successfully.",
        data=data.model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.post("/generate")
async def start_blueprint_generation(
    project_id: UUID,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
    payload: BlueprintGeneratePayload | None = None,
) -> JSONResponse:
    """Initiate or resume persistent blueprint generation."""
    force = payload.force_regenerate if payload else False
    bp = await service.start_generation(project_id, current_user, force_regenerate=force)
    data = _to_status_schema(bp)
    return success_response(
        message="Blueprint generation initiated successfully.",
        data=data.model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.post("/retry")
async def retry_blueprint_generation(
    project_id: UUID,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
    payload: BlueprintRetryPayload | None = None,
) -> JSONResponse:
    """Perform targeted recovery on an affected output or full generation retry."""
    target_key = payload.target_output_key if payload else None
    bp = await service.retry_generation(project_id, current_user, target_output_key=target_key)
    data = _to_status_schema(bp)
    return success_response(
        message="Blueprint retry initiated successfully.",
        data=data.model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("/content")
async def get_blueprint_content(
    project_id: UUID,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
) -> JSONResponse:
    """Retrieve synthesized blueprint document sections."""
    bp = await service.get_status(project_id, current_user)
    content = await service.get_content(project_id, current_user)
    data = BlueprintContentResponse(
        project_instance_id=project_id,
        status=bp.status.value,
        qa_status=bp.qa_status.value,
        qa_score=bp.qa_score,
        content=content,
    )
    return success_response(
        message="Blueprint content retrieved successfully.",
        data=data.model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.post("/approve")
async def approve_blueprint(
    project_id: UUID,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
) -> JSONResponse:
    """Authoritatively approve the generated blueprint."""
    bp = await service.approve_blueprint(project_id, current_user)
    data = BlueprintApproveResponse(
        success=True,
        status=bp.status.value,
        approved_at=bp.approved_at,
    )
    return success_response(
        message="Blueprint approved successfully.",
        data=data.model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("/events")
async def stream_blueprint_events(
    request: Request,
    project_id: UUID,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
) -> StreamingResponse:
    """Stream SSE updates during blueprint generation."""
    # Pre-flight authorization check before opening SSE stream
    initial_bp = await service.get_status(project_id, current_user)

    async def event_generator():
        last_signature: str | None = None
        seq = 0
        bp = initial_bp
        while not await request.is_disconnected():
            if seq > 0:
                bp = await service.get_status(project_id, current_user)
            schema = _to_status_schema(bp)
            bp_status_val = bp.status.value if hasattr(bp.status, "value") else str(bp.status)

            # Deterministic signature derived from available canonical state
            current_signature = f"{bp_status_val}:{bp.progress_percent}:{bp.current_step}:{bp.updated_at}"

            if current_signature != last_signature or seq == 0:
                seq += 1
                ts = int(bp.updated_at.timestamp()) if bp.updated_at else seq
                event_id = f"{project_id}_{ts}_{seq}"
                data_json = schema.model_dump_json()
                yield f"id: {event_id}\nevent: update\nretry: 2000\ndata: {data_json}\n\n"
                last_signature = current_signature
            else:
                yield ": keep-alive\n\n"

            if bp_status_val in ["READY_FOR_APPROVAL", "APPROVED", "FAILED", "QA_REJECTED"]:
                break

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sections/{section_key}")
async def get_blueprint_section(
    project_id: UUID,
    section_key: str,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
) -> JSONResponse:
    """Retrieve structured content and compiled Markdown for a specific canonical section."""
    section_data = await service.get_section(project_id, section_key, current_user)
    data = BlueprintSectionDetailSchema(**section_data)
    return success_response(
        message=f"Blueprint section '{section_key}' retrieved successfully.",
        data=data.model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("/documents/{document_key}")
async def get_blueprint_document(
    project_id: UUID,
    document_key: str,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
) -> JSONResponse:
    """Retrieve a document-oriented representation of a blueprint output."""
    doc_data = await service.get_document(project_id, document_key, current_user)
    data = BlueprintDocumentSchema(**doc_data)
    return success_response(
        message=f"Blueprint document '{document_key}' retrieved successfully.",
        data=data.model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("/documents/{document_key}/raw")
async def download_blueprint_document_raw(
    project_id: UUID,
    document_key: str,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
) -> Response:
    """Download raw Markdown for the currently selected blueprint document."""
    raw_markdown, filename = await service.get_raw_document(project_id, document_key, current_user)
    return Response(
        content=raw_markdown,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
