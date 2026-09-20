"""
GrowFlow — Technology Agent Prompt Module.

Synthesizes production-grade technology stack selections with learning curves and educational rationales.

Architecture ref:
  6F § 4.3 — Technology Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT

if TYPE_CHECKING:
    from backend.app.domain.ai.contracts.agents import TechnologyAgentInput

PROMPT_VERSION: str = "1.0.0"


def build_technology_system_prompt() -> str:
    """System prompt establishing Technology Agent architectural stack directives."""
    return (
        f"{SHARED_SYSTEM_PROMPT}\n\n"
        "### SPECIALIZED AGENT DIRECTIVE: TECHNOLOGY AGENT\n"
        "You are the Technology Agent. Your purpose is to select a cohesive, modern, and production-grade "
        "technology stack tailored to the project requirements, constraints, and the student's assessed skill tier.\n\n"
        "RESPONSIBILITIES:\n"
        "1. Select explicit technologies for Backend, Database, Frontend, Security/Auth, and Telemetry/Observability.\n"
        "2. Provide clear versions, roles, technical rationales, and honest learning curve evaluations (LOW, MODERATE, STEEP).\n"
        "3. Specify communication protocols (e.g. HTTPS/REST, WebSockets, Event Streams).\n"
        "4. Balance student preferences against architectural suitability. If a student preferred tool is inappropriate, "
        "gently substitute it with a superior alternative and document the reasoning in the justification matrix.\n"
        "5. Ensure interoperability between chosen components (e.g. relational DB with async ORM and typed schema models).\n"
        "6. Do not introduce extraneous distributed systems (Kafka, Kubernetes, microservices) unless strictly warranted.\n"
    )


def build_technology_user_prompt(input_data: TechnologyAgentInput) -> str:
    """User prompt formatting Idea, Scope, student skill tier, and preferred technologies."""
    prefs = (
        ", ".join(input_data.preferred_technologies)
        if input_data.preferred_technologies
        else "None specified."
    )
    scope = input_data.scope

    return (
        f"Select the technology stack for the following project:\n\n"
        f"### PROJECT IDEA SUMMARY\n"
        f"- Title: {input_data.idea.refined_title}\n"
        f"- Domain: {input_data.idea.core_domain}\n"
        f"- Problem: {input_data.idea.problem_statement}\n\n"
        f"### SCOPE & CONSTRAINTS\n"
        f"- In-Scope: {', '.join(scope.in_scope)}\n"
        f"- Out-of-Scope: {', '.join(scope.out_of_scope)}\n"
        f"- Architectural Boundaries: {', '.join(scope.architectural_boundaries)}\n"
        f"- Technical Constraints: {', '.join(scope.technical_constraints)}\n\n"
        f"### STUDENT PROFILE\n"
        f"- Assessed Skill Tier: {input_data.student_skill_level}\n"
        f"- Student Preferred Technologies: {prefs}\n\n"
        f"TASK:\n"
        f"Generate a rigorous TechnologyAgentOutput conforming strictly to the requested schema. "
        f"Populate backend, database, frontend, security_auth, telemetry_observability, communication_protocols (>= 1), "
        f"and justification_matrix."
    )
