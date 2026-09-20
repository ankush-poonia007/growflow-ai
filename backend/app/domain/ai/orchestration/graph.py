"""
GrowFlow — Gate 09 Unit 4: LangGraph StateGraph Builder.

Implements the frozen blueprint generation topology:
START
  ↓
IDEA
  ↓
SCOPE
  ↓
┌──────────────┬──────────────┬──────────────┐
│ TECHNOLOGY   │ FEATURES     │ MVP          │
│ STANDARD     │ STANDARD     │ REASONING    │
└──────────────┴──────────────┴──────────────┘
               ↓
        SPECIFICATION
               ↓
           TIMELINE
               ↓
             RISK
               ↓
             TASK
               ↓
          MILESTONE
               ↓
            README
               ↓
           QA / JUDGE
               ↓
          QA ROUTER
          /         \
       PASS         FAIL
        ↓             ↓
       END       regeneration
                     ↓
              targeted agent
                     ↓
               downstream chain
                     ↓
                    QA

Architecture ref:
  6F § 4 — Agent Dependency Graph & Topologies
  6F § 31-35 — Quality Assurance, Severity & Regeneration Loop
  Gate 09 — Unit 4 Frozen Specification
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from langgraph.graph import END, START, StateGraph

from backend.app.domain.ai.orchestration.router import (
    VALID_REGENERATION_TARGETS,
    route_after_qa,
    route_from_regeneration_router,
)
from backend.app.domain.ai.orchestration.state import OrchestrationState

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

    from backend.app.domain.ai.orchestration.nodes import WorkflowNodeRegistry


def build_blueprint_graph(node_registry: WorkflowNodeRegistry) -> CompiledStateGraph:
    """
    Constructs and compiles the frozen 12-agent LangGraph execution graph with
    cooperative cancellation checkpoints, parallel fan-out/fan-in, and targeted
    regeneration routing.
    """
    builder: StateGraph[OrchestrationState] = StateGraph(OrchestrationState)

    # 1. Register 12 concrete Agent nodes
    builder.add_node("idea", node_registry.node_idea)
    builder.add_node("scope", node_registry.node_scope)
    builder.add_node("technology", node_registry.node_technology)
    builder.add_node("features", node_registry.node_features)
    builder.add_node("mvp", node_registry.node_mvp)
    builder.add_node("specification", node_registry.node_specification)
    builder.add_node("timeline", node_registry.node_timeline)
    builder.add_node("risk", node_registry.node_risk)
    builder.add_node("task", node_registry.node_task)
    builder.add_node("milestone", node_registry.node_milestone)
    builder.add_node("readme", node_registry.node_readme)
    builder.add_node("qa_judge", node_registry.node_qa_judge)

    # 2. Register regeneration router node (dispatches lifecycle event via node_registry)
    builder.add_node("regeneration_router", node_registry.node_regeneration_router)

    # 3. Add static forward edges
    # START -> idea -> scope
    builder.add_edge(START, "idea")
    builder.add_edge("idea", "scope")

    # Parallel fan-out: scope -> technology, features, mvp
    builder.add_edge("scope", "technology")
    builder.add_edge("scope", "features")
    builder.add_edge("scope", "mvp")

    # Parallel fan-in: technology, features, mvp -> specification
    builder.add_edge("technology", "specification")
    builder.add_edge("features", "specification")
    builder.add_edge("mvp", "specification")

    # Sequential downstream pipeline
    builder.add_edge("specification", "timeline")
    builder.add_edge("timeline", "risk")
    builder.add_edge("risk", "task")
    builder.add_edge("task", "milestone")
    builder.add_edge("milestone", "readme")
    builder.add_edge("readme", "qa_judge")

    # 4. Add conditional routing edges
    # QA Judge evaluation branch
    builder.add_conditional_edges(
        "qa_judge",
        route_after_qa,
        {
            "end_passed": END,
            "end_cancelled": END,
            "end_failed": END,
            "regeneration_router": "regeneration_router",
        },
    )

    # Targeted regeneration dynamic branch
    regeneration_routing_map: dict[Any, str] = {
        target: target for target in VALID_REGENERATION_TARGETS
    }
    builder.add_conditional_edges(
        "regeneration_router",
        route_from_regeneration_router,
        regeneration_routing_map,
    )

    return builder.compile()
