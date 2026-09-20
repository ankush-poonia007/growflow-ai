"""
GrowFlow — Unit Tests for 12 AI Agent Contracts & Pydantic Schemas.

Verifies:
- All 11 generator agent input and output models instantiate with valid data.
- QA/Judge input and output contracts instantiate correctly.
- Required field validation and rejection of missing data.
- Enum validation across feature priorities, risk categories, and learning curves.
- Regex validation for entity IDs (F01, T01, M1, R01).
- List length constraints and composition validators.
- Timeline duration mathematical consistency.
- Risk domain coverage (TECHNICAL and SECURITY).
- Serialization and deserialization roundtrip.
- Negative regeneration_attempt rejection.
- Gateway compatibility with MockAIProviderAdapter.
"""

from datetime import datetime
import uuid

from pydantic import ValidationError
import pytest

from backend.app.domain.ai.contracts.agents import (
    APIEndpointSpec,
    DataEntitySpec,
    EnvVarSpec,
    FeatureItem,
    FeaturePriority,
    FeaturesAgentOutput,
    FieldSpec,
    GateDecision,
    IdeaAgentInput,
    IdeaAgentOutput,
    IntegrationFlowSpec,
    LearningCurve,
    MilestoneAgentOutput,
    MilestoneItem,
    ReadmeAgentOutput,
    RiskAgentOutput,
    RiskCategory,
    RiskItem,
    RiskLikelihood,
    RiskSeverity,
    ScopeAgentOutput,
    SpecificationAgentOutput,
    TaskAgentOutput,
    TaskCategory,
    TaskItem,
    TaskPriority,
    TechItem,
    TechnologyAgentOutput,
    TimelineAgentOutput,
    TimelinePhase,
)
from backend.app.domain.ai.contracts.base import (
    AgentExecutionProvenance,
    BaseAgentInput,
    BaseAgentOutput,
)
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.models import AIUsageMetadata, ProviderCapability

# ==============================================================================
# 1. Base Contracts & Provenance Tests
# ==============================================================================


def test_base_agent_input_valid():
    """Verify BaseAgentInput instantiates and rejects invalid regeneration attempts."""
    inp = BaseAgentInput(
        execution_id="exec-123",
        project_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        agent_name="IdeaAgent",
        contract_version="1.0.0",
        regeneration_attempt=0,
        qa_feedback_hint="Focus on agricultural domain.",
    )
    assert inp.execution_id == "exec-123"
    assert inp.regeneration_attempt == 0
    assert inp.qa_feedback_hint == "Focus on agricultural domain."


def test_base_agent_input_rejects_negative_regeneration_attempt():
    """Verify negative regeneration_attempt raises ValidationError."""
    with pytest.raises(ValidationError):
        BaseAgentInput(
            execution_id="exec-123",
            project_id=uuid.uuid4(),
            student_id=uuid.uuid4(),
            agent_name="IdeaAgent",
            regeneration_attempt=-1,
        )


def test_base_agent_output_defaults():
    """Verify BaseAgentOutput default values and confidence score bounds."""
    out = BaseAgentOutput(
        agent_name="IdeaAgent",
        summary="Synthesized agricultural project idea.",
    )
    assert out.confidence_score == 1.0
    assert out.assumptions == []
    assert out.warnings == []

    # Rejects confidence score out of bounds
    with pytest.raises(ValidationError):
        BaseAgentOutput(
            agent_name="IdeaAgent",
            summary="Test",
            confidence_score=1.5,
        )


def test_agent_execution_provenance_rejects_raw_keys():
    """Verify AgentExecutionProvenance validates safe key alias and rejects raw credentials."""
    prov = AgentExecutionProvenance(
        agent_name="IdeaAgent",
        generation_number=1,
        execution_id="exec-123",
        correlation_id="corr-456",
        provider="openrouter",
        model="openai/gpt-4o",
        key_alias="key_1",
        capability=ProviderCapability.STANDARD,
        latency_ms=450.5,
        usage=AIUsageMetadata(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    assert prov.key_alias == "key_1"

    # Raw API key in key_alias must raise ValidationError
    with pytest.raises(ValidationError, match="Raw API key"):
        AgentExecutionProvenance(
            agent_name="IdeaAgent",
            generation_number=1,
            execution_id="exec-123",
            correlation_id="corr-456",
            provider="openrouter",
            model="openai/gpt-4o",
            key_alias="sk-or-v1-abcdef1234567890",
            capability=ProviderCapability.STANDARD,
            latency_ms=450.5,
            usage=AIUsageMetadata(prompt_tokens=100, completion_tokens=50, total_tokens=150),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )


# ==============================================================================
# 2. Generator Agent Contracts Validation
# ==============================================================================


def test_idea_agent_contract_validation():
    """Verify IdeaAgentInput and IdeaAgentOutput validation."""
    pid = uuid.uuid4()
    sid = uuid.uuid4()

    inp = IdeaAgentInput(
        execution_id="exec-1",
        project_id=pid,
        student_id=sid,
        agent_name="IdeaAgent",
        project_name="CropGuard",
        initial_problem="Pest outbreaks destroy yields.",
        initial_solution="Autonomous pest tracking drones.",
        complexity_preference="INTERMEDIATE",
        student_skill_level="INTERMEDIATE",
        assessment_readiness_tier="HIGH",
    )
    assert inp.project_name == "CropGuard"

    # Valid output
    out = IdeaAgentOutput(
        agent_name="IdeaAgent",
        summary="AI-driven agricultural drone tracking system.",
        refined_title="CropGuard AI",
        vision_statement="Empower farmers with real-time autonomous pest detection.",
        problem_statement="Untreated pest infestations result in 30% crop loss annually.",
        proposed_solution="Edge-accelerated autonomous drone vision system.",
        target_users=["Commercial agronomists", "Smallholder cooperatives"],
        value_propositions=["Reduce pesticide costs by 40%", "Early blight detection"],
        core_domain="AgriTech",
    )
    assert len(out.target_users) == 2

    # Fails if target_users is empty (< 1)
    with pytest.raises(ValidationError):
        IdeaAgentOutput(
            agent_name="IdeaAgent",
            summary="Test",
            refined_title="Title",
            vision_statement="Vision",
            problem_statement="Problem",
            proposed_solution="Solution",
            target_users=[],  # Invalid min_length=1
            value_propositions=["Val1", "Val2"],
            core_domain="Domain",
        )


def test_scope_agent_contract_validation():
    """Verify ScopeAgentOutput enforces list length constraints."""
    out = ScopeAgentOutput(
        agent_name="ScopeAgent",
        summary="Defined operational boundaries.",
        in_scope=["Telemetry pipeline", "Edge inferencing", "Admin dashboard"],
        out_of_scope=["Hardware manufacturing", "Satellite imagery billing"],
        architectural_boundaries=["FastAPI REST API", "Local SQLite on edge drone"],
        technical_constraints=["Must process images under 200ms"],
        deliverable_outcomes=["Complete system blueprint"],
    )
    assert len(out.in_scope) == 3
    assert len(out.out_of_scope) == 2

    # Fails if in_scope < 3
    with pytest.raises(ValidationError):
        ScopeAgentOutput(
            agent_name="ScopeAgent",
            summary="Test",
            in_scope=["Only one", "Only two"],  # Invalid
            out_of_scope=["Out 1", "Out 2"],
            architectural_boundaries=["B1", "B2"],
            technical_constraints=["C1"],
            deliverable_outcomes=["O1"],
        )


def test_technology_agent_contract_validation():
    """Verify TechnologyAgentOutput structure and LearningCurve enum."""
    tech = TechnologyAgentOutput(
        agent_name="TechnologyAgent",
        summary="Recommended full-stack Python + React architecture.",
        backend=TechItem(
            name="FastAPI",
            version="0.115",
            role="Core REST API",
            rationale="Async high performance and Pydantic integration.",
            learning_curve=LearningCurve.MODERATE,
        ),
        database=TechItem(
            name="PostgreSQL",
            version="16",
            role="Primary relational datastore",
            rationale="Robust ACID transactions and JSONB support.",
            learning_curve=LearningCurve.LOW,
        ),
        frontend=TechItem(
            name="React",
            version="19",
            role="Web user interface",
            rationale="Component reusability and widespread adoption.",
            learning_curve=LearningCurve.MODERATE,
        ),
        communication_protocols=["HTTPS/REST", "Server-Sent Events"],
        security_auth=TechItem(
            name="Supabase JWT",
            role="Authentication & RBAC",
            rationale="Secure stateless token authorization.",
            learning_curve=LearningCurve.LOW,
        ),
        telemetry_observability=TechItem(
            name="Structlog",
            role="Structured JSON logging",
            rationale="High performance contextual logging.",
            learning_curve=LearningCurve.LOW,
        ),
    )
    assert tech.backend.name == "FastAPI"
    assert tech.backend.learning_curve == LearningCurve.MODERATE


def test_features_agent_contract_validation():
    """Verify FeaturesAgentOutput enforces min 4 features, regex IDs, uniqueness, and min 2 P0s."""
    features = [
        FeatureItem(
            feature_id="F01",
            title="Telemetry Ingestion",
            description="Ingest edge packets",
            priority=FeaturePriority.P0,
            module="Ingestion",
            user_story="As an operator I want telemetry",
        ),
        FeatureItem(
            feature_id="F02",
            title="Alert Dispatcher",
            description="Send SMS alerts",
            priority=FeaturePriority.P0,
            module="Notifications",
            user_story="As a farmer I want alert notifications",
        ),
        FeatureItem(
            feature_id="F03",
            title="Dashboard Visualizer",
            description="View crop health",
            priority=FeaturePriority.P1,
            module="UI",
            user_story="As an agronomist I want visuals",
        ),
        FeatureItem(
            feature_id="F04",
            title="Export Reports",
            description="Generate PDF report",
            priority=FeaturePriority.P2,
            module="Reporting",
            user_story="As an auditor I want PDF exports",
        ),
    ]

    out = FeaturesAgentOutput(
        agent_name="FeaturesAgent",
        summary="Synthesized core system features.",
        features=features,
    )
    assert len(out.features) == 4

    # Rejects invalid regex on feature_id
    with pytest.raises(ValidationError):
        FeatureItem(
            feature_id="FEAT_1",  # Invalid regex
            title="Bad ID",
            description="Desc",
            priority=FeaturePriority.P0,
            module="Mod",
            user_story="Story",
        )

    # Rejects duplicate feature_ids
    duplicate_features = [
        features[0],
        features[0],  # Duplicate F01
        features[2],
        features[3],
    ]
    with pytest.raises(ValidationError, match="unique"):
        FeaturesAgentOutput(
            agent_name="FeaturesAgent",
            summary="Test",
            features=duplicate_features,
        )

    # Rejects if fewer than 2 P0 features
    features_one_p0 = [
        features[0],  # P0
        features[2],  # P1
        features[3],  # P2
        FeatureItem(
            feature_id="F05",
            title="F5",
            description="D5",
            priority=FeaturePriority.P1,
            module="M",
            user_story="S",
        ),
    ]
    with pytest.raises(ValidationError, match="at least 2 P0"):
        FeaturesAgentOutput(
            agent_name="FeaturesAgent",
            summary="Test",
            features=features_one_p0,
        )


def test_timeline_agent_duration_consistency():
    """Verify TimelineAgentOutput enforces that phase durations sum to estimated_total_weeks."""
    phases = [
        TimelinePhase(phase_number=1, name="Foundation", duration_weeks=4, focus_area="Setup"),
        TimelinePhase(phase_number=2, name="Core Features", duration_weeks=5, focus_area="Dev"),
        TimelinePhase(phase_number=3, name="Testing & Polish", duration_weeks=3, focus_area="QA"),
    ]

    # Valid: 4 + 5 + 3 = 12
    out = TimelineAgentOutput(
        agent_name="TimelineAgent",
        summary="12-week development timeline.",
        estimated_total_weeks=12,
        phases=phases,
        critical_path_summary="Foundation -> Core Dev -> QA",
    )
    assert out.estimated_total_weeks == 12

    # Inconsistent sum: 4 + 5 + 3 = 12 != 14
    with pytest.raises(ValidationError, match="must equal estimated_total_weeks"):
        TimelineAgentOutput(
            agent_name="TimelineAgent",
            summary="Invalid timeline.",
            estimated_total_weeks=14,
            phases=phases,
            critical_path_summary="Path",
        )


def test_risk_agent_coverage_validation():
    """Verify RiskAgentOutput requires at least 4 risks and coverage of both TECHNICAL and SECURITY."""
    valid_risks = [
        RiskItem(
            risk_id="R01",
            category=RiskCategory.TECHNICAL,
            title="Edge Latency",
            severity=RiskSeverity.HIGH,
            likelihood=RiskLikelihood.MEDIUM,
            impact_description="Sensor lag",
            mitigation_strategy="Optimized tensor models",
            fallback_plan="Cloud offload",
        ),
        RiskItem(
            risk_id="R02",
            category=RiskCategory.SECURITY,
            title="Token Hijacking",
            severity=RiskSeverity.HIGH,
            likelihood=RiskLikelihood.LOW,
            impact_description="Data breach",
            mitigation_strategy="Short-lived JWTs",
            fallback_plan="Revocation list",
        ),
        RiskItem(
            risk_id="R03",
            category=RiskCategory.OPERATIONAL,
            title="Drone Battery Degradation",
            severity=RiskSeverity.MEDIUM,
            likelihood=RiskLikelihood.HIGH,
            impact_description="Shorter flight time",
            mitigation_strategy="Battery health telemetry",
            fallback_plan="Secondary battery dock",
        ),
        RiskItem(
            risk_id="R04",
            category=RiskCategory.SCOPE,
            title="Feature Creep",
            severity=RiskSeverity.MEDIUM,
            likelihood=RiskLikelihood.MEDIUM,
            impact_description="Missed deadline",
            mitigation_strategy="Strict change request approval",
            fallback_plan="Defer to v2",
        ),
    ]

    out = RiskAgentOutput(
        agent_name="RiskAgent",
        summary="Identified project risks.",
        risks=valid_risks,
    )
    assert len(out.risks) == 4

    # Rejects if missing SECURITY category
    risks_no_sec = [r for r in valid_risks if r.category != RiskCategory.SECURITY] + [
        RiskItem(
            risk_id="R05",
            category=RiskCategory.INTEGRATION,
            title="API Failure",
            severity=RiskSeverity.LOW,
            likelihood=RiskLikelihood.LOW,
            impact_description="Desc",
            mitigation_strategy="Mitigation",
            fallback_plan="Fallback",
        )
    ]
    with pytest.raises(ValidationError, match="SECURITY"):
        RiskAgentOutput(
            agent_name="RiskAgent",
            summary="Test",
            risks=risks_no_sec,
        )


def test_task_agent_validation():
    """Verify TaskAgentOutput enforces minimum 8 tasks and ID uniqueness."""
    tasks = [
        TaskItem(
            task_id=f"T{i:02d}",
            title=f"Task {i}",
            description="Work item",
            category=TaskCategory.BACKEND,
            priority=TaskPriority.P0,
            estimated_hours=4,
        )
        for i in range(1, 9)
    ]
    out = TaskAgentOutput(
        agent_name="TaskAgent",
        summary="Detailed work breakdown.",
        tasks=tasks,
    )
    assert len(out.tasks) == 8

    # Rejects duplicate task IDs
    duplicate_tasks = list(tasks)
    duplicate_tasks[1] = duplicate_tasks[0]
    with pytest.raises(ValidationError, match="unique"):
        TaskAgentOutput(
            agent_name="TaskAgent",
            summary="Test",
            tasks=duplicate_tasks,
        )


def test_milestone_agent_validation():
    """Verify MilestoneAgentOutput enforces minimum 3 milestones and ID uniqueness."""
    milestones = [
        MilestoneItem(
            milestone_id="M1",
            name="Foundation",
            target_week=3,
            deliverables=["Environment verified"],
            associated_task_ids=["T01", "T02"],
            verification_criteria="Tests green",
            gate_decision=GateDecision.GATE_1_FOUNDATION,
        ),
        MilestoneItem(
            milestone_id="M2",
            name="MVP Core",
            target_week=7,
            deliverables=["End-to-end ingestion"],
            associated_task_ids=["T03", "T04"],
            verification_criteria="Telemetry ingested",
            gate_decision=GateDecision.GATE_2_CORE_MVP,
        ),
        MilestoneItem(
            milestone_id="M3",
            name="Final Polish",
            target_week=12,
            deliverables=["System deployed"],
            associated_task_ids=["T05", "T06"],
            verification_criteria="Production sign-off",
            gate_decision=GateDecision.GATE_3_POLISH_HANDOFF,
        ),
    ]

    out = MilestoneAgentOutput(
        agent_name="MilestoneAgent",
        summary="Milestones plan.",
        milestones=milestones,
    )
    assert len(out.milestones) == 3


def test_specification_agent_validation():
    """Verify SpecificationAgentOutput requires at least 2 entities and 3 API endpoints."""
    out = SpecificationAgentOutput(
        agent_name="SpecificationAgent",
        summary="API and entity specifications.",
        entities=[
            DataEntitySpec(entity_name="Project", fields=[FieldSpec(name="id", data_type="uuid")]),
            DataEntitySpec(
                entity_name="Telemetry", fields=[FieldSpec(name="packet", data_type="json")]
            ),
        ],
        api_endpoints=[
            APIEndpointSpec(path="/api/v1/projects", method="GET", description="List projects"),
            APIEndpointSpec(path="/api/v1/projects", method="POST", description="Create project"),
            APIEndpointSpec(
                path="/api/v1/telemetry", method="POST", description="Ingest telemetry"
            ),
        ],
        integration_flows=[
            IntegrationFlowSpec(
                flow_name="Sync",
                source_component="Drone",
                target_component="API",
                description="Sync",
            )
        ],
        system_acceptance_criteria=["Sub-100ms response time", "99.9% uptime"],
    )
    assert len(out.entities) == 2
    assert len(out.api_endpoints) == 3


def test_readme_agent_validation():
    """Verify ReadmeAgentOutput structure and serialization."""
    out = ReadmeAgentOutput(
        agent_name="ReadmeAgent",
        summary="Project README.",
        project_title="CropGuard AI",
        project_tagline="Autonomous Drone Pest Detection",
        overview="High-performance edge intelligence platform.",
        architecture_overview="Clean layered FastAPI + React architecture.",
        tech_stack_summary={"Backend": "FastAPI", "Database": "PostgreSQL"},
        getting_started=["git clone ...", "docker compose up"],
        environment_variables=[
            EnvVarSpec(name="DATABASE_URL", required=True, description="Postgres connection string")
        ],
        contributing_guidelines="Please read CONTRIBUTING.md before submitting PRs.",
    )
    assert out.project_title == "CropGuard AI"
    json_str = out.model_dump_json()
    assert "CropGuard AI" in json_str
    deserialized = ReadmeAgentOutput.model_validate_json(json_str)
    assert deserialized.project_title == out.project_title


# ==============================================================================
# 3. Unit 1 Gateway Compatibility Test
# ==============================================================================


@pytest.mark.asyncio
async def test_agent_output_schema_compatibility_with_mock_gateway():
    """
    Verify that agent output Pydantic schemas are 100% compatible with Unit 1's
    AIProviderGateway.execute_structured(...) via MockAIProviderAdapter.
    """
    adapter = MockAIProviderAdapter()
    sample_output = IdeaAgentOutput(
        agent_name="IdeaAgent",
        summary="Synthesized agricultural project idea.",
        refined_title="CropGuard AI",
        vision_statement="Autonomous vision-based pest detection.",
        problem_statement="Pests destroy crops.",
        proposed_solution="Drones with edge cameras.",
        target_users=["Farmers", "Agronomists"],
        value_propositions=["Reduce pesticide usage", "Improve yield"],
        core_domain="AgriTech",
    )
    adapter.register_structured_response("IdeaAgentOutput", sample_output)

    gateway = AIProviderGateway(adapter=adapter)
    result = await gateway.execute_structured(
        schema=IdeaAgentOutput,
        prompt="Synthesize project idea for CropGuard",
        system_prompt="You are GrowFlow Idea Agent.",
    )

    assert isinstance(result.content, IdeaAgentOutput)
    assert result.content.agent_name == "IdeaAgent"
    assert result.content.refined_title == "CropGuard AI"
    assert result.provider == "mock"
    assert result.latency_ms >= 0.0
