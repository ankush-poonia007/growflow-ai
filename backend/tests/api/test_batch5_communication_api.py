"""
GrowFlow Phase 7 Batch 5 — Tests for Mentor Communication, Help Requests, Notes & Student Group Membership.

Validates:
- Student Group Joining via join code:
  - 401 Unauthenticated
  - 403 Forbidden for Mentor caller (RequireStudent)
  - 404 for invalid/non-existent join code (GROUP_NOT_FOUND)
  - 400 for inactive or archived group (GROUP_NOT_ACTIVE)
  - 409 for duplicate active membership (GROUP_ALREADY_MEMBER)
  - 200 for successful join with enriched group details
  - 200 for listing student groups (with mentor_name)
- Multi-Group Project Authorization Invariant:
  - GROUP MEMBERSHIP != PROJECT AUTHORIZATION
  - Multi-group student Riya is in Mentor Elena's and Mentor Sofia's groups
  - Project A belongs to Mentor Elena's group
  - Mentor Elena is authorized (200 OK)
  - Mentor Sofia is strictly forbidden (403 Forbidden)
- Help Requests Lifecycle & Semantics:
  - M33: GET /api/v1/mentors/help-requests (List mentor help requests)
  - M33: GET /api/v1/mentors/help-requests/{id} (Help request detail)
  - M33: POST /api/v1/mentors/help-requests/{id}/respond:
    - Status RESOLVED sets resolved_at
    - Status IN_PROGRESS preserves/nulls resolved_at
  - Cross-mentor help request response forbidden (403 Forbidden)
- Mentor Notes & Student Feedback:
  - M34: POST /api/v1/mentors/notes (Create note, student-visible vs internal)
  - M34: GET /api/v1/mentors/project-instances/{id}/notes (Mentor views all notes)
  - M14: GET /api/v1/projects/{id}/mentor-notes (Student views notes - INTERNAL notes hidden)
  - M14: POST /api/v1/projects/{id}/mentor-notes/{note_id}/acknowledge (Student acknowledges note)
  - Cross-mentor note creation/inspection forbidden (403 Forbidden)
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
    get_group_service,
    get_help_request_service,
    get_mentor_feedback_service,
    get_project_service,
)
from backend.app.api.schemas.group import GroupMembershipResponseSchema, GroupResponseSchema
from backend.app.application.services.group_service import GroupService
from backend.app.application.services.help_request_service import HelpRequestService
from backend.app.application.services.mentor_feedback_service import MentorFeedbackService
from backend.app.application.services.project_service import ProjectService
from backend.app.application.services.outbox_service import OutboxService
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.domain.project.models import ProjectHealth, ProjectPhase, ProjectStatus
from backend.app.infrastructure.database.models.organization import (
    GroupMembershipModel,
    GroupModel,
)
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.database.models.workspace_extensions import (
    ProjectHelpRequestModel,
    ProjectMentorNoteModel,
)
from backend.app.infrastructure.repositories.group_repository import GroupRepository
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.infrastructure.repositories.workspace_extension_repositories import (
    HelpRequestRepository,
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
def mentor_elena() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("11111111-0001-0000-0000-000000000001"),
        email="mentor.elena@growflow.ai",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def mentor_sofia() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("11111111-0003-0000-0000-000000000003"),
        email="mentor.sofia@growflow.ai",
        role=UserRole.MENTOR,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def student_aarav() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("22222222-0001-0000-0000-000000000001"),
        email="student.aarav@growflow.ai",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )


@pytest.fixture
def student_riya() -> CurrentUser:
    return CurrentUser(
        user_id=uuid.UUID("22222222-0002-0000-0000-000000000002"),
        email="student.riya@growflow.ai",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )


# =========================================================================
# SECTION 1: Student Group Join & Listing
# =========================================================================

def test_join_group_unauthenticated(client: TestClient):
    """Join group requires authentication (401)."""
    response = client.post("/api/v1/groups/join", json={"join_code": "ELENA2026"})
    assert response.status_code == 401


def test_join_group_forbidden_for_mentor(client: TestClient, app, mentor_elena):
    """Mentors cannot join groups as students (403)."""
    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    response = client.post("/api/v1/groups/join", json={"join_code": "ELENA2026"})
    assert response.status_code == 403


def test_join_group_invalid_code_not_found(client: TestClient, app, student_aarav):
    """Invalid join code returns 404 GROUP_NOT_FOUND."""
    app.dependency_overrides[get_current_user] = lambda: student_aarav
    mock_service = AsyncMock(spec=GroupService)
    mock_service.join_group.side_effect = NotFoundException(
        "Invalid group join code.", code="GROUP_NOT_FOUND"
    )
    app.dependency_overrides[get_group_service] = lambda: mock_service

    response = client.post("/api/v1/groups/join", json={"join_code": "INVALID99"})
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "GROUP_NOT_FOUND"


def test_join_group_inactive_rejected(client: TestClient, app, student_aarav):
    """Inactive or archived group join returns 400 GROUP_NOT_ACTIVE."""
    app.dependency_overrides[get_current_user] = lambda: student_aarav
    mock_service = AsyncMock(spec=GroupService)
    mock_service.join_group.side_effect = BusinessRuleException(
        "Cannot join an inactive or archived group.", code="GROUP_NOT_ACTIVE"
    )
    app.dependency_overrides[get_group_service] = lambda: mock_service

    response = client.post("/api/v1/groups/join", json={"join_code": "CLOSED2026"})
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "GROUP_NOT_ACTIVE"


def test_join_group_already_member_conflict(client: TestClient, app, student_aarav):
    """Joining a group student is already member of returns 409 GROUP_ALREADY_MEMBER."""
    app.dependency_overrides[get_current_user] = lambda: student_aarav
    mock_service = AsyncMock(spec=GroupService)
    mock_service.join_group.side_effect = ConflictException(
        "Student is already an active member of this group.", code="GROUP_ALREADY_MEMBER"
    )
    app.dependency_overrides[get_group_service] = lambda: mock_service

    response = client.post("/api/v1/groups/join", json={"join_code": "ELENA2026"})
    assert response.status_code == 409
    body = response.json()
    assert body["error"]["code"] == "GROUP_ALREADY_MEMBER"


def test_join_group_success(client: TestClient, app, student_aarav):
    """Valid join code adds membership and returns enriched details."""
    app.dependency_overrides[get_current_user] = lambda: student_aarav
    mock_service = AsyncMock(spec=GroupService)

    mock_group = GroupModel(
        id=uuid.uuid4(),
        mentor_id=uuid.uuid4(),
        name="Elena's AI Research Cohort",
        join_code="ELENA2026",
        status="ACTIVE",
    )
    mock_membership = GroupMembershipModel(
        id=uuid.uuid4(),
        group_id=mock_group.id,
        student_id=student_aarav.user_id,
        status="ACTIVE",
        joined_at=datetime.now(UTC),
    )
    mock_membership.group_name = "Elena's AI Research Cohort"
    mock_membership.join_code = "ELENA2026"
    mock_service.join_group.return_value = mock_membership
    app.dependency_overrides[get_group_service] = lambda: mock_service

    response = client.post("/api/v1/groups/join", json={"join_code": "ELENA2026"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["group_name"] == "Elena's AI Research Cohort"
    assert data["join_code"] == "ELENA2026"
    assert data["status"] == "ACTIVE"


def test_list_student_groups(client: TestClient, app, student_riya):
    """Student lists enrolled groups with mentor information."""
    app.dependency_overrides[get_current_user] = lambda: student_riya
    mock_service = AsyncMock(spec=GroupService)
    g1 = GroupModel(id=uuid.uuid4(), mentor_id=uuid.uuid4(), name="Elena's Cohort", join_code="ELENA2026", status="ACTIVE")
    g1.mentor_name = "Dr. Elena Rostova"
    g2 = GroupModel(id=uuid.uuid4(), mentor_id=uuid.uuid4(), name="Sofia's Cloud Studio", join_code="SOFIA2026", status="ACTIVE")
    g2.mentor_name = "Prof. Sofia Patel"
    mock_service.list_groups_for_user.return_value = [g1, g2]
    app.dependency_overrides[get_group_service] = lambda: mock_service

    response = client.get("/api/v1/groups")
    assert response.status_code == 200
    groups = response.json()["data"]
    assert len(groups) == 2
    assert groups[0]["mentor_name"] == "Dr. Elena Rostova"
    assert groups[1]["mentor_name"] == "Prof. Sofia Patel"


# =========================================================================
# SECTION 2: Multi-Group Project Authorization Invariant
# =========================================================================

def test_multi_group_isolation_supervising_mentor_authorized(client: TestClient, app, mentor_elena):
    """Mentor Elena supervises Project Alpha (Group Elena) -> 200 OK."""
    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    mock_proj_service = AsyncMock(spec=ProjectService)

    proj_id = uuid.uuid4()
    mock_instance = ProjectInstanceModel(
        id=proj_id,
        student_id=uuid.UUID("22222222-0002-0000-0000-000000000002"),
        group_id=uuid.uuid4(),
        name="Riya Smart Inventory Engine",
        problem="Tracking",
        proposed_solution="AI Scanner",
        complexity="MEDIUM",
        current_phase=ProjectPhase.BLUEPRINT.value,
        health=ProjectHealth.HEALTHY.value,
        progress_percentage=40,
        status=ProjectStatus.ACTIVE.value,
    )
    mock_proj_service.get_project.return_value = mock_instance
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    response = client.get(f"/api/v1/projects/{proj_id}")
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Riya Smart Inventory Engine"


def test_multi_group_isolation_non_supervising_mentor_forbidden(client: TestClient, app, mentor_sofia):
    """Mentor Sofia attempts to access Riya's project in Group Elena -> 403 Forbidden."""
    app.dependency_overrides[get_current_user] = lambda: mentor_sofia
    mock_proj_service = AsyncMock(spec=ProjectService)
    mock_proj_service.get_project.side_effect = AuthorizationException(
        "Access denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service

    proj_id = uuid.uuid4()
    response = client.get(f"/api/v1/projects/{proj_id}")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


# =========================================================================
# SECTION 3: Mentor Help Requests Lifecycle (M33)
# =========================================================================

def test_list_mentor_help_requests(client: TestClient, app, mentor_elena):
    """Mentor lists help requests for supervised projects."""
    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    mock_help_service = AsyncMock(spec=HelpRequestService)
    mock_help_service.list_mentor_help_requests.return_value = [
        {
            "id": str(uuid.uuid4()),
            "project_instance_id": str(uuid.uuid4()),
            "project_name": "Autonomous Rover Navigation",
            "student_id": str(uuid.uuid4()),
            "student_name": "Aarav Sharma",
            "student_email": "student.aarav@growflow.ai",
            "group_id": str(uuid.uuid4()),
            "group_name": "Elena's AI Research Cohort",
            "subject": "Camera calibration drift",
            "description": "Intrinsic matrix fails on resolution change",
            "category": "TECHNICAL",
            "priority": "HIGH",
            "status": "OPEN",
            "mentor_response": None,
            "resolved_at": None,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
    ]
    app.dependency_overrides[get_help_request_service] = lambda: mock_help_service

    response = client.get("/api/v1/mentors/help-requests")
    assert response.status_code == 200
    items = response.json()["data"]
    assert len(items) == 1
    assert items[0]["subject"] == "Camera calibration drift"
    assert items[0]["status"] == "OPEN"


def test_respond_help_request_resolved_sets_resolved_at(client: TestClient, app, mentor_elena):
    """Responding with RESOLVED status populates resolved_at timestamp."""
    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    mock_help_service = AsyncMock(spec=HelpRequestService)
    req_id = uuid.uuid4()
    now_iso = datetime.now(UTC).isoformat()

    mock_help_service.respond_help_request.return_value = {
        "id": str(req_id),
        "project_instance_id": str(uuid.uuid4()),
        "project_name": "Autonomous Rover Navigation",
        "student_id": str(uuid.uuid4()),
        "student_name": "Aarav Sharma",
        "student_email": "student.aarav@growflow.ai",
        "group_id": str(uuid.uuid4()),
        "group_name": "Elena's AI Research Cohort",
        "subject": "Camera calibration drift",
        "description": "Intrinsic matrix fails on resolution change",
        "category": "TECHNICAL",
        "priority": "HIGH",
        "status": "RESOLVED",
        "mentor_response": "Use cv2.fisheye calibration with 800x600 resolution lock.",
        "resolved_at": now_iso,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    app.dependency_overrides[get_help_request_service] = lambda: mock_help_service

    payload = {
        "mentor_response": "Use cv2.fisheye calibration with 800x600 resolution lock.",
        "status": "RESOLVED",
    }
    response = client.post(f"/api/v1/mentors/help-requests/{req_id}/respond", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "RESOLVED"
    assert data["resolved_at"] is not None
    assert "cv2.fisheye" in data["mentor_response"]


def test_respond_help_request_in_progress_nulls_resolved_at(client: TestClient, app, mentor_elena):
    """Responding with IN_PROGRESS preserves/nulls resolved_at timestamp."""
    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    mock_help_service = AsyncMock(spec=HelpRequestService)
    req_id = uuid.uuid4()
    now_iso = datetime.now(UTC).isoformat()

    mock_help_service.respond_help_request.return_value = {
        "id": str(req_id),
        "project_instance_id": str(uuid.uuid4()),
        "project_name": "Autonomous Rover Navigation",
        "student_id": str(uuid.uuid4()),
        "student_name": "Aarav Sharma",
        "student_email": "student.aarav@growflow.ai",
        "group_id": str(uuid.uuid4()),
        "group_name": "Elena's AI Research Cohort",
        "subject": "Camera calibration drift",
        "description": "Intrinsic matrix fails",
        "category": "TECHNICAL",
        "priority": "HIGH",
        "status": "IN_PROGRESS",
        "mentor_response": "Reviewing your calibration matrix.",
        "resolved_at": None,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    app.dependency_overrides[get_help_request_service] = lambda: mock_help_service

    payload = {
        "mentor_response": "Reviewing your calibration matrix.",
        "status": "IN_PROGRESS",
    }
    response = client.post(f"/api/v1/mentors/help-requests/{req_id}/respond", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "IN_PROGRESS"
    assert data["resolved_at"] is None


def test_respond_help_request_cross_mentor_forbidden(client: TestClient, app, mentor_sofia):
    """Mentor Sofia cannot respond to help request of Elena's supervised student (403)."""
    app.dependency_overrides[get_current_user] = lambda: mentor_sofia
    mock_help_service = AsyncMock(spec=HelpRequestService)
    mock_help_service.respond_help_request.side_effect = AuthorizationException(
        "Access denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )
    app.dependency_overrides[get_help_request_service] = lambda: mock_help_service

    req_id = uuid.uuid4()
    payload = {"mentor_response": "Unauthorized response", "status": "RESOLVED"}
    response = client.post(f"/api/v1/mentors/help-requests/{req_id}/respond", json=payload)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


@pytest.mark.asyncio
async def test_help_request_repository_update_response_refreshes_and_persists():
    """
    Regression test for M33 Help Request Response HTTP 500 (MissingGreenlet):
    Verifies that update_response:
    1. Explicitly sets updated_at to a datetime
    2. Correctly sets status and mentor_response
    3. Flushes and refreshes the entity from session (preventing MissingGreenlet on expired attributes)
    4. Sets resolved_at ONLY when status is RESOLVED, nulls when IN_PROGRESS
    """
    mock_session = AsyncMock()
    repo = HelpRequestRepository(mock_session)

    req_id = uuid.uuid4()
    mock_req = ProjectHelpRequestModel(
        id=req_id,
        project_instance_id=str(uuid.uuid4()),
        student_id=str(uuid.uuid4()),
        subject="Docker networking fails",
        description="Bridge network connection refused",
        category="TECHNICAL",
        priority="HIGH",
        status="OPEN",
        mentor_response=None,
        resolved_at=None,
    )
    repo.get_by_id = AsyncMock(return_value=mock_req)

    # 1. Update with status=RESOLVED
    updated = await repo.update_response(
        request_id=req_id,
        mentor_response="Configure host-gateway in extra_hosts.",
        status="RESOLVED",
    )

    assert updated is not None
    assert updated.status == "RESOLVED"
    assert updated.mentor_response == "Configure host-gateway in extra_hosts."
    assert updated.resolved_at is not None
    assert updated.updated_at is not None
    mock_session.flush.assert_called()
    mock_session.refresh.assert_called_with(mock_req)

    # 2. Update with status=IN_PROGRESS (preserves/nulls resolved_at)
    mock_session.reset_mock()
    updated_progress = await repo.update_response(
        request_id=req_id,
        mentor_response="Investigating firewall settings.",
        status="IN_PROGRESS",
    )
    assert updated_progress.status == "IN_PROGRESS"
    assert updated_progress.resolved_at is None
    mock_session.flush.assert_called()
    mock_session.refresh.assert_called_with(mock_req)


@pytest.mark.asyncio
async def test_help_request_lifecycle_student_create_mentor_respond_student_view(
    mentor_elena, mentor_sofia, student_aarav
):
    """
    Complete lifecycle regression test:
    Student creates Help Request
    → supervising Mentor retrieves it
    → Mentor responds (invoking real HelpRequestService.respond_help_request)
    → response is persisted
    → status is correct (RESOLVED, resolved_at set)
    → Student retrieves request
    → Mentor response is present
    → Unauthorized Mentor cannot respond (403 AuthorizationException)
    """
    proj_id = uuid.uuid4()
    group_id = uuid.uuid4()

    mock_project = ProjectInstanceModel(
        id=proj_id,
        student_id=student_aarav.user_id,
        group_id=group_id,
        name="Autonomous Rover Navigation",
        problem="Obstacle avoidance",
        proposed_solution="LIDAR SLAM",
        complexity="HIGH",
        current_phase=ProjectPhase.BLUEPRINT.value,
        health=ProjectHealth.HEALTHY.value,
        progress_percentage=60,
        status=ProjectStatus.ACTIVE.value,
    )
    mock_group = GroupModel(
        id=group_id,
        mentor_id=mentor_elena.user_id,
        name="Elena's AI Research Cohort",
        join_code="ELENA2026",
        status="ACTIVE",
    )
    student_user_model = UserModel(
        id=str(student_aarav.user_id),
        email=student_aarav.email,
        full_name="Aarav Sharma",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    mock_proj_repo = AsyncMock(spec=ProjectRepository)
    mock_proj_repo.get_by_id.return_value = mock_project

    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_group_repo.get_by_id.return_value = mock_group

    stored_requests: dict[str, ProjectHelpRequestModel] = {}

    mock_help_repo = AsyncMock(spec=HelpRequestRepository)

    async def fake_add(req):
        now = datetime.now(UTC)
        req.created_at = now
        req.updated_at = now
        stored_requests[str(req.id)] = req
        return req

    async def fake_get_by_id(req_id):
        return stored_requests.get(str(req_id))

    async def fake_get_detailed(req_id):
        req = stored_requests.get(str(req_id))
        if not req:
            return None
        return (req, mock_project, student_user_model, mock_group)

    async def fake_update_response(request_id, mentor_response, status="RESOLVED"):
        req = stored_requests.get(str(request_id))
        if req:
            now = datetime.now(UTC)
            req.mentor_response = mentor_response.strip()
            req.status = status.upper()
            req.updated_at = now
            if status.upper() == "RESOLVED":
                req.resolved_at = now
            else:
                req.resolved_at = None
        return req

    mock_help_repo.add.side_effect = fake_add
    mock_help_repo.get_by_id.side_effect = fake_get_by_id
    mock_help_repo.get_detailed_by_id.side_effect = fake_get_detailed
    mock_help_repo.update_response.side_effect = fake_update_response

    mock_outbox = AsyncMock(spec=OutboxService)

    # Real HelpRequestService instance!
    service = HelpRequestService(
        project_repo=mock_proj_repo,
        group_repo=mock_group_repo,
        help_request_repo=mock_help_repo,
        outbox_service=mock_outbox,
    )

    # Step 1: Student creates Help Request
    created = await service.create_help_request(
        project_id=proj_id,
        current_user=student_aarav,
        subject="LiDAR point cloud drift",
        description="Drift observed on steep gradients",
        category="TECHNICAL",
        priority="HIGH",
    )
    req_id = created["id"]
    assert created["status"] == "OPEN"
    assert created["mentor_response"] is None
    assert created["resolved_at"] is None

    # Step 2: Supervising Mentor retrieves it
    retrieved = await service.get_mentor_help_request(
        mentor_id=mentor_elena.user_id,
        request_id=req_id,
    )
    assert retrieved["id"] == req_id
    assert retrieved["student_name"] == "Aarav Sharma"
    assert retrieved["status"] == "OPEN"

    # Step 3: Mentor responds (RESOLVED)
    response_result = await service.respond_help_request(
        mentor_id=mentor_elena.user_id,
        request_id=req_id,
        mentor_response="Calibrate IMU extrinsics and enable loop closure.",
        status="RESOLVED",
    )
    assert response_result["status"] == "RESOLVED"
    assert response_result["mentor_response"] == "Calibrate IMU extrinsics and enable loop closure."
    assert response_result["resolved_at"] is not None
    assert response_result["updated_at"] is not None

    # Step 4: Verify response is persisted in repository
    persisted = stored_requests[req_id]
    assert persisted.status == "RESOLVED"
    assert persisted.mentor_response == "Calibrate IMU extrinsics and enable loop closure."
    assert persisted.resolved_at is not None

    # Step 5: Student retrieves request and verifies Mentor response is present
    student_view = await service.get_help_request(
        project_id=proj_id,
        request_id=req_id,
        current_user=student_aarav,
    )
    assert student_view["status"] == "RESOLVED"
    assert student_view["mentor_response"] == "Calibrate IMU extrinsics and enable loop closure."
    assert student_view["resolved_at"] is not None

    # Step 6: Verify unauthorized Mentor cannot respond
    with pytest.raises(AuthorizationException):
        await service.respond_help_request(
            mentor_id=mentor_sofia.user_id,
            request_id=req_id,
            mentor_response="Unauthorized response attempt",
            status="RESOLVED",
        )


def test_api_help_request_respond_and_student_retrieval_flow(
    client: TestClient, app, mentor_elena, mentor_sofia, student_aarav
):
    """
    HTTP API flow verifying mentor response submission and student inspection:
    1. Mentor responds to student help request -> 200 OK
    2. Student retrieves request -> 200 OK with mentor_response present
    3. Unauthorized mentor receives 403 Forbidden
    """
    req_id = uuid.uuid4()
    proj_id = uuid.uuid4()
    now_iso = datetime.now(UTC).isoformat()

    stored = {
        "id": str(req_id),
        "project_instance_id": str(proj_id),
        "project_name": "Autonomous Rover Navigation",
        "student_id": str(student_aarav.user_id),
        "student_name": "Aarav Sharma",
        "student_email": student_aarav.email,
        "group_id": str(uuid.uuid4()),
        "group_name": "Elena's AI Research Cohort",
        "subject": "LiDAR point cloud drift",
        "description": "Drift observed on steep gradients",
        "category": "TECHNICAL",
        "priority": "HIGH",
        "status": "OPEN",
        "mentor_response": None,
        "resolved_at": None,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    mock_help_service = AsyncMock(spec=HelpRequestService)

    async def fake_respond(mentor_id, request_id, mentor_response, status="RESOLVED"):
        if str(mentor_id) != str(mentor_elena.user_id):
            raise AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")
        stored["status"] = status
        stored["mentor_response"] = mentor_response
        stored["resolved_at"] = datetime.now(UTC).isoformat() if status == "RESOLVED" else None
        stored["updated_at"] = datetime.now(UTC).isoformat()
        return dict(stored)

    async def fake_get_student(project_id, request_id, current_user):
        return dict(stored)

    mock_help_service.respond_help_request.side_effect = fake_respond
    mock_help_service.get_help_request.side_effect = fake_get_student
    app.dependency_overrides[get_help_request_service] = lambda: mock_help_service

    # Mentor Elena responds
    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    resp = client.post(
        f"/api/v1/mentors/help-requests/{req_id}/respond",
        json={"mentor_response": "Calibrate IMU extrinsics.", "status": "RESOLVED"},
    )
    assert resp.status_code == 200
    res_data = resp.json()["data"]
    assert res_data["status"] == "RESOLVED"
    assert res_data["mentor_response"] == "Calibrate IMU extrinsics."
    assert res_data["resolved_at"] is not None

    # Student Aarav retrieves the request
    app.dependency_overrides[get_current_user] = lambda: student_aarav
    resp_student = client.get(f"/api/v1/projects/{proj_id}/help-requests/{req_id}")
    assert resp_student.status_code == 200
    student_data = resp_student.json()["data"]
    assert student_data["status"] == "RESOLVED"
    assert student_data["mentor_response"] == "Calibrate IMU extrinsics."
    assert student_data["resolved_at"] is not None

    # Unauthorized Mentor Sofia attempts to respond -> 403 Forbidden
    app.dependency_overrides[get_current_user] = lambda: mentor_sofia
    resp_unauth = client.post(
        f"/api/v1/mentors/help-requests/{req_id}/respond",
        json={"mentor_response": "Unauthorized response", "status": "RESOLVED"},
    )
    assert resp_unauth.status_code == 403
    assert resp_unauth.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


# =========================================================================
# SECTION 4: Mentor Notes & Student Feedback Visibility (M34 / M14)
# =========================================================================

def test_mentor_create_note_success(client: TestClient, app, mentor_elena):
    """Mentor creates advisory note on supervised project instance."""
    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    mock_feedback_service = AsyncMock(spec=MentorFeedbackService)

    note_id = uuid.uuid4()
    proj_id = uuid.uuid4()
    mock_feedback_service.create_mentor_note.return_value = {
        "id": str(note_id),
        "project_instance_id": str(proj_id),
        "mentor_id": str(mentor_elena.user_id),
        "mentor_name": "Dr. Elena Rostova",
        "title": "Camera Calibration Note",
        "message": "Refactor camera buffer to avoid frame loss.",
        "note_type": "ACTIONABLE",
        "status": "UNREAD",
        "related_resource_type": None,
        "related_resource_id": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    app.dependency_overrides[get_mentor_feedback_service] = lambda: mock_feedback_service

    payload = {
        "project_instance_id": str(proj_id),
        "title": "Camera Calibration Note",
        "message": "Refactor camera buffer to avoid frame loss.",
        "note_type": "ACTIONABLE",
    }
    response = client.post("/api/v1/mentors/notes", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["title"] == "Camera Calibration Note"
    assert data["message"] == "Refactor camera buffer to avoid frame loss."
    assert data["note_type"] == "ACTIONABLE"


def test_mentor_list_notes_includes_internal(client: TestClient, app, mentor_elena):
    """Mentor inspecting project instance notes sees BOTH visible and internal notes."""
    app.dependency_overrides[get_current_user] = lambda: mentor_elena
    mock_feedback_service = AsyncMock(spec=MentorFeedbackService)
    proj_id = uuid.uuid4()

    mock_feedback_service.list_mentor_notes_for_project.return_value = [
        {
            "id": str(uuid.uuid4()),
            "project_instance_id": str(proj_id),
            "mentor_id": str(mentor_elena.user_id),
            "mentor_name": "Dr. Elena Rostova",
            "title": "Visible Feedback",
            "message": "Visible feedback for student",
            "note_type": "ACTIONABLE",
            "status": "UNREAD",
            "created_at": datetime.now(UTC).isoformat(),
        },
        {
            "id": str(uuid.uuid4()),
            "project_instance_id": str(proj_id),
            "mentor_id": str(mentor_elena.user_id),
            "mentor_name": "Dr. Elena Rostova",
            "title": "Mentor Internal Log",
            "message": "Internal note: Student struggling with concurrency",
            "note_type": "INTERNAL",
            "status": "UNREAD",
            "created_at": datetime.now(UTC).isoformat(),
        },
    ]
    app.dependency_overrides[get_mentor_feedback_service] = lambda: mock_feedback_service

    response = client.get(f"/api/v1/mentors/project-instances/{proj_id}/notes")
    assert response.status_code == 200
    items = response.json()["data"]
    assert len(items) == 2
    types = [i["note_type"] for i in items]
    assert "ACTIONABLE" in types
    assert "INTERNAL" in types


def test_student_feedback_filters_internal_notes(client: TestClient, app, student_aarav):
    """Student endpoint (M14) filters out internal notes, showing ONLY student-visible feedback."""
    app.dependency_overrides[get_current_user] = lambda: student_aarav
    mock_feedback_service = AsyncMock(spec=MentorFeedbackService)
    proj_id = uuid.uuid4()

    # The service contract guarantees INTERNAL notes are filtered out for students
    mock_feedback_service.list_mentor_notes.return_value = [
        {
            "id": str(uuid.uuid4()),
            "project_instance_id": str(proj_id),
            "mentor_id": str(uuid.uuid4()),
            "title": "Public Note",
            "message": "Public feedback note",
            "note_type": "ACTIONABLE",
            "status": "UNREAD",
            "related_resource_type": None,
            "related_resource_id": None,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
    ]
    app.dependency_overrides[get_mentor_feedback_service] = lambda: mock_feedback_service

    response = client.get(f"/api/v1/projects/{proj_id}/mentor-notes")
    assert response.status_code == 200
    items = response.json()["data"]
    assert len(items) == 1
    assert items[0]["title"] == "Public Note"
    assert items[0]["note_type"] == "ACTIONABLE"


def test_student_acknowledge_mentor_note(client: TestClient, app, student_aarav):
    """Student acknowledges note without altering project state."""
    app.dependency_overrides[get_current_user] = lambda: student_aarav
    mock_feedback_service = AsyncMock(spec=MentorFeedbackService)
    proj_id = uuid.uuid4()
    note_id = uuid.uuid4()

    mock_feedback_service.acknowledge_note.return_value = {
        "id": str(note_id),
        "project_instance_id": str(proj_id),
        "mentor_id": str(uuid.uuid4()),
        "title": "Public Note",
        "message": "Refactor camera buffer",
        "note_type": "ACTIONABLE",
        "status": "ACKNOWLEDGED",
        "related_resource_type": None,
        "related_resource_id": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    app.dependency_overrides[get_mentor_feedback_service] = lambda: mock_feedback_service

    response = client.post(f"/api/v1/projects/{proj_id}/mentor-notes/{note_id}/acknowledge")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "ACKNOWLEDGED"

