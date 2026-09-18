"""
GrowFlow — Blueprint Pydantic Schemas.

Defines typed request and response schemas for:
- /api/v1/projects/{project_id}/blueprint/status
- /api/v1/projects/{project_id}/blueprint/generate
- /api/v1/projects/{project_id}/blueprint/retry
- /api/v1/projects/{project_id}/blueprint/content
- /api/v1/projects/{project_id}/blueprint/approve
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field


class BlueprintIssueSchema(BaseModel):
    section: str
    severity: str
    description: str
    recommendation: str


class BlueprintQAFeedbackSchema(BaseModel):
    status: str
    score: int
    summary: str
    evaluated_criteria: dict[str, int] = Field(default_factory=dict)
    issues: list[BlueprintIssueSchema] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class BlueprintGenerationProgressSchema(BaseModel):
    completed_sections: list[str] = Field(default_factory=list)
    total_sections: int = 10
    in_progress_section: str | None = None
    failed_sections: list[str] = Field(default_factory=list)


class BlueprintStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    blueprint_id: uuid.UUID | None = None
    project_instance_id: uuid.UUID
    project_id: uuid.UUID | None = None
    student_id: uuid.UUID
    status: str
    current_step: str | None = None
    progress_percent: int = 0
    current_stage: int = 0
    generation_progress: BlueprintGenerationProgressSchema | None = None
    error_message: str | None = None
    failed_output_key: str | None = None
    qa_status: str
    qa_score: int | None = None
    qa_feedback: dict[str, Any] | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class BlueprintContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_instance_id: uuid.UUID
    status: str
    qa_status: str
    qa_score: int | None = None
    content: dict[str, Any] = Field(default_factory=dict)


class BlueprintGeneratePayload(BaseModel):
    force_regenerate: bool = False


class BlueprintRetryPayload(BaseModel):
    target_output_key: str | None = None


class BlueprintApproveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool
    status: str
    approved_at: datetime
