"""
GrowFlow — Blueprint SQLAlchemy ORM Models.

Defines ORM mappings for:
- blueprints (canonical blueprint table)
- blueprint_jobs (asynchronous/persistent generation job records)

Architecture ref:
  6B § 7 — Project Instances
  6N § 18 — AI Provider Gateway
  6N § 20 — Blueprint Agent Graph
  Gate 09 — AI Blueprint & Agent System
"""

from __future__ import annotations

from datetime import (  # noqa: TC003 — evaluated at runtime by SQLAlchemy mapper
    datetime,
)
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.domain.blueprint.models import (
    BlueprintIssue,
    BlueprintJobStatus,
    BlueprintJobType,
    BlueprintQAFeedback,
    BlueprintQAStatus,
    BlueprintSession,
    BlueprintStatus,
)
from backend.app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

JSON_TYPE = JSON().with_variant(postgresql.JSONB(), "postgresql")


class BlueprintModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for blueprints table representing a project blueprint."""

    __tablename__ = "blueprints"

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
        default=BlueprintStatus.NOT_STARTED.value,
        index=True,
        nullable=False,
    )
    current_step: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    progress_percent: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
    failed_output_key: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    qa_status: Mapped[str] = mapped_column(
        String(50),
        default=BlueprintQAStatus.PENDING.value,
        nullable=False,
    )
    qa_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None,
    )
    qa_feedback: Mapped[dict[str, Any] | None] = mapped_column(
        JSON_TYPE,
        nullable=True,
        default=None,
    )
    content: Mapped[dict[str, Any] | None] = mapped_column(
        JSON_TYPE,
        nullable=True,
        default=None,
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    __table_args__ = (
        UniqueConstraint("project_instance_id", name="uq_blueprints_project_instance"),
    )

    def to_domain(self) -> BlueprintSession:
        qa_feedback_domain = None
        if self.qa_feedback:
            issues = [
                BlueprintIssue(
                    section=i.get("section", ""),
                    severity=i.get("severity", "MEDIUM"),
                    description=i.get("description", ""),
                    recommendation=i.get("recommendation", ""),
                )
                for i in self.qa_feedback.get("issues", [])
            ]
            qa_feedback_domain = BlueprintQAFeedback(
                status=BlueprintQAStatus(self.qa_feedback.get("status", BlueprintQAStatus.PENDING.value)),
                score=self.qa_feedback.get("score", 0),
                summary=self.qa_feedback.get("summary", ""),
                evaluated_criteria=self.qa_feedback.get("evaluated_criteria", {}),
                issues=issues,
                recommendations=self.qa_feedback.get("recommendations", []),
            )

        return BlueprintSession(
            id=UUID(str(self.id)),
            project_instance_id=UUID(str(self.project_instance_id)),
            student_id=UUID(str(self.student_id)),
            status=BlueprintStatus(self.status),
            current_step=self.current_step,
            progress_percent=self.progress_percent,
            error_message=self.error_message,
            failed_output_key=self.failed_output_key,
            qa_status=BlueprintQAStatus(self.qa_status),
            qa_score=self.qa_score,
            qa_feedback=qa_feedback_domain,
            content=self.content or {},
            approved_at=self.approved_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class BlueprintJobModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for blueprint_jobs tracking persistent generation runs."""

    __tablename__ = "blueprint_jobs"

    blueprint_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("blueprints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    job_type: Mapped[str] = mapped_column(
        String(50),
        default=BlueprintJobType.FULL_GENERATION.value,
        nullable=False,
    )
    target_output: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=BlueprintJobStatus.PENDING.value,
        index=True,
        nullable=False,
    )
    current_step: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    progress_percent: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
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
