"""
GrowFlow — Student Project Assessment Route Endpoints.

Implements /api/v1/projects/{project_id}/assessment endpoints:
- GET /status — check active status & progress
- POST /start — start new or resume existing assessment
- GET /questions/{question_index} — get specific question & prior answer
- POST /answers — submit or update answer
- POST /complete — validate & finalize assessment
- GET /result — get synthesized Enriched Project Understanding

Architecture ref:
  6C § 13 — Project Instance APIs
  6N § 16 — Assessment Architecture
  5B § 18 & 19 — AI Assessment & Enriched Project Understanding
  1 § 31 — Final Student-Side Concept
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, status

from backend.app.api.dependencies.auth import RequireStudent
from backend.app.api.dependencies.services import AssessmentServiceDep
from backend.app.api.responses.base import success_response
from backend.app.api.schemas.assessment import (
    AssessmentAnswerSchema,
    AssessmentAnswerSubmitResponseSchema,
    AssessmentAnswerSubmitSchema,
    AssessmentOptionSchema,
    AssessmentQuestionResponseSchema,
    AssessmentQuestionSchema,
    AssessmentResultResponseSchema,
    AssessmentStartResponseSchema,
    AssessmentStatusResponseSchema,
)

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

router = APIRouter(prefix="/projects/{project_id}/assessment", tags=["Assessment"])


def _to_question_schema(q) -> AssessmentQuestionSchema:
    return AssessmentQuestionSchema(
        id=q.id,
        order_index=q.order_index,
        category=q.category,
        question_text=q.question_text,
        help_text=q.help_text,
        question_type=q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
        options=[
            AssessmentOptionSchema(
                value=opt.value,
                label=opt.label,
                description=opt.description,
            )
            for opt in q.options
        ],
        is_adaptive=q.is_adaptive,
        context_badge=q.context_badge,
    )


def _to_answer_schema(a) -> AssessmentAnswerSchema | None:
    if not a:
        return None
    return AssessmentAnswerSchema(
        id=str(a.id),
        assessment_id=str(a.assessment_id),
        question_id=a.question_id,
        question_index=a.question_index,
        question_text=a.question_text,
        question_type=a.question_type,
        selected_option=a.selected_option,
        text_response=a.text_response,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


def _to_result_schema(r) -> AssessmentResultResponseSchema:
    return AssessmentResultResponseSchema(
        id=str(r.id),
        assessment_id=str(r.assessment_id),
        project_instance_id=str(r.project_instance_id),
        skill_level=r.skill_level,
        project_complexity=r.project_complexity,
        alignment=r.alignment,
        technical_confidence=r.technical_confidence,
        learning_depth=r.learning_depth,
        recommended_focus=r.recommended_focus,
        summary=r.summary,
        overall_score=r.overall_score,
        readiness_tier=r.readiness_tier,
        dimension_scores=r.dimension_scores or {},
        identified_gaps=r.identified_gaps or [],
        recommendations=r.recommendations or [],
        created_at=r.created_at.isoformat() if r.created_at else None,
    )


@router.get(
    "/status",
    summary="Get Assessment Status",
    response_model=AssessmentStatusResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_assessment_status(
    project_id: UUID,
    current_user: RequireStudent,
    assessment_service: AssessmentServiceDep,
) -> JSONResponse:
    data = await assessment_service.get_assessment_status(project_id, current_user)
    return success_response(
        message="Assessment status retrieved.",
        data=data,
    )


@router.post(
    "/start",
    summary="Start or Resume Assessment",
    response_model=AssessmentStartResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def start_assessment(
    project_id: UUID,
    current_user: RequireStudent,
    assessment_service: AssessmentServiceDep,
) -> JSONResponse:
    assessment, current_question = await assessment_service.start_or_resume_assessment(
        project_id, current_user
    )
    status_data = await assessment_service.get_assessment_status(project_id, current_user)
    payload = AssessmentStartResponseSchema(
        session=AssessmentStatusResponseSchema(**status_data),
        current_question=_to_question_schema(current_question),
    ).model_dump()
    return success_response(
        message="Assessment session started/resumed.",
        data=payload,
    )


@router.get(
    "/questions/{question_index}",
    summary="Get Assessment Question by Index",
    response_model=AssessmentQuestionResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_assessment_question(
    project_id: UUID,
    question_index: int,
    current_user: RequireStudent,
    assessment_service: AssessmentServiceDep,
) -> JSONResponse:
    question, answer = await assessment_service.get_question(
        project_id, question_index, current_user
    )
    payload = AssessmentQuestionResponseSchema(
        question=_to_question_schema(question),
        answer=_to_answer_schema(answer),
    ).model_dump()
    return success_response(
        message="Assessment question retrieved.",
        data=payload,
    )


@router.post(
    "/answers",
    summary="Submit or Update Assessment Answer",
    response_model=AssessmentAnswerSubmitResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def submit_assessment_answer(
    project_id: UUID,
    payload: AssessmentAnswerSubmitSchema,
    current_user: RequireStudent,
    assessment_service: AssessmentServiceDep,
) -> JSONResponse:
    saved_answer, assessment, next_idx = await assessment_service.submit_answer(
        project_id=project_id,
        question_index=payload.question_index,
        selected_option=payload.selected_option,
        text_response=payload.text_response,
        current_user=current_user,
    )
    status_data = await assessment_service.get_assessment_status(project_id, current_user)
    answered_count = status_data["answered_count"]
    total_questions = status_data["total_questions"]
    is_eligible = answered_count == total_questions

    response_data = AssessmentAnswerSubmitResponseSchema(
        answer=_to_answer_schema(saved_answer),  # type: ignore[arg-type]
        current_question_index=assessment.current_question_index,
        next_question_index=next_idx,
        answered_count=answered_count,
        total_questions=total_questions,
        is_complete_eligible=is_eligible,
    ).model_dump()
    return success_response(
        message="Answer submitted successfully.",
        data=response_data,
    )


@router.post(
    "/complete",
    summary="Complete Assessment",
    response_model=AssessmentResultResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def complete_assessment(
    project_id: UUID,
    current_user: RequireStudent,
    assessment_service: AssessmentServiceDep,
) -> JSONResponse:
    _assessment, result = await assessment_service.complete_assessment(
        project_id, current_user
    )
    payload = _to_result_schema(result).model_dump()
    return success_response(
        message="Assessment completed successfully. Enriched Project Understanding synthesized.",
        data=payload,
    )


@router.get(
    "/result",
    summary="Get Enriched Project Understanding Result",
    response_model=AssessmentResultResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_assessment_result(
    project_id: UUID,
    current_user: RequireStudent,
    assessment_service: AssessmentServiceDep,
) -> JSONResponse:
    result = await assessment_service.get_assessment_result(project_id, current_user)
    payload = _to_result_schema(result).model_dump()
    return success_response(
        message="Assessment result retrieved.",
        data=payload,
    )
