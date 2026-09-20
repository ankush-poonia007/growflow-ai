"""
GrowFlow — Timeline Agent Implementation.

Synthesizes phased implementation schedule, total duration, and critical path analysis.

Architecture ref:
  6F § 4.7 — Timeline Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import TimelineAgentInput, TimelineAgentOutput
from backend.app.domain.ai.prompts.timeline import (
    PROMPT_VERSION,
    build_timeline_system_prompt,
    build_timeline_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class TimelineAgent(BaseAgent[TimelineAgentInput, TimelineAgentOutput]):
    """Agent responsible for phased sprint schedule, duration calculation, and critical path."""

    @property
    def agent_name(self) -> str:
        return "timeline_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[TimelineAgentOutput]:
        return TimelineAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: TimelineAgentInput) -> str:
        return build_timeline_system_prompt()

    def build_user_prompt(self, input_data: TimelineAgentInput) -> str:
        return build_timeline_user_prompt(input_data)
