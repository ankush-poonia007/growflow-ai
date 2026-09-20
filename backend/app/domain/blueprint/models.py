"""
GrowFlow — Blueprint Domain Models.

Defines pure domain entities, state machines, and enums for:
- Blueprint lifecycle states and progression
- 10 canonical architectural output sections
- QA / Judge scoring, evaluation, and feedback
- Blueprint generation jobs and targeted recovery

Architecture ref:
  6B § 7 — Project Instances & Relationships
  6N § 18 — AI Provider Gateway
  6N § 20 — Blueprint Agent Graph
  6N § 21 — AI Output Authority Boundary
  Gate 09 — AI Blueprint & Agent System
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
import uuid


class BlueprintStatus(StrEnum):
    """
    Authoritative Blueprint lifecycle states.
    """

    NOT_STARTED = "NOT_STARTED"
    GENERATING = "GENERATING"
    GENERATED = "GENERATED"
    VALIDATING = "VALIDATING"
    QA_REJECTED = "QA_REJECTED"
    READY_FOR_APPROVAL = "READY_FOR_APPROVAL"
    APPROVED = "APPROVED"
    FAILED = "FAILED"


class BlueprintQAStatus(StrEnum):
    """
    Authoritative QA / Judge evaluation status.
    """

    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"


class BlueprintJobType(StrEnum):
    """
    Type of blueprint generation job.
    """

    FULL_GENERATION = "FULL_GENERATION"
    TARGETED_RETRY = "TARGETED_RETRY"


class BlueprintJobStatus(StrEnum):
    """
    Execution status of an asynchronous/persistent blueprint job.
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BlueprintSectionKey(StrEnum):
    """
    The 10 canonical high-level document/output sections of a GrowFlow Blueprint.
    """

    PROJECT_PROFILE = "project_profile"
    TECH_STACK = "tech_stack"
    FEATURES = "features"
    SPECIFICATIONS = "specifications"
    MVP = "mvp"
    DURATION = "duration"
    RISKS = "risks"
    TASKS = "tasks"
    MILESTONES = "milestones"
    README = "readme"


CANONICAL_BLUEPRINT_SECTION_ORDER: list[BlueprintSectionKey] = [
    BlueprintSectionKey.PROJECT_PROFILE,
    BlueprintSectionKey.TECH_STACK,
    BlueprintSectionKey.FEATURES,
    BlueprintSectionKey.SPECIFICATIONS,
    BlueprintSectionKey.MVP,
    BlueprintSectionKey.DURATION,
    BlueprintSectionKey.RISKS,
    BlueprintSectionKey.TASKS,
    BlueprintSectionKey.MILESTONES,
    BlueprintSectionKey.README,
]


@dataclass(frozen=True)
class BlueprintIssue:
    """A specific issue identified by validation or the QA/Judge."""

    section: str
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    recommendation: str


@dataclass(frozen=True)
class BlueprintQAFeedback:
    """Structured QA/Judge scorecard evaluating the generated blueprint."""

    status: BlueprintQAStatus
    score: int  # 0..100
    summary: str
    evaluated_criteria: dict[str, int] = field(default_factory=dict)
    issues: list[BlueprintIssue] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class BlueprintSession:
    """Pure domain entity representing a project's blueprint."""

    id: uuid.UUID
    project_instance_id: uuid.UUID
    student_id: uuid.UUID
    status: BlueprintStatus
    current_step: str | None = None
    progress_percent: int = 0
    error_message: str | None = None
    failed_output_key: str | None = None
    qa_status: BlueprintQAStatus = BlueprintQAStatus.PENDING
    qa_score: int | None = None
    qa_feedback: BlueprintQAFeedback | None = None
    content: dict[str, Any] = field(default_factory=dict)
    generation_number: int = 1
    approved_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
