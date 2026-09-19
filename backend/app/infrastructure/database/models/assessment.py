"""
GrowFlow — Assessment SQLAlchemy ORM Models.

Defines ORM mappings for:
- assessments (session table)
- assessment_answers (submitted answer instances)
- assessment_results (enriched project understanding results)

Architecture ref:
  6N § 16 — Assessment Architecture (10 standardized core + 5 dynamic questions)
  5B § 18 & 19 — AI Assessment & Enriched Project Understanding
  6B § 7 — Project Instances
"""

from __future__ import annotations

from datetime import (  # noqa: TC003 — evaluated at runtime by SQLAlchemy mapper
    datetime,
)
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.domain.assessment.models import (
    AssessmentAnswer,
    AssessmentQuestionOption,
    AssessmentQuestionRecord,
    AssessmentQuestionTemplate,
    AssessmentReadinessTier,
    AssessmentResult,
    AssessmentSession,
    AssessmentStatus,
    QuestionType,
)
from backend.app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

JSON_TYPE = JSON().with_variant(postgresql.JSONB(), "postgresql")


class AssessmentQuestionTemplateModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for assessment_question_templates table."""

    __tablename__ = "assessment_question_templates"
    __table_args__ = (
        UniqueConstraint("version", "sequence_number", name="uq_template_version_seq"),
    )

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False, index=True)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    help_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    question_type: Mapped[str] = mapped_column(
        String(50), default=QuestionType.MULTIPLE_CHOICE.value, nullable=False
    )
    options: Mapped[list[dict[str, Any]]] = mapped_column(JSON_TYPE, default=list, nullable=False)

    def to_domain(self) -> AssessmentQuestionTemplate:
        opts = [
            AssessmentQuestionOption(
                value=o.get("value", ""),
                label=o.get("label", ""),
                description=o.get("description", ""),
            )
            for o in (self.options or [])
        ]
        return AssessmentQuestionTemplate(
            id=UUID(str(self.id)),
            version=self.version,
            sequence_number=self.sequence_number,
            question_text=self.question_text,
            active=self.active,
            category=self.category or "",
            help_text=self.help_text or "",
            question_type=QuestionType(self.question_type)
            if self.question_type in QuestionType._value2member_map_
            else QuestionType.MULTIPLE_CHOICE,
            options=opts,
            created_at=self.created_at,
        )


class AssessmentQuestionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for assessment_questions table representing persisted generated questions."""

    __tablename__ = "assessment_questions"
    __table_args__ = (
        UniqueConstraint("assessment_id", "sequence_number", name="uq_assessment_question_seq"),
    )

    assessment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "CORE" or "DYNAMIC"
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    generation_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSON_TYPE, default=dict, nullable=False
    )
    generated_from_question_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("assessment_questions.id", ondelete="SET NULL"),
        nullable=True,
    )

    def to_domain(self) -> AssessmentQuestionRecord:
        return AssessmentQuestionRecord(
            id=UUID(str(self.id)),
            assessment_id=UUID(self.assessment_id),
            sequence_number=self.sequence_number,
            question_type=self.question_type,
            question_text=self.question_text,
            generation_metadata=self.generation_metadata or {},
            generated_from_question_id=UUID(self.generated_from_question_id)
            if self.generated_from_question_id
            else None,
            created_at=self.created_at,
        )


class AssessmentModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for assessments table representing a project assessment session."""

    __tablename__ = "assessments"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=AssessmentStatus.NOT_STARTED.value,
        index=True,
        nullable=False,
    )
    current_question_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    def to_domain(self) -> AssessmentSession:
        return AssessmentSession(
            id=UUID(str(self.id)),
            project_instance_id=UUID(self.project_instance_id),
            student_id=UUID(self.student_id),
            status=AssessmentStatus(self.status),
            current_question_index=self.current_question_index,
            total_questions=self.total_questions,
            started_at=self.started_at,
            completed_at=self.completed_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class AssessmentAnswerModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for assessment_answers table."""

    __tablename__ = "assessment_answers"
    __table_args__ = (
        UniqueConstraint(
            "assessment_id",
            "question_id",
            name="uq_assessment_answer",
        ),
    )

    assessment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question_id: Mapped[str] = mapped_column(String(100), nullable=False)
    question_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(
        String(50),
        default=QuestionType.MULTIPLE_CHOICE.value,
        nullable=False,
    )
    selected_option: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_domain(self) -> AssessmentAnswer:
        return AssessmentAnswer(
            id=UUID(str(self.id)),
            assessment_id=UUID(self.assessment_id),
            question_id=self.question_id,
            question_index=self.question_index,
            question_text=self.question_text,
            question_type=QuestionType(self.question_type),
            selected_option=self.selected_option,
            text_response=self.text_response,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class AssessmentResultModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    SQLAlchemy model for assessment_results table.
    Persists Enriched Project Understanding synthesized upon completion.
    """

    __tablename__ = "assessment_results"

    assessment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    skill_level: Mapped[str] = mapped_column(String(50), nullable=False)
    project_complexity: Mapped[str] = mapped_column(String(50), nullable=False)
    alignment: Mapped[str] = mapped_column(String(255), nullable=False)
    technical_confidence: Mapped[str] = mapped_column(String(50), nullable=False)
    learning_depth: Mapped[str] = mapped_column(String(50), nullable=False)
    recommended_focus: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    readiness_tier: Mapped[str] = mapped_column(
        String(50),
        default=AssessmentReadinessTier.MODERATE.value,
        nullable=False,
    )
    dimension_scores: Mapped[dict[str, Any]] = mapped_column(
        JSON_TYPE, default=dict, nullable=False
    )
    identified_gaps: Mapped[list[Any]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    recommendations: Mapped[list[Any]] = mapped_column(JSON_TYPE, default=list, nullable=False)

    def to_domain(self) -> AssessmentResult:
        return AssessmentResult(
            id=UUID(str(self.id)),
            assessment_id=UUID(self.assessment_id),
            project_instance_id=UUID(self.project_instance_id),
            skill_level=self.skill_level,
            project_complexity=self.project_complexity,
            alignment=self.alignment,
            technical_confidence=self.technical_confidence,
            learning_depth=self.learning_depth,
            recommended_focus=self.recommended_focus,
            summary=self.summary,
            overall_score=self.overall_score,
            readiness_tier=AssessmentReadinessTier(self.readiness_tier),
            dimension_scores=self.dimension_scores or {},
            identified_gaps=self.identified_gaps or [],
            recommendations=self.recommendations or [],
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
