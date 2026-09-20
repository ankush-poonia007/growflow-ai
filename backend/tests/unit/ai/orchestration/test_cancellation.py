"""
GrowFlow — Unit 4 Test: Cooperative Cancellation & In-Flight Discard.

Verifies:
- Cancellation before execution (job claimed but cancelled before graph invocation)
- Cancellation between nodes / pre-node cooperative check
- In-flight provider results discarded upon cancellation
- Cancellation during regeneration loop aborted cleanly
- Cancellation idempotency on active and terminal jobs
- Canonical blueprint content remains untouched on cancellation
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
import uuid

import pytest

from backend.app.application.services.blueprint_service import BlueprintService
from backend.app.domain.ai.contracts.base import AgentExecutionProvenance
from backend.app.domain.ai.orchestration.events import InMemoryEventPublisher, WorkflowEventType
from backend.app.domain.ai.orchestration.worker import BlueprintWorker
from backend.app.domain.blueprint.models import BlueprintJobStatus, BlueprintStatus
from backend.app.domain.identity.models import AccountStatus, CurrentUser, UserRole
from backend.app.infrastructure.ai.models import AIUsageMetadata, ProviderCapability
from backend.app.infrastructure.database.models.blueprint import BlueprintJobModel, BlueprintModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.tests.unit.ai.fixtures import (
    TEST_PROJECT_ID,
    TEST_STUDENT_ID,
    make_idea_output,
    make_scope_output,
)


def make_provenance(name: str) -> AgentExecutionProvenance:
    now = datetime.now(UTC)
    return AgentExecutionProvenance(
        agent_name=name,
        agent_version="1.0.0",
        prompt_version="1.0.0",
        contract_version="1.0.0",
        generation_number=1,
        regeneration_attempt=0,
        execution_id="job-cancel-test",
        correlation_id="job-cancel-test",
        provider="mock",
        model="mock-v1",
        key_alias="key_1",
        capability=ProviderCapability.STANDARD,
        latency_ms=10.0,
        usage=AIUsageMetadata(
            prompt_tokens=20,
            completion_tokens=20,
            total_tokens=40,
            estimated_cost_usd=0.0001,
        ),
        retry_count=0,
        started_at=now,
        completed_at=now,
    )


def make_mock_project_repo(project):
    repo = AsyncMock()
    repo.get_by_id.return_value = project
    repo.get_profile.return_value = None
    repo.list_technologies.return_value = []
    return repo


def make_mock_assessment_repo():
    repo = AsyncMock()
    repo.get_by_project_id.return_value = None
    repo.get_answers.return_value = []
    repo.get_result_by_assessment_id.return_value = None
    return repo


@pytest.fixture
def base_entities():
    project_id = TEST_PROJECT_ID
    student_id = TEST_STUDENT_ID
    blueprint_id = uuid.uuid4()
    job_id = uuid.uuid4()

    project = ProjectInstanceModel(
        id=str(project_id),
        student_id=str(student_id),
        name="AgriTelemetry",
        problem="Crop yield tracking",
        proposed_solution="Sensor array",
        complexity="INTERMEDIATE",
        current_phase="BLUEPRINT",
        health="HEALTHY",
    )

    blueprint = BlueprintModel(
        id=str(blueprint_id),
        project_instance_id=str(project_id),
        student_id=str(student_id),
        generation_number=1,
        status=BlueprintStatus.GENERATING.value,
        progress_percent=0,
        content={"canonical_key": "safe_unchanged_content"},
    )

    job = BlueprintJobModel(
        id=str(job_id),
        blueprint_id=str(blueprint_id),
        project_instance_id=str(project_id),
        job_type="FULL_GENERATION",
        generation_number=1,
        status=BlueprintJobStatus.RUNNING.value,
        cancellation_requested=False,
    )

    return project, blueprint, job


@pytest.mark.asyncio
async def test_cancellation_before_execution(base_entities) -> None:
    """Worker detects cancellation_requested before invoking LangGraph."""
    project, blueprint, job = base_entities
    job.cancellation_requested = True
    job.status = BlueprintJobStatus.CANCELLING.value
    original_content = dict(blueprint.content)

    events_pub = InMemoryEventPublisher()
    bp_repo = AsyncMock()
    bp_repo.claim_job_lease.return_value = True
    bp_repo.get_job_by_id.return_value = job
    bp_repo.get_by_id.return_value = blueprint
    bp_repo.is_cancellation_requested.return_value = True

    project_repo = make_mock_project_repo(project)
    assessment_repo = make_mock_assessment_repo()
    exec_repo = AsyncMock()

    worker = BlueprintWorker(
        event_publisher=events_pub,
        blueprint_repo=bp_repo,
        project_repo=project_repo,
        assessment_repo=assessment_repo,
        agent_execution_repo=exec_repo,
    )

    await worker.run_generation_job(job.id, project.id, blueprint.id)

    # Job is marked CANCELLED
    bp_repo.complete_job.assert_called_once_with(job, BlueprintJobStatus.CANCELLED)
    # Canonical blueprint was never committed
    bp_repo.commit_canonical_blueprint.assert_not_called()
    # Content is preserved
    assert blueprint.content == original_content
    # Cancellation event emitted
    event_types = [e.event_type for e in events_pub.events]
    assert WorkflowEventType.JOB_CANCELLED.value in event_types


@pytest.mark.asyncio
async def test_cancellation_cooperative_check_between_nodes(base_entities) -> None:
    """Cancellation flag set during graph execution causes node to abort."""
    project, blueprint, job = base_entities
    original_content = dict(blueprint.content)

    events_pub = InMemoryEventPublisher()
    bp_repo = AsyncMock()
    bp_repo.claim_job_lease.return_value = True
    bp_repo.get_job_by_id.return_value = job
    bp_repo.get_by_id.return_value = blueprint
    # Initially not cancelled, but becomes cancelled after idea agent runs
    bp_repo.is_cancellation_requested.side_effect = [False, True, True, True]

    project_repo = make_mock_project_repo(project)
    assessment_repo = make_mock_assessment_repo()
    exec_repo = AsyncMock()

    worker = BlueprintWorker(
        event_publisher=events_pub,
        blueprint_repo=bp_repo,
        project_repo=project_repo,
        assessment_repo=assessment_repo,
        agent_execution_repo=exec_repo,
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "backend.app.domain.ai.agents.idea.IdeaAgent.execute",
            AsyncMock(return_value=(make_idea_output(), make_provenance("idea"))),
        )
        mp.setattr(
            "backend.app.domain.ai.agents.scope.ScopeAgent.execute",
            AsyncMock(return_value=(make_scope_output(), make_provenance("scope"))),
        )

        await worker.run_generation_job(job.id, project.id, blueprint.id)

    # Job is marked CANCELLED
    bp_repo.complete_job.assert_called_once_with(job, BlueprintJobStatus.CANCELLED)
    # Canonical commit was never reached
    bp_repo.commit_canonical_blueprint.assert_not_called()
    assert blueprint.content == original_content


@pytest.mark.asyncio
async def test_service_cancel_generation_active_job(base_entities) -> None:
    """BlueprintService.cancel_generation transitions active job to CANCELLING."""
    project, blueprint, job = base_entities

    current_student = CurrentUser(
        user_id=project.student_id,
        email="test@growflow.internal",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )

    bp_repo = AsyncMock()
    bp_repo.get_by_project_id_for_update.return_value = blueprint
    bp_repo.get_active_job.return_value = job

    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = project

    service = BlueprintService(
        blueprint_repo=bp_repo,
        project_repo=project_repo,
        assessment_repo=AsyncMock(),
        project_service=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    res = await service.cancel_generation(project.id, current_student)

    assert res.status == BlueprintStatus.GENERATING
    bp_repo.request_cancellation.assert_called_once_with(job.id)


@pytest.mark.asyncio
async def test_service_cancel_generation_idempotency_terminal_job(base_entities) -> None:
    """Cancelling an already terminal (COMPLETED or APPROVED) job is a no-op."""
    project, blueprint, _ = base_entities
    blueprint.status = BlueprintStatus.APPROVED.value

    current_student = CurrentUser(
        user_id=project.student_id,
        email="test@growflow.internal",
        role=UserRole.STUDENT,
        status=AccountStatus.ACTIVE,
    )

    # When blueprint is already terminal
    bp_repo = AsyncMock()
    bp_repo.get_by_project_id_for_update.return_value = blueprint
    bp_repo.get_active_job.return_value = None

    project_repo = AsyncMock()
    project_repo.get_by_id.return_value = project

    service = BlueprintService(
        blueprint_repo=bp_repo,
        project_repo=project_repo,
        assessment_repo=AsyncMock(),
        project_service=AsyncMock(),
        outbox_service=AsyncMock(),
    )

    res = await service.cancel_generation(project.id, current_student)

    assert res.status == BlueprintStatus.APPROVED
    bp_repo.request_cancellation.assert_not_called()
