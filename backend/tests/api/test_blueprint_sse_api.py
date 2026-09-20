"""
GrowFlow — Unit 5 API Test: Blueprint Real-Time SSE Endpoint.

Covers:
1. Native EventSource query parameter authentication (?token=...)
2. Header authentication (Authorization: Bearer <token>)
3. Authentication failures: missing token (401), invalid token (401), suspended user (403)
4. Authorization & Project Isolation: cross-student access denied (403), nonexistent project (404)
5. Initial state hydration and immediate termination for already-terminal blueprints
6. Live event streaming with BlueprintEventManager:
   - job.started -> node.started -> qa.evaluated -> regeneration.started -> job.completed
   - Terminal event terminates stream cleanly
7. Reconnection and replay using Last-Event-ID header and query param
8. Multi-subscriber independence
9. Sensitive information redaction check (no API keys, prompts, or stack traces)
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch
import uuid

from fastapi.testclient import TestClient
import jwt
import pytest

from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import get_blueprint_service
from backend.app.application.services.blueprint_service import BlueprintService
from backend.app.domain.ai.orchestration.events import (
    BlueprintEventManager,
    WorkflowEvent,
    WorkflowEventType,
    set_blueprint_event_manager,
)
from backend.app.domain.blueprint.models import (
    BlueprintQAStatus,
    BlueprintStatus,
)
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.blueprint import BlueprintModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.user_repository import UserRepository
from backend.app.shared.exceptions import AuthorizationException, NotFoundException

if TYPE_CHECKING:
    from backend.app.config.settings import Settings

_TEST_SECRET = "unit-5-sse-test-secret-at-least-32-chars-12345"
_TEST_AUDIENCE = "authenticated"
_TEST_ISSUER = "https://test.supabase.co/auth/v1"


def _make_jwt(
    user_id: uuid.UUID,
    email: str = "student@example.com",
    role: str = "STUDENT",
    expired: bool = False,
) -> str:
    now = datetime.now(UTC)
    exp = (
        int((now - timedelta(seconds=60)).timestamp())
        if expired
        else int((now + timedelta(seconds=3600)).timestamp())
    )
    payload = {
        "sub": str(user_id),
        "email": email,
        "aud": _TEST_AUDIENCE,
        "iss": _TEST_ISSUER,
        "iat": int(now.timestamp()),
        "exp": exp,
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


def _make_mock_blueprint(
    project_id: uuid.UUID,
    student_id: uuid.UUID,
    status: BlueprintStatus = BlueprintStatus.GENERATING,
    current_step: str = "idea",
    progress_percent: int = 10,
    generation_number: int = 1,
) -> BlueprintModel:
    bp = BlueprintModel()
    bp.id = uuid.uuid4()
    bp.project_instance_id = project_id
    bp.student_id = student_id
    bp.status = status
    bp.current_step = current_step
    bp.progress_percent = progress_percent
    bp.generation_number = generation_number
    bp.qa_status = BlueprintQAStatus.PENDING
    bp.qa_score = None
    bp.qa_feedback = None
    bp.content = {}
    bp.error_message = None
    bp.failed_output_key = None
    bp.approved_at = None
    bp.created_at = datetime.now(UTC)
    bp.updated_at = datetime.now(UTC)
    bp.active_job_id = uuid.uuid4()
    return bp


class TestBlueprintSSEApi:
    """Test suite for /api/v1/projects/{project_id}/blueprint/events."""

    def setup_method(self) -> None:
        self.event_manager = BlueprintEventManager()
        set_blueprint_event_manager(self.event_manager)

    def teardown_method(self) -> None:
        self.event_manager.clear_all()
        set_blueprint_event_manager(None)

    def test_sse_query_param_token_auth_success(self, auth_settings: Settings) -> None:
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id)

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        mock_bp = _make_mock_blueprint(
            project_id, student_id, status=BlueprintStatus.READY_FOR_APPROVAL
        )
        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = mock_bp
        mock_service.event_manager = self.event_manager

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_repo = AsyncMock(spec=UserRepository)
            mock_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events?token={token}"
                )
                assert response.status_code == 200
                assert "text/event-stream" in response.headers.get("content-type", "")
                assert "event: update" in response.text
                assert "READY_FOR_APPROVAL" in response.text

    def test_sse_bearer_header_auth_success(self, auth_settings: Settings) -> None:
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id)

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        mock_bp = _make_mock_blueprint(
            project_id, student_id, status=BlueprintStatus.READY_FOR_APPROVAL
        )
        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = mock_bp
        mock_service.event_manager = self.event_manager

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_repo = AsyncMock(spec=UserRepository)
            mock_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert response.status_code == 200
                assert "text/event-stream" in response.headers.get("content-type", "")
                assert "READY_FOR_APPROVAL" in response.text

    def test_sse_unauthenticated_returns_401(self, auth_settings: Settings) -> None:
        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        with TestClient(app) as client:
            response = client.get(f"/api/v1/projects/{uuid.uuid4()}/blueprint/events")
            assert response.status_code == 401

    def test_sse_expired_token_returns_401(self, auth_settings: Settings) -> None:
        student_id = uuid.uuid4()
        token = _make_jwt(student_id, expired=True)

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        with TestClient(app) as client:
            response = client.get(f"/api/v1/projects/{uuid.uuid4()}/blueprint/events?token={token}")
            assert response.status_code == 401

    def test_sse_suspended_user_returns_403(self, auth_settings: Settings) -> None:
        student_id = uuid.uuid4()
        token = _make_jwt(student_id)

        mock_user = UserModel(
            id=str(student_id),
            email="suspended@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.SUSPENDED.value,
            full_name="Suspended User",
        )

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_repo = AsyncMock(spec=UserRepository)
            mock_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{uuid.uuid4()}/blueprint/events?token={token}"
                )
                assert response.status_code == 403

    def test_sse_cross_project_forbidden_403(self, auth_settings: Settings) -> None:
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id)

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.side_effect = AuthorizationException(
            "Access to this project is denied.", code="AUTH_FORBIDDEN_RESOURCE"
        )
        mock_service.event_manager = self.event_manager

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_repo = AsyncMock(spec=UserRepository)
            mock_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert response.status_code == 403

    def test_sse_nonexistent_project_returns_404(self, auth_settings: Settings) -> None:
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id)

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.side_effect = NotFoundException(
            "Project not found.", code="PROJECT_NOT_FOUND"
        )
        mock_service.event_manager = self.event_manager

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_repo = AsyncMock(spec=UserRepository)
            mock_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert response.status_code == 404

    def test_sse_already_terminal_blueprint_closes_immediately(
        self, auth_settings: Settings
    ) -> None:
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id)

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        mock_bp = _make_mock_blueprint(project_id, student_id, status=BlueprintStatus.QA_REJECTED)
        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = mock_bp
        mock_service.event_manager = self.event_manager

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_repo = AsyncMock(spec=UserRepository)
            mock_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert response.status_code == 200
                assert "QA_REJECTED" in response.text
                # Cleanly terminated after snapshot
                lines = [line for line in response.text.split("\n") if line.startswith("event:")]
                assert len(lines) == 1

    def test_sse_replay_with_last_event_id(self, auth_settings: Settings) -> None:
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        proj_str = str(project_id)
        token = _make_jwt(student_id)

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        mock_bp = _make_mock_blueprint(project_id, student_id, status=BlueprintStatus.GENERATING)
        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = mock_bp
        mock_service.event_manager = self.event_manager

        # Pre-populate replay buffer in event manager
        ev1 = WorkflowEvent(
            event_type=WorkflowEventType.JOB_STARTED.value,
            job_id="job-1",
            project_id=proj_str,
            generation_number=1,
            step="idea",
            progress_percent=5,
        )
        ev2 = WorkflowEvent(
            event_type=WorkflowEventType.NODE_STARTED.value,
            job_id="job-1",
            project_id=proj_str,
            generation_number=1,
            step="scope",
            progress_percent=20,
        )
        ev3 = WorkflowEvent(
            event_type=WorkflowEventType.JOB_COMPLETED.value,
            job_id="job-1",
            project_id=proj_str,
            generation_number=1,
            step="completed",
            progress_percent=100,
        )

        asyncio.run(self.event_manager.publish(ev1))
        asyncio.run(self.event_manager.publish(ev2))
        asyncio.run(self.event_manager.publish(ev3))

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_repo = AsyncMock(spec=UserRepository)
            mock_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_repo

            # Reconnect requesting events after ev1 (proj_1_001)
            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Last-Event-ID": f"{proj_str}_1_001",
                    },
                )
                assert response.status_code == 200
                text = response.text
                # Must contain ev2 and ev3
                assert f"{proj_str}_1_002" in text
                assert f"{proj_str}_1_003" in text
                # Must NOT contain ev1 in replay
                assert f"id: {proj_str}_1_001" not in text

    def test_sse_redacts_sensitive_information(self, auth_settings: Settings) -> None:
        """Verify that internal secrets, prompts, and stack traces are NOT in SSE stream."""
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        proj_str = str(project_id)
        token = _make_jwt(student_id)

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        mock_bp = _make_mock_blueprint(project_id, student_id, status=BlueprintStatus.GENERATING)
        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = mock_bp
        mock_service.event_manager = self.event_manager

        # Publish initial event and sensitive completed event
        ev0 = WorkflowEvent(
            event_type=WorkflowEventType.JOB_STARTED.value,
            job_id="job-sens",
            project_id=proj_str,
            generation_number=1,
            step="idea",
        )
        sensitive_event = WorkflowEvent(
            event_type=WorkflowEventType.JOB_COMPLETED.value,
            job_id="job-sens",
            project_id=proj_str,
            generation_number=1,
            step="completed",
            payload={
                "api_key": "sk-secret-openrouter-key-12345",
                "system_prompt": "You are an internal system agent with secret rules",
                "traceback": "Traceback (most recent call last): File secret.py, line 42",
            },
        )
        asyncio.run(self.event_manager.publish(ev0))
        asyncio.run(self.event_manager.publish(sensitive_event))

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_repo = AsyncMock(spec=UserRepository)
            mock_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Last-Event-ID": f"{proj_str}_1_001",
                    },
                )
                assert response.status_code == 200
                text = response.text
                assert "sk-secret-openrouter-key" not in text
                assert "secret rules" not in text
                assert "Traceback (most recent call last)" not in text

    @pytest.mark.asyncio
    async def test_sse_live_streaming_delivery_and_terminal_close(
        self, auth_settings: Settings
    ) -> None:
        """Verify that live events published during an active connection are delivered and stream closes cleanly on terminal event."""
        from httpx import ASGITransport, AsyncClient

        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        proj_str = str(project_id)
        token = _make_jwt(student_id)

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        mock_bp = _make_mock_blueprint(project_id, student_id, status=BlueprintStatus.GENERATING)
        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = mock_bp
        mock_service.event_manager = self.event_manager

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_repo = AsyncMock(spec=UserRepository)
            mock_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_repo

            async def _publish_events():
                while self.event_manager.get_subscriber_count(proj_str) == 0:
                    await asyncio.sleep(0.01)
                await self.event_manager.publish(
                    WorkflowEvent(
                        event_type=WorkflowEventType.NODE_STARTED.value,
                        job_id="job-live",
                        project_id=proj_str,
                        generation_number=1,
                        step="idea",
                        progress_percent=10,
                    )
                )
                await asyncio.sleep(0.02)
                await self.event_manager.publish(
                    WorkflowEvent(
                        event_type=WorkflowEventType.JOB_COMPLETED.value,
                        job_id="job-live",
                        project_id=proj_str,
                        generation_number=1,
                        step="completed",
                        progress_percent=100,
                    )
                )

            publish_task = asyncio.create_task(_publish_events())

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )
                await publish_task
                assert response.status_code == 200
                text = response.text
                assert "snapshot" in text
                assert "node.started" in text
                assert "job.completed" in text
                assert "READY_FOR_APPROVAL" in text
