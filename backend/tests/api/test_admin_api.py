"""
GrowFlow Phase 7 Batch 7 Part 1 — Tests for Admin Governance APIs.

Validates:
- GET /api/v1/admin/overview:
  - 401 Unauthenticated
  - 403 Forbidden for Student role
  - 403 Forbidden for Mentor role
  - 200 OK for Admin role
- GET /api/v1/admin/mentors:
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role
- GET /api/v1/admin/mentors/{mentor_id}:
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role with mentor detail
  - 404 Not Found for non-existent mentor
- GET /api/v1/admin/students:
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role
- GET /api/v1/admin/students/{student_id}:
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role with student detail
  - 404 Not Found for non-existent student
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from unittest.mock import AsyncMock
import uuid

from fastapi.testclient import TestClient
import pytest

from backend.app.api.dependencies.auth import get_current_user
from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import get_admin_service
from backend.app.api.schemas.admin import (
    AdminCohortSummarySchema,
    AdminMentorDetailSchema,
    AdminMentorSummarySchema,
    AdminOverviewResponseSchema,
    AdminStudentDetailSchema,
    AdminStudentMembershipSchema,
    AdminStudentProjectSchema,
    AdminStudentSummarySchema,
    AdminStudentTechnologySchema,
    AdminSupervisedStudentSchema,
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
# AD01 — Overview Tests
# ---------------------------------------------------------------------------


def test_admin_overview_unauthenticated(client: TestClient):
    """GET /api/v1/admin/overview returns 401 when token is missing."""
    res = client.get("/api/v1/admin/overview")
    assert res.status_code == 401
    body = res.json()
    assert body["success"] is False


def test_admin_overview_forbidden_student(client: TestClient, app, student_user: CurrentUser):
    """GET /api/v1/admin/overview returns 403 Forbidden for Student account."""
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/overview")
    assert res.status_code == 403
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "AUTH_FORBIDDEN_ROLE"


def test_admin_overview_forbidden_mentor(client: TestClient, app, mentor_user: CurrentUser):
    """GET /api/v1/admin/overview returns 403 Forbidden for Mentor account."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/overview")
    assert res.status_code == 403
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "AUTH_FORBIDDEN_ROLE"


def test_admin_overview_success(client: TestClient, app, admin_user: CurrentUser):
    """GET /api/v1/admin/overview returns 200 OK with truthful metrics for Admin."""
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_overview_metrics.return_value = AdminOverviewResponseSchema(
        total_mentors=12,
        active_mentors=10,
        total_students=145,
        active_students=120,
        total_groups=8,
        active_groups=6,
        total_projects=180,
        active_projects=45,
        completed_projects=130,
        at_risk_projects=5,
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/overview")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["total_mentors"] == 12
    assert data["active_mentors"] == 10
    assert data["total_students"] == 145
    assert data["at_risk_projects"] == 5


# ---------------------------------------------------------------------------
# AD02 — Mentor Directory Tests
# ---------------------------------------------------------------------------


def test_list_mentors_unauthenticated(client: TestClient):
    """GET /api/v1/admin/mentors returns 401 when token is missing."""
    res = client.get("/api/v1/admin/mentors")
    assert res.status_code == 401


def test_list_mentors_forbidden_student(client: TestClient, app, student_user: CurrentUser):
    """GET /api/v1/admin/mentors returns 403 for Student."""
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/mentors")
    assert res.status_code == 403


def test_list_mentors_forbidden_mentor(client: TestClient, app, mentor_user: CurrentUser):
    """GET /api/v1/admin/mentors returns 403 for Mentor."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/mentors")
    assert res.status_code == 403


def test_list_mentors_success(client: TestClient, app, admin_user: CurrentUser):
    """GET /api/v1/admin/mentors returns 200 with mentor list for Admin."""
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = AsyncMock(spec=AdminService)
    mentor_id = uuid.uuid4()
    mock_service.list_mentors.return_value = [
        AdminMentorSummarySchema(
            id=str(mentor_id),
            email="dr.smith@growflow.test",
            full_name="Dr. Jane Smith",
            role="MENTOR",
            status="ACTIVE",
            avatar_url=None,
            mentor_id="MNT-001",
            designation="Principal Architect",
            organization="Tech Labs",
            specialization="Distributed Systems",
            group_count=2,
            student_count=18,
            project_count=12,
            last_login_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
        )
    ]
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/mentors?search=Jane&status=ACTIVE")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["full_name"] == "Dr. Jane Smith"
    assert body["data"][0]["student_count"] == 18


# ---------------------------------------------------------------------------
# AD03 — Mentor Detail Tests
# ---------------------------------------------------------------------------


def test_get_mentor_detail_success(client: TestClient, app, admin_user: CurrentUser):
    """GET /api/v1/admin/mentors/{mentor_id} returns 200 with detail."""
    app.dependency_overrides[get_current_user] = lambda: admin_user
    mentor_id = uuid.uuid4()

    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_mentor_detail.return_value = AdminMentorDetailSchema(
        id=str(mentor_id),
        email="mentor.detail@growflow.test",
        full_name="Prof. Alan Turing",
        role="MENTOR",
        status="ACTIVE",
        avatar_url=None,
        mentor_id="MNT-100",
        designation="Professor",
        organization="Cambridge",
        bio="Pioneer of computing",
        specialization="Theoretical CS",
        skills=["Algorithms", "Complexity"],
        max_students=20,
        is_accepting_students=True,
        last_login_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        groups=[
            AdminCohortSummarySchema(
                id=str(uuid.uuid4()),
                name="Cohort Alpha",
                join_code="ALPHA12",
                status="ACTIVE",
                student_count=10,
                project_count=8,
                created_at=datetime.now(UTC),
            )
        ],
        supervised_students=[
            AdminSupervisedStudentSchema(
                id=str(uuid.uuid4()),
                full_name="Ada Lovelace",
                email="ada@growflow.test",
                group_name="Cohort Alpha",
                active_projects_count=1,
            )
        ],
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get(f"/api/v1/admin/mentors/{mentor_id}")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["full_name"] == "Prof. Alan Turing"
    assert len(body["data"]["groups"]) == 1
    assert len(body["data"]["supervised_students"]) == 1


def test_get_mentor_detail_not_found(client: TestClient, app, admin_user: CurrentUser):
    """GET /api/v1/admin/mentors/{mentor_id} returns 404 when mentor not found."""
    app.dependency_overrides[get_current_user] = lambda: admin_user
    mentor_id = uuid.uuid4()

    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_mentor_detail.side_effect = NotFoundException(
        "Mentor not found.",
        code="MENTOR_NOT_FOUND",
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get(f"/api/v1/admin/mentors/{mentor_id}")
    assert res.status_code == 404
    body = res.json()
    assert body["success"] is False


# ---------------------------------------------------------------------------
# AD04 — Student Directory Tests
# ---------------------------------------------------------------------------


def test_list_students_unauthenticated(client: TestClient):
    """GET /api/v1/admin/students returns 401 when token is missing."""
    res = client.get("/api/v1/admin/students")
    assert res.status_code == 401


def test_list_students_forbidden_student(client: TestClient, app, student_user: CurrentUser):
    """GET /api/v1/admin/students returns 403 for Student."""
    app.dependency_overrides[get_current_user] = lambda: student_user
    res = client.get("/api/v1/admin/students")
    assert res.status_code == 403


def test_list_students_forbidden_mentor(client: TestClient, app, mentor_user: CurrentUser):
    """GET /api/v1/admin/students returns 403 for Mentor."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    res = client.get("/api/v1/admin/students")
    assert res.status_code == 403


def test_list_students_success(client: TestClient, app, admin_user: CurrentUser):
    """GET /api/v1/admin/students returns 200 with student list for Admin."""
    app.dependency_overrides[get_current_user] = lambda: admin_user

    mock_service = AsyncMock(spec=AdminService)
    student_id = uuid.uuid4()
    mock_service.list_students.return_value = [
        AdminStudentSummarySchema(
            id=str(student_id),
            email="alex@growflow.test",
            full_name="Alex Rivera",
            role="STUDENT",
            status="ACTIVE",
            avatar_url=None,
            student_id="STU-2026-001",
            college="MIT",
            branch="Computer Science",
            year_of_study=3,
            primary_track="Full-Stack Web Development",
            group_count=1,
            project_count=2,
            active_project_count=1,
            at_risk_project_count=0,
            last_login_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
        )
    ]
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get("/api/v1/admin/students?track=Full-Stack")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["full_name"] == "Alex Rivera"
    assert body["data"][0]["college"] == "MIT"


# ---------------------------------------------------------------------------
# AD05 — Student Detail Tests
# ---------------------------------------------------------------------------


def test_get_student_detail_success(client: TestClient, app, admin_user: CurrentUser):
    """GET /api/v1/admin/students/{student_id} returns 200 with detail."""
    app.dependency_overrides[get_current_user] = lambda: admin_user
    student_id = uuid.uuid4()

    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_student_detail.return_value = AdminStudentDetailSchema(
        id=str(student_id),
        email="alex@growflow.test",
        full_name="Alex Rivera",
        role="STUDENT",
        status="ACTIVE",
        avatar_url=None,
        student_id="STU-2026-001",
        college="MIT",
        branch="Computer Science",
        year_of_study=3,
        bio="Aspiring systems engineer",
        primary_track="Full-Stack Web Development",
        technologies=[
            AdminStudentTechnologySchema(
                technology_id=str(uuid.uuid4()),
                technology_name="Python",
                proficiency_level="ADVANCED",
            )
        ],
        last_login_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        groups=[
            AdminStudentMembershipSchema(
                group_id=str(uuid.uuid4()),
                group_name="Web Cohort 2026",
                mentor_name="Dr. Smith",
                status="ACTIVE",
                joined_at=datetime.now(UTC),
            )
        ],
        projects=[
            AdminStudentProjectSchema(
                id=str(uuid.uuid4()),
                name="GrowFlow Telemetry Engine",
                track="Full-Stack",
                current_phase="IMPLEMENTATION",
                health="HEALTHY",
                progress_percentage=65,
                status="ACTIVE",
                group_name="Web Cohort 2026",
                created_at=datetime.now(UTC),
            )
        ],
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get(f"/api/v1/admin/students/{student_id}")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["full_name"] == "Alex Rivera"
    assert len(body["data"]["technologies"]) == 1
    assert body["data"]["technologies"][0]["technology_name"] == "Python"
    assert len(body["data"]["projects"]) == 1
    assert body["data"]["projects"][0]["health"] == "HEALTHY"


def test_get_student_detail_not_found(client: TestClient, app, admin_user: CurrentUser):
    """GET /api/v1/admin/students/{student_id} returns 404 when student not found."""
    app.dependency_overrides[get_current_user] = lambda: admin_user
    student_id = uuid.uuid4()

    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_student_detail.side_effect = NotFoundException(
        "Student not found.",
        code="STUDENT_NOT_FOUND",
    )
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    res = client.get(f"/api/v1/admin/students/{student_id}")
    assert res.status_code == 404
    body = res.json()
    assert body["success"] is False
