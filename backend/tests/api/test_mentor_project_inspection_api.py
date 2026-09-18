"""
GrowFlow Phase 7 Batch 4 — Tests for Mentor Project Instance Deep Inspection (M24–M30).

Validates:
- Authorization Boundary:
  - Unauthenticated access returns 401
  - Student caller receives 403 across all inspection endpoints
  - Missing project returns 404
  - Non-supervising Mentor receives 403
- Deep Inspection Surfaces:
  - M24: GET /api/v1/mentors/project-instances/{project_id}/blueprint (Read-only, pinned version)
  - M25: GET /api/v1/mentors/project-instances/{project_id}/tasks (Read-only, canonical status/priority)
  - M26: GET /api/v1/mentors/project-instances/{project_id}/milestones (Read-only, gates & progress)
  - M27: GET /api/v1/mentors/project-instances/{project_id}/risks (Read-only, severity & mitigations)
  - M28: GET /api/v1/mentors/project-instances/{project_id}/documents (Read-only, specification catalog)
  - M29: GET /api/v1/mentors/project-instances/{project_id}/github (Read-only observational, no secrets)
  - M30: GET /api/v1/mentors/project-instances/{project_id}/activity (Read-only, canonical domain events)
- Mutation Invariant:
  - Mentor cannot mutate blueprint, tasks, milestones, risks, documents, or github
- Mandatory Cross-Mentor Security Isolation Matrix:
  - Mentor A supervising Project A: 200 OK
  - Mentor A attempting to inspect Project B: 403 Forbidden
  - Mentor B supervising Project B: 200 OK
  - Mentor B attempting to inspect Project A: 403 Forbidden
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
from backend.app.api.dependencies.services import (
    get_activity_service,
    get_blueprint_service,
    get_execution_service,
    get_github_service,
    get_project_service,
)
from backend.app.api.schemas.execution import (
    DocumentResponse,
    MilestoneResponse,
    RiskResponse,
    TaskResponse,
)
from backend.app.api.schemas.mentor_supervision import (
    MentorProjectInstanceDetailSchema,
)
from backend.app.application.services.activity_service import ActivityService
from backend.app.application.services.blueprint_service import BlueprintService
from backend.app.application.services.execution_service import ExecutionService
from backend.app.application.services.github_service import GitHubService
from backend.app.application.services.project_service import ProjectService
from backend.app.domain.blueprint.models import (
    BlueprintQAFeedback,
    BlueprintQAStatus,
    BlueprintSession,
    BlueprintStatus,
)
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.shared.exceptions import AuthorizationException, NotFoundException


async def _mock_db_session() -> AsyncGenerator[AsyncMock, None]:
    mock_session = AsyncMock()
    yield mock_session


@pytest.fixture(autouse=True)
def override_db(app):
    app.dependency_overrides[get_db_session] = _mock_db_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mentor_user_a() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        email="mentor_a@growflow.test",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def mentor_user_b() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        email="mentor_b@growflow.test",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def student_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        email="student@growflow.test",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def project_a_id() -> uuid.UUID:
    return uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


@pytest.fixture
def project_b_id() -> uuid.UUID:
    return uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _sample_project_detail(project_id: uuid.UUID, name: str = "Project A") -> MentorProjectInstanceDetailSchema:
    return MentorProjectInstanceDetailSchema(
        id=str(project_id),
        name=name,
        problem="Agricultural moisture monitoring problem",
        proposed_solution="IoT sensor network with mesh telemetry",
        complexity="INTERMEDIATE",
        current_phase="DEVELOPMENT",
        health="HEALTHY",
        progress_percentage=45,
        status="ACTIVE",
        deadline=None,
        started_at=datetime.now(UTC),
        completed_at=None,
        student_id=str(uuid.uuid4()),
        student_name="Student User",
        student_email="student@growflow.test",
        group_id=str(uuid.uuid4()),
        group_name="Agritech Cohort",
        source_definition_id=str(uuid.uuid4()),
        source_definition_name="Smart Soil Telemetry Spec",
        source_definition_version_number=3,
        objective="Deploy autonomous moisture sensing",
        scope="Sensors, solar harvest, LoRa telemetry",
        expected_outcome="Functional field deployment",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _sample_blueprint_session(project_id: uuid.UUID) -> BlueprintSession:
    return BlueprintSession(
        id=uuid.uuid4(),
        project_instance_id=project_id,
        student_id=uuid.uuid4(),
        status=BlueprintStatus.APPROVED,
        current_step="completed",
        progress_percent=100,
        qa_status=BlueprintQAStatus.PASS,
        qa_score=94,
        qa_feedback=BlueprintQAFeedback(
            status=BlueprintQAStatus.PASS,
            score=94,
            summary="High quality architecture specification.",
            evaluated_criteria={"feasibility": 95, "completeness": 93},
            issues=[],
            recommendations=["Consider adding battery backup details."],
        ),
        content={
            "project_profile": {"title": "Smart Soil Telemetry", "summary": "Sensors and edge analytics."},
            "tech_stack": {"primary_language": "Python", "frameworks": ["FastAPI", "React"]},
            "features": {"core": ["Moisture reading", "Alert triggers"]},
            "specifications": {"architecture": "Microservices with MQTT gateway"},
            "mvp": {"scope": "Single probe reporting every 10 minutes"},
            "duration": {"estimate_weeks": 8},
            "risks": {"primary": "Moisture ingress in probe casing"},
            "tasks": {"tasks_breakdown": [{"id": "T01", "name": "Firmware initialisation", "priority": "HIGH"}]},
            "milestones": {"milestones_schedule": [{"gate": "M1", "name": "Prototype validation"}]},
            "readme": {"markdown": "# Smart Soil Telemetry\nReadme contents"},
        },
    )


# ============================================================================
# AUTHORIZATION TESTS
# ============================================================================

@pytest.mark.parametrize(
    "subpath",
    [
        "blueprint",
        "tasks",
        "milestones",
        "risks",
        "documents",
        "github",
        "activity",
    ],
)
def test_inspection_endpoints_unauthenticated_return_401(client: TestClient, project_a_id: uuid.UUID, subpath: str):
    """Inspection endpoints must reject unauthenticated requests with HTTP 401."""
    response = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/{subpath}")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "subpath",
    [
        "blueprint",
        "tasks",
        "milestones",
        "risks",
        "documents",
        "github",
        "activity",
    ],
)
def test_inspection_endpoints_student_caller_returns_403(
    client: TestClient, app, student_user: CurrentUser, project_a_id: uuid.UUID, subpath: str
):
    """Students accessing Mentor inspection endpoints must receive HTTP 403."""
    app.dependency_overrides[get_current_user] = lambda: student_user
    response = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/{subpath}")
    assert response.status_code == 403


def test_inspection_endpoint_missing_project_returns_404(
    client: TestClient, app, mentor_user_a: CurrentUser, project_a_id: uuid.UUID
):
    """Missing project returns 404 NotFoundException."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.assert_mentor_supervises_project.side_effect = NotFoundException(
        "Project not found.", code="PROJECT_NOT_FOUND"
    )
    mock_proj_service.get_supervised_project_detail.side_effect = NotFoundException(
        "Project not found.", code="PROJECT_NOT_FOUND"
    )
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    response = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/blueprint")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PROJECT_NOT_FOUND"


def test_inspection_endpoint_non_supervising_mentor_returns_403(
    client: TestClient, app, mentor_user_a: CurrentUser, project_b_id: uuid.UUID
):
    """Mentor outside supervision scope receives 403 Forbidden."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.get_supervised_project_detail.side_effect = AuthorizationException(
        "You do not supervise this project instance.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    mock_proj_service.assert_mentor_supervises_project.side_effect = AuthorizationException(
        "You do not supervise this project instance.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    response = client.get(f"/api/v1/mentors/project-instances/{project_b_id}/blueprint")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


# ============================================================================
# M24: BLUEPRINT DEEP INSPECTION
# ============================================================================

def test_m24_get_supervised_blueprint_success(
    client: TestClient, app, mentor_user_a: CurrentUser, project_a_id: uuid.UUID
):
    """M24: Authorized mentor reads canonical blueprint status, content, and pinned definition version."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    proj_detail = _sample_project_detail(project_a_id)
    bp_session = _sample_blueprint_session(project_a_id)

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.get_supervised_project_detail.return_value = proj_detail
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    mock_bp_service = AsyncMock(spec=BlueprintService)
    mock_bp_service.get_status.return_value = bp_session
    mock_bp_service.get_content.return_value = bp_session.content
    app.dependency_overrides[get_blueprint_service] = lambda: mock_bp_service

    response = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/blueprint")
    assert response.status_code == 200
    data = response.json()["data"]

    # Verify project context and pinned definition version
    assert data["project"]["id"] == str(project_a_id)
    assert data["project"]["source_definition_version_number"] == 3
    assert data["project"]["source_definition_name"] == "Smart Soil Telemetry Spec"

    # Verify blueprint canonical session & QA score
    assert data["blueprint"]["status"] == "APPROVED"
    assert data["blueprint"]["qa_score"] == 94
    assert data["blueprint"]["qa_feedback"]["summary"] == "High quality architecture specification."

    # Verify structured content sections
    assert "project_profile" in data["content"]
    assert "tech_stack" in data["content"]
    assert data["content"]["tech_stack"]["primary_language"] == "Python"


def test_m24_mentor_cannot_mutate_blueprint(
    client: TestClient, app, mentor_user_a: CurrentUser, project_a_id: uuid.UUID
):
    """M24: Mentor attempting to trigger blueprint approval or generation is denied."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    # Student mutation endpoint blocks mentor
    response_approve = client.post(f"/api/v1/projects/{project_a_id}/blueprint/approve")
    assert response_approve.status_code == 403


# ============================================================================
# M25: TASKS DEEP INSPECTION
# ============================================================================

def test_m25_get_supervised_tasks_success(
    client: TestClient, app, mentor_user_a: CurrentUser, project_a_id: uuid.UUID
):
    """M25: Authorized mentor inspects project tasks with canonical status and priority."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.assert_mentor_supervises_project.return_value = None
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    task1 = TaskResponse(
        id=str(uuid.uuid4()),
        project_instance_id=str(project_a_id),
        milestone_id=str(uuid.uuid4()),
        task_code="T01",
        title="Implement LoRa Transceiver Driver",
        description="Write SPI driver for SX1262 LoRa module.",
        status="IN_PROGRESS",
        priority="HIGH",
        category="EMBEDDED",
        phase="DEVELOPMENT",
        due_date=None,
        dependencies=[],
        acceptance_criteria=["Packet sent with SNR > 6dB"],
        completed_at=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_exec_service = AsyncMock(spec=ExecutionService)
    mock_exec_service.list_tasks.return_value = [task1]
    app.dependency_overrides[get_execution_service] = lambda: mock_exec_service

    response = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/tasks")
    assert response.status_code == 200
    tasks = response.json()["data"]
    assert len(tasks) == 1
    assert tasks[0]["task_code"] == "T01"
    assert tasks[0]["status"] == "IN_PROGRESS"
    assert tasks[0]["priority"] == "HIGH"


# ============================================================================
# M26: MILESTONES DEEP INSPECTION
# ============================================================================

def test_m26_get_supervised_milestones_success(
    client: TestClient, app, mentor_user_a: CurrentUser, project_a_id: uuid.UUID
):
    """M26: Authorized mentor inspects project milestones with progress indicators."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.assert_mentor_supervises_project.return_value = None
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    m1 = MilestoneResponse(
        id=str(uuid.uuid4()),
        project_instance_id=str(project_a_id),
        title="Hardware Demonstration Gate",
        description="Field test moisture probe accuracy.",
        gate_code="M01",
        target_date=None,
        status="IN_PROGRESS",
        progress_percent=60,
        deliverables=["Field sensor test report"],
        section_order=1,
        task_count=5,
        completed_task_count=3,
        tasks=[],
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_exec_service = AsyncMock(spec=ExecutionService)
    mock_exec_service.list_milestones.return_value = [m1]
    app.dependency_overrides[get_execution_service] = lambda: mock_exec_service

    response = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/milestones")
    assert response.status_code == 200
    milestones = response.json()["data"]
    assert len(milestones) == 1
    assert milestones[0]["gate_code"] == "M01"
    assert milestones[0]["progress_percent"] == 60


# ============================================================================
# M27: RISKS DEEP INSPECTION
# ============================================================================

def test_m27_get_supervised_risks_success(
    client: TestClient, app, mentor_user_a: CurrentUser, project_a_id: uuid.UUID
):
    """M27: Authorized mentor inspects project risks with canonical severity and mitigations."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.assert_mentor_supervises_project.return_value = None
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    r1 = RiskResponse(
        id=str(uuid.uuid4()),
        project_instance_id=str(project_a_id),
        risk_code="R01",
        title="Battery drain in sub-zero ambient temperatures",
        description="LiPo battery chemistry degrades below -5C.",
        severity="HIGH",
        probability="MEDIUM",
        impact="HIGH",
        status="OPEN",
        mitigation="Incorporate thermal insulation and duty-cycle throttle.",
        owner="Alex Rivera",
        review_date=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_exec_service = AsyncMock(spec=ExecutionService)
    mock_exec_service.list_risks.return_value = [r1]
    app.dependency_overrides[get_execution_service] = lambda: mock_exec_service

    response = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/risks")
    assert response.status_code == 200
    risks = response.json()["data"]
    assert len(risks) == 1
    assert risks[0]["risk_code"] == "R01"
    assert risks[0]["severity"] == "HIGH"
    assert "thermal insulation" in risks[0]["mitigation"]


# ============================================================================
# M28: DOCUMENTS DEEP INSPECTION
# ============================================================================

def test_m28_get_supervised_documents_success(
    client: TestClient, app, mentor_user_a: CurrentUser, project_a_id: uuid.UUID
):
    """M28: Authorized mentor inspects project document catalog and content."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.assert_mentor_supervises_project.return_value = None
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    doc1 = DocumentResponse(
        id=str(uuid.uuid4()),
        project_instance_id=str(project_a_id),
        document_key="system_architecture_spec",
        title="System Architecture Specification",
        doc_type="SPECIFICATION",
        format="markdown",
        content="# Architecture Specification\nEdge mesh topology with cellular uplink gateway.",
        version="1.0",
        status="ACTIVE",
        source="BLUEPRINT_INIT",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_exec_service = AsyncMock(spec=ExecutionService)
    mock_exec_service.list_documents.return_value = [doc1]
    app.dependency_overrides[get_execution_service] = lambda: mock_exec_service

    response = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/documents")
    assert response.status_code == 200
    docs = response.json()["data"]
    assert len(docs) == 1
    assert docs[0]["title"] == "System Architecture Specification"
    assert docs[0]["doc_type"] == "SPECIFICATION"


# ============================================================================
# M29: GITHUB OBSERVATIONAL INSPECTION
# ============================================================================

def test_m29_get_supervised_github_success(
    client: TestClient, app, mentor_user_a: CurrentUser, project_a_id: uuid.UUID
):
    """M29: Authorized mentor inspects observational GitHub state; zero secrets returned."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.assert_mentor_supervises_project.return_value = None
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    gh_data = {
        "id": str(uuid.uuid4()),
        "project_instance_id": str(project_a_id),
        "repository_name": "smart-soil-telemetry",
        "repository_url": "https://github.com/growflow-students/smart-soil-telemetry",
        "connection_status": "CONNECTED",
        "default_branch": "main",
        "commit_count": 14,
        "last_sync_at": datetime.now(UTC).isoformat(),
        "sync_error": None,
        "cached_commits_preview": [
            {
                "sha": "a1b2c3d4",
                "message": "feat: add sensor calibration routine",
                "author": "alex_rivera",
                "date": datetime.now(UTC).isoformat(),
            }
        ],
    }

    mock_gh_service = AsyncMock(spec=GitHubService)
    mock_gh_service.get_integration.return_value = gh_data
    app.dependency_overrides[get_github_service] = lambda: mock_gh_service

    response = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/github")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["repository_name"] == "smart-soil-telemetry"
    assert data["connection_status"] == "CONNECTED"
    assert data["commit_count"] == 14
    # Ensure no secrets or tokens exist in response
    assert "token" not in data
    assert "secret" not in data
    assert "access_token" not in data


# ============================================================================
# M30: ACTIVITY AUDIT TRAIL INSPECTION
# ============================================================================

def test_m30_get_supervised_activity_success(
    client: TestClient, app, mentor_user_a: CurrentUser, project_a_id: uuid.UUID
):
    """M30: Authorized mentor inspects project activity derived from canonical domain events."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.assert_mentor_supervises_project.return_value = None
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    activity_data = [
        {
            "id": str(uuid.uuid4()),
            "event_type": "TaskCompleted",
            "title": "Task Completed",
            "description": "Task 'Implement LoRa Transceiver Driver' marked completed.",
            "actor_role": "STUDENT",
            "actor_id": str(uuid.uuid4()),
            "resource_type": "project_task",
            "resource_id": str(uuid.uuid4()),
            "occurred_at": datetime.now(UTC).isoformat(),
            "metadata": {"task_code": "T01", "title": "Implement LoRa Transceiver Driver"},
        },
        {
            "id": str(uuid.uuid4()),
            "event_type": "BlueprintApproved",
            "title": "Blueprint Approved",
            "description": "Architecture blueprint reviewed, evaluated, and approved.",
            "actor_role": "STUDENT",
            "actor_id": str(uuid.uuid4()),
            "resource_type": "blueprint",
            "resource_id": str(uuid.uuid4()),
            "occurred_at": datetime.now(UTC).isoformat(),
            "metadata": {"qa_score": 94},
        },
    ]

    mock_act_service = AsyncMock(spec=ActivityService)
    mock_act_service.get_project_activity.return_value = activity_data
    app.dependency_overrides[get_activity_service] = lambda: mock_act_service

    response = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/activity")
    assert response.status_code == 200
    events = response.json()["data"]
    assert len(events) == 2
    assert events[0]["event_type"] == "TaskCompleted"
    assert events[1]["event_type"] == "BlueprintApproved"


# ============================================================================
# MANDATORY CROSS-MENTOR SECURITY ISOLATION MATRIX (M24–M30)
# ============================================================================

@pytest.mark.parametrize(
    "subpath",
    [
        "blueprint",
        "tasks",
        "milestones",
        "risks",
        "documents",
        "github",
        "activity",
    ],
)
def test_mandatory_cross_mentor_isolation_matrix(
    client: TestClient,
    app,
    mentor_user_a: CurrentUser,
    mentor_user_b: CurrentUser,
    project_a_id: uuid.UUID,
    project_b_id: uuid.UUID,
    subpath: str,
):
    """
    Mandatory Cross-Mentor Isolation Matrix across M24–M30:
    Mentor A -> Project A: 200 OK
    Mentor A -> Project B: 403 Forbidden
    Mentor B -> Project B: 200 OK
    Mentor B -> Project A: 403 Forbidden
    """
    mock_proj_service = AsyncMock(spec=ProjectService)

    async def _mock_assert_supervision(*args, **kwargs):
        proj_id = kwargs.get("project_id", args[0] if args else None)
        mentor_id = kwargs.get("mentor_id", args[1] if len(args) > 1 else None)
        # Mentor A supervises Project A, Mentor B supervises Project B
        if str(mentor_id) == str(mentor_user_a.user_id) and str(proj_id) == str(project_a_id):
            return None
        if str(mentor_id) == str(mentor_user_b.user_id) and str(proj_id) == str(project_b_id):
            return None
        raise AuthorizationException(
            "You do not supervise this project instance.", code="AUTH_FORBIDDEN_RESOURCE"
        )

    async def _mock_get_detail(*args, **kwargs):
        proj_id = kwargs.get("project_id", args[0] if args else None)
        mentor_id = kwargs.get("mentor_id", args[1] if len(args) > 1 else None)
        if str(mentor_id) == str(mentor_user_a.user_id) and str(proj_id) == str(project_a_id):
            return _sample_project_detail(project_a_id, "Project A")
        if str(mentor_id) == str(mentor_user_b.user_id) and str(proj_id) == str(project_b_id):
            return _sample_project_detail(project_b_id, "Project B")
        raise AuthorizationException(
            "You do not supervise this project instance.", code="AUTH_FORBIDDEN_RESOURCE"
        )

    mock_proj_service.assert_mentor_supervises_project.side_effect = _mock_assert_supervision
    mock_proj_service.get_supervised_project_detail.side_effect = _mock_get_detail
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    # Setup mocks for all inspection services
    mock_bp_service = AsyncMock(spec=BlueprintService)
    mock_bp_service.get_status.return_value = _sample_blueprint_session(project_a_id)
    mock_bp_service.get_content.return_value = {}
    app.dependency_overrides[get_blueprint_service] = lambda: mock_bp_service

    mock_exec_service = AsyncMock(spec=ExecutionService)
    mock_exec_service.list_tasks.return_value = []
    mock_exec_service.list_milestones.return_value = []
    mock_exec_service.list_risks.return_value = []
    mock_exec_service.list_documents.return_value = []
    app.dependency_overrides[get_execution_service] = lambda: mock_exec_service

    mock_gh_service = AsyncMock(spec=GitHubService)
    mock_gh_service.get_integration.return_value = {"repository_name": "repo"}
    app.dependency_overrides[get_github_service] = lambda: mock_gh_service

    mock_act_service = AsyncMock(spec=ActivityService)
    mock_act_service.get_project_activity.return_value = []
    app.dependency_overrides[get_activity_service] = lambda: mock_act_service

    # 1. Mentor A inspecting Project A -> ALLOWED (200)
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a
    res_a_a = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/{subpath}")
    assert res_a_a.status_code == 200, f"Mentor A accessing Project A on {subpath} must be 200"

    # 2. Mentor A inspecting Project B -> FORBIDDEN (403)
    res_a_b = client.get(f"/api/v1/mentors/project-instances/{project_b_id}/{subpath}")
    assert res_a_b.status_code == 403, f"Mentor A accessing Project B on {subpath} must be 403"

    # 3. Mentor B inspecting Project B -> ALLOWED (200)
    app.dependency_overrides[get_current_user] = lambda: mentor_user_b
    res_b_b = client.get(f"/api/v1/mentors/project-instances/{project_b_id}/{subpath}")
    assert res_b_b.status_code == 200, f"Mentor B accessing Project B on {subpath} must be 200"

    # 4. Mentor B inspecting Project A -> FORBIDDEN (403)
    res_b_a = client.get(f"/api/v1/mentors/project-instances/{project_a_id}/{subpath}")
    assert res_b_a.status_code == 403, f"Mentor B accessing Project A on {subpath} must be 403"
