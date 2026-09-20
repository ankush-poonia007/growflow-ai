"""
GrowFlow Gate 10 — API Tests for Execution Management Foundation.

Exercises the REAL ExecutionService and canonical authorization helpers with controlled
in-memory repository doubles to test the complete HTTP API surface, cross-student isolation,
mentor permissions, admin governance, cross-project containment, and lifecycle operations.

Covers:
1. Tasks (S18 & S19):
   - List tasks returns 200
   - Create task returns 201
   - Get task returns 200
   - Update task status to COMPLETED updates completed_at and returns 200
   - Delete task returns 200
2. Milestones (S20 & S21):
   - List milestones returns 200
   - Get milestone returns 200 with task breakdown
   - Create milestone returns 201
   - Update milestone returns 200
3. Risks (S22 & S23):
   - List risks returns 200
   - Create risk returns 201
   - Get risk returns 200
   - Update risk returns 200
   - Delete risk returns 200
4. Roadmap (S24):
   - Deterministic projection returns 200 with summary and categorized queues
5. Documents (S25 & S26):
   - List documents returns 200
   - Create document returns 201
   - Get document returns 200
   - Update document increments version (1.0 -> 1.1) and returns 200
   - Download raw markdown returns 200 with attachment header
6. Security & Isolation (Gate 10 Hardening):
   - Cross-student access denied (403 Forbidden) across read and mutation endpoints
   - Supervising mentor permitted read-only (200 OK), denied mutation (403 Forbidden)
   - Non-supervising mentor denied all access (403 Forbidden)
   - Admin permitted governance read and write operations
   - Cross-project entity containment returns 404 Not Found (no cross-project IDOR)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, patch
import uuid

from fastapi.testclient import TestClient
import jwt
import pytest

from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import get_execution_service
from backend.app.application.services.execution_service import ExecutionService
from backend.app.application.services.outbox_service import OutboxService
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.execution import (
    ProjectDocumentModel,
    ProjectMilestoneModel,
    ProjectRiskModel,
    ProjectTaskModel,
)
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository
from backend.app.infrastructure.repositories.group_repository import GroupRepository
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.infrastructure.repositories.user_repository import UserRepository

if TYPE_CHECKING:
    from collections.abc import Generator

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
def supervising_mentor_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def other_mentor_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def admin_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def project_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def project_b_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def owner_token(owner_student_id: uuid.UUID) -> str:
    return _make_jwt(owner_student_id, "owner@example.com", UserRole.STUDENT.value)


@pytest.fixture
def other_token(other_student_id: uuid.UUID) -> str:
    return _make_jwt(other_student_id, "other@example.com", UserRole.STUDENT.value)


@pytest.fixture
def supervising_mentor_token(supervising_mentor_id: uuid.UUID) -> str:
    return _make_jwt(supervising_mentor_id, "mentor_sup@example.com", UserRole.MENTOR.value)


@pytest.fixture
def other_mentor_token(other_mentor_id: uuid.UUID) -> str:
    return _make_jwt(other_mentor_id, "mentor_other@example.com", UserRole.MENTOR.value)


@pytest.fixture
def admin_token(admin_id: uuid.UUID) -> str:
    return _make_jwt(admin_id, "admin@example.com", UserRole.ADMIN.value)


@pytest.fixture
def sample_project(owner_student_id: uuid.UUID, project_id: uuid.UUID) -> ProjectInstanceModel:
    proj = ProjectInstanceModel()
    proj.id = str(project_id)  # type: ignore[assignment]
    proj.student_id = str(owner_student_id)
    proj.name = "Smart Logistics Drone"
    proj.problem = "Last-mile medical supply delivery delays"
    proj.proposed_solution = "Automated waypoint tracking drone"
    proj.complexity = "INTERMEDIATE"
    proj.current_phase = "PLANNING"
    proj.health = "HEALTHY"
    proj.status = "ACTIVE"
    proj.progress_percentage = 35
    proj.group_id = None
    proj.created_at = datetime.now(UTC)
    proj.updated_at = datetime.now(UTC)
    return proj


@pytest.fixture
def project_b(other_student_id: uuid.UUID, project_b_id: uuid.UUID) -> ProjectInstanceModel:
    proj = ProjectInstanceModel()
    proj.id = str(project_b_id)  # type: ignore[assignment]
    proj.student_id = str(other_student_id)
    proj.name = "Autonomous Ocean Cleanup Vessel"
    proj.problem = "Ocean plastics tracking"
    proj.proposed_solution = "Autonomous solar-powered cleanup drone"
    proj.complexity = "ADVANCED"
    proj.current_phase = "PLANNING"
    proj.health = "HEALTHY"
    proj.status = "ACTIVE"
    proj.progress_percentage = 20
    proj.group_id = None
    proj.created_at = datetime.now(UTC)
    proj.updated_at = datetime.now(UTC)
    return proj


@pytest.fixture
def sample_milestone(project_id: uuid.UUID) -> ProjectMilestoneModel:
    m = ProjectMilestoneModel()
    m.id = str(uuid.uuid4())  # type: ignore[assignment]
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
    t.id = str(uuid.uuid4())  # type: ignore[assignment]
    t.project_instance_id = str(project_id)
    t.milestone_id = str(sample_milestone.id)
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
    r.id = str(uuid.uuid4())  # type: ignore[assignment]
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
    d.id = str(uuid.uuid4())  # type: ignore[assignment]
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


@pytest.fixture
def project_b_milestone(project_b_id: uuid.UUID) -> ProjectMilestoneModel:
    m = ProjectMilestoneModel()
    m.id = str(uuid.uuid4())  # type: ignore[assignment]
    m.project_instance_id = str(project_b_id)
    m.title = "Project B Vessel Frame Assembly"
    m.description = "Hardware hull design"
    m.gate_code = "M1"
    m.status = "UPCOMING"
    m.progress_percent = 0
    m.deliverables = ["CAD Schematics"]
    m.section_order = 1
    m.created_at = datetime.now(UTC)
    m.updated_at = datetime.now(UTC)
    return m


@pytest.fixture
def project_b_task(project_b_id: uuid.UUID) -> ProjectTaskModel:
    t = ProjectTaskModel()
    t.id = str(uuid.uuid4())  # type: ignore[assignment]
    t.project_instance_id = str(project_b_id)
    t.milestone_id = None
    t.task_code = "T01"
    t.title = "Project B Hull Hydrodynamics Simulation"
    t.description = "Simulate drag"
    t.status = "TODO"
    t.priority = "MEDIUM"
    t.category = "HARDWARE"
    t.phase = "PLANNING"
    t.dependencies = []
    t.acceptance_criteria = []
    t.created_at = datetime.now(UTC)
    t.updated_at = datetime.now(UTC)
    return t


@pytest.fixture
def project_b_risk(project_b_id: uuid.UUID) -> ProjectRiskModel:
    r = ProjectRiskModel()
    r.id = str(uuid.uuid4())  # type: ignore[assignment]
    r.project_instance_id = str(project_b_id)
    r.risk_code = "R01"
    r.title = "Project B Saltwater corrosion"
    r.description = "Rapid rust"
    r.severity = "HIGH"
    r.probability = "HIGH"
    r.impact = "HIGH"
    r.status = "OPEN"
    r.mitigation = "Marine-grade coating"
    r.owner = "Student"
    r.created_at = datetime.now(UTC)
    r.updated_at = datetime.now(UTC)
    return r


@pytest.fixture
def project_b_document(project_b_id: uuid.UUID) -> ProjectDocumentModel:
    d = ProjectDocumentModel()
    d.id = str(uuid.uuid4())  # type: ignore[assignment]
    d.project_instance_id = str(project_b_id)
    d.document_key = "vessel_hull_spec"
    d.title = "Vessel Hull Specification"
    d.doc_type = "SPECIFICATION"
    d.format = "markdown"
    d.content = "# Vessel Hull Specification\n\nConfidential Project B Data."
    d.version = "1.0"
    d.status = "ACTIVE"
    d.source = "STUDENT_CREATED"
    d.created_at = datetime.now(UTC)
    d.updated_at = datetime.now(UTC)
    return d


@pytest.fixture
def client(
    auth_settings: Settings,
    owner_student_id: uuid.UUID,
    other_student_id: uuid.UUID,
    supervising_mentor_id: uuid.UUID,
    other_mentor_id: uuid.UUID,
    admin_id: uuid.UUID,
    sample_project: ProjectInstanceModel,
    project_b: ProjectInstanceModel,
    sample_milestone: ProjectMilestoneModel,
    sample_task: ProjectTaskModel,
    sample_risk: ProjectRiskModel,
    sample_document: ProjectDocumentModel,
    project_b_milestone: ProjectMilestoneModel,
    project_b_task: ProjectTaskModel,
    project_b_risk: ProjectRiskModel,
    project_b_document: ProjectDocumentModel,
) -> Generator[TestClient, None, None]:
    """
    Wires up a REAL ExecutionService instance with in-memory repository doubles.
    This guarantees that real service authorization logic (ownership, mentor rules,
    admin privileges, and containment) executes on every HTTP request.
    """
    # In-memory entity stores
    project_store: dict[str, ProjectInstanceModel] = {
        str(sample_project.id): sample_project,
        str(project_b.id): project_b,
    }
    milestone_store: dict[str, ProjectMilestoneModel] = {
        str(sample_milestone.id): sample_milestone,
        str(project_b_milestone.id): project_b_milestone,
    }
    task_store: dict[str, ProjectTaskModel] = {
        str(sample_task.id): sample_task,
        str(project_b_task.id): project_b_task,
    }
    risk_store: dict[str, ProjectRiskModel] = {
        str(sample_risk.id): sample_risk,
        str(project_b_risk.id): project_b_risk,
    }
    document_store: dict[str, ProjectDocumentModel] = {
        str(sample_document.id): sample_document,
        str(project_b_document.id): project_b_document,
    }
    blueprint_store: dict[str, Any] = {}

    user_store: dict[str, UserModel] = {
        str(owner_student_id): UserModel(
            id=str(owner_student_id),
            email="owner@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Owner Student",
        ),
        str(other_student_id): UserModel(
            id=str(other_student_id),
            email="other@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Other Student",
        ),
        str(supervising_mentor_id): UserModel(
            id=str(supervising_mentor_id),
            email="mentor_sup@example.com",
            role=UserRole.MENTOR.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Supervising Mentor",
        ),
        str(other_mentor_id): UserModel(
            id=str(other_mentor_id),
            email="mentor_other@example.com",
            role=UserRole.MENTOR.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Other Mentor",
        ),
        str(admin_id): UserModel(
            id=str(admin_id),
            email="admin@example.com",
            role=UserRole.ADMIN.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Platform Admin",
        ),
    }

    mock_user_repo = AsyncMock(spec=UserRepository)
    mock_user_repo.get_by_id.side_effect = lambda uid: user_store.get(str(uid))

    # Project repository
    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_project_repo.get_by_id.side_effect = lambda pid: project_store.get(str(pid))

    async def _save_proj(p: ProjectInstanceModel) -> ProjectInstanceModel:
        project_store[str(p.id)] = p
        return p

    mock_project_repo.save.side_effect = _save_proj

    # Group repository (Mentor supervision evaluation)
    mock_group_repo = AsyncMock(spec=GroupRepository)

    async def _is_supervised(student_id: uuid.UUID | str, mentor_id: uuid.UUID | str) -> bool:
        return str(mentor_id) == str(supervising_mentor_id) and str(student_id) == str(
            owner_student_id
        )

    mock_group_repo.is_student_supervised_by_mentor.side_effect = _is_supervised
    mock_group_repo.get_by_id.return_value = None

    # Blueprint repository
    mock_blueprint_repo = AsyncMock(spec=BlueprintRepository)
    mock_blueprint_repo.get_latest_by_project.side_effect = lambda pid: blueprint_store.get(
        str(pid)
    )

    # Milestone repository
    mock_milestone_repo = AsyncMock()
    mock_milestone_repo.count_by_project.side_effect = lambda pid: len(
        [m for m in milestone_store.values() if m.project_instance_id == str(pid)]
    )

    async def _list_milestones(pid: uuid.UUID | str) -> list[ProjectMilestoneModel]:
        return sorted(
            [m for m in milestone_store.values() if m.project_instance_id == str(pid)],
            key=lambda x: (x.section_order, x.created_at or datetime.min.replace(tzinfo=UTC)),
        )

    mock_milestone_repo.list_by_project.side_effect = _list_milestones
    mock_milestone_repo.get_by_id.side_effect = lambda mid: milestone_store.get(str(mid))

    async def _create_milestone(m: ProjectMilestoneModel) -> ProjectMilestoneModel:
        if m.created_at is None:
            m.created_at = datetime.now(UTC)
        if m.updated_at is None:
            m.updated_at = datetime.now(UTC)
        milestone_store[str(m.id)] = m
        return m

    async def _save_milestone(m: ProjectMilestoneModel) -> ProjectMilestoneModel:
        m.updated_at = datetime.now(UTC)
        milestone_store[str(m.id)] = m
        return m

    mock_milestone_repo.create.side_effect = _create_milestone
    mock_milestone_repo.save.side_effect = _save_milestone

    # Task repository
    mock_task_repo = AsyncMock()
    mock_task_repo.count_by_project.side_effect = lambda pid: len(
        [t for t in task_store.values() if t.project_instance_id == str(pid)]
    )
    mock_task_repo.count_completed_by_project.side_effect = lambda pid: len(
        [
            t
            for t in task_store.values()
            if t.project_instance_id == str(pid) and t.status == "COMPLETED"
        ]
    )

    async def _list_tasks(
        pid: uuid.UUID | str,
        status: str | None = None,
        priority: str | None = None,
        milestone_id: str | None = None,
        phase: str | None = None,
        search: str | None = None,
    ) -> list[ProjectTaskModel]:
        res = [t for t in task_store.values() if t.project_instance_id == str(pid)]
        if status:
            res = [t for t in res if t.status == status]
        if priority:
            res = [t for t in res if t.priority == priority]
        if milestone_id:
            res = [t for t in res if t.milestone_id == milestone_id]
        if phase:
            res = [t for t in res if t.phase == phase]
        if search:
            q = search.strip().lower()
            res = [
                t
                for t in res
                if q in (t.title or "").lower()
                or q in (t.description or "").lower()
                or q in (t.task_code or "").lower()
            ]
        return sorted(res, key=lambda x: x.created_at or datetime.min.replace(tzinfo=UTC))

    mock_task_repo.list_by_project.side_effect = _list_tasks
    mock_task_repo.get_by_id.side_effect = lambda tid: task_store.get(str(tid))

    async def _create_task(t: ProjectTaskModel) -> ProjectTaskModel:
        if t.created_at is None:
            t.created_at = datetime.now(UTC)
        if t.updated_at is None:
            t.updated_at = datetime.now(UTC)
        task_store[str(t.id)] = t
        return t

    async def _save_task(t: ProjectTaskModel) -> ProjectTaskModel:
        t.updated_at = datetime.now(UTC)
        task_store[str(t.id)] = t
        return t

    mock_task_repo.create.side_effect = _create_task
    mock_task_repo.save.side_effect = _save_task

    async def _del_task(tid: uuid.UUID | str) -> bool:
        return task_store.pop(str(tid), None) is not None

    mock_task_repo.delete_by_id.side_effect = _del_task

    # Risk repository
    mock_risk_repo = AsyncMock()
    mock_risk_repo.count_by_project.side_effect = lambda pid: len(
        [r for r in risk_store.values() if r.project_instance_id == str(pid)]
    )

    async def _list_risks(
        pid: uuid.UUID | str,
        status: str | None = None,
        severity: str | None = None,
        search: str | None = None,
    ) -> list[ProjectRiskModel]:
        res = [r for r in risk_store.values() if r.project_instance_id == str(pid)]
        if status:
            res = [r for r in res if r.status == status]
        if severity:
            res = [r for r in res if r.severity == severity]
        if search:
            q = search.strip().lower()
            res = [
                r for r in res if q in (r.title or "").lower() or q in (r.risk_code or "").lower()
            ]
        return sorted(res, key=lambda x: x.created_at or datetime.min.replace(tzinfo=UTC))

    mock_risk_repo.list_by_project.side_effect = _list_risks
    mock_risk_repo.get_by_id.side_effect = lambda rid: risk_store.get(str(rid))

    async def _create_risk(r: ProjectRiskModel) -> ProjectRiskModel:
        if r.created_at is None:
            r.created_at = datetime.now(UTC)
        if r.updated_at is None:
            r.updated_at = datetime.now(UTC)
        risk_store[str(r.id)] = r
        return r

    async def _save_risk(r: ProjectRiskModel) -> ProjectRiskModel:
        r.updated_at = datetime.now(UTC)
        risk_store[str(r.id)] = r
        return r

    mock_risk_repo.create.side_effect = _create_risk
    mock_risk_repo.save.side_effect = _save_risk

    async def _del_risk(rid: uuid.UUID | str) -> bool:
        return risk_store.pop(str(rid), None) is not None

    mock_risk_repo.delete_by_id.side_effect = _del_risk

    # Document repository
    mock_doc_repo = AsyncMock()
    mock_doc_repo.count_by_project.side_effect = lambda pid: len(
        [d for d in document_store.values() if d.project_instance_id == str(pid)]
    )

    async def _list_docs(
        pid: uuid.UUID | str,
        doc_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[ProjectDocumentModel]:
        res = [d for d in document_store.values() if d.project_instance_id == str(pid)]
        if doc_type:
            res = [d for d in res if d.doc_type == doc_type]
        if status:
            res = [d for d in res if d.status == status]
        if search:
            q = search.strip().lower()
            res = [
                d
                for d in res
                if q in (d.title or "").lower()
                or q in (d.document_key or "").lower()
                or q in (d.content or "").lower()
            ]
        return sorted(res, key=lambda x: x.created_at or datetime.min.replace(tzinfo=UTC))

    mock_doc_repo.list_by_project.side_effect = _list_docs
    mock_doc_repo.get_by_id.side_effect = lambda did: document_store.get(str(did))

    async def _create_doc(d: ProjectDocumentModel) -> ProjectDocumentModel:
        if d.created_at is None:
            d.created_at = datetime.now(UTC)
        if d.updated_at is None:
            d.updated_at = datetime.now(UTC)
        document_store[str(d.id)] = d
        return d

    async def _save_doc(d: ProjectDocumentModel) -> ProjectDocumentModel:
        d.updated_at = datetime.now(UTC)
        document_store[str(d.id)] = d
        return d

    mock_doc_repo.create.side_effect = _create_doc
    mock_doc_repo.save.side_effect = _save_doc

    mock_outbox_service = AsyncMock(spec=OutboxService)

    # Real ExecutionService initialized with our stateful mock repositories
    real_execution_service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=mock_group_repo,
        blueprint_repo=mock_blueprint_repo,
        milestone_repo=mock_milestone_repo,
        task_repo=mock_task_repo,
        risk_repo=mock_risk_repo,
        document_repo=mock_doc_repo,
        outbox_service=mock_outbox_service,
    )

    app = create_app(auth_settings)
    app.dependency_overrides[get_execution_service] = lambda: real_execution_service
    app.dependency_overrides[get_db_session] = lambda: AsyncMock()

    with (
        patch("backend.app.api.dependencies.auth.UserRepository", return_value=mock_user_repo),
        TestClient(app, base_url="http://testserver") as test_client,
    ):
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# 1. Tests: Tasks (S18 & S19)
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
    assert len(data) >= 1
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
    assert res.json()["data"]["title"] == "Build WebSocket notification channel"
    assert res.json()["data"]["task_code"] == "T02"


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
    assert res.json()["data"]["status"] == "COMPLETED"


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

    # Ensure deleted
    verify_res = client.get(
        f"/api/v1/projects/{project_id}/tasks/{sample_task.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert verify_res.status_code == 404


# ============================================================================
# 2. Tests: Milestones (S20 & S21)
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
    assert len(data) >= 1
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


def test_create_milestone_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
) -> None:
    payload = {
        "title": "Hardware Assembly & Flight Testing",
        "description": "Assemble motors, frame, and run trial flight paths.",
        "gate_code": "M2",
        "deliverables": ["Assembled Frame", "Flight Log Data"],
    }
    res = client.post(
        f"/api/v1/projects/{project_id}/milestones",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=payload,
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["title"] == "Hardware Assembly & Flight Testing"
    assert data["gate_code"] == "M2"
    assert data["deliverables"] == ["Assembled Frame", "Flight Log Data"]


def test_update_milestone_success(
    client: TestClient,
    project_id: uuid.UUID,
    sample_milestone: ProjectMilestoneModel,
    owner_token: str,
) -> None:
    payload = {
        "title": "Core Architecture Foundation (Completed)",
        "status": "COMPLETED",
    }
    res = client.patch(
        f"/api/v1/projects/{project_id}/milestones/{sample_milestone.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=payload,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["title"] == "Core Architecture Foundation (Completed)"
    assert data["status"] == "COMPLETED"


# ============================================================================
# 3. Tests: Risks (S22 & S23)
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
    assert len(res.json()["data"]) >= 1
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
        "probability": "LOW",
        "impact": "MEDIUM",
        "mitigation": "Increase timeout threshold and implement retry exponential backoff.",
    }
    res = client.post(
        f"/api/v1/projects/{project_id}/risks",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=payload,
    )
    assert res.status_code == 201
    assert res.json()["data"]["title"] == "Component latency spike"
    assert res.json()["data"]["risk_code"] == "R02"


def test_get_risk_success(
    client: TestClient,
    project_id: uuid.UUID,
    sample_risk: ProjectRiskModel,
    owner_token: str,
) -> None:
    res = client.get(
        f"/api/v1/projects/{project_id}/risks/{sample_risk.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["id"] == str(sample_risk.id)
    assert res.json()["data"]["risk_code"] == "R01"


def test_update_risk_success(
    client: TestClient,
    project_id: uuid.UUID,
    sample_risk: ProjectRiskModel,
    owner_token: str,
) -> None:
    payload = {
        "status": "RESOLVED",
        "severity": "LOW",
        "mitigation": "Dynamic throttle limit applied and validated.",
    }
    res = client.patch(
        f"/api/v1/projects/{project_id}/risks/{sample_risk.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=payload,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "RESOLVED"
    assert data["severity"] == "LOW"


def test_delete_risk_success(
    client: TestClient,
    project_id: uuid.UUID,
    sample_risk: ProjectRiskModel,
    owner_token: str,
) -> None:
    res = client.delete(
        f"/api/v1/projects/{project_id}/risks/{sample_risk.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200

    verify_res = client.get(
        f"/api/v1/projects/{project_id}/risks/{sample_risk.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert verify_res.status_code == 404


# ============================================================================
# 4. Tests: Roadmap Projection (S24)
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
    assert len(data["milestones"]) >= 1
    assert "grouped_tasks" in data


# ============================================================================
# 5. Tests: Documents (S25 & S26)
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
    assert len(data) >= 1
    assert data[0]["document_key"] == "master_architecture"


def test_create_document_success(
    client: TestClient,
    project_id: uuid.UUID,
    owner_token: str,
) -> None:
    payload = {
        "title": "API Specification Document",
        "doc_type": "SPECIFICATION",
        "format": "markdown",
        "content": "# API Specification\n\nREST contract endpoints and payloads.",
    }
    res = client.post(
        f"/api/v1/projects/{project_id}/documents",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=payload,
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["title"] == "API Specification Document"
    assert data["version"] == "1.0"
    assert data["status"] == "ACTIVE"


def test_get_document_success(
    client: TestClient,
    project_id: uuid.UUID,
    sample_document: ProjectDocumentModel,
    owner_token: str,
) -> None:
    res = client.get(
        f"/api/v1/projects/{project_id}/documents/{sample_document.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["id"] == str(sample_document.id)
    assert res.json()["data"]["document_key"] == "master_architecture"


def test_update_document_success_with_version_increment(
    client: TestClient,
    project_id: uuid.UUID,
    sample_document: ProjectDocumentModel,
    owner_token: str,
) -> None:
    payload = {
        "title": "Master Architecture Blueprint (v1.1)",
        "content": "# Master Architecture Blueprint\n\nUpdated with real-time websocket protocols.",
    }
    res = client.patch(
        f"/api/v1/projects/{project_id}/documents/{sample_document.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=payload,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["title"] == "Master Architecture Blueprint (v1.1)"
    assert data["version"] == "1.1"


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
    assert (
        f'attachment; filename="{sample_document.document_key}.md"'
        in res.headers["content-disposition"]
    )
    assert "Master Architecture Blueprint" in res.text


# ============================================================================
# 6. Security: Cross-Student Access & Mutation Isolation (G4)
# ============================================================================


def test_cross_student_read_access_forbidden(
    client: TestClient,
    project_id: uuid.UUID,
    sample_task: ProjectTaskModel,
    sample_milestone: ProjectMilestoneModel,
    sample_risk: ProjectRiskModel,
    sample_document: ProjectDocumentModel,
    other_token: str,
) -> None:
    """Verifies that Student B receives 403 Forbidden when attempting to read Student A's project."""
    endpoints = [
        f"/api/v1/projects/{project_id}/tasks",
        f"/api/v1/projects/{project_id}/tasks/{sample_task.id}",
        f"/api/v1/projects/{project_id}/milestones",
        f"/api/v1/projects/{project_id}/milestones/{sample_milestone.id}",
        f"/api/v1/projects/{project_id}/risks",
        f"/api/v1/projects/{project_id}/risks/{sample_risk.id}",
        f"/api/v1/projects/{project_id}/documents",
        f"/api/v1/projects/{project_id}/documents/{sample_document.id}",
        f"/api/v1/projects/{project_id}/documents/{sample_document.id}/download",
        f"/api/v1/projects/{project_id}/roadmap",
    ]
    for url in endpoints:
        res = client.get(url, headers={"Authorization": f"Bearer {other_token}"})
        assert res.status_code == 403, f"Expected 403 Forbidden on GET {url}, got {res.status_code}"
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_cross_student_mutation_forbidden(
    client: TestClient,
    project_id: uuid.UUID,
    sample_task: ProjectTaskModel,
    sample_milestone: ProjectMilestoneModel,
    sample_risk: ProjectRiskModel,
    sample_document: ProjectDocumentModel,
    other_token: str,
) -> None:
    """Verifies that Student B receives 403 Forbidden when attempting to mutate Student A's execution items."""
    mutations: list[tuple[str, str, dict[str, Any] | None]] = [
        ("POST", f"/api/v1/projects/{project_id}/tasks", {"title": "X", "phase": "PLANNING"}),
        ("PATCH", f"/api/v1/projects/{project_id}/tasks/{sample_task.id}", {"title": "X"}),
        ("DELETE", f"/api/v1/projects/{project_id}/tasks/{sample_task.id}", None),
        ("POST", f"/api/v1/projects/{project_id}/milestones", {"title": "X"}),
        (
            "PATCH",
            f"/api/v1/projects/{project_id}/milestones/{sample_milestone.id}",
            {"title": "X"},
        ),
        ("POST", f"/api/v1/projects/{project_id}/risks", {"title": "X", "mitigation": "M"}),
        ("PATCH", f"/api/v1/projects/{project_id}/risks/{sample_risk.id}", {"title": "X"}),
        ("DELETE", f"/api/v1/projects/{project_id}/risks/{sample_risk.id}", None),
        ("POST", f"/api/v1/projects/{project_id}/documents", {"title": "X", "content": "C"}),
        ("PATCH", f"/api/v1/projects/{project_id}/documents/{sample_document.id}", {"title": "X"}),
    ]
    for method, url, payload in mutations:
        if method == "POST":
            res = client.post(url, headers={"Authorization": f"Bearer {other_token}"}, json=payload)
        elif method == "PATCH":
            res = client.patch(
                url, headers={"Authorization": f"Bearer {other_token}"}, json=payload
            )
        elif method == "DELETE":
            res = client.delete(url, headers={"Authorization": f"Bearer {other_token}"})
        assert res.status_code == 403, f"Expected 403 on {method} {url}, got {res.status_code}"
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


# ============================================================================
# 7. Security: Supervising Mentor Permissions (G4-Mentor)
# ============================================================================


def test_supervising_mentor_can_read_execution_data(
    client: TestClient,
    project_id: uuid.UUID,
    sample_task: ProjectTaskModel,
    sample_milestone: ProjectMilestoneModel,
    sample_risk: ProjectRiskModel,
    sample_document: ProjectDocumentModel,
    supervising_mentor_token: str,
) -> None:
    """Verifies that an assigned supervising mentor has read-only access to execution data."""
    read_endpoints = [
        f"/api/v1/projects/{project_id}/tasks",
        f"/api/v1/projects/{project_id}/tasks/{sample_task.id}",
        f"/api/v1/projects/{project_id}/milestones",
        f"/api/v1/projects/{project_id}/milestones/{sample_milestone.id}",
        f"/api/v1/projects/{project_id}/risks",
        f"/api/v1/projects/{project_id}/risks/{sample_risk.id}",
        f"/api/v1/projects/{project_id}/documents",
        f"/api/v1/projects/{project_id}/documents/{sample_document.id}",
        f"/api/v1/projects/{project_id}/documents/{sample_document.id}/download",
        f"/api/v1/projects/{project_id}/roadmap",
    ]
    for url in read_endpoints:
        res = client.get(url, headers={"Authorization": f"Bearer {supervising_mentor_token}"})
        assert res.status_code == 200, (
            f"Expected 200 OK on {url} for supervising mentor, got {res.status_code}"
        )


def test_supervising_mentor_cannot_mutate_execution_data(
    client: TestClient,
    project_id: uuid.UUID,
    sample_task: ProjectTaskModel,
    sample_milestone: ProjectMilestoneModel,
    sample_risk: ProjectRiskModel,
    sample_document: ProjectDocumentModel,
    supervising_mentor_token: str,
) -> None:
    """Verifies that a supervising mentor is prohibited from modifying student execution records."""
    mutations: list[tuple[str, str, dict[str, Any] | None]] = [
        (
            "POST",
            f"/api/v1/projects/{project_id}/tasks",
            {"title": "Mentor Task", "phase": "PLANNING"},
        ),
        (
            "PATCH",
            f"/api/v1/projects/{project_id}/tasks/{sample_task.id}",
            {"title": "Updated by Mentor"},
        ),
        ("DELETE", f"/api/v1/projects/{project_id}/tasks/{sample_task.id}", None),
        ("POST", f"/api/v1/projects/{project_id}/milestones", {"title": "Mentor Milestone"}),
        (
            "PATCH",
            f"/api/v1/projects/{project_id}/milestones/{sample_milestone.id}",
            {"title": "Updated by Mentor"},
        ),
        (
            "POST",
            f"/api/v1/projects/{project_id}/risks",
            {"title": "Mentor Risk", "mitigation": "Mitigation"},
        ),
        (
            "PATCH",
            f"/api/v1/projects/{project_id}/risks/{sample_risk.id}",
            {"title": "Updated by Mentor"},
        ),
        ("DELETE", f"/api/v1/projects/{project_id}/risks/{sample_risk.id}", None),
        (
            "POST",
            f"/api/v1/projects/{project_id}/documents",
            {"title": "Mentor Doc", "content": "Content"},
        ),
        (
            "PATCH",
            f"/api/v1/projects/{project_id}/documents/{sample_document.id}",
            {"title": "Updated by Mentor"},
        ),
    ]
    for method, url, payload in mutations:
        if method == "POST":
            res = client.post(
                url, headers={"Authorization": f"Bearer {supervising_mentor_token}"}, json=payload
            )
        elif method == "PATCH":
            res = client.patch(
                url, headers={"Authorization": f"Bearer {supervising_mentor_token}"}, json=payload
            )
        elif method == "DELETE":
            res = client.delete(
                url, headers={"Authorization": f"Bearer {supervising_mentor_token}"}
            )
        assert res.status_code == 403, (
            f"Expected 403 on {method} {url} for supervising mentor, got {res.status_code}"
        )
        assert "Only the project owner may modify execution items" in res.json()["message"]
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


# ============================================================================
# 8. Security: Non-Supervising Mentor Isolation (G4-Mentor)
# ============================================================================


def test_non_supervising_mentor_access_denied(
    client: TestClient,
    project_id: uuid.UUID,
    sample_task: ProjectTaskModel,
    other_mentor_token: str,
) -> None:
    """Verifies that a mentor who does not supervise the project is denied all access."""
    # Read attempt -> 403 Forbidden
    read_res = client.get(
        f"/api/v1/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {other_mentor_token}"},
    )
    assert read_res.status_code == 403
    assert read_res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"

    # Mutation attempt -> 403 Forbidden
    mutate_res = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {other_mentor_token}"},
        json={"title": "Unauthorized Mentor Task", "phase": "PLANNING"},
    )
    assert mutate_res.status_code == 403
    assert mutate_res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


# ============================================================================
# 9. Security: Admin Governance Permissions (G4-Admin)
# ============================================================================


def test_admin_can_read_and_mutate_execution_data(
    client: TestClient,
    project_id: uuid.UUID,
    sample_task: ProjectTaskModel,
    sample_risk: ProjectRiskModel,
    sample_document: ProjectDocumentModel,
    admin_token: str,
) -> None:
    """Verifies platform admin access for governance, support, and administrative updates."""
    # Admin Read
    res = client.get(
        f"/api/v1/projects/{project_id}/tasks", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200

    res = client.get(
        f"/api/v1/projects/{project_id}/roadmap", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200

    # Admin Create Task
    create_res = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Admin Created Task", "phase": "PLANNING"},
    )
    assert create_res.status_code == 201

    # Admin Update Task
    update_res = client.patch(
        f"/api/v1/projects/{project_id}/tasks/{sample_task.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Admin Repaired Task Title"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["title"] == "Admin Repaired Task Title"

    # Admin Delete Task
    del_res = client.delete(
        f"/api/v1/projects/{project_id}/tasks/{sample_task.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert del_res.status_code == 200


# ============================================================================
# 10. Security: Cross-Project Entity Containment (IDOR Protection)
# ============================================================================


def test_cross_project_entity_containment_returns_404(
    client: TestClient,
    project_id: uuid.UUID,
    project_b_task: ProjectTaskModel,
    project_b_milestone: ProjectMilestoneModel,
    project_b_risk: ProjectRiskModel,
    project_b_document: ProjectDocumentModel,
    owner_token: str,
) -> None:
    """
    Verifies that an authorized user on Project A cannot access or mutate
    entities belonging to Project B by manipulating URL parameters.
    The service must verify entity.project_instance_id == project.id and return 404.
    """
    containment_cases: list[tuple[str, str, str]] = [
        ("GET", f"/api/v1/projects/{project_id}/tasks/{project_b_task.id}", "TASK_NOT_FOUND"),
        ("PATCH", f"/api/v1/projects/{project_id}/tasks/{project_b_task.id}", "TASK_NOT_FOUND"),
        ("DELETE", f"/api/v1/projects/{project_id}/tasks/{project_b_task.id}", "TASK_NOT_FOUND"),
        (
            "GET",
            f"/api/v1/projects/{project_id}/milestones/{project_b_milestone.id}",
            "MILESTONE_NOT_FOUND",
        ),
        (
            "PATCH",
            f"/api/v1/projects/{project_id}/milestones/{project_b_milestone.id}",
            "MILESTONE_NOT_FOUND",
        ),
        ("GET", f"/api/v1/projects/{project_id}/risks/{project_b_risk.id}", "RISK_NOT_FOUND"),
        ("PATCH", f"/api/v1/projects/{project_id}/risks/{project_b_risk.id}", "RISK_NOT_FOUND"),
        ("DELETE", f"/api/v1/projects/{project_id}/risks/{project_b_risk.id}", "RISK_NOT_FOUND"),
        (
            "GET",
            f"/api/v1/projects/{project_id}/documents/{project_b_document.id}",
            "DOCUMENT_NOT_FOUND",
        ),
        (
            "PATCH",
            f"/api/v1/projects/{project_id}/documents/{project_b_document.id}",
            "DOCUMENT_NOT_FOUND",
        ),
        (
            "GET",
            f"/api/v1/projects/{project_id}/documents/{project_b_document.id}/download",
            "DOCUMENT_NOT_FOUND",
        ),
    ]
    for method, url, expected_code in containment_cases:
        if method == "GET":
            res = client.get(url, headers={"Authorization": f"Bearer {owner_token}"})
        elif method == "PATCH":
            res = client.patch(
                url, headers={"Authorization": f"Bearer {owner_token}"}, json={"title": "Injected"}
            )
        elif method == "DELETE":
            res = client.delete(url, headers={"Authorization": f"Bearer {owner_token}"})
        assert res.status_code == 404, f"Expected 404 on {method} {url}, got {res.status_code}"
        assert res.json()["error"]["code"] == expected_code
