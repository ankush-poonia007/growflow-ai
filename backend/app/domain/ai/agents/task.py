"""
GrowFlow — Task Agent Implementation.

Decomposes specifications, technology, timeline, and risks into a granular engineering work breakdown structure.

Architecture ref:
  6F § 4.9 — Task Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.contracts.agents import TaskAgentInput, TaskAgentOutput
from backend.app.domain.ai.prompts.task import (
    PROMPT_VERSION,
    build_task_system_prompt,
    build_task_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability


class TaskAgent(BaseAgent[TaskAgentInput, TaskAgentOutput]):
    """Agent responsible for granular work breakdown structure (WBS) and task dependency mapping."""

    @property
    def agent_name(self) -> str:
        return "task_agent"

    @property
    def capability(self) -> ProviderCapability:
        return ProviderCapability.STANDARD

    @property
    def output_schema(self) -> type[TaskAgentOutput]:
        return TaskAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: TaskAgentInput) -> str:
        return build_task_system_prompt()

    def build_user_prompt(self, input_data: TaskAgentInput) -> str:
        return build_task_user_prompt(input_data)
