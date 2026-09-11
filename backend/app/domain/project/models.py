"""
GrowFlow — Project Domain Models.

Defines canonical domain entities, state machines, and enums for:
- Project Definitions & immutable snapshots
- Project Instances, Profiles, Technologies, and Histories

Architecture ref:
  6B § 7.1 — project_definitions
  6B § 7.2 — project_definition_versions
  6B § 7.3 — project_instances
  6B § 10.1 — project_profiles
  6B § 11.1 — project_technologies
  6B § 20 & § 44 — project_phase_history & canonical phase model
  6B § 21 & § 43 — project_health_history & health model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime
    import uuid


class ProjectPhase(StrEnum):
    """
    Canonical 8-stage project lifecycle sequence.

    Architecture ref: 6B § 44.
    """

    IDEA = "IDEA"
    ASSESSMENT = "ASSESSMENT"
    BLUEPRINT = "BLUEPRINT"
    PLANNING = "PLANNING"
    IMPLEMENTATION = "IMPLEMENTATION"
    TESTING = "TESTING"
    DEPLOYMENT = "DEPLOYMENT"
    COMPLETED = "COMPLETED"


CANONICAL_PHASE_ORDER: list[ProjectPhase] = [
    ProjectPhase.IDEA,
    ProjectPhase.ASSESSMENT,
    ProjectPhase.BLUEPRINT,
    ProjectPhase.PLANNING,
    ProjectPhase.IMPLEMENTATION,
    ProjectPhase.TESTING,
    ProjectPhase.DEPLOYMENT,
    ProjectPhase.COMPLETED,
]

CANONICAL_NEXT_PHASE: dict[ProjectPhase, ProjectPhase] = {
    ProjectPhase.IDEA: ProjectPhase.ASSESSMENT,
    ProjectPhase.ASSESSMENT: ProjectPhase.BLUEPRINT,
    ProjectPhase.BLUEPRINT: ProjectPhase.PLANNING,
    ProjectPhase.PLANNING: ProjectPhase.IMPLEMENTATION,
    ProjectPhase.IMPLEMENTATION: ProjectPhase.TESTING,
    ProjectPhase.TESTING: ProjectPhase.DEPLOYMENT,
    ProjectPhase.DEPLOYMENT: ProjectPhase.COMPLETED,
}


def can_transition_phase(current: ProjectPhase, target: ProjectPhase) -> bool:
    """
    Validate whether a phase transition adheres to the canonical sequential state machine.

    Arbitrary forward leaps (e.g. IDEA -> IMPLEMENTATION) are forbidden.
    """
    return CANONICAL_NEXT_PHASE.get(current) == target


class ProjectHealth(StrEnum):
    """
    Canonical project health indicators.

    Architecture ref: 6B § 43, 5C § 15 & § 39.
    """

    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class ProjectComplexity(StrEnum):
    """Complexity classification for project definitions and instances."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class ProjectStatus(StrEnum):
    """Overall operational lifecycle status of a student project instance."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class ProjectDefinitionStatus(StrEnum):
    """Lifecycle status of a mentor project definition."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


@dataclass
class ProjectDefinition:
    """Reusable mentor-owned project definition."""

    id: uuid.UUID
    owner_mentor_id: uuid.UUID
    name: str
    status: ProjectDefinitionStatus = ProjectDefinitionStatus.DRAFT
    current_version_id: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ProjectDefinitionVersion:
    """Immutable snapshot of a project definition version."""

    id: uuid.UUID
    project_definition_id: uuid.UUID
    version_number: int
    name: str
    problem: str
    proposed_solution: str
    created_by: uuid.UUID
    complexity: ProjectComplexity = ProjectComplexity.INTERMEDIATE
    description: str = ""
    duration: str = ""
    constraints: str = ""
    assumptions: str = ""
    technology_snapshot: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime | None = None


@dataclass
class ProjectInstance:
    """Independent student-owned project execution context."""

    id: uuid.UUID
    student_id: uuid.UUID
    name: str
    problem: str = ""
    proposed_solution: str = ""
    complexity: ProjectComplexity = ProjectComplexity.INTERMEDIATE
    current_phase: ProjectPhase = ProjectPhase.IDEA
    health: ProjectHealth = ProjectHealth.HEALTHY
    progress_percentage: int = 0
    status: ProjectStatus = ProjectStatus.ACTIVE
    group_id: uuid.UUID | None = None
    project_definition_id: uuid.UUID | None = None
    source_definition_version_id: uuid.UUID | None = None
    deadline: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ProjectProfile:
    """Structured application profile for a project instance."""

    id: uuid.UUID
    project_instance_id: uuid.UUID
    objective: str = ""
    target_users: str = ""
    project_type: str = ""
    student_skill_context: str = ""
    goals: str = ""
    scope: str = ""
    expected_outcome: str = ""
    constraints: str = ""
    assumptions: str = ""
    context: str = ""
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ProjectTechnology:
    """Technology decision within a project instance."""

    id: uuid.UUID
    project_instance_id: uuid.UUID
    technology_id: uuid.UUID
    category: str = ""
    purpose: str = ""
    why_selected: str = ""
    appropriateness: str = ""
    student_understanding: str = ""
    usage_context: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ProjectPhaseHistory:
    """Authoritative historical record of a project phase transition."""

    id: uuid.UUID
    project_instance_id: uuid.UUID
    previous_phase: ProjectPhase
    new_phase: ProjectPhase
    changed_by: uuid.UUID
    reason: str = ""
    changed_at: datetime | None = None


@dataclass
class ProjectHealthHistory:
    """Authoritative historical record of a project health transition."""

    id: uuid.UUID
    project_instance_id: uuid.UUID
    previous_health: ProjectHealth
    new_health: ProjectHealth
    changed_by: uuid.UUID
    reason: str = ""
    changed_at: datetime | None = None
