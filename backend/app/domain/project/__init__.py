"""
GrowFlow — Domain Project Package.

Exports project definitions, instances, profiles, technologies, phase/health histories,
and canonical state machines.
"""

from backend.app.domain.project.models import (
    CANONICAL_NEXT_PHASE,
    CANONICAL_PHASE_ORDER,
    ProjectComplexity,
    ProjectDefinition,
    ProjectDefinitionStatus,
    ProjectDefinitionVersion,
    ProjectHealth,
    ProjectHealthHistory,
    ProjectInstance,
    ProjectPhase,
    ProjectPhaseHistory,
    ProjectProfile,
    ProjectStatus,
    ProjectTechnology,
    can_transition_phase,
)

__all__ = [
    "CANONICAL_NEXT_PHASE",
    "CANONICAL_PHASE_ORDER",
    "ProjectComplexity",
    "ProjectDefinition",
    "ProjectDefinitionStatus",
    "ProjectDefinitionVersion",
    "ProjectHealth",
    "ProjectHealthHistory",
    "ProjectInstance",
    "ProjectPhase",
    "ProjectPhaseHistory",
    "ProjectProfile",
    "ProjectStatus",
    "ProjectTechnology",
    "can_transition_phase",
]
