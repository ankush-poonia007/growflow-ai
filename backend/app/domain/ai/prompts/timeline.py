"""
GrowFlow — Timeline Agent Prompt Module.

Synthesizes phased implementation sprint schedule, total duration, and critical path analysis.

Architecture ref:
  6F § 4.7 — Timeline Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT

if TYPE_CHECKING:
    from backend.app.domain.ai.contracts.agents import TimelineAgentInput

PROMPT_VERSION: str = "1.0.0"


def build_timeline_system_prompt() -> str:
    """System prompt establishing Timeline Agent scheduling directives."""
    return (
        f"{SHARED_SYSTEM_PROMPT}\n\n"
        "### SPECIALIZED AGENT DIRECTIVE: TIMELINE AGENT\n"
        "You are the Timeline Agent. Your purpose is to structure a realistic, phased implementation timeline "
        "and determine the critical path bottlenecks based on the project specification and complexity.\n\n"
        "RESPONSIBILITIES:\n"
        "1. Define at least 3 sequential or partially overlapping development phases (e.g. Foundation, Core Backend/Ingestion, Frontend/Polish).\n"
        "2. For each phase, specify phase_number (1-indexed), name, duration_weeks (integer >= 1), focus_area, deliverables, and dependencies.\n"
        "3. CRITICAL MATHEMATICAL INVARIANT: The sum of `duration_weeks` across all phases MUST EXACTLY equal `estimated_total_weeks`.\n"
        "   Example: If Phase 1 = 3 weeks, Phase 2 = 4 weeks, Phase 3 = 3 weeks, then `estimated_total_weeks` MUST be 10.\n"
        "4. Summarize the critical path sequence identifying high-risk technical bottlenecks.\n"
        "5. Calibrate phase durations to match student capacity (typical capstone projects range 8 to 14 weeks).\n"
    )


def build_timeline_user_prompt(input_data: TimelineAgentInput) -> str:
    """User prompt formatting Idea and Specification inputs for schedule synthesis."""
    spec = input_data.specification
    target_deadline = input_data.project_deadline_weeks or 12

    return (
        f"Synthesize the phased implementation timeline for the following project:\n\n"
        f"### PROJECT PROFILE\n"
        f"- Title: {input_data.idea.refined_title}\n"
        f"- Target Complexity: {input_data.complexity}\n"
        f"- Recommended Project Deadline: {target_deadline} weeks\n\n"
        f"### TECHNICAL SPECIFICATION SUMMARY\n"
        f"- Data Entities to Build: {', '.join(e.entity_name for e in spec.entities)}\n"
        f"- Endpoints to Implement: {', '.join(f'{ep.method} {ep.path}' for ep in spec.api_endpoints)}\n"
        f"- Acceptance Criteria: {'; '.join(spec.system_acceptance_criteria)}\n\n"
        f"TASK:\n"
        f"Generate a rigorous TimelineAgentOutput conforming strictly to the requested schema. "
        f"Ensure `phases` has >= 3 items and the sum of `duration_weeks` of all phases EXACTLY equals `estimated_total_weeks`."
    )
