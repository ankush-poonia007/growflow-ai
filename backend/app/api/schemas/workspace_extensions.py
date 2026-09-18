"""
GrowFlow — Workspace Extensions Pydantic Schemas (Batch 06: S27–S33).

Defines request and response models for:
- GitHub observation & sync
- Canonical activity audit trail
- AI Mentor conversations & action confirmation
- Help requests & mentor feedback
- Project changes & versioned regenerations
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# GitHub (S27)
# -----------------------------------------------------------------------------
class GitHubConnectPayload(BaseModel):
    repository_url: str = Field(..., min_length=5, description="Full HTTPS URL of GitHub repository")
    repository_name: str | None = Field(None, description="Optional repository name")
    default_branch: str = Field(default="main", description="Primary default branch name")


class GitHubIntegrationResponse(BaseModel):
    id: str | None = None
    project_instance_id: str
    repository_name: str = ""
    repository_url: str = ""
    connection_status: str = "NOT_CONNECTED"
    default_branch: str = "main"
    commit_count: int = 0
    last_sync_at: str | None = None
    sync_error: str | None = None
    cached_commits_preview: list[dict[str, Any]] = []


# -----------------------------------------------------------------------------
# Activity (S28)
# -----------------------------------------------------------------------------
class ActivityItemResponse(BaseModel):
    id: str
    event_type: str
    title: str
    description: str
    actor_role: str
    actor_id: str | None = None
    resource_type: str
    resource_id: str
    occurred_at: str | None = None
    metadata: dict[str, Any] = {}


# -----------------------------------------------------------------------------
# AI Mentor (S29)
# -----------------------------------------------------------------------------
class AIMentorSendMessagePayload(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class AIMentorExecuteActionPayload(BaseModel):
    action_type: str = Field(..., description="Action type to execute (e.g. CREATE_TASK, CREATE_HELP_REQUEST)")
    payload: dict[str, Any] = Field(default_factory=dict)


class AIMentorMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: list[dict[str, Any]] = []
    suggested_action: dict[str, Any] | None = None
    created_at: str | None = None


class AIMentorConversationResponse(BaseModel):
    conversation_id: str
    project_instance_id: str
    title: str
    ai_available: bool
    messages: list[AIMentorMessageResponse] = []


class AIMentorSendResponse(BaseModel):
    user_message: AIMentorMessageResponse
    assistant_message: AIMentorMessageResponse
    ai_available: bool


# -----------------------------------------------------------------------------
# Help Requests (S30)
# -----------------------------------------------------------------------------
class HelpRequestCreatePayload(BaseModel):
    subject: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5, max_length=5000)
    category: str = Field(default="TECHNICAL")
    priority: str = Field(default="MEDIUM")


class HelpRequestResponse(BaseModel):
    id: str
    project_instance_id: str
    student_id: str
    subject: str
    description: str
    category: str
    priority: str
    status: str
    mentor_response: str | None = None
    resolved_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# -----------------------------------------------------------------------------
# Mentor Feedback (S31)
# -----------------------------------------------------------------------------
class MentorNoteResponse(BaseModel):
    id: str
    project_instance_id: str
    mentor_id: str | None = None
    title: str
    message: str
    note_type: str
    status: str
    related_resource_type: str | None = None
    related_resource_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# -----------------------------------------------------------------------------
# Project Changes & Regeneration (S32 & S33)
# -----------------------------------------------------------------------------
class ProjectChangeAnalyzePayload(BaseModel):
    change_title: str = Field(..., min_length=3, max_length=255)
    change_description: str = Field(..., min_length=10, max_length=5000)
    change_type: str = Field(default="SCOPE")  # SCOPE, TECH_STACK, ARCHITECTURE, SCHEDULE


class ProjectChangeConfirmPayload(BaseModel):
    idempotency_key: str | None = Field(None, max_length=100)


class ProjectChangeResponse(BaseModel):
    id: str
    project_instance_id: str
    student_id: str
    change_title: str
    change_description: str
    change_type: str
    status: str
    idempotency_key: str | None = None
    impact_analysis: dict[str, Any] = {}
    source_blueprint_version_number: int = 1
    resulting_blueprint_version_number: int | None = None
    qa_score: int | None = None
    qa_feedback: dict[str, Any] | None = None
    created_at: str | None = None
    updated_at: str | None = None


class BlueprintVersionResponse(BaseModel):
    id: str
    blueprint_id: str
    project_instance_id: str
    version_number: int
    status: str
    qa_score: int | None = None
    qa_feedback: dict[str, Any] | None = None
    change_summary: str | None = None
    created_at: str | None = None
    content: dict[str, Any] | None = None
