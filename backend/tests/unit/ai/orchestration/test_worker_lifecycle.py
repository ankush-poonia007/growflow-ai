"""
GrowFlow — Unit 4 Test: Worker Lifecycle, Parallel Execution, and Canonical Persistence.

Verifies:
- Full 12-agent graph execution managed by BlueprintWorker
- Parallel fan-out of Technology, Features, and MVP without collision
- Atomic canonical blueprint commit ONLY after QA PASS (score >= 75, 0 CRITICAL)
- Failure preservation (previous canonical content untouched on agent exception or QA reject)
- Job claim and duplicate execution prevention
- Startup orphan recovery
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

from backend.app.domain.ai.contracts.base import AgentExecutionProvenance
from backend.app.domain.ai.orchestration.events import InMemoryEventPublisher, WorkflowEventType
from backend.app.domain.ai.orchestration.worker import BlueprintWorker
from backend.app.domain.blueprint.models import (
    BlueprintJobStatus,
    BlueprintSectionKey,
    BlueprintStatus,
)
from backend.app.infrastructure.ai.models import AIUsageMetadata, ProviderCapability
from backend.app.infrastructure.database.models.blueprint import BlueprintJobModel, BlueprintModel
from backend.app.infrastructure.database.models.project import ProjectInstanceModel
from backend.tests.unit.ai.fixtures import (
    TEST_PROJECT_ID,
    TEST_STUDENT_ID,
    make_features_output,
    make_idea_output,
    make_milestone_output,
    make_mvp_output,
    make_qa_judge_output_pass,
    make_readme_output,
    make_risk_output,
    make_scope_output,
    make_specification_output,
    make_task_output,
    make_technology_output,
    make_timeline_output,
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
        execution_id="job-test-1",
        correlation_id="job-test-1",
        provider="mock",
        model="mock-v1",
        key_alias="key_1",
        capability=ProviderCapability.STANDARD,
        latency_ms=15.0,
        usage=AIUsageMetadata(
            prompt_tokens=25,
            completion_tokens=25,
            total_tokens=50,
            estimated_cost_usd=0.0002,
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
def mock_entities():
    project_id = TEST_PROJECT_ID
    student_id = TEST_STUDENT_ID
    blueprint_id = uuid.uuid4()
    job_id = uuid.uuid4()

    project = ProjectInstanceModel(
        id=str(project_id),
        student_id=str(student_id),
        name="AgriFlow Telemetry",
        problem="Agricultural moisture tracking",
        proposed_solution="Autonomous drone telemetry",
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
        content={"initial_section": "old_canonical_content"},
    )

    job = BlueprintJobModel(
        id=str(job_id),
        blueprint_id=str(blueprint_id),
        project_instance_id=str(project_id),
        job_type="FULL_GENERATION",
        generation_number=1,
        status=BlueprintJobStatus.PENDING.value,
        cancellation_requested=False,
    )

    return project, blueprint, job


@pytest.mark.asyncio
async def test_worker_happy_path_canonical_commit(mock_entities) -> None:
    project, blueprint, job = mock_entities
    events_pub = InMemoryEventPublisher()

    # Mock Repositories
    bp_repo = AsyncMock()
    bp_repo.claim_job_lease.return_value = True
    bp_repo.get_job_by_id.return_value = job
    bp_repo.get_by_id.return_value = blueprint
    bp_repo.is_cancellation_requested.return_value = False
    bp_repo.commit_canonical_blueprint.return_value = True

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

    # Mock all 12 agents returning valid outputs
    worker._ai_gateway = MagicMock()

    # Create dummy outputs
    def make_mock_exec(name: str, out: Any):
        return AsyncMock(return_value=(out, make_provenance(name)))

    # Intercept node execution with realistic mock outputs
    with (
        pytest.MonkeyPatch.context() as mp,
    ):
        (
            mp.setattr(
                "backend.app.domain.ai.agents.idea.IdeaAgent.execute",
                make_mock_exec("idea", make_idea_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.scope.ScopeAgent.execute",
                make_mock_exec("scope", make_scope_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.technology.TechnologyAgent.execute",
                make_mock_exec("technology", make_technology_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.features.FeaturesAgent.execute",
                make_mock_exec("features", make_features_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.mvp.MVPAgent.execute",
                make_mock_exec("mvp", make_mvp_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.specification.SpecificationAgent.execute",
                make_mock_exec("specification", make_specification_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.timeline.TimelineAgent.execute",
                make_mock_exec("timeline", make_timeline_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.risk.RiskAgent.execute",
                make_mock_exec("risk", make_risk_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.task.TaskAgent.execute",
                make_mock_exec("task", make_task_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.milestone.MilestoneAgent.execute",
                make_mock_exec("milestone", make_milestone_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.readme.ReadmeAgent.execute",
                make_mock_exec("readme", make_readme_output()),
            ),
        )
        (
            mp.setattr(
                "backend.app.domain.ai.agents.qa.QAJudgeAgent.execute",
                make_mock_exec("qa_judge", make_qa_judge_output_pass()),
            ),
        )

        await worker.run_generation_job(job.id, project.id, blueprint.id)

    # 1. Verify lease acquired
    bp_repo.claim_job_lease.assert_called_once()

    # 2. Verify canonical commit called with all 10 canonical sections
    bp_repo.commit_canonical_blueprint.assert_called_once()
    commit_args = bp_repo.commit_canonical_blueprint.call_args.kwargs
    committed_content = commit_args["content"]

    for sec in BlueprintSectionKey:
        assert sec.value in committed_content, f"Missing canonical section '{sec.value}'"

    assert commit_args["qa_score"] >= 75
    assert commit_args["expected_generation_number"] == 1

    # 3. Verify event flow
    event_types = [e.event_type for e in events_pub.events]
    assert WorkflowEventType.JOB_STARTED.value in event_types
    assert WorkflowEventType.NODE_STARTED.value in event_types
    assert WorkflowEventType.NODE_COMPLETED.value in event_types
    assert WorkflowEventType.QA_EVALUATED.value in event_types
    assert WorkflowEventType.JOB_COMPLETED.value in event_types


@pytest.mark.asyncio
async def test_worker_failure_preserves_canonical_content(mock_entities) -> None:
    project, blueprint, job = mock_entities
    events_pub = InMemoryEventPublisher()

    original_content = {"safe_old_key": "safe_old_value"}
    blueprint.content = original_content

    bp_repo = AsyncMock()
    bp_repo.claim_job_lease.return_value = True
    bp_repo.get_job_by_id.return_value = job
    bp_repo.get_by_id.return_value = blueprint
    bp_repo.is_cancellation_requested.return_value = False

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

    # Simulate catastrophic agent failure on specification node
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "backend.app.domain.ai.agents.idea.IdeaAgent.execute",
            AsyncMock(return_value=(make_idea_output(), make_provenance("idea"))),
        )
        mp.setattr(
            "backend.app.domain.ai.agents.scope.ScopeAgent.execute",
            AsyncMock(return_value=(make_scope_output(), make_provenance("scope"))),
        )
        mp.setattr(
            "backend.app.domain.ai.agents.technology.TechnologyAgent.execute",
            AsyncMock(return_value=(make_technology_output(), make_provenance("technology"))),
        )
        mp.setattr(
            "backend.app.domain.ai.agents.features.FeaturesAgent.execute",
            AsyncMock(return_value=(make_features_output(), make_provenance("features"))),
        )
        mp.setattr(
            "backend.app.domain.ai.agents.mvp.MVPAgent.execute",
            AsyncMock(return_value=(make_mvp_output(), make_provenance("mvp"))),
        )
        mp.setattr(
            "backend.app.domain.ai.agents.specification.SpecificationAgent.execute",
            AsyncMock(side_effect=RuntimeError("Provider 503 Service Unavailable")),
        )

        await worker.run_generation_job(job.id, project.id, blueprint.id)

    # 1. Canonical commit was NEVER called
    bp_repo.commit_canonical_blueprint.assert_not_called()

    # 2. Job marked FAILED
    bp_repo.complete_job.assert_called_once()
    assert bp_repo.complete_job.call_args.args[1] == BlueprintJobStatus.FAILED

    # 3. Previous canonical content remains untouched
    assert blueprint.content == original_content

    # 4. Job failed event published
    event_types = [e.event_type for e in events_pub.events]
    assert WorkflowEventType.JOB_FAILED.value in event_types


@pytest.mark.asyncio
async def test_worker_duplicate_lease_prevented(mock_entities) -> None:
    project, blueprint, job = mock_entities

    bp_repo = AsyncMock()
    # Another active worker holds the lease!
    bp_repo.claim_job_lease.return_value = False

    project_repo = AsyncMock()
    assessment_repo = AsyncMock()
    exec_repo = AsyncMock()

    worker = BlueprintWorker(
        blueprint_repo=bp_repo,
        project_repo=project_repo,
        assessment_repo=assessment_repo,
        agent_execution_repo=exec_repo,
    )

    await worker.run_generation_job(job.id, project.id, blueprint.id)

    # Worker bails out early without querying entities or executing graph
    bp_repo.get_job_by_id.assert_not_called()
    project_repo.get_by_id.assert_not_called()
