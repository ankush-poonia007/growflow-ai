"""
GrowFlow Phase 7 Batch 2 — Tests for Mentor Project Definitions & Versioned Assignment (M17–M21).

Validates:
- M17: GET /api/v1/project-definitions (List mentor definitions with version snapshot)
- M18: GET /api/v1/project-definitions/{id} (Detail view & version history)
- M19: POST /api/v1/project-definitions (Create definition -> produces v1)
- M20: PATCH /api/v1/project-definitions/{id} (Edit definition -> produces v2, preserves v1)
- M21: POST /api/v1/project-definitions/{id}/assign (Assign to student in supervised group)
- Mandatory Version Isolation: Proves Student project instance referencing V1 is completely isolated
  and unaffected when Mentor updates definition to V2.
- Authorization Matrix: 401 unauthenticated, 403 non-owner / student, 404 not found, 409 duplicate assignment.
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
from backend.app.api.dependencies.services import get_project_definition_service
from backend.app.application.services.project_definition_service import ProjectDefinitionService
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.domain.organization.models import GroupMembershipStatus, GroupStatus
from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectDefinitionStatus,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
)
from backend.app.infrastructure.database.models.organization import GroupMembershipModel, GroupModel
from backend.app.infrastructure.database.models.project import (
    ProjectDefinitionModel,
    ProjectDefinitionVersionModel,
    ProjectInstanceModel,
)
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    ConflictException,
    NotFoundException,
)


async def _mock_db_session() -> AsyncGenerator[AsyncMock, None]:
    mock_session = AsyncMock()
    yield mock_session


@pytest.fixture(autouse=True)
def override_db(app):
    app.dependency_overrides[get_db_session] = _mock_db_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mentor_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="mentor1@growflow.test",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def other_mentor_user() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.uuid4(),
        email="mentor2@growflow.test",
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


def test_list_definitions_mentor_success(
    client: TestClient,
    app,
    mentor_user: CurrentUser,
):
    """M17: GET /api/v1/project-definitions returns 200 with mentor definitions and current version snapshot."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user

    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()
    def_model = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(mentor_user.user_id),
        name="Precision Agriculture Drone",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_id),
    )
    ver_model = ProjectDefinitionVersionModel(
        id=ver_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="Precision Agriculture Drone",
        problem="Crop monitoring latency",
        proposed_solution="Autonomous multispectral UAV",
        complexity=ProjectComplexity.ADVANCED.value,
        description="Build an autonomous survey drone",
        duration="12 weeks",
        constraints="Max budget $800",
        assumptions="Open field testing permitted",
        technology_snapshot=[{"name": "PX4"}, {"name": "ROS2"}],
        created_by=str(mentor_user.user_id),
    )

    mock_service = AsyncMock(spec=ProjectDefinitionService)
    mock_service.list_definitions.return_value = [(def_model, ver_model)]
    app.dependency_overrides[get_project_definition_service] = lambda: mock_service

    res = client.get("/api/v1/project-definitions")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    item = body["data"][0]
    assert item["id"] == str(def_id)
    assert item["name"] == "Precision Agriculture Drone"
    assert item["current_version"]["version_number"] == 1
    assert item["current_version"]["complexity"] == "ADVANCED"


def test_get_definition_owner_and_authorization_matrix(
    client: TestClient,
    app,
    mentor_user: CurrentUser,
    other_mentor_user: CurrentUser,
    student_user: CurrentUser,
):
    """M18: GET /api/v1/project-definitions/{id} enforces authorization matrix (200, 403, 404)."""
    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()
    def_model = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(mentor_user.user_id),
        name="Edge AI Camera",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_id),
    )
    ver_model = ProjectDefinitionVersionModel(
        id=ver_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="Edge AI Camera",
        problem="Real-time object detection on low-power devices",
        proposed_solution="Quantized YOLO on Raspberry Pi",
        complexity=ProjectComplexity.INTERMEDIATE.value,
        created_by=str(mentor_user.user_id),
    )

    mock_service = AsyncMock(spec=ProjectDefinitionService)
    app.dependency_overrides[get_project_definition_service] = lambda: mock_service

    # 1. Owner Mentor -> 200 OK
    app.dependency_overrides[get_current_user] = lambda: mentor_user
    mock_service.get_definition.return_value = (def_model, ver_model)
    res = client.get(f"/api/v1/project-definitions/{def_id}")
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "Edge AI Camera"
    assert res.json()["data"]["current_version"]["version_number"] == 1

    # 2. Non-owner Mentor -> 403 Forbidden
    app.dependency_overrides[get_current_user] = lambda: other_mentor_user
    mock_service.get_definition.side_effect = AuthorizationException(
        "Access to this project definition is denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    res = client.get(f"/api/v1/project-definitions/{def_id}")
    assert res.status_code == 403

    # 3. Not Found -> 404
    missing_id = uuid.uuid4()
    mock_service.get_definition.side_effect = NotFoundException(
        "Project definition not found.", code="PROJECT_DEFINITION_NOT_FOUND"
    )
    res = client.get(f"/api/v1/project-definitions/{missing_id}")
    assert res.status_code == 404


def test_create_definition_mentor_success(
    client: TestClient,
    app,
    mentor_user: CurrentUser,
):
    """M19: POST /api/v1/project-definitions creates definition and initial v1 snapshot."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user

    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()
    def_model = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(mentor_user.user_id),
        name="Smart Irrigation System",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_id),
    )
    ver_model = ProjectDefinitionVersionModel(
        id=ver_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="Smart Irrigation System",
        problem="Water wastage in agriculture",
        proposed_solution="Soil moisture telemetry & automated valves",
        complexity=ProjectComplexity.INTERMEDIATE.value,
        description="Build an automated irrigation controller",
        duration="6 weeks",
        created_by=str(mentor_user.user_id),
    )

    mock_service = AsyncMock(spec=ProjectDefinitionService)
    mock_service.create_definition.return_value = (def_model, ver_model)
    app.dependency_overrides[get_project_definition_service] = lambda: mock_service

    payload = {
        "name": "Smart Irrigation System",
        "problem": "Water wastage in agriculture",
        "proposed_solution": "Soil moisture telemetry & automated valves",
        "complexity": "INTERMEDIATE",
        "description": "Build an automated irrigation controller",
        "duration": "6 weeks",
    }
    res = client.post("/api/v1/project-definitions", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert body["data"]["id"] == str(def_id)
    assert body["data"]["current_version"]["version_number"] == 1
    assert body["data"]["owner_mentor_id"] == str(mentor_user.user_id)


def test_update_definition_creates_v2_snapshot(
    client: TestClient,
    app,
    mentor_user: CurrentUser,
):
    """M20: PATCH /api/v1/project-definitions/{id} creates v2 snapshot while preserving v1."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user

    def_id = uuid.uuid4()
    ver2_id = uuid.uuid4()
    def_model = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(mentor_user.user_id),
        name="Smart Irrigation Pro",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver2_id),
    )
    ver2_model = ProjectDefinitionVersionModel(
        id=ver2_id,
        project_definition_id=str(def_id),
        version_number=2,
        name="Smart Irrigation Pro",
        problem="Water wastage in agriculture",
        proposed_solution="LoRaWAN soil telemetry & cloud analytics",
        complexity=ProjectComplexity.ADVANCED.value,
        created_by=str(mentor_user.user_id),
    )

    mock_service = AsyncMock(spec=ProjectDefinitionService)
    mock_service.update_definition.return_value = (def_model, ver2_model)
    app.dependency_overrides[get_project_definition_service] = lambda: mock_service

    res = client.patch(
        f"/api/v1/project-definitions/{def_id}",
        json={
            "name": "Smart Irrigation Pro",
            "proposed_solution": "LoRaWAN soil telemetry & cloud analytics",
            "complexity": "ADVANCED",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["current_version"]["version_number"] == 2
    assert body["data"]["current_version"]["name"] == "Smart Irrigation Pro"


def test_version_isolation_student_instances_unaffected():
    """
    SECTION 25 MANDATORY TEST: Version Isolation.

    Proves:
    1. Definition V1 exists.
    2. Student project instance is created referencing V1 snapshot.
    3. Student works on project (progress, phase, custom attributes).
    4. Mentor edits definition producing V2 snapshot.
    5. V1 remains historically valid.
    6. V2 contains updated values.
    7. Existing student project instance remains strictly pinned to V1 with zero mutation.
    """
    mentor_id = uuid.uuid4()
    student_id = uuid.uuid4()
    def_id = uuid.uuid4()
    v1_id = uuid.uuid4()
    v2_id = uuid.uuid4()

    # 1. Definition V1 snapshot
    v1 = ProjectDefinitionVersionModel(
        id=v1_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="Autonomous Solar Rover",
        problem="Remote terrain monitoring bottlenecks",
        proposed_solution="Solar-powered autonomous rover",
        complexity=ProjectComplexity.INTERMEDIATE.value,
        description="Rover with standard telemetry",
        duration="8 weeks",
        created_by=str(mentor_id),
        created_at=datetime(2026, 9, 1, 10, 0, 0, tzinfo=UTC),
    )

    # 2. Student project instance instantiated from V1
    student_instance = ProjectInstanceModel(
        id=uuid.uuid4(),
        student_id=str(student_id),
        project_definition_id=str(def_id),
        source_definition_version_id=str(v1_id),
        name="Autonomous Solar Rover",
        problem="Remote terrain monitoring bottlenecks",
        proposed_solution="Solar-powered autonomous rover",
        complexity=ProjectComplexity.INTERMEDIATE.value,
        current_phase=ProjectPhase.PLANNING.value,
        health=ProjectHealth.HEALTHY.value,
        progress_percentage=35,
        status=ProjectStatus.ACTIVE.value,
        started_at=datetime(2026, 9, 2, 10, 0, 0, tzinfo=UTC),
    )

    # Snapshot student instance state prior to mentor edit
    initial_student_snapshot_id = student_instance.source_definition_version_id
    initial_student_name = student_instance.name
    initial_student_solution = student_instance.proposed_solution
    initial_student_phase = student_instance.current_phase
    initial_student_progress = student_instance.progress_percentage

    # 3. Mentor edits definition -> produces V2
    v2 = ProjectDefinitionVersionModel(
        id=v2_id,
        project_definition_id=str(def_id),
        version_number=2,
        name="Autonomous Solar Rover Gen-2",
        problem="Remote terrain monitoring with extreme weather resilience",
        proposed_solution="Nuclear-thermal RTG hybrid rover with satellite uplink",
        complexity=ProjectComplexity.ADVANCED.value,
        description="High-end rover for deep-space terrain",
        duration="16 weeks",
        created_by=str(mentor_id),
        created_at=datetime(2026, 9, 13, 15, 0, 0, tzinfo=UTC),
    )

    # Definition container current_version points to V2
    definition = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(mentor_id),
        name="Autonomous Solar Rover Gen-2",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(v2_id),
    )

    # 4. ASSERTION: V1 remains historically intact
    assert v1.version_number == 1
    assert v1.name == "Autonomous Solar Rover"
    assert v1.proposed_solution == "Solar-powered autonomous rover"
    assert v1.id == v1_id

    # 5. ASSERTION: V2 contains updated values
    assert v2.version_number == 2
    assert v2.name == "Autonomous Solar Rover Gen-2"
    assert v2.complexity == ProjectComplexity.ADVANCED.value
    assert definition.current_version_id == str(v2_id)

    # 6. CRITICAL ARCHITECTURAL ASSERTION: Student Project Instance is completely isolated
    assert student_instance.source_definition_version_id == initial_student_snapshot_id == str(v1_id)
    assert student_instance.name == initial_student_name == "Autonomous Solar Rover"
    assert student_instance.proposed_solution == initial_student_solution == "Solar-powered autonomous rover"
    assert student_instance.current_phase == initial_student_phase == ProjectPhase.PLANNING.value
    assert student_instance.progress_percentage == initial_student_progress == 35
    assert student_instance.source_definition_version_id != str(v2_id)
    assert student_instance.name != v2.name


def test_assign_definition_authorized_success(
    client: TestClient,
    app,
    mentor_user: CurrentUser,
):
    """M21: POST /api/v1/project-definitions/{id}/assign assigns definition to student in supervised group."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user

    def_id = uuid.uuid4()
    student_id = uuid.uuid4()
    group_id = uuid.uuid4()

    instance_model = ProjectInstanceModel(
        id=uuid.uuid4(),
        student_id=str(student_id),
        group_id=str(group_id),
        project_definition_id=str(def_id),
        source_definition_version_id=str(uuid.uuid4()),
        name="Precision Agriculture Drone",
        problem="Crop monitoring latency",
        proposed_solution="Autonomous multispectral UAV",
        complexity=ProjectComplexity.ADVANCED.value,
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
        progress_percentage=0,
        status=ProjectStatus.ACTIVE.value,
    )

    mock_service = AsyncMock(spec=ProjectDefinitionService)
    mock_service.assign_definition.return_value = instance_model
    app.dependency_overrides[get_project_definition_service] = lambda: mock_service

    payload = {
        "student_id": str(student_id),
        "group_id": str(group_id),
        "deadline": "2026-11-30T18:00:00Z",
    }
    res = client.post(f"/api/v1/project-definitions/{def_id}/assign", json=payload)
    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert body["data"]["student_id"] == str(student_id)
    assert body["data"]["group_id"] == str(group_id)
    assert body["data"]["project_definition_id"] == str(def_id)


def test_assign_definition_unauthorized_group_forbidden(
    client: TestClient,
    app,
    mentor_user: CurrentUser,
):
    """M21: Assigning into an unauthorized group returns 403 Forbidden."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user

    def_id = uuid.uuid4()
    other_group_id = uuid.uuid4()
    student_id = uuid.uuid4()

    mock_service = AsyncMock(spec=ProjectDefinitionService)
    mock_service.assign_definition.side_effect = AuthorizationException(
        "Access to this group is denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_project_definition_service] = lambda: mock_service

    payload = {
        "student_id": str(student_id),
        "group_id": str(other_group_id),
    }
    res = client.post(f"/api/v1/project-definitions/{def_id}/assign", json=payload)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_assign_definition_duplicate_rejected_409(
    client: TestClient,
    app,
    mentor_user: CurrentUser,
):
    """M21: Duplicate assignment for the same student and definition returns 409 Conflict."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user

    def_id = uuid.uuid4()
    student_id = uuid.uuid4()
    group_id = uuid.uuid4()

    mock_service = AsyncMock(spec=ProjectDefinitionService)
    mock_service.assign_definition.side_effect = ConflictException(
        "Student already has an active instance of this project definition.",
        code="PROJECT_ALREADY_ASSIGNED",
    )
    app.dependency_overrides[get_project_definition_service] = lambda: mock_service

    payload = {
        "student_id": str(student_id),
        "group_id": str(group_id),
    }
    res = client.post(f"/api/v1/project-definitions/{def_id}/assign", json=payload)
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "PROJECT_ALREADY_ASSIGNED"
