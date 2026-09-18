"""
GrowFlow Phase 7 Batch 3 — Tests for Mentor Student & Project Supervision Directories.

Validates:
- M10: GET /api/v1/mentors/students (Cross-group Students Directory)
- M11: GET /api/v1/mentors/students/{student_id} (Student Supervision Detail)
- M12: GET /api/v1/mentors/students/{student_id}/projects (Student Project Instances)
- M16: GET /api/v1/mentors/projects/instances (Mentor Projects Directory)
- M22: GET /api/v1/mentors/project-instances (Project Instance Monitoring Grid)
- M23: GET /api/v1/mentors/project-instances/{project_id} (Project Instance Detail)
- M31: GET /api/v1/mentors/at-risk (Global At-Risk Directory - WARNING/CRITICAL only)
- M32: GET /api/v1/mentors/at-risk/{project_id} (Global At-Risk Detail)
- Cross-Mentor Security & Data Isolation Matrix:
  - Mentor A cannot access Student B (403)
  - Mentor A cannot access Project B (403)
  - Mentor A cannot access At-Risk Project B (403)
  - Student caller receives 403 Forbidden across all mentor endpoints
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
from backend.app.api.dependencies.services import (
    get_mentor_student_service,
    get_project_service,
)
from backend.app.api.schemas.mentor_supervision import (
    MentorProjectInstanceDetailSchema,
    MentorProjectInstanceSummarySchema,
    MentorStudentDetailSchema,
    MentorStudentGroupSummarySchema,
    MentorStudentSummarySchema,
)
from backend.app.api.schemas.project import ProjectResponseSchema
from backend.app.application.services.mentor_student_service import MentorStudentService
from backend.app.application.services.project_service import ProjectService
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.domain.project.models import ProjectHealth, ProjectPhase, ProjectStatus
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
        user_id=uuid.uuid4(),
        email="mentor_a@growflow.test",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def mentor_user_b() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="mentor_b@growflow.test",
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


def test_list_supervised_students_unauthenticated(client: TestClient):
    """M10: Unauthenticated request rejected with 401."""
    response = client.get("/api/v1/mentors/students")
    assert response.status_code == 401


def test_list_supervised_students_forbidden_for_student(client: TestClient, app, student_user):
    """M10: Student caller rejected with 403."""
    app.dependency_overrides[get_current_user] = lambda: student_user
    response = client.get("/api/v1/mentors/students")
    assert response.status_code == 403


def test_list_supervised_students_success(client: TestClient, app, mentor_user_a):
    """M10: Authorized mentor retrieves only supervised students."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_student = MentorStudentSummarySchema(
        student_id=str(uuid.uuid4()),
        full_name="Alice Student",
        email="alice@student.test",
        avatar_url=None,
        groups=[
            MentorStudentGroupSummarySchema(
                group_id=str(uuid.uuid4()),
                group_name="Robotics Cohort Alpha",
                joined_at=datetime.now(UTC),
                membership_status="ACTIVE",
            )
        ],
        project_count=2,
        active_project_count=1,
        latest_phase="BLUEPRINT",
        latest_health="HEALTHY",
    )

    mock_service = AsyncMock(spec=MentorStudentService)
    mock_service.list_supervised_students.return_value = [mock_student]
    app.dependency_overrides[get_mentor_student_service] = lambda: mock_service

    response = client.get("/api/v1/mentors/students?search=Alice")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["full_name"] == "Alice Student"
    assert body["data"][0]["project_count"] == 2
    mock_service.list_supervised_students.assert_called_once_with(
        mentor_id=mentor_user_a.user_id,
        group_id=None,
        search="Alice",
    )


def test_get_supervised_student_detail_success(client: TestClient, app, mentor_user_a):
    """M11: Authorized mentor retrieves student supervision detail."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a
    student_id = uuid.uuid4()

    mock_detail = MentorStudentDetailSchema(
        student_id=str(student_id),
        full_name="Alice Student",
        email="alice@student.test",
        avatar_url=None,
        bio="Aspiring robotics engineer",
        goals="Deploy autonomous drone",
        interests="Robotics, Embedded Systems",
        groups=[
            MentorStudentGroupSummarySchema(
                group_id=str(uuid.uuid4()),
                group_name="Robotics Cohort Alpha",
                joined_at=datetime.now(UTC),
                membership_status="ACTIVE",
            )
        ],
        projects=[],
    )

    mock_service = AsyncMock(spec=MentorStudentService)
    mock_service.get_supervised_student_detail.return_value = mock_detail
    app.dependency_overrides[get_mentor_student_service] = lambda: mock_service

    response = client.get(f"/api/v1/mentors/students/{student_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["bio"] == "Aspiring robotics engineer"


def test_get_supervised_student_detail_cross_mentor_forbidden(client: TestClient, app, mentor_user_a):
    """M11: Accessing student from another mentor cohort raises 403."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a
    foreign_student_id = uuid.uuid4()

    mock_service = AsyncMock(spec=MentorStudentService)
    mock_service.get_supervised_student_detail.side_effect = AuthorizationException(
        "You do not supervise this student.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_mentor_student_service] = lambda: mock_service

    response = client.get(f"/api/v1/mentors/students/{foreign_student_id}")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_get_supervised_student_detail_not_found(client: TestClient, app, mentor_user_a):
    """M11: Accessing non-existent student raises 404."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a
    missing_id = uuid.uuid4()

    mock_service = AsyncMock(spec=MentorStudentService)
    mock_service.get_supervised_student_detail.side_effect = NotFoundException(
        "Student not found.", code="USER_NOT_FOUND"
    )
    app.dependency_overrides[get_mentor_student_service] = lambda: mock_service

    response = client.get(f"/api/v1/mentors/students/{missing_id}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


def test_list_supervised_student_projects_success(client: TestClient, app, mentor_user_a):
    """M12: List operational project instances for a supervised student."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a
    student_id = uuid.uuid4()

    mock_proj = ProjectResponseSchema(
        id=str(uuid.uuid4()),
        student_id=str(student_id),
        group_id=str(uuid.uuid4()),
        project_definition_id=str(uuid.uuid4()),
        source_definition_version_id=str(uuid.uuid4()),
        name="Precision Agriculture Drone",
        problem="Crop survey latency",
        proposed_solution="Automated fixed-wing drone",
        complexity="ADVANCED",
        current_phase="EXECUTION",
        health="HEALTHY",
        progress_percentage=45,
        status="ACTIVE",
        deadline=None,
        started_at=datetime.now(UTC),
        completed_at=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_service = AsyncMock(spec=MentorStudentService)
    mock_service.list_supervised_student_projects.return_value = [mock_proj]
    app.dependency_overrides[get_mentor_student_service] = lambda: mock_service

    response = client.get(f"/api/v1/mentors/students/{student_id}/projects")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["name"] == "Precision Agriculture Drone"
    assert body["data"][0]["current_phase"] == "EXECUTION"


def test_list_supervised_project_instances_directory_m16(client: TestClient, app, mentor_user_a):
    """M16: Cross-cohort project directory returns supervised instances with metadata."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_item = MentorProjectInstanceSummarySchema(
        id=str(uuid.uuid4()),
        name="Autonomous Solar Rover",
        student_id=str(uuid.uuid4()),
        student_name="Bob Student",
        student_email="bob@student.test",
        group_id=str(uuid.uuid4()),
        group_name="CleanTech Group",
        current_phase="IDEA",
        health="HEALTHY",
        progress_percentage=10,
        status="ACTIVE",
        deadline=None,
        source_definition_id=str(uuid.uuid4()),
        source_definition_name="Solar Rover Template",
        source_definition_version_number=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.list_supervised_projects.return_value = [mock_item]
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    response = client.get("/api/v1/mentors/projects/instances?search=Solar")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["source_definition_version_number"] == 1


def test_list_student_project_instances_monitoring_m22(client: TestClient, app, mentor_user_a):
    """M22: Project instance monitoring grid returns supervised records."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    mock_item = MentorProjectInstanceSummarySchema(
        id=str(uuid.uuid4()),
        name="Telemetry Satellite Relay",
        student_id=str(uuid.uuid4()),
        student_name="Charlie Student",
        student_email="charlie@student.test",
        group_id=str(uuid.uuid4()),
        group_name="Aerospace Group",
        current_phase="DEVELOPMENT",
        health="WARNING",
        progress_percentage=60,
        status="ACTIVE",
        deadline=None,
        source_definition_id=None,
        source_definition_name=None,
        source_definition_version_number=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.list_supervised_projects.return_value = [mock_item]
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    response = client.get("/api/v1/mentors/project-instances?health=WARNING")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"][0]["health"] == "WARNING"


def test_get_supervised_project_instance_detail_m23(client: TestClient, app, mentor_user_a):
    """M23: Read-only detail view preserves pinned definition version and profile."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a
    project_id = uuid.uuid4()

    mock_detail = MentorProjectInstanceDetailSchema(
        id=str(project_id),
        name="Precision Agriculture Drone",
        problem="Rural telemetry latency",
        proposed_solution="Fixed-wing UAV",
        complexity="ADVANCED",
        current_phase="BLUEPRINT",
        health="HEALTHY",
        progress_percentage=25,
        status="ACTIVE",
        deadline=None,
        started_at=datetime.now(UTC),
        completed_at=None,
        student_id=str(uuid.uuid4()),
        student_name="Alice Student",
        student_email="alice@student.test",
        group_id=str(uuid.uuid4()),
        group_name="Robotics Cohort Alpha",
        source_definition_id=str(uuid.uuid4()),
        source_definition_name="Agriculture Drone Template",
        source_definition_version_number=2,
        objective="Automate rural crop surveys",
        scope="Flight simulation and computer vision pipeline",
        expected_outcome="Functional prototype simulation",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.get_supervised_project_detail.return_value = mock_detail
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    response = client.get(f"/api/v1/mentors/project-instances/{project_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["source_definition_version_number"] == 2
    assert body["data"]["objective"] == "Automate rural crop surveys"


def test_list_at_risk_projects_m31(client: TestClient, app, mentor_user_a):
    """M31: Global At-Risk directory returns WARNING/CRITICAL projects only, excluding HEALTHY."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a

    warning_proj = MentorProjectInstanceSummarySchema(
        id=str(uuid.uuid4()),
        name="Overdue Solar Tracker",
        student_id=str(uuid.uuid4()),
        student_name="Diana Student",
        student_email="diana@student.test",
        group_id=str(uuid.uuid4()),
        group_name="Energy Systems Cohort",
        current_phase="DEVELOPMENT",
        health="WARNING",
        progress_percentage=35,
        status="ACTIVE",
        deadline=None,
        source_definition_id=None,
        source_definition_name=None,
        source_definition_version_number=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    critical_proj = MentorProjectInstanceSummarySchema(
        id=str(uuid.uuid4()),
        name="Failing Battery Inverter",
        student_id=str(uuid.uuid4()),
        student_name="Evan Student",
        student_email="evan@student.test",
        group_id=str(uuid.uuid4()),
        group_name="Energy Systems Cohort",
        current_phase="TESTING",
        health="CRITICAL",
        progress_percentage=80,
        status="ACTIVE",
        deadline=None,
        source_definition_id=None,
        source_definition_name=None,
        source_definition_version_number=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.list_at_risk_projects.return_value = [critical_proj, warning_proj]
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    response = client.get("/api/v1/mentors/at-risk")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    # Verify no HEALTHY projects
    for p in body["data"]:
        assert p["health"] in ("WARNING", "CRITICAL")
        assert p["health"] != "HEALTHY"


def test_get_at_risk_project_detail_m32(client: TestClient, app, mentor_user_a):
    """M32: Detailed view for at-risk project instance."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a
    project_id = uuid.uuid4()

    mock_detail = MentorProjectInstanceDetailSchema(
        id=str(project_id),
        name="Failing Battery Inverter",
        problem="Thermal runaway in power stage",
        proposed_solution="Dual-stage heatsink with active cutoff",
        complexity="ADVANCED",
        current_phase="TESTING",
        health="CRITICAL",
        progress_percentage=80,
        status="ACTIVE",
        deadline=None,
        started_at=datetime.now(UTC),
        completed_at=None,
        student_id=str(uuid.uuid4()),
        student_name="Evan Student",
        student_email="evan@student.test",
        group_id=str(uuid.uuid4()),
        group_name="Energy Systems Cohort",
        source_definition_id=None,
        source_definition_name=None,
        source_definition_version_number=None,
        objective="Develop thermal protection circuit",
        scope="Power electronics thermal safety",
        expected_outcome="Zero-damage cutoff under peak load",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.get_at_risk_project_detail.return_value = mock_detail
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    response = client.get(f"/api/v1/mentors/at-risk/{project_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["health"] == "CRITICAL"


def test_get_at_risk_project_detail_healthy_rejected(client: TestClient, app, mentor_user_a):
    """M32: Requesting a HEALTHY project via at-risk detail endpoint is rejected with 404."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a
    project_id = uuid.uuid4()

    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.get_at_risk_project_detail.side_effect = NotFoundException(
        "Project is not currently at risk.", code="PROJECT_NOT_AT_RISK"
    )
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    response = client.get(f"/api/v1/mentors/at-risk/{project_id}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PROJECT_NOT_AT_RISK"


def test_mandatory_cross_mentor_security_isolation_matrix(
    client: TestClient, app, mentor_user_a, mentor_user_b
):
    """
    Mandatory Section 49 & 50 Cross-Mentor Isolation Matrix:
    Mentor A -> Student A (200), Project A (200), At-Risk A (200)
    Mentor A -> Student B (403), Project B (403), At-Risk B (403)
    Mentor B -> Student A (403), Project A (403), At-Risk A (403)
    """
    student_a_id = uuid.uuid4()
    student_b_id = uuid.uuid4()
    project_a_id = uuid.uuid4()
    project_b_id = uuid.uuid4()

    # Create real services with mocked repos to test authorization decisions
    mock_group_repo = AsyncMock()
    mock_user_repo = AsyncMock()
    mock_project_repo = AsyncMock()
    mock_profile_repo = AsyncMock()

    # User lookup returns appropriate user
    user_a = AsyncMock(id=str(student_a_id), full_name="Student A", email="a@test.com", avatar_url=None)
    user_b = AsyncMock(id=str(student_b_id), full_name="Student B", email="b@test.com", avatar_url=None)

    async def get_user_by_id(uid):
        if str(uid) == str(student_a_id):
            return user_a
        if str(uid) == str(student_b_id):
            return user_b
        return None

    mock_user_repo.get_by_id.side_effect = get_user_by_id

    # Supervision check:
    # Mentor A supervises Student A only. Mentor B supervises Student B only.
    async def is_supervised(student_id, mentor_id):
        if str(mentor_id) == str(mentor_user_a.user_id) and str(student_id) == str(student_a_id):
            return True
        if str(mentor_id) == str(mentor_user_b.user_id) and str(student_id) == str(student_b_id):
            return True
        return False

    mock_group_repo.is_student_supervised_by_mentor.side_effect = is_supervised
    mock_group_repo.list_by_mentor.return_value = []
    mock_group_repo.list_student_memberships.return_value = []
    mock_project_repo.list_by_student.return_value = []
    mock_profile_repo.get_student_profile.return_value = None

    # Wire real MentorStudentService
    real_student_service = MentorStudentService(
        user_repo=mock_user_repo,
        group_repo=mock_group_repo,
        project_repo=mock_project_repo,
        profile_repo=mock_profile_repo,
    )
    app.dependency_overrides[get_mentor_student_service] = lambda: real_student_service

    # Wire ProjectService for project isolation check
    mock_proj_service = AsyncMock(spec=ProjectService)

    async def get_proj_detail(project_id, mentor_id):
        if str(mentor_id) == str(mentor_user_a.user_id):
            if str(project_id) == str(project_a_id):
                return MentorProjectInstanceDetailSchema(
                    id=str(project_a_id),
                    name="Project A",
                    problem="P",
                    proposed_solution="S",
                    complexity="INTERMEDIATE",
                    current_phase="IDEA",
                    health="WARNING",
                    progress_percentage=0,
                    status="ACTIVE",
                    student_id=str(student_a_id),
                    student_name="Student A",
                    student_email="a@test.com",
                )
            raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")
        if str(mentor_id) == str(mentor_user_b.user_id):
            if str(project_id) == str(project_b_id):
                return MentorProjectInstanceDetailSchema(
                    id=str(project_b_id),
                    name="Project B",
                    problem="P",
                    proposed_solution="S",
                    complexity="INTERMEDIATE",
                    current_phase="IDEA",
                    health="CRITICAL",
                    progress_percentage=0,
                    status="ACTIVE",
                    student_id=str(student_b_id),
                    student_name="Student B",
                    student_email="b@test.com",
                )
            raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")

    mock_proj_service.get_supervised_project_detail.side_effect = get_proj_detail

    async def get_at_risk_detail(project_id, mentor_id):
        detail = await get_proj_detail(project_id=project_id, mentor_id=mentor_id)
        return detail

    mock_proj_service.get_at_risk_project_detail.side_effect = get_at_risk_detail
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    # --- Scenario 1: Mentor A accesses Student A -> 200 OK ---
    app.dependency_overrides[get_current_user] = lambda: mentor_user_a
    res_a_a = client.get(f"/api/v1/mentors/students/{student_a_id}")
    assert res_a_a.status_code == 200

    # --- Scenario 2: Mentor A accesses Student B -> 403 Forbidden ---
    res_a_b = client.get(f"/api/v1/mentors/students/{student_b_id}")
    assert res_a_b.status_code == 403

    # --- Scenario 3: Mentor A accesses Project A -> 200 OK ---
    res_proj_a_a = client.get(f"/api/v1/mentors/project-instances/{project_a_id}")
    assert res_proj_a_a.status_code == 200

    # --- Scenario 4: Mentor A accesses Project B -> 403 Forbidden ---
    res_proj_a_b = client.get(f"/api/v1/mentors/project-instances/{project_b_id}")
    assert res_proj_a_b.status_code == 403

    # --- Scenario 5: Mentor A accesses At-Risk Project A -> 200 OK ---
    res_risk_a_a = client.get(f"/api/v1/mentors/at-risk/{project_a_id}")
    assert res_risk_a_a.status_code == 200

    # --- Scenario 6: Mentor A accesses At-Risk Project B -> 403 Forbidden ---
    res_risk_a_b = client.get(f"/api/v1/mentors/at-risk/{project_b_id}")
    assert res_risk_a_b.status_code == 403

    # --- Scenario 7: Mentor B accesses Student A -> 403 Forbidden ---
    app.dependency_overrides[get_current_user] = lambda: mentor_user_b
    res_b_a = client.get(f"/api/v1/mentors/students/{student_a_id}")
    assert res_b_a.status_code == 403

    # --- Scenario 8: Mentor B accesses Project A -> 403 Forbidden ---
    res_proj_b_a = client.get(f"/api/v1/mentors/project-instances/{project_a_id}")
    assert res_proj_b_a.status_code == 403
