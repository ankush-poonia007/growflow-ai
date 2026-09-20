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
from datetime import UTC, datetime
import json
from typing import Any
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import (
    JSONResponse,
    StreamingResponse,
)

from backend.app.api.dependencies.auth import RequireStudent  # noqa: TC001
from backend.app.api.dependencies.services import BlueprintServiceDep  # noqa: TC001
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
from backend.app.domain.ai.orchestration.events import WorkflowEvent, WorkflowEventType
from backend.app.domain.blueprint.models import CANONICAL_BLUEPRINT_SECTION_ORDER

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
        k.value for k in CANONICAL_BLUEPRINT_SECTION_ORDER if bp.content and k.value in bp.content
    ]
    failed_sections = [bp.failed_output_key] if bp.failed_output_key else []
    in_prog = (
        bp.current_step if getattr(bp.status, "value", str(bp.status)) == "GENERATING" else None
    )

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


@router.post("/cancel")
async def cancel_blueprint_generation(
    project_id: UUID,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
) -> JSONResponse:
    """Cooperatively request cancellation of active blueprint generation."""
    bp = await service.cancel_generation(project_id, current_user)
    data = _to_status_schema(bp)
    return success_response(
        message="Blueprint generation cancellation requested successfully.",
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


STEP_PROGRESS_MAP: dict[str, int] = {
    "job.started": 5,
    "idea": 10,
    "scope": 20,
    "technology": 30,
    "features": 40,
    "mvp": 50,
    "specification": 60,
    "timeline": 70,
    "risk": 75,
    "task": 80,
    "milestone": 85,
    "readme": 90,
    "qa_judge": 95,
    "completed": 100,
}


def _project_workflow_event(
    event: WorkflowEvent,
    bp: Any,
    current_user: Any,
) -> dict[str, Any]:
    status_val = "GENERATING"
    step_val = event.step or "generating"
    progress = event.progress_percent
    if progress is None:
        progress = STEP_PROGRESS_MAP.get(step_val, 10)

    qa_status_val = event.payload.get("qa_status") or (
        bp.qa_status.value
        if hasattr(bp.qa_status, "value")
        else str(bp.qa_status)
        if bp.qa_status
        else None
    )
    qa_score_val = event.payload.get("qa_score") or bp.qa_score
    error_msg = None
    failed_key = None

    if event.event_type == WorkflowEventType.JOB_COMPLETED.value:
        status_val = "READY_FOR_APPROVAL"
        progress = 100
        step_val = "completed"
    elif event.event_type == WorkflowEventType.JOB_FAILED.value:
        if event.payload.get("reason") == "QA_REJECTED":
            status_val = "QA_REJECTED"
            qa_status_val = "FAIL"
        else:
            status_val = "FAILED"
        error_msg = event.payload.get("error") or "Generation failed"
        failed_key = event.step
    elif event.event_type == WorkflowEventType.JOB_CANCELLED.value:
        status_val = "CANCELLED"
        step_val = "cancelled"

    completed_sections = [
        k.value for k in CANONICAL_BLUEPRINT_SECTION_ORDER if bp.content and k.value in bp.content
    ]

    progress_dict = {
        "completed_sections": completed_sections,
        "total_sections": len(CANONICAL_BLUEPRINT_SECTION_ORDER),
        "in_progress_section": step_val if status_val == "GENERATING" else None,
        "failed_sections": [failed_key] if failed_key else [],
    }

    return {
        "id": str(bp.id),
        "blueprint_id": str(bp.id),
        "project_instance_id": str(bp.project_instance_id),
        "project_id": str(bp.project_instance_id),
        "student_id": str(current_user.user_id),
        "status": status_val,
        "current_step": step_val,
        "progress_percent": progress,
        "current_stage": len(completed_sections),
        "generation_progress": progress_dict,
        "error_message": error_msg or bp.error_message,
        "failed_output_key": failed_key or bp.failed_output_key,
        "qa_status": qa_status_val,
        "qa_score": qa_score_val,
        "qa_feedback": bp.qa_feedback.model_dump()
        if hasattr(bp.qa_feedback, "model_dump")
        else (bp.qa_feedback if isinstance(bp.qa_feedback, dict) else None),
        "approved_at": bp.approved_at.isoformat() if getattr(bp, "approved_at", None) else None,
        "created_at": bp.created_at.isoformat() if getattr(bp, "created_at", None) else None,
        "updated_at": event.timestamp.isoformat(),
        # Enriched metadata for Unit 5 and Unit 6
        "event_id": event.event_id,
        "event_type": event.event_type,
        "event_version": "1.0.0",
        "job_id": event.job_id,
        "generation_number": event.generation_number,
        "timestamp": event.timestamp.isoformat(),
        "regeneration_attempt": event.payload.get("regeneration_attempt", 0),
        "regeneration_target": event.payload.get("regeneration_target"),
        "active_job": {
            "id": event.job_id,
            "status": "RUNNING" if status_val == "GENERATING" else status_val,
        },
    }


def _project_db_snapshot(
    bp: Any,
    current_user: Any,
    event_id: str,
) -> dict[str, Any]:
    schema = _to_status_schema(bp)
    data = schema.model_dump(mode="json")
    bp_status_val = data.get("status", "GENERATING")
    data.update(
        {
            "event_id": event_id,
            "event_type": "snapshot",
            "event_version": "1.0.0",
            "job_id": str(getattr(bp, "active_job_id", "")) or None,
            "generation_number": getattr(bp, "generation_number", 1),
            "timestamp": datetime.now(UTC).isoformat(),
            "regeneration_attempt": 0,
            "regeneration_target": None,
            "active_job": {
                "id": str(getattr(bp, "active_job_id", "")),
                "status": bp_status_val,
            }
            if getattr(bp, "active_job_id", None)
            else None,
        }
    )
    return data


@router.get("/events")
async def stream_blueprint_events(
    request: Request,
    project_id: UUID,
    current_user: RequireStudent,
    service: BlueprintServiceDep,
) -> StreamingResponse:
    from backend.app.domain.ai.orchestration.events import (
        BlueprintEventManager,
        get_blueprint_event_manager,
    )

    proj_str = str(project_id)
    raw_manager = getattr(service, "event_manager", None)
    event_manager = (
        raw_manager
        if isinstance(raw_manager, BlueprintEventManager)
        else get_blueprint_event_manager()
    )

    # 1. Register subscriber queue FIRST to prevent lost events during hydration
    queue = await event_manager.subscribe(proj_str)

    # 2. Pre-flight authorization & durable state check
    try:
        initial_bp = await service.get_status(project_id, current_user)
    except Exception:
        await event_manager.unsubscribe(proj_str, queue)
        raise

    # 3. Check for Last-Event-ID header or query parameter for replay
    last_event_id = request.headers.get("Last-Event-ID") or request.query_params.get(
        "last_event_id"
    )
    replay_events = event_manager.get_replay_events(proj_str, last_event_id)

    async def event_generator():
        try:
            # Step A: Replay missed events if requested and available
            has_terminal_replay = False
            if replay_events:
                for rev in replay_events:
                    payload = _project_workflow_event(rev, initial_bp, current_user)
                    data_json = json.dumps(payload, default=str)
                    yield f"id: {rev.event_id}\nevent: update\nretry: 2000\ndata: {data_json}\n\n"
                    if rev.event_type in [
                        WorkflowEventType.JOB_COMPLETED.value,
                        WorkflowEventType.JOB_FAILED.value,
                        WorkflowEventType.JOB_CANCELLED.value,
                    ]:
                        has_terminal_replay = True

            if has_terminal_replay:
                return

            if not replay_events:
                # Step B: Initial state hydration snapshot
                ts = (
                    int(initial_bp.updated_at.timestamp())
                    if getattr(initial_bp, "updated_at", None)
                    else 1
                )
                gen_num = getattr(initial_bp, "generation_number", 1)
                snapshot_id = f"{proj_str}_{gen_num}_{ts:03d}"
                snapshot_data = _project_db_snapshot(initial_bp, current_user, snapshot_id)
                data_json = json.dumps(snapshot_data, default=str)
                yield f"id: {snapshot_id}\nevent: update\nretry: 2000\ndata: {data_json}\n\n"

            # Step C: If initial state is already terminal, close stream cleanly
            initial_status = (
                initial_bp.status.value
                if hasattr(initial_bp.status, "value")
                else str(initial_bp.status)
            )
            if initial_status in [
                "READY_FOR_APPROVAL",
                "APPROVED",
                "COMPLETED",
                "GENERATED",
                "FAILED",
                "QA_REJECTED",
                "CANCELLED",
            ]:
                return

            # Step D: Stream live events with 15s keepalive heartbeat
            while not await request.is_disconnected():
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    payload = _project_workflow_event(event, initial_bp, current_user)
                    data_json = json.dumps(payload, default=str)
                    yield f"id: {event.event_id}\nevent: update\nretry: 2000\ndata: {data_json}\n\n"

                    # Close cleanly upon receiving terminal workflow event
                    if event.event_type in [
                        WorkflowEventType.JOB_COMPLETED.value,
                        WorkflowEventType.JOB_FAILED.value,
                        WorkflowEventType.JOB_CANCELLED.value,
                    ]:
                        break
                except TimeoutError:
                    yield ": keep-alive\n\n"
        finally:
            await event_manager.unsubscribe(proj_str, queue)

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
