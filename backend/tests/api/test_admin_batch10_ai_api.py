"""
GrowFlow Phase 7 Batch 10 — Tests for Admin AI Observability, Quality, Cost & Key Pool APIs.

Validates:
- AD11: GET /api/v1/admin/ai/observatory
  - 401 Unauthenticated, 403 Forbidden for Student/Mentor, 200 OK for Admin
- AD12: GET /api/v1/admin/ai/usage
  - 401 Unauthenticated, 403 Forbidden for Student/Mentor, 200 OK for Admin
- AD13: GET /api/v1/admin/ai/executions
  - 401 Unauthenticated, 403 Forbidden for Student/Mentor, 200 OK with filters/pagination
- AD14: GET /api/v1/admin/ai/executions/{execution_id}
  - 401 Unauthenticated, 403 Forbidden for Student/Mentor, 200 OK for valid execution, 404 for unknown
- AD15: GET /api/v1/admin/ai/quality
  - 401 Unauthenticated, 403 Forbidden for Student/Mentor, 200 OK for Admin
- AD16: GET /api/v1/admin/ai/cost
  - 401 Unauthenticated, 403 Forbidden for Student/Mentor, 200 OK with unmetered cost posture
- AD17: GET /api/v1/admin/ai/cost/{dimension}
  - 401 Unauthenticated, 403 Forbidden for Student/Mentor, 200 OK for valid dimension, 404 for invalid
- AD18: GET /api/v1/admin/ai/keys
  - 401 Unauthenticated, 403 Forbidden for Student/Mentor, 200 OK with safe masked keys & no secrets
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
import uuid

from fastapi.testclient import TestClient
import pytest

from backend.app.api.dependencies.auth import get_current_user
from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import get_admin_service
from backend.app.api.schemas.admin import (
    AdminAIActiveJobSchema,
    AdminAICapabilityUsageSchema,
    AdminAICostDimensionItemSchema,
    AdminAICostDimensionResponseSchema,
    AdminAICostResponseSchema,
    AdminAIExecutionItemSchema,
    AdminAIExecutionsResponseSchema,
    AdminAIExecutionsSummarySchema,
    AdminAIGatewayPostureSchema,
    AdminAIKeySlotSchema,
    AdminAIKeysResponseSchema,
    AdminAIObservatoryKPISchema,
    AdminAIObservatoryResponseSchema,
    AdminAIProjectUsageSchema,
    AdminAIQualityResponseSchema,
    AdminAIQualityScoreDistributionSchema,
    AdminAIQualityTopIssueSchema,
    AdminAIRecentActivitySchema,
    AdminAITimeBucketSchema,
    AdminAITraceDetailResponseSchema,
    AdminAITraceDomainEventSchema,
    AdminAITracePipelineStageSchema,
    AdminAITraceQAFeedbackSchema,
    AdminAIUsageOverallVolumeSchema,
    AdminAIUsageResponseSchema,
)
from backend.app.application.services.admin_service import AdminService
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.shared.exceptions import NotFoundException


async def _mock_db_session() -> AsyncGenerator[AsyncMock, None]:
    mock_session = AsyncMock()
    yield mock_session


@pytest.fixture(autouse=True)
def override_db(app):
    app.dependency_overrides[get_db_session] = _mock_db_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="admin@growflow.test",
        role=UserRole.ADMIN,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def mentor_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="mentor@growflow.test",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def student_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="student@growflow.test",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )


# ---------------------------------------------------------------------------
# AD11 — AI Observatory Tests
# ---------------------------------------------------------------------------

def test_admin_ai_observatory_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/ai/observatory")
    assert res.status_code == 401


def test_admin_ai_observatory_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/ai/observatory")
    assert res.status_code == 403


def test_admin_ai_observatory_forbidden_mentor(client: TestClient, app, mentor_user):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/ai/observatory")
    assert res.status_code == 403


def test_admin_ai_observatory_success_admin(client: TestClient, app, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = MagicMock(spec=AdminService)
    mock_service.get_ai_observatory = AsyncMock(
        return_value=AdminAIObservatoryResponseSchema(
            gateway=AdminAIGatewayPostureSchema(
                provider="OpenRouter",
                status="OPERATIONAL",
                base_url="https://openrouter.ai/api/v1",
                configured_key_slots=2,
                total_slots=5,
                default_model="openai/gpt-4o",
                fast_model="openai/gpt-4o-mini",
                standard_model="openai/gpt-4o",
                reasoning_model="openai/o1",
                fallback_model="openai/gpt-4o-mini",
                request_timeout_seconds=60,
                max_retries=3,
                credential_note="Safe disclosure",
            ),
            kpis=AdminAIObservatoryKPISchema(
                total_ai_transactions=15,
                blueprint_jobs_total=10,
                blueprint_jobs_completed=8,
                blueprint_jobs_failed=2,
                success_rate_percent=80.0,
                currently_running_jobs=1,
                average_duration_seconds=12.5,
                mentor_messages_total=3,
                change_requests_total=2,
            ),
            active_jobs=[
                AdminAIActiveJobSchema(
                    id="job-1",
                    blueprint_id="bp-1",
                    project_instance_id="proj-1",
                    project_name="Smart Farm",
                    job_type="FULL_GENERATION",
                    status="RUNNING",
                    current_step="tech_stack",
                    progress_percent=20,
                    started_at=datetime.now(UTC),
                    created_at=datetime.now(UTC),
                )
            ],
            recent_activity=[],
        )
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/ai/observatory")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["gateway"]["provider"] == "OpenRouter"
    assert data["gateway"]["configured_key_slots"] == 2
    assert data["kpis"]["total_ai_transactions"] == 15
    assert data["kpis"]["success_rate_percent"] == 80.0
    assert len(data["active_jobs"]) == 1
    assert data["notices"]["token_metering"] == "UNMETERED / NOT PERSISTED"


# ---------------------------------------------------------------------------
# AD12 — AI Usage Tests
# ---------------------------------------------------------------------------

def test_admin_ai_usage_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/ai/usage")
    assert res.status_code == 401


def test_admin_ai_usage_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/ai/usage")
    assert res.status_code == 403


def test_admin_ai_usage_success_admin(client: TestClient, app, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = MagicMock(spec=AdminService)
    mock_service.get_ai_usage = AsyncMock(
        return_value=AdminAIUsageResponseSchema(
            overall_volume=AdminAIUsageOverallVolumeSchema(
                blueprint_synthesis_jobs=10,
                ai_mentor_messages=4,
                project_change_analyses=2,
                total_recorded_transactions=16,
            ),
            time_trend=[
                AdminAITimeBucketSchema(
                    date="2026-03-01",
                    blueprint_jobs_count=5,
                    mentor_messages_count=2,
                    total_count=7,
                )
            ],
            capability_breakdown=[
                AdminAICapabilityUsageSchema(
                    capability_key="BLUEPRINT_GEN",
                    label="Blueprint Master Synthesis",
                    count=8,
                    percentage=50.0,
                )
            ],
            project_distribution=[
                AdminAIProjectUsageSchema(
                    project_id="proj-1",
                    project_name="Precision Irrigation",
                    synthesis_jobs_count=5,
                    mentor_messages_count=2,
                    total_transactions=7,
                )
            ],
            outcome_distribution={"COMPLETED": 8, "FAILED": 2},
            token_metering="UNMETERED / NOT PERSISTED",
            rate_limit_telemetry="NOT PERSISTED",
        )
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/ai/usage")
    assert res.status_code == 200
    body = res.json()
    data = body["data"]
    assert data["overall_volume"]["total_recorded_transactions"] == 16
    assert data["token_metering"] == "UNMETERED / NOT PERSISTED"
    assert data["rate_limit_telemetry"] == "NOT PERSISTED"
    assert len(data["capability_breakdown"]) == 1


# ---------------------------------------------------------------------------
# AD13 — AI Executions Tests
# ---------------------------------------------------------------------------

def test_admin_ai_executions_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/ai/executions")
    assert res.status_code == 401


def test_admin_ai_executions_forbidden_mentor(client: TestClient, app, mentor_user):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/ai/executions")
    assert res.status_code == 403


def test_admin_ai_executions_success_admin(client: TestClient, app, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = MagicMock(spec=AdminService)
    mock_service.list_ai_executions = AsyncMock(
        return_value=AdminAIExecutionsResponseSchema(
            total=1,
            limit=25,
            offset=0,
            summary=AdminAIExecutionsSummarySchema(
                total=1, completed=1, failed=0, running=0, pending=0
            ),
            executions=[
                AdminAIExecutionItemSchema(
                    id="exec-1",
                    source="blueprint_jobs",
                    project_instance_id="proj-1",
                    project_name="AgriTech Hub",
                    capability="Blueprint Engine",
                    job_type="FULL_GENERATION",
                    target_output=None,
                    status="COMPLETED",
                    current_step="readme",
                    progress_percent=100,
                    duration_seconds=15,
                    error=None,
                    started_at=datetime.now(UTC),
                    completed_at=datetime.now(UTC),
                    created_at=datetime.now(UTC),
                )
            ],
        )
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/ai/executions?status=COMPLETED&limit=25")
    assert res.status_code == 200
    body = res.json()
    data = body["data"]
    assert data["total"] == 1
    assert len(data["executions"]) == 1
    assert data["executions"][0]["status"] == "COMPLETED"
    assert data["executions"][0]["capability"] == "Blueprint Engine"


# ---------------------------------------------------------------------------
# AD14 — AI Trace Detail Tests
# ---------------------------------------------------------------------------

def test_admin_ai_trace_detail_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/ai/executions/job-1")
    assert res.status_code == 401


def test_admin_ai_trace_detail_not_found(client: TestClient, app, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = MagicMock(spec=AdminService)
    mock_service.get_ai_trace_detail = AsyncMock(
        side_effect=NotFoundException("AI Execution 'unknown-id' not found.", code="EXECUTION_NOT_FOUND")
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/ai/executions/unknown-id")
    assert res.status_code == 404
    body = res.json()
    assert body["error"]["code"] == "EXECUTION_NOT_FOUND"


def test_admin_ai_trace_detail_success_admin(client: TestClient, app, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = MagicMock(spec=AdminService)
    mock_service.get_ai_trace_detail = AsyncMock(
        return_value=AdminAITraceDetailResponseSchema(
            id="job-1",
            blueprint_id="bp-1",
            project_instance_id="proj-1",
            project_name="Crop Health AI",
            student_id="usr-stud-1",
            job_type="FULL_GENERATION",
            target_output=None,
            status="COMPLETED",
            current_step="readme",
            progress_percent=100,
            duration_seconds=14,
            sanitized_error=None,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
            pipeline_stages=[
                AdminAITracePipelineStageSchema(
                    stage_order=1,
                    section_key="project_profile",
                    title="Project Profile & Domain Context",
                    status="COMPLETED",
                    progress_milestone=10,
                )
            ],
            qa_result=AdminAITraceQAFeedbackSchema(
                qa_status="PASS",
                qa_score=88,
                summary="QA passed with high fidelity",
                evaluated_criteria={"completeness": 95, "architectural_coherence": 90},
                issues=[],
                recommendations=["Proceed with deployment"],
            ),
            domain_events=[
                AdminAITraceDomainEventSchema(
                    id="ev-1",
                    event_type="BlueprintGenerated",
                    status="PUBLISHED",
                    correlation_id="corr-1",
                    occurred_at=datetime.now(UTC),
                )
            ],
        )
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/ai/executions/job-1")
    assert res.status_code == 200
    body = res.json()
    data = body["data"]
    assert data["id"] == "job-1"
    assert data["status"] == "COMPLETED"
    assert len(data["pipeline_stages"]) == 1
    assert data["qa_result"]["qa_score"] == 88
    assert data["telemetry_notices"]["http_wire_packets"] == "UNAVAILABLE"


# ---------------------------------------------------------------------------
# AD15 — AI Quality Tests
# ---------------------------------------------------------------------------

def test_admin_ai_quality_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/ai/quality")
    assert res.status_code == 401


def test_admin_ai_quality_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/ai/quality")
    assert res.status_code == 403


def test_admin_ai_quality_success_admin(client: TestClient, app, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = MagicMock(spec=AdminService)
    mock_service.get_ai_quality = AsyncMock(
        return_value=AdminAIQualityResponseSchema(
            total_evaluated=12,
            passed_count=10,
            failed_count=2,
            pending_count=0,
            pass_rate_percent=83.3,
            average_qa_score=85.4,
            min_qa_score=40,
            max_qa_score=96,
            score_distribution=AdminAIQualityScoreDistributionSchema(
                range_0_49=1,
                range_50_69=1,
                range_70_84=4,
                range_85_100=6,
            ),
            criteria_averages={
                "completeness": 91.2,
                "architectural_coherence": 87.0,
                "risk_mitigation": 82.5,
            },
            top_issues=[
                AdminAIQualityTopIssueSchema(
                    section="risks",
                    severity="LOW",
                    count=3,
                    sample_description="Telemetry backoff jitter parameter missing",
                    recommendation="Add exponential backoff",
                )
            ],
            approval_conversion_rate=90.0,
        )
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/ai/quality")
    assert res.status_code == 200
    body = res.json()
    data = body["data"]
    assert data["total_evaluated"] == 12
    assert data["passed_count"] == 10
    assert data["pass_rate_percent"] == 83.3
    assert data["average_qa_score"] == 85.4
    assert data["deferred_capabilities"]["rag_faithfulness_evaluation"] == "DEFERRED"


# ---------------------------------------------------------------------------
# AD16 — AI Cost & Usage Tests
# ---------------------------------------------------------------------------

def test_admin_ai_cost_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/ai/cost")
    assert res.status_code == 401


def test_admin_ai_cost_forbidden_mentor(client: TestClient, app, mentor_user):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/ai/cost")
    assert res.status_code == 403


def test_admin_ai_cost_success_admin(client: TestClient, app, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = MagicMock(spec=AdminService)
    mock_service.get_ai_cost = AsyncMock(
        return_value=AdminAICostResponseSchema(
            execution_volume_total=24,
            blueprint_jobs_count=16,
            ai_mentor_messages_count=6,
            change_analyses_count=2,
            active_models=["openai/gpt-4o", "openai/gpt-4o-mini"],
            provider="OpenRouter",
            billing_model="DIRECT_PROVIDER_BILLED — OPENROUTER",
            cost_telemetry_state="UNMETERED / NOT PERSISTED",
            token_metering_state="UNMETERED / NOT PERSISTED",
        )
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/ai/cost")
    assert res.status_code == 200
    body = res.json()
    data = body["data"]
    assert data["execution_volume_total"] == 24
    assert data["cost_telemetry_state"] == "UNMETERED / NOT PERSISTED"
    assert data["token_metering_state"] == "UNMETERED / NOT PERSISTED"
    assert "OPENROUTER" in data["billing_model"]
    # Verify no fabricated dollar costs
    assert "dollars" not in data
    assert "cost_usd" not in data


# ---------------------------------------------------------------------------
# AD17 — Cost Breakdown Tests
# ---------------------------------------------------------------------------

def test_admin_ai_cost_dimension_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/ai/cost/agent")
    assert res.status_code == 401


def test_admin_ai_cost_dimension_invalid_404(client: TestClient, app, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = MagicMock(spec=AdminService)
    mock_service.get_ai_cost_dimension = AsyncMock(
        side_effect=NotFoundException("Cost breakdown dimension 'invalid_dim' not found.", code="DIMENSION_NOT_FOUND")
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/ai/cost/invalid_dim")
    assert res.status_code == 404
    body = res.json()
    assert body["error"]["code"] == "DIMENSION_NOT_FOUND"


def test_admin_ai_cost_dimension_success_agent(client: TestClient, app, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = MagicMock(spec=AdminService)
    mock_service.get_ai_cost_dimension = AsyncMock(
        return_value=AdminAICostDimensionResponseSchema(
            dimension="agent",
            title="Execution Volume by AI Capability / Agent",
            metric_type="EXECUTION_VOLUME",
            total_volume=20,
            items=[
                AdminAICostDimensionItemSchema(
                    key="blueprint_generation",
                    label="Blueprint Master Generation",
                    execution_count=14,
                    percentage=70.0,
                    detail="10-output synthesis",
                ),
                AdminAICostDimensionItemSchema(
                    key="ai_mentor",
                    label="AI Mentor Supervisory Assistant",
                    execution_count=6,
                    percentage=30.0,
                    detail="Advisory chat",
                ),
            ],
        )
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/ai/cost/agent")
    assert res.status_code == 200
    body = res.json()
    data = body["data"]
    assert data["dimension"] == "agent"
    assert data["metric_type"] == "EXECUTION_VOLUME"
    assert len(data["items"]) == 2


# ---------------------------------------------------------------------------
# AD18 — API Key Pool Monitoring Tests & Security Assertions
# ---------------------------------------------------------------------------

def test_admin_ai_keys_unauthenticated(client: TestClient):
    res = client.get("/api/v1/admin/ai/keys")
    assert res.status_code == 401


def test_admin_ai_keys_forbidden_student(client: TestClient, app, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/ai/keys")
    assert res.status_code == 403


def test_admin_ai_keys_success_admin_and_security_check(client: TestClient, app, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = MagicMock(spec=AdminService)
    mock_service.get_ai_keys = AsyncMock(
        return_value=AdminAIKeysResponseSchema(
            provider="OpenRouter",
            gateway_base_url="https://openrouter.ai/api/v1",
            total_slots=5,
            configured_key_count=2,
            rotation_mechanism="In-Memory Round-Robin",
            rotation_runtime_state="RUNTIME_IN_MEMORY",
            slots=[
                AdminAIKeySlotSchema(
                    slot_index=1,
                    slot_label="OpenRouter Key Slot 1",
                    env_var_name="OPENROUTER_API_KEY_1",
                    status="CONFIGURED",
                    provider="OpenRouter",
                    masked_identifier="sk-or-••••••••••••••••3a8f",
                    rotation_posture="ACTIVE_IN_ROTATION",
                ),
                AdminAIKeySlotSchema(
                    slot_index=2,
                    slot_label="OpenRouter Key Slot 2",
                    env_var_name="OPENROUTER_API_KEY_2",
                    status="CONFIGURED",
                    provider="OpenRouter",
                    masked_identifier="sk-or-••••••••••••••••7b2e",
                    rotation_posture="ACTIVE_IN_ROTATION",
                ),
                AdminAIKeySlotSchema(
                    slot_index=3,
                    slot_label="OpenRouter Key Slot 3",
                    env_var_name="OPENROUTER_API_KEY_3",
                    status="NOT_CONFIGURED",
                    provider="OpenRouter",
                    masked_identifier=None,
                    rotation_posture="UNCONFIGURED",
                ),
                AdminAIKeySlotSchema(
                    slot_index=4,
                    slot_label="OpenRouter Key Slot 4",
                    env_var_name="OPENROUTER_API_KEY_4",
                    status="NOT_CONFIGURED",
                    provider="OpenRouter",
                    masked_identifier=None,
                    rotation_posture="UNCONFIGURED",
                ),
                AdminAIKeySlotSchema(
                    slot_index=5,
                    slot_label="OpenRouter Key Slot 5",
                    env_var_name="OPENROUTER_API_KEY_5",
                    status="NOT_CONFIGURED",
                    provider="OpenRouter",
                    masked_identifier=None,
                    rotation_posture="UNCONFIGURED",
                ),
            ],
        )
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/ai/keys")
    assert res.status_code == 200
    body = res.json()
    data = body["data"]
    assert data["provider"] == "OpenRouter"
    assert data["configured_key_count"] == 2
    assert len(data["slots"]) == 5

    # CRITICAL SECURITY ASSERTION:
    # Ensure no raw secret or unmasked key material is present in response
    raw_response_text = res.text
    assert "Bearer" not in raw_response_text
    for slot in data["slots"]:
        if slot["masked_identifier"]:
            assert "••••••••" in slot["masked_identifier"]
            assert len(slot["masked_identifier"]) < 35
