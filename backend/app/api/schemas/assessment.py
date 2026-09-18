"""
GrowFlow — Assessment API Pydantic Schemas.

Defines request/response contracts for Assessment endpoints:
- GET /api/v1/projects/{project_id}/assessment/status
- POST /api/v1/projects/{project_id}/assessment/start
- GET /api/v1/projects/{project_id}/assessment/questions/{question_index}
- POST /api/v1/projects/{project_id}/assessment/answers
- POST /api/v1/projects/{project_id}/assessment/complete
- GET /api/v1/projects/{project_id}/assessment/result
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AssessmentOptionSchema(BaseModel):
    """Multiple choice option presentation."""

    model_config = ConfigDict(extra="forbid")

    value: str
    label: str
    description: str = ""


class AssessmentQuestionSchema(BaseModel):
    """Canonical question model returned to the student."""

    model_config = ConfigDict(extra="forbid")

    id: str
    order_index: int
    category: str
    question_text: str
    help_text: str
    question_type: str
    options: list[AssessmentOptionSchema] = Field(default_factory=list)
    is_adaptive: bool = False
    context_badge: str | None = None


class AssessmentAnswerSchema(BaseModel):
    """Persisted student answer response."""

    model_config = ConfigDict(extra="forbid")

    id: str
    assessment_id: str
    question_id: str
    question_index: int
    question_text: str
    question_type: str
    selected_option: str | None = None
    text_response: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AssessmentStatusResponseSchema(BaseModel):
    """Summary of active assessment status and progression."""

    model_config = ConfigDict(extra="forbid")

    project_id: str
    project_name: str
    current_phase: str
    status: str
    current_question_index: int
    total_questions: int
    answered_count: int
    progress_percentage: int
    started_at: str | None = None
    completed_at: str | None = None


class AssessmentStartResponseSchema(BaseModel):
    """Response returned upon starting or resuming an assessment."""

    model_config = ConfigDict(extra="forbid")

    session: AssessmentStatusResponseSchema
    current_question: AssessmentQuestionSchema


class AssessmentQuestionResponseSchema(BaseModel):
    """Response returned when fetching a specific question by index."""

    model_config = ConfigDict(extra="forbid")

    question: AssessmentQuestionSchema
    answer: AssessmentAnswerSchema | None = None


class AssessmentAnswerSubmitSchema(BaseModel):
    """Payload for submitting or updating an answer to a question."""

    model_config = ConfigDict(extra="forbid")

    question_index: int = Field(..., ge=1, le=15, description="Question index (1 to 15)")
    selected_option: str | None = Field(default=None, description="Selected option value for MULTIPLE_CHOICE")
    text_response: str | None = Field(default=None, description="Open text response for TEXT")


class AssessmentAnswerSubmitResponseSchema(BaseModel):
    """Response returned after submitting an answer."""

    model_config = ConfigDict(extra="forbid")

    answer: AssessmentAnswerSchema
    current_question_index: int
    next_question_index: int | None = None
    answered_count: int
    total_questions: int
    is_complete_eligible: bool


class AssessmentResultResponseSchema(BaseModel):
    """
    Synthesized Enriched Project Understanding result.
    Grounding context for future Blueprint generation.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    assessment_id: str
    project_instance_id: str
    skill_level: str
    project_complexity: str
    alignment: str
    technical_confidence: str
    learning_depth: str
    recommended_focus: str
    summary: str
    overall_score: int
    readiness_tier: str
    dimension_scores: dict[str, int]
    identified_gaps: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    created_at: str | None = None
