"""
GrowFlow — Mentor Supervision API Schemas.

Defines response payloads for:
- M10: Mentor Students Directory
- M11: Student Detail
- M12: Student Projects
- M16: Mentor Projects Directory
- M22: Student Project Instances
- M23: Project Instance Detail
- M31: Global At-Risk Directory
- M32: Global At-Risk Detail
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, computed_field

from backend.app.api.schemas.project import ProjectResponseSchema


class MentorStudentGroupSummarySchema(BaseModel):
    """Cohort summary for a student enrolled in a mentor-supervised group."""

    model_config = ConfigDict(from_attributes=True)

    group_id: str
    group_name: str
    joined_at: datetime | None = None
    membership_status: str


class MentorStudentSummarySchema(BaseModel):
    """Cross-group student summary for M10 Students Directory."""

    model_config = ConfigDict(from_attributes=True)

    student_id: str
    full_name: str
    email: str
    avatar_url: str | None = None
    groups: list[MentorStudentGroupSummarySchema] = []
    project_count: int = 0
    active_project_count: int = 0
    latest_phase: str | None = None
    latest_health: str | None = None


class MentorStudentDetailSchema(BaseModel):
    """Read-only student supervision detail for M11."""

    model_config = ConfigDict(from_attributes=True)

    student_id: str
    full_name: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    goals: str | None = None
    interests: str | None = None
    groups: list[MentorStudentGroupSummarySchema] = []
    projects: list[ProjectResponseSchema] = []

    @computed_field
    @property
    def id(self) -> str:
        return self.student_id


class MentorProjectInstanceSummarySchema(BaseModel):
    """Cross-group project instance summary for M16, M22, and M31."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    student_id: str
    student_name: str
    student_email: str
    group_id: str | None = None
    group_name: str | None = None
    current_phase: str
    health: str
    progress_percentage: int
    status: str
    deadline: datetime | None = None
    source_definition_id: str | None = None
    source_definition_name: str | None = None
    source_definition_version_number: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MentorProjectInstanceDetailSchema(BaseModel):
    """Detailed read-only student project instance for M23 and M32."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    problem: str
    proposed_solution: str
    complexity: str
    current_phase: str
    health: str
    progress_percentage: int
    status: str
    deadline: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    student_id: str
    student_name: str
    student_email: str
    group_id: str | None = None
    group_name: str | None = None
    source_definition_id: str | None = None
    source_definition_name: str | None = None
    source_definition_version_number: int | None = None
    objective: str | None = None
    scope: str | None = None
    expected_outcome: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MentorHelpRequestSummarySchema(BaseModel):
    """Schema for a student help request displayed in the mentor inbox."""

    id: str
    project_instance_id: str
    project_name: str
    student_id: str
    student_name: str
    student_email: str
    group_id: str | None = None
    group_name: str | None = None
    subject: str
    description: str
    category: str
    priority: str
    status: str
    mentor_response: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class HelpRequestRespondPayload(BaseModel):
    """Payload for a mentor responding to a student help request."""

    mentor_response: str = Field(..., min_length=1, max_length=5000)
    status: str = Field(default="RESOLVED")


class MentorNoteCreatePayload(BaseModel):
    """Payload for a mentor creating a note on a project instance."""

    project_instance_id: str
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=5000)
    note_type: str = Field(default="INFORMATIONAL")
    related_resource_type: str | None = None
    related_resource_id: str | None = None


class MentorNoteItemSchema(BaseModel):
    """Schema for a mentor note on a project instance."""

    id: str
    project_instance_id: str
    mentor_id: str | None = None
    mentor_name: str | None = None
    title: str
    message: str
    note_type: str
    status: str
    related_resource_type: str | None = None
    related_resource_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MentorAIChatPayload(BaseModel):
    """Payload for initiating a conversation turn with Group AI or Mentor Portfolio AI."""

    message: str = Field(..., min_length=1, max_length=5000)
    history: list[dict[str, Any]] | None = None


class MentorAIChatResponse(BaseModel):
    """Response returned from Group AI or Mentor Portfolio AI consultation."""

    user_message: dict[str, Any]
    assistant_message: dict[str, Any]
    ai_available: bool
    scope: str
    group_id: str | None = None
    group_name: str | None = None
    mentor_id: str | None = None


class MentorAIStatusResponse(BaseModel):
    """Availability status and scope metadata for Group AI or Mentor Portfolio AI."""

    ai_available: bool
    scope: str
    group_id: str | None = None
    group_name: str | None = None
    mentor_id: str | None = None

