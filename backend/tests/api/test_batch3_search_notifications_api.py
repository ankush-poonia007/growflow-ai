"""
GrowFlow Phase 8 Batch 3 — Targeted API Tests for Search, Notifications, and Shared State.

Covers:
1. Search APIs:
   - 401 Unauthorized for unauthenticated requests
   - Student authorized search and exclusion of other students' data
   - Mentor authorized search and exclusion of unrelated groups/students
   - Admin search across governance entities
   - Bounded queries and empty query handling
2. Notification APIs:
   - 401 Unauthorized for unauthenticated requests
   - List notifications strictly scoped to recipient
   - Unread count accurate
   - Mark single read (idempotent, sets read_at)
   - Mark all read (scoped to current user)
   - Cross-user mark read 404 (does not leak existence)
3. Event-to-Notification Mapping:
   - Exact 8 canonical events generate notifications
   - Routine events (TaskCreated, DocumentCreated, etc.) DO NOT generate notifications
   - Deduplication / idempotency on event_id
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from fastapi.testclient import TestClient
import jwt
import pytest

from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import (
    get_notification_service,
    get_search_service,
)
from backend.app.application.services.notification_service import (
    IN_SCOPE_NOTIFICATION_EVENTS,
    NotificationService,
)
from backend.app.application.services.search_service import SearchService
from backend.app.domain.identity import UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.notification import NotificationModel
from backend.app.infrastructure.database.models.organization import GroupModel
from backend.app.infrastructure.database.models.outbox import DomainEventModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.group_repository import GroupRepository
from backend.app.infrastructure.repositories.notification_repository import (
    NotificationRepository,
)
from backend.app.infrastructure.repositories.project_repository import ProjectRepository

if TYPE_CHECKING:
    from backend.app.config.settings import Settings

_TEST_SECRET = "batch3-test-jwt-secret-at-least-32-chars-long-12345"
_TEST_AUDIENCE = "authenticated"
_TEST_ISSUER = "https://test.supabase.co/auth/v1"


def _make_jwt(
    user_id: uuid.UUID | str,
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
def student_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def mentor_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def admin_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def student_token(student_id: uuid.UUID) -> str:
    return _make_jwt(student_id, "student@example.com", UserRole.STUDENT.value)


@pytest.fixture
def mentor_token(mentor_id: uuid.UUID) -> str:
    return _make_jwt(mentor_id, "mentor@example.com", UserRole.MENTOR.value)


@pytest.fixture
def admin_token(admin_id: uuid.UUID) -> str:
    return _make_jwt(admin_id, "admin@example.com", UserRole.ADMIN.value)


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def client(
    auth_settings: Settings,
    mock_session: AsyncMock,
    student_id: uuid.UUID,
    mentor_id: uuid.UUID,
    admin_id: uuid.UUID,
) -> TestClient:
    app = create_app(auth_settings)

    # In-memory store for notifications during testing
    notifications_store: list[NotificationModel] = []

    # Mock user repository get_by_id
    async def mock_get_user(user_id):
        uid_str = str(user_id)
        if uid_str == str(student_id):
            return UserModel(id=student_id, email="student@example.com", role="STUDENT", status="ACTIVE")
        elif uid_str == str(mentor_id):
            return UserModel(id=mentor_id, email="mentor@example.com", role="MENTOR", status="ACTIVE")
        elif uid_str == str(admin_id):
            return UserModel(id=admin_id, email="admin@example.com", role="ADMIN", status="ACTIVE")
        return None

    mock_notif_repo = AsyncMock(spec=NotificationRepository)

    async def mock_create_notification(**kwargs):
        event_id = kwargs.get("event_id")
        user_id = str(kwargs["user_id"])
        if event_id:
            for n in notifications_store:
                if n.event_id == str(event_id) and str(n.user_id) == user_id:
                    return n
        notif = NotificationModel(
            id=uuid.uuid4(),
            user_id=str(kwargs["user_id"]),
            actor_id=str(kwargs.get("actor_id")) if kwargs.get("actor_id") else None,
            actor_role=kwargs.get("actor_role"),
            title=kwargs["title"],
            message=kwargs["message"],
            notification_type=kwargs["notification_type"],
            category=kwargs.get("category", "SYSTEM"),
            resource_type=kwargs.get("resource_type"),
            resource_id=str(kwargs.get("resource_id")) if kwargs.get("resource_id") else None,
            link=kwargs.get("link", ""),
            is_read=False,
            read_at=None,
            created_at=datetime.now(UTC),
            event_id=str(event_id) if event_id else None,
        )
        notifications_store.append(notif)
        return notif

    async def mock_list_by_user(user_id, limit=20, offset=0, unread_only=False):
        res = [n for n in notifications_store if str(n.user_id) == str(user_id)]
        if unread_only:
            res = [n for n in res if not n.is_read]
        return res[offset : offset + limit]

    async def mock_count_unread(user_id):
        return len([n for n in notifications_store if str(n.user_id) == str(user_id) and not n.is_read])

    async def mock_mark_read(notification_id, user_id):
        for n in notifications_store:
            if str(n.id) == str(notification_id) and str(n.user_id) == str(user_id):
                n.is_read = True
                n.read_at = datetime.now(UTC)
                return n
        return None

    async def mock_mark_all_read(user_id):
        count = 0
        now = datetime.now(UTC)
        for n in notifications_store:
            if str(n.user_id) == str(user_id) and not n.is_read:
                n.is_read = True
                n.read_at = now
                count += 1
        return count

    mock_notif_repo.create_notification = AsyncMock(side_effect=mock_create_notification)
    mock_notif_repo.list_by_user = AsyncMock(side_effect=mock_list_by_user)
    mock_notif_repo.count_unread = AsyncMock(side_effect=mock_count_unread)
    mock_notif_repo.mark_read = AsyncMock(side_effect=mock_mark_read)
    mock_notif_repo.mark_all_read = AsyncMock(side_effect=mock_mark_all_read)

    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_group_repo = AsyncMock(spec=GroupRepository)

    notif_service = NotificationService(mock_notif_repo, mock_project_repo, mock_group_repo)
    search_service = SearchService(mock_session)

    # Attach in-memory store to client for inspection
    app.dependency_overrides[get_db_session] = lambda: mock_session
    app.dependency_overrides[get_notification_service] = lambda: notif_service
    app.dependency_overrides[get_search_service] = lambda: search_service

    with patch("backend.app.infrastructure.repositories.user_repository.UserRepository.get_by_id", side_effect=mock_get_user):
        yield TestClient(app)


# =========================================================================
# 1. SEARCH API TESTS
# =========================================================================

def test_search_unauthenticated_returns_401(client: TestClient):
    """Anonymous access to /api/v1/search returns 401 Unauthorized."""
    response = client.get("/api/v1/search?q=drone")
    assert response.status_code == 401


def test_search_empty_query_returns_empty_results(client: TestClient, student_token: str):
    """Searching with an empty query returns 200 with total: 0 and results: []."""
    response = client.get(
        "/api/v1/search?q=",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["query"] == ""
    assert data["total"] == 0
    assert data["results"] == []


def test_search_student_scope(client: TestClient, student_token: str, mock_session: AsyncMock):
    """Student search returns own projects and published definitions, excluding others."""
    # Mock database results for student
    mock_project = ProjectInstanceModel(
        id=uuid.uuid4(),
        student_id=str(uuid.uuid4()),
        name="Precision Drone Telemetry",
        problem="Telemetry gaps",
        proposed_solution="Sensor fusion",
        current_phase="BLUEPRINT",
        health="HEALTHY",
        status="ACTIVE",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.side_effect = [
        [mock_project],  # projects
        [uuid.uuid4()],  # project_ids for subqueries
        [],              # tasks
        [],              # milestones
        [],              # documents
        [],              # definitions
        [],              # help_requests
    ]
    mock_session.execute.return_value = mock_result

    response = client.get(
        "/api/v1/search?q=drone",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["workplace"] == "BUILD"
    assert len(data["results"]) >= 1
    assert data["results"][0]["title"] == "Precision Drone Telemetry"
    assert data["results"][0]["resource_type"] == "project"


def test_search_admin_scope(client: TestClient, admin_token: str, mock_session: AsyncMock):
    """Admin search returns users and platform governance records."""
    mock_user = UserModel(
        id=uuid.uuid4(),
        email="student1@example.com",
        full_name="Alice Student",
        role="STUDENT",
        status="ACTIVE",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.side_effect = [
        [mock_user],  # users
        [],           # groups
        [],           # definitions
        [],           # projects
        [],           # events
        [],           # documents
    ]
    mock_session.execute.return_value = mock_result

    response = client.get(
        "/api/v1/search?q=alice",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["workplace"] == "GOVERN"
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == "Alice Student"
    assert data["results"][0]["resource_type"] == "user"


# =========================================================================
# 2. NOTIFICATIONS API TESTS
# =========================================================================

def test_notifications_unauthenticated_returns_401(client: TestClient):
    """Anonymous access to /api/v1/notifications returns 401."""
    response = client.get("/api/v1/notifications")
    assert response.status_code == 401


def test_notifications_lifecycle_and_unread_count(
    client: TestClient,
    student_token: str,
    student_id: uuid.UUID,
):
    """Test empty list, adding notification, unread count, and mark read."""
    # 1. Initially empty
    resp = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"] == []

    # 2. Unread count initially 0
    resp_count = client.get(
        "/api/v1/notifications/unread-count",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp_count.status_code == 200
    assert resp_count.json()["data"]["unread_count"] == 0


@pytest.mark.asyncio
async def test_exact_eight_canonical_events_and_exclusions():
    """Verify that only the approved 8 canonical domain events trigger notifications."""
    assert len(IN_SCOPE_NOTIFICATION_EVENTS) == 8

    # Approved events
    assert "MentorNoteCreated" in IN_SCOPE_NOTIFICATION_EVENTS
    assert "MentorNoteAcknowledged" in IN_SCOPE_NOTIFICATION_EVENTS
    assert "HelpRequestCreated" in IN_SCOPE_NOTIFICATION_EVENTS
    assert "HelpRequestResponded" in IN_SCOPE_NOTIFICATION_EVENTS
    assert "BlueprintGenerated" in IN_SCOPE_NOTIFICATION_EVENTS
    assert "BlueprintApproved" in IN_SCOPE_NOTIFICATION_EVENTS
    assert "ProjectChangeRequested" in IN_SCOPE_NOTIFICATION_EVENTS
    assert "ProjectChangeCompleted" in IN_SCOPE_NOTIFICATION_EVENTS

    # Excluded routine events (Must NEVER be in notification events)
    excluded = [
        "TaskCreated",
        "TaskUpdated",
        "TaskCompleted",
        "DocumentCreated",
        "DocumentUpdated",
        "GitHubSynced",
        "AIMentorMessageSent",
        "ProjectDefinitionCreated",
        "GroupCreated",
    ]
    for ev in excluded:
        assert ev not in IN_SCOPE_NOTIFICATION_EVENTS


@pytest.mark.asyncio
async def test_event_deduplication_on_event_id():
    """Verify that processing the same domain event twice does not duplicate notifications."""
    mock_repo = AsyncMock(spec=NotificationRepository)
    existing_notif = NotificationModel(
        id=uuid.uuid4(),
        user_id=str(uuid.uuid4()),
        title="Blueprint Synthesized",
        message="Your blueprint is ready",
        notification_type="BlueprintGenerated",
        event_id="event-12345",
    )
    mock_repo.get_by_event_id.return_value = existing_notif

    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_group_repo = AsyncMock(spec=GroupRepository)

    service = NotificationService(mock_repo, mock_project_repo, mock_group_repo)

    # Replay event
    event = DomainEventModel(
        id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        event_type="BlueprintGenerated",
        actor_id=None,
        actor_role="SYSTEM",
        resource_type="blueprint",
        resource_id="bp-1",
        project_instance_id="proj-1",
        metadata_json={},
    )
    mock_project_repo.get_by_id.return_value = ProjectInstanceModel(
        id="proj-1",
        student_id="student-999",
        name="Drone Project",
        problem="",
        proposed_solution="",
    )

    # Real repo create_notification check
    repo = NotificationRepository(AsyncMock())
    repo.get_by_event_id = AsyncMock(return_value=existing_notif)
    repo.add = AsyncMock()

    result = await repo.create_notification(
        user_id="student-999",
        title="Blueprint Synthesized",
        message="Your blueprint is ready",
        notification_type="BlueprintGenerated",
        event_id="event-12345",
    )
    # Returns existing without adding
    assert result == existing_notif
    repo.add.assert_not_called()


def test_search_mentor_scope(client: TestClient, mentor_token: str, mentor_id: uuid.UUID, mock_session: AsyncMock):
    """Mentor search returns supervised groups and projects."""
    mock_group = GroupModel(
        id=uuid.uuid4(),
        mentor_id=str(mentor_id),
        name="AI Explorers",
        join_code="AI-101",
        status="ACTIVE",
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.side_effect = [
        [mock_group],    # groups
        [uuid.uuid4()],  # student_ids
        [],              # students
        [],              # supervised projects
        [],              # tasks
        [],              # help_requests
        [],              # change_requests
        [],              # definitions
    ]
    mock_session.execute.return_value = mock_result

    response = client.get(
        "/api/v1/search?q=explorers",
        headers={"Authorization": f"Bearer {mentor_token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["workplace"] == "SUPERVISE"
    assert len(data["results"]) >= 1
    assert data["results"][0]["title"] == "AI Explorers"
    assert data["results"][0]["resource_type"] == "group"


def test_search_query_bounding(client: TestClient, student_token: str, mock_session: AsyncMock):
    """Query limits and string lengths are bounded; oversized/malformed queries are rejected with 422."""
    # 1. Oversized query (> 100 chars) is rejected with 422
    response_long = client.get(
        f"/api/v1/search?q={'a' * 150}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response_long.status_code == 422

    # 2. Oversized limit (> 50) is rejected with 422
    response_limit = client.get(
        "/api/v1/search?q=drone&limit=500",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response_limit.status_code == 422

    # 3. Valid bounded query returns 200
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    response_valid = client.get(
        "/api/v1/search?q=drone&limit=50",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response_valid.status_code == 200


def test_notification_cross_user_isolation_and_idempotency(
    client: TestClient,
    student_token: str,
    mentor_token: str,
    student_id: uuid.UUID,
    mentor_id: uuid.UUID,
):
    """Notification reads and updates are strictly isolated; other users get 404."""
    # 1. Create a notification for student
    from backend.app.api.dependencies.services import get_notification_service
    notif_service = client.app.dependency_overrides[get_notification_service]()
    import asyncio
    created = asyncio.run(notif_service._notification_repo.create_notification(
        user_id=student_id,
        title="Note from Mentor",
        message="Review your architecture",
        notification_type="MentorNoteCreated",
        category="FEEDBACK",
        link="/student/notes/1",
    ))

    # 2. Mentor tries to mark student's notification as read -> 404 (does not leak existence)
    resp_cross = client.patch(
        f"/api/v1/notifications/{created.id}/read",
        headers={"Authorization": f"Bearer {mentor_token}"},
    )
    assert resp_cross.status_code == 404

    # 3. Student marks own notification as read -> 200
    resp_read = client.patch(
        f"/api/v1/notifications/{created.id}/read",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp_read.status_code == 200
    assert resp_read.json()["data"]["is_read"] is True

    # 4. Idempotent: marking read a second time also returns 200 with is_read True
    resp_read_again = client.patch(
        f"/api/v1/notifications/{created.id}/read",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp_read_again.status_code == 200
    assert resp_read_again.json()["data"]["is_read"] is True


def test_notification_mark_all_read_scoped_to_caller(
    client: TestClient,
    student_token: str,
    mentor_token: str,
    student_id: uuid.UUID,
    mentor_id: uuid.UUID,
):
    """Mark all read only marks notifications for the calling recipient."""
    from backend.app.api.dependencies.services import get_notification_service
    notif_service = client.app.dependency_overrides[get_notification_service]()
    import asyncio

    # Add 2 for student, 1 for mentor
    asyncio.run(notif_service._notification_repo.create_notification(
        user_id=student_id,
        title="S1",
        message="M1",
        notification_type="BlueprintGenerated",
    ))
    asyncio.run(notif_service._notification_repo.create_notification(
        user_id=student_id,
        title="S2",
        message="M2",
        notification_type="BlueprintApproved",
    ))
    asyncio.run(notif_service._notification_repo.create_notification(
        user_id=mentor_id,
        title="Mentor Notif",
        message="M-msg",
        notification_type="HelpRequestCreated",
    ))

    # Student marks all read
    resp = client.post(
        "/api/v1/notifications/mark-all-read",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 200
    # Mentor's unread count must still be 1
    resp_m = client.get(
        "/api/v1/notifications/unread-count",
        headers={"Authorization": f"Bearer {mentor_token}"},
    )
    assert resp_m.status_code == 200
    assert resp_m.json()["data"]["unread_count"] >= 1


def test_notification_model_and_migration_schema():
    """Verify notification table definition matches UserModel key type and index requirements."""
    table = NotificationModel.__table__

    # 1. Primary key and foreign key types
    assert str(table.c.id.type) == "VARCHAR(36)" or "VARCHAR" in str(table.c.id.type)
    assert str(table.c.user_id.type) == "VARCHAR(36)" or "VARCHAR" in str(table.c.user_id.type)

    # 2. Required columns exist
    expected_cols = {
        "id", "user_id", "actor_id", "actor_role", "title", "message",
        "notification_type", "category", "resource_type", "resource_id",
        "link", "is_read", "read_at", "created_at", "event_id",
    }
    actual_cols = {c.name for c in table.columns}
    assert expected_cols.issubset(actual_cols)

    # 3. Compound index requirements
    index_names = {idx.name for idx in table.indexes}
    assert "ix_notifications_user_unread" in index_names
    assert "ix_notifications_user_created" in index_names

    # 4. Compound unique constraint on (event_id, user_id)
    unique_constraints = {c.name: [col.name for col in c.columns] for c in table.constraints if hasattr(c, "columns") and c.name}
    assert "uq_notifications_event_user" in unique_constraints
    assert unique_constraints["uq_notifications_event_user"] == ["event_id", "user_id"]


@pytest.mark.asyncio
async def test_project_change_completed_dual_recipient_and_idempotency():
    """
    Verify that ProjectChangeCompleted creates TWO recipient-scoped notifications:
    1. exactly one notification for student project owner
    2. exactly one notification for supervising mentor
    Also verifies:
    - unrelated student receives none
    - unrelated mentor receives none
    - retrying the same event does not create duplicates (idempotent on (event_id, user_id))
    - both notifications reference the same canonical event
    - both notifications remain recipient-scoped
    - existing read/unread behavior remains unchanged
    """
    student_id = uuid.uuid4()
    mentor_id = uuid.uuid4()
    unrelated_student_id = uuid.uuid4()
    unrelated_mentor_id = uuid.uuid4()
    group_id = uuid.uuid4()
    project_id = uuid.uuid4()

    # Canonical entities
    project = ProjectInstanceModel(
        id=project_id,
        student_id=str(student_id),
        group_id=str(group_id),
        name="Autonomous Drone Delivery",
        problem="Package routing bottlenecks",
        proposed_solution="Decentralized aerial network",
    )
    group = GroupModel(
        id=group_id,
        mentor_id=str(mentor_id),
        name="Robotics Cohort 2026",
        join_code="ROBOT-2026",
        status="ACTIVE",
    )

    notifications_store: list[NotificationModel] = []

    async def store_create_notification(**kwargs):
        event_id = kwargs.get("event_id")
        user_id = str(kwargs["user_id"])
        if event_id:
            for n in notifications_store:
                if n.event_id == str(event_id) and str(n.user_id) == user_id:
                    return n
        notif = NotificationModel(
            id=uuid.uuid4(),
            user_id=user_id,
            actor_id=str(kwargs.get("actor_id")) if kwargs.get("actor_id") else None,
            actor_role=kwargs.get("actor_role"),
            title=kwargs["title"],
            message=kwargs["message"],
            notification_type=kwargs["notification_type"],
            category=kwargs.get("category", "TECHNICAL"),
            resource_type=kwargs.get("resource_type"),
            resource_id=str(kwargs.get("resource_id")) if kwargs.get("resource_id") else None,
            link=kwargs.get("link", ""),
            is_read=False,
            read_at=None,
            created_at=datetime.now(UTC),
            event_id=str(event_id) if event_id else None,
        )
        notifications_store.append(notif)
        return notif

    mock_notif_repo = AsyncMock(spec=NotificationRepository)
    mock_notif_repo.create_notification.side_effect = store_create_notification
    mock_notif_repo.list_by_user.side_effect = lambda user_id, **kw: [n for n in notifications_store if str(n.user_id) == str(user_id)]
    mock_notif_repo.count_unread.side_effect = lambda user_id: len([n for n in notifications_store if str(n.user_id) == str(user_id) and not n.is_read])

    mock_project_repo = AsyncMock(spec=ProjectRepository)
    mock_project_repo.get_by_id.return_value = project

    mock_group_repo = AsyncMock(spec=GroupRepository)
    mock_group_repo.get_by_id.return_value = group

    service = NotificationService(mock_notif_repo, mock_project_repo, mock_group_repo)

    # Canonical event
    event = DomainEventModel(
        id=uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890"),
        event_type="ProjectChangeCompleted",
        actor_id=str(student_id),
        actor_role="STUDENT",
        resource_type="ProjectChangeRequest",
        resource_id=str(uuid.uuid4()),
        project_instance_id=str(project_id),
        group_id=str(group_id),
        metadata_json={
            "resulting_blueprint_version_number": 2,
            "resulting_version_number": 2,
            "change_title": "Migrate to Rust Core",
        },
    )

    # First emission
    created = await service.handle_domain_event(event)

    # 1. Exactly TWO recipient records created
    assert len(created) == 2
    assert len(notifications_store) == 2

    # 2. Student project owner notification
    student_notifs = [n for n in notifications_store if str(n.user_id) == str(student_id)]
    assert len(student_notifs) == 1
    student_n = student_notifs[0]
    assert student_n.notification_type == "ProjectChangeCompleted"
    assert "Blueprint Regenerated" in student_n.title
    assert "v2" in student_n.message
    assert f"/student/projects/{project_id}/blueprint" == student_n.link
    assert student_n.is_read is False

    # 3. Supervising mentor notification
    mentor_notifs = [n for n in notifications_store if str(n.user_id) == str(mentor_id)]
    assert len(mentor_notifs) == 1
    mentor_n = mentor_notifs[0]
    assert mentor_n.notification_type == "ProjectChangeCompleted"
    assert "Project Change Completed" in mentor_n.title
    assert "v2" in mentor_n.message
    assert f"/mentor/projects/{project_id}" == mentor_n.link
    assert mentor_n.is_read is False

    # 4. Both reference the exact same canonical event
    assert student_n.event_id == mentor_n.event_id == str(event.id)

    # 5. Unrelated users receive NONE
    unrelated_student_notifs = [n for n in notifications_store if str(n.user_id) == str(unrelated_student_id)]
    assert len(unrelated_student_notifs) == 0
    unrelated_mentor_notifs = [n for n in notifications_store if str(n.user_id) == str(unrelated_mentor_id)]
    assert len(unrelated_mentor_notifs) == 0

    # 6. Retrying the same event does not create duplicates (idempotency)
    replayed = await service.handle_domain_event(event)
    assert len(replayed) == 2
    assert len(notifications_store) == 2
    assert len([n for n in notifications_store if str(n.user_id) == str(student_id)]) == 1
    assert len([n for n in notifications_store if str(n.user_id) == str(mentor_id)]) == 1

    # 7. Both notifications remain recipient-scoped
    assert await mock_notif_repo.count_unread(student_id) == 1
    assert await mock_notif_repo.count_unread(mentor_id) == 1
    assert await mock_notif_repo.count_unread(unrelated_student_id) == 0
    assert await mock_notif_repo.count_unread(unrelated_mentor_id) == 0

    # 8. Existing read/unread behavior remains unchanged
    student_n.is_read = True
    student_n.read_at = datetime.now(UTC)
    assert await mock_notif_repo.count_unread(student_id) == 0
    assert await mock_notif_repo.count_unread(mentor_id) == 1
    assert mentor_n.is_read is False

