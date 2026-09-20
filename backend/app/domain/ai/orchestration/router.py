"""
GrowFlow — LangGraph Routing & Regeneration Logic.

Enforces:
- QA Evaluation Gate: PASS iff overall_score >= 75 AND zero CRITICAL findings.
- Bounded automatic regeneration: Maximum 2 attempts per generation job.
- Targeted node identification: Extracting failing target agent and feedback hint.
- Dynamic routing back to targeted generator node while preserving valid upstream outputs.

Architecture ref:
  6F § 31 — QA Severity & Gate
  6F § 32 — Targeted Regeneration
  6F § 35 — Regeneration Boundaries (max 2 attempts)
  Gate 09 — Decision A3 (Frozen Resolution)
  Gate 09 — Unit 4 LangGraph Orchestration
"""

from __future__ import annotations

from typing import Any

from backend.app.domain.ai.orchestration.state import (
    OrchestrationState,  # noqa: TC001 — Needed at runtime for LangGraph type hint reflection
)
from backend.app.domain.blueprint.models import BlueprintQAStatus

VALID_REGENERATION_TARGETS: set[str] = {
    "idea",
    "scope",
    "technology",
    "features",
    "mvp",
    "specification",
    "timeline",
    "risk",
    "task",
    "milestone",
    "readme",
}

MAX_REGENERATION_ATTEMPTS: int = 2
QA_PASS_SCORE_THRESHOLD: int = 75


def evaluate_qa_pass_condition(state: OrchestrationState) -> bool:
    """
    Evaluate Gate 09 Decision A3 rule:
    PASS iff overall_score >= 75 AND zero CRITICAL findings.
    """
    qa_status = state.get("qa_status")
    score = state.get("qa_score") or 0
    findings = state.get("qa_findings", [])

    has_critical = any(
        getattr(f, "severity", None) == "CRITICAL"
        or (isinstance(f, dict) and f.get("severity") == "CRITICAL")
        for f in findings
    )

    if has_critical:
        return False

    if score < QA_PASS_SCORE_THRESHOLD:
        return False

    return qa_status == BlueprintQAStatus.PASS or score >= QA_PASS_SCORE_THRESHOLD


def route_after_qa(state: OrchestrationState) -> str:
    """
    Conditional edge function evaluated immediately after QA / Judge execution.
    Returns:
    - 'end_passed': Workflow succeeded, ready for canonical persistence.
    - 'end_cancelled': Cooperative cancellation was acknowledged.
    - 'end_failed': Bounded regeneration attempts exhausted (>= 2).
    - 'regeneration_router': Bounded retry eligible, proceeds to target identification.
    """
    if state.get("cancellation_requested", False) or state.get("workflow_status") == "CANCELLING":
        return "end_cancelled"

    if evaluate_qa_pass_condition(state):
        return "end_passed"

    attempt = state.get("regeneration_attempt", 0)
    if attempt >= MAX_REGENERATION_ATTEMPTS:
        return "end_failed"

    return "regeneration_router"


def node_regeneration_router(state: OrchestrationState) -> dict[str, Any]:
    """
    StateGraph node executed when QA evaluation fails and automatic attempts remain.
    Increments the regeneration counter, determines the target agent to re-run,
    and formats the targeted revision hint.
    """
    current_attempt = state.get("regeneration_attempt", 0) + 1
    findings = state.get("qa_findings", [])

    # 1. Identify targeted agent from QA findings
    chosen_target: str | None = None
    chosen_hint: str | None = None

    # First priority: finding explicitly requesting regeneration
    for f in findings:
        target = getattr(f, "target_agent", None) or (
            f.get("target_agent") if isinstance(f, dict) else None
        )
        requires_regen = getattr(f, "requires_regeneration", False) or (
            f.get("requires_regeneration") if isinstance(f, dict) else False
        )
        if target:
            clean_target = str(target).lower().replace("_agent", "")
            if clean_target in VALID_REGENERATION_TARGETS and requires_regen:
                chosen_target = clean_target
                rec = getattr(f, "recommendation", "") or (
                    f.get("recommendation", "") if isinstance(f, dict) else ""
                )
                desc = getattr(f, "description", "") or (
                    f.get("description", "") if isinstance(f, dict) else ""
                )
                chosen_hint = rec or desc
                break

    # Second priority: finding with highest severity (CRITICAL or ERROR)
    if not chosen_target:
        for f in findings:
            target = getattr(f, "target_agent", None) or (
                f.get("target_agent") if isinstance(f, dict) else None
            )
            severity = getattr(f, "severity", "") or (
                f.get("severity", "") if isinstance(f, dict) else ""
            )
            if target:
                clean_target = str(target).lower().replace("_agent", "")
                if clean_target in VALID_REGENERATION_TARGETS and severity in ["CRITICAL", "ERROR"]:
                    chosen_target = clean_target
                    rec = getattr(f, "recommendation", "") or (
                        f.get("recommendation", "") if isinstance(f, dict) else ""
                    )
                    desc = getattr(f, "description", "") or (
                        f.get("description", "") if isinstance(f, dict) else ""
                    )
                    chosen_hint = rec or desc
                    break

    # Fallback default: timeline or features
    if not chosen_target:
        chosen_target = state.get("regeneration_target") or "features"
        chosen_hint = "Address QA findings to ensure architectural consistency and completeness."

    return {
        "regeneration_attempt": current_attempt,
        "regeneration_target": chosen_target,
        "qa_feedback_hint": chosen_hint,
        "current_step": f"regenerating_{chosen_target}",
        "workflow_status": "RUNNING",
    }


def route_from_regeneration_router(state: OrchestrationState) -> str:
    """
    Conditional edge function routing from regeneration_router to the targeted generator node.
    """
    target = state.get("regeneration_target", "features")
    if target in VALID_REGENERATION_TARGETS:
        return target
    return "features"
