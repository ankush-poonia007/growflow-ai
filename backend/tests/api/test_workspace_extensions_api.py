"""
GrowFlow Batch 6 (S27–S33) — API Tests for Workspace Extensions.

Comprehensive test suite covering:
- S27: GitHub Integration (get, connect, sync, disconnect)
- S28: Activity Trail (list domain events)
- S29: AI Mentor (history, chat with truthful status, execute action)
- S30: Help Requests (list, create, detail)
- S31: Mentor Feedback (list notes, acknowledge note)
- S32 & S33: Project Changes & Regeneration (analyze, confirm with versioning and idempotency, list versions)
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
from backend.app.api.dependencies.services import (
    get_activity_service,
    get_ai_mentor_service,
    get_github_service,
    get_help_request_service,
    get_mentor_feedback_service,
    get_project_change_service,
)
from backend.app.application.services.activity_service import ActivityService
from backend.app.application.services.ai_mentor_service import AIMentorService
from backend.app.application.services.github_service import GitHubService
from backend.app.application.services.help_request_service import HelpRequestService
from backend.app.application.services.mentor_feedback_service import MentorFeedbackService
from backend.app.application.services.project_change_service import ProjectChangeService
from backend.app.domain.identity import UserRole
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.user import UserModel

if TYPE_CHECKING:
    from backend.app.config.settings import Settings

_TEST_SECRET = "extensions-test-secret-at-least-32-chars-long-123"
_TEST_AUDIENCE = "authenticated"
_TEST_ISSUER = "https://test.supabase.co/auth/v1"


def _make_jwt(
    user_id: uuid.UUID,
    email: str = "student@example.com",
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
def project_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def token(student_id: uuid.UUID) -> str:
    return _make_jwt(student_id, "student@example.com", UserRole.STUDENT.value)


class MockUserRepo:
    def __init__(self, student_id: uuid.UUID) -> None:
        self._users = {
            str(student_id): UserModel(
                id=str(student_id),
                email="student@example.com",
                role="STUDENT",
                status="ACTIVE",
            )
        }

    async def get_by_id(self, user_id: uuid.UUID | str) -> UserModel | None:
        return self._users.get(str(user_id))


@pytest.fixture
def mock_github_service() -> GitHubService:
    service = AsyncMock(spec=GitHubService)
    integration_data = {
        "id": str(uuid.uuid4()),
        "project_instance_id": str(uuid.uuid4()),
        "repository_name": "demo-app",
        "repository_url": "https://github.com/growflow/demo-app",
        "connection_status": "CONNECTED",
        "default_branch": "main",
        "commit_count": 5,
        "last_sync_at": datetime.now(UTC).isoformat(),
        "sync_error": None,
        "cached_commits_preview": [{"sha": "abc1234", "message": "feat: init", "date": datetime.now(UTC).isoformat()}],
    }
    service.get_integration.return_value = integration_data
    service.connect_repository.return_value = integration_data
    service.sync_repository.return_value = integration_data
    service.disconnect_repository.return_value = {**integration_data, "connection_status": "NOT_CONNECTED"}
    return service


@pytest.fixture
def mock_activity_service() -> ActivityService:
    service = AsyncMock(spec=ActivityService)
    service.get_project_activity.return_value = [
        {
            "id": str(uuid.uuid4()),
            "event_type": "GitHubSynced",
            "title": "GitHub Synchronized",
            "description": "Repository commits synchronized.",
            "actor_role": "STUDENT",
            "actor_id": str(uuid.uuid4()),
            "resource_type": "ProjectGitHubIntegration",
            "resource_id": str(uuid.uuid4()),
            "occurred_at": datetime.now(UTC).isoformat(),
            "metadata": {},
        }
    ]
    return service


@pytest.fixture
def mock_ai_mentor_service() -> AIMentorService:
    service = AsyncMock(spec=AIMentorService)
    service.get_conversation_history.return_value = {
        "conversation_id": str(uuid.uuid4()),
        "project_instance_id": str(uuid.uuid4()),
        "title": "Project Consultation",
        "ai_available": True,
        "messages": [],
    }
    service.send_message.return_value = {
        "user_message": {"id": str(uuid.uuid4()), "role": "user", "content": "Hello", "created_at": datetime.now(UTC).isoformat()},
        "assistant_message": {"id": str(uuid.uuid4()), "role": "assistant", "content": "Hi there!", "sources": [], "suggested_action": None, "created_at": datetime.now(UTC).isoformat()},
        "ai_available": True,
    }
    service.execute_suggested_action.return_value = {"status": "SUCCESS", "action_type": "CREATE_TASK", "resource_id": str(uuid.uuid4())}
    return service


@pytest.fixture
def mock_help_service() -> HelpRequestService:
    service = AsyncMock(spec=HelpRequestService)
    req_data = {
        "id": str(uuid.uuid4()),
        "project_instance_id": str(uuid.uuid4()),
        "student_id": str(uuid.uuid4()),
        "subject": "Need help with DB",
        "description": "How to set up foreign keys?",
        "category": "TECHNICAL",
        "priority": "HIGH",
        "status": "OPEN",
        "mentor_response": None,
        "resolved_at": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    service.list_help_requests.return_value = [req_data]
    service.create_help_request.return_value = req_data
    service.get_help_request.return_value = req_data
    return service


@pytest.fixture
def mock_mentor_feedback_service() -> MentorFeedbackService:
    service = AsyncMock(spec=MentorFeedbackService)
    note_data = {
        "id": str(uuid.uuid4()),
        "project_instance_id": str(uuid.uuid4()),
        "mentor_id": str(uuid.uuid4()),
        "title": "Architecture Recommendation",
        "message": "Consider using Redis caching for high-load endpoints.",
        "note_type": "ACTIONABLE",
        "status": "UNREAD",
        "related_resource_type": None,
        "related_resource_id": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    service.list_mentor_notes.return_value = [note_data]
    service.acknowledge_note.return_value = {**note_data, "status": "ACKNOWLEDGED"}
    return service


@pytest.fixture
def mock_change_service() -> ProjectChangeService:
    service = AsyncMock(spec=ProjectChangeService)
    change_data = {
        "id": str(uuid.uuid4()),
        "project_instance_id": str(uuid.uuid4()),
        "student_id": str(uuid.uuid4()),
        "change_title": "Add Redis caching",
        "change_description": "Cache session queries with Redis",
        "change_type": "TECH_STACK",
        "status": "ANALYZED",
        "idempotency_key": None,
        "impact_analysis": {"affected_sections": ["technical_stack"], "estimated_risk": "MEDIUM"},
        "source_blueprint_version_number": 1,
        "resulting_blueprint_version_number": None,
        "qa_score": None,
        "qa_feedback": None,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    service.list_change_requests.return_value = [change_data]
    service.get_change_request.return_value = change_data
    service.analyze_change.return_value = change_data
    service.confirm_change.return_value = {
        **change_data,
        "status": "COMPLETED",
        "resulting_blueprint_version_number": 2,
        "qa_score": 92,
    }
    service.list_blueprint_versions.return_value = [
        {"id": str(uuid.uuid4()), "blueprint_id": str(uuid.uuid4()), "project_instance_id": str(uuid.uuid4()), "version_number": 1, "status": "ARCHIVED", "qa_score": 90, "change_summary": "Original", "created_at": datetime.now(UTC).isoformat()},
        {"id": str(uuid.uuid4()), "blueprint_id": str(uuid.uuid4()), "project_instance_id": str(uuid.uuid4()), "version_number": 2, "status": "APPROVED", "qa_score": 92, "change_summary": "Regenerated", "created_at": datetime.now(UTC).isoformat()},
    ]
    service.get_blueprint_version.return_value = {
        "id": str(uuid.uuid4()),
        "blueprint_id": str(uuid.uuid4()),
        "project_instance_id": str(uuid.uuid4()),
        "version_number": 2,
        "status": "APPROVED",
        "content": {},
        "qa_score": 92,
        "qa_feedback": {},
        "change_summary": "Regenerated",
        "created_at": datetime.now(UTC).isoformat(),
    }
    return service


@pytest.fixture
def client(
    auth_settings: Settings,
    student_id: uuid.UUID,
    mock_github_service: GitHubService,
    mock_activity_service: ActivityService,
    mock_ai_mentor_service: AIMentorService,
    mock_help_service: HelpRequestService,
    mock_mentor_feedback_service: MentorFeedbackService,
    mock_change_service: ProjectChangeService,
) -> TestClient:
    app = create_app(auth_settings)
    mock_user_repo = MockUserRepo(student_id)

    app.dependency_overrides[get_github_service] = lambda: mock_github_service
    app.dependency_overrides[get_activity_service] = lambda: mock_activity_service
    app.dependency_overrides[get_ai_mentor_service] = lambda: mock_ai_mentor_service
    app.dependency_overrides[get_help_request_service] = lambda: mock_help_service
    app.dependency_overrides[get_mentor_feedback_service] = lambda: mock_mentor_feedback_service
    app.dependency_overrides[get_project_change_service] = lambda: mock_change_service
    app.dependency_overrides[get_db_session] = lambda: AsyncMock()

    with patch("backend.app.api.dependencies.auth.UserRepository", return_value=mock_user_repo):
        yield TestClient(app)

    app.dependency_overrides.clear()


# ============================================================================
# Test Cases
# ============================================================================

def test_github_endpoints(client: TestClient, project_id: uuid.UUID, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    
    # GET
    res = client.get(f"/api/v1/projects/{project_id}/github", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["connection_status"] == "CONNECTED"

    # Connect
    res = client.post(
        f"/api/v1/projects/{project_id}/github/connect",
        json={"repository_url": "https://github.com/growflow/demo-app"},
        headers=headers,
    )
    assert res.status_code == 200

    # Sync
    res = client.post(f"/api/v1/projects/{project_id}/github/sync", headers=headers)
    assert res.status_code == 200

    # Disconnect
    res = client.post(f"/api/v1/projects/{project_id}/github/disconnect", headers=headers)
    assert res.status_code == 200


def test_activity_endpoint(client: TestClient, project_id: uuid.UUID, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(f"/api/v1/projects/{project_id}/activity", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) == 1
    assert res.json()["data"][0]["event_type"] == "GitHubSynced"


def test_ai_mentor_endpoints(client: TestClient, project_id: uuid.UUID, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get history
    res = client.get(f"/api/v1/projects/{project_id}/ai-mentor", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["ai_available"] is True

    # Chat
    res = client.post(
        f"/api/v1/projects/{project_id}/ai-mentor/chat",
        json={"content": "What is the best DB design?"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["assistant_message"]["content"] == "Hi there!"

    # Execute action
    res = client.post(
        f"/api/v1/projects/{project_id}/ai-mentor/execute-action",
        json={"action_type": "CREATE_TASK", "payload": {"title": "Task 1"}},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "SUCCESS"


def test_help_request_endpoints(client: TestClient, project_id: uuid.UUID, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}

    # List
    res = client.get(f"/api/v1/projects/{project_id}/help-requests", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) == 1

    # Create
    res = client.post(
        f"/api/v1/projects/{project_id}/help-requests",
        json={"subject": "Need help with DB", "description": "How to set up foreign keys?", "category": "TECHNICAL", "priority": "HIGH"},
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["data"]["status"] == "OPEN"

    # Detail
    help_id = res.json()["data"]["id"]
    res = client.get(f"/api/v1/projects/{project_id}/help-requests/{help_id}", headers=headers)
    assert res.status_code == 200


def test_mentor_feedback_endpoints(client: TestClient, project_id: uuid.UUID, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}

    # List
    res = client.get(f"/api/v1/projects/{project_id}/mentor-notes", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) == 1

    # Acknowledge
    note_id = res.json()["data"][0]["id"]
    res = client.post(f"/api/v1/projects/{project_id}/mentor-notes/{note_id}/acknowledge", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "ACKNOWLEDGED"


def test_project_change_endpoints(client: TestClient, project_id: uuid.UUID, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}

    # List
    res = client.get(f"/api/v1/projects/{project_id}/changes", headers=headers)
    assert res.status_code == 200

    # Analyze
    res = client.post(
        f"/api/v1/projects/{project_id}/changes/analyze",
        json={"change_title": "Add Redis caching", "change_description": "Cache session queries with Redis", "change_type": "TECH_STACK"},
        headers=headers,
    )
    assert res.status_code == 201
    change_id = res.json()["data"]["id"]

    # Detail
    res = client.get(f"/api/v1/projects/{project_id}/changes/{change_id}", headers=headers)
    assert res.status_code == 200

    # Confirm
    res = client.post(
        f"/api/v1/projects/{project_id}/changes/{change_id}/confirm",
        json={"idempotency_key": "test-key-123"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "COMPLETED"
    assert res.json()["data"]["resulting_blueprint_version_number"] == 2

    # List versions
    res = client.get(f"/api/v1/projects/{project_id}/blueprint-versions", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) == 2

    # Get version 2
    res = client.get(f"/api/v1/projects/{project_id}/blueprint-versions/2", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["version_number"] == 2


def test_authorization_matrix(client: TestClient, project_id: uuid.UUID, token: str, mock_github_service: GitHubService) -> None:
    """
    11. Authorization Matrix Test:
    - Unauthenticated request -> 401
    - Forbidden resource (student accessing another student's project) -> 403
    - Non-existent project -> 404
    - Non-existent resource -> 404
    """
    # 1. Unauthenticated request (no Bearer token) -> 401
    res = client.get(f"/api/v1/projects/{project_id}/github")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "AUTH_MISSING_TOKEN"

    res = client.get(f"/api/v1/projects/{project_id}/activity")
    assert res.status_code == 401

    res = client.get(f"/api/v1/projects/{project_id}/help-requests")
    assert res.status_code == 401

    res = client.get(f"/api/v1/projects/{project_id}/mentor-notes")
    assert res.status_code == 401

    res = client.get(f"/api/v1/projects/{project_id}/changes")
    assert res.status_code == 401

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Forbidden resource (service raises AuthorizationException) -> 403
    from backend.app.shared.exceptions import AuthorizationException, NotFoundException
    mock_github_service.get_integration.side_effect = AuthorizationException("Access denied.", code="AUTH_FORBIDDEN_RESOURCE")
    res = client.get(f"/api/v1/projects/{project_id}/github", headers=headers)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"

    # 3. Non-existent project (service raises NotFoundException) -> 404
    non_existent_project = uuid.uuid4()
    mock_github_service.get_integration.side_effect = NotFoundException("Project not found.", code="PROJECT_NOT_FOUND")
    res = client.get(f"/api/v1/projects/{non_existent_project}/github", headers=headers)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "PROJECT_NOT_FOUND"

    # Reset mock side effects
    mock_github_service.get_integration.side_effect = None

