"""
GrowFlow — Features Agent Implementation.

Decomposes scope into prioritized backlog items with user stories and dependency tracing.

Architecture ref:
  6F § 4.4 — Features Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import FeaturesAgentInput, FeaturesAgentOutput
from backend.app.domain.ai.prompts.features import (
    PROMPT_VERSION,
    build_features_system_prompt,
    build_features_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class FeaturesAgent(BaseAgent[FeaturesAgentInput, FeaturesAgentOutput]):
    """Agent responsible for decomposing scope into prioritized, structured user features."""

    @property
    def agent_name(self) -> str:
        return "features_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[FeaturesAgentOutput]:
        return FeaturesAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: FeaturesAgentInput) -> str:
        return build_features_system_prompt()

    def build_user_prompt(self, input_data: FeaturesAgentInput) -> str:
        return build_features_user_prompt(input_data)
