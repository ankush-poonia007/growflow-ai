"""
GrowFlow — QA / Judge Agent Contracts & Scorecard.

Defines:
- QASeverity: Canonical severity levels (INFO, WARNING, ERROR, CRITICAL).
- QAFinding: Structured individual evaluation finding.
- QAJudgeAgentInput: Input context containing all synthesized outputs and base contexts.
- QAJudgeAgentOutput: Evaluated QA scorecard and gate decision.

Frozen QA Pass Rule:
  PASS iff:
    overall_score >= 75
    AND
    zero CRITICAL findings

Architecture ref:
  6F § 4.12 — QA/Judge Agent
  6F § 30   — QA Trigger Categories
  6F § 31   — QA Severity
  Gate 09 Decision A3 — QA evaluation thresholds
  Gate 09 — Unit 2 Implementation
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.domain.ai.contracts.base import BaseAgentInput, BaseAgentOutput
from backend.app.domain.blueprint.models import BlueprintQAStatus

if TYPE_CHECKING:
    from backend.app.domain.ai.context.models import AssessmentContext, ProjectBaseContext


class QASeverity(StrEnum):
    """
    Authoritative QA severity taxonomy.
    CRITICAL findings immediately block blueprint approval.
    """

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class QAFinding(BaseModel):
    """A discrete discrepancy, contradiction, or gap identified during QA."""

    model_config = ConfigDict(extra="forbid")

    finding_id: str = Field(..., description="Unique finding ID (e.g. QA-F01).")
    section: str = Field(..., description="Affected blueprint section key.")
    target_agent: str = Field(
        ..., description="Agent responsible for emitting the affected section."
    )
    severity: QASeverity = Field(..., description="Severity level.")
    category: str = Field(
        ...,
        description="Category (e.g. SCHEMA, CONTRADICTION, SCOPE_VIOLATION, TECH_INCONSISTENCY).",
    )
    description: str = Field(..., description="Detailed description of the issue.")
    recommendation: str = Field(..., description="Actionable recommendation for resolution.")
    requires_regeneration: bool = Field(
        default=False,
        description="Whether this finding warrants targeted agent regeneration.",
    )


class QAJudgeAgentInput(BaseAgentInput):
    """Input context for QA / Judge Agent."""

    all_agent_outputs: dict[str, Any] = Field(
        ...,
        description="Mapping of agent names/sections to their structured output payloads.",
    )
    project_context: ProjectBaseContext = Field(
        ...,
        description="Authoritative base project metadata.",
    )
    assessment_context: AssessmentContext = Field(
        ...,
        description="Authoritative student assessment EPU and answers.",
    )


class QAJudgeAgentOutput(BaseAgentOutput):
    """Evaluated scorecard and gate verdict produced by QA / Judge Agent."""

    status: BlueprintQAStatus = Field(
        ...,
        description="Authoritative gate status (PASS or FAIL).",
    )
    overall_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall blueprint quality score (0 to 100).",
    )
    evaluated_criteria: dict[str, int] = Field(
        default_factory=dict,
        description="Scores per dimension (completeness, consistency, feasibility, etc.).",
    )
    findings: list[QAFinding] = Field(
        default_factory=list,
        description="List of identified issues across all sections.",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Overall architectural guidance.",
    )
    regeneration_target: str | None = Field(
        default=None,
        description="Agent name or section key recommended for targeted regeneration if status is FAIL.",
    )
    requires_human_review: bool = Field(
        default=False,
        description="True if automated regeneration is exhausted or fatal contradiction detected.",
    )

    @model_validator(mode="after")
    def enforce_frozen_qa_pass_rule(self) -> QAJudgeAgentOutput:
        """
        Enforce Gate 09 Decision A3:
        PASS requires overall_score >= 75 AND zero CRITICAL findings.
        If any CRITICAL finding exists or score < 75, status MUST be FAIL.
        """
        has_critical = any(f.severity == QASeverity.CRITICAL for f in self.findings)
        score_eligible = self.overall_score >= 75

        if self.status == BlueprintQAStatus.PASS:
            if has_critical:
                raise ValueError(
                    "QA status cannot be PASS when CRITICAL findings exist. "
                    f"Found {sum(1 for f in self.findings if f.severity == QASeverity.CRITICAL)} CRITICAL finding(s)."
                )
            if not score_eligible:
                raise ValueError(
                    f"QA status cannot be PASS when overall_score ({self.overall_score}) is below 75."
                )

        if (
            self.status == BlueprintQAStatus.FAIL
            and not self.regeneration_target
            and not self.requires_human_review
        ):
            # When failed, a target agent or human review escalation is expected
            pass

        return self
