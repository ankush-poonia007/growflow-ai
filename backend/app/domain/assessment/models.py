"""
GrowFlow — Assessment Domain Models.

Defines pure domain entities and value objects for the Assessment subsystem:
- AssessmentStatus
- QuestionType
- AssessmentReadinessTier
- AssessmentQuestionOption
- AssessmentQuestion
- AssessmentAnswer
- AssessmentSession
- AssessmentResult

Architecture ref:
  6N § 16 — Assessment Architecture (10 standardized core + 5 dynamic project-specific questions)
  5B § 18 & 19 — AI Assessment & Enriched Project Understanding
  1 § 31 — Final Student-Side Concept (15-question assessment -> Enriched Project Understanding)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID


class AssessmentStatus(StrEnum):
    """Lifecycle status of a student project assessment session."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class QuestionType(StrEnum):
    """Permissible answer input paradigms for assessment questions."""

    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TEXT = "TEXT"


class AssessmentReadinessTier(StrEnum):
    """Evaluated readiness tier for proceeding to Blueprint generation."""

    HIGH = "HIGH"
    MODERATE = "MODERATE"
    NEEDS_REFINEMENT = "NEEDS_REFINEMENT"


@dataclass(frozen=True)
class AssessmentQuestionOption:
    """Option choice for MULTIPLE_CHOICE questions."""

    value: str
    label: str
    description: str = ""


@dataclass(frozen=True)
class AssessmentQuestion:
    """Authoritative question definition presented to the student."""

    id: str
    order_index: int  # 1 to 15
    category: str
    question_text: str
    help_text: str
    question_type: QuestionType
    options: list[AssessmentQuestionOption] = field(default_factory=list)
    is_adaptive: bool = False
    context_badge: str | None = None


@dataclass(frozen=True)
class AssessmentAnswer:
    """Persisted student answer response to an assessment question."""

    id: UUID
    assessment_id: UUID
    question_id: str
    question_index: int
    question_text: str
    question_type: QuestionType
    selected_option: str | None = None
    text_response: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class AssessmentSession:
    """Authoritative persistent assessment session for a student project instance."""

    id: UUID
    project_instance_id: UUID
    student_id: UUID
    status: AssessmentStatus
    current_question_index: int
    total_questions: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class AssessmentQuestionTemplate:
    """Versioned template for standardized core assessment questions."""

    id: UUID
    version: int
    sequence_number: int
    question_text: str
    active: bool
    category: str = ""
    help_text: str = ""
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    options: list[AssessmentQuestionOption] = field(default_factory=list)
    created_at: datetime | None = None


@dataclass(frozen=True)
class AssessmentQuestionRecord:
    """Persisted question entity instantiated or synthesized for an assessment session."""

    id: UUID
    assessment_id: UUID
    sequence_number: int
    question_type: str  # "CORE" or "DYNAMIC"
    question_text: str
    generation_metadata: dict[str, Any] = field(default_factory=dict)
    generated_from_question_id: UUID | None = None
    created_at: datetime | None = None


@dataclass(frozen=True)
class AssessmentResult:
    """
    Enriched Project Understanding synthesized upon assessment completion.
    Serves as structured project context for future Blueprint generation (S12-S14).
    """

    id: UUID
    assessment_id: UUID
    project_instance_id: UUID
    skill_level: str
    project_complexity: str
    alignment: str
    technical_confidence: str
    learning_depth: str
    recommended_focus: str
    summary: str
    overall_score: int
    readiness_tier: AssessmentReadinessTier
    dimension_scores: dict[str, int] = field(default_factory=dict)
    identified_gaps: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
