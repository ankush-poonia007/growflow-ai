"""
GrowFlow — Execution Management SQLAlchemy ORM Models.

Defines ORM mappings for:
- project_milestones
- project_tasks
- project_risks
- project_documents

Architecture ref:
  6B § 20 & § 44 — Execution phase progression and deliverables
  Gate 10 — Execution Management Foundation
"""

from __future__ import annotations

from datetime import (  # noqa: TC003 — evaluated at runtime by SQLAlchemy mapper
    datetime,
)
from typing import Any
import uuid

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

JSON_TYPE = JSON().with_variant(postgresql.JSONB(), "postgresql")


class ProjectMilestoneModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for project_milestones table."""

    __tablename__ = "project_milestones"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    gate_code: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    target_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    status: Mapped[str] = mapped_column(String(50), default="UPCOMING", index=True, nullable=False)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deliverables: Mapped[list[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    section_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    tasks: Mapped[list[ProjectTaskModel]] = relationship(
        "ProjectTaskModel",
        back_populates="milestone",
        cascade="all, delete-orphan",
        order_by="ProjectTaskModel.created_at",
    )


class ProjectTaskModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for project_tasks table."""

    __tablename__ = "project_tasks"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    milestone_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("project_milestones.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        default=None,
    )
    task_code: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="TODO", index=True, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="MEDIUM", index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    phase: Mapped[str] = mapped_column(String(50), default="PLANNING", index=True, nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    dependencies: Mapped[list[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    acceptance_criteria: Mapped[list[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    milestone: Mapped[ProjectMilestoneModel | None] = relationship(
        "ProjectMilestoneModel",
        back_populates="tasks",
    )


class ProjectRiskModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for project_risks table."""

    __tablename__ = "project_risks"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    risk_code: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="MEDIUM", index=True, nullable=False)
    probability: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)
    impact: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", index=True, nullable=False)
    mitigation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    owner: Mapped[str] = mapped_column(String(255), default="Student", nullable=False)
    review_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class ProjectDocumentModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for project_documents table."""

    __tablename__ = "project_documents"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    document_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), default="SPECIFICATION", index=True, nullable=False)
    format: Mapped[str] = mapped_column(String(50), default="markdown", nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="BLUEPRINT_GENERATED", nullable=False)
