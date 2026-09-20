"""
GrowFlow — Orchestration State Contract.

Defines OrchestrationState:
TypedDict representation tailored for LangGraph StateGraph execution,
incorporating reducer annotations for concurrent parallel branches
while strictly preserving compatibility with BlueprintWorkflowState.

Architecture ref:
  6F § 12 — LangGraph State
  6F § 13 — State vs Database
  Gate 09 — Unit 2 State Contract
  Gate 09 — Unit 4 LangGraph Orchestration
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — used in TypedDict annotations
import operator
from typing import Annotated, Any
import uuid  # noqa: TC003 — used in TypedDict annotations

from backend.app.domain.ai.context.models import (  # noqa: TC001 — used in TypedDict annotations
    AssessmentContext,
    ProjectBaseContext,
)
from backend.app.domain.ai.contracts.base import (  # noqa: TC001 — used in TypedDict annotations
    AgentExecutionProvenance,
)
from backend.app.domain.ai.contracts.qa import (
    QAFinding,  # noqa: TC001 — used in TypedDict annotations
)
from backend.app.domain.ai.contracts.state import BlueprintWorkflowState
from backend.app.domain.blueprint.models import (
    BlueprintQAStatus,  # noqa: TC001 — used in TypedDict annotations
)


def take_latest_step(current: str | None, update: str | None) -> str:
    return update or current or ""


def take_latest_status(current: str | None, update: str | None) -> str:
    return update or current or "RUNNING"


class OrchestrationState(BlueprintWorkflowState, total=False):
    """
    TypedDict representing the active execution state within LangGraph StateGraph.

    Inherits from BlueprintWorkflowState while declaring explicit `Annotated[..., operator.or_]`
    mergers on `agent_outputs` and `agent_execution_metadata` so that parallel fan-out nodes
    (Technology, Features, MVP) can commit concurrent dictionary updates without collision.
    """

    # Scoping & tracing
    project_id: uuid.UUID
    student_id: uuid.UUID
    generation_number: int
    execution_id: str
    correlation_id: str

    # Foundational immutable context
    project_context: ProjectBaseContext
    assessment_context: AssessmentContext

    # Workflow progression (annotated with reducers for parallel branches)
    current_step: Annotated[str, take_latest_step]
    workflow_status: Annotated[str, take_latest_status]
    cancellation_requested: Annotated[bool, operator.or_]

    # Concurrent branch reduction channels
    agent_outputs: Annotated[dict[str, Any], operator.or_]
    agent_execution_metadata: Annotated[dict[str, AgentExecutionProvenance], operator.or_]

    # QA / Evaluation & Feedback Loop
    qa_findings: list[QAFinding]
    qa_score: int | None
    qa_status: BlueprintQAStatus
    regeneration_attempt: int
    regeneration_target: str | None
    qa_feedback_hint: str | None

    # Profiling & Diagnostics
    errors: list[str]
    started_at: datetime | None
    completed_at: datetime | None
