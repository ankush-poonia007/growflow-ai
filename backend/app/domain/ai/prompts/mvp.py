"""
GrowFlow — MVP Agent Prompt Module.

Synthesizes the lean Stage-1 Minimum Viable Product boundary, core user journey, and validation criteria.

Architecture ref:
  6F § 4.5 — MVP Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT

if TYPE_CHECKING:
    from backend.app.domain.ai.contracts.agents import MVPAgentInput

PROMPT_VERSION: str = "1.0.0"


def build_mvp_system_prompt() -> str:
    """System prompt establishing MVP Agent reasoning directives."""
    return (
        f"{SHARED_SYSTEM_PROMPT}\n\n"
        "### SPECIALIZED AGENT DIRECTIVE: MVP AGENT (REASONING TIER)\n"
        "You are the MVP Agent operating at the REASONING capability tier. Your purpose is to define the "
        "leanest possible Stage-1 walking skeleton that delivers end-to-end user value while strictly protecting "
        "the student from over-commitment.\n\n"
        "RESPONSIBILITIES:\n"
        "1. Define a concise, memorable MVP name.\n"
        "2. Articulate an end-to-end core user journey (minimum 3 sequential steps) that proves the system works.\n"
        "3. Specify included capabilities (minimum 2) representing the foundational core.\n"
        "4. Explicitly state capabilities deferred from MVP (minimum 1) to protect the delivery timeline.\n"
        "5. Formulate measurable, testable validation criteria (minimum 2) to evaluate whether the MVP is successful.\n"
        "6. Describe the minimum viable architecture (monolithic, single container, or simple client-server).\n"
        "7. If external research evidence is provided in context, incorporate its insights into feasibility criteria.\n"
    )


def build_mvp_user_prompt(input_data: MVPAgentInput) -> str:
    """User prompt formatting Idea, Scope, and optional research evidence."""
    idea = input_data.idea
    scope = input_data.scope

    research_block = "No external research evidence provided."
    if input_data.research_evidence:
        research_block = "\n".join(
            f"- [{r.source_type}] {r.title}: {r.snippet}" for r in input_data.research_evidence
        )

    return (
        f"Define the Stage-1 MVP boundary for the following project:\n\n"
        f"### PROJECT IDEA\n"
        f"- Title: {idea.refined_title}\n"
        f"- Vision: {idea.vision_statement}\n"
        f"- Core Domain: {idea.core_domain}\n\n"
        f"### SCOPE BOUNDARIES\n"
        f"- In-Scope: {', '.join(scope.in_scope)}\n"
        f"- Out-of-Scope: {', '.join(scope.out_of_scope)}\n"
        f"- Technical Constraints: {', '.join(scope.technical_constraints)}\n\n"
        f"### RESEARCH EVIDENCE (DATA)\n"
        f"{research_block}\n\n"
        f"TASK:\n"
        f"Generate a rigorous MVPAgentOutput conforming strictly to the requested schema. "
        f"Ensure `core_user_journey` has >= 3 steps, `included_capabilities` has >= 2 items, "
        f"`excluded_from_mvp` has >= 1 item, and `validation_criteria` has >= 2 items."
    )
