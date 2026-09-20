"""
GrowFlow — QA / Judge Agent Implementation.

Evaluates synthesized blueprint sections against project problem, assessment EPU, and consistency rules.

Architecture ref:
  6F § 4.12 — QA / Judge Agent
  6E § 18   — Model Capabilities (QA = REASONING)
  Gate 09 Decision A3 — QA evaluation thresholds
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from backend.app.domain.ai.agents.base import BaseAgent
from backend.app.domain.ai.context.models import AssessmentContext, ProjectBaseContext
from backend.app.domain.ai.contracts.qa import (
    QAJudgeAgentInput,
    QAJudgeAgentOutput,
)
from backend.app.domain.ai.prompts.qa import (
    PROMPT_VERSION,
    build_qa_judge_system_prompt,
    build_qa_judge_user_prompt,
)
from backend.app.infrastructure.ai.models import ProviderCapability

# Rebuild Pydantic forward references using explicit context types namespace
QAJudgeAgentInput.model_rebuild(
    _types_namespace={
        "ProjectBaseContext": ProjectBaseContext,
        "AssessmentContext": AssessmentContext,
    }
)


class QAJudgeAgent(BaseAgent[QAJudgeAgentInput, QAJudgeAgentOutput]):
    """Agent responsible for comprehensive blueprint quality evaluation, scoring, and gate verdicts."""

    @property
    def agent_name(self) -> str:
        return "qa_judge_agent"

    @property
    def capability(self) -> ProviderCapability:
        # Frozen architectural requirement: QA/Judge uses REASONING tier
        return ProviderCapability.REASONING

    @property
    def output_schema(self) -> type[QAJudgeAgentOutput]:
        return QAJudgeAgentOutput

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_system_prompt(self, input_data: QAJudgeAgentInput) -> str:
        return build_qa_judge_system_prompt()

    def build_user_prompt(self, input_data: QAJudgeAgentInput) -> str:
        return build_qa_judge_user_prompt(input_data)
