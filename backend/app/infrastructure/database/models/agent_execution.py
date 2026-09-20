"""
GrowFlow — Agent Execution SQLAlchemy ORM Model.

Defines ORM mappings for:
- agent_executions (persistent provenance records for individual agent executions)

Architecture ref:
  6B § 27.2 — agent_executions
  6E § 31   — Execution Provenance Tracking
  6F § 45   — Agent Model & Capability Assignment
  Gate 09 — Unit 4 Orchestration & Durable Execution
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — evaluated at runtime by SQLAlchemy mapper

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AgentExecutionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for agent_executions tracking per-agent execution provenance."""

    __tablename__ = "agent_executions"

    blueprint_job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("blueprint_jobs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
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
    execution_id: Mapped[str] = mapped_column(
        String(36),
        index=True,
        nullable=False,
    )
    correlation_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
    )
    agent_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    agent_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    prompt_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    contract_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    generation_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    regeneration_attempt: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    key_alias: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    capability: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    prompt_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    completion_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    estimated_cost_usd: Mapped[float] = mapped_column(
        Numeric(10, 6),
        default=0.0,
        nullable=False,
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
