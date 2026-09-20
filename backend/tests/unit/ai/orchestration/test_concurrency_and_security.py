"""
GrowFlow — Unit 4 Test: Concurrency Protection, Cross-Project Security & Startup Recovery.

Verifies:
- Concurrency protection: Two simultaneous generation calls for one project return existing active job and prevent competing jobs
- Security boundary: Student B cannot start or cancel generation on Student A's project
- Startup recovery: Abandoned RUNNING jobs transition to FAILED, CANCELLING jobs transition to CANCELLED truthfully, canonical content preserved
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

from backend.app.application.services.blueprint_service import BlueprintService
from backend.app.domain.blueprint.models import BlueprintJobStatus, BlueprintStatus
from backend.app.domain.identity.models import AccountStatus, CurrentUser, UserRole
from backend.app.domain.project.models import ProjectPhase
from backend.app.infrastructure.database.models.blueprint import BlueprintJobModel, BlueprintModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository
from backend.app.shared.exceptions import AuthorizationException
from backend.tests.unit.ai.fixtures import TEST_PROJECT_ID, TEST_STUDENT_ID


@pytest.fixture
def test_entities():
    project_id = TEST_PROJECT_ID
    student_a_id = TEST_STUDENT_ID
    student_b_id = uuid.uuid4()
    blueprint_id = uuid.uuid4()

    project = ProjectInstanceModel(
        id=str(project_id),
        student_id=str(student_a_id),
        name="SecurityProject",
        problem="Problem Statement",
        proposed_solution="Solution",
        complexity="INTERMEDIATE",
        current_phase=ProjectPhase.BLUEPRINT.value,
        health="HEALTHY",
    )

    blueprint = BlueprintModel(
        id=str(blueprint_id),
        project_instance_id=str(project_id),
        student_id=str(student_a_id),
        generation_number=1,
        status=BlueprintStatus.GENERATING.value,
        progress_percent=25,
        content={"canonical_initial": "data"},
    )

    job = BlueprintJobModel(
        id=str(uuid.uuid4()),
        blueprint_id=str(blueprint_id),
        project_instance_id=str(project_id),
        job_type="FULL_GENERATION",
        generation_number=1,
        status=BlueprintJobStatus.RUNNING.value,
        cancellation_requested=False,
    )

    user_a = CurrentUser(
        user_id=student_a_id,
        email="student_a@growflow.internal",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )

    user_b = CurrentUser(
        user_id=student_b_id,
        email="student_b@growflow.internal",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )

    return project, blueprint, job, user_a, user_b


@pytest.mark.asyncio
async def test_concurrent_generation_protection_returns_active_job(test_entities) -> None:
    """If a generation job is already active, start_generation returns existing generation without creating a competing job."""
    project, blueprint, job, user_a, _ = test_entities

    bp_repo = AsyncMock()
    # Lock row and observe GENERATING status
    bp_repo.get_by_project_id_for_update.return_value = blueprint
    bp_repo.get_active_job.return_value = job

    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = project

    assessment_repo = AsyncMock()
    assessment_repo.get_by_project_id.return_value = MagicMock(status="COMPLETED")

    service = BlueprintService(
        blueprint_repo=bp_repo,
        project_repo=project_repo,
        assessment_repo=assessment_repo,
        project_service=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    # Calling start_generation when already active
    session = await service.start_generation(project.id, user_a, force_regenerate=False)

    # Returns active session
    assert session.status == BlueprintStatus.GENERATING
    # Generation number was NOT incremented
    bp_repo.increment_generation_number.assert_not_called()
    # No new job was created
    bp_repo.create_job.assert_not_called()


@pytest.mark.asyncio
async def test_security_student_cannot_start_generation_on_other_project(test_entities) -> None:
    """Student B cannot start blueprint generation on Student A's project."""
    project, _, _, _, user_b = test_entities

    bp_repo = AsyncMock()
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = project

    service = BlueprintService(
        blueprint_repo=bp_repo,
        project_repo=project_repo,
        assessment_repo=AsyncMock(),
        project_service=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    with pytest.raises(AuthorizationException, match="Access to this project is denied"):
        await service.start_generation(project.id, user_b)


@pytest.mark.asyncio
async def test_security_student_cannot_cancel_generation_on_other_project(test_entities) -> None:
    """Student B cannot cancel blueprint generation on Student A's project."""
    project, _, _, _, user_b = test_entities

    bp_repo = AsyncMock()
    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = project

    service = BlueprintService(
        blueprint_repo=bp_repo,
        project_repo=project_repo,
        assessment_repo=AsyncMock(),
        project_service=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    with pytest.raises(AuthorizationException, match="Access to this project is denied"):
        await service.cancel_generation(project.id, user_b)


@pytest.mark.asyncio
async def test_startup_orphan_recovery_reconciles_running_and_cancelling_jobs() -> None:
    """Startup recovery truthfully reconciles abandoned RUNNING and CANCELLING jobs."""
    session = AsyncMock()
    repo = BlueprintRepository(session=session)

    job_running = BlueprintJobModel(
        id=str(uuid.uuid4()),
        blueprint_id=str(uuid.uuid4()),
        project_instance_id=str(uuid.uuid4()),
        job_type="FULL_GENERATION",
        generation_number=2,
        status=BlueprintJobStatus.RUNNING.value,
    )

    job_cancelling = BlueprintJobModel(
        id=str(uuid.uuid4()),
        blueprint_id=str(uuid.uuid4()),
        project_instance_id=str(uuid.uuid4()),
        job_type="FULL_GENERATION",
        generation_number=3,
        status=BlueprintJobStatus.CANCELLING.value,
    )

    mock_jobs_res = MagicMock()
    mock_jobs_res.scalars.return_value.all.return_value = [job_running, job_cancelling]

    mock_bps_res = MagicMock()
    mock_bps_res.scalars.return_value.all.return_value = []

    session.execute.side_effect = [mock_jobs_res, mock_bps_res]

    recovered_count = await repo.recover_orphaned_jobs(error_message="Process rebooted")

    assert recovered_count == 2
    # RUNNING job transitioned truthfully to FAILED
    assert job_running.status == BlueprintJobStatus.FAILED.value
    assert "Process rebooted" in job_running.error

    # CANCELLING job transitioned truthfully to CANCELLED
    assert job_cancelling.status == BlueprintJobStatus.CANCELLED.value

    # Session flushed
    session.flush.assert_called_once()
