"""
GrowFlow — Milestone Agent Implementation.

Groups tasks into major stage gate deliverables and defines verification criteria.

Architecture ref:
  6F § 4.10 — Milestone Agent
  Gate 09 Decision A1 — Task -> Milestone serial dependency
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import (
    MilestoneAgentInput,
    MilestoneAgentOutput,
)
from backend.app.domain.ai.prompts.milestone import (
    PROMPT_VERSION,
    build_milestone_system_prompt,
    build_milestone_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class MilestoneAgent(BaseAgent[MilestoneAgentInput, MilestoneAgentOutput]):
    """Agent responsible for defining stage gate deliverables and grouping task milestones."""

    @property
    def agent_name(self) -> str:
        return "milestone_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[MilestoneAgentOutput]:
        return MilestoneAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: MilestoneAgentInput) -> str:
        return build_milestone_system_prompt()

    def build_user_prompt(self, input_data: MilestoneAgentInput) -> str:
        return build_milestone_user_prompt(input_data)
