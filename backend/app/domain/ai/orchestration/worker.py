"""
GrowFlow — Unit 4 Blueprint Generation Background Worker.

Executes the compiled 12-agent LangGraph orchestration graph asynchronously,
decoupled from HTTP request lifecycles.

Responsibilities:
- Job claim and lease management to prevent duplicate execution across workers
- Authorized ProjectContext and AssessmentContext assembly
- Cooperative cancellation checkpoints before and after every agent execution
- Immediate provenance persistence into agent_executions table
- Real-time job progress tracking
- Bounded automatic regeneration handling (via LangGraph router)
- Atomic canonical commit ONLY after QA PASS (overall_score >= 75 and 0 CRITICAL)
- Failure preservation (preserving canonical blueprint content on error/rejection/cancellation)
- Lifecycle event emission for Unit 5 streaming and monitoring

Architecture ref:
  6F § 4 — Agent Dependency Graph & Topologies
  6F § 31-35 — QA & Targeted Regeneration
  6H § 12 — Background Jobs & Reliability
  Gate 09 — Unit 4 Frozen Specification
"""

from __future__ import annotations

from datetime import UTC, datetime
import traceback
from typing import TYPE_CHECKING, Any, cast
import uuid

from backend.app.domain.ai.context.builder import ProjectContextBuilder
from backend.app.domain.ai.orchestration.events import (
    NoOpEventPublisher,
    WorkflowEvent,
    WorkflowEventPublisher,
    WorkflowEventType,
)
from backend.app.domain.ai.orchestration.graph import build_blueprint_graph
from backend.app.domain.ai.orchestration.nodes import WorkflowNodeRegistry
from backend.app.domain.ai.orchestration.router import evaluate_qa_pass_condition
from backend.app.domain.blueprint.models import (
    BlueprintJobStatus,
    BlueprintQAStatus,
    BlueprintSectionKey,
    BlueprintStatus,
)
from backend.app.domain.identity.models import AccountStatus, CurrentUser, UserRole
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.repositories.agent_execution_repository import (
    AgentExecutionRepository,
)
from backend.app.infrastructure.repositories.assessment_repository import AssessmentRepository
from backend.app.infrastructure.repositories.blueprint_repository import BlueprintRepository
from backend.app.infrastructure.repositories.project_repository import ProjectRepository
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from backend.app.domain.ai.contracts.base import AgentExecutionProvenance
    from backend.app.domain.ai.orchestration.state import OrchestrationState
    from backend.app.infrastructure.database.models.blueprint import (
        BlueprintJobModel,
        BlueprintModel,
    )

logger = get_logger("growflow.ai.orchestration.worker")

STEP_PROGRESS_MAP: dict[str, int] = {
    "idea": 10,
    "scope": 20,
    "technology": 30,
    "features": 40,
    "mvp": 50,
    "specification": 60,
    "timeline": 70,
    "risk": 75,
    "task": 80,
    "milestone": 85,
    "readme": 90,
    "qa_judge": 95,
}


def assemble_canonical_content(agent_outputs: dict[str, Any]) -> dict[str, Any]:
    """
    Transforms outputs from the 12 concrete agents into the canonical 10-section
    blueprint dictionary format.
    """

    def dump_val(val: Any) -> Any:
        if val is None:
            return {}
        if hasattr(val, "model_dump"):
            return val.model_dump()
        if hasattr(val, "to_dict"):
            return val.to_dict()
        if isinstance(val, dict):
            return val
        return str(val)

    idea = dump_val(agent_outputs.get("idea"))
    scope = dump_val(agent_outputs.get("scope"))

    # Project Profile combines Idea and Scope outputs
    project_profile = {
        "idea": idea,
        "scope": scope,
    }

    return {
        BlueprintSectionKey.PROJECT_PROFILE.value: project_profile,
        BlueprintSectionKey.TECH_STACK.value: dump_val(agent_outputs.get("technology")),
        BlueprintSectionKey.FEATURES.value: dump_val(agent_outputs.get("features")),
        BlueprintSectionKey.SPECIFICATIONS.value: dump_val(agent_outputs.get("specification")),
        BlueprintSectionKey.MVP.value: dump_val(agent_outputs.get("mvp")),
        BlueprintSectionKey.DURATION.value: dump_val(agent_outputs.get("timeline")),
        BlueprintSectionKey.RISKS.value: dump_val(agent_outputs.get("risk")),
        BlueprintSectionKey.TASKS.value: dump_val(agent_outputs.get("task")),
        BlueprintSectionKey.MILESTONES.value: dump_val(agent_outputs.get("milestone")),
        BlueprintSectionKey.README.value: dump_val(agent_outputs.get("readme")),
    }


class BlueprintWorker:
    """
    Durable execution worker managing LangGraph workflow runs, database transactions,
    provenance recording, and canonical commits.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        ai_gateway: AIProviderGateway | None = None,
        event_publisher: WorkflowEventPublisher | None = None,
        worker_id: str | None = None,
        # Direct dependency overrides for unit test environments
        blueprint_repo: BlueprintRepository | None = None,
        project_repo: ProjectRepository | None = None,
        assessment_repo: AssessmentRepository | None = None,
        agent_execution_repo: AgentExecutionRepository | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._ai_gateway = ai_gateway or AIProviderGateway()
        self._event_publisher = event_publisher or NoOpEventPublisher()
        self._worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"

        self._direct_bp_repo = blueprint_repo
        self._direct_project_repo = project_repo
        self._direct_assessment_repo = assessment_repo
        self._direct_agent_execution_repo = agent_execution_repo

    async def run_generation_job(
        self,
        job_id: uuid.UUID | str,
        project_id: uuid.UUID | str,
        blueprint_id: uuid.UUID | str,
        worker_id: str | None = None,
    ) -> None:
        """
        Executes a persistent blueprint generation job from start to finish.
        Safe against server disconnects and concurrent workers.
        """
        w_id = worker_id or self._worker_id
        parsed_job_id = uuid.UUID(str(job_id))
        parsed_project_id = uuid.UUID(str(project_id))
        parsed_blueprint_id = uuid.UUID(str(blueprint_id))

        if self._session_factory is not None:
            async with self._session_factory() as session:
                bp_repo = BlueprintRepository(session)
                p_repo = ProjectRepository(session)
                a_repo = AssessmentRepository(session)
                exec_repo = AgentExecutionRepository(session)

                await self._execute_job(
                    session=session,
                    bp_repo=bp_repo,
                    project_repo=p_repo,
                    assessment_repo=a_repo,
                    exec_repo=exec_repo,
                    job_id=parsed_job_id,
                    project_id=parsed_project_id,
                    blueprint_id=parsed_blueprint_id,
                    worker_id=w_id,
                )
        else:
            # Test / mock mode with directly injected repositories
            if not (
                self._direct_bp_repo
                and self._direct_project_repo
                and self._direct_assessment_repo
                and self._direct_agent_execution_repo
            ):
                raise RuntimeError(
                    "BlueprintWorker requires session_factory or direct repositories."
                )

            await self._execute_job(
                session=None,
                bp_repo=self._direct_bp_repo,
                project_repo=self._direct_project_repo,
                assessment_repo=self._direct_assessment_repo,
                exec_repo=self._direct_agent_execution_repo,
                job_id=parsed_job_id,
                project_id=parsed_project_id,
                blueprint_id=parsed_blueprint_id,
                worker_id=w_id,
            )

    async def _execute_job(
        self,
        session: AsyncSession | None,
        bp_repo: BlueprintRepository,
        project_repo: ProjectRepository,
        assessment_repo: AssessmentRepository,
        exec_repo: AgentExecutionRepository,
        job_id: uuid.UUID,
        project_id: uuid.UUID,
        blueprint_id: uuid.UUID,
        worker_id: str,
    ) -> None:
        # 1. Claim lease
        claimed = await bp_repo.claim_job_lease(job_id, worker_id)
        if session:
            await session.commit()

        if not claimed:
            logger.warning(
                "Blueprint job already leased or not executable",
                job_id=str(job_id),
                worker_id=worker_id,
            )
            return

        # 2. Reload entities
        job = await bp_repo.get_job_by_id(job_id)
        project = await project_repo.get_by_id(project_id)
        blueprint = await bp_repo.get_by_id(blueprint_id)

        if not job or not project or not blueprint:
            logger.error(
                "BlueprintWorker missing required entities",
                job_id=str(job_id),
                project_id=str(project_id),
                blueprint_id=str(blueprint_id),
            )
            return

        # 3. Check for cancellation before starting
        if job.cancellation_requested or job.status == "CANCELLING":
            await self._handle_cancellation(session, bp_repo, job, blueprint, project_id)
            return

        # 4. Assemble authorized context
        student_user = CurrentUser(
            user_id=uuid.UUID(str(project.student_id)),
            email=f"{project.student_id}@student.growflow",
            role=UserRole.STUDENT,
            status=AccountStatus.ACTIVE,
        )
        context_builder = ProjectContextBuilder(project_repo, assessment_repo)
        base_context, assessment_context = await context_builder.build_base_contexts(
            project_id, student_user
        )

        gen_number = job.generation_number or blueprint.generation_number or 1

        # 5. Initialize OrchestrationState
        initial_state: OrchestrationState = {
            "project_id": uuid.UUID(str(project_id)),
            "student_id": uuid.UUID(str(project.student_id)),
            "generation_number": gen_number,
            "execution_id": str(job.id),
            "correlation_id": str(job.id),
            "project_context": base_context,
            "assessment_context": assessment_context,
            "current_step": "idea",
            "workflow_status": "RUNNING",
            "cancellation_requested": False,
            "agent_outputs": {},
            "agent_execution_metadata": {},
            "qa_findings": [],
            "qa_score": 0,
            "qa_status": BlueprintQAStatus.PENDING,
            "regeneration_attempt": 0,
            "regeneration_target": None,
            "qa_feedback_hint": None,
            "started_at": datetime.now(UTC),
            "completed_at": None,
        }

        # 6. Publish job.started event
        await self._event_publisher.publish(
            WorkflowEvent(
                event_type=WorkflowEventType.JOB_STARTED.value,
                job_id=str(job.id),
                project_id=str(project_id),
                generation_number=gen_number,
                step="idea",
                progress_percent=5,
                execution_id=str(job.id),
                correlation_id=str(job.id),
            )
        )

        # 7. Setup Node Registry with cancellation checks & provenance persistence
        async def check_cancellation_callback(state: OrchestrationState) -> bool:
            return await bp_repo.is_cancellation_requested(job_id)

        async def persist_provenance_callback(
            prov: AgentExecutionProvenance, state: OrchestrationState
        ) -> None:
            try:
                await exec_repo.record_execution(
                    provenance=prov,
                    blueprint_job_id=str(job_id),
                    blueprint_id=str(blueprint_id),
                    project_instance_id=str(project_id),
                )
                if session:
                    await session.commit()
            except Exception as pe:
                logger.error("Failed to persist agent execution provenance", error=str(pe))

        node_registry = WorkflowNodeRegistry(
            gateway=self._ai_gateway,
            cancellation_checker=check_cancellation_callback,
            event_publisher=self._event_publisher,
            execution_persister=persist_provenance_callback,
        )

        # 8. Build graph and execute
        graph = build_blueprint_graph(node_registry)

        try:
            final_state = await graph.ainvoke(initial_state)

            # 9. Handle cooperative cancellation
            if (
                final_state.get("cancellation_requested", False)
                or final_state.get("workflow_status") == "CANCELLING"
                or await bp_repo.is_cancellation_requested(job_id)
            ):
                await self._handle_cancellation(session, bp_repo, job, blueprint, project_id)
                return

            # 10. Evaluate QA
            qa_passed = evaluate_qa_pass_condition(cast("OrchestrationState", final_state))
            agent_outputs = final_state.get("agent_outputs", {})
            qa_score = final_state.get("qa_score", 0)
            qa_findings = final_state.get("qa_findings", [])

            qa_feedback = {
                "status": BlueprintQAStatus.PASS.value
                if qa_passed
                else BlueprintQAStatus.FAIL.value,
                "score": qa_score,
                "summary": "Blueprint QA evaluation complete.",
                "issues": [
                    {
                        "section": getattr(f, "section", "")
                        or (f.get("section", "") if isinstance(f, dict) else ""),
                        "severity": getattr(f, "severity", "")
                        or (f.get("severity", "") if isinstance(f, dict) else ""),
                        "description": getattr(f, "description", "")
                        or (f.get("description", "") if isinstance(f, dict) else ""),
                        "recommendation": getattr(f, "recommendation", "")
                        or (f.get("recommendation", "") if isinstance(f, dict) else ""),
                    }
                    for f in qa_findings
                ],
            }

            if qa_passed:
                # 11. Atomic canonical commit ONLY after QA PASS
                canonical_content = assemble_canonical_content(agent_outputs)
                committed = await bp_repo.commit_canonical_blueprint(
                    blueprint_id=blueprint_id,
                    job_id=job_id,
                    expected_generation_number=gen_number,
                    content=canonical_content,
                    qa_score=qa_score,
                    qa_feedback=qa_feedback,
                )

                if committed:
                    if session:
                        await session.commit()

                    await self._event_publisher.publish(
                        WorkflowEvent(
                            event_type=WorkflowEventType.JOB_COMPLETED.value,
                            job_id=str(job.id),
                            project_id=str(project_id),
                            generation_number=gen_number,
                            step="completed",
                            progress_percent=100,
                            execution_id=str(job.id),
                            correlation_id=str(job.id),
                            payload={"qa_score": qa_score},
                        )
                    )
                    logger.info(
                        "Blueprint generation completed and committed canonically",
                        job_id=str(job.id),
                        generation_number=gen_number,
                        qa_score=qa_score,
                    )
                else:
                    logger.warning(
                        "Canonical blueprint commit rejected (preconditions failed or cancelled)",
                        job_id=str(job.id),
                    )
                    await self._handle_cancellation(session, bp_repo, job, blueprint, project_id)
            else:
                # 12. QA Rejection after exhausted regeneration attempts
                logger.warning(
                    "Blueprint generation rejected by QA Judge; preserving previous canonical content",
                    job_id=str(job.id),
                    generation_number=gen_number,
                    qa_score=qa_score,
                    regen_attempts=final_state.get("regeneration_attempt", 0),
                )
                await bp_repo.complete_job(
                    job,
                    BlueprintJobStatus.FAILED,
                    error=f"QA validation failed after {final_state.get('regeneration_attempt', 0)} automatic regeneration attempts. Score: {qa_score}",
                )
                await bp_repo.record_qa_result(
                    blueprint=blueprint,
                    qa_status=BlueprintQAStatus.FAIL,
                    qa_score=qa_score,
                    qa_feedback=qa_feedback,
                )
                await bp_repo.update_status(
                    blueprint=blueprint,
                    status=BlueprintStatus.QA_REJECTED,
                    error_message=f"Blueprint rejected by QA Judge (Score: {qa_score})",
                    failed_output_key="qa_judge",
                )
                if session:
                    await session.commit()

                await self._event_publisher.publish(
                    WorkflowEvent(
                        event_type=WorkflowEventType.JOB_FAILED.value,
                        job_id=str(job.id),
                        project_id=str(project_id),
                        generation_number=gen_number,
                        step="qa_judge",
                        execution_id=str(job.id),
                        correlation_id=str(job.id),
                        payload={"qa_score": qa_score, "reason": "QA_REJECTED"},
                    )
                )

        except Exception as exc:
            # 13. Failure preservation on runtime exception
            logger.error(
                "Blueprint execution worker exception; preserving canonical content",
                job_id=str(job.id),
                error=str(exc),
                traceback=traceback.format_exc(),
            )
            await bp_repo.complete_job(
                job,
                BlueprintJobStatus.FAILED,
                error=str(exc),
            )
            # Revert blueprint state while strictly preserving previous canonical content
            await bp_repo.update_status(
                blueprint=blueprint,
                status=BlueprintStatus.FAILED,
                error_message=f"Workflow failed: {exc}",
            )
            if session:
                await session.commit()

            await self._event_publisher.publish(
                WorkflowEvent(
                    event_type=WorkflowEventType.JOB_FAILED.value,
                    job_id=str(job.id),
                    project_id=str(project_id),
                    generation_number=gen_number,
                    step="failed",
                    execution_id=str(job.id),
                    correlation_id=str(job.id),
                    payload={"error": str(exc)},
                )
            )

    async def _handle_cancellation(
        self,
        session: AsyncSession | None,
        bp_repo: BlueprintRepository,
        job: BlueprintJobModel,
        blueprint: BlueprintModel,
        project_id: uuid.UUID,
    ) -> None:
        """Handles graceful cancellation, discarding transient state and preserving canonical content."""
        await bp_repo.complete_job(job, BlueprintJobStatus.CANCELLED)
        job.cancellation_requested = True

        # Restore blueprint status based on whether previous content existed
        has_content = bool(blueprint.content)
        new_status = BlueprintStatus.GENERATED if has_content else BlueprintStatus.FAILED
        await bp_repo.update_status(
            blueprint=blueprint,
            status=new_status,
            error_message="Generation cancelled by student." if not has_content else None,
        )

        if session:
            await session.commit()

        await self._event_publisher.publish(
            WorkflowEvent(
                event_type=WorkflowEventType.JOB_CANCELLED.value,
                job_id=str(job.id),
                project_id=str(project_id),
                generation_number=job.generation_number or 1,
                step="cancelled",
                execution_id=str(job.id),
                correlation_id=str(job.id),
            )
        )
        logger.info("Blueprint generation cancelled successfully", job_id=str(job.id))
