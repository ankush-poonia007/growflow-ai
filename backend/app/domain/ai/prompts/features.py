"""
GrowFlow — Features Agent Prompt Module.

Decomposes scope into prioritized functional backlog capabilities with user stories and dependencies.

Architecture ref:
  6F § 4.4 — Features Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT

if TYPE_CHECKING:
    from backend.app.domain.ai.contracts.agents import FeaturesAgentInput

PROMPT_VERSION: str = "1.0.0"


def build_features_system_prompt() -> str:
    """System prompt establishing Features Agent functional breakdown directives."""
    return (
        f"{SHARED_SYSTEM_PROMPT}\n\n"
        "### SPECIALIZED AGENT DIRECTIVE: FEATURES AGENT\n"
        "You are the Features Agent. Your purpose is to translate the project idea and scope into a "
        "prioritized, actionable backlog of discrete software features.\n\n"
        "RESPONSIBILITIES:\n"
        "1. Generate at least 4 discrete, substantive features.\n"
        "2. Deterministically format feature IDs as F01, F02, F03, F04, etc. All feature IDs must be unique.\n"
        "3. Prioritize each feature as P0 (Must Have / Foundational), P1 (Should Have / Core Functional), or P2 (Nice to Have).\n"
        "4. CRITICAL INVARIANT: You MUST include at least two P0 features.\n"
        "5. Frame every feature with a standard user story ('As a <user>, I want <action> so that <benefit>').\n"
        "6. Group features into logical subsystem modules (e.g. Auth, Telemetry, Dashboard, Reporting).\n"
        "7. Declare explicit dependencies between features using feature IDs (e.g. ['F01']).\n"
        "8. STRICT SCOPE ENFORCEMENT: Never create features that fall into the out-of-scope declarations.\n"
    )


def build_features_user_prompt(input_data: FeaturesAgentInput) -> str:
    """User prompt formatting Idea and Scope inputs for feature breakdown."""
    idea = input_data.idea
    scope = input_data.scope

    return (
        f"Decompose the following scoped project into functional features:\n\n"
        f"### PROJECT IDEA\n"
        f"- Title: {idea.refined_title}\n"
        f"- Target Users: {', '.join(idea.target_users)}\n"
        f"- Vision: {idea.vision_statement}\n\n"
        f"### STRICT SCOPE BOUNDARIES\n"
        f"- In-Scope Capabilities: {', '.join(scope.in_scope)}\n"
        f"- Explicit Out-of-Scope Exclusions: {', '.join(scope.out_of_scope)}\n"
        f"- Technical Constraints: {', '.join(scope.technical_constraints)}\n\n"
        f"TASK:\n"
        f"Generate a rigorous FeaturesAgentOutput conforming strictly to the requested schema. "
        f"Ensure `features` has at least 4 items, unique IDs matching regex '^F\\d{{2}}$', and at least 2 P0 features."
    )
