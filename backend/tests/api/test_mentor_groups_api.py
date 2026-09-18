"""
GrowFlow Phase 7 Batch 1 — Tests for Mentor Shell, Navigation & Group Endpoints.

Validates:
- GET /api/v1/groups/{group_id}/projects
  - 401 Unauthenticated
  - 403 Forbidden for non-supervising mentor
  - 200 OK with project list for supervising mentor
- GET /api/v1/mentors/overview
  - 401 Unauthenticated
  - 403 Forbidden for Student role
  - 200 OK with truthful aggregated metrics for Mentor
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
    get_mentor_overview_service,
    get_project_service,
)
from backend.app.application.services.mentor_overview_service import MentorOverviewService
from backend.app.application.services.project_service import ProjectService
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.identity.models import CurrentUser
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.shared.exceptions import AuthorizationException


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


def test_list_group_projects_unauthenticated(client: TestClient):
    """GET /api/v1/groups/{group_id}/projects returns 401 without auth token."""
    res = client.get(f"/api/v1/groups/{uuid.uuid4()}/projects")
    assert res.status_code == 401
    body = res.json()
    assert body["success"] is False


def test_list_group_projects_forbidden(
    client: TestClient,
    app,
    mentor_user: CurrentUser,
):
    """GET /api/v1/groups/{group_id}/projects returns 403 when mentor does not supervise the group."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user

    mock_project_service = AsyncMock(spec=ProjectService)
    mock_project_service.list_group_projects.side_effect = AuthorizationException(
        "You do not supervise this group.",
        code="AUTH_FORBIDDEN_RESOURCE",
    )
    app.dependency_overrides[get_project_service] = lambda: mock_project_service

    group_id = uuid.uuid4()
    res = client.get(f"/api/v1/groups/{group_id}/projects")
    assert res.status_code == 403
    body = res.json()
    assert body["success"] is False
    msg = body.get("message") or body.get("error", {}).get("message", "")
    assert "supervise" in msg


def test_list_group_projects_success(
    client: TestClient,
    app,
    mentor_user: CurrentUser,
):
    """GET /api/v1/groups/{group_id}/projects returns 200 with projects list."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user

    project_id = uuid.uuid4()
    mock_proj = ProjectInstanceModel(
        id=project_id,
        student_id=str(uuid.uuid4()),
        group_id=str(uuid.uuid4()),
        name="Telemetry Pipeline",
        problem="Lack of real-time monitoring",
        proposed_solution="Build distributed ingest pipeline",
        complexity="ADVANCED",
        current_phase="IMPLEMENTATION",
        health="HEALTHY",
        progress_percentage=45,
        status="ACTIVE",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_project_service = AsyncMock(spec=ProjectService)
    mock_project_service.list_group_projects.return_value = [mock_proj]
    app.dependency_overrides[get_project_service] = lambda: mock_project_service

    res = client.get(f"/api/v1/groups/{mock_proj.group_id}/projects")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["name"] == "Telemetry Pipeline"
    assert body["data"][0]["progress_percentage"] == 45


def test_mentor_overview_unauthenticated(client: TestClient):
    """GET /api/v1/mentors/overview returns 401 when unauthenticated."""
    res = client.get("/api/v1/mentors/overview")
    assert res.status_code == 401
    assert res.json()["success"] is False


def test_mentor_overview_forbidden_for_student(
    client: TestClient,
    app,
    student_user: CurrentUser,
):
    """GET /api/v1/mentors/overview returns 403 when user is a student."""
    app.dependency_overrides[get_current_user] = lambda: student_user

    res = client.get("/api/v1/mentors/overview")
    assert res.status_code == 403
    assert res.json()["success"] is False


def test_mentor_overview_success(
    client: TestClient,
    app,
    mentor_user: CurrentUser,
):
    """GET /api/v1/mentors/overview returns 200 with aggregated metrics."""
    app.dependency_overrides[get_current_user] = lambda: mentor_user

    mock_overview_service = AsyncMock(spec=MentorOverviewService)
    mock_overview_service.get_mentor_overview.return_value = {
        "total_groups": 2,
        "total_students": 14,
        "total_projects": 8,
        "at_risk_projects": 1,
        "groups": [
            {
                "id": str(uuid.uuid4()),
                "name": "Distributed Systems A",
                "join_code": "DS-2026-A",
                "status": "ACTIVE",
                "student_count": 8,
                "project_count": 4,
                "at_risk_count": 1,
                "created_at": "2026-09-01T10:00:00Z",
            }
        ],
    }
    app.dependency_overrides[get_mentor_overview_service] = lambda: mock_overview_service

    res = client.get("/api/v1/mentors/overview")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["total_groups"] == 2
    assert body["data"]["total_students"] == 14
    assert body["data"]["total_projects"] == 8
    assert body["data"]["at_risk_projects"] == 1
    assert len(body["data"]["groups"]) == 1
    assert body["data"]["groups"][0]["name"] == "Distributed Systems A"
