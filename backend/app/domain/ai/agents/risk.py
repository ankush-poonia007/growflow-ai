"""
GrowFlow — Risk Agent Implementation.

Synthesizes technical, security, operational, and schedule risks with mitigations and fallbacks.

Architecture ref:
  6F § 4.8 — Risk Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import RiskAgentInput, RiskAgentOutput
from backend.app.domain.ai.prompts.risk import (
    PROMPT_VERSION,
    build_risk_system_prompt,
    build_risk_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class RiskAgent(BaseAgent[RiskAgentInput, RiskAgentOutput]):
    """Agent responsible for threat modeling, risk evaluation, and mitigation planning."""

    @property
    def agent_name(self) -> str:
        return "risk_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[RiskAgentOutput]:
        return RiskAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: RiskAgentInput) -> str:
        return build_risk_system_prompt()

    def build_user_prompt(self, input_data: RiskAgentInput) -> str:
        return build_risk_user_prompt(input_data)
