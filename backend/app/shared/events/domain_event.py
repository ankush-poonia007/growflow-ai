"""
GrowFlow — Canonical Domain Event & Outbox Contracts.

Defines the standard domain event schema and outbox lifecycle states.

Architecture ref:
  6B § 29 — domain_events
  6B § 30 — Transactional outbox
  6H § 6  — Domain events catalogue
  6H § 7  — Event contract fields
  6H § 14 — Outbox lifecycle
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
import uuid


class DomainEventType(StrEnum):
    """Canonical domain event types supported in Gate 05."""

    PROJECT_CREATED = "ProjectCreated"
    PROJECT_PHASE_CHANGED = "ProjectPhaseChanged"
    PROJECT_HEALTH_CHANGED = "ProjectHealthChanged"
    GROUP_CREATED = "GroupCreated"
    STUDENT_JOINED_GROUP = "StudentJoinedGroup"
    PROJECT_DEFINITION_CREATED = "ProjectDefinitionCreated"
    PROJECT_DEFINITION_ASSIGNED = "ProjectDefinitionAssigned"
    BLUEPRINT_GENERATED = "BlueprintGenerated"
    BLUEPRINT_APPROVED = "BlueprintApproved"
    TASK_CREATED = "TaskCreated"
    TASK_UPDATED = "TaskUpdated"
    TASK_COMPLETED = "TaskCompleted"
    MILESTONE_UPDATED = "MilestoneUpdated"
    RISK_CREATED = "RiskCreated"
    RISK_UPDATED = "RiskUpdated"
    DOCUMENT_CREATED = "DocumentCreated"
    DOCUMENT_UPDATED = "DocumentUpdated"
    GITHUB_CONNECTED = "GitHubConnected"
    GITHUB_SYNCED = "GitHubSynced"
    HELP_REQUEST_CREATED = "HelpRequestCreated"
    HELP_REQUEST_UPDATED = "HelpRequestUpdated"
    MENTOR_NOTE_CREATED = "MentorNoteCreated"
    MENTOR_NOTE_ACKNOWLEDGED = "MentorNoteAcknowledged"
    PROJECT_CHANGE_REQUESTED = "ProjectChangeRequested"
    PROJECT_CHANGE_ANALYZED = "ProjectChangeAnalyzed"
    PROJECT_CHANGE_CONFIRMED = "ProjectChangeConfirmed"
    PROJECT_CHANGE_COMPLETED = "ProjectChangeCompleted"
    AI_MENTOR_MESSAGE_SENT = "AIMentorMessageSent"


class OutboxStatus(StrEnum):
    """Lifecycle status of an outbox record."""

    PENDING = "PENDING"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class EventVisibility(StrEnum):
    """Visibility scope of the event."""

    INTERNAL = "INTERNAL"
    STUDENT = "STUDENT"
    MENTOR = "MENTOR"
    PUBLIC = "PUBLIC"


def utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass
class DomainEvent:
    """Canonical domain event container and transactional outbox item."""

    event_type: str
    actor_role: str
    resource_type: str
    resource_id: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    actor_id: uuid.UUID | None = None
    project_instance_id: uuid.UUID | None = None
    group_id: uuid.UUID | None = None
    visibility: EventVisibility = EventVisibility.INTERNAL
    metadata: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""
    status: OutboxStatus = OutboxStatus.PENDING
    occurred_at: datetime = field(default_factory=utcnow)
    published_at: datetime | None = None
    attempt_count: int = 0
    last_error: str | None = None
