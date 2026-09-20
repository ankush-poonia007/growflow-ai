"""
GrowFlow — Task Agent Prompt Module.

Decomposes specifications, technology, timeline, and risk mitigations into granular engineering tasks.

Architecture ref:
  6F § 4.9 — Task Agent
  Gate 09 — Unit 3 Implementation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT

if TYPE_CHECKING:
    from backend.app.domain.ai.contracts.agents import TaskAgentInput

PROMPT_VERSION: str = "1.0.0"


def build_task_system_prompt() -> str:
    """System prompt establishing Task Agent work breakdown directives."""
    return (
        f"{SHARED_SYSTEM_PROMPT}\n\n"
        "### SPECIALIZED AGENT DIRECTIVE: TASK AGENT\n"
        "You are the Task Agent. Your purpose is to translate specifications, features, technology stack, "
        "and risk mitigations into an actionable engineering work breakdown structure (WBS).\n\n"
        "RESPONSIBILITIES:\n"
        "1. Generate at least 8 granular, actionable engineering tasks.\n"
        "2. Deterministically assign unique IDs matching regex '^T\\d{2}$' (e.g. T01, T02, T03, ..., T08).\n"
        "3. Cover foundational and full-lifecycle engineering categories: "
        "SETUP, DATABASE, BACKEND, FRONTEND, INTEGRATION, TESTING, DEPLOYMENT.\n"
        "4. Assign realistic effort in hours (integer >= 1, typical tasks range 4 to 16 hours).\n"
        "5. Explicitly declare task dependencies by task ID (e.g. T03 depends on ['T01', 'T02']). Avoid cyclic dependencies.\n"
        "6. Trace features back to specific tasks where applicable by referencing the feature_id (e.g. 'F01').\n"
        "7. Include explicit tasks addressing test automation (unit/integration) and risk mitigation.\n"
    )


def build_task_user_prompt(input_data: TaskAgentInput) -> str:
    """User prompt formatting Specification, Technology, Features, Timeline, and Risk inputs."""
    spec = input_data.specification
    tech = input_data.technology
    features = input_data.features
    timeline = input_data.timeline
    risks = input_data.risks

    return (
        f"Decompose the following project into granular engineering tasks:\n\n"
        f"### ARCHITECTURAL SPECIFICATIONS\n"
        f"- Entities: {', '.join(e.entity_name for e in spec.entities)}\n"
        f"- Endpoints: {', '.join(f'{ep.method} {ep.path}' for ep in spec.api_endpoints)}\n\n"
        f"### TECHNOLOGY STACK\n"
        f"- Backend: {tech.backend.name}\n"
        f"- Database: {tech.database.name}\n"
        f"- Frontend: {tech.frontend.name}\n\n"
        f"### FEATURE BACKLOG\n"
        f"{', '.join(f'[{f.feature_id}] {f.title}' for f in features.features)}\n\n"
        f"### TIMELINE SCHEDULE\n"
        f"- Total Weeks: {timeline.estimated_total_weeks}\n"
        f"- Phases: {', '.join(p.name for p in timeline.phases)}\n\n"
        f"### KEY RISKS TO MITIGATE\n"
        f"{', '.join(f'[{r.risk_id}] {r.title}' for r in risks.risks[:3])}\n\n"
        f"TASK:\n"
        f"Generate a rigorous TaskAgentOutput conforming strictly to the requested schema. "
        f"Ensure `tasks` contains at least 8 items with unique IDs matching '^T\\d{{2}}$' and positive estimated_hours."
    )
