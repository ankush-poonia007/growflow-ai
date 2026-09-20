"""
GrowFlow Phase 8 / Batch 4 — Targeted Tests for Background Jobs, SSE & Reliability Hardening.

Covers:
1. Orphan RUNNING job recovery transitions to FAILED with truthful error on startup.
2. Associated GENERATING blueprint transitions to FAILED; terminal jobs preserved.
3. Job progress synchronization during generation updates current_step & progress_percent.
4. Job completion sets 100% progress_percent; failure preserves error.
5. OutboxService.emit marks PUBLISHED on success, and FAILED with error on failure.
6. BlueprintService.start_generation schedules execution via background asyncio Task.
7. Idempotency guard prevents redundant scheduling when already GENERATING.
8. SSE endpoint (/events) outputs proper framing (id:, event: update, retry: 2000, data:) and terminates on terminal state.
9. SSE authentication supports ?token= query parameter and enforces student ownership.
10. Cross-project SSE access returns 403 Forbidden.
"""

from __future__ import annotations

import asyncio
import contextlib
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from fastapi.testclient import TestClient
import jwt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.dependencies.database import get_db_session
from backend.app.api.dependencies.services import get_blueprint_service
from backend.app.application.services.blueprint_service import BlueprintService
from backend.app.application.services.notification_service import NotificationService
from backend.app.application.services.outbox_service import OutboxService
from backend.app.domain.assessment.models import AssessmentStatus
from backend.app.domain.blueprint.models import (
    BlueprintJobStatus,
    BlueprintJobType,
    BlueprintQAStatus,
    BlueprintSession,
    BlueprintStatus,
)
from backend.app.domain.identity import AccountStatus, UserRole
from backend.app.domain.project.models import ProjectPhase
from backend.app.factory import create_app
from backend.app.infrastructure.database.models.assessment import (
    AssessmentModel,
    AssessmentResultModel,
)
from backend.app.infrastructure.database.models.blueprint import (
    BlueprintJobModel,
    BlueprintModel,
)
from backend.app.infrastructure.database.models.outbox import DomainEventModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.database.models.user import UserModel
from backend.app.infrastructure.repositories.assessment_repository import (
    AssessmentRepository,
)
from backend.app.infrastructure.repositories.blueprint_repository import (
    BlueprintRepository,
)
from backend.app.infrastructure.repositories.outbox_repository import OutboxRepository
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.infrastructure.repositories.user_repository import UserRepository
from backend.app.shared.events.domain_event import OutboxStatus
from backend.app.shared.exceptions import AuthorizationException, NotFoundException

if TYPE_CHECKING:
    from backend.app.config.settings import Settings

_TEST_SECRET = "batch-4-test-secret-at-least-32-chars-long-12345"
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


# =============================================================================
# 1 & 2. ORPHAN JOB RECOVERY & RECOVERY STATE
# =============================================================================


@pytest.mark.asyncio
async def test_orphan_job_recovery_transitions_to_failed():
    """Stranded RUNNING jobs and associated GENERATING blueprints must transition to FAILED."""
    mock_session = AsyncMock(spec=AsyncSession)

    job_running = BlueprintJobModel(
        id=str(uuid.uuid4()),
        blueprint_id=str(uuid.uuid4()),
        project_instance_id=str(uuid.uuid4()),
        job_type=BlueprintJobType.FULL_GENERATION.value,
        status=BlueprintJobStatus.RUNNING.value,
        progress_percent=40,
    )

    bp_generating = BlueprintModel(
        id=uuid.UUID(job_running.blueprint_id),
        project_instance_id=str(job_running.project_instance_id),
        student_id=str(uuid.uuid4()),
        status=BlueprintStatus.GENERATING.value,
        progress_percent=40,
    )

    # Mock DB query results
    res_jobs = MagicMock()
    res_jobs.scalars.return_value.all.return_value = [job_running]

    res_bps = MagicMock()
    res_bps.scalars.return_value.all.return_value = [bp_generating]

    mock_session.execute.side_effect = [res_jobs, res_bps]

    repo = BlueprintRepository(mock_session)
    recovered_count = await repo.recover_orphaned_jobs(
        error_message="Execution interrupted by server restart"
    )

    assert recovered_count == 1
    assert job_running.status == BlueprintJobStatus.FAILED.value
    assert job_running.error == "Execution interrupted by server restart"
    assert job_running.completed_at is not None
    assert bp_generating.status == BlueprintStatus.FAILED.value
    assert bp_generating.error_message == "Execution interrupted by server restart"
    assert mock_session.flush.called


@pytest.mark.asyncio
async def test_orphan_job_recovery_preserves_clean_state_when_no_orphans():
    """Startup recovery does nothing when there are no stranded RUNNING jobs."""
    mock_session = AsyncMock(spec=AsyncSession)
    res_jobs = MagicMock()
    res_jobs.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = res_jobs

    repo = BlueprintRepository(mock_session)
    recovered_count = await repo.recover_orphaned_jobs()

    assert recovered_count == 0
    assert not mock_session.flush.called


# =============================================================================
# 3 & 4. JOB PROGRESS & COMPLETION/FAILURE PERSISTENCE
# =============================================================================


@pytest.mark.asyncio
async def test_job_progress_synchronization_and_completion():
    """Job progress updates correctly and completion enforces 100% progress."""
    mock_session = AsyncMock(spec=AsyncSession)
    repo = BlueprintRepository(mock_session)

    job = BlueprintJobModel(
        id=str(uuid.uuid4()),
        blueprint_id=str(uuid.uuid4()),
        project_instance_id=str(uuid.uuid4()),
        job_type=BlueprintJobType.FULL_GENERATION.value,
        status=BlueprintJobStatus.RUNNING.value,
        progress_percent=10,
        current_step="project_profile",
    )

    # Test progress update
    await repo.update_job_progress(job, current_step="tech_stack", progress_percent=30)
    assert job.current_step == "tech_stack"
    assert job.progress_percent == 30
    assert mock_session.flush.called

    # Test complete job
    await repo.complete_job(job, BlueprintJobStatus.COMPLETED)
    assert job.status == BlueprintJobStatus.COMPLETED.value
    assert job.progress_percent == 100
    assert job.completed_at is not None

    # Test failure preserves error
    failed_job = BlueprintJobModel(
        id=str(uuid.uuid4()),
        blueprint_id=str(uuid.uuid4()),
        project_instance_id=str(uuid.uuid4()),
        job_type=BlueprintJobType.FULL_GENERATION.value,
        status=BlueprintJobStatus.RUNNING.value,
        progress_percent=50,
    )
    await repo.complete_job(
        failed_job,
        BlueprintJobStatus.FAILED,
        error="Synthesis failed due to rate limit",
    )
    assert failed_job.status == BlueprintJobStatus.FAILED.value
    assert failed_job.error == "Synthesis failed due to rate limit"
    assert failed_job.progress_percent == 50  # error preserves current percent


# =============================================================================
# 5. OUTBOX STATUS FINALIZATION (PUBLISHED / FAILED)
# =============================================================================


@pytest.mark.asyncio
async def test_outbox_transitions_to_published_on_success():
    """Domain events transition to PUBLISHED when notification succeeds."""
    mock_outbox_repo = AsyncMock(spec=OutboxRepository)
    mock_notif_service = AsyncMock(spec=NotificationService)

    event = DomainEventModel(
        id=uuid.uuid4(),
        event_type="BlueprintGenerated",
        actor_role="STUDENT",
        resource_type="blueprint",
        resource_id=str(uuid.uuid4()),
        status=OutboxStatus.PENDING.value,
    )
    mock_outbox_repo.enqueue_event.return_value = event
    mock_notif_service.handle_domain_event.return_value = []

    outbox_svc = OutboxService(
        outbox_repo=mock_outbox_repo,
        notification_service=mock_notif_service,
    )

    result = await outbox_svc.emit(
        event_type="BlueprintGenerated",
        actor_role="STUDENT",
        resource_type="blueprint",
        resource_id=event.resource_id,
    )

    assert result.id == event.id
    mock_outbox_repo.mark_published.assert_awaited_once_with(event.id)
    assert not mock_outbox_repo.mark_failed.called


@pytest.mark.asyncio
async def test_outbox_transitions_to_failed_without_aborting_domain_tx():
    """Domain events transition to FAILED when notification processing throws, without aborting tx."""
    mock_outbox_repo = AsyncMock(spec=OutboxRepository)
    mock_notif_service = AsyncMock(spec=NotificationService)

    event = DomainEventModel(
        id=uuid.uuid4(),
        event_type="BlueprintGenerated",
        actor_role="STUDENT",
        resource_type="blueprint",
        resource_id=str(uuid.uuid4()),
        status=OutboxStatus.PENDING.value,
    )
    mock_outbox_repo.enqueue_event.return_value = event
    mock_notif_service.handle_domain_event.side_effect = RuntimeError(
        "Notification recipient lookup failed"
    )

    outbox_svc = OutboxService(
        outbox_repo=mock_outbox_repo,
        notification_service=mock_notif_service,
    )

    # Must not raise RuntimeError; should record failure on outbox
    result = await outbox_svc.emit(
        event_type="BlueprintGenerated",
        actor_role="STUDENT",
        resource_type="blueprint",
        resource_id=event.resource_id,
    )

    assert result.id == event.id
    mock_outbox_repo.mark_failed.assert_awaited_once_with(
        event.id, error="Notification recipient lookup failed"
    )
    assert not mock_outbox_repo.mark_published.called


# =============================================================================
# 6 & 7. BACKGROUND EXECUTION SCHEDULING & IDEMPOTENCY
# =============================================================================


@pytest.mark.asyncio
async def test_blueprint_background_execution_scheduling():
    """start_generation returns GENERATING immediately and schedules execution in background Task."""
    student_id = uuid.uuid4()
    proj_id = uuid.uuid4()
    bp_id = uuid.uuid4()

    mock_bp_repo = AsyncMock(spec=BlueprintRepository)
    mock_proj_repo = AsyncMock(spec=ProjectRepository)
    mock_assess_repo = AsyncMock(spec=AssessmentRepository)
    mock_proj_service = AsyncMock()
    mock_outbox_service = AsyncMock()

    proj = ProjectInstanceModel(
        id=str(proj_id),
        student_id=str(student_id),
        name="Test Proj",
        current_phase=ProjectPhase.BLUEPRINT.value,
    )
    mock_proj_repo.get_by_id.return_value = proj

    assess = AssessmentModel(
        id=str(uuid.uuid4()),
        project_instance_id=str(proj_id),
        status=AssessmentStatus.COMPLETED.value,
    )
    mock_assess_repo.get_by_project_id.return_value = assess

    initial_bp = BlueprintModel(
        id=bp_id,
        project_instance_id=str(proj_id),
        student_id=str(student_id),
        status=BlueprintStatus.NOT_STARTED.value,
        progress_percent=0,
        qa_status=BlueprintQAStatus.PENDING.value,
    )
    mock_bp_repo.create_or_get_blueprint.return_value = initial_bp

    generating_bp = BlueprintModel(
        id=bp_id,
        project_instance_id=str(proj_id),
        student_id=str(student_id),
        status=BlueprintStatus.GENERATING.value,
        current_step="project_profile",
        progress_percent=5,
        qa_status=BlueprintQAStatus.PENDING.value,
    )
    mock_bp_repo.update_status.return_value = generating_bp

    job = BlueprintJobModel(
        id=str(uuid.uuid4()),
        blueprint_id=str(bp_id),
        project_instance_id=str(proj_id),
        status=BlueprintJobStatus.RUNNING.value,
    )
    mock_bp_repo.create_job.return_value = job

    service = BlueprintService(
        blueprint_repo=mock_bp_repo,
        project_repo=mock_proj_repo,
        assessment_repo=mock_assess_repo,
        project_service=mock_proj_service,
        outbox_service=mock_outbox_service,
    )

    current_user = MagicMock()
    current_user.user_id = student_id
    current_user.is_admin = False
    current_user.is_student = True
    current_user.is_mentor = False

    # Mock background runner so it doesn't run un-mocked DB calls
    with patch.object(service, "_run_generation_task", new_callable=AsyncMock) as mock_task_runner:
        result = await service.start_generation(proj_id, current_user)

        # Immediate return in GENERATING status
        assert result.status == BlueprintStatus.GENERATING
        assert result.progress_percent == 5
        assert result.current_step == "project_profile"

        # Background task was scheduled
        await asyncio.sleep(0.01)
        mock_task_runner.assert_called_once_with(
            project_id=str(proj_id),
            blueprint_id=str(bp_id),
            job_id=str(job.id),
        )


@pytest.mark.asyncio
async def test_blueprint_generation_idempotency_guard():
    """start_generation on an already GENERATING session returns existing state without rescheduling."""
    student_id = uuid.uuid4()
    proj_id = uuid.uuid4()
    bp_id = uuid.uuid4()

    mock_bp_repo = AsyncMock(spec=BlueprintRepository)
    mock_proj_repo = AsyncMock(spec=ProjectRepository)
    mock_assess_repo = AsyncMock(spec=AssessmentRepository)
    mock_proj_service = AsyncMock()
    mock_outbox_service = AsyncMock()

    proj = ProjectInstanceModel(
        id=str(proj_id),
        student_id=str(student_id),
        name="Test Proj",
        current_phase=ProjectPhase.BLUEPRINT.value,
    )
    mock_proj_repo.get_by_id.return_value = proj

    assess = AssessmentModel(
        id=str(uuid.uuid4()),
        project_instance_id=str(proj_id),
        status=AssessmentStatus.COMPLETED.value,
    )
    mock_assess_repo.get_by_project_id.return_value = assess

    in_progress_bp = BlueprintModel(
        id=bp_id,
        project_instance_id=str(proj_id),
        student_id=str(student_id),
        status=BlueprintStatus.GENERATING.value,
        progress_percent=40,
        current_step="specifications",
        qa_status=BlueprintQAStatus.PENDING.value,
    )
    mock_bp_repo.create_or_get_blueprint.return_value = in_progress_bp

    service = BlueprintService(
        blueprint_repo=mock_bp_repo,
        project_repo=mock_proj_repo,
        assessment_repo=mock_assess_repo,
        project_service=mock_proj_service,
        outbox_service=mock_outbox_service,
    )

    current_user = MagicMock()
    current_user.user_id = student_id
    current_user.is_admin = False
    current_user.is_student = True
    current_user.is_mentor = False

    with patch.object(service, "_run_generation_task", new_callable=AsyncMock) as mock_task_runner:
        result = await service.start_generation(proj_id, current_user, force_regenerate=False)

        assert result.status == BlueprintStatus.GENERATING
        assert result.progress_percent == 40
        assert result.current_step == "specifications"

        # Did NOT create new job or schedule new background task
        assert not mock_bp_repo.create_job.called
        assert not mock_task_runner.called


@pytest.mark.asyncio
async def test_background_task_session_isolation_and_completion():
    """Background task executes in an isolated session from session_factory and completes successfully."""
    proj_id = uuid.uuid4()
    bp_id = uuid.uuid4()
    job_id = uuid.uuid4()

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session
    mock_session_factory.return_value.__aexit__.return_value = None

    proj = ProjectInstanceModel(
        id=str(proj_id),
        student_id=str(uuid.uuid4()),
        name="Isolated Background Project",
        current_phase=ProjectPhase.BLUEPRINT.value,
    )
    bp = BlueprintModel(
        id=bp_id,
        project_instance_id=str(proj_id),
        student_id=str(proj.student_id),
        status=BlueprintStatus.GENERATING.value,
    )
    job = BlueprintJobModel(
        id=str(job_id),
        blueprint_id=str(bp_id),
        project_instance_id=str(proj_id),
        status=BlueprintJobStatus.RUNNING.value,
    )

    res_job = MagicMock()
    res_job.scalars.return_value.first.return_value = job
    mock_session.execute.return_value = res_job

    service = BlueprintService(
        blueprint_repo=AsyncMock(),
        project_repo=AsyncMock(),
        assessment_repo=AsyncMock(),
        project_service=AsyncMock(),
        outbox_service=AsyncMock(),
        session_factory=mock_session_factory,
    )

    with patch("backend.app.infrastructure.repositories.project_repository.ProjectRepository.get_by_id", new_callable=AsyncMock) as mock_p_get, \
         patch("backend.app.infrastructure.repositories.blueprint_repository.BlueprintRepository.get_by_id", new_callable=AsyncMock) as mock_bp_get, \
         patch.object(service, "_execute_generation_pipeline", new_callable=AsyncMock) as mock_pipeline, \
         patch("backend.app.infrastructure.repositories.blueprint_repository.BlueprintRepository.complete_job", new_callable=AsyncMock) as mock_complete:

        mock_p_get.return_value = proj
        mock_bp_get.return_value = bp

        await service._run_generation_task(
            project_id=str(proj_id),
            blueprint_id=str(bp_id),
            job_id=str(job_id),
        )

        mock_session_factory.assert_called_once()
        mock_pipeline.assert_called_once()
        mock_complete.assert_called_once_with(job, BlueprintJobStatus.COMPLETED)
        assert mock_session.commit.called


@pytest.mark.asyncio
async def test_background_task_handles_pipeline_failure_cleanly():
    """Background task marks job and blueprint FAILED if generation pipeline throws an exception."""
    proj_id = uuid.uuid4()
    bp_id = uuid.uuid4()
    job_id = uuid.uuid4()

    mock_session = AsyncMock(spec=AsyncSession)
    mock_session_factory = MagicMock()
    mock_session_factory.return_value.__aenter__.return_value = mock_session
    mock_session_factory.return_value.__aexit__.return_value = None

    proj = ProjectInstanceModel(
        id=str(proj_id),
        student_id=str(uuid.uuid4()),
        name="Isolated Background Project",
        current_phase=ProjectPhase.BLUEPRINT.value,
    )
    bp = BlueprintModel(
        id=bp_id,
        project_instance_id=str(proj_id),
        student_id=str(proj.student_id),
        status=BlueprintStatus.GENERATING.value,
    )
    job = BlueprintJobModel(
        id=str(job_id),
        blueprint_id=str(bp_id),
        project_instance_id=str(proj_id),
        status=BlueprintJobStatus.RUNNING.value,
    )

    res_job = MagicMock()
    res_job.scalars.return_value.first.return_value = job
    mock_session.execute.return_value = res_job

    service = BlueprintService(
        blueprint_repo=AsyncMock(),
        project_repo=AsyncMock(),
        assessment_repo=AsyncMock(),
        project_service=AsyncMock(),
        outbox_service=AsyncMock(),
        session_factory=mock_session_factory,
    )

    with patch("backend.app.infrastructure.repositories.project_repository.ProjectRepository.get_by_id", new_callable=AsyncMock) as mock_p_get, \
         patch("backend.app.infrastructure.repositories.blueprint_repository.BlueprintRepository.get_by_id", new_callable=AsyncMock) as mock_bp_get, \
         patch.object(service, "_execute_generation_pipeline", side_effect=RuntimeError("AI Gateway Timeout")), \
         patch("backend.app.infrastructure.repositories.blueprint_repository.BlueprintRepository.complete_job", new_callable=AsyncMock) as mock_complete, \
         patch("backend.app.infrastructure.repositories.blueprint_repository.BlueprintRepository.update_status", new_callable=AsyncMock) as mock_update_status:

        mock_p_get.return_value = proj
        mock_bp_get.return_value = bp

        await service._run_generation_task(
            project_id=str(proj_id),
            blueprint_id=str(bp_id),
            job_id=str(job_id),
        )

        mock_complete.assert_called_once_with(job, BlueprintJobStatus.FAILED, error="AI Gateway Timeout")
        mock_update_status.assert_called_once_with(bp, BlueprintStatus.FAILED, error_message="AI Gateway Timeout")
        assert mock_session.commit.called


# =============================================================================
# 8, 9 & 10. SSE FRAMING, TERMINAL COMPLETION & AUTHENTICATION
# =============================================================================


class TestBlueprintSSE:
    def test_sse_framing_and_terminal_completion(
        self, auth_settings: Settings
    ):
        """SSE stream outputs valid framing (id, event: update, retry: 2000, data) and terminates."""
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id, role="STUDENT")

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        terminal_bp = BlueprintSession(
            id=uuid.uuid4(),
            project_instance_id=project_id,
            student_id=student_id,
            status=BlueprintStatus.READY_FOR_APPROVAL,
            progress_percent=100,
            qa_status=BlueprintQAStatus.PASS,
            qa_score=92,
            content={"project_profile": {"title": "Done"}},
            updated_at=datetime.now(UTC),
        )

        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = terminal_bp

        async def _override_get_db_session():
            yield AsyncMock()

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = _override_get_db_session
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_user_repo = AsyncMock(spec=UserRepository)
            mock_user_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_user_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )

                assert response.status_code == 200
                assert "text/event-stream" in response.headers.get("content-type", "")

                text = response.text
                assert "event: update" in text
                assert "retry: 2000" in text
                assert "id:" in text
                assert "data:" in text
                assert "READY_FOR_APPROVAL" in text
                assert "generation_progress" in text

        app.dependency_overrides.clear()

    def test_sse_query_param_token_authentication(
        self, auth_settings: Settings
    ):
        """EventSource ?token= query parameter authenticates successfully when header is absent."""
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id, role="STUDENT")

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        terminal_bp = BlueprintSession(
            id=uuid.uuid4(),
            project_instance_id=project_id,
            student_id=student_id,
            status=BlueprintStatus.READY_FOR_APPROVAL,
            progress_percent=100,
            qa_status=BlueprintQAStatus.PASS,
            updated_at=datetime.now(UTC),
        )

        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = terminal_bp

        async def _override_get_db_session():
            yield AsyncMock()

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = _override_get_db_session
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_user_repo = AsyncMock(spec=UserRepository)
            mock_user_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_user_repo

            with TestClient(app) as client:
                # No Authorization header; query parameter ?token= only
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events?token={token}"
                )

                assert response.status_code == 200
                assert "text/event-stream" in response.headers.get("content-type", "")
                assert "READY_FOR_APPROVAL" in response.text

        app.dependency_overrides.clear()

    def test_sse_cross_project_forbidden(
        self, auth_settings: Settings
    ):
        """Student attempting to stream events for another student's project receives 403 Forbidden."""
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id, role="STUDENT")

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        from backend.app.shared.exceptions import AuthorizationException

        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.side_effect = AuthorizationException(
            "Access to this project is denied.", code="AUTH_FORBIDDEN_RESOURCE"
        )

        async def _override_get_db_session():
            yield AsyncMock()

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = _override_get_db_session
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_user_repo = AsyncMock(spec=UserRepository)
            mock_user_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_user_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )

                assert response.status_code == 403

        app.dependency_overrides.clear()

    def test_sse_unauthenticated_returns_401(self, auth_settings: Settings):
        """Unauthenticated SSE request without token or header returns 401."""
        async def _override_get_db_session():
            yield AsyncMock()

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = _override_get_db_session
        with TestClient(app) as client:
            response = client.get(f"/api/v1/projects/{uuid.uuid4()}/blueprint/events")
            assert response.status_code == 401
        app.dependency_overrides.clear()

    def test_sse_invalid_token_returns_401(self, auth_settings: Settings):
        """SSE request with invalid or corrupted JWT token returns 401."""
        async def _override_get_db_session():
            yield AsyncMock()

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = _override_get_db_session
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/projects/{uuid.uuid4()}/blueprint/events?token=invalid.jwt.token"
            )
            assert response.status_code == 401
        app.dependency_overrides.clear()

    def test_rest_endpoint_with_query_param_token_returns_401(
        self, auth_settings: Settings
    ):
        """Non-SSE REST endpoint strictly rejects ?token= query parameter without Authorization header."""
        student_id = uuid.uuid4()
        token = _make_jwt(student_id, role="STUDENT")

        async def _override_get_db_session():
            yield AsyncMock()

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = _override_get_db_session
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/projects/{uuid.uuid4()}/blueprint/status?token={token}"
            )
            assert response.status_code == 401
        app.dependency_overrides.clear()

    def test_sse_nonexistent_project_returns_404(
        self, auth_settings: Settings
    ):
        """SSE connection for a nonexistent project returns 404 Not Found."""
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id, role="STUDENT")

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

        async def _override_get_db_session():
            yield AsyncMock()

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = _override_get_db_session
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_user_repo = AsyncMock(spec=UserRepository)
            mock_user_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_user_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert response.status_code == 404

        app.dependency_overrides.clear()

    @pytest.mark.parametrize(
        "term_status",
        [
            BlueprintStatus.READY_FOR_APPROVAL,
            BlueprintStatus.QA_REJECTED,
            BlueprintStatus.FAILED,
            BlueprintStatus.APPROVED,
        ],
    )
    def test_sse_all_terminal_states_close_stream(
        self, auth_settings: Settings, term_status: BlueprintStatus
    ):
        """Every truthful terminal status causes the SSE stream to emit the terminal event and terminate."""
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id, role="STUDENT")

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        terminal_bp = BlueprintSession(
            id=uuid.uuid4(),
            project_instance_id=project_id,
            student_id=student_id,
            status=term_status,
            progress_percent=100 if term_status != BlueprintStatus.FAILED else 40,
            qa_status=BlueprintQAStatus.PASS if term_status != BlueprintStatus.QA_REJECTED else BlueprintQAStatus.FAIL,
            updated_at=datetime.now(UTC),
        )

        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = terminal_bp

        async def _override_get_db_session():
            yield AsyncMock()

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = _override_get_db_session
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_user_repo = AsyncMock(spec=UserRepository)
            mock_user_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_user_repo

            with TestClient(app) as client:
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )

                assert response.status_code == 200
                assert "event: update" in response.text
                assert term_status.value in response.text

        app.dependency_overrides.clear()

    def test_sse_reconnect_reads_latest_canonical_state(
        self, auth_settings: Settings
    ):
        """A reconnected SSE stream immediately reads the latest canonical database state."""
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id, role="STUDENT")

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        bp_completed = BlueprintSession(
            id=uuid.uuid4(),
            project_instance_id=project_id,
            student_id=student_id,
            status=BlueprintStatus.READY_FOR_APPROVAL,
            progress_percent=100,
            current_step="readme",
            updated_at=datetime.now(UTC),
        )

        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = bp_completed

        async def _override_get_db_session():
            yield AsyncMock()

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = _override_get_db_session
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_user_repo = AsyncMock(spec=UserRepository)
            mock_user_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_user_repo

            with TestClient(app) as client:
                res = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert res.status_code == 200
                assert "READY_FOR_APPROVAL" in res.text

        app.dependency_overrides.clear()

    def test_sse_keepalive_when_state_unchanged(
        self, auth_settings: Settings
    ):
        """When canonical state is unchanged across polling intervals, stream emits : keep-alive comments."""
        student_id = uuid.uuid4()
        project_id = uuid.uuid4()
        token = _make_jwt(student_id, role="STUDENT")

        mock_user = UserModel(
            id=str(student_id),
            email="student@example.com",
            role=UserRole.STUDENT.value,
            status=AccountStatus.ACTIVE.value,
            full_name="Student User",
        )

        now = datetime.now(UTC)
        bp_stable = BlueprintSession(
            id=uuid.uuid4(),
            project_instance_id=project_id,
            student_id=student_id,
            status=BlueprintStatus.GENERATING,
            progress_percent=50,
            current_step="features",
            updated_at=now,
        )

        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = bp_stable

        async def _override_get_db_session():
            yield AsyncMock()

        app = create_app(auth_settings)
        app.dependency_overrides[get_db_session] = _override_get_db_session
        app.dependency_overrides[get_blueprint_service] = lambda: mock_service

        with patch("backend.app.api.dependencies.auth.UserRepository") as mock_user_repo_cls:
            mock_user_repo = AsyncMock(spec=UserRepository)
            mock_user_repo.get_by_id.return_value = mock_user
            mock_user_repo_cls.return_value = mock_user_repo

            from backend.app.domain.ai.orchestration.events import (
                WorkflowEvent,
                WorkflowEventType,
                get_blueprint_event_manager,
            )

            manager = get_blueprint_event_manager()
            mock_service.event_manager = manager

            ev_term = WorkflowEvent(
                event_type=WorkflowEventType.JOB_COMPLETED.value,
                job_id="job-term",
                project_id=str(project_id),
                generation_number=1,
                step="completed",
            )

            orig_wait_for = asyncio.wait_for

            async def _fast_wait_for(fut, timeout):
                if not hasattr(_fast_wait_for, "timed_out"):
                    _fast_wait_for.timed_out = True
                    # Await real queue.get() with a 0.05s timeout -> raises real asyncio.TimeoutError
                    return await orig_wait_for(fut, timeout=0.05)
                # After keepalive was emitted, publish real terminal event to real event manager
                await manager.publish(ev_term)
                # Await real queue.get() which now receives the published ev_term
                return await orig_wait_for(fut, timeout=1.0)

            with (
                patch("asyncio.wait_for", side_effect=_fast_wait_for),
                TestClient(app) as client,
            ):
                response = client.get(
                    f"/api/v1/projects/{project_id}/blueprint/events",
                    headers={"Authorization": f"Bearer {token}"},
                )
                assert response.status_code == 200
                assert ": keep-alive" in response.text
                assert "READY_FOR_APPROVAL" in response.text

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_sse_disconnect_does_not_cancel_background_task(
        self, auth_settings: Settings
    ):
        """Client disconnect from SSE stream does not cancel the underlying background asyncio generation task."""
        async def _dummy_bg_job():
            await asyncio.sleep(10)
            return "ok"

        bg_task = asyncio.create_task(_dummy_bg_job())
        BlueprintService._active_tasks.add(bg_task)

        mock_request = AsyncMock()
        mock_request.headers = {}
        mock_request.query_params = {}
        mock_request.is_disconnected.return_value = True

        mock_service = AsyncMock(spec=BlueprintService)
        mock_service.get_status.return_value = BlueprintSession(
            id=uuid.uuid4(),
            project_instance_id=uuid.uuid4(),
            student_id=uuid.uuid4(),
            status=BlueprintStatus.GENERATING,
            progress_percent=20,
            updated_at=datetime.now(UTC),
        )

        from backend.app.api.routes.blueprint import stream_blueprint_events
        response = await stream_blueprint_events(
            request=mock_request,
            project_id=uuid.uuid4(),
            current_user=MagicMock(),
            service=mock_service,
        )

        async for _ in response.body_iterator:
            pass

        assert not bg_task.cancelled()
        assert not bg_task.done()

        bg_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await bg_task
        BlueprintService._active_tasks.discard(bg_task)
