"""
GrowFlow Gate 05 — API Tests for Core Domain Foundation.

Tests HTTP endpoints across all Gate 05 domains:
- Unauthenticated requests return canonical 401
- Role-based authorization boundaries (Student vs Mentor) return canonical 403
- Users & User Preferences endpoints (/api/v1/users/me)
- Student Profile endpoints (/api/v1/students/me)
- Mentor Profile endpoints (/api/v1/mentors/me)
- Groups & Student Join endpoints (/api/v1/groups)
- Project Definitions & Versioning endpoints (/api/v1/project-definitions)
- Project Instances, Phase Transitions, and Overview (/api/v1/projects)
- Canonical envelope format verification
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
from backend.app.domain.organization.models import (
    GroupMembershipStatus,
    GroupStatus,
)
from backend.app.domain.project.models import (
    ProjectComplexity,
    ProjectDefinitionStatus,
    ProjectHealth,
    ProjectPhase,
    ProjectStatus,
)
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.organization import (
    GroupMembershipModel,
    GroupModel,
)
from backend.app.infrastructure.database.models.profile import (
    MentorProfileModel,
    StudentProfileModel,
    UserPreferenceModel,
)
from backend.app.infrastructure.database.models.project import (
    ProjectDefinitionModel,
    ProjectDefinitionVersionModel,
    ProjectInstanceModel,
)
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.user_repository import UserRepository
from backend.app.shared.exceptions import ConflictException, NotFoundException

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


# ============================================================================
# 1. UNAUTHENTICATED REQUESTS (401)
# ============================================================================


@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("GET", "/api/v1/users/me"),
        ("GET", "/api/v1/students/me"),
        ("GET", "/api/v1/mentors/me"),
        ("GET", "/api/v1/groups"),
        ("GET", "/api/v1/project-definitions"),
        ("GET", "/api/v1/project-definitions/catalog"),
        ("GET", "/api/v1/project-definitions/catalog/00000000-0000-0000-0000-000000000001"),
        ("POST", "/api/v1/project-definitions/catalog/00000000-0000-0000-0000-000000000001/select"),
        ("GET", "/api/v1/projects"),
    ],
)
def test_unauthenticated_requests_return_401(test_env: dict, method: str, endpoint: str) -> None:
    client: TestClient = test_env["client"]
    res = client.request(method, endpoint)
    assert res.status_code == 401
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "AUTH_MISSING_TOKEN"


# ============================================================================
# 2. ROLE-BASED ACCESS CONTROL (403 AUTH_FORBIDDEN_ROLE)
# ============================================================================


def test_student_forbidden_from_mentor_endpoints(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    student_id = uuid.uuid4()
    token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        # Student cannot access /api/v1/mentors/me
        res = client.get("/api/v1/mentors/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"

        # Student cannot create a group (POST /api/v1/groups)
        res = client.post(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "New Cohort"},
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"

        # Student cannot create a project definition (POST /api/v1/project-definitions)
        res = client.post(
            "/api/v1/project-definitions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Distributed Cache",
                "problem": "High DB latency",
                "proposed_solution": "Redis layer",
            },
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"


def test_mentor_forbidden_from_student_endpoints(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    mentor_id = uuid.uuid4()
    token = _make_jwt(mentor_id, role="MENTOR")
    mentor_user = UserModel(
        id=str(mentor_id),
        email="mentor@example.com",
        role=UserRole.MENTOR.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = mentor_user

        # Mentor cannot access /api/v1/students/me
        res = client.get("/api/v1/students/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"

        # Mentor cannot create a student project instance directly (POST /api/v1/projects)
        res = client.post(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "My Project",
                "problem": "P",
                "proposed_solution": "S",
            },
        )
        # Mentor cannot access student catalog (GET /api/v1/project-definitions/catalog)
        res = client.get(
            "/api/v1/project-definitions/catalog",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"

        dummy_def_id = uuid.uuid4()
        # Mentor cannot access student catalog detail (GET /api/v1/project-definitions/catalog/{id})
        res_detail = client.get(
            f"/api/v1/project-definitions/catalog/{dummy_def_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_detail.status_code == 403
        assert res_detail.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"

        # Mentor cannot select a project definition as student (POST /api/v1/project-definitions/catalog/{id}/select)
        res_select = client.post(
            f"/api/v1/project-definitions/catalog/{dummy_def_id}/select",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_select.status_code == 403
        assert res_select.json()["error"]["code"] == "AUTH_FORBIDDEN_ROLE"


# ============================================================================
# 3. USER PROFILE & PREFERENCES ENDPOINTS
# ============================================================================


def test_get_and_patch_user_self(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    profile_svc: AsyncMock = test_env["profile_svc"]

    user_id = uuid.uuid4()
    token = _make_jwt(user_id, email="alice@example.com", role="STUDENT")
    user = UserModel(
        id=str(user_id),
        email="alice@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
        full_name="Alice Smith",
        avatar_url=None,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = user
        profile_svc.get_user_self.return_value = user

        # GET /api/v1/users/me
        res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["email"] == "alice@example.com"
        assert data["full_name"] == "Alice Smith"

        # PATCH /api/v1/users/me
        updated_user = UserModel(
            id=str(user_id),
            email="alice@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Alice Wonder",
            avatar_url="https://img.example.com/alice.png",
        )
        profile_svc.update_user_self.return_value = updated_user
        res = client.patch(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "full_name": "Alice Wonder",
                "avatar_url": "https://img.example.com/alice.png",
            },
        )
        assert res.status_code == 200
        assert res.json()["data"]["full_name"] == "Alice Wonder"


def test_user_preferences_flow(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    profile_svc: AsyncMock = test_env["profile_svc"]

    user_id = uuid.uuid4()
    token = _make_jwt(user_id, role="STUDENT")
    user = UserModel(
        id=str(user_id),
        email="test@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = user

        pref = UserPreferenceModel(
            user_id=str(user_id),
            email_notifications=True,
            timezone="UTC",
            preferences={"theme": "DARK"},
        )
        profile_svc.get_or_create_preferences.return_value = pref
        profile_svc.update_preferences.return_value = pref

        # GET /api/v1/users/me/preferences
        res = client.get(
            "/api/v1/users/me/preferences",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        assert res.json()["data"]["email_notifications"] is True

        # PATCH /api/v1/users/me/preferences
        res = client.patch(
            "/api/v1/users/me/preferences",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email_notifications": False,
                "timezone": "America/New_York",
                "preferences": {"theme": "LIGHT"},
            },
        )
        assert res.status_code == 200


def test_student_profile_endpoints(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    profile_svc: AsyncMock = test_env["profile_svc"]

    student_id = uuid.uuid4()
    token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="stu@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        stu_profile = StudentProfileModel(
            user_id=str(student_id),
            student_id="STU-001",
            bio="Aspiring engineer",
            goals="Master cloud systems",
            interests="Distributed systems, AI",
        )
        profile_svc.get_or_create_student_profile.return_value = (
            stu_profile,
            [],
        )
        profile_svc.update_student_profile.return_value = (stu_profile, [])

        # GET /api/v1/students/me
        res = client.get("/api/v1/students/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["data"]["student_id"] == "STU-001"
        assert res.json()["data"]["bio"] == "Aspiring engineer"

        # PATCH /api/v1/students/me
        res = client.patch(
            "/api/v1/students/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"bio": "Updated bio", "goals": "New goals"},
        )
        assert res.status_code == 200


def test_mentor_profile_endpoints(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    profile_svc: AsyncMock = test_env["profile_svc"]

    mentor_id = uuid.uuid4()
    token = _make_jwt(mentor_id, role="MENTOR")
    mentor_user = UserModel(
        id=str(mentor_id),
        email="mentor@example.com",
        role=UserRole.MENTOR.value,
        status=AccountStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = mentor_user

        mentor_profile = MentorProfileModel(
            user_id=str(mentor_id),
            mentor_id="MEN-001",
            bio="Senior Engineer",
            specialization="Cloud Infrastructure",
        )
        profile_svc.get_or_create_mentor_profile.return_value = mentor_profile
        profile_svc.update_mentor_profile.return_value = mentor_profile

        # GET /api/v1/mentors/me
        res = client.get("/api/v1/mentors/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["data"]["mentor_id"] == "MEN-001"

        # PATCH /api/v1/mentors/me
        res = client.patch(
            "/api/v1/mentors/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "bio": "Updated bio",
                "specialization": "Kubernetes & Scalability",
            },
        )
        assert res.status_code == 200


# ============================================================================
# 4. GROUP LIFECYCLE & JOIN FLOW
# ============================================================================


def test_group_creation_and_join_flow(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    group_svc: AsyncMock = test_env["group_svc"]

    mentor_id = uuid.uuid4()
    student_id = uuid.uuid4()
    mentor_token = _make_jwt(mentor_id, role="MENTOR")
    student_token = _make_jwt(student_id, role="STUDENT")

    group_id = uuid.uuid4()
    group = GroupModel(
        id=group_id,
        mentor_id=str(mentor_id),
        name="Cohort 2026",
        join_code="JOIN1234",
        status=GroupStatus.ACTIVE.value,
    )

    # 1. Mentor creates group
    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = UserModel(
            id=str(mentor_id),
            email="mentor@example.com",
            role=UserRole.MENTOR.value,
            status=AccountStatus.ACTIVE.value,
        )
        group_svc.create_group.return_value = group

        res = client.post(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {mentor_token}"},
            json={"name": "Cohort 2026"},
        )
        assert res.status_code == 201
        assert res.json()["data"]["name"] == "Cohort 2026"
        assert res.json()["data"]["join_code"] == "JOIN1234"

    # 2. Student joins group with join code
    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
        )
        membership = GroupMembershipModel(
            id=uuid.uuid4(),
            group_id=str(group_id),
            student_id=str(student_id),
            status=GroupMembershipStatus.ACTIVE.value,
        )
        group_svc.join_group.return_value = membership

        res = client.post(
            "/api/v1/groups/join",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"join_code": "JOIN1234"},
        )
        assert res.status_code == 200
        assert res.json()["data"]["group_id"] == str(group_id)
        assert res.json()["data"]["status"] == "ACTIVE"


# ============================================================================
# 5. PROJECT DEFINITION IMMUTABLE VERSIONING & ASSIGNMENT
# ============================================================================


def test_project_definition_creation_and_immutability(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    def_svc: AsyncMock = test_env["def_svc"]

    mentor_id = uuid.uuid4()
    mentor_token = _make_jwt(mentor_id, role="MENTOR")
    mentor_user = UserModel(
        id=str(mentor_id),
        email="mentor@example.com",
        role=UserRole.MENTOR.value,
        status=AccountStatus.ACTIVE.value,
    )

    def_id = uuid.uuid4()
    ver1_id = uuid.uuid4()
    definition = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(mentor_id),
        name="Microservices Architecture",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver1_id),
    )
    version_1 = ProjectDefinitionVersionModel(
        id=ver1_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="Microservices Architecture",
        problem="Monolith bottlenecks",
        proposed_solution="Service decomposition",
        created_by=str(mentor_id),
        complexity=ProjectComplexity.INTERMEDIATE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = mentor_user
        def_svc.create_definition.return_value = (definition, version_1)
        def_svc.get_definition.return_value = (definition, version_1)

        # POST /api/v1/project-definitions (Create definition -> produces v1)
        res = client.post(
            "/api/v1/project-definitions",
            headers={"Authorization": f"Bearer {mentor_token}"},
            json={
                "name": "Microservices Architecture",
                "problem": "Monolith bottlenecks",
                "proposed_solution": "Service decomposition",
                "complexity": "INTERMEDIATE",
            },
        )
        assert res.status_code == 201
        data = res.json()["data"]
        assert data["name"] == "Microservices Architecture"
        assert data["current_version"]["version_number"] == 1

        # PATCH /api/v1/project-definitions/{id} (Updates definition -> produces v2)
        ver2_id = uuid.uuid4()
        version_2 = ProjectDefinitionVersionModel(
            id=ver2_id,
            project_definition_id=str(def_id),
            version_number=2,
            name="Microservices Architecture v2",
            problem="Monolith bottlenecks",
            proposed_solution="Service decomposition with Kafka",
            created_by=str(mentor_id),
            complexity=ProjectComplexity.ADVANCED.value,
        )
        def_svc.update_definition.return_value = (definition, version_2)

        res = client.patch(
            f"/api/v1/project-definitions/{def_id}",
            headers={"Authorization": f"Bearer {mentor_token}"},
            json={
                "name": "Microservices Architecture v2",
                "proposed_solution": "Service decomposition with Kafka",
                "complexity": "ADVANCED",
            },
        )
        assert res.status_code == 200
        assert res.json()["data"]["current_version"]["version_number"] == 2


def test_student_mentor_project_catalog(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    def_svc: AsyncMock = test_env["def_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    mentor_1_id = uuid.uuid4()
    mentor_2_id = uuid.uuid4()

    def_1_id = uuid.uuid4()
    ver_1_id = uuid.uuid4()
    def_1 = ProjectDefinitionModel(
        id=def_1_id,
        owner_mentor_id=str(mentor_1_id),
        name="Autonomous Solar Rover",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_1_id),
    )
    ver_1 = ProjectDefinitionVersionModel(
        id=ver_1_id,
        project_definition_id=str(def_1_id),
        version_number=1,
        name="Autonomous Solar Rover",
        problem="Remote terrain monitoring bottlenecks",
        proposed_solution="Solar-powered autonomous rover",
        created_by=str(mentor_1_id),
        complexity=ProjectComplexity.INTERMEDIATE.value,
        description="Build an autonomous ground rover",
        duration="8 weeks",
        constraints="Budget limit $500",
        assumptions="Sunlight available",
        technology_snapshot=[{"name": "ROS2"}, {"name": "Python"}],
    )

    def_2_id = uuid.uuid4()
    ver_2_id = uuid.uuid4()
    def_2 = ProjectDefinitionModel(
        id=def_2_id,
        owner_mentor_id=str(mentor_2_id),
        name="Compiler Optimization Pipeline",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_2_id),
    )
    ver_2 = ProjectDefinitionVersionModel(
        id=ver_2_id,
        project_definition_id=str(def_2_id),
        version_number=2,
        name="Compiler Optimization Pipeline",
        problem="Matrix vectorization bottlenecks",
        proposed_solution="Custom LLVM passes",
        created_by=str(mentor_2_id),
        complexity=ProjectComplexity.ADVANCED.value,
        description="High-performance code generation",
        duration="12 weeks",
        constraints="LLVM 18+",
        assumptions="Target x86_64",
        technology_snapshot=[{"name": "C++"}, {"name": "LLVM"}],
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        # 1. Populated catalog from multiple mentors
        def_svc.list_catalog.return_value = [(def_1, ver_1), (def_2, ver_2)]

        res = client.get(
            "/api/v1/project-definitions/catalog",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["message"] == "Mentor project catalog retrieved."
        items = body["data"]
        assert len(items) == 2

        item1 = items[0]
        assert item1["id"] == str(def_1_id)
        assert item1["name"] == "Autonomous Solar Rover"
        assert item1["status"] == "ACTIVE"
        assert item1["version_number"] == 1
        assert item1["problem"] == "Remote terrain monitoring bottlenecks"
        assert item1["proposed_solution"] == "Solar-powered autonomous rover"
        assert item1["complexity"] == "INTERMEDIATE"
        assert item1["description"] == "Build an autonomous ground rover"
        assert len(item1["technology_snapshot"]) == 2

        # Forbidden fields must NOT be exposed
        assert "owner_mentor_id" not in item1
        assert "created_by" not in item1
        assert "current_version_id" not in item1
        assert "student_id" not in item1

        item2 = items[1]
        assert item2["id"] == str(def_2_id)
        assert item2["name"] == "Compiler Optimization Pipeline"
        assert item2["complexity"] == "ADVANCED"
        assert item2["version_number"] == 2

        # 2. Empty catalog returns valid empty collection
        def_svc.list_catalog.return_value = []
        res_empty = client.get(
            "/api/v1/project-definitions/catalog",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res_empty.status_code == 200
        assert res_empty.json()["data"] == []


def test_student_mentor_project_detail_api(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    def_svc: AsyncMock = test_env["def_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    mentor_id = uuid.uuid4()
    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()
    definition = ProjectDefinitionModel(
        id=def_id,
        owner_mentor_id=str(mentor_id),
        name="Autonomous Solar Rover",
        status=ProjectDefinitionStatus.ACTIVE.value,
        current_version_id=str(ver_id),
    )
    version = ProjectDefinitionVersionModel(
        id=ver_id,
        project_definition_id=str(def_id),
        version_number=1,
        name="Autonomous Solar Rover",
        problem="Remote terrain monitoring bottlenecks",
        proposed_solution="Solar-powered autonomous rover",
        created_by=str(mentor_id),
        complexity=ProjectComplexity.INTERMEDIATE.value,
        description="Build an autonomous ground rover",
        duration="8 weeks",
        constraints="Budget limit $500",
        assumptions="Sunlight available",
        technology_snapshot=[{"name": "ROS2"}],
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        # 1. Student retrieves ACTIVE definition detail (200 OK)
        def_svc.get_catalog_item.return_value = (definition, version)
        res = client.get(
            f"/api/v1/project-definitions/catalog/{def_id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["message"] == "Mentor project definition detail retrieved."
        data = body["data"]
        assert data["id"] == str(def_id)
        assert data["name"] == "Autonomous Solar Rover"
        assert data["status"] == "ACTIVE"
        assert data["version_number"] == 1
        assert data["problem"] == "Remote terrain monitoring bottlenecks"
        assert data["proposed_solution"] == "Solar-powered autonomous rover"
        assert data["complexity"] == "INTERMEDIATE"
        assert data["description"] == "Build an autonomous ground rover"
        assert data["duration"] == "8 weeks"
        assert data["constraints"] == "Budget limit $500"
        assert data["assumptions"] == "Sunlight available"
        assert len(data["technology_snapshot"]) == 1

        # Mentor-private fields must NOT be leaked
        assert "owner_mentor_id" not in data
        assert "created_by" not in data
        assert "current_version_id" not in data
        assert "student_id" not in data

        # 2. Nonexistent definition -> 404
        def_svc.get_catalog_item.side_effect = NotFoundException(
            "Project definition not found.", code="PROJECT_DEFINITION_NOT_FOUND"
        )
        nonexistent_id = uuid.uuid4()
        res_404 = client.get(
            f"/api/v1/project-definitions/catalog/{nonexistent_id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res_404.status_code == 404
        assert res_404.json()["error"]["code"] == "PROJECT_DEFINITION_NOT_FOUND"

        # 3. Missing/invalid version snapshot -> 404 safe
        def_svc.get_catalog_item.side_effect = NotFoundException(
            "Project definition version not found.", code="PROJECT_DEFINITION_NO_VERSION"
        )
        res_no_ver = client.get(
            f"/api/v1/project-definitions/catalog/{def_id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res_no_ver.status_code == 404
        assert res_no_ver.json()["error"]["code"] == "PROJECT_DEFINITION_NO_VERSION"


def test_student_mentor_project_selection_api(test_env: dict) -> None:
    client: TestClient = test_env["client"]
    def_svc: AsyncMock = test_env["def_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="student@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    mentor_id = uuid.uuid4()
    def_id = uuid.uuid4()
    ver_id = uuid.uuid4()
    instance_id = uuid.uuid4()

    instance = ProjectInstanceModel(
        id=instance_id,
        student_id=str(student_id),
        project_definition_id=str(def_id),
        source_definition_version_id=str(ver_id),
        name="Autonomous Solar Rover",
        problem="Remote terrain monitoring bottlenecks",
        proposed_solution="Solar-powered autonomous rover",
        complexity=ProjectComplexity.INTERMEDIATE.value,
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
        progress_percentage=0,
        status=ProjectStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user

        # 1. Student selects ACTIVE definition (201 Created)
        def_svc.select_definition.return_value = instance
        res = client.post(
            f"/api/v1/project-definitions/catalog/{def_id}/select",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 201
        body = res.json()
        assert body["success"] is True
        assert body["message"] == "Mentor project selected successfully."
        data = body["data"]
        assert data["id"] == str(instance_id)
        assert data["student_id"] == str(student_id)
        assert data["project_definition_id"] == str(def_id)
        assert data["source_definition_version_id"] == str(ver_id)
        assert data["current_phase"] == "IDEA"
        assert data["health"] == "HEALTHY"
        assert data["status"] == "ACTIVE"
        assert data["progress_percentage"] == 0

        # 2. Duplicate active selection -> 409 Conflict
        def_svc.select_definition.side_effect = ConflictException(
            "Student already has an active instance of this project definition.",
            code="PROJECT_ALREADY_SELECTED",
        )
        res_dup = client.post(
            f"/api/v1/project-definitions/catalog/{def_id}/select",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res_dup.status_code == 409
        dup_body = res_dup.json()
        assert dup_body["success"] is False
        assert dup_body["error"]["code"] == "PROJECT_ALREADY_SELECTED"


# ============================================================================
# 6. PROJECT INSTANCE LIFECYCLE & OVERVIEW
# ============================================================================


def test_project_instance_creation_and_phase_transition(
    test_env: dict,
) -> None:
    client: TestClient = test_env["client"]
    proj_svc: AsyncMock = test_env["proj_svc"]

    student_id = uuid.uuid4()
    student_token = _make_jwt(student_id, role="STUDENT")
    student_user = UserModel(
        id=str(student_id),
        email="stu@example.com",
        role=UserRole.STUDENT.value,
        status=AccountStatus.ACTIVE.value,
    )

    proj_id = uuid.uuid4()
    project = ProjectInstanceModel(
        id=proj_id,
        student_id=str(student_id),
        name="Smart Grid",
        problem="Energy loss",
        proposed_solution="IoT load balancer",
        complexity=ProjectComplexity.INTERMEDIATE.value,
        current_phase=ProjectPhase.IDEA.value,
        health=ProjectHealth.HEALTHY.value,
        progress_percentage=0,
        status=ProjectStatus.ACTIVE.value,
    )

    with patch.object(UserRepository, "get_by_id", new_callable=AsyncMock) as mock_user:
        mock_user.return_value = student_user
        proj_svc.create_project.return_value = project
        proj_svc.get_project.return_value = project

        # 1. Create project (POST /api/v1/projects)
        res = client.post(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "name": "Smart Grid",
                "problem": "Energy loss",
                "proposed_solution": "IoT load balancer",
            },
        )
        assert res.status_code == 201
        assert res.json()["data"]["current_phase"] == "IDEA"
        assert res.json()["data"]["health"] == "HEALTHY"

        # 2. Transition phase: IDEA -> ASSESSMENT (Valid next transition)
        project_assessment = ProjectInstanceModel(
            id=proj_id,
            student_id=str(student_id),
            name="Smart Grid",
            problem="Energy loss",
            proposed_solution="IoT load balancer",
            complexity=ProjectComplexity.INTERMEDIATE.value,
            current_phase=ProjectPhase.ASSESSMENT.value,
            health=ProjectHealth.HEALTHY.value,
            progress_percentage=12,
            status=ProjectStatus.ACTIVE.value,
        )
        proj_svc.transition_phase.return_value = project_assessment

        res = client.post(
            f"/api/v1/projects/{proj_id}/phase",
            headers={"Authorization": f"Bearer {student_token}"},
            json={
                "target_phase": "ASSESSMENT",
                "reason": "Moved to assessment",
            },
        )
        assert res.status_code == 200
        assert res.json()["data"]["current_phase"] == "ASSESSMENT"

        # 3. Get Project Overview Aggregator (GET /api/v1/projects/{id}/overview)
        overview_data = {
            "id": str(proj_id),
            "student_id": str(student_id),
            "name": "Smart Grid",
            "problem": "Energy loss",
            "proposed_solution": "IoT load balancer",
            "complexity": "INTERMEDIATE",
            "current_phase": ProjectPhase.ASSESSMENT.value,
            "health": ProjectHealth.HEALTHY.value,
            "progress_percentage": 12,
            "status": "ACTIVE",
            "profile": {
                "objective": "Zero-loss power distribution",
            },
            "technologies": [],
            "recent_activity": {},
        }
        proj_svc.get_project_overview.return_value = overview_data

        res = client.get(
            f"/api/v1/projects/{proj_id}/overview",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert res.status_code == 200
        ov = res.json()["data"]
        assert ov["current_phase"] == "ASSESSMENT"
        assert ov["health"] == "HEALTHY"
        assert ov["profile"]["objective"] == "Zero-loss power distribution"
