"""
GrowFlow — Base AI Agent Abstraction.

Defines the lightweight, generic BaseAgent[TInput, TOutput] coordinating:
- Typed input validation
- System and user prompt construction with version tracking
- Seamless injection of targeted QA feedback for regeneration attempts
- Delegation to centralized AIProviderGateway.execute_structured
- Execution timing and operational provenance assembly
- Strict decoupling from database persistence, LangGraph orchestration, and SSE

Architecture ref:
  6F § 4  — Agent Responsibilities
  6F § 5  — Agent Input/Output Contract
  6F § 92 — Agent Observability & Provenance
  Gate 09 Decision A3 — Targeted regeneration bounded execution
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from backend.app.domain.ai.contracts.base import (
    AgentExecutionProvenance,
    BaseAgentInput,
    BaseAgentOutput,
)
from backend.app.infrastructure.ai.models import (
    AIExecutionResult,
    AIUsageMetadata,
    ProviderCapability,
)
from backend.app.shared.logging import get_logger
from backend.app.shared.logging.context import get_correlation_id

if TYPE_CHECKING:
    from backend.app.infrastructure.ai.gateway import AIProviderGateway

logger = get_logger("growflow.domain.ai.agents.base")


class BaseAgent[TInput: BaseAgentInput, TOutput: BaseAgentOutput](ABC):
    """
    Abstract generic base agent defining the standardized execution lifecycle
    for all 12 blueprint synthesis and evaluation agents.
    """

    def __init__(self, gateway: AIProviderGateway) -> None:
        self._gateway = gateway

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Canonical logical identifier of this agent (e.g. 'idea_agent')."""
        ...

    @property
    @abstractmethod
    def capability(self) -> ProviderCapability:
        """Required model capability tier (STANDARD or REASONING)."""
        ...

    @property
    @abstractmethod
    def output_schema(self) -> type[TOutput]:
        """Target Pydantic v2 output model class."""
        ...

    @property
    def agent_version(self) -> str:
        """Semantic version of the agent code implementation."""
        return "1.0.0"

    @property
    def prompt_version(self) -> str:
        """Semantic version of the prompt templates utilized by this agent."""
        return "1.0.0"

    @abstractmethod
    def build_system_prompt(self, input_data: TInput) -> str:
        """Assemble the system instructions tailored to this agent's domain."""
        ...

    @abstractmethod
    def build_user_prompt(self, input_data: TInput) -> str:
        """Assemble the user prompt containing typed context and domain instructions."""
        ...

    async def execute(
        self,
        input_data: TInput,
        correlation_id: str | None = None,
        generation_number: int = 1,
    ) -> tuple[TOutput, AgentExecutionProvenance]:
        """
        Execute the agent synthesis lifecycle:
        1. Construct versioned system and user prompts.
        2. Append targeted QA feedback if regenerating.
        3. Invoke AIProviderGateway.execute_structured with model capability.
        4. Measure wall-clock latency and assemble AgentExecutionProvenance.
        5. Return typed (TOutput, AgentExecutionProvenance) tuple.
        """
        effective_correlation_id = (
            correlation_id or get_correlation_id() or f"exec-{input_data.execution_id[:8]}"
        )

        logger.info(
            "Starting agent execution",
            agent_name=self.agent_name,
            capability=self.capability.value,
            execution_id=input_data.execution_id,
            regeneration_attempt=input_data.regeneration_attempt,
            correlation_id=effective_correlation_id,
        )

        system_prompt = self.build_system_prompt(input_data)
        user_prompt = self.build_user_prompt(input_data)

        # Inject targeted QA corrective feedback when regenerating
        if input_data.regeneration_attempt > 0 and input_data.qa_feedback_hint:
            user_prompt += (
                f"\n\n### TARGETED REGENERATION GUIDANCE (Attempt {input_data.regeneration_attempt})\n"
                f"The previous draft of this section was flagged during architectural QA review. "
                f"You MUST explicitly address and resolve the following finding in your output:\n"
                f"{input_data.qa_feedback_hint}\n"
            )

        started_at = datetime.now(UTC)

        result: AIExecutionResult[TOutput] = await self._gateway.execute_structured(
            schema=self.output_schema,
            prompt=user_prompt,
            system_prompt=system_prompt,
            capability=self.capability,
            correlation_id=effective_correlation_id,
            execution_id=input_data.execution_id,
        )

        completed_at = datetime.now(UTC)

        # Content is typed TOutput guaranteed by execute_structured validation
        output_content: TOutput = result.content  # type: ignore[assignment]

        provenance = AgentExecutionProvenance(
            agent_name=self.agent_name,
            agent_version=self.agent_version,
            prompt_version=self.prompt_version,
            contract_version=input_data.contract_version,
            generation_number=generation_number,
            regeneration_attempt=input_data.regeneration_attempt,
            execution_id=input_data.execution_id,
            correlation_id=effective_correlation_id,
            provider=result.provider,
            model=result.model,
            key_alias=result.key_alias,
            capability=result.capability,
            latency_ms=result.latency_ms,
            usage=result.usage or AIUsageMetadata(),
            retry_count=result.retry_count,
            status="SUCCESS",
            started_at=started_at,
            completed_at=completed_at,
        )

        logger.info(
            "Agent execution completed successfully",
            agent_name=self.agent_name,
            model=result.model,
            latency_ms=round(result.latency_ms, 2),
            total_tokens=provenance.usage.total_tokens,
            correlation_id=effective_correlation_id,
        )

        return output_content, provenance
