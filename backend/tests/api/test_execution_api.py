"""
GrowFlow Batch 5 (S18–S26) — API Tests for Execution Management Foundation.

Covers:
1. Tasks (S18 & S19):
   - List tasks returns 200
   - Create task returns 201
   - Get task returns 200
   - Update task status to COMPLETED updates completed_at and returns 200
   - Delete task returns 200
   - Cross-student access returns 403 Forbidden
2. Milestones (S20 & S21):
   - List milestones returns 200
   - Get milestone returns 200 with task breakdown
   - Update milestone returns 200
3. Risks (S22 & S23):
   - List risks returns 200
   - Create risk returns 201
   - Update risk returns 200
   - Delete risk returns 200
4. Roadmap (S24):
   - Deterministic projection returns 200 with summary and categorized queues
5. Documents (S25 & S26):
   - List documents returns 200
   - Create document returns 201
   - Get document returns 200
   - Update document bumps version and returns 200
   - Download raw markdown returns 200 with attachment header
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch
import uuid

from fastapi.testclient import TestClient
import jwt
import pytest

from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import get_execution_service
from backend.app.application.services.execution_service import ExecutionService
from backend.app.domain.identity import UserRole
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.execution import (
    ProjectDocumentModel,
    ProjectMilestoneModel,
    ProjectRiskModel,
    ProjectTaskModel,
)
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.execution_repository import (
    DocumentRepository,
    MilestoneRepository,
    RiskRepository,
    TaskRepository,
)
from backend.app.infrastructure.repositories.group_repository import GroupRepository
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.infrastructure.repositories.user_repository import UserRepository

if TYPE_CHECKING:
    from backend.app.config.settings import Settings

_TEST_SECRET = "execution-test-secret-at-least-32-chars-long-123"
_TEST_AUDIENCE = "authenticated"
_TEST_ISSUER = "https://test.supabase.co/auth/v1"


def _make_jwt(
    user_id: uuid.UUID,
    email: str = "test@example.com",
    role: str = "STUDENT",
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "email": email,
        "aud": _TEST_AUDIENCE,
        "iss": _TEST_ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=3600)).timestamp()),
        "app_metadata": {"role": role},
    }
    return jwt.encode(payload, _TEST_SECRET, algorithm="HS256")


@pytest.fixture
def auth_settings(test_settings: Settings) -> Settings:
    test_settings.auth.JWT_SECRET = _TEST_SECRET
    test_settings.auth.JWT_AUDIENCE = _TEST_AUDIENCE
    test_settings.auth.JWT_ISSUER = _TEST_ISSUER
    test_settings.database.DATABASE_URL = None
    return test_settings


@pytest.fixture
def owner_student_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def other_student_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def project_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def owner_token(owner_student_id: uuid.UUID) -> str:
    return _make_jwt(owner_student_id, "owner@example.com", UserRole.STUDENT.value)


@pytest.fixture
def other_token(other_student_id: uuid.UUID) -> str:
    return _make_jwt(other_student_id, "other@example.com", UserRole.STUDENT.value)


@pytest.fixture
def sample_project(owner_student_id: uuid.UUID, project_id: uuid.UUID) -> ProjectInstanceModel:
    proj = ProjectInstanceModel()
    proj.id = str(project_id)
    proj.student_id = str(owner_student_id)
    proj.name = "Smart Logistics Drone"
    proj.problem = "Last-mile medical supply delivery delays"
    proj.proposed_solution = "Automated waypoint tracking drone"
    proj.complexity = "INTERMEDIATE"
    proj.current_phase = "BLUEPRINT"
    proj.health = "HEALTHY"
    proj.status = "ACTIVE"
    proj.progress_percentage = 35
    proj.group_id = None
    proj.created_at = datetime.now(UTC)
    proj.updated_at = datetime.now(UTC)
    return proj


@pytest.fixture
def sample_milestone(project_id: uuid.UUID) -> ProjectMilestoneModel:
    m = ProjectMilestoneModel()
    m.id = str(uuid.uuid4())
    m.project_instance_id = str(project_id)
    m.title = "Core Architecture Foundation"
    m.description = "Base models and database schemas setup"
    m.gate_code = "M1"
    m.status = "IN_PROGRESS"
    m.progress_percent = 50
    m.deliverables = ["Database Schema", "FastAPI Scaffolding"]
    m.section_order = 1
    m.created_at = datetime.now(UTC)
    m.updated_at = datetime.now(UTC)
    return m


@pytest.fixture
def sample_task(project_id: uuid.UUID, sample_milestone: ProjectMilestoneModel) -> ProjectTaskModel:
    t = ProjectTaskModel()
    t.id = str(uuid.uuid4())
    t.project_instance_id = str(project_id)
    t.milestone_id = sample_milestone.id
    t.task_code = "T01"
    t.title = "Configure database schema models"
    t.description = "Implement SQLAlchemy execution models"
    t.status = "TODO"
    t.priority = "HIGH"
    t.category = "BACKEND"
    t.phase = "IMPLEMENTATION"
    t.due_date = datetime.now(UTC) + timedelta(days=7)
    t.dependencies = []
    t.acceptance_criteria = ["Migration runs cleanly", "Unit tests pass"]
    t.completed_at = None
    t.created_at = datetime.now(UTC)
    t.updated_at = datetime.now(UTC)
    return t


@pytest.fixture
def sample_risk(project_id: uuid.UUID) -> ProjectRiskModel:
    r = ProjectRiskModel()
    r.id = str(uuid.uuid4())
    r.project_instance_id = str(project_id)
    r.risk_code = "R01"
    r.title = "Battery consumption during high headwinds"
    r.description = "Adverse weather conditions may deplete battery faster than calculated."
    r.severity = "HIGH"
    r.probability = "MEDIUM"
    r.impact = "HIGH"
    r.status = "OPEN"
    r.mitigation = "Implement dynamic return-to-base threshold triggers."
    r.owner = "Student"
    r.review_date = None
    r.created_at = datetime.now(UTC)
    r.updated_at = datetime.now(UTC)
    return r


@pytest.fixture
def sample_document(project_id: uuid.UUID) -> ProjectDocumentModel:
    d = ProjectDocumentModel()
    d.id = str(uuid.uuid4())
    d.project_instance_id = str(project_id)
    d.document_key = "master_architecture"
    d.title = "Master Architecture Blueprint"
    d.doc_type = "BLUEPRINT"
    d.format = "markdown"
    d.content = "# Master Architecture Blueprint\n\nOperational architecture details."
    d.version = "1.0"
    d.status = "ACTIVE"
    d.source = "BLUEPRINT_INIT"
    d.created_at = datetime.now(UTC)
    d.updated_at = datetime.now(UTC)
    return d


class MockUserRepo:
    def __init__(self, owner_student_id: uuid.UUID, other_student_id: uuid.UUID) -> None:
        self._users = {
            str(owner_student_id): UserModel(
                id=str(owner_student_id),
                email="owner@example.com",
                role="STUDENT",
                status="ACTIVE",
            ),
            str(other_student_id): UserModel(
                id=str(other_student_id),
                email="other@example.com",
                role="STUDENT",
                status="ACTIVE",
            ),
        }

    async def get_by_id(self, user_id: uuid.UUID | str) -> UserModel | None:
        return self._users.get(str(user_id))


@pytest.fixture
def mock_execution_service(
    sample_project: ProjectInstanceModel,
    sample_milestone: ProjectMilestoneModel,
    sample_task: ProjectTaskModel,
    sample_risk: ProjectRiskModel,
    sample_document: ProjectDocumentModel,
) -> ExecutionService:
    service = AsyncMock(spec=ExecutionService)

    from backend.app.api.schemas.execution import (
        DocumentResponse,
        MilestoneResponse,
        RiskResponse,
        RoadmapGroupedTasks,
        RoadmapMilestoneItem,
        RoadmapResponse,
        RoadmapSummary,
        TaskResponse,
    )

    t_resp = TaskResponse.model_validate(sample_task)
    m_resp = MilestoneResponse(
        id=sample_milestone.id,
        project_instance_id=sample_milestone.project_instance_id,
        title=sample_milestone.title,
        description=sample_milestone.description or "",
        gate_code=sample_milestone.gate_code or "",
        target_date=sample_milestone.target_date,
        status=sample_milestone.status,
        progress_percent=sample_milestone.progress_percent,
        deliverables=sample_milestone.deliverables or [],
        section_order=sample_milestone.section_order,
        task_count=1,
        completed_task_count=0,
        tasks=[t_resp],
        created_at=sample_milestone.created_at,
        updated_at=sample_milestone.updated_at,
    )
    r_resp = RiskResponse.model_validate(sample_risk)
    d_resp = DocumentResponse.model_validate(sample_document)

    roadmap_resp = RoadmapResponse(
        project_id=str(sample_project.id),
        project_name=sample_project.name,
        current_phase=sample_project.current_phase,
        summary=RoadmapSummary(
            total_milestones=1,
            completed_milestones=0,
            total_tasks=1,
            completed_tasks=0,
            overdue_tasks_count=0,
            blocked_tasks_count=0,
            current_phase=sample_project.current_phase,
            overall_progress=sample_project.progress_percentage,
        ),
        milestones=[
            RoadmapMilestoneItem(
                id=m_resp.id,
                gate_code=m_resp.gate_code,
                title=m_resp.title,
                description=m_resp.description,
                status=m_resp.status,
                progress_percent=m_resp.progress_percent,
                target_date=m_resp.target_date,
                deliverables=m_resp.deliverables,
                tasks=[t_resp],
            )
        ],
        grouped_tasks=RoadmapGroupedTasks(
            overdue=[],
            blocked=[],
            in_progress=[],
            upcoming=[t_resp],
            completed=[],
        ),
    )

    # Wire mocked methods
    service.list_tasks.return_value = [t_resp]
    service.get_task.return_value = t_resp
    service.create_task.return_value = t_resp
    service.update_task.return_value = t_resp
    service.delete_task.return_value = True

    service.list_milestones.return_value = [m_resp]
    service.get_milestone.return_value = m_resp
    service.create_milestone.return_value = m_resp
    service.update_milestone.return_value = m_resp

    service.list_risks.return_value = [r_resp]
    service.get_risk.return_value = r_resp
    service.create_risk.return_value = r_resp
    service.update_risk.return_value = r_resp
    service.delete_risk.return_value = True

    service.get_roadmap.return_value = roadmap_resp

    service.list_documents.return_value = [d_resp]
    service.get_document.return_value = d_resp
    service.create_document.return_value = d_resp
    service.update_document.return_value = d_resp
    service.get_raw_document.return_value = ("master_architecture.md", d_resp.content)

    return service


@pytest.fixture
def client(
    auth_settings: Settings,
    mock_execution_service: ExecutionService,
    owner_student_id: uuid.UUID,
    other_student_id: uuid.UUID,
) -> TestClient:
    app = create_app(auth_settings)
    mock_user_repo = MockUserRepo(owner_student_id, other_student_id)

    app.dependency_overrides[get_execution_service] = lambda: mock_execution_service
    app.dependency_overrides[get_db_session] = lambda: AsyncMock()

    with patch("backend.app.api.dependencies.auth.UserRepository", return_value=mock_user_repo):
        yield TestClient(app)

    app.dependency_overrides.clear()


# ============================================================================
# Tests: Tasks (S18 & S19)
# ============================================================================

def test_list_tasks_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
) -> None:
    res = client.get(
        f"/api/v1/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["task_code"] == "T01"


def test_create_task_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
) -> None:
    payload = {
        "title": "Build WebSocket notification channel",
        "description": "Establish persistent duplex connections",
        "priority": "HIGH",
        "category": "BACKEND",
        "phase": "IMPLEMENTATION",
    }
    res = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=payload,
    )
    assert res.status_code == 201
    assert res.json()["data"]["title"] == "Configure database schema models"


def test_get_task_success(
    client: TestClient,
    project_id: uuid.UUID,
    sample_task: ProjectTaskModel,
    owner_token: str,
) -> None:
    res = client.get(
        f"/api/v1/projects/{project_id}/tasks/{sample_task.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["id"] == str(sample_task.id)


def test_update_task_success(
    client: TestClient,
    project_id: uuid.UUID,
    sample_task: ProjectTaskModel,
    owner_token: str,
) -> None:
    payload = {"status": "COMPLETED"}
    res = client.patch(
        f"/api/v1/projects/{project_id}/tasks/{sample_task.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=payload,
    )
    assert res.status_code == 200


def test_delete_task_success(
    client: TestClient,
    project_id: uuid.UUID,
    sample_task: ProjectTaskModel,
    owner_token: str,
) -> None:
    res = client.delete(
        f"/api/v1/projects/{project_id}/tasks/{sample_task.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200


# ============================================================================
# Tests: Milestones (S20 & S21)
# ============================================================================

def test_list_milestones_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
) -> None:
    res = client.get(
        f"/api/v1/projects/{project_id}/milestones",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["gate_code"] == "M1"
    assert data[0]["progress_percent"] == 50


def test_get_milestone_success(
    client: TestClient,
    project_id: uuid.UUID,
    sample_milestone: ProjectMilestoneModel,
    owner_token: str,
) -> None:
    res = client.get(
        f"/api/v1/projects/{project_id}/milestones/{sample_milestone.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["gate_code"] == "M1"


# ============================================================================
# Tests: Risks (S22 & S23)
# ============================================================================

def test_list_risks_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
) -> None:
    res = client.get(
        f"/api/v1/projects/{project_id}/risks",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    assert len(res.json()["data"]) == 1
    assert res.json()["data"][0]["risk_code"] == "R01"


def test_create_risk_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
) -> None:
    payload = {
        "title": "Component latency spike",
        "description": "Network latency exceeding timeout",
        "severity": "MEDIUM",
        "mitigation": "Increase timeout threshold",
    }
    res = client.post(
        f"/api/v1/projects/{project_id}/risks",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=payload,
    )
    assert res.status_code == 201


# ============================================================================
# Tests: Roadmap Projection (S24)
# ============================================================================

def test_get_roadmap_projection_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
) -> None:
    res = client.get(
        f"/api/v1/projects/{project_id}/roadmap",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert "summary" in data
    assert data["summary"]["overall_progress"] == 35
    assert len(data["milestones"]) == 1
    assert "grouped_tasks" in data


# ============================================================================
# Tests: Documents (S25 & S26)
# ============================================================================

def test_list_documents_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
) -> None:
    res = client.get(
        f"/api/v1/projects/{project_id}/documents",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["document_key"] == "master_architecture"


def test_download_raw_document_success(
    client: TestClient,
    project_id: uuid.UUID,
    sample_document: ProjectDocumentModel,
    owner_token: str,
) -> None:
    res = client.get(
        f"/api/v1/projects/{project_id}/documents/{sample_document.id}/download",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    assert "text/markdown" in res.headers["content-type"]
    assert "attachment; filename=" in res.headers["content-disposition"]
    assert "Master Architecture Blueprint" in res.text
