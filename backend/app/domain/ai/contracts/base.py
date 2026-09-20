"""
GrowFlow — Base AI Agent Contracts & Provenance.

Defines:
- BaseAgentInput: Base class for typed input contracts for all agents.
- BaseAgentOutput: Base class for typed output contracts for all agents.
- AgentExecutionProvenance: Standardized runtime execution provenance contract.

Architecture ref:
  6E § 44 — Structured Output Contracts
  6F § 5  — Agent Input/Output Contract
  6F § 92 — Agent Observability & Provenance
  Gate 09 — Unit 2 Implementation
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Pydantic runtime schema validation
import re
import uuid  # noqa: TC003 — Pydantic runtime schema validation

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.infrastructure.ai.models import (  # noqa: TC001 — Pydantic runtime schema validation
    AIUsageMetadata,
    ProviderCapability,
)


class BaseAgentInput(BaseModel):
    """
    Standard base contract for all agent input contexts.
    Guarantees deterministic execution scoping and traceability across the graph.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    execution_id: str = Field(
        ...,
        description="Unique identifier for the current workflow execution run.",
    )
    project_id: uuid.UUID = Field(
        ...,
        description="Target project instance UUID.",
    )
    student_id: uuid.UUID = Field(
        ...,
        description="Owner student UUID.",
    )
    agent_name: str = Field(
        ...,
        description="Canonical logical name of the executing agent.",
    )
    contract_version: str = Field(
        default="1.0.0",
        description="Semantic version of this agent contract.",
    )
    regeneration_attempt: int = Field(
        default=0,
        ge=0,
        description="Attempt index for targeted regeneration (0 for initial generation).",
    )
    qa_feedback_hint: str | None = Field(
        default=None,
        description="Targeted corrective guidance provided by QA/Judge during regeneration.",
    )


class BaseAgentOutput(BaseModel):
    """
    Standard base contract for all agent structured synthesis outputs.
    Guarantees consistent metadata, assumptions, and uncertainty expressions.
    """

    model_config = ConfigDict(extra="forbid")

    agent_name: str = Field(
        ...,
        description="Canonical logical name of the emitting agent.",
    )
    contract_version: str = Field(
        default="1.0.0",
        description="Semantic version of this agent contract.",
    )
    summary: str = Field(
        ...,
        description="Executive summary of the synthesized architectural section.",
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Agent self-assessed confidence level in synthesized decisions.",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Explicit technical or domain assumptions made during reasoning.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Identified potential risks, tradeoffs, or uncertainties.",
    )


class AgentExecutionProvenance(BaseModel):
    """
    Contract representing the operational and provider provenance of an agent execution.
    Captured per agent node and aggregated into workflow state and telemetry.
    """

    model_config = ConfigDict(extra="forbid")

    agent_name: str
    agent_version: str = "1.0.0"
    prompt_version: str = "1.0.0"
    contract_version: str = "1.0.0"
    generation_number: int = Field(..., ge=1)
    regeneration_attempt: int = Field(default=0, ge=0)
    execution_id: str
    correlation_id: str
    provider: str
    model: str
    key_alias: str = Field(
        ...,
        description="Safe pool alias (e.g. 'key_1'). MUST NEVER contain actual API keys.",
    )
    capability: ProviderCapability
    latency_ms: float = Field(..., ge=0.0)
    usage: AIUsageMetadata
    retry_count: int = Field(default=0, ge=0)
    status: str = "SUCCESS"
    started_at: datetime
    completed_at: datetime

    @field_validator("key_alias")
    @classmethod
    def validate_safe_key_alias(cls, v: str) -> str:
        """Enforce that raw credentials are never leaked into provenance."""
        if re.search(r"sk-[a-zA-Z0-9_-]{10,}", v) or "bearer" in v.lower():
            raise ValueError("Raw API key or authorization token detected in key_alias")
        return v
