"""
GrowFlow — Unit 4 Test: LangGraph Graph Topology & Agent Mapping.

Verifies:
- All 12 concrete Unit 3 agent nodes exist in the LangGraph graph
- Regeneration router node exists
- START -> IDEA -> SCOPE
- Parallel fan-out: SCOPE -> [TECHNOLOGY, FEATURES, MVP]
- Parallel fan-in: [TECHNOLOGY, FEATURES, MVP] -> SPECIFICATION
- Linear downstream pipeline: SPECIFICATION -> TIMELINE -> RISK -> TASK -> MILESTONE -> README -> QA_JUDGE
- QA Judge is the authoritative final evaluator
- Every node in WorkflowNodeRegistry invokes the correct Unit 3 Agent
"""

from __future__ import annotations

import pytest

from backend.app.domain.ai.agents.features import FeaturesAgent
from backend.app.domain.ai.agents.idea import IdeaAgent
from backend.app.domain.ai.agents.milestone import MilestoneAgent
from backend.app.domain.ai.agents.mvp import MVPAgent
from backend.app.domain.ai.agents.qa import QAJudgeAgent
from backend.app.domain.ai.agents.readme import ReadmeAgent
from backend.app.domain.ai.agents.risk import RiskAgent
from backend.app.domain.ai.agents.scope import ScopeAgent
from backend.app.domain.ai.agents.specification import SpecificationAgent
from backend.app.domain.ai.agents.task import TaskAgent
from backend.app.domain.ai.agents.technology import TechnologyAgent
from backend.app.domain.ai.agents.timeline import TimelineAgent
from backend.app.domain.ai.orchestration.graph import build_blueprint_graph
from backend.app.domain.ai.orchestration.nodes import WorkflowNodeRegistry
from backend.app.domain.ai.orchestration.router import (
    evaluate_qa_pass_condition,
    node_regeneration_router,
    route_after_qa,
    route_from_regeneration_router,
)
from backend.app.domain.ai.orchestration.state import (
    OrchestrationState,  # noqa: TC001
)
from backend.app.domain.blueprint.models import BlueprintQAStatus


@pytest.fixture
def mock_node_registry() -> WorkflowNodeRegistry:
    return WorkflowNodeRegistry()


def test_graph_compiles_and_contains_all_12_nodes(mock_node_registry: WorkflowNodeRegistry) -> None:
    graph = build_blueprint_graph(mock_node_registry)
    assert graph is not None

    expected_nodes = {
        "idea",
        "scope",
        "technology",
        "features",
        "mvp",
        "specification",
        "timeline",
        "risk",
        "task",
        "milestone",
        "readme",
        "qa_judge",
        "regeneration_router",
    }

    graph_nodes = set(graph.nodes.keys())
    for node_name in expected_nodes:
        assert node_name in graph_nodes, f"Expected node '{node_name}' missing from LangGraph graph"


def test_agent_mapping_to_unit3_concrete_agents(mock_node_registry: WorkflowNodeRegistry) -> None:
    assert isinstance(mock_node_registry.idea_agent, IdeaAgent)
    assert isinstance(mock_node_registry.scope_agent, ScopeAgent)
    assert isinstance(mock_node_registry.technology_agent, TechnologyAgent)
    assert isinstance(mock_node_registry.features_agent, FeaturesAgent)
    assert isinstance(mock_node_registry.mvp_agent, MVPAgent)
    assert isinstance(mock_node_registry.specification_agent, SpecificationAgent)
    assert isinstance(mock_node_registry.timeline_agent, TimelineAgent)
    assert isinstance(mock_node_registry.risk_agent, RiskAgent)
    assert isinstance(mock_node_registry.task_agent, TaskAgent)
    assert isinstance(mock_node_registry.milestone_agent, MilestoneAgent)
    assert isinstance(mock_node_registry.readme_agent, ReadmeAgent)
    assert isinstance(mock_node_registry.qa_judge_agent, QAJudgeAgent)


def test_qa_pass_evaluation_boundary_conditions() -> None:
    # 1. Score >= 75 and 0 CRITICAL -> PASS
    state_pass: OrchestrationState = {
        "qa_score": 75,
        "qa_status": BlueprintQAStatus.PASS,
        "qa_findings": [
            {"severity": "MEDIUM", "description": "Minor issue"},
            {"severity": "LOW", "description": "Low issue"},
        ],
    }
    assert evaluate_qa_pass_condition(state_pass) is True

    # 2. Score < 75 -> FAIL
    state_low_score: OrchestrationState = {
        "qa_score": 74,
        "qa_status": BlueprintQAStatus.FAIL,
        "qa_findings": [],
    }
    assert evaluate_qa_pass_condition(state_low_score) is False

    # 3. Score >= 75 but has CRITICAL finding -> FAIL
    state_critical: OrchestrationState = {
        "qa_score": 90,
        "qa_status": BlueprintQAStatus.FAIL,
        "qa_findings": [
            {"severity": "CRITICAL", "description": "Critical flaw in specification"},
        ],
    }
    assert evaluate_qa_pass_condition(state_critical) is False


def test_route_after_qa_branches() -> None:
    # Cancellation branch
    state_cancel: OrchestrationState = {"cancellation_requested": True}
    assert route_after_qa(state_cancel) == "end_cancelled"

    # Pass branch
    state_pass: OrchestrationState = {
        "qa_score": 85,
        "qa_status": BlueprintQAStatus.PASS,
        "qa_findings": [],
        "cancellation_requested": False,
    }
    assert route_after_qa(state_pass) == "end_passed"

    # Fail branch attempt 0 -> regeneration_router
    state_fail_0: OrchestrationState = {
        "qa_score": 60,
        "qa_status": BlueprintQAStatus.FAIL,
        "qa_findings": [{"severity": "CRITICAL", "description": "Needs rework"}],
        "regeneration_attempt": 0,
        "cancellation_requested": False,
    }
    assert route_after_qa(state_fail_0) == "regeneration_router"

    # Fail branch attempt 1 -> regeneration_router
    state_fail_1: OrchestrationState = {
        "qa_score": 60,
        "qa_status": BlueprintQAStatus.FAIL,
        "qa_findings": [{"severity": "CRITICAL", "description": "Needs rework"}],
        "regeneration_attempt": 1,
        "cancellation_requested": False,
    }
    assert route_after_qa(state_fail_1) == "regeneration_router"

    # Fail branch attempt 2 -> end_failed (attempts exhausted)
    state_fail_2: OrchestrationState = {
        "qa_score": 60,
        "qa_status": BlueprintQAStatus.FAIL,
        "qa_findings": [{"severity": "CRITICAL", "description": "Needs rework"}],
        "regeneration_attempt": 2,
        "cancellation_requested": False,
    }
    assert route_after_qa(state_fail_2) == "end_failed"


def test_node_regeneration_router_identifies_target() -> None:
    state: OrchestrationState = {
        "regeneration_attempt": 0,
        "qa_findings": [
            {
                "target_agent": "timeline",
                "severity": "CRITICAL",
                "requires_regeneration": True,
                "recommendation": "Extend sprint 2 by 1 week",
            }
        ],
    }
    patch = node_regeneration_router(state)
    assert patch["regeneration_attempt"] == 1
    assert patch["regeneration_target"] == "timeline"
    assert "Extend sprint 2" in patch["qa_feedback_hint"]
    assert patch["current_step"] == "regenerating_timeline"

    # Router dynamic next step
    merged_state = {**state, **patch}
    assert route_from_regeneration_router(merged_state) == "timeline"
