"""
GrowFlow — Specification Agent Implementation.

Synthesizes data entities, REST API endpoint contracts, integration flows, and acceptance criteria.

Architecture ref:
  6F § 4.6 — Specification Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import (
    SpecificationAgentInput,
    SpecificationAgentOutput,
)
from backend.app.domain.ai.prompts.specification import (
    PROMPT_VERSION,
    build_specification_system_prompt,
    build_specification_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class SpecificationAgent(BaseAgent[SpecificationAgentInput, SpecificationAgentOutput]):
    """Agent responsible for technical specification synchronization (entities, APIs, flows)."""

    @property
    def agent_name(self) -> str:
        return "specification_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[SpecificationAgentOutput]:
        return SpecificationAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: SpecificationAgentInput) -> str:
        return build_specification_system_prompt()

    def build_user_prompt(self, input_data: SpecificationAgentInput) -> str:
        return build_specification_user_prompt(input_data)
