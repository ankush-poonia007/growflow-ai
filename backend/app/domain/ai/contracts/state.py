"""
GrowFlow — Shared Blueprint Workflow State Contract.

Defines:
- BlueprintWorkflowState: TypedDict representation compatible with LangGraph StateGraph.
- BlueprintWorkflowStateModel: Pydantic equivalent for serialization and validation.

Architecture ref:
  6F § 12 — LangGraph State
  6F § 13 — State vs Database
  6F § 14 — State Persistence
  Gate 09 — Unit 2 Implementation
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Pydantic runtime schema validation
from typing import Any, TypedDict
import uuid  # noqa: TC003 — Pydantic runtime schema validation

from pydantic import BaseModel, ConfigDict, Field

from backend.app.domain.ai.context.models import (  # noqa: TC001 — Pydantic runtime schema validation
    AssessmentContext,
    ProjectBaseContext,
)
from backend.app.domain.ai.contracts.base import (  # noqa: TC001 — Pydantic runtime schema validation
    AgentExecutionProvenance,
)
from backend.app.domain.ai.contracts.qa import (
    QAFinding,  # noqa: TC001 — Pydantic runtime schema validation
)
from backend.app.domain.blueprint.models import BlueprintQAStatus


class BlueprintWorkflowState(TypedDict, total=False):
    """
    TypedDict representing the transient execution state of the blueprint LangGraph workflow.
    Directly consumed by LangGraph StateGraph nodes.
    """

    # Canonical scoping
    project_id: uuid.UUID
    student_id: uuid.UUID
    generation_number: int

    # Execution tracing
    execution_id: str
    correlation_id: str

    # Immutable context
    project_context: ProjectBaseContext
    assessment_context: AssessmentContext

    # Workflow progression
    current_step: str
    workflow_status: str
    cancellation_requested: bool
    agent_outputs: dict[str, Any]
    agent_execution_metadata: dict[str, AgentExecutionProvenance]

    # QA / Evaluation
    qa_findings: list[QAFinding]
    qa_score: int | None
    qa_status: BlueprintQAStatus
    regeneration_attempt: int
    regeneration_target: str | None

    # Error handling & profiling
    errors: list[str]
    started_at: datetime | None
    completed_at: datetime | None


class BlueprintWorkflowStateModel(BaseModel):
    """
    Pydantic representation of the shared workflow state for serialization,
    state inspection, and future durable checkpointing.
    """

    model_config = ConfigDict(extra="forbid")

    project_id: uuid.UUID
    student_id: uuid.UUID
    generation_number: int = Field(default=1, ge=1)

    execution_id: str
    correlation_id: str

    project_context: ProjectBaseContext
    assessment_context: AssessmentContext

    current_step: str = "initialized"
    workflow_status: str = "RUNNING"
    cancellation_requested: bool = False
    agent_outputs: dict[str, Any] = Field(default_factory=dict)
    agent_execution_metadata: dict[str, AgentExecutionProvenance] = Field(default_factory=dict)

    qa_findings: list[QAFinding] = Field(default_factory=list)
    qa_score: int | None = None
    qa_status: BlueprintQAStatus = BlueprintQAStatus.PENDING
    regeneration_attempt: int = Field(default=0, ge=0)
    regeneration_target: str | None = None

    errors: list[str] = Field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def to_state_dict(self) -> BlueprintWorkflowState:
        """Convert to LangGraph-compatible state dictionary."""
        return BlueprintWorkflowState(
            project_id=self.project_id,
            student_id=self.student_id,
            generation_number=self.generation_number,
            execution_id=self.execution_id,
            correlation_id=self.correlation_id,
            project_context=self.project_context,
            assessment_context=self.assessment_context,
            current_step=self.current_step,
            workflow_status=self.workflow_status,
            cancellation_requested=self.cancellation_requested,
            agent_outputs=self.agent_outputs,
            agent_execution_metadata=self.agent_execution_metadata,
            qa_findings=self.qa_findings,
            qa_score=self.qa_score,
            qa_status=self.qa_status,
            regeneration_attempt=self.regeneration_attempt,
            regeneration_target=self.regeneration_target,
            errors=self.errors,
            started_at=self.started_at,
            completed_at=self.completed_at,
        )
