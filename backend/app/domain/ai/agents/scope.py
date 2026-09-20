"""
GrowFlow — Scope Agent Implementation.

Enforces boundaries, exclusions, architectural constraints, and deliverable outcomes.

Architecture ref:
  6F § 4.2 — Scope Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import ScopeAgentInput, ScopeAgentOutput
from backend.app.domain.ai.prompts.scope import (
    PROMPT_VERSION,
    build_scope_system_prompt,
    build_scope_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class ScopeAgent(BaseAgent[ScopeAgentInput, ScopeAgentOutput]):
    """Agent responsible for defining in/out-of-scope boundaries and architectural constraints."""

    @property
    def agent_name(self) -> str:
        return "scope_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[ScopeAgentOutput]:
        return ScopeAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: ScopeAgentInput) -> str:
        return build_scope_system_prompt()

    def build_user_prompt(self, input_data: ScopeAgentInput) -> str:
        return build_scope_user_prompt(input_data)
