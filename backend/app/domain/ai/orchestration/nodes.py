"""
GrowFlow — LangGraph Node Implementations.

Maps each of the 12 concrete Unit 3 AI agents to a deterministic LangGraph StateGraph node.
Handles input contract construction, cooperative cancellation, provenance collection,
and state patch generation.

Architecture ref:
  6F § 41 — LangGraph Node Design
  6F § 42 — Agent Base Abstraction
  Gate 09 — Unit 3 Concrete Agents
  Gate 09 — Unit 4 Orchestration
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any
import uuid

from backend.app.domain.ai.agents.features import FeaturesAgent
from backend.app.domain.ai.agents.idea import IdeaAgent
from backend.app.domain.ai.agents.milestone import MilestoneAgent
from backend.app.domain.ai.agents.mvp import MVPAgent
from backend.app.domain.ai.agents.qa import QAJudgeAgent
from backend.app.domain.ai.agents.readme import ReadmeAgent
from backend.app.domain.ai.agents.risk import RiskAgent
from backend.app.domain.ai.agents.scope import ScopeAgent
from backend.app.domain.ai.agents.specification import SpecificationAgent
from backend.app.domain.ai.agents.task import TaskAgent
from backend.app.domain.ai.agents.technology import TechnologyAgent
from backend.app.domain.ai.agents.timeline import TimelineAgent
from backend.app.domain.ai.context.builder import ProjectContextBuilder
from backend.app.domain.ai.contracts.agents import (
    FeaturesAgentInput,
    IdeaAgentInput,
    MilestoneAgentInput,
    MVPAgentInput,
    ReadmeAgentInput,
    ReadmeCuratedContext,
    RiskAgentInput,
    ScopeAgentInput,
    SpecificationAgentInput,
    TaskAgentInput,
    TechnologyAgentInput,
    TimelineAgentInput,
)
from backend.app.domain.ai.contracts.qa import QAJudgeAgentInput
from backend.app.domain.blueprint.models import BlueprintQAStatus
from backend.app.infrastructure.ai.gateway import AIProviderGateway

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from backend.app.domain.ai.contracts.base import AgentExecutionProvenance
    from backend.app.domain.ai.orchestration.events import WorkflowEventPublisher
    from backend.app.domain.ai.orchestration.state import OrchestrationState


class WorkflowNodeRegistry:
    """Registry holding instantiated Unit 3 agents and defining their LangGraph node execution methods."""

    def __init__(
        self,
        gateway: AIProviderGateway | None = None,
        cancellation_checker: Callable[[OrchestrationState], Awaitable[bool]] | None = None,
        event_publisher: WorkflowEventPublisher | None = None,
        execution_persister: Callable[
            [AgentExecutionProvenance, OrchestrationState], Awaitable[None]
        ]
        | None = None,
    ) -> None:
        gw = gateway or AIProviderGateway()
        self._cancellation_checker = cancellation_checker
        self._event_publisher = event_publisher
        self._execution_persister = execution_persister

        self.idea_agent = IdeaAgent(gateway=gw)
        self.scope_agent = ScopeAgent(gateway=gw)
        self.technology_agent = TechnologyAgent(gateway=gw)
        self.features_agent = FeaturesAgent(gateway=gw)
        self.mvp_agent = MVPAgent(gateway=gw)
        self.specification_agent = SpecificationAgent(gateway=gw)
        self.timeline_agent = TimelineAgent(gateway=gw)
        self.risk_agent = RiskAgent(gateway=gw)
        self.task_agent = TaskAgent(gateway=gw)
        self.milestone_agent = MilestoneAgent(gateway=gw)
        self.readme_agent = ReadmeAgent(gateway=gw)
        self.qa_judge_agent = QAJudgeAgent(gateway=gw)

    async def _is_cancelled(self, state: OrchestrationState) -> bool:
        if (
            state.get("cancellation_requested", False)
            or state.get("workflow_status") == "CANCELLING"
        ):
            return True
        if self._cancellation_checker:
            with contextlib.suppress(Exception):
                if await self._cancellation_checker(state):
                    return True
        return False

    async def _emit_event(
        self,
        event_type: str,
        state: OrchestrationState,
        step: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        if self._event_publisher:
            with contextlib.suppress(Exception):
                from backend.app.domain.ai.orchestration.events import WorkflowEvent

                await self._event_publisher.publish(
                    WorkflowEvent(
                        event_type=event_type,
                        job_id=str(state.get("execution_id", "")),
                        project_id=str(state.get("project_id", "")),
                        generation_number=state.get("generation_number", 1),
                        step=step,
                        execution_id=state.get("execution_id"),
                        correlation_id=state.get("correlation_id"),
                        payload=payload or {},
                    )
                )

    async def _persist_provenance(
        self, provenance: AgentExecutionProvenance, state: OrchestrationState
    ) -> None:
        if self._execution_persister:
            with contextlib.suppress(Exception):
                await self._execution_persister(provenance, state)

    def _extract_regen_context(
        self, state: OrchestrationState, node_name: str
    ) -> tuple[str | None, int]:
        """Extract regeneration hint and attempt count if the current node is targeted."""
        is_targeted = state.get("regeneration_target") == node_name
        hint = state.get("qa_feedback_hint") if is_targeted else None
        attempt = state.get("regeneration_attempt", 0) if is_targeted else 0
        return hint, attempt

    # -------------------------------------------------------------------------
    # 1. Idea Node
    # -------------------------------------------------------------------------
    async def node_idea(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "idea")
        hint, attempt = self._extract_regen_context(state, "idea")
        base = state["project_context"]
        assess = state["assessment_context"]
        context = ProjectContextBuilder.build_idea_context(base, assess)

        agent_input = IdeaAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="idea_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            project_name=context.project_name,
            initial_problem=context.problem,
            initial_solution=context.proposed_solution,
            complexity_preference=context.complexity,
            student_skill_level=context.skill_level,
            assessment_readiness_tier=context.readiness_tier,
            assessment_recommendations=context.assessment_recommendations,
        )

        output, provenance = await self.idea_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "idea")

        return {
            "current_step": "idea",
            "workflow_status": "RUNNING",
            "agent_outputs": {"idea": output},
            "agent_execution_metadata": {"idea": provenance},
        }

    # -------------------------------------------------------------------------
    # 2. Scope Node
    # -------------------------------------------------------------------------
    async def node_scope(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "scope")
        hint, attempt = self._extract_regen_context(state, "scope")
        base = state["project_context"]
        assess = state["assessment_context"]
        context = ProjectContextBuilder.build_scope_context(base, assess)
        outputs = state.get("agent_outputs", {})

        agent_input = ScopeAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="scope_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            idea=outputs["idea"],
            assessment_gaps=context.identified_gaps,
        )

        output, provenance = await self.scope_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "scope")

        return {
            "current_step": "scope",
            "workflow_status": "RUNNING",
            "agent_outputs": {"scope": output},
            "agent_execution_metadata": {"scope": provenance},
        }

    # -------------------------------------------------------------------------
    # 3. Technology Node (Parallel Branch 1)
    # -------------------------------------------------------------------------
    async def node_technology(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "technology")
        hint, attempt = self._extract_regen_context(state, "technology")
        base = state["project_context"]
        assess = state["assessment_context"]
        context = ProjectContextBuilder.build_technology_context(base, assess)
        outputs = state.get("agent_outputs", {})

        agent_input = TechnologyAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="technology_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            idea=outputs["idea"],
            scope=outputs["scope"],
            student_skill_level=context.skill_level,
            preferred_technologies=context.preferred_technologies,
        )

        output, provenance = await self.technology_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "technology")

        return {
            "current_step": "technology",
            "workflow_status": "RUNNING",
            "agent_outputs": {"technology": output},
            "agent_execution_metadata": {"technology": provenance},
        }

    # -------------------------------------------------------------------------
    # 4. Features Node (Parallel Branch 2)
    # -------------------------------------------------------------------------
    async def node_features(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "features")
        hint, attempt = self._extract_regen_context(state, "features")
        outputs = state.get("agent_outputs", {})

        agent_input = FeaturesAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="features_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            idea=outputs["idea"],
            scope=outputs["scope"],
        )

        output, provenance = await self.features_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "features")

        return {
            "current_step": "features",
            "workflow_status": "RUNNING",
            "agent_outputs": {"features": output},
            "agent_execution_metadata": {"features": provenance},
        }

    # -------------------------------------------------------------------------
    # 5. MVP Node (Parallel Branch 3 - REASONING)
    # -------------------------------------------------------------------------
    async def node_mvp(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "mvp")
        hint, attempt = self._extract_regen_context(state, "mvp")
        outputs = state.get("agent_outputs", {})

        agent_input = MVPAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="mvp_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            idea=outputs["idea"],
            scope=outputs["scope"],
            research_evidence=[],
        )

        output, provenance = await self.mvp_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "mvp")

        return {
            "current_step": "mvp",
            "workflow_status": "RUNNING",
            "agent_outputs": {"mvp": output},
            "agent_execution_metadata": {"mvp": provenance},
        }

    # -------------------------------------------------------------------------
    # 6. Specification Node (Parallel Fan-in Junction)
    # -------------------------------------------------------------------------
    async def node_specification(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "specification")
        hint, attempt = self._extract_regen_context(state, "specification")
        outputs = state.get("agent_outputs", {})

        agent_input = SpecificationAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="specification_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            idea=outputs["idea"],
            scope=outputs["scope"],
            technology=outputs["technology"],
            features=outputs["features"],
            mvp=outputs["mvp"],
        )

        output, provenance = await self.specification_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "specification")

        return {
            "current_step": "specification",
            "workflow_status": "RUNNING",
            "agent_outputs": {"specification": output},
            "agent_execution_metadata": {"specification": provenance},
        }

    # -------------------------------------------------------------------------
    # 7. Timeline Node
    # -------------------------------------------------------------------------
    async def node_timeline(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "timeline")
        hint, attempt = self._extract_regen_context(state, "timeline")
        base = state["project_context"]
        assess = state["assessment_context"]
        context = ProjectContextBuilder.build_timeline_context(base, assess)
        outputs = state.get("agent_outputs", {})

        agent_input = TimelineAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="timeline_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            idea=outputs["idea"],
            specification=outputs["specification"],
            complexity=context.complexity,
            project_deadline_weeks=context.deadline_weeks,
        )

        output, provenance = await self.timeline_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "timeline")

        return {
            "current_step": "timeline",
            "workflow_status": "RUNNING",
            "agent_outputs": {"timeline": output},
            "agent_execution_metadata": {"timeline": provenance},
        }

    # -------------------------------------------------------------------------
    # 8. Risk Node
    # -------------------------------------------------------------------------
    async def node_risk(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "risk")
        hint, attempt = self._extract_regen_context(state, "risk")
        outputs = state.get("agent_outputs", {})

        agent_input = RiskAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="risk_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            technology=outputs["technology"],
            features=outputs["features"],
            specification=outputs["specification"],
            timeline=outputs["timeline"],
        )

        output, provenance = await self.risk_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "risk")

        return {
            "current_step": "risk",
            "workflow_status": "RUNNING",
            "agent_outputs": {"risk": output},
            "agent_execution_metadata": {"risk": provenance},
        }

    # -------------------------------------------------------------------------
    # 9. Task Node
    # -------------------------------------------------------------------------
    async def node_task(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "task")
        hint, attempt = self._extract_regen_context(state, "task")
        outputs = state.get("agent_outputs", {})

        agent_input = TaskAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="task_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            specification=outputs["specification"],
            technology=outputs["technology"],
            features=outputs["features"],
            timeline=outputs["timeline"],
            risks=outputs["risk"],
        )

        output, provenance = await self.task_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "task")

        return {
            "current_step": "task",
            "workflow_status": "RUNNING",
            "agent_outputs": {"task": output},
            "agent_execution_metadata": {"task": provenance},
        }

    # -------------------------------------------------------------------------
    # 10. Milestone Node
    # -------------------------------------------------------------------------
    async def node_milestone(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "milestone")
        hint, attempt = self._extract_regen_context(state, "milestone")
        outputs = state.get("agent_outputs", {})

        agent_input = MilestoneAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="milestone_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            timeline=outputs["timeline"],
            tasks=outputs["task"],
        )

        output, provenance = await self.milestone_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "milestone")

        return {
            "current_step": "milestone",
            "workflow_status": "RUNNING",
            "agent_outputs": {"milestone": output},
            "agent_execution_metadata": {"milestone": provenance},
        }

    # -------------------------------------------------------------------------
    # 11. Readme Node
    # -------------------------------------------------------------------------
    async def node_readme(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "readme")
        hint, attempt = self._extract_regen_context(state, "readme")
        outputs = state.get("agent_outputs", {})

        agent_input = ReadmeAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="readme_agent",
            regeneration_attempt=attempt,
            qa_feedback_hint=hint,
            curated_context=ReadmeCuratedContext(
                idea=outputs["idea"],
                scope=outputs["scope"],
                technology=outputs["technology"],
                features=outputs["features"],
                mvp=outputs["mvp"],
                timeline=outputs["timeline"],
                risks=outputs["risk"],
                tasks=outputs["task"],
                milestones=outputs["milestone"],
            ),
        )

        output, provenance = await self.readme_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)
        await self._emit_event("node.completed", state, "readme")

        return {
            "current_step": "readme",
            "workflow_status": "RUNNING",
            "agent_outputs": {"readme": output},
            "agent_execution_metadata": {"readme": provenance},
        }

    # -------------------------------------------------------------------------
    # 12. QA / Judge Node (REASONING)
    # -------------------------------------------------------------------------
    async def node_qa_judge(self, state: OrchestrationState) -> dict[str, Any]:
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._emit_event("node.started", state, "qa_judge")
        base = state["project_context"]
        assess = state["assessment_context"]
        outputs = state.get("agent_outputs", {})

        agent_input = QAJudgeAgentInput(
            execution_id=state["execution_id"],
            project_id=uuid.UUID(str(state["project_id"])),
            student_id=uuid.UUID(str(state["student_id"])),
            agent_name="qa_judge_agent",
            regeneration_attempt=state.get("regeneration_attempt", 0),
            qa_feedback_hint=state.get("qa_feedback_hint"),
            all_agent_outputs={
                "idea": outputs["idea"].model_dump()
                if hasattr(outputs["idea"], "model_dump")
                else outputs["idea"],
                "scope": outputs["scope"].model_dump()
                if hasattr(outputs["scope"], "model_dump")
                else outputs["scope"],
                "technology": outputs["technology"].model_dump()
                if hasattr(outputs["technology"], "model_dump")
                else outputs["technology"],
                "features": outputs["features"].model_dump()
                if hasattr(outputs["features"], "model_dump")
                else outputs["features"],
                "mvp": outputs["mvp"].model_dump()
                if hasattr(outputs["mvp"], "model_dump")
                else outputs["mvp"],
                "specification": outputs["specification"].model_dump()
                if hasattr(outputs["specification"], "model_dump")
                else outputs["specification"],
                "timeline": outputs["timeline"].model_dump()
                if hasattr(outputs["timeline"], "model_dump")
                else outputs["timeline"],
                "risks": outputs["risk"].model_dump()
                if hasattr(outputs["risk"], "model_dump")
                else outputs["risk"],
                "tasks": outputs["task"].model_dump()
                if hasattr(outputs["task"], "model_dump")
                else outputs["task"],
                "milestones": outputs["milestone"].model_dump()
                if hasattr(outputs["milestone"], "model_dump")
                else outputs["milestone"],
                "readme": outputs["readme"].model_dump()
                if hasattr(outputs["readme"], "model_dump")
                else outputs["readme"],
            },
            project_context=base,
            assessment_context=assess,
        )

        output, provenance = await self.qa_judge_agent.execute(agent_input)
        if await self._is_cancelled(state):
            return {
                "workflow_status": "CANCELLING",
                "cancellation_requested": True,
                "current_step": "cancelled",
            }

        await self._persist_provenance(provenance, state)

        qa_status_enum = (
            BlueprintQAStatus.PASS if output.status.value == "PASS" else BlueprintQAStatus.FAIL
        )

        await self._emit_event(
            "qa.evaluated",
            state,
            "qa_judge",
            payload={
                "qa_score": output.overall_score,
                "qa_status": qa_status_enum.value,
                "findings_count": len(output.findings),
            },
        )

        return {
            "current_step": "qa_judge",
            "workflow_status": "RUNNING",
            "agent_outputs": {"qa_judge": output},
            "agent_execution_metadata": {"qa_judge": provenance},
            "qa_findings": output.findings,
            "qa_score": output.overall_score,
            "qa_status": qa_status_enum,
        }

    # -------------------------------------------------------------------------
    # 13. Regeneration Router Node (Emits regeneration.started lifecycle event)
    # -------------------------------------------------------------------------
    async def node_regeneration_router(self, state: OrchestrationState) -> dict[str, Any]:
        from backend.app.domain.ai.orchestration.router import (
            node_regeneration_router as pure_regeneration_router,
        )

        update = pure_regeneration_router(state)
        await self._emit_event(
            "regeneration.started",
            state,
            str(update.get("current_step", "regeneration_router")),
            payload={
                "regeneration_attempt": update.get("regeneration_attempt", 1),
                "regeneration_target": update.get("regeneration_target"),
                "qa_feedback_hint": update.get("qa_feedback_hint"),
            },
        )
        return update
