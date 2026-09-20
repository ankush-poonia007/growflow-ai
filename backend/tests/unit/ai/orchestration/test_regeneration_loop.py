"""
GrowFlow — Unit 4 Test: Targeted Regeneration Dependency Chains & Bounded Retry Loop.

Verifies:
- Targeted agent rerun executes only the target and its downstream dependencies
- Unaffected upstream outputs are preserved in state
- Parallel branches not affected by regeneration do not rerun
- Automatic regeneration is bounded at maximum 2 attempts
- Generation number is preserved (not incremented) across automatic regenerations
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend.app.domain.ai.contracts.base import AgentExecutionProvenance
from backend.app.domain.ai.contracts.qa import QAFinding, QASeverity
from backend.app.domain.ai.orchestration.graph import build_blueprint_graph
from backend.app.domain.ai.orchestration.nodes import WorkflowNodeRegistry
from backend.app.domain.ai.orchestration.state import (
    OrchestrationState,  # noqa: TC001
)
from backend.app.domain.blueprint.models import BlueprintQAStatus
from backend.app.infrastructure.ai.models import AIUsageMetadata, ProviderCapability
from backend.tests.unit.ai.fixtures import (
    TEST_EXECUTION_ID,
    TEST_PROJECT_ID,
    TEST_STUDENT_ID,
    make_features_output,
    make_idea_output,
    make_milestone_output,
    make_mvp_output,
    make_qa_judge_input,
    make_qa_judge_output_fail,
    make_qa_judge_output_pass,
    make_readme_output,
    make_risk_output,
    make_scope_output,
    make_specification_output,
    make_task_output,
    make_technology_output,
    make_timeline_output,
)


def make_dummy_provenance(agent_name: str) -> AgentExecutionProvenance:
    now = datetime.now(UTC)
    return AgentExecutionProvenance(
        agent_name=agent_name,
        agent_version="1.0.0",
        prompt_version="1.0.0",
        contract_version="1.0.0",
        generation_number=1,
        regeneration_attempt=0,
        execution_id="exec-123",
        correlation_id="corr-123",
        provider="mock",
        model="mock-v1",
        key_alias="key_1",
        capability=ProviderCapability.STANDARD,
        latency_ms=10.0,
        usage=AIUsageMetadata(
            prompt_tokens=10,
            completion_tokens=10,
            total_tokens=20,
            estimated_cost_usd=0.0001,
        ),
        retry_count=0,
        started_at=now,
        completed_at=now,
    )


@pytest.fixture
def base_initial_state() -> OrchestrationState:
    qa_input = make_qa_judge_input()
    return {
        "project_id": str(TEST_PROJECT_ID),
        "student_id": str(TEST_STUDENT_ID),
        "generation_number": 3,
        "execution_id": TEST_EXECUTION_ID,
        "correlation_id": TEST_EXECUTION_ID,
        "project_context": qa_input.project_context,
        "assessment_context": qa_input.assessment_context,
        "current_step": "idea",
        "workflow_status": "RUNNING",
        "cancellation_requested": False,
        "agent_outputs": {},
        "agent_execution_metadata": {},
        "qa_findings": [],
        "qa_score": 0,
        "qa_status": BlueprintQAStatus.PENDING,
        "regeneration_attempt": 0,
        "regeneration_target": None,
        "qa_feedback_hint": None,
    }


@pytest.mark.asyncio
async def test_targeted_regeneration_timeline_chain(base_initial_state: OrchestrationState) -> None:
    """
    When QA fails targeting 'timeline':
    - timeline, risk, task, milestone, readme, qa_judge rerun.
    - idea, scope, technology, features, mvp, specification do NOT rerun.
    """
    call_counts: dict[str, int] = {}

    def track(name: str, output: Any):
        async def fake_execute(agent_input):
            call_counts[name] = call_counts.get(name, 0) + 1
            return output, make_dummy_provenance(name)

        return fake_execute

    registry = WorkflowNodeRegistry()
    registry.idea_agent.execute = AsyncMock(side_effect=track("idea", make_idea_output()))
    registry.scope_agent.execute = AsyncMock(side_effect=track("scope", make_scope_output()))
    registry.technology_agent.execute = AsyncMock(
        side_effect=track("technology", make_technology_output())
    )
    registry.features_agent.execute = AsyncMock(
        side_effect=track("features", make_features_output())
    )
    registry.mvp_agent.execute = AsyncMock(side_effect=track("mvp", make_mvp_output()))
    registry.specification_agent.execute = AsyncMock(
        side_effect=track("specification", make_specification_output())
    )
    registry.timeline_agent.execute = AsyncMock(
        side_effect=track("timeline", make_timeline_output())
    )
    registry.risk_agent.execute = AsyncMock(side_effect=track("risk", make_risk_output()))
    registry.task_agent.execute = AsyncMock(side_effect=track("task", make_task_output()))
    registry.milestone_agent.execute = AsyncMock(
        side_effect=track("milestone", make_milestone_output())
    )
    registry.readme_agent.execute = AsyncMock(side_effect=track("readme", make_readme_output()))

    # QA Judge fails on attempt 0 targeting timeline, passes on attempt 1
    async def fake_qa(agent_input):
        call_counts["qa_judge"] = call_counts.get("qa_judge", 0) + 1
        attempt = agent_input.regeneration_attempt
        if attempt == 0:
            out = make_qa_judge_output_fail()
            out.overall_score = 65
            out.findings = [
                QAFinding(
                    finding_id="QA-F01",
                    section="timeline",
                    target_agent="timeline",
                    severity=QASeverity.CRITICAL,
                    category="TIMELINE_OVERLAP",
                    description="Critical timeline overlap",
                    recommendation="Fix sprint duration overlap",
                    requires_regeneration=True,
                )
            ]
            out.regeneration_target = "timeline"
        else:
            out = make_qa_judge_output_pass()
            out.overall_score = 85
            out.findings = []
        return out, make_dummy_provenance("qa_judge")

    registry.qa_judge_agent.execute = AsyncMock(side_effect=fake_qa)

    graph = build_blueprint_graph(registry)
    final_state = await graph.ainvoke(base_initial_state)

    # 1. Unaffected upstream nodes ran exactly ONCE
    assert call_counts["idea"] == 1
    assert call_counts["scope"] == 1
    assert call_counts["technology"] == 1
    assert call_counts["features"] == 1
    assert call_counts["mvp"] == 1
    assert call_counts["specification"] == 1

    # 2. Targeted and downstream nodes ran TWICE
    assert call_counts["timeline"] == 2
    assert call_counts["risk"] == 2
    assert call_counts["task"] == 2
    assert call_counts["milestone"] == 2
    assert call_counts["readme"] == 2
    assert call_counts["qa_judge"] == 2

    # 3. Final state outcome
    assert final_state["regeneration_attempt"] == 1
    assert final_state["generation_number"] == 3  # Frozen rule: does NOT increment on regen
    assert final_state["qa_score"] == 85


@pytest.mark.asyncio
async def test_targeted_regeneration_features_chain(base_initial_state: OrchestrationState) -> None:
    """
    When QA fails targeting 'features':
    - features reruns.
    - parallel peers (technology, mvp) and upstream (idea, scope) do NOT rerun.
    - downstream (specification, timeline, risk, task, milestone, readme, qa_judge) rerun.
    """
    call_counts: dict[str, int] = {}

    def track(name: str, output: Any):
        async def fake_execute(agent_input):
            call_counts[name] = call_counts.get(name, 0) + 1
            return output, make_dummy_provenance(name)

        return fake_execute

    registry = WorkflowNodeRegistry()
    registry.idea_agent.execute = AsyncMock(side_effect=track("idea", make_idea_output()))
    registry.scope_agent.execute = AsyncMock(side_effect=track("scope", make_scope_output()))
    registry.technology_agent.execute = AsyncMock(
        side_effect=track("technology", make_technology_output())
    )
    registry.features_agent.execute = AsyncMock(
        side_effect=track("features", make_features_output())
    )
    registry.mvp_agent.execute = AsyncMock(side_effect=track("mvp", make_mvp_output()))
    registry.specification_agent.execute = AsyncMock(
        side_effect=track("specification", make_specification_output())
    )
    registry.timeline_agent.execute = AsyncMock(
        side_effect=track("timeline", make_timeline_output())
    )
    registry.risk_agent.execute = AsyncMock(side_effect=track("risk", make_risk_output()))
    registry.task_agent.execute = AsyncMock(side_effect=track("task", make_task_output()))
    registry.milestone_agent.execute = AsyncMock(
        side_effect=track("milestone", make_milestone_output())
    )
    registry.readme_agent.execute = AsyncMock(side_effect=track("readme", make_readme_output()))

    async def fake_qa(agent_input):
        call_counts["qa_judge"] = call_counts.get("qa_judge", 0) + 1
        attempt = agent_input.regeneration_attempt
        if attempt == 0:
            out = make_qa_judge_output_fail()
            out.overall_score = 60
            out.findings = [
                QAFinding(
                    finding_id="QA-F01",
                    section="features",
                    target_agent="features",
                    severity=QASeverity.CRITICAL,
                    category="SCOPE_VIOLATION",
                    description="Features missing security scope",
                    recommendation="Add missing authentication module",
                    requires_regeneration=True,
                )
            ]
            out.regeneration_target = "features"
        else:
            out = make_qa_judge_output_pass()
            out.overall_score = 90
            out.findings = []
        return out, make_dummy_provenance("qa_judge")

    registry.qa_judge_agent.execute = AsyncMock(side_effect=fake_qa)

    graph = build_blueprint_graph(registry)
    final_state = await graph.ainvoke(base_initial_state)
    assert final_state["qa_score"] == 90

    # Unaffected upstream and parallel branches ran ONCE
    assert call_counts["idea"] == 1
    assert call_counts["scope"] == 1
    assert call_counts["technology"] == 1
    assert call_counts["mvp"] == 1

    # Features and downstream chain ran TWICE
    assert call_counts["features"] == 2
    assert call_counts["specification"] == 2
    assert call_counts["timeline"] == 2
    assert call_counts["risk"] == 2
    assert call_counts["task"] == 2
    assert call_counts["milestone"] == 2
    assert call_counts["readme"] == 2
    assert call_counts["qa_judge"] == 2


@pytest.mark.asyncio
async def test_maximum_two_regeneration_attempts_exhausted(
    base_initial_state: OrchestrationState,
) -> None:
    """
    When QA fails repeatedly:
    - attempt 1 occurs
    - attempt 2 occurs
    - attempt 3 does NOT occur
    - terminates with end_failed
    """
    qa_calls = 0

    registry = WorkflowNodeRegistry()
    registry.idea_agent.execute = AsyncMock(
        return_value=(make_idea_output(), make_dummy_provenance("idea"))
    )
    registry.scope_agent.execute = AsyncMock(
        return_value=(make_scope_output(), make_dummy_provenance("scope"))
    )
    registry.technology_agent.execute = AsyncMock(
        return_value=(make_technology_output(), make_dummy_provenance("technology"))
    )
    registry.features_agent.execute = AsyncMock(
        return_value=(make_features_output(), make_dummy_provenance("features"))
    )
    registry.mvp_agent.execute = AsyncMock(
        return_value=(make_mvp_output(), make_dummy_provenance("mvp"))
    )
    registry.specification_agent.execute = AsyncMock(
        return_value=(make_specification_output(), make_dummy_provenance("specification"))
    )
    registry.timeline_agent.execute = AsyncMock(
        return_value=(make_timeline_output(), make_dummy_provenance("timeline"))
    )
    registry.risk_agent.execute = AsyncMock(
        return_value=(make_risk_output(), make_dummy_provenance("risk"))
    )
    registry.task_agent.execute = AsyncMock(
        return_value=(make_task_output(), make_dummy_provenance("task"))
    )
    registry.milestone_agent.execute = AsyncMock(
        return_value=(make_milestone_output(), make_dummy_provenance("milestone"))
    )
    registry.readme_agent.execute = AsyncMock(
        return_value=(make_readme_output(), make_dummy_provenance("readme"))
    )

    # QA persistently fails targeting task
    async def persistently_failing_qa(agent_input):
        nonlocal qa_calls
        qa_calls += 1
        out = make_qa_judge_output_fail()
        out.overall_score = 50
        out.findings = [
            QAFinding(
                finding_id="QA-F01",
                section="tasks",
                target_agent="task",
                severity=QASeverity.CRITICAL,
                category="MALFORMED_TASKS",
                description="Tasks are malformed",
                recommendation="Revise task breakdown",
                requires_regeneration=True,
            )
        ]
        out.regeneration_target = "task"
        return out, make_dummy_provenance("qa_judge")

    registry.qa_judge_agent.execute = AsyncMock(side_effect=persistently_failing_qa)

    graph = build_blueprint_graph(registry)
    final_state = await graph.ainvoke(base_initial_state)

    # Initial run (0) + attempt 1 (1) + attempt 2 (2) = 3 total QA evaluations
    assert qa_calls == 3
    assert final_state["regeneration_attempt"] == 2
    assert final_state["qa_score"] == 50
    # QA score < 75 with critical findings -> fail
    assert final_state["qa_status"] == BlueprintQAStatus.FAIL
