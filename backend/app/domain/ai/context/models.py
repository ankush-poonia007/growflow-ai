"""
GrowFlow — Typed Context Models & Agent Projections.

Defines:
- ProjectBaseContext: Curated, isolated project metadata extracted from PostgreSQL.
- AssessmentContext: Enriched Project Understanding and student assessment answers.
- Purpose-built agent projection models (IdeaAgentContext, TechnologyAgentContext, etc.).

Architecture ref:
  6F § 15 — Agent Context Architecture
  6F § 16 — Context Is Not 'Everything'
  6F § 17 — Agent Context Contracts
  6F § 90 — Agent Data Isolation
  Gate 09 — Unit 2 Implementation
"""

from __future__ import annotations

from typing import Any
import uuid  # noqa: TC003 — Pydantic runtime schema validation

from pydantic import BaseModel, ConfigDict, Field

# ==============================================================================
# 1. Base Context Models
# ==============================================================================


class AssessmentAnswerItem(BaseModel):
    """Scoped student answer from the completed assessment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    question_id: str
    question_index: int
    question_text: str
    selected_option: str | None = None
    text_response: str | None = None


class AssessmentContext(BaseModel):
    """Authoritative Enriched Project Understanding (EPU) and relevant responses."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    assessment_id: uuid.UUID
    project_id: uuid.UUID
    skill_level: str
    project_complexity: str
    alignment: str
    technical_confidence: str
    learning_depth: str
    overall_score: int
    readiness_tier: str
    dimension_scores: dict[str, Any] = Field(default_factory=dict)
    identified_gaps: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    answers: list[AssessmentAnswerItem] = Field(default_factory=list)


class ProjectBaseContext(BaseModel):
    """
    Curated, sanitized base project metadata.
    Strictly excludes mentor notes, administrative data, and credentials.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    project_id: uuid.UUID
    student_id: uuid.UUID
    name: str
    problem: str
    proposed_solution: str
    complexity: str
    current_phase: str
    health: str
    profile_objective: str = ""
    profile_target_users: str = ""
    profile_constraints: str = ""
    profile_assumptions: str = ""
    preferred_technologies: list[str] = Field(default_factory=list)


# ==============================================================================
# 2. Purpose-Built Agent Projections
# ==============================================================================


class IdeaAgentContext(BaseModel):
    """Tailored context projection for Idea Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    project_name: str
    problem: str
    proposed_solution: str
    complexity: str
    skill_level: str
    readiness_tier: str
    assessment_recommendations: list[str] = Field(default_factory=list)


class ScopeAgentContext(BaseModel):
    """Tailored context projection for Scope Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    profile_constraints: str
    profile_assumptions: str
    identified_gaps: list[str] = Field(default_factory=list)


class TechnologyAgentContext(BaseModel):
    """Tailored context projection for Technology Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    skill_level: str
    complexity: str
    preferred_technologies: list[str] = Field(default_factory=list)


class FeaturesAgentContext(BaseModel):
    """Tailored context projection for Features Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    target_users: str
    profile_objective: str


class MVPAgentContext(BaseModel):
    """Tailored context projection for MVP Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    complexity: str
    skill_level: str


class SpecificationAgentContext(BaseModel):
    """Tailored context projection for Specification Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    project_name: str
    complexity: str


class TimelineAgentContext(BaseModel):
    """Tailored context projection for Timeline Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    complexity: str
    deadline_weeks: int = 12


class RiskAgentContext(BaseModel):
    """Tailored context projection for Risk Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    identified_gaps: list[str] = Field(default_factory=list)
    complexity: str


class TaskAgentContext(BaseModel):
    """Tailored context projection for Task Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    complexity: str


class MilestoneAgentContext(BaseModel):
    """Tailored context projection for Milestone Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    project_name: str


class ReadmeAgentContext(BaseModel):
    """Tailored context projection for README Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    project_name: str


class QAJudgeAgentContext(BaseModel):
    """Tailored context projection for QA / Judge Agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    project_base: ProjectBaseContext
    assessment: AssessmentContext
