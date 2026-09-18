"""
GrowFlow — Workspace Extensions ORM Models (Batch 06: S27–S33).

Defines database models for:
- project_github_integrations (Observation/monitoring metadata, non-canonical read-cache)
- project_blueprint_versions (Non-destructive blueprint version history)
- project_change_requests (Formal impact analysis and regeneration records)
- ai_mentor_conversations & ai_mentor_messages (Project-scoped AI conversation records)
- project_help_requests (Student-side assistance request lifecycle)
- project_mentor_notes (Advisory and actionable mentor communication)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

JSON_TYPE = JSON().with_variant(postgresql.JSONB(), "postgresql")


class ProjectGitHubIntegrationModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Observation and monitoring metadata for linked GitHub repository.
    Non-canonical read model; does NOT act as a competing git store.
    """

    __tablename__ = "project_github_integrations"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    repository_name: Mapped[str] = mapped_column(String(255), nullable=False)
    repository_url: Mapped[str] = mapped_column(String(500), nullable=False)
    connection_status: Mapped[str] = mapped_column(
        String(50),
        default="NOT_CONNECTED",
        nullable=False,
    )
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    commit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    sync_error: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    cached_commits_preview: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON_TYPE,
        nullable=True,
        default=None,
    )


class ProjectBlueprintVersionModel(Base, UUIDPrimaryKeyMixin):
    """
    Non-destructive historical blueprint snapshots.
    Follows canonical project_definition_versions pattern with dynamic version_number.
    """

    __tablename__ = "project_blueprint_versions"

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
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="APPROVED", nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, nullable=False)
    qa_score: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    qa_feedback: Mapped[dict[str, Any] | None] = mapped_column(JSON_TYPE, nullable=True, default=None)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("blueprint_id", "version_number", name="uq_project_blueprint_version"),
    )


class ProjectChangeRequestModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Formal change proposals, deterministic impact analysis, and regeneration outcomes.
    """

    __tablename__ = "project_change_requests"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    change_title: Mapped[str] = mapped_column(String(255), nullable=False)
    change_description: Mapped[str] = mapped_column(Text, nullable=False)
    change_type: Mapped[str] = mapped_column(String(50), default="SCOPE", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ANALYZED", nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    impact_analysis: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, nullable=False)
    source_blueprint_version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    resulting_blueprint_version_number: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    qa_score: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    qa_feedback: Mapped[dict[str, Any] | None] = mapped_column(JSON_TYPE, nullable=True, default=None)


class AIMentorConversationModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Project-scoped AI conversation header.
    """

    __tablename__ = "ai_mentor_conversations"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), default="Project Consultation", nullable=False)


class AIMentorMessageModel(Base, UUIDPrimaryKeyMixin):
    """
    Individual message in an AI Mentor conversation thread.
    Normal messages do NOT mutate project state.
    """

    __tablename__ = "ai_mentor_messages"

    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_mentor_conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[list[dict[str, Any]]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    suggested_action: Mapped[dict[str, Any] | None] = mapped_column(JSON_TYPE, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class ProjectHelpRequestModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Student-side assistance request lifecycle.
    """

    __tablename__ = "project_help_requests"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    student_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="TECHNICAL", nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="OPEN", nullable=False)
    mentor_response: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class ProjectMentorNoteModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Advisory and actionable communication delivered from mentors to students.
    """

    __tablename__ = "project_mentor_notes"

    project_instance_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("project_instances.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    mentor_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[str] = mapped_column(String(50), default="INFORMATIONAL", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="UNREAD", nullable=False)
    related_resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
    related_resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True, default=None)
