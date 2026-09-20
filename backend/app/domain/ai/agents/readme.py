"""
GrowFlow — README Agent Implementation.

Synthesizes project repository README, architecture overview, setup guide, and safe environment variable specifications.

Architecture ref:
  6F § 4.11 — README Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import ReadmeAgentInput, ReadmeAgentOutput
from backend.app.domain.ai.prompts.readme import (
    PROMPT_VERSION,
    build_readme_system_prompt,
    build_readme_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class ReadmeAgent(BaseAgent[ReadmeAgentInput, ReadmeAgentOutput]):
    """Agent responsible for developer documentation, setup instructions, and environment configuration specs."""

    @property
    def agent_name(self) -> str:
        return "readme_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[ReadmeAgentOutput]:
        return ReadmeAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: ReadmeAgentInput) -> str:
        return build_readme_system_prompt()

    def build_user_prompt(self, input_data: ReadmeAgentInput) -> str:
        return build_readme_user_prompt(input_data)
