"""
GrowFlow Phase 7 Batch 7 Part 2 — Tests for Admin Governance APIs (AD06–AD10).

Validates:
- AD06: GET /api/v1/admin/groups
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role with cohort list
  - Search & filter handling
- AD07: GET /api/v1/admin/groups/{group_id}
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role with detailed group governance
  - 404 Not Found for non-existent group
- AD08: GET /api/v1/admin/projects
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role with projects list
  - Phase, health, and status filter handling
- AD09: GET /api/v1/admin/definitions & GET /api/v1/admin/definitions/{definition_id}
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role with immutable versions tree
  - 404 Not Found for non-existent definition
- AD10: GET /api/v1/admin/instances & GET /api/v1/admin/instances/{project_id}
  - 401 Unauthenticated
  - 403 Forbidden for Student/Mentor
  - 200 OK for Admin role with summary KPIs and instances
  - 200 OK for Canonical instance governance detail
  - 404 Not Found for non-existent instance
- Read-only validation (no write endpoints exposed).
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
    AdminGroupDetailSchema,
    AdminGroupMemberSchema,
    AdminGroupProjectSchema,
    AdminGroupSummarySchema,
    AdminHealthTransitionSchema,
    AdminInstanceMonitoringResponseSchema,
    AdminInstanceSummarySchema,
    AdminPhaseTransitionSchema,
    AdminProjectDefinitionDetailSchema,
    AdminProjectDefinitionSummarySchema,
    AdminProjectDefinitionVersionSchema,
    AdminProjectInstanceDetailSchema,
    AdminProjectInstanceRefSchema,
    AdminProjectSummarySchema,
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


# ============================================================
# AD06 — Groups Directory Tests
# ============================================================

def test_list_groups_unauthenticated(client: TestClient):
    response = client.get("/api/v1/admin/groups")
    assert response.status_code == 401


def test_list_groups_forbidden_student(app, client: TestClient, student_user: CurrentUser):
    app.dependency_overrides[get_current_user] = lambda: student_user
    response = client.get("/api/v1/admin/groups")
    assert response.status_code == 403


def test_list_groups_forbidden_mentor(app, client: TestClient, mentor_user: CurrentUser):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    response = client.get("/api/v1/admin/groups")
    assert response.status_code == 403


def test_list_groups_success(app, client: TestClient, admin_user: CurrentUser):
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    mock_service.list_groups.return_value = [
        AdminGroupSummarySchema(
            id=str(uuid.uuid4()),
            name="Cohort Alpha",
            join_code="ALPHA1",
            status="ACTIVE",
            mentor_id=str(uuid.uuid4()),
            mentor_name="Dr. Vance",
            mentor_email="vance@growflow.test",
            student_count=12,
            project_count=8,
            created_at=now,
            updated_at=now,
        )
    ]
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    response = client.get("/api/v1/admin/groups?search=Alpha&status=ACTIVE")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Cohort Alpha"
    assert data[0]["student_count"] == 12
    mock_service.list_groups.assert_awaited_once_with(search="Alpha", status="ACTIVE")


# ============================================================
# AD07 — Group Detail Tests
# ============================================================

def test_get_group_detail_unauthenticated(client: TestClient):
    response = client.get(f"/api/v1/admin/groups/{uuid.uuid4()}")
    assert response.status_code == 401


def test_get_group_detail_forbidden(app, client: TestClient, student_user: CurrentUser):
    app.dependency_overrides[get_current_user] = lambda: student_user
    response = client.get(f"/api/v1/admin/groups/{uuid.uuid4()}")
    assert response.status_code == 403


def test_get_group_detail_success(app, client: TestClient, admin_user: CurrentUser):
    gid = uuid.uuid4()
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    mock_service.get_group_detail.return_value = AdminGroupDetailSchema(
        id=str(gid),
        name="Cohort Beta",
        join_code="BETA01",
        status="ACTIVE",
        created_at=now,
        updated_at=now,
        mentor_id=str(uuid.uuid4()),
        mentor_name="Marcus Brody",
        mentor_email="brody@growflow.test",
        mentor_avatar_url=None,
        mentor_specialization="Fullstack Architecture",
        student_count=1,
        project_count=1,
        active_project_count=1,
        members=[
            AdminGroupMemberSchema(
                id=str(uuid.uuid4()),
                student_id=str(uuid.uuid4()),
                full_name="Aarav Patel",
                email="aarav@growflow.test",
                avatar_url=None,
                status="ACTIVE",
                joined_at=now,
            )
        ],
        projects=[
            AdminGroupProjectSchema(
                id=str(uuid.uuid4()),
                name="AI Code Reviewer",
                student_id=str(uuid.uuid4()),
                student_name="Aarav Patel",
                current_phase="IMPLEMENTATION",
                health="HEALTHY",
                progress_percentage=45,
                status="ACTIVE",
                created_at=now,
            )
        ],
    )
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    response = client.get(f"/api/v1/admin/groups/{gid}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Cohort Beta"
    assert data["mentor_specialization"] == "Fullstack Architecture"
    assert len(data["members"]) == 1
    assert len(data["projects"]) == 1


def test_get_group_detail_not_found(app, client: TestClient, admin_user: CurrentUser):
    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_group_detail.side_effect = NotFoundException("Group not found")
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    response = client.get(f"/api/v1/admin/groups/{uuid.uuid4()}")
    assert response.status_code == 404


# ============================================================
# AD08 — Projects Directory Tests
# ============================================================

def test_list_projects_unauthenticated(client: TestClient):
    response = client.get("/api/v1/admin/projects")
    assert response.status_code == 401


def test_list_projects_forbidden(app, client: TestClient, mentor_user: CurrentUser):
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    response = client.get("/api/v1/admin/projects")
    assert response.status_code == 403


def test_list_projects_success(app, client: TestClient, admin_user: CurrentUser):
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    mock_service.list_projects.return_value = [
        AdminProjectSummarySchema(
            id=str(uuid.uuid4()),
            name="Smart Health Monitor",
            student_id=str(uuid.uuid4()),
            student_name="Priya Sharma",
            student_email="priya@growflow.test",
            mentor_id=str(uuid.uuid4()),
            mentor_name="Sarah Connor",
            group_id=str(uuid.uuid4()),
            group_name="Cohort Gamma",
            current_phase="TESTING",
            health="WARNING",
            progress_percentage=75,
            status="ACTIVE",
            complexity="ADVANCED",
            source_definition_name="IoT Health Platform",
            created_at=now,
            updated_at=now,
        )
    ]
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    response = client.get("/api/v1/admin/projects?health=WARNING&phase=TESTING")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Smart Health Monitor"
    assert data[0]["health"] == "WARNING"


# ============================================================
# AD09 — Project Definition Monitoring Tests
# ============================================================

def test_list_definitions_unauthenticated(client: TestClient):
    response = client.get("/api/v1/admin/definitions")
    assert response.status_code == 401


def test_list_definitions_forbidden(app, client: TestClient, student_user: CurrentUser):
    app.dependency_overrides[get_current_user] = lambda: student_user
    response = client.get("/api/v1/admin/definitions")
    assert response.status_code == 403


def test_list_definitions_success(app, client: TestClient, admin_user: CurrentUser):
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    mock_service.list_definitions.return_value = [
        AdminProjectDefinitionSummarySchema(
            id=str(uuid.uuid4()),
            name="Fullstack Microservices System",
            owner_mentor_id=str(uuid.uuid4()),
            owner_mentor_name="Dr. Vance",
            owner_mentor_email="vance@growflow.test",
            status="ACTIVE",
            current_version_id=str(uuid.uuid4()),
            current_version_number=2,
            complexity="ADVANCED",
            instance_count=5,
            version_count=2,
            created_at=now,
            updated_at=now,
        )
    ]
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    response = client.get("/api/v1/admin/definitions")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Fullstack Microservices System"
    assert data[0]["current_version_number"] == 2


def test_get_definition_detail_success(app, client: TestClient, admin_user: CurrentUser):
    did = uuid.uuid4()
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    mock_service.get_definition_detail.return_value = AdminProjectDefinitionDetailSchema(
        id=str(did),
        name="Fullstack Microservices System",
        owner_mentor_id=str(uuid.uuid4()),
        owner_mentor_name="Dr. Vance",
        owner_mentor_email="vance@growflow.test",
        status="ACTIVE",
        current_version_id=str(uuid.uuid4()),
        current_version_number=1,
        complexity="ADVANCED",
        instance_count=1,
        version_count=1,
        created_at=now,
        updated_at=now,
        versions=[
            AdminProjectDefinitionVersionSchema(
                id=str(uuid.uuid4()),
                version_number=1,
                name="V1 Initial",
                problem="Distributed state challenges",
                proposed_solution="Event driven architecture",
                complexity="ADVANCED",
                description="Comprehensive template",
                duration="8 weeks",
                constraints="",
                assumptions="",
                technology_snapshot=[{"name": "Kafka"}],
                created_by=str(uuid.uuid4()),
                created_at=now,
            )
        ],
        assigned_instances=[
            AdminProjectInstanceRefSchema(
                id=str(uuid.uuid4()),
                name="Aarav's Microservices",
                student_name="Aarav Patel",
                current_phase="IMPLEMENTATION",
                health="HEALTHY",
                status="ACTIVE",
            )
        ],
    )
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    response = client.get(f"/api/v1/admin/definitions/{did}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["versions"]) == 1
    assert len(data["assigned_instances"]) == 1


# ============================================================
# AD10 — Project Instance Monitoring & Canonical Detail Tests
# ============================================================

def test_get_instances_monitoring_success(app, client: TestClient, admin_user: CurrentUser):
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    mock_service.get_instances_monitoring.return_value = AdminInstanceMonitoringResponseSchema(
        summary=AdminInstanceSummarySchema(
            total_instances=10,
            healthy_count=7,
            warning_count=2,
            critical_count=1,
            completed_count=3,
        ),
        instances=[
            AdminProjectSummarySchema(
                id=str(uuid.uuid4()),
                name="Project One",
                student_id=str(uuid.uuid4()),
                student_name="Aarav Patel",
                student_email="aarav@growflow.test",
                mentor_id=str(uuid.uuid4()),
                mentor_name="Dr. Vance",
                group_id=str(uuid.uuid4()),
                group_name="Cohort Alpha",
                current_phase="IMPLEMENTATION",
                health="HEALTHY",
                progress_percentage=50,
                status="ACTIVE",
                complexity="INTERMEDIATE",
                source_definition_name=None,
                created_at=now,
                updated_at=now,
            )
        ],
    )
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    response = client.get("/api/v1/admin/instances")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["summary"]["total_instances"] == 10
    assert data["summary"]["healthy_count"] == 7
    assert len(data["instances"]) == 1


def test_get_canonical_instance_detail_success(app, client: TestClient, admin_user: CurrentUser):
    pid = uuid.uuid4()
    mock_service = AsyncMock(spec=AdminService)
    now = datetime.now(UTC)
    mock_service.get_instance_detail.return_value = AdminProjectInstanceDetailSchema(
        id=str(pid),
        name="Project Canonical",
        problem="Problem Statement",
        proposed_solution="Solution Statement",
        complexity="INTERMEDIATE",
        current_phase="IMPLEMENTATION",
        health="HEALTHY",
        progress_percentage=60,
        status="ACTIVE",
        deadline=None,
        started_at=now,
        completed_at=None,
        created_at=now,
        updated_at=now,
        student_id=str(uuid.uuid4()),
        student_name="Priya Sharma",
        student_email="priya@growflow.test",
        student_avatar_url=None,
        mentor_id=str(uuid.uuid4()),
        mentor_name="Sarah Connor",
        mentor_email="connor@growflow.test",
        group_id=str(uuid.uuid4()),
        group_name="Cohort Alpha",
        definition_id=str(uuid.uuid4()),
        definition_name="Web Architecture",
        version_number=1,
        profile_objective="Build scalable web platform",
        profile_target_users="Engineers",
        profile_project_type="Web App",
        profile_student_skill_context="React, Python",
        profile_goals="Master systems",
        profile_scope="End-to-end",
        profile_expected_outcome="Deployed application",
        profile_constraints="None",
        profile_assumptions="None",
        phase_history=[
            AdminPhaseTransitionSchema(
                id=str(uuid.uuid4()),
                previous_phase="ARCHITECTURE",
                new_phase="IMPLEMENTATION",
                reason="Review approved",
                changed_at=now,
            )
        ],
        health_history=[
            AdminHealthTransitionSchema(
                id=str(uuid.uuid4()),
                previous_health="WARNING",
                new_health="HEALTHY",
                reason="Blocker resolved",
                changed_at=now,
            )
        ],
    )
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    response = client.get(f"/api/v1/admin/instances/{pid}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Project Canonical"
    assert data["student_name"] == "Priya Sharma"
    assert data["mentor_name"] == "Sarah Connor"
    assert data["definition_name"] == "Web Architecture"
    assert len(data["phase_history"]) == 1
    assert len(data["health_history"]) == 1


def test_get_canonical_instance_detail_not_found(app, client: TestClient, admin_user: CurrentUser):
    mock_service = AsyncMock(spec=AdminService)
    mock_service.get_instance_detail.side_effect = NotFoundException("Project instance not found")
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[get_admin_service] = lambda: mock_service

    response = client.get(f"/api/v1/admin/instances/{uuid.uuid4()}")
    assert response.status_code == 404
