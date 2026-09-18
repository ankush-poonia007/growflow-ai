"""
GrowFlow — Execution Management API Schemas.

Pydantic schemas for:
- Tasks
- Milestones
- Risks
- Roadmap (Deterministic Projection)
- Documents
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Task Schemas
# ============================================================================

class TaskCreatePayload(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    priority: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    category: str = ""
    phase: str = Field(default="PLANNING", pattern="^(PLANNING|IMPLEMENTATION|TESTING|DEPLOYMENT)$")
    milestone_id: str | None = None
    due_date: datetime | None = None
    dependencies: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)


class TaskUpdatePayload(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = Field(default=None, pattern="^(TODO|IN_PROGRESS|BLOCKED|COMPLETED)$")
    priority: str | None = Field(default=None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    category: str | None = None
    phase: str | None = Field(default=None, pattern="^(PLANNING|IMPLEMENTATION|TESTING|DEPLOYMENT)$")
    milestone_id: str | None = None
    due_date: datetime | None = None
    dependencies: list[str] | None = None
    acceptance_criteria: list[str] | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_instance_id: str
    milestone_id: str | None = None
    task_code: str = ""
    title: str
    description: str = ""
    status: str
    priority: str
    category: str = ""
    phase: str
    due_date: datetime | None = None
    dependencies: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Milestone Schemas
# ============================================================================

class MilestoneCreatePayload(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    gate_code: str = ""
    target_date: datetime | None = None
    deliverables: list[str] = Field(default_factory=list)


class MilestoneUpdatePayload(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    gate_code: str | None = None
    target_date: datetime | None = None
    status: str | None = Field(default=None, pattern="^(UPCOMING|IN_PROGRESS|COMPLETED|AT_RISK)$")
    deliverables: list[str] | None = None


class MilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_instance_id: str
    title: str
    description: str = ""
    gate_code: str = ""
    target_date: datetime | None = None
    status: str
    progress_percent: int = 0
    deliverables: list[str] = Field(default_factory=list)
    section_order: int = 0
    task_count: int = 0
    completed_task_count: int = 0
    tasks: list[TaskResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Risk Schemas
# ============================================================================

class RiskCreatePayload(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    severity: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    probability: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH)$")
    impact: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH)$")
    mitigation: str = ""
    owner: str = "Student"
    review_date: datetime | None = None


class RiskUpdatePayload(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    severity: str | None = Field(default=None, pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    probability: str | None = Field(default=None, pattern="^(LOW|MEDIUM|HIGH)$")
    impact: str | None = Field(default=None, pattern="^(LOW|MEDIUM|HIGH)$")
    status: str | None = Field(default=None, pattern="^(OPEN|MITIGATING|RESOLVED|ACCEPTED)$")
    mitigation: str | None = None
    owner: str | None = None
    review_date: datetime | None = None


class RiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_instance_id: str
    risk_code: str = ""
    title: str
    description: str = ""
    severity: str
    probability: str
    impact: str
    status: str
    mitigation: str = ""
    owner: str = "Student"
    review_date: datetime | None = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Roadmap Projection Schemas
# ============================================================================

class RoadmapSummary(BaseModel):
    total_milestones: int
    completed_milestones: int
    total_tasks: int
    completed_tasks: int
    overdue_tasks_count: int
    blocked_tasks_count: int
    current_phase: str
    overall_progress: int


class RoadmapMilestoneItem(BaseModel):
    id: str
    gate_code: str
    title: str
    description: str = ""
    status: str
    progress_percent: int
    target_date: datetime | None = None
    deliverables: list[str] = Field(default_factory=list)
    tasks: list[TaskResponse] = Field(default_factory=list)


class RoadmapGroupedTasks(BaseModel):
    overdue: list[TaskResponse] = Field(default_factory=list)
    blocked: list[TaskResponse] = Field(default_factory=list)
    in_progress: list[TaskResponse] = Field(default_factory=list)
    upcoming: list[TaskResponse] = Field(default_factory=list)
    completed: list[TaskResponse] = Field(default_factory=list)


class RoadmapResponse(BaseModel):
    project_id: str
    project_name: str
    current_phase: str
    summary: RoadmapSummary
    milestones: list[RoadmapMilestoneItem]
    grouped_tasks: RoadmapGroupedTasks


# ============================================================================
# Document Schemas
# ============================================================================

class DocumentCreatePayload(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    doc_type: str = Field(default="SPECIFICATION", pattern="^(BLUEPRINT|ARCHITECTURE|SPECIFICATION|README|REPORT|GENERAL)$")
    format: str = Field(default="markdown", pattern="^(markdown|text)$")
    content: str = ""


class DocumentUpdatePayload(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = None
    status: str | None = Field(default=None, pattern="^(ACTIVE|ARCHIVED|DRAFT)$")


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_instance_id: str
    document_key: str
    title: str
    doc_type: str
    format: str
    content: str
    version: str
    status: str
    source: str
    created_at: datetime
    updated_at: datetime
