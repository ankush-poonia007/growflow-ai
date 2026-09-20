"""
GrowFlow — README Agent Prompt Module.

Synthesizes comprehensive developer onboarding documentation, architecture overview, and environment configuration specs.

Architecture ref:
  6F § 4.11 — README Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT

if TYPE_CHECKING:
    from backend.app.domain.ai.contracts.agents import ReadmeAgentInput

PROMPT_VERSION: str = "1.0.0"


def build_readme_system_prompt() -> str:
    """System prompt establishing README Agent developer guide directives."""
    return (
        f"{SHARED_SYSTEM_PROMPT}\n\n"
        "### SPECIALIZED AGENT DIRECTIVE: README AGENT\n"
        "You are the README Agent. Your purpose is to harmonize all upstream validated architectural decisions "
        "into a professional, comprehensive, and developer-friendly project README and setup guide.\n\n"
        "RESPONSIBILITIES:\n"
        "1. Synthesize a professional project title and punchy, descriptive tagline.\n"
        "2. Provide an executive technical overview of the project mission and problem it solves.\n"
        "3. Provide an architecture overview describing component interactions and architectural boundaries.\n"
        "4. Summarize the technology stack into a clean dictionary of key-value pairs (e.g. {'Backend': 'FastAPI', 'Database': 'PostgreSQL'}).\n"
        "5. Formulate step-by-step local developer setup instructions (minimum 2 steps: clone, install, run migrations, start server).\n"
        "6. Specify necessary environment variables with default placeholders and descriptions.\n"
        "   SECURITY RULE: NEVER output real credentials, secret API keys, or production passwords. Use placeholders (e.g. 'your-secret-here').\n"
        "7. Include standard open-source or educational contributing guidelines.\n"
        "8. STRICT CONSISTENCY: Every technology mentioned in the README MUST match the decisions made by the Technology Agent.\n"
    )


def build_readme_user_prompt(input_data: ReadmeAgentInput) -> str:
    """User prompt formatting the curated context from all 10 preceding generator agents."""
    ctx = input_data.curated_context
    idea = ctx.idea
    tech = ctx.technology
    mvp = ctx.mvp

    return (
        f"Synthesize the project README and onboarding guide for the following validated project:\n\n"
        f"### PROJECT PROFILE\n"
        f"- Title: {idea.refined_title}\n"
        f"- Vision: {idea.vision_statement}\n"
        f"- Problem: {idea.problem_statement}\n"
        f"- Proposed Solution: {idea.proposed_solution}\n\n"
        f"### ARCHITECTURAL TECH STACK\n"
        f"- Backend: {tech.backend.name} ({tech.backend.version or 'latest'})\n"
        f"- Database: {tech.database.name} ({tech.database.version or 'latest'})\n"
        f"- Frontend: {tech.frontend.name} ({tech.frontend.version or 'latest'})\n"
        f"- Auth/Security: {tech.security_auth.name}\n\n"
        f"### MVP WALKING SKELETON\n"
        f"- Name: {mvp.mvp_name}\n"
        f"- Architecture: {mvp.minimum_viable_architecture}\n"
        f"- Core User Journey: {' -> '.join(mvp.core_user_journey)}\n\n"
        f"TASK:\n"
        f"Generate a rigorous ReadmeAgentOutput conforming strictly to the requested schema. "
        f"Ensure `getting_started` has >= 2 concrete steps and environment variables are properly described with safe placeholders."
    )
