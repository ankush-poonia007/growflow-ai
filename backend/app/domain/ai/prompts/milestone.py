"""
GrowFlow — Milestone Agent Prompt Module.

Groups tasks into major stage gate deliverables and defines verification criteria.

Architecture ref:
  6F § 4.10 — Milestone Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT

if TYPE_CHECKING:
    from backend.app.domain.ai.contracts.agents import MilestoneAgentInput

PROMPT_VERSION: str = "1.0.0"


def build_milestone_system_prompt() -> str:
    """System prompt establishing Milestone Agent stage gate directives."""
    return (
        f"{SHARED_SYSTEM_PROMPT}\n\n"
        "### SPECIALIZED AGENT DIRECTIVE: MILESTONE AGENT\n"
        "You are the Milestone Agent. Your purpose is to group the granular engineering tasks into "
        "major stage gate milestones, establishing target delivery weeks and rigorous verification criteria.\n\n"
        "RESPONSIBILITIES:\n"
        "1. Define at least 3 major milestones with IDs matching regex '^M\\d{1,2}$' (e.g. M1, M2, M3).\n"
        "2. Map each milestone to one of the canonical gate decisions:\n"
        "   - GATE_1_FOUNDATION: Architecture scaffold, database schema, and baseline connectivity.\n"
        "   - GATE_2_CORE_MVP: End-to-end walking skeleton demonstrating core user journey.\n"
        "   - GATE_3_POLISH_HANDOFF: Test suites, CI/CD, documentation, and final release criteria.\n"
        "3. CRITICAL TASK TRACEABILITY: You MUST associate tasks from the supplied task backlog by their exact task IDs (e.g. ['T01', 'T02']).\n"
        "   Never reference non-existent task IDs.\n"
        "4. Assign realistic target weeks that fall within the timeline total duration.\n"
        "5. Formulate unambiguous, testable verification criteria for passing each stage gate.\n"
    )


def build_milestone_user_prompt(input_data: MilestoneAgentInput) -> str:
    """User prompt formatting Timeline phases and Task breakdown inputs."""
    timeline = input_data.timeline
    tasks = input_data.tasks

    tasks_listing = "\n".join(
        f"- [{t.task_id}] {t.title} ({t.category}, {t.estimated_hours}h)" for t in tasks.tasks
    )

    return (
        f"Structure the stage gate milestones for the following project schedule and task breakdown:\n\n"
        f"### PROJECT TIMELINE\n"
        f"- Total Duration: {timeline.estimated_total_weeks} weeks\n"
        f"- Phases: {', '.join(f'{p.name} ({p.duration_weeks}w)' for p in timeline.phases)}\n\n"
        f"### AVAILABLE ENGINEERING TASKS (DATA)\n"
        f"{tasks_listing}\n\n"
        f"TASK:\n"
        f"Generate a rigorous MilestoneAgentOutput conforming strictly to the requested schema. "
        f"Ensure `milestones` has >= 3 items with unique IDs matching '^M\\d{{1,2}}$', valid GateDecisions, "
        f"and `associated_task_ids` referencing real task IDs from the backlog."
    )
