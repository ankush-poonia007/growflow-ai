"""
GrowFlow — Scope Agent Prompt Module.

Establishes rigid functional boundaries, exclusions, constraints, and deliverable outcomes.

Architecture ref:
  6F § 4.2 — Scope Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT

if TYPE_CHECKING:
    from backend.app.domain.ai.contracts.agents import ScopeAgentInput

PROMPT_VERSION: str = "1.0.0"


def build_scope_system_prompt() -> str:
    """System prompt establishing Scope Agent boundary directives."""
    return (
        f"{SHARED_SYSTEM_PROMPT}\n\n"
        "### SPECIALIZED AGENT DIRECTIVE: SCOPE AGENT\n"
        "You are the Scope Agent. Your primary role is to enforce ruthless engineering discipline and "
        "prevent scope creep by defining strict boundaries around what will be built and what will NOT be built.\n\n"
        "RESPONSIBILITIES:\n"
        "1. Define at least 3 concrete, essential IN-SCOPE capabilities directly serving the project vision.\n"
        "2. Define at least 2 explicit OUT-OF-SCOPE exclusions (non-goals, deferred features, or enterprise complexities).\n"
        "3. Define at least 2 architectural boundaries (e.g. modular monolith vs microservices, client vs server responsibilities).\n"
        "4. Articulate real technical constraints (hardware limits, network latency, deployment footprint, single-node boundaries).\n"
        "5. Specify measurable deliverable outcomes representing success.\n"
        "6. Translate any identified student assessment skill gaps into protective technical constraints.\n"
    )


def build_scope_user_prompt(input_data: ScopeAgentInput) -> str:
    """User prompt formatting Idea output and student assessment gaps."""
    gaps_block = (
        "\n".join(f"- {gap}" for gap in input_data.assessment_gaps)
        if input_data.assessment_gaps
        else "No critical skill gaps identified."
    )

    idea = input_data.idea
    return (
        f"Define the project boundaries and scope for the following validated project idea:\n\n"
        f"### VALIDATED PROJECT IDEA\n"
        f"- Title: {idea.refined_title}\n"
        f"- Core Domain: {idea.core_domain}\n"
        f"- Problem: {idea.problem_statement}\n"
        f"- Proposed Solution: {idea.proposed_solution}\n"
        f"- Target Users: {', '.join(idea.target_users)}\n"
        f"- Value Propositions: {', '.join(idea.value_propositions)}\n\n"
        f"### STUDENT SKILL GAPS FROM ASSESSMENT (DATA)\n"
        f"{gaps_block}\n\n"
        f"TASK:\n"
        f"Generate a rigorous ScopeAgentOutput conforming strictly to the requested schema. "
        f"Ensure `in_scope` has >= 3 items, `out_of_scope` has >= 2 items, `architectural_boundaries` has >= 2 items, "
        f"and `technical_constraints` has >= 1 item."
    )
