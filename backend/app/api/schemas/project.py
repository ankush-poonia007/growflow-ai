"""
GrowFlow — Project API Request & Response Schemas.

Architecture ref:
  6C § 13 — Project Instance APIs
  6C § 14 — Project Overview API
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Pydantic runtime schema validation
from typing import Any

from pydantic import BaseModel, Field


class ProjectCreateSchema(BaseModel):
    """Payload for a student to create an independent project instance."""

    name: str = Field(min_length=1, max_length=255)
    problem: str = Field(default="")
    proposed_solution: str = Field(default="")
    complexity: str = Field(default="INTERMEDIATE")
    technologies: list[str] = Field(default_factory=list)
    deadline: datetime | None = None
    group_id: str | None = None


class ProjectUpdateSchema(BaseModel):
    """Payload to update an existing project instance."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    problem: str | None = None
    proposed_solution: str | None = None
    complexity: str | None = None
    deadline: datetime | None = None


class ProjectPhaseTransitionSchema(BaseModel):
    """Payload to transition project lifecycle phase."""

    target_phase: str
    reason: str = Field(default="")


class ProjectHealthUpdateSchema(BaseModel):
    """Payload to record a project health transition."""

    health: str
    reason: str = Field(default="")


class ProjectResponseSchema(BaseModel):
    """Response schema for a project instance."""

    id: str
    student_id: str
    group_id: str | None = None
    project_definition_id: str | None = None
    source_definition_version_id: str | None = None
    name: str
    problem: str
    proposed_solution: str
    complexity: str | None = "INTERMEDIATE"
    current_phase: str
    health: str
    progress_percentage: int
    status: str
    deadline: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProjectOverviewResponseSchema(BaseModel):
    """Aggregated project overview response schema per 6C § 14."""

    id: str
    student_id: str
    group_id: str | None = None
    project_definition_id: str | None = None
    name: str
    problem: str
    proposed_solution: str
    complexity: str
    current_phase: str
    health: str
    progress_percentage: int
    status: str
    deadline: str | None = None
    days_remaining: int | None = None
    profile: dict[str, Any] | None = None
    technologies: list[dict[str, Any]] = Field(default_factory=list)
    recent_activity: dict[str, Any] = Field(default_factory=dict)
