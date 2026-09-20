"""
GrowFlow — QA / Judge Agent Prompt Module.

Evaluates synthesized blueprint sections against project problem, assessment EPU, and consistency rules.

Architecture ref:
  6F § 4.12 — QA / Judge Agent
  6E § 18   — Model Capabilities (QA = REASONING)
  Gate 09 Decision A3 — QA evaluation thresholds
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT

if TYPE_CHECKING:
    from backend.app.domain.ai.contracts.qa import QAJudgeAgentInput

PROMPT_VERSION: str = "1.0.0"


def build_qa_judge_system_prompt() -> str:
    """System prompt establishing QA / Judge Agent evaluation directives."""
    return (
        f"{SHARED_SYSTEM_PROMPT}\n\n"
        "### SPECIALIZED AGENT DIRECTIVE: QA / JUDGE AGENT (REASONING TIER)\n"
        "You are the QA / Judge Agent operating at the REASONING capability tier. Your purpose is to act as "
        "a rigorous, objective architectural review board evaluating the entire synthesized project blueprint.\n\n"
        "EVALUATION CRITERIA (Score each dimension 0 to 100):\n"
        "1. Completeness: Are all required sections, entities, APIs, tasks, and milestones substantive and fully specified?\n"
        "2. Technical Consistency: Do data entities, endpoints, technologies, and features align without contradictions?\n"
        "3. Scope Containment: Are all features strictly within the in-scope boundary without violating out-of-scope exclusions?\n"
        "4. Student Feasibility: Is the complexity realistic given the student's assessed skill tier and readiness score?\n"
        "5. Architectural Rigor: Are security, threat mitigations, and test automation adequately addressed?\n\n"
        "FROZEN GATE 09 DECISION A3 (PASS / FAIL RULE):\n"
        "- PASS requires: overall_score >= 75 AND ZERO CRITICAL findings.\n"
        "- If overall_score < 75 OR any finding has severity == 'CRITICAL', status MUST BE 'FAIL'.\n"
        "- If status == 'FAIL', you MUST specify a concrete `regeneration_target` (e.g. 'features_agent', 'technology_agent') "
        "or set `requires_human_review` = true if contradictions are fatal.\n\n"
        "SEVERITY DEFINITIONS FOR FINDINGS:\n"
        "- CRITICAL: Blocker violation (e.g. direct contradiction of scope, impossible architecture, severe security gap). Blocks PASS.\n"
        "- ERROR: Significant technical flaw that impairs execution quality.\n"
        "- WARNING: Tradeoff or optimization opportunity that should be addressed.\n"
        "- INFO: Minor educational note or stylistic suggestion.\n"
    )


def build_qa_judge_user_prompt(input_data: QAJudgeAgentInput) -> str:
    """User prompt formatting base context, assessment EPU, and all synthesized agent outputs."""
    p_ctx = input_data.project_context
    a_ctx = input_data.assessment_context

    sections_summary: dict[str, str] = {}
    for section_name, section_payload in input_data.all_agent_outputs.items():
        if isinstance(section_payload, dict):
            title = (
                section_payload.get("refined_title")
                or section_payload.get("mvp_name")
                or section_payload.get("project_title")
                or ""
            )
            summary = section_payload.get("summary") or json.dumps(section_payload)[:300]
            if title:
                sections_summary[section_name] = f"{title} — {summary}"
            else:
                sections_summary[section_name] = summary
        else:
            sections_summary[section_name] = str(section_payload)[:300]

    sections_formatted = "\n".join(
        f"- [{name}]: {content}" for name, content in sections_summary.items()
    )

    return (
        f"Evaluate the complete project blueprint for the following project:\n\n"
        f"### PROJECT BASE CONTEXT\n"
        f"- Project Name: {p_ctx.name}\n"
        f"- Problem: {p_ctx.problem}\n"
        f"- Proposed Solution: {p_ctx.proposed_solution}\n"
        f"- Target Complexity: {p_ctx.complexity}\n\n"
        f"### STUDENT ASSESSMENT EPU (DATA)\n"
        f"- Assessed Skill Tier: {a_ctx.skill_level}\n"
        f"- Technical Confidence: {a_ctx.technical_confidence}\n"
        f"- Assessment Score: {a_ctx.overall_score}\n"
        f"- Readiness Tier: {a_ctx.readiness_tier}\n"
        f"- Identified Gaps: {', '.join(a_ctx.identified_gaps) if a_ctx.identified_gaps else 'None'}\n\n"
        f"### SYNTHESIZED BLUEPRINT SECTIONS (DATA)\n"
        f"{sections_formatted}\n\n"
        f"TASK:\n"
        f"Generate a rigorous QAJudgeAgentOutput conforming strictly to the requested schema. "
        f"Enforce the frozen Gate 09 Decision A3 rule: status is PASS iff overall_score >= 75 AND zero CRITICAL findings exist. "
        f"If failed, specify `regeneration_target` or set `requires_human_review` to true."
    )
