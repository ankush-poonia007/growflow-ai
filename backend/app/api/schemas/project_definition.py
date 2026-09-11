"""
GrowFlow — Project Definition API Request & Response Schemas.

Architecture ref:
  6C § 12 — Project Definition APIs
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Pydantic runtime schema validation
from typing import Any

from pydantic import BaseModel, Field


class ProjectDefinitionCreateSchema(BaseModel):
    """Payload to create a new reusable project definition."""

    name: str = Field(min_length=1, max_length=255)
    problem: str = Field(min_length=1)
    proposed_solution: str = Field(min_length=1)
    complexity: str = Field(default="INTERMEDIATE")
    description: str = Field(default="")
    duration: str = Field(default="")
    constraints: str = Field(default="")
    assumptions: str = Field(default="")
    technology_snapshot: list[dict[str, Any]] = Field(default_factory=list)


class ProjectDefinitionUpdateSchema(BaseModel):
    """Payload to update a project definition and publish a new version."""

    name: str | None = None
    problem: str | None = None
    proposed_solution: str | None = None
    complexity: str | None = None
    description: str | None = None
    duration: str | None = None
    constraints: str | None = None
    assumptions: str | None = None
    technology_snapshot: list[dict[str, Any]] | None = None


class ProjectDefinitionVersionResponseSchema(BaseModel):
    """Response schema for a specific definition version snapshot."""

    id: str
    project_definition_id: str
    version_number: int
    name: str
    problem: str
    proposed_solution: str
    complexity: str
    description: str | None = ""
    duration: str | None = ""
    constraints: str | None = ""
    assumptions: str | None = ""
    technology_snapshot: list[Any] = Field(default_factory=list)
    created_by: str
    created_at: datetime | None = None


class ProjectDefinitionResponseSchema(BaseModel):
    """Response schema for a project definition container."""

    id: str
    owner_mentor_id: str
    name: str
    status: str
    current_version_id: str | None = None
    current_version: ProjectDefinitionVersionResponseSchema | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProjectDefinitionAssignSchema(BaseModel):
    """Payload to assign a project definition to a student."""

    student_id: str
    group_id: str | None = None
    deadline: datetime | None = None
