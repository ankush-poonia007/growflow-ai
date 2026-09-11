"""
GrowFlow Gate 04 — API Tests for Authentication & Security Foundation.

Tests the HTTP security boundary:
- 401 responses for missing, malformed, expired, invalid, and unknown user tokens.
- 403 responses for suspended accounts, inactive accounts, and insufficient roles.
- Canonical success & error response envelope structure.
- Role-based access control matrix (STUDENT, MENTOR, ADMIN).
- Resource-based ownership enforcement.
- Verification that tokens and secrets are never disclosed in responses or headers.
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
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.user_repository import UserRepository

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from backend.app.config.settings import Settings

_TEST_SECRET = "gate-04-test-secret-at-least-32-chars-long-123"
_TEST_AUDIENCE = "authenticated"
_TEST_ISSUER = "https://test.supabase.co/auth/v1"


def _make_jwt(
    user_id: uuid.UUID,
    email: str = "test@example.com",
    expires_in_seconds: int = 3600,
    secret: str = _TEST_SECRET,
    audience: str = _TEST_AUDIENCE,
    issuer: str = _TEST_ISSUER,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "email": email,
        "aud": audience,
        "iss": issuer,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


async def _mock_db_session() -> AsyncGenerator[AsyncMock, None]:
    """Provide a mock AsyncSession for fast, isolated API tests."""
    mock_session = AsyncMock()
    yield mock_session


@pytest.fixture
def auth_settings(test_settings: Settings) -> Settings:
    """Return test settings with known auth secrets."""
    test_settings.auth.JWT_SECRET = _TEST_SECRET
    test_settings.auth.JWT_AUDIENCE = _TEST_AUDIENCE
    test_settings.auth.JWT_ISSUER = _TEST_ISSUER
    test_settings.database.DATABASE_URL = None
    return test_settings


@pytest.fixture
def auth_client(auth_settings: Settings) -> Generator[TestClient, None, None]:
    """Test client configured with test auth settings and mocked DB session."""
    app = create_app(settings=auth_settings)
    app.dependency_overrides[get_db_session] = _mock_db_session
    with TestClient(app, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 1. Unauthenticated and Malformed Token Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_unauthenticated_request_returns_401(auth_client: TestClient) -> None:
    """Request without Authorization header returns canonical 401 AUTH_MISSING_TOKEN."""
    response = auth_client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_MISSING_TOKEN"
    assert data["data"] is None


@pytest.mark.api
def test_invalid_auth_header_format_returns_401(auth_client: TestClient) -> None:
    """Authorization header without 'Bearer ' prefix returns canonical 401 AUTH_INVALID_TOKEN_FORMAT."""
    response = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_INVALID_TOKEN_FORMAT"


@pytest.mark.api
def test_expired_token_returns_401(auth_client: TestClient) -> None:
    """Expired JWT returns canonical 401 AUTH_TOKEN_EXPIRED."""
    expired_token = _make_jwt(uuid.uuid4(), expires_in_seconds=-10)
    response = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_TOKEN_EXPIRED"


@pytest.mark.api
def test_invalid_signature_returns_401(auth_client: TestClient) -> None:
    """JWT signed with wrong secret returns canonical 401 AUTH_INVALID_SIGNATURE."""
    bad_token = _make_jwt(uuid.uuid4(), secret="different-secret-key-that-will-fail-validation")
    response = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {bad_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_INVALID_SIGNATURE"


# ---------------------------------------------------------------------------
# 2. Database Identity Lookup & Account Status Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_unknown_user_returns_401(auth_client: TestClient) -> None:
    """Valid token for user not present in DB returns canonical 401 AUTH_USER_NOT_FOUND."""
    user_id = uuid.uuid4()
    token = _make_jwt(user_id)

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        response = auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_USER_NOT_FOUND"


@pytest.mark.api
def test_suspended_user_returns_403(auth_client: TestClient) -> None:
    """User in SUSPENDED status returns canonical 403 AUTH_ACCOUNT_SUSPENDED."""
    user_id = uuid.uuid4()
    token = _make_jwt(user_id)
    suspended_user = UserModel(
        id=str(user_id),
        email="suspended@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.SUSPENDED.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = suspended_user
        response = auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_ACCOUNT_SUSPENDED"


@pytest.mark.api
def test_inactive_user_returns_403(auth_client: TestClient) -> None:
    """User in INACTIVE status returns canonical 403 AUTH_ACCOUNT_INACTIVE."""
    user_id = uuid.uuid4()
    token = _make_jwt(user_id)
    inactive_user = UserModel(
        id=str(user_id),
        email="inactive@example.com",
        role=UserRole.MENTOR.value,
        status=AccountStatus.INACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = inactive_user
        response = auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_ACCOUNT_INACTIVE"


# ---------------------------------------------------------------------------
# 3. Successful Authenticated Identity (/api/v1/auth/me)
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_authenticated_user_me_endpoint(auth_client: TestClient) -> None:
    """Valid authenticated request returns canonical 200 success response with profile."""
    user_id = uuid.uuid4()
    token = _make_jwt(user_id, email="alice@example.com")
    alice = UserModel(
        id=str(user_id),
        email="alice@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
        full_name="Alice Student",
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = alice
        response = auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == str(user_id)
    assert data["data"]["email"] == "alice@example.com"
    assert data["data"]["role"] == "STUDENT"
    assert data["data"]["status"] == "ACTIVE"
    assert data["data"]["full_name"] == "Alice Student"


# ---------------------------------------------------------------------------
# 4. Role Authorization Matrix Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_student_role_authorization_matrix(auth_client: TestClient) -> None:
    """
    STUDENT role:
    - Allowed on /student-only (200)
    - Denied on /mentor-only (403 AUTH_FORBIDDEN_ROLE)
    - Denied on /admin-only (403 AUTH_FORBIDDEN_ROLE)
    """
    user_id = uuid.uuid4()
    token = _make_jwt(user_id)
    student = UserModel(
        id=str(user_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = student

        # 1. Student endpoint -> 200
        res_student = auth_client.get(
            "/api/v1/auth/student-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_student.status_code == 200
        assert res_student.json()["success"] is True

        # 2. Mentor endpoint -> 403
        res_mentor = auth_client.get(
            "/api/v1/auth/mentor-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_mentor.status_code == 403
        assert res_mentor.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"

        # 3. Admin endpoint -> 403
        res_admin = auth_client.get(
            "/api/v1/auth/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_admin.status_code == 403
        assert res_admin.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"


@pytest.mark.api
def test_mentor_role_authorization_matrix(auth_client: TestClient) -> None:
    """
    MENTOR role:
    - Denied on /student-only (403 AUTH_FORBIDDEN_ROLE)
    - Allowed on /mentor-only (200)
    - Denied on /admin-only (403 AUTH_FORBIDDEN_ROLE)
    """
    user_id = uuid.uuid4()
    token = _make_jwt(user_id)
    mentor = UserModel(
        id=str(user_id),
        email="mentor@example.com",
        role=UserRole.MENTOR.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mentor

        # 1. Student endpoint -> 403
        res_student = auth_client.get(
            "/api/v1/auth/student-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_student.status_code == 403

        # 2. Mentor endpoint -> 200
        res_mentor = auth_client.get(
            "/api/v1/auth/mentor-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_mentor.status_code == 200

        # 3. Admin endpoint -> 403
        res_admin = auth_client.get(
            "/api/v1/auth/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_admin.status_code == 403


@pytest.mark.api
def test_admin_role_authorization_matrix(auth_client: TestClient) -> None:
    """
    ADMIN role:
    - Allowed on /admin-only (200)
    - Denied on student-specific workflows per 6D § 23 (403 AUTH_FORBIDDEN_ROLE)
    """
    user_id = uuid.uuid4()
    token = _make_jwt(user_id)
    admin = UserModel(
        id=str(user_id),
        email="admin@example.com",
        role=UserRole.ADMIN.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = admin

        # 1. Admin endpoint -> 200
        res_admin = auth_client.get(
            "/api/v1/auth/admin-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_admin.status_code == 200

        # 2. Student endpoint -> 403 (least privilege)
        res_student = auth_client.get(
            "/api/v1/auth/student-only",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_student.status_code == 403


# ---------------------------------------------------------------------------
# 5. Resource Ownership Authorization Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_resource_ownership_allowed_for_owner(auth_client: TestClient) -> None:
    """Owner can access their own resource ID."""
    user_id = uuid.uuid4()
    token = _make_jwt(user_id)
    user = UserModel(
        id=str(user_id),
        email="owner@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = user
        response = auth_client.get(
            f"/api/v1/auth/resource/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.api
def test_resource_ownership_denied_for_non_owner(auth_client: TestClient) -> None:
    """Accessing another user's resource ID returns 403 AUTH_FORBIDDEN_RESOURCE."""
    user_id = uuid.uuid4()
    other_id = uuid.uuid4()
    token = _make_jwt(user_id)
    user = UserModel(
        id=str(user_id),
        email="requester@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = user
        response = auth_client.get(
            f"/api/v1/auth/resource/{other_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AUTH_FORBIDDEN_RESOURCE"


# ---------------------------------------------------------------------------
# 6. Non-Disclosure & Security Defense Tests
# ---------------------------------------------------------------------------


@pytest.mark.api
def test_error_response_does_not_leak_secrets(auth_client: TestClient) -> None:
    """Failed authentication responses never disclose verification secret or token internals."""
    response = auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert response.status_code == 401
    body_text = response.text
    assert _TEST_SECRET not in body_text
    assert "Traceback" not in body_text
