"""
GrowFlow Phase 8 Batch 5 — Cross-Role Platform Hardening API Tests.

Comprehensive automated verification of:
1. Authentication Boundaries (401: missing token, invalid format, invalid signature)
2. Role Boundaries (403: Student -> Mentor/Admin, Mentor -> Admin, Mentor -> Student mutation)
3. Student Isolation & IDOR Protection (403: cross-student projects/tasks/milestones/risks/docs)
4. Student Group Project Leak Fix (Student receives only their own projects from group listing)
5. Mentor Supervision Isolation & Cross-Mentor Cohort Boundary (Two-Branch Rule fix)
6. Legitimate Unassigned Project Supervision (Mentor supervises individual projects of enrolled students)
7. Supervising Mentor Group Project Listing (Mentor receives all projects in their cohort)
8. Nested Resource Isolation (404: child task/milestone/risk/document belonging to other project)
9. Nonexistent Resource Contracts (404: nonexistent project/group)
10. Admin Governance Boundaries (200: Admin retains governance access and cross-resource visibility)
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
    get_admin_service,
    get_execution_service,
    get_github_service,
    get_group_service,
    get_mentor_overview_service,
    get_mentor_student_service,
    get_project_service,
)
from backend.app.application.services.activity_service import ActivityService
from backend.app.application.services.admin_service import AdminService
from backend.app.application.services.execution_service import ExecutionService
from backend.app.application.services.github_service import GitHubService
from backend.app.application.services.group_service import GroupService
from backend.app.application.services.project_service import ProjectService
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.domain.project.models import ProjectHealth, ProjectPhase, ProjectStatus
from backend.app.infrastructure.database.models.execution import (
    ProjectDocumentModel,
    ProjectMilestoneModel,
    ProjectRiskModel,
    ProjectTaskModel,
)
from backend.app.domain.organization.models import GroupStatus
from backend.app.infrastructure.database.models.organization import (
    GroupMembershipModel,
    GroupModel,
)
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.shared.exceptions import AuthorizationException, NotFoundException


# ============================================================================
# DB Session & Fixture Setup
# ============================================================================

async def _mock_db_session() -> AsyncGenerator[AsyncMock, None]:
    mock_session = AsyncMock()
    yield mock_session


@pytest.fixture(autouse=True)
def override_db(app):
    app.dependency_overrides[get_db_session] = _mock_db_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def student_a() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="student_a@growflow.test",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def student_b() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="student_b@growflow.test",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def mentor_a() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="mentor_a@growflow.test",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def mentor_b() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="mentor_b@growflow.test",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def admin_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="admin@growflow.test",
        role=UserRole.ADMIN,
        status=AccountStatus.ACTIVE,
    )


def _make_project_model(
    project_id: uuid.UUID,
    student_id: uuid.UUID,
    group_id: uuid.UUID | None = None,
    name: str = "Test Project",
) -> ProjectInstanceModel:
    proj = ProjectInstanceModel()
    proj.id = project_id
    proj.student_id = student_id
    proj.group_id = group_id
    proj.project_definition_id = None
    proj.source_definition_version_id = None
    proj.name = name
    proj.problem = "Test Problem"
    proj.proposed_solution = "Test Solution"
    proj.complexity = "MEDIUM"
    proj.current_phase = ProjectPhase.IMPLEMENTATION.value
    proj.health = ProjectHealth.HEALTHY.value
    proj.progress_percentage = 40
    proj.status = ProjectStatus.ACTIVE.value
    proj.deadline = None
    proj.started_at = datetime.now(UTC)
    proj.completed_at = None
    proj.created_at = datetime.now(UTC)
    proj.updated_at = datetime.now(UTC)
    return proj


def _make_group_model(
    group_id: uuid.UUID,
    mentor_id: uuid.UUID,
    name: str = "Test Cohort",
) -> GroupModel:
    grp = GroupModel()
    grp.id = group_id
    grp.mentor_id = mentor_id
    grp.name = name
    grp.join_code = f"GRP{str(group_id)[:4].upper()}"
    grp.status = GroupStatus.ACTIVE.value
    grp.created_at = datetime.now(UTC)
    grp.updated_at = datetime.now(UTC)
    return grp


# ============================================================================
# 1. AUTHENTICATION BOUNDARIES (401)
# ============================================================================

def test_unauthenticated_request_returns_401(client: TestClient):
    """Missing Authorization header on protected endpoint returns 401 AUTH_MISSING_TOKEN."""
    target_url = f"/api/v1/projects/{uuid.uuid4()}"
    res = client.get(target_url)
    assert res.status_code == 401
    body = res.json()
    assert body["error"]["code"] == "AUTH_MISSING_TOKEN"


def test_invalid_token_format_returns_401(client: TestClient):
    """Malformed Authorization header returns 401 AUTH_INVALID_TOKEN_FORMAT."""
    target_url = f"/api/v1/projects/{uuid.uuid4()}"
    res = client.get(target_url, headers={"Authorization": "NotBearer invalid_token"})
    assert res.status_code == 401
    body = res.json()
    assert body["error"]["code"] == "AUTH_INVALID_TOKEN_FORMAT"


def test_invalid_jwt_signature_returns_401(client: TestClient):
    """Invalid or forged JWT signature returns 401 AUTH_INVALID_TOKEN."""
    target_url = f"/api/v1/projects/{uuid.uuid4()}"
    # Header format correct, but token invalid/forged
    res = client.get(target_url, headers={"Authorization": "Bearer forged.header.signature"})
    assert res.status_code == 401
    body = res.json()
    assert body["error"]["code"] == "AUTH_INVALID_TOKEN"


# ============================================================================
# 2. ROLE BOUNDARIES (403)
# ============================================================================

def test_student_accessing_mentor_overview_returns_403(client: TestClient, app, student_a):
    """Student caller rejected with 403 AUTH_FORBIDDEN_ROLE from mentor overview."""
    app.dependency_overrides[get_current_user] = lambda: student_a
    res = client.get("/api/v1/mentors/overview")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"


def test_student_creating_group_returns_403(client: TestClient, app, student_a):
    """Student caller rejected with 403 AUTH_FORBIDDEN_ROLE from POST /api/v1/groups."""
    app.dependency_overrides[get_current_user] = lambda: student_a
    res = client.post("/api/v1/groups", json={"name": "Forbidden Student Group"})
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"


def test_student_accessing_admin_endpoints_returns_403(client: TestClient, app, student_a):
    """Student caller rejected with 403 AUTH_FORBIDDEN_ROLE from all Admin endpoints."""
    app.dependency_overrides[get_current_user] = lambda: student_a
    for path in ["/api/v1/admin/overview", "/api/v1/admin/health", "/api/v1/admin/mentors", "/api/v1/admin/students"]:
        res = client.get(path)
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"


def test_mentor_accessing_admin_endpoints_returns_403(client: TestClient, app, mentor_a):
    """Mentor caller rejected with 403 AUTH_FORBIDDEN_ROLE from Admin endpoints."""
    app.dependency_overrides[get_current_user] = lambda: mentor_a
    for path in ["/api/v1/admin/overview", "/api/v1/admin/health"]:
        res = client.get(path)
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"


def test_mentor_creating_student_project_returns_403(client: TestClient, app, mentor_a):
    """Mentor caller rejected with 403 AUTH_FORBIDDEN_ROLE from student-only project creation."""
    app.dependency_overrides[get_current_user] = lambda: mentor_a
    res = client.post("/api/v1/projects", json={
        "name": "Mentor Project",
        "problem": "Problem",
        "proposed_solution": "Solution",
        "complexity": "MEDIUM",
    })
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"


# ============================================================================
# 3. STUDENT ISOLATION & IDOR PROTECTION (403)
# ============================================================================

def test_student_cannot_access_other_student_project(client: TestClient, app, student_a, student_b):
    """Student A cannot access Student B's project (403 AUTH_FORBIDDEN_RESOURCE)."""
    project_b = _make_project_model(uuid.uuid4(), student_b.user_id)

    mock_project_service = AsyncMock(spec=ProjectService)
    mock_project_service.get_project.side_effect = AuthorizationException(
        "Access to this project is denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_project_service] = lambda: mock_project_service
    app.dependency_overrides[get_current_user] = lambda: student_a

    res = client.get(f"/api/v1/projects/{project_b.id}")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_student_cannot_access_other_student_tasks(client: TestClient, app, student_a, student_b):
    """Student A cannot access tasks of Student B's project (403 AUTH_FORBIDDEN_RESOURCE)."""
    project_b = _make_project_model(uuid.uuid4(), student_b.user_id)

    mock_execution_service = AsyncMock(spec=ExecutionService)
    mock_execution_service.list_tasks.side_effect = AuthorizationException(
        "Access denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_execution_service] = lambda: mock_execution_service
    app.dependency_overrides[get_current_user] = lambda: student_a

    res = client.get(f"/api/v1/projects/{project_b.id}/tasks")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_student_cannot_access_other_student_milestones(client: TestClient, app, student_a, student_b):
    """Student A cannot access milestones of Student B's project (403 AUTH_FORBIDDEN_RESOURCE)."""
    project_b = _make_project_model(uuid.uuid4(), student_b.user_id)

    mock_execution_service = AsyncMock(spec=ExecutionService)
    mock_execution_service.list_milestones.side_effect = AuthorizationException(
        "Access denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_execution_service] = lambda: mock_execution_service
    app.dependency_overrides[get_current_user] = lambda: student_a

    res = client.get(f"/api/v1/projects/{project_b.id}/milestones")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_student_cannot_access_other_student_risks(client: TestClient, app, student_a, student_b):
    """Student A cannot access risks of Student B's project (403 AUTH_FORBIDDEN_RESOURCE)."""
    project_b = _make_project_model(uuid.uuid4(), student_b.user_id)

    mock_execution_service = AsyncMock(spec=ExecutionService)
    mock_execution_service.list_risks.side_effect = AuthorizationException(
        "Access denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_execution_service] = lambda: mock_execution_service
    app.dependency_overrides[get_current_user] = lambda: student_a

    res = client.get(f"/api/v1/projects/{project_b.id}/risks")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_student_cannot_access_other_student_documents(client: TestClient, app, student_a, student_b):
    """Student A cannot access documents of Student B's project (403 AUTH_FORBIDDEN_RESOURCE)."""
    project_b = _make_project_model(uuid.uuid4(), student_b.user_id)

    mock_execution_service = AsyncMock(spec=ExecutionService)
    mock_execution_service.list_documents.side_effect = AuthorizationException(
        "Access denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_execution_service] = lambda: mock_execution_service
    app.dependency_overrides[get_current_user] = lambda: student_a

    res = client.get(f"/api/v1/projects/{project_b.id}/documents")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


# ============================================================================
# 4. STUDENT GROUP PROJECT LIST LEAK FIX VERIFICATION
# ============================================================================

@pytest.mark.asyncio
async def test_student_group_project_list_leak_eliminated(student_a, student_b):
    """
    Direct Service & API Invariant:
    A student querying group projects receives ONLY their own project instances in that group.
    Other students' projects in the same cohort group are filtered out.
    """
    group_id = uuid.uuid4()
    mock_group_repo = AsyncMock()
    mock_project_repo = AsyncMock()

    # Group exists
    group = _make_group_model(group_id, uuid.uuid4())
    mock_group_repo.get_by_id.return_value = group

    # Student A is an active member
    mock_group_repo.get_active_membership_for_student.return_value = MagicMock()

    # In database, group contains projects from Student A and Student B
    proj_a = _make_project_model(uuid.uuid4(), student_a.user_id, group_id, name="Student A Project")
    proj_b = _make_project_model(uuid.uuid4(), student_b.user_id, group_id, name="Student B Project")
    mock_project_repo.list_by_group.return_value = [proj_a, proj_b]

    service = ProjectService(
        project_repo=mock_project_repo,
        group_repo=mock_group_repo,
        technology_repo=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    # Student A queries group projects
    results = await service.list_group_projects(group_id, student_a)

    # Invariant: exactly 1 project returned (Student A's own), Student B's project is NOT leaked!
    assert len(results) == 1
    assert results[0].id == proj_a.id
    assert results[0].student_id == student_a.user_id


# ============================================================================
# 5. MENTOR SUPERVISION ISOLATION & THE TWO-BRANCH RULE FIX
# ============================================================================

def test_mentor_cannot_access_other_mentor_group(client: TestClient, app, mentor_a):
    """Mentor A cannot access Mentor B's group (403 AUTH_FORBIDDEN_RESOURCE)."""
    group_b_id = uuid.uuid4()
    mock_group_service = AsyncMock(spec=GroupService)
    mock_group_service.get_group.side_effect = AuthorizationException(
        "Access to this group is denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_group_service] = lambda: mock_group_service
    app.dependency_overrides[get_current_user] = lambda: mentor_a

    res = client.get(f"/api/v1/groups/{group_b_id}")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_mentor_cannot_access_other_mentor_group_projects(client: TestClient, app, mentor_a):
    """Mentor A cannot list projects in Mentor B's group (403 AUTH_FORBIDDEN_RESOURCE)."""
    group_b_id = uuid.uuid4()
    mock_project_service = AsyncMock(spec=ProjectService)
    mock_project_service.list_group_projects.side_effect = AuthorizationException(
        "You do not supervise this group.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_project_service] = lambda: mock_project_service
    app.dependency_overrides[get_current_user] = lambda: mentor_a

    res = client.get(f"/api/v1/groups/{group_b_id}/projects")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


@pytest.mark.asyncio
async def test_critical_cross_mentor_cohort_leak_eliminated(mentor_a, mentor_b, student_a):
    """
    CRITICAL TWO-BRANCH RULE VERIFICATION:
    Student X is enrolled in Mentor A's cohort (Project A, group_a).
    Student X is ALSO enrolled in an unrelated group supervised by Mentor B.
    Mentor B attempts to access Project A.

    BEFORE FIX: Fall-through to is_student_supervised_by_mentor granted Mentor B access!
    AFTER FIX: Cohort group ownership is authoritative. Fall-through is eliminated.
    Expected: AuthorizationException(403 AUTH_FORBIDDEN_RESOURCE).
    """
    group_a_id = uuid.uuid4()
    group_a = _make_group_model(group_a_id, mentor_a.user_id, name="Cohort A")
    project_a = _make_project_model(uuid.uuid4(), student_a.user_id, group_id=group_a_id)

    mock_group_repo = AsyncMock()
    mock_project_repo = AsyncMock()

    mock_project_repo.get_by_id.return_value = project_a
    mock_group_repo.get_by_id.return_value = group_a

    # Note: student_a IS supervised by mentor_b in an unrelated group
    mock_group_repo.is_student_supervised_by_mentor.return_value = True

    execution_service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=mock_group_repo,
        blueprint_repo=AsyncMock(),
        milestone_repo=AsyncMock(),
        task_repo=AsyncMock(),
        risk_repo=AsyncMock(),
        document_repo=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    # Mentor B attempts to access Project A: MUST BE REJECTED WITH 403!
    with pytest.raises(AuthorizationException) as exc_info:
        await execution_service._verify_project_access(project_a.id, mentor_b)
    assert exc_info.value.code == "AUTH_FORBIDDEN_RESOURCE"

    # Mentor A (supervising mentor of Cohort A): MUST SUCCEED!
    granted_project = await execution_service._verify_project_access(project_a.id, mentor_a)
    assert granted_project.id == project_a.id


@pytest.mark.asyncio
async def test_mentor_can_supervise_unassigned_project_of_enrolled_student(mentor_a, mentor_b, student_a):
    """
    CANONICAL TWO-BRANCH BRANCH 2:
    Project U has group_id = None (individual / unassigned project created by student_a).
    Student A is actively supervised by Mentor A.
    Student A is NOT supervised by Mentor B.

    Mentor A -> Granted access (supervises student in active group).
    Mentor B -> Denied access (403 AUTH_FORBIDDEN_RESOURCE).
    """
    project_u = _make_project_model(uuid.uuid4(), student_a.user_id, group_id=None)

    mock_group_repo = AsyncMock()
    mock_project_repo = AsyncMock()
    mock_project_repo.get_by_id.return_value = project_u

    async def _mock_is_supervised(student_id, mentor_id):
        return str(mentor_id) == str(mentor_a.user_id)

    mock_group_repo.is_student_supervised_by_mentor.side_effect = _mock_is_supervised

    execution_service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=mock_group_repo,
        blueprint_repo=AsyncMock(),
        milestone_repo=AsyncMock(),
        task_repo=AsyncMock(),
        risk_repo=AsyncMock(),
        document_repo=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    # Mentor A (supervises student_a): MUST BE GRANTED
    granted = await execution_service._verify_project_access(project_u.id, mentor_a)
    assert granted.id == project_u.id

    # Mentor B (does not supervise student_a): MUST BE FORBIDDEN
    with pytest.raises(AuthorizationException) as exc_info:
        await execution_service._verify_project_access(project_u.id, mentor_b)
    assert exc_info.value.code == "AUTH_FORBIDDEN_RESOURCE"


# ============================================================================
# 6. SUPERVISING MENTOR GROUP PROJECT LISTING
# ============================================================================

@pytest.mark.asyncio
async def test_supervising_mentor_lists_all_group_projects(mentor_a, student_a, student_b):
    """Supervising mentor receives all projects belonging to their cohort group."""
    group_id = uuid.uuid4()
    group = _make_group_model(group_id, mentor_a.user_id)

    mock_group_repo = AsyncMock()
    mock_project_repo = AsyncMock()
    mock_group_repo.get_by_id.return_value = group

    proj_a = _make_project_model(uuid.uuid4(), student_a.user_id, group_id)
    proj_b = _make_project_model(uuid.uuid4(), student_b.user_id, group_id)
    mock_project_repo.list_by_group.return_value = [proj_a, proj_b]

    service = ProjectService(
        project_repo=mock_project_repo,
        group_repo=mock_group_repo,
        technology_repo=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    results = await service.list_group_projects(group_id, mentor_a)
    assert len(results) == 2


# ============================================================================
# 7. NESTED RESOURCE ISOLATION CONTRACT (404)
# ============================================================================

@pytest.mark.asyncio
async def test_nested_task_mismatch_returns_404(student_a):
    """Requesting Task from Project B via Project A's URL yields 404 TASK_NOT_FOUND."""
    project_a = _make_project_model(uuid.uuid4(), student_a.user_id)
    other_project_id = str(uuid.uuid4())

    mock_project_repo = AsyncMock()
    mock_project_repo.get_by_id.return_value = project_a

    # Task belongs to other_project_id, not project_a
    foreign_task = ProjectTaskModel(
        id=str(uuid.uuid4()),
        project_instance_id=other_project_id,
        milestone_id=None,
        task_code="T01",
        title="Foreign Task",
        description="",
        status="TODO",
        priority="MEDIUM",
        category="GENERAL",
        phase="IMPLEMENTATION",
    )
    mock_task_repo = AsyncMock()
    mock_task_repo.get_by_id.return_value = foreign_task

    service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=AsyncMock(),
        blueprint_repo=AsyncMock(),
        milestone_repo=AsyncMock(),
        task_repo=mock_task_repo,
        risk_repo=AsyncMock(),
        document_repo=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    with pytest.raises(NotFoundException) as exc_info:
        await service.get_task(project_a.id, foreign_task.id, student_a)
    assert exc_info.value.code == "TASK_NOT_FOUND"


@pytest.mark.asyncio
async def test_nested_milestone_mismatch_returns_404(student_a):
    """Requesting Milestone from Project B via Project A's URL yields 404 MILESTONE_NOT_FOUND."""
    project_a = _make_project_model(uuid.uuid4(), student_a.user_id)
    other_project_id = str(uuid.uuid4())

    mock_project_repo = AsyncMock()
    mock_project_repo.get_by_id.return_value = project_a

    foreign_milestone = ProjectMilestoneModel(
        id=str(uuid.uuid4()),
        project_instance_id=other_project_id,
        title="Foreign Milestone",
        description="",
        gate_code="M1",
        status="UPCOMING",
        progress_percent=0,
        deliverables=[],
        section_order=1,
    )
    mock_milestone_repo = AsyncMock()
    mock_milestone_repo.get_by_id.return_value = foreign_milestone

    service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=AsyncMock(),
        blueprint_repo=AsyncMock(),
        milestone_repo=mock_milestone_repo,
        task_repo=AsyncMock(),
        risk_repo=AsyncMock(),
        document_repo=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    with pytest.raises(NotFoundException) as exc_info:
        await service.get_milestone(project_a.id, foreign_milestone.id, student_a)
    assert exc_info.value.code == "MILESTONE_NOT_FOUND"


@pytest.mark.asyncio
async def test_nested_risk_mismatch_returns_404(student_a):
    """Requesting Risk from Project B via Project A's URL yields 404 RISK_NOT_FOUND."""
    project_a = _make_project_model(uuid.uuid4(), student_a.user_id)
    other_project_id = str(uuid.uuid4())

    mock_project_repo = AsyncMock()
    mock_project_repo.get_by_id.return_value = project_a

    foreign_risk = ProjectRiskModel(
        id=str(uuid.uuid4()),
        project_instance_id=other_project_id,
        risk_code="R01",
        title="Foreign Risk",
        description="",
        severity="HIGH",
        probability="LOW",
        impact="BLOCKING",
        status="IDENTIFIED",
    )
    mock_risk_repo = AsyncMock()
    mock_risk_repo.get_by_id.return_value = foreign_risk

    service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=AsyncMock(),
        blueprint_repo=AsyncMock(),
        milestone_repo=AsyncMock(),
        task_repo=AsyncMock(),
        risk_repo=mock_risk_repo,
        document_repo=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    with pytest.raises(NotFoundException) as exc_info:
        await service.get_risk(project_a.id, foreign_risk.id, student_a)
    assert exc_info.value.code == "RISK_NOT_FOUND"


@pytest.mark.asyncio
async def test_nested_document_mismatch_returns_404(student_a):
    """Requesting Document from Project B via Project A's URL yields 404 DOCUMENT_NOT_FOUND."""
    project_a = _make_project_model(uuid.uuid4(), student_a.user_id)
    other_project_id = str(uuid.uuid4())

    mock_project_repo = AsyncMock()
    mock_project_repo.get_by_id.return_value = project_a

    foreign_doc = ProjectDocumentModel(
        id=str(uuid.uuid4()),
        project_instance_id=other_project_id,
        document_key="foreign_doc",
        title="Foreign Doc",
        doc_type="ARCHITECTURE",
        format="MARKDOWN",
        content="",
        version="1.0",
        status="PUBLISHED",
        source="SYSTEM",
    )
    mock_doc_repo = AsyncMock()
    mock_doc_repo.get_by_id.return_value = foreign_doc

    service = ExecutionService(
        project_repo=mock_project_repo,
        group_repo=AsyncMock(),
        blueprint_repo=AsyncMock(),
        milestone_repo=AsyncMock(),
        task_repo=AsyncMock(),
        risk_repo=AsyncMock(),
        document_repo=mock_doc_repo,
        outbox_service=AsyncMock(),
    )

    with pytest.raises(NotFoundException) as exc_info:
        await service.get_document(project_a.id, foreign_doc.id, student_a)
    assert exc_info.value.code == "DOCUMENT_NOT_FOUND"


# ============================================================================
# 8. NONEXISTENT RESOURCE CONTRACTS (404)
# ============================================================================

def test_nonexistent_project_returns_404(client: TestClient, app, student_a):
    """Nonexistent project yields 404 PROJECT_NOT_FOUND."""
    mock_project_service = AsyncMock(spec=ProjectService)
    mock_project_service.get_project.side_effect = NotFoundException(
        "Project not found.", code="PROJECT_NOT_FOUND"
    )
    app.dependency_overrides[get_project_service] = lambda: mock_project_service
    app.dependency_overrides[get_current_user] = lambda: student_a

    res = client.get(f"/api/v1/projects/{uuid.uuid4()}")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "PROJECT_NOT_FOUND"


def test_nonexistent_group_returns_404(client: TestClient, app, mentor_a):
    """Nonexistent group yields 404 GROUP_NOT_FOUND."""
    mock_group_service = AsyncMock(spec=GroupService)
    mock_group_service.get_group.side_effect = NotFoundException(
        "Group not found.", code="GROUP_NOT_FOUND"
    )
    app.dependency_overrides[get_group_service] = lambda: mock_group_service
    app.dependency_overrides[get_current_user] = lambda: mentor_a

    res = client.get(f"/api/v1/groups/{uuid.uuid4()}")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "GROUP_NOT_FOUND"


# ============================================================================
# 9. ADMIN GOVERNANCE BOUNDARIES (200)
# ============================================================================

def test_admin_governance_access_and_cross_visibility(client: TestClient, app, admin_user):
    """Authorized Admin retains access to governance endpoints and cross-resource reads."""
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_admin_service = AsyncMock(spec=AdminService)
    mock_admin_service.get_overview_metrics.return_value = MagicMock(model_dump=lambda: {"total_users": 10})
    mock_admin_service.get_system_health.return_value = MagicMock(model_dump=lambda: {"status": "HEALTHY"})
    mock_admin_service.list_mentors.return_value = []
    mock_admin_service.list_students.return_value = []
    app.dependency_overrides[get_admin_service] = lambda: mock_admin_service

    # Admin overview
    res = client.get("/api/v1/admin/overview")
    assert res.status_code == 200

    # Admin health (AD19)
    res = client.get("/api/v1/admin/health")
    assert res.status_code == 200

    # Admin mentors
    res = client.get("/api/v1/admin/mentors")
    assert res.status_code == 200

    # Admin students
    res = client.get("/api/v1/admin/students")
    assert res.status_code == 200
