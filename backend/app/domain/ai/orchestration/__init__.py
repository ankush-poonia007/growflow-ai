"""
GrowFlow — Domain AI Orchestration Package.

LangGraph StateGraph orchestration, durable worker execution, cooperative cancellation,
targeted automatic regeneration, provenance persistence, and internal workflow events.
"""

from __future__ import annotations

from backend.app.domain.ai.orchestration.events import (
    InMemoryEventPublisher,
    NoOpEventPublisher,
    WorkflowEvent,
    WorkflowEventPublisher,
    WorkflowEventType,
)
from backend.app.domain.ai.orchestration.graph import build_blueprint_graph
from backend.app.domain.ai.orchestration.nodes import WorkflowNodeRegistry
from backend.app.domain.ai.orchestration.router import (
    MAX_REGENERATION_ATTEMPTS,
    QA_PASS_SCORE_THRESHOLD,
    VALID_REGENERATION_TARGETS,
    evaluate_qa_pass_condition,
    node_regeneration_router,
    route_after_qa,
    route_from_regeneration_router,
)
from backend.app.domain.ai.orchestration.state import OrchestrationState
from backend.app.domain.ai.orchestration.worker import BlueprintWorker, assemble_canonical_content

__all__ = [
    "MAX_REGENERATION_ATTEMPTS",
    "QA_PASS_SCORE_THRESHOLD",
    "VALID_REGENERATION_TARGETS",
    "BlueprintWorker",
    "InMemoryEventPublisher",
    "NoOpEventPublisher",
    "OrchestrationState",
    "WorkflowEvent",
    "WorkflowEventPublisher",
    "WorkflowEventType",
    "WorkflowNodeRegistry",
    "assemble_canonical_content",
    "build_blueprint_graph",
    "evaluate_qa_pass_condition",
    "node_regeneration_router",
    "route_after_qa",
    "route_from_regeneration_router",
]
