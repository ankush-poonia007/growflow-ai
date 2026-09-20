"""
GrowFlow — MVP Agent Implementation.

Defines the Stage-1 Minimum Viable Product boundary, core user journey, and validation criteria.

Architecture ref:
  6F § 4.5 — MVP Agent
  6E § 18  — Model Capabilities (MVP = REASONING)
  Gate 09 Decision A4 — Model capability policy
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import MVPAgentInput, MVPAgentOutput
from backend.app.domain.ai.prompts.mvp import (
    PROMPT_VERSION,
    build_mvp_system_prompt,
    build_mvp_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class MVPAgent(BaseAgent[MVPAgentInput, MVPAgentOutput]):
    """Agent responsible for defining the lean walking skeleton MVP boundary using high-depth reasoning."""

    @property
    def agent_name(self) -> str:
        return "mvp_agent"

    @property
    def capability(self) -> ProviderCapability:
        # Frozen architectural requirement: MVP uses REASONING tier
        return ProviderCapability.REASONING

    @property
    def output_schema(self) -> type[MVPAgentOutput]:
        return MVPAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: MVPAgentInput) -> str:
        return build_mvp_system_prompt()

    def build_user_prompt(self, input_data: MVPAgentInput) -> str:
        return build_mvp_user_prompt(input_data)
