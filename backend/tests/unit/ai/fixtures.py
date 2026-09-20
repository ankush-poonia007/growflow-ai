"""
GrowFlow — Unit 3 Test Fixtures & Valid Contract Factories.

Provides fully compliant Pydantic v2 fixture instances for all 12 agent input
and output schemas to support zero-network mock provider execution and assertion.
"""

from __future__ import annotations

import uuid

from backend.app.domain.ai.context.models import AssessmentContext, ProjectBaseContext
from backend.app.domain.ai.contracts.agents import (
    APIEndpointSpec,
    DataEntitySpec,
    EnvVarSpec,
    FeatureItem,
    FeaturePriority,
    FeaturesAgentInput,
    FeaturesAgentOutput,
    FieldSpec,
    GateDecision,
    IdeaAgentInput,
    IdeaAgentOutput,
    IntegrationFlowSpec,
    LearningCurve,
    MilestoneAgentInput,
    MilestoneAgentOutput,
    MilestoneItem,
    MVPAgentInput,
    MVPAgentOutput,
    ReadmeAgentInput,
    ReadmeAgentOutput,
    ReadmeCuratedContext,
    RiskAgentInput,
    RiskAgentOutput,
    RiskCategory,
    RiskItem,
    RiskLikelihood,
    RiskSeverity,
    ScopeAgentInput,
    ScopeAgentOutput,
    SpecificationAgentInput,
    SpecificationAgentOutput,
    TaskAgentInput,
    TaskAgentOutput,
    TaskCategory,
    TaskItem,
    TaskPriority,
    TechItem,
    TechJustification,
    TechnologyAgentInput,
    TechnologyAgentOutput,
    TimelineAgentInput,
    TimelineAgentOutput,
    TimelinePhase,
)
from backend.app.domain.ai.contracts.qa import (
    QAFinding,
    QAJudgeAgentInput,
    QAJudgeAgentOutput,
    QASeverity,
)
from backend.app.domain.blueprint.models import BlueprintQAStatus

# Resolve forward references for QAJudgeAgentInput
QAJudgeAgentInput.model_rebuild(
    _types_namespace={
        "ProjectBaseContext": ProjectBaseContext,
        "AssessmentContext": AssessmentContext,
    }
)

TEST_PROJECT_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
TEST_STUDENT_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
TEST_EXECUTION_ID = "exec-test-run-001"


# ==============================================================================
# 1. Output Factories (Guaranteed to satisfy Pydantic validators)
# ==============================================================================


def make_idea_output() -> IdeaAgentOutput:
    return IdeaAgentOutput(
        agent_name="idea_agent",
        summary="Synthesized agricultural monitoring architecture.",
        confidence_score=0.95,
        assumptions=["Field telemetry is transmitted over cellular or LoRa."],
        warnings=["Battery life on field drones is constrained."],
        refined_title="AgriFlow Autonomous Telemetry System",
        vision_statement="Empower farmers with real-time autonomous sensor intelligence.",
        problem_statement="Fragmented crop health monitoring leads to crop loss.",
        proposed_solution="An autonomous drone telemetry pipeline with automated alerts.",
        target_users=["Agronomists", "Field Operators"],
        value_propositions=[
            "Reduce survey latency from 3 days to 10 minutes",
            "Continuous anomaly detection on soil and crop moisture",
        ],
        core_domain="Precision Agriculture",
    )


def make_scope_output() -> ScopeAgentOutput:
    return ScopeAgentOutput(
        agent_name="scope_agent",
        summary="Defined operational boundaries and constraints.",
        confidence_score=0.92,
        in_scope=[
            "Edge drone sensor ingestion over REST API",
            "PostgreSQL telemetry storage and threshold alerts",
            "Web dashboard for live field visualizations",
        ],
        out_of_scope=[
            "Hardware autopilot firmware programming",
            "Multi-tenant international cloud deployment",
        ],
        architectural_boundaries=[
            "Modular monolith backend with clear domain boundaries",
            "Strict isolation between telemetry ingestion and user dashboard",
        ],
        technical_constraints=[
            "Must deploy on a single 4GB RAM virtual machine",
        ],
        deliverable_outcomes=[
            "Functional REST API with 99.9% uptime for sensor payloads",
        ],
    )


def make_technology_output() -> TechnologyAgentOutput:
    return TechnologyAgentOutput(
        agent_name="technology_agent",
        summary="Cohesive Python and React technical stack selection.",
        confidence_score=0.94,
        backend=TechItem(
            name="FastAPI",
            version="0.115",
            role="Asynchronous Web API framework",
            rationale="High performance with native Pydantic validation.",
            learning_curve=LearningCurve.MODERATE,
        ),
        database=TechItem(
            name="PostgreSQL",
            version="16",
            role="Relational primary datastore",
            rationale="ACID guarantees and robust JSONB support for sensor metadata.",
            learning_curve=LearningCurve.LOW,
        ),
        frontend=TechItem(
            name="React",
            version="19",
            role="Single-page application client",
            rationale="Component reusability and mature ecosystem.",
            learning_curve=LearningCurve.MODERATE,
        ),
        communication_protocols=["HTTPS/REST", "Transactional Outbox Event Streams"],
        security_auth=TechItem(
            name="Supabase Auth / JWT",
            role="User authentication and token verification",
            rationale="Stateless JWT validation with role-based access control.",
            learning_curve=LearningCurve.LOW,
        ),
        telemetry_observability=TechItem(
            name="Structured JSON Logging",
            role="Operational telemetry",
            rationale="Correlation ID tracing across requests.",
            learning_curve=LearningCurve.LOW,
        ),
        third_party_services=[],
        justification_matrix=[
            TechJustification(
                technology_name="FastAPI",
                category="Backend",
                selection_rationale="Matches student's intermediate Python skills.",
                student_understanding_expectation="Must understand async/await syntax.",
            )
        ],
    )


def make_features_output() -> FeaturesAgentOutput:
    return FeaturesAgentOutput(
        agent_name="features_agent",
        summary="Prioritized backlog of 4 core project capabilities.",
        confidence_score=0.91,
        features=[
            FeatureItem(
                feature_id="F01",
                title="Sensor Telemetry Ingestion",
                description="Ingest edge drone multispectral and GPS packets.",
                priority=FeaturePriority.P0,
                module="Telemetry",
                user_story="As an operator, I want real-time sensor packets stored safely.",
                dependencies=[],
            ),
            FeatureItem(
                feature_id="F02",
                title="Threshold Alerting Engine",
                description="Evaluate sensor thresholds and trigger anomaly notifications.",
                priority=FeaturePriority.P0,
                module="Alerts",
                user_story="As an agronomist, I want alert triggers when moisture dips below 20%.",
                dependencies=["F01"],
            ),
            FeatureItem(
                feature_id="F03",
                title="Field Overview Dashboard",
                description="Interactive GIS map rendering drone paths and metric summaries.",
                priority=FeaturePriority.P1,
                module="Frontend",
                user_story="As an operator, I want to see drone paths on an interactive map.",
                dependencies=["F01"],
            ),
            FeatureItem(
                feature_id="F04",
                title="CSV Telemetry Export",
                description="Export historical sensor records to CSV for offline analysis.",
                priority=FeaturePriority.P2,
                module="Export",
                user_story="As a researcher, I want to export raw CSV telemetry data.",
                dependencies=["F01"],
            ),
        ],
    )


def make_mvp_output() -> MVPAgentOutput:
    return MVPAgentOutput(
        agent_name="mvp_agent",
        summary="Stage-1 core walking skeleton MVP boundary.",
        confidence_score=0.96,
        mvp_name="AgriFlow Core Telemetry MVP",
        core_user_journey=[
            "Drone edge agent posts sensor telemetry packet to API",
            "API stores telemetry and verifies anomaly threshold",
            "Operator logs in and views live reading on dashboard",
        ],
        included_capabilities=[
            "Autonomous sensor packet ingestion API",
            "Automated moisture threshold alert trigger",
        ],
        excluded_from_mvp=[
            "Historical predictive ML modeling",
        ],
        validation_criteria=[
            "Ingest 100 packets/sec with p99 latency < 200ms",
            "Zero telemetry record loss under simulated network disconnect",
        ],
        minimum_viable_architecture="FastAPI single service + PostgreSQL database on Docker.",
    )


def make_specification_output() -> SpecificationAgentOutput:
    return SpecificationAgentOutput(
        agent_name="specification_agent",
        summary="Technical data schemas and REST endpoint specifications.",
        confidence_score=0.93,
        entities=[
            DataEntitySpec(
                entity_name="TelemetryRecord",
                fields=[
                    FieldSpec(name="id", data_type="UUID", required=True),
                    FieldSpec(name="sensor_type", data_type="VARCHAR(50)", required=True),
                    FieldSpec(name="reading_value", data_type="FLOAT", required=True),
                ],
                relationships=["Belongs to FieldBoundary"],
            ),
            DataEntitySpec(
                entity_name="FieldBoundary",
                fields=[
                    FieldSpec(name="id", data_type="UUID", required=True),
                    FieldSpec(name="name", data_type="VARCHAR(100)", required=True),
                ],
                relationships=["Has many TelemetryRecords"],
            ),
        ],
        api_endpoints=[
            APIEndpointSpec(
                path="/api/v1/telemetry",
                method="POST",
                description="Ingest edge drone sensor telemetry packet.",
                auth_required=True,
            ),
            APIEndpointSpec(
                path="/api/v1/telemetry",
                method="GET",
                description="List historical telemetry for active field.",
                auth_required=True,
            ),
            APIEndpointSpec(
                path="/api/v1/alerts",
                method="GET",
                description="List unresolved anomaly alerts.",
                auth_required=True,
            ),
        ],
        integration_flows=[
            IntegrationFlowSpec(
                flow_name="Telemetry Ingestion Flow",
                source_component="Drone Edge Agent",
                target_component="FastAPI Ingestion Endpoint",
                description="HTTP POST payload validated and persisted to PostgreSQL.",
            )
        ],
        system_acceptance_criteria=[
            "All endpoints return standard RFC-7807 error envelopes on failure",
            "Sensor ingestion endpoint processes valid payload in < 150ms",
        ],
    )


def make_timeline_output() -> TimelineAgentOutput:
    return TimelineAgentOutput(
        agent_name="timeline_agent",
        summary="10-week phased implementation plan.",
        confidence_score=0.90,
        estimated_total_weeks=10,
        phases=[
            TimelinePhase(
                phase_number=1,
                name="Foundation & Architecture Setup",
                duration_weeks=3,
                focus_area="Database schemas, migrations, and auth integration.",
                deliverables=["PostgreSQL models", "FastAPI app scaffold"],
                dependencies=[],
            ),
            TimelinePhase(
                phase_number=2,
                name="Core Ingestion & Alerting Engine",
                duration_weeks=4,
                focus_area="Telemetry ingestion endpoints and threshold evaluations.",
                deliverables=["POST /api/v1/telemetry", "Alert event triggers"],
                dependencies=[1],
            ),
            TimelinePhase(
                phase_number=3,
                name="Frontend Dashboard & Verification",
                duration_weeks=3,
                focus_area="React dashboard components, end-to-end integration tests.",
                deliverables=["React dashboard", "Integration test suite"],
                dependencies=[2],
            ),
        ],
        critical_path_summary="Database schema setup -> Ingestion endpoint -> Alert trigger -> Dashboard.",
    )


def make_risk_output() -> RiskAgentOutput:
    return RiskAgentOutput(
        agent_name="risk_agent",
        summary="Threat model and risk mitigation matrix.",
        confidence_score=0.92,
        risks=[
            RiskItem(
                risk_id="R01",
                category=RiskCategory.TECHNICAL,
                title="Database write contention during telemetry bursts",
                severity=RiskSeverity.HIGH,
                likelihood=RiskLikelihood.MEDIUM,
                impact_description="High-frequency edge bursts could exhaust connection pool.",
                warning_signs=["Connection timeout logs in PostgreSQL"],
                mitigation_strategy="Implement batch insertion and connection pool sizing.",
                fallback_plan="Buffer telemetry locally on edge if backend returns 503.",
            ),
            RiskItem(
                risk_id="R02",
                category=RiskCategory.SECURITY,
                title="Unauthorized telemetry injection via unauthenticated endpoints",
                severity=RiskSeverity.HIGH,
                likelihood=RiskLikelihood.LOW,
                impact_description="Malicious actors could spoof sensor readings.",
                warning_signs=["Unexpected source IPs in ingestion logs"],
                mitigation_strategy="Enforce JWT or HMAC signing on all telemetry payloads.",
                fallback_plan="Revoke compromised edge API keys immediately.",
            ),
            RiskItem(
                risk_id="R03",
                category=RiskCategory.OPERATIONAL,
                title="Intermittent edge cellular connectivity",
                severity=RiskSeverity.MEDIUM,
                likelihood=RiskLikelihood.HIGH,
                impact_description="Drones operating in remote valleys lose connectivity.",
                warning_signs=["Gaps in telemetry timestamp sequences"],
                mitigation_strategy="Local SQLite buffering on drone edge software.",
                fallback_plan="Manual SD card extraction after mission landing.",
            ),
            RiskItem(
                risk_id="R04",
                category=RiskCategory.SCOPE,
                title="Over-ambitious GIS visualization scope",
                severity=RiskSeverity.LOW,
                likelihood=RiskLikelihood.MEDIUM,
                impact_description="Complex 3D map rendering delays MVP delivery.",
                warning_signs=["Frontend sprint velocity dropping in Phase 3"],
                mitigation_strategy="Stick to 2D Leaflet map view for MVP.",
                fallback_plan="Tabular data view fallback if map library causes defects.",
            ),
        ],
    )


def make_task_output() -> TaskAgentOutput:
    return TaskAgentOutput(
        agent_name="task_agent",
        summary="Detailed work breakdown structure with 8 granular engineering tasks.",
        confidence_score=0.91,
        tasks=[
            TaskItem(
                task_id="T01",
                title="Setup project workspace and Docker Compose environment",
                description="Initialize FastAPI repo, PostgreSQL container, and pyproject.toml.",
                category=TaskCategory.SETUP,
                priority=TaskPriority.P0,
                estimated_hours=6,
                dependencies=[],
            ),
            TaskItem(
                task_id="T02",
                title="Create PostgreSQL database schema and Alembic migrations",
                description="Define TelemetryRecord and FieldBoundary SQLAlchemy models.",
                category=TaskCategory.DATABASE,
                priority=TaskPriority.P0,
                estimated_hours=8,
                dependencies=["T01"],
            ),
            TaskItem(
                task_id="T03",
                title="Implement POST /api/v1/telemetry ingestion endpoint",
                description="FastAPI route with Pydantic payload validation and DB insertion.",
                category=TaskCategory.BACKEND,
                priority=TaskPriority.P0,
                estimated_hours=10,
                dependencies=["T02"],
                feature_id="F01",
            ),
            TaskItem(
                task_id="T04",
                title="Implement threshold evaluation service and alert triggers",
                description="Evaluate incoming readings against user configured minimums.",
                category=TaskCategory.BACKEND,
                priority=TaskPriority.P0,
                estimated_hours=8,
                dependencies=["T03"],
                feature_id="F02",
            ),
            TaskItem(
                task_id="T05",
                title="Build React dashboard sensor summary cards",
                description="Display latest telemetry values with status badge indicators.",
                category=TaskCategory.FRONTEND,
                priority=TaskPriority.P1,
                estimated_hours=12,
                dependencies=["T01"],
                feature_id="F03",
            ),
            TaskItem(
                task_id="T06",
                title="Integrate frontend client with telemetry REST API",
                description="Fetch live telemetry data using TanStack Query / Axios.",
                category=TaskCategory.INTEGRATION,
                priority=TaskPriority.P1,
                estimated_hours=8,
                dependencies=["T03", "T05"],
                feature_id="F03",
            ),
            TaskItem(
                task_id="T07",
                title="Write unit and integration tests for telemetry ingestion",
                description="Pytest test suite covering valid payloads and 422 validations.",
                category=TaskCategory.TESTING,
                priority=TaskPriority.P0,
                estimated_hours=8,
                dependencies=["T03", "T04"],
            ),
            TaskItem(
                task_id="T08",
                title="Configure CI/CD automated linting and test workflow",
                description="GitHub Actions pipeline running ruff, mypy, and pytest.",
                category=TaskCategory.DEPLOYMENT,
                priority=TaskPriority.P1,
                estimated_hours=6,
                dependencies=["T07"],
            ),
        ],
    )


def make_milestone_output() -> MilestoneAgentOutput:
    return MilestoneAgentOutput(
        agent_name="milestone_agent",
        summary="3 Stage-gate milestones grouping all tasks.",
        confidence_score=0.93,
        milestones=[
            MilestoneItem(
                milestone_id="M1",
                name="Foundation & Ingestion Pipeline Gate",
                target_week=3,
                deliverables=[
                    "Dockerized backend and database",
                    "Telemetry ingestion REST API operational",
                ],
                associated_task_ids=["T01", "T02", "T03"],
                verification_criteria="Automated test verifies POST /api/v1/telemetry inserts row in PostgreSQL.",
                gate_decision=GateDecision.GATE_1_FOUNDATION,
            ),
            MilestoneItem(
                milestone_id="M2",
                name="Core MVP & Alerting Gate",
                target_week=7,
                deliverables=[
                    "Alert threshold detection working",
                    "Frontend dashboard displaying readings",
                ],
                associated_task_ids=["T04", "T05", "T06"],
                verification_criteria="End-to-end flow demonstrates sensor packet generating UI alert.",
                gate_decision=GateDecision.GATE_2_CORE_MVP,
            ),
            MilestoneItem(
                milestone_id="M3",
                name="Polish, Verification & Handoff Gate",
                target_week=10,
                deliverables=[
                    "100% test pass rate in CI pipeline",
                    "Project README and setup guide finalized",
                ],
                associated_task_ids=["T07", "T08"],
                verification_criteria="CI pipeline runs clean with zero lint or test failures.",
                gate_decision=GateDecision.GATE_3_POLISH_HANDOFF,
            ),
        ],
    )


def make_readme_output() -> ReadmeAgentOutput:
    return ReadmeAgentOutput(
        agent_name="readme_agent",
        summary="Comprehensive developer documentation and onboarding guide.",
        confidence_score=0.96,
        project_title="AgriFlow — Autonomous Telemetry Pipeline",
        project_tagline="Real-time precision agricultural telemetry edge ingestion and alerting.",
        overview="AgriFlow is a modular capstone project delivering high-throughput sensor telemetry ingestion.",
        architecture_overview="Built with FastAPI, PostgreSQL, and React with clean architectural decoupling.",
        tech_stack_summary={
            "Backend": "FastAPI (Python 3.12)",
            "Database": "PostgreSQL 16",
            "Frontend": "React 19 + TypeScript",
        },
        getting_started=[
            "Clone the repository: `git clone https://github.com/example/agriflow.git`",
            "Run local environment: `docker compose up -d`",
            "Execute database migrations: `alembic upgrade head`",
            "Start development server: `uvicorn backend.app.main:app --reload`",
        ],
        environment_variables=[
            EnvVarSpec(
                name="DATABASE_URL",
                required=True,
                default_value="postgresql+asyncpg://user:pass@localhost:5432/agriflow",
                description="PostgreSQL connection string.",
            ),
            EnvVarSpec(
                name="JWT_SECRET",
                required=True,
                default_value=None,
                description="Secret key for signing auth tokens.",
            ),
        ],
        contributing_guidelines="Submit pull requests against the develop branch with full unit test coverage.",
    )


def make_qa_judge_output_pass() -> QAJudgeAgentOutput:
    return QAJudgeAgentOutput(
        agent_name="qa_judge_agent",
        summary="All blueprint sections meet architectural quality standards.",
        confidence_score=0.98,
        status=BlueprintQAStatus.PASS,
        overall_score=88,
        evaluated_criteria={
            "completeness": 90,
            "technical_consistency": 88,
            "scope_containment": 92,
            "student_feasibility": 85,
            "architectural_rigor": 85,
        },
        findings=[
            QAFinding(
                finding_id="QA-F01",
                section="risks",
                target_agent="risk_agent",
                severity=QASeverity.INFO,
                category="DOCUMENTATION",
                description="Consider documenting edge battery degradation during cold weather.",
                recommendation="Add cold weather drone battery note to operational assumptions.",
                requires_regeneration=False,
            )
        ],
        recommendations=[
            "Proceed with implementation of Phase 1 database models.",
            "Verify local Docker Compose before installing edge hardware.",
        ],
        regeneration_target=None,
        requires_human_review=False,
    )


def make_qa_judge_output_fail() -> QAJudgeAgentOutput:
    return QAJudgeAgentOutput(
        agent_name="qa_judge_agent",
        summary="Critical contradiction detected between scope and features.",
        confidence_score=0.95,
        status=BlueprintQAStatus.FAIL,
        overall_score=62,
        evaluated_criteria={
            "completeness": 70,
            "technical_consistency": 55,
            "scope_containment": 50,
            "student_feasibility": 70,
            "architectural_rigor": 65,
        },
        findings=[
            QAFinding(
                finding_id="QA-F01",
                section="features",
                target_agent="features_agent",
                severity=QASeverity.CRITICAL,
                category="SCOPE_VIOLATION",
                description="Feature F04 introduces international currency conversion declared out-of-scope.",
                recommendation="Remove currency conversion and replace with standard in-scope sensor export.",
                requires_regeneration=True,
            )
        ],
        recommendations=["Regenerate features agent to remove out-of-scope capabilities."],
        regeneration_target="features_agent",
        requires_human_review=False,
    )


# ==============================================================================
# 2. Input Factories
# ==============================================================================


def make_idea_input() -> IdeaAgentInput:
    return IdeaAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="idea_agent",
        project_name="AgriFlow Telemetry",
        initial_problem="Farmers cannot track field moisture quickly across large farms.",
        initial_solution="Automated drone telemetry system streaming sensor records to a dashboard.",
        complexity_preference="INTERMEDIATE",
        student_skill_level="INTERMEDIATE",
        assessment_readiness_tier="MODERATE",
        assessment_recommendations=["Focus on modular service design and database indexing."],
    )


def make_scope_input() -> ScopeAgentInput:
    return ScopeAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="scope_agent",
        idea=make_idea_output(),
        assessment_gaps=["Limited distributed systems experience"],
    )


def make_technology_input() -> TechnologyAgentInput:
    return TechnologyAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="technology_agent",
        idea=make_idea_output(),
        scope=make_scope_output(),
        student_skill_level="INTERMEDIATE",
        preferred_technologies=["FastAPI", "PostgreSQL", "React"],
    )


def make_features_input() -> FeaturesAgentInput:
    return FeaturesAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="features_agent",
        idea=make_idea_output(),
        scope=make_scope_output(),
    )


def make_mvp_input() -> MVPAgentInput:
    return MVPAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="mvp_agent",
        idea=make_idea_output(),
        scope=make_scope_output(),
        research_evidence=[],
    )


def make_specification_input() -> SpecificationAgentInput:
    return SpecificationAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="specification_agent",
        idea=make_idea_output(),
        scope=make_scope_output(),
        technology=make_technology_output(),
        features=make_features_output(),
        mvp=make_mvp_output(),
    )


def make_timeline_input() -> TimelineAgentInput:
    return TimelineAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="timeline_agent",
        idea=make_idea_output(),
        specification=make_specification_output(),
        complexity="INTERMEDIATE",
        project_deadline_weeks=10,
    )


def make_risk_input() -> RiskAgentInput:
    return RiskAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="risk_agent",
        technology=make_technology_output(),
        features=make_features_output(),
        specification=make_specification_output(),
        timeline=make_timeline_output(),
    )


def make_task_input() -> TaskAgentInput:
    return TaskAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="task_agent",
        specification=make_specification_output(),
        technology=make_technology_output(),
        features=make_features_output(),
        timeline=make_timeline_output(),
        risks=make_risk_output(),
    )


def make_milestone_input() -> MilestoneAgentInput:
    return MilestoneAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="milestone_agent",
        timeline=make_timeline_output(),
        tasks=make_task_output(),
    )


def make_readme_input() -> ReadmeAgentInput:
    return ReadmeAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="readme_agent",
        curated_context=ReadmeCuratedContext(
            idea=make_idea_output(),
            scope=make_scope_output(),
            technology=make_technology_output(),
            features=make_features_output(),
            mvp=make_mvp_output(),
            timeline=make_timeline_output(),
            risks=make_risk_output(),
            tasks=make_task_output(),
            milestones=make_milestone_output(),
        ),
    )


def make_qa_judge_input() -> QAJudgeAgentInput:
    return QAJudgeAgentInput(
        execution_id=TEST_EXECUTION_ID,
        project_id=TEST_PROJECT_ID,
        student_id=TEST_STUDENT_ID,
        agent_name="qa_judge_agent",
        all_agent_outputs={
            "idea": make_idea_output().model_dump(),
            "scope": make_scope_output().model_dump(),
            "technology": make_technology_output().model_dump(),
            "features": make_features_output().model_dump(),
            "mvp": make_mvp_output().model_dump(),
            "specification": make_specification_output().model_dump(),
            "timeline": make_timeline_output().model_dump(),
            "risks": make_risk_output().model_dump(),
            "tasks": make_task_output().model_dump(),
            "milestones": make_milestone_output().model_dump(),
            "readme": make_readme_output().model_dump(),
        },
        project_context=ProjectBaseContext(
            project_id=TEST_PROJECT_ID,
            student_id=TEST_STUDENT_ID,
            name="AgriFlow Telemetry",
            problem="Farmers cannot track field moisture quickly across large farms.",
            proposed_solution="Automated drone telemetry system streaming sensor records to a dashboard.",
            complexity="INTERMEDIATE",
            current_phase="IDEA",
            health="HEALTHY",
        ),
        assessment_context=AssessmentContext(
            assessment_id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
            project_id=TEST_PROJECT_ID,
            skill_level="INTERMEDIATE",
            project_complexity="INTERMEDIATE",
            alignment="STRONG",
            technical_confidence="HIGH",
            learning_depth="STANDARD",
            overall_score=85,
            readiness_tier="MODERATE",
        ),
    )
