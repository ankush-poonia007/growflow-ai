"""
GrowFlow — Idea Agent Prompt Module.

Synthesizes raw student concept into an authoritative, domain-scoped project idea.

Architecture ref:
  6F § 4.1 — Idea Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT

if TYPE_CHECKING:
    from backend.app.domain.ai.contracts.agents import IdeaAgentInput

PROMPT_VERSION: str = "1.0.0"


def build_idea_system_prompt() -> str:
    """System prompt establishing Idea Agent reasoning directives."""
    return (
        f"{SHARED_SYSTEM_PROMPT}\n\n"
        "### SPECIALIZED AGENT DIRECTIVE: IDEA AGENT\n"
        "You are the Idea Agent. Your purpose is to elevate a student's initial project concept into "
        "a well-defined, professionally structured software engineering project profile.\n\n"
        "RESPONSIBILITIES:\n"
        "1. Synthesize a professional, compelling project title and concise vision statement.\n"
        "2. Articulate the core problem statement and proposed software solution clearly.\n"
        "3. Identify primary and secondary target user personas.\n"
        "4. Formulate distinct, measurable value propositions.\n"
        "5. Categorize the project into its canonical domain (e.g. Healthcare, EdTech, FinTech, Precision Agriculture).\n"
        "6. Calibrate ambition to the student's assessed skill tier and readiness score.\n"
        "7. State explicit domain assumptions and initial technical warnings.\n"
        "8. CRITICAL: Do not lock the project into a specific programming language, web framework, or database at this stage. "
        "Keep the focus on domain, users, and problem-solution fit.\n"
    )


def build_idea_user_prompt(input_data: IdeaAgentInput) -> str:
    """User prompt formatting student project context and assessment profile."""
    recommendations_block = (
        "\n".join(f"- {rec}" for rec in input_data.assessment_recommendations)
        if input_data.assessment_recommendations
        else "None specified."
    )

    return (
        f"Synthesize the project profile for the following student project:\n\n"
        f"### PROJECT INPUT CONTEXT\n"
        f"- Project Name: {input_data.project_name}\n"
        f"- Target Complexity Preference: {input_data.complexity_preference}\n"
        f"- Assessed Student Skill Level: {input_data.student_skill_level}\n"
        f"- Assessment Readiness Tier: {input_data.assessment_readiness_tier}\n\n"
        f"### STUDENT PROBLEM STATEMENT (DATA)\n"
        f"{input_data.initial_problem}\n\n"
        f"### STUDENT PROPOSED SOLUTION (DATA)\n"
        f"{input_data.initial_solution}\n\n"
        f"### ASSESSMENT RECOMMENDATIONS (DATA)\n"
        f"{recommendations_block}\n\n"
        f"TASK:\n"
        f"Generate a rigorous IdeaAgentOutput conforming strictly to the requested schema. "
        f"Ensure `target_users` contains at least 1 persona and `value_propositions` contains at least 2 distinct value statements."
    )
