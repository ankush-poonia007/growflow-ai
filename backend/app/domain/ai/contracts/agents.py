"""
GrowFlow — Generator Agent Contracts & Nested Pydantic Schemas.

Defines the typed input and output contracts for the 11 generator agents:
1. Idea Agent
2. Scope Agent
3. Technology Agent
4. Features Agent
5. MVP Agent
6. Specification Agent
7. Timeline / Duration Agent
8. Risk Agent
9. Task Agent
10. Milestone Agent
11. README Agent

Architecture ref:
  6F § 4  — Agent Responsibilities (4.1 through 4.11)
  6F § 5  — Agent Input/Output Contract
  Gate 09 — Unit 2 Implementation
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.domain.ai.contracts.base import BaseAgentInput, BaseAgentOutput

# ==============================================================================
# 1. Enums
# ==============================================================================


class LearningCurve(StrEnum):
    """Learning curve assessment for recommended technologies."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    STEEP = "STEEP"


class FeaturePriority(StrEnum):
    """Canonical feature priority classification."""

    P0 = "P0"  # Must have / Core foundational
    P1 = "P1"  # Should have / Important functional
    P2 = "P2"  # Good to have / Stretch goal


class RiskCategory(StrEnum):
    """Architectural and operational risk taxonomy."""

    TECHNICAL = "TECHNICAL"
    OPERATIONAL = "OPERATIONAL"
    INTEGRATION = "INTEGRATION"
    SCOPE = "SCOPE"
    SECURITY = "SECURITY"


class RiskSeverity(StrEnum):
    """Severity ratings for identified project risks."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RiskLikelihood(StrEnum):
    """Probability of risk materialization."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TaskCategory(StrEnum):
    """Granular work breakdown domains."""

    SETUP = "SETUP"
    DATABASE = "DATABASE"
    BACKEND = "BACKEND"
    FRONTEND = "FRONTEND"
    INTEGRATION = "INTEGRATION"
    TESTING = "TESTING"
    DEPLOYMENT = "DEPLOYMENT"


class TaskPriority(StrEnum):
    """Task scheduling priority."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class GateDecision(StrEnum):
    """Milestone gate evaluation deliverables."""

    GATE_1_FOUNDATION = "GATE_1_FOUNDATION"
    GATE_2_CORE_MVP = "GATE_2_CORE_MVP"
    GATE_3_POLISH_HANDOFF = "GATE_3_POLISH_HANDOFF"


# ==============================================================================
# 2. Common Nested Structures
# ==============================================================================


class TechItem(BaseModel):
    """A specific technology stack decision."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Name of technology/framework.")
    version: str | None = Field(default=None, description="Recommended version or major release.")
    role: str = Field(..., description="Role within the architecture (e.g. Web framework, ORM).")
    rationale: str = Field(..., description="Technical justification for selecting this tool.")
    learning_curve: LearningCurve = Field(..., description="Expected learning curve for student.")


class TechJustification(BaseModel):
    """Detailed justification for technology choices within a category."""

    model_config = ConfigDict(extra="forbid")

    technology_name: str
    category: str
    selection_rationale: str
    student_understanding_expectation: str


class FeatureItem(BaseModel):
    """A discrete, prioritized project capability."""

    model_config = ConfigDict(extra="forbid")

    feature_id: str = Field(
        ...,
        pattern=r"^F\d{2}$",
        description="Deterministic identifier formatted as F01, F02, etc.",
    )
    title: str = Field(..., description="Concise feature name.")
    description: str = Field(..., description="Functional description of capability.")
    priority: FeaturePriority = Field(..., description="P0 (Must), P1 (Should), P2 (Good to have).")
    module: str = Field(..., description="Subsystem/module this feature belongs to.")
    user_story: str = Field(..., description="As a <user>, I want <action> so that <benefit>.")
    dependencies: list[str] = Field(
        default_factory=list,
        description="List of feature_ids that must precede this feature.",
    )


class FieldSpec(BaseModel):
    """Specification of an entity field or attribute."""

    model_config = ConfigDict(extra="forbid")

    name: str
    data_type: str
    required: bool = True
    description: str = ""


class DataEntitySpec(BaseModel):
    """Technical data model / schema specification."""

    model_config = ConfigDict(extra="forbid")

    entity_name: str = Field(..., description="Name of the domain entity/table.")
    fields: list[FieldSpec] = Field(default_factory=list, description="Attributes and types.")
    relationships: list[str] = Field(
        default_factory=list,
        description="Relationships to other entities (e.g. 1-to-many with Task).",
    )


class APIEndpointSpec(BaseModel):
    """REST API endpoint contract specification."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(..., description="URL path (e.g. /api/v1/projects).")
    method: str = Field(..., description="HTTP Method (GET, POST, PUT, DELETE, PATCH).")
    description: str = Field(..., description="Operational intent of endpoint.")
    auth_required: bool = True
    request_payload_summary: str | None = None
    response_summary: str = "JSON response specification."


class IntegrationFlowSpec(BaseModel):
    """Interaction between components or external services."""

    model_config = ConfigDict(extra="forbid")

    flow_name: str
    source_component: str
    target_component: str
    description: str


class ResearchSource(BaseModel):
    """Provenance for external web/document evidence (e.g. Tavily/RAG)."""

    model_config = ConfigDict(extra="forbid")

    title: str
    url: str | None = None
    snippet: str = ""
    source_type: str = "WEB"


class TimelinePhase(BaseModel):
    """Phased development sprint or interval."""

    model_config = ConfigDict(extra="forbid")

    phase_number: int = Field(..., ge=1)
    name: str
    duration_weeks: int = Field(..., ge=1)
    focus_area: str
    deliverables: list[str] = Field(default_factory=list)
    dependencies: list[int] = Field(default_factory=list)


class RiskItem(BaseModel):
    """Identified project risk with mitigation strategy."""

    model_config = ConfigDict(extra="forbid")

    risk_id: str = Field(
        ...,
        pattern=r"^R\d{2}$",
        description="Deterministic identifier formatted as R01, R02, etc.",
    )
    category: RiskCategory
    title: str
    severity: RiskSeverity
    likelihood: RiskLikelihood
    impact_description: str
    warning_signs: list[str] = Field(default_factory=list)
    mitigation_strategy: str
    fallback_plan: str


class TaskItem(BaseModel):
    """Granular implementation task within work breakdown structure."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(
        ...,
        pattern=r"^T\d{2}$",
        description="Deterministic identifier formatted as T01, T02, etc.",
    )
    title: str
    description: str
    category: TaskCategory
    priority: TaskPriority
    estimated_hours: int = Field(..., ge=1)
    dependencies: list[str] = Field(
        default_factory=list,
        description="List of task_ids that must precede this task.",
    )
    feature_id: str | None = Field(
        default=None,
        description="Associated feature_id if directly tied to a feature.",
    )


class MilestoneItem(BaseModel):
    """Major stage gate deliverable grouping tasks."""

    model_config = ConfigDict(extra="forbid")

    milestone_id: str = Field(
        ...,
        pattern=r"^M\d{1,2}$",
        description="Identifier formatted as M1, M2, etc.",
    )
    name: str
    target_week: int = Field(..., ge=1)
    deliverables: list[str] = Field(default_factory=list)
    associated_task_ids: list[str] = Field(default_factory=list)
    verification_criteria: str
    gate_decision: GateDecision


class EnvVarSpec(BaseModel):
    """Environment configuration variable specification."""

    model_config = ConfigDict(extra="forbid")

    name: str
    required: bool = True
    default_value: str | None = None
    description: str = ""


# ==============================================================================
# 3. Agent 1: Idea Agent
# ==============================================================================


class IdeaAgentInput(BaseAgentInput):
    """Input context for Idea Agent."""

    project_name: str
    initial_problem: str
    initial_solution: str
    complexity_preference: str
    student_skill_level: str
    assessment_readiness_tier: str
    assessment_recommendations: list[str] = Field(default_factory=list)


class IdeaAgentOutput(BaseAgentOutput):
    """Synthesized core project idea and domain profile."""

    refined_title: str
    vision_statement: str
    problem_statement: str
    proposed_solution: str
    target_users: list[str] = Field(..., min_length=1)
    value_propositions: list[str] = Field(..., min_length=2)
    core_domain: str


# ==============================================================================
# 4. Agent 2: Scope Agent
# ==============================================================================


class ScopeAgentInput(BaseAgentInput):
    """Input context for Scope Agent."""

    idea: IdeaAgentOutput
    assessment_gaps: list[str] = Field(default_factory=list)


class ScopeAgentOutput(BaseAgentOutput):
    """Rigid boundaries and in/out-of-scope declarations."""

    in_scope: list[str] = Field(..., min_length=3)
    out_of_scope: list[str] = Field(..., min_length=2)
    architectural_boundaries: list[str] = Field(..., min_length=2)
    technical_constraints: list[str] = Field(..., min_length=1)
    deliverable_outcomes: list[str] = Field(..., min_length=1)


# ==============================================================================
# 5. Agent 3: Technology Agent
# ==============================================================================


class TechnologyAgentInput(BaseAgentInput):
    """Input context for Technology Agent."""

    idea: IdeaAgentOutput
    scope: ScopeAgentOutput
    student_skill_level: str
    preferred_technologies: list[str] = Field(default_factory=list)


class TechnologyAgentOutput(BaseAgentOutput):
    """Complete technology stack selection with learning rationale."""

    backend: TechItem
    database: TechItem
    frontend: TechItem
    communication_protocols: list[str] = Field(..., min_length=1)
    security_auth: TechItem
    telemetry_observability: TechItem
    third_party_services: list[TechItem] = Field(default_factory=list)
    justification_matrix: list[TechJustification] = Field(default_factory=list)


# ==============================================================================
# 6. Agent 4: Features Agent
# ==============================================================================


class FeaturesAgentInput(BaseAgentInput):
    """Input context for Features Agent."""

    idea: IdeaAgentOutput
    scope: ScopeAgentOutput


class FeaturesAgentOutput(BaseAgentOutput):
    """Decomposed, prioritized feature capabilities."""

    features: list[FeatureItem] = Field(..., min_length=4)

    @model_validator(mode="after")
    def validate_features_composition(self) -> FeaturesAgentOutput:
        """Validate feature ID uniqueness and priority distribution."""
        ids = [f.feature_id for f in self.features]
        if len(ids) != len(set(ids)):
            raise ValueError("All feature_ids must be unique")
        p0_count = sum(1 for f in self.features if f.priority == FeaturePriority.P0)
        if p0_count < 2:
            raise ValueError(
                f"Features output must contain at least 2 P0 features (found {p0_count})"
            )
        return self


# ==============================================================================
# 7. Agent 5: MVP Agent
# ==============================================================================


class MVPAgentInput(BaseAgentInput):
    """Input context for MVP Agent."""

    idea: IdeaAgentOutput
    scope: ScopeAgentOutput
    research_evidence: list[ResearchSource] = Field(default_factory=list)


class MVPAgentOutput(BaseAgentOutput):
    """Lean Stage-1 MVP boundary and user journey."""

    mvp_name: str
    core_user_journey: list[str] = Field(..., min_length=3)
    included_capabilities: list[str] = Field(..., min_length=2)
    excluded_from_mvp: list[str] = Field(..., min_length=1)
    validation_criteria: list[str] = Field(..., min_length=2)
    minimum_viable_architecture: str


# ==============================================================================
# 8. Agent 6: Specification Agent
# ==============================================================================


class SpecificationAgentInput(BaseAgentInput):
    """Input context for Specification Agent (synchronization point)."""

    idea: IdeaAgentOutput
    scope: ScopeAgentOutput
    technology: TechnologyAgentOutput
    features: FeaturesAgentOutput
    mvp: MVPAgentOutput


class SpecificationAgentOutput(BaseAgentOutput):
    """Technical implementation specifications and interfaces."""

    entities: list[DataEntitySpec] = Field(..., min_length=2)
    api_endpoints: list[APIEndpointSpec] = Field(..., min_length=3)
    integration_flows: list[IntegrationFlowSpec] = Field(default_factory=list)
    system_acceptance_criteria: list[str] = Field(..., min_length=2)


# ==============================================================================
# 9. Agent 7: Timeline / Duration Agent
# ==============================================================================


class TimelineAgentInput(BaseAgentInput):
    """Input context for Timeline Agent."""

    idea: IdeaAgentOutput
    specification: SpecificationAgentOutput
    complexity: str
    project_deadline_weeks: int | None = 12


class TimelineAgentOutput(BaseAgentOutput):
    """Phased duration breakdown and critical path."""

    estimated_total_weeks: int = Field(..., ge=1)
    phases: list[TimelinePhase] = Field(..., min_length=3)
    critical_path_summary: str

    @model_validator(mode="after")
    def validate_phase_durations(self) -> TimelineAgentOutput:
        """Enforce that phase durations sum exactly to estimated_total_weeks."""
        total_phase_weeks = sum(p.duration_weeks for p in self.phases)
        if total_phase_weeks != self.estimated_total_weeks:
            raise ValueError(
                f"Sum of phase duration_weeks ({total_phase_weeks}) must equal "
                f"estimated_total_weeks ({self.estimated_total_weeks})"
            )
        return self


# ==============================================================================
# 10. Agent 8: Risk Agent
# ==============================================================================


class RiskAgentInput(BaseAgentInput):
    """Input context for Risk Agent."""

    technology: TechnologyAgentOutput
    features: FeaturesAgentOutput
    specification: SpecificationAgentOutput
    timeline: TimelineAgentOutput


class RiskAgentOutput(BaseAgentOutput):
    """Technical and operational risk mitigations."""

    risks: list[RiskItem] = Field(..., min_length=4)

    @model_validator(mode="after")
    def validate_risk_categories(self) -> RiskAgentOutput:
        """Enforce coverage of both TECHNICAL and SECURITY risks."""
        categories = {r.category for r in self.risks}
        if RiskCategory.TECHNICAL not in categories:
            raise ValueError("Risk assessment must include at least one TECHNICAL risk")
        if RiskCategory.SECURITY not in categories:
            raise ValueError("Risk assessment must include at least one SECURITY risk")
        ids = [r.risk_id for r in self.risks]
        if len(ids) != len(set(ids)):
            raise ValueError("All risk_ids must be unique")
        return self


# ==============================================================================
# 11. Agent 9: Task Agent
# ==============================================================================


class TaskAgentInput(BaseAgentInput):
    """Input context for Task Agent."""

    specification: SpecificationAgentOutput
    technology: TechnologyAgentOutput
    features: FeaturesAgentOutput
    timeline: TimelineAgentOutput
    risks: RiskAgentOutput


class TaskAgentOutput(BaseAgentOutput):
    """Granular work breakdown structure."""

    tasks: list[TaskItem] = Field(..., min_length=8)

    @model_validator(mode="after")
    def validate_task_ids(self) -> TaskAgentOutput:
        """Enforce task ID uniqueness."""
        ids = [t.task_id for t in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("All task_ids must be unique")
        return self


# ==============================================================================
# 12. Agent 10: Milestone Agent
# ==============================================================================


class MilestoneAgentInput(BaseAgentInput):
    """Input context for Milestone Agent (strictly serial after Task Agent)."""

    timeline: TimelineAgentOutput
    tasks: TaskAgentOutput


class MilestoneAgentOutput(BaseAgentOutput):
    """Gate deliverables and milestone schedule."""

    milestones: list[MilestoneItem] = Field(..., min_length=3)

    @model_validator(mode="after")
    def validate_milestones(self) -> MilestoneAgentOutput:
        """Enforce milestone ID uniqueness."""
        ids = [m.milestone_id for m in self.milestones]
        if len(ids) != len(set(ids)):
            raise ValueError("All milestone_ids must be unique")
        return self


# ==============================================================================
# 13. Agent 11: README Agent
# ==============================================================================


class ReadmeCuratedContext(BaseModel):
    """Curated validated outputs from all upstream agents for README synthesis."""

    model_config = ConfigDict(extra="forbid")

    idea: IdeaAgentOutput
    scope: ScopeAgentOutput
    technology: TechnologyAgentOutput
    features: FeaturesAgentOutput
    mvp: MVPAgentOutput
    timeline: TimelineAgentOutput
    risks: RiskAgentOutput
    tasks: TaskAgentOutput
    milestones: MilestoneAgentOutput


class ReadmeAgentInput(BaseAgentInput):
    """Input context for README Agent."""

    curated_context: ReadmeCuratedContext


class ReadmeAgentOutput(BaseAgentOutput):
    """Synthesized project README and setup guide."""

    project_title: str
    project_tagline: str
    overview: str
    architecture_overview: str
    tech_stack_summary: dict[str, str]
    getting_started: list[str] = Field(..., min_length=2)
    environment_variables: list[EnvVarSpec] = Field(default_factory=list)
    contributing_guidelines: str
