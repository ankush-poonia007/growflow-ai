"""
GrowFlow — Idea Agent Implementation.

Transforms student problem/solution context into a structured, domain-scoped project idea.

Architecture ref:
  6F § 4.1 — Idea Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import IdeaAgentInput, IdeaAgentOutput
from backend.app.domain.ai.prompts.idea import (
    PROMPT_VERSION,
    build_idea_system_prompt,
    build_idea_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class IdeaAgent(BaseAgent[IdeaAgentInput, IdeaAgentOutput]):
    """Agent responsible for synthesizing the core domain profile, vision, and value proposition."""

    @property
    def agent_name(self) -> str:
        return "idea_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[IdeaAgentOutput]:
        return IdeaAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: IdeaAgentInput) -> str:
        return build_idea_system_prompt()

    def build_user_prompt(self, input_data: IdeaAgentInput) -> str:
        return build_idea_user_prompt(input_data)
