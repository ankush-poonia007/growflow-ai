"""
GrowFlow Batch S06 — API Tests for Student Project Profile & Information.

Tests HTTP endpoints:
- GET /api/v1/projects/{project_id}
- PATCH /api/v1/projects/{project_id}

Coverage:
1. Canonical retrieval by project owner (200 OK)
2. Cross-student access rejection (403 Forbidden)
3. Nonexistent project (404 Not Found)
4. Malformed UUID (422 Unprocessable Entity)
5. Successful partial update by owner (200 OK)
6. Non-owner update rejection (403 Forbidden)
7. Empty/whitespace project name validation (400 BusinessRuleException)
8. Invalid complexity enum validation (400 BusinessRuleException)
9. Mentor project instance isolation (preserves definition & version IDs)
10. Unauthenticated access rejection (401 Unauthorized)
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
    get_group_service,
    get_profile_service,
    get_project_definition_service,
    get_project_service,
)
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
)
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.user_repository import UserRepository
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    NotFoundException,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from backend.app.config.settings import Settings

_TEST_SECRET = "gate-05-test-secret-at-least-32-chars-long-123"
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


async def _mock_db_session() -> AsyncGenerator[AsyncMock, None]:
    mock_session = AsyncMock()
    yield mock_session


@pytest.fixture
def auth_settings(test_settings: Settings) -> Settings:
    test_settings.auth.JWT_SECRET = _TEST_SECRET
    test_settings.auth.JWT_AUDIENCE = _TEST_AUDIENCE
    test_settings.auth.JWT_ISSUER = _TEST_ISSUER
    test_settings.database.DATABASE_URL = None
    return test_settings


@pytest.fixture
def test_env(auth_settings: Settings) -> Generator[dict, None, None]:
    app = create_app(settings=auth_settings)
    app.dependency_overrides[get_db_session] = _mock_db_session

    mock_profile_svc = AsyncMock()
    mock_group_svc = AsyncMock()
    mock_def_svc = AsyncMock()
    mock_proj_svc = AsyncMock()

    app.dependency_overrides[get_profile_service] = lambda: mock_profile_svc
    app.dependency_overrides[get_group_service] = lambda: mock_group_svc
    app.dependency_overrides[get_project_definition_service] = lambda: mock_def_svc
    app.dependency_overrides[get_project_service] = lambda: mock_proj_svc

    with TestClient(app, base_url="http://testserver") as client:
        yield {
            "client": client,
            "profile_svc": mock_profile_svc,
            "group_svc": mock_group_svc,
            "def_svc": mock_def_svc,
            "proj_svc": mock_proj_svc,
        }
    app.dependency_overrides.clear()


def test_unauthenticated_project_profile_endpoints_return_401(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    proj_id = uuid.uuid4()

    res_get = client.get(f"/api/v1/projects/{proj_id}")
    assert res_get.status_code == 401

    res_patch = client.patch(f"/api/v1/projects/{proj_id}", json={"name": "New Name"})
    assert res_patch.status_code == 401


def test_get_project_profile_success(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    proj_svc: AsyncMock = test_env["proj_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    proj_id = uuid.uuid4()
    project = ProjectInstanceModel(
        id=str(proj_id),
        student_id=str(student_id),
        name="Autonomous Solar Rover",
        problem="Terrain monitoring bottlenecks",
        proposed_solution="Solar autonomous rover",
        complexity=ProjectComplexity.ADVANCED.value,
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
        progress_percentage=0,
        status=ProjectStatus.ACTIVE.value,
    )
    proj_svc.get_project.return_value = project

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        res = client.get(
            f"/api/v1/projects/{proj_id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["message"] == "Project retrieved."
        data = body["data"]
        assert data["id"] == str(proj_id)
        assert data["student_id"] == str(student_id)
        assert data["name"] == "Autonomous Solar Rover"
        assert data["complexity"] == "ADVANCED"
        assert data["current_phase"] == "IDEA"
        assert data["health"] == "HEALTHY"
        assert data["progress_percentage"] == 0
        assert data["status"] == "ACTIVE"


def test_get_project_profile_cross_student_denied(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    proj_svc: AsyncMock = test_env["proj_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    proj_id = uuid.uuid4()
    proj_svc.get_project.side_effect = AuthorizationException(
        "Access to this project is denied.", code="AUTH_FORBIDDEN_RESOURCE"
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        res = client.get(
            f"/api/v1/projects/{proj_id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_get_project_profile_not_found(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    proj_svc: AsyncMock = test_env["proj_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    proj_id = uuid.uuid4()
    proj_svc.get_project.side_effect = NotFoundException(
        "Project not found.", code="PROJECT_NOT_FOUND"
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        res = client.get(
            f"/api/v1/projects/{proj_id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "PROJECT_NOT_FOUND"


def test_get_project_profile_malformed_uuid(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user
        res = client.get(
            "/api/v1/projects/not-a-valid-uuid",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 422


def test_update_project_profile_success(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    proj_svc: AsyncMock = test_env["proj_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    proj_id = uuid.uuid4()
    updated_project = ProjectInstanceModel(
        id=str(proj_id),
        student_id=str(student_id),
        name="Updated Autonomous Solar Rover",
        problem="Updated problem statement",
        proposed_solution="Updated proposed solution",
        complexity=ProjectComplexity.ADVANCED.value,
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
        progress_percentage=0,
        status=ProjectStatus.ACTIVE.value,
    )
    proj_svc.update_project.return_value = updated_project

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        res = client.patch(
            f"/api/v1/projects/{proj_id}",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "name": "Updated Autonomous Solar Rover",
                "problem": "Updated problem statement",
                "proposed_solution": "Updated proposed solution",
                "complexity": "ADVANCED",
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["message"] == "Project updated."
        data = body["data"]
        assert data["name"] == "Updated Autonomous Solar Rover"
        assert data["problem"] == "Updated problem statement"
        assert data["proposed_solution"] == "Updated proposed solution"
        assert data["complexity"] == "ADVANCED"


def test_update_project_profile_forbidden_for_non_owner(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    proj_svc: AsyncMock = test_env["proj_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    proj_id = uuid.uuid4()
    proj_svc.update_project.side_effect = AuthorizationException(
        "Only the project owner may modify project details.",
        code="AUTH_FORBIDDEN_RESOURCE",
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        res = client.patch(
            f"/api/v1/projects/{proj_id}",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"name": "Hacked Name"},
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


def test_update_project_profile_validation_empty_name(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    proj_svc: AsyncMock = test_env["proj_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    proj_id = uuid.uuid4()
    proj_svc.update_project.side_effect = BusinessRuleException(
        "Project name cannot be empty.", code="PROJECT_INVALID_NAME"
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        res = client.patch(
            f"/api/v1/projects/{proj_id}",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"name": "   "},
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "PROJECT_INVALID_NAME"


def test_update_project_profile_validation_invalid_complexity(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    proj_svc: AsyncMock = test_env["proj_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    proj_id = uuid.uuid4()
    proj_svc.update_project.side_effect = BusinessRuleException(
        "Unknown complexity value: EXTREME.", code="PROJECT_INVALID_COMPLEXITY"
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        res = client.patch(
            f"/api/v1/projects/{proj_id}",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"complexity": "EXTREME"},
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "PROJECT_INVALID_COMPLEXITY"


def test_update_mentor_project_preserves_definition_immutability(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    proj_svc: AsyncMock = test_env["proj_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    proj_id = uuid.uuid4()
    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()

    # Pinned mentor project instance
    updated_project = ProjectInstanceModel(
        id=str(proj_id),
        student_id=str(student_id),
        project_definition_id=str(def_id),
        source_definition_version_id=str(ver_id),
        name="Student Custom Title for Mentor Project",
        problem="Updated student notes on problem",
        proposed_solution="Customized approach",
        complexity=ProjectComplexity.ADVANCED.value,
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
        progress_percentage=0,
        status=ProjectStatus.ACTIVE.value,
    )
    proj_svc.update_project.return_value = updated_project

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        res = client.patch(
            f"/api/v1/projects/{proj_id}",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"name": "Student Custom Title for Mentor Project"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        # Preserves pinned definition and version snapshot IDs
        assert data["project_definition_id"] == str(def_id)
        assert data["source_definition_version_id"] == str(ver_id)
        assert data["name"] == "Student Custom Title for Mentor Project"
