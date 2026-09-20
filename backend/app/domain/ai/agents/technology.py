"""
GrowFlow — Technology Agent Implementation.

Recommends a cohesive, production-grade technical stack with educational learning rationales.

Architecture ref:
  6F § 4.3 — Technology Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import TechnologyAgentInput, TechnologyAgentOutput
from backend.app.domain.ai.prompts.technology import (
    PROMPT_VERSION,
    build_technology_system_prompt,
    build_technology_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class TechnologyAgent(BaseAgent[TechnologyAgentInput, TechnologyAgentOutput]):
    """Agent responsible for selecting and justifying the complete architectural technology stack."""

    @property
    def agent_name(self) -> str:
        return "technology_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[TechnologyAgentOutput]:
        return TechnologyAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: TechnologyAgentInput) -> str:
        return build_technology_system_prompt()

    def build_user_prompt(self, input_data: TechnologyAgentInput) -> str:
        return build_technology_user_prompt(input_data)
