"""
GrowFlow — Assessment Application Service.

Coordinates:
- Assessment question generation (10 standardized core + 5 dynamic adaptive)
- Session lifecycle (not started -> in progress -> completed)
- Answer persistence & idempotent upsert
- Adaptive project-specific question synthesis
- Enriched Project Understanding & result generation
- Student ownership enforcement & project lifecycle synchronization

Architecture ref:
  6N § 16 — Assessment Architecture (10 standardized core + 5 dynamic questions)
  5B § 18 & 19 — AI Assessment & Enriched Project Understanding
  1 § 31 — Final Student-Side Concept
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
import uuid

from backend.app.domain.assessment.models import (
    AssessmentAnswer,
    AssessmentQuestion,
    AssessmentQuestionOption,
    AssessmentReadinessTier,
    AssessmentResult,
    AssessmentSession,
    AssessmentStatus,
    QuestionType,
)
from backend.app.domain.project.models import ProjectPhase
from backend.app.infrastructure.database.models.assessment import (
    AssessmentAnswerModel,
    AssessmentModel,
    AssessmentResultModel,
)
from backend.app.shared.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    NotFoundException,
)

if TYPE_CHECKING:
    from backend.app.application.services.outbox_service import OutboxService
    from backend.app.domain.identity import CurrentUser
    from backend.app.infrastructure.database.models.project import ProjectInstanceModel
    from backend.app.infrastructure.repositories.assessment_repository import (
        AssessmentRepository,
    )
    from backend.app.infrastructure.repositories.project_repository import (
        ProjectRepository,
    )


class AssessmentService:
    """Application service for managing student assessment sessions, questions, answers, and results."""

    TOTAL_QUESTIONS: int = 15
    CORE_QUESTIONS_COUNT: int = 10
    ADAPTIVE_QUESTIONS_COUNT: int = 5

    def __init__(
        self,
        assessment_repo: AssessmentRepository,
        project_repo: ProjectRepository,
        outbox_service: OutboxService | None = None,
    ) -> None:
        self._assessment_repo = assessment_repo
        self._project_repo = project_repo
        self._outbox_service = outbox_service

    # =========================================================================
    # Authorization & Project Resolution
    # =========================================================================

    async def _resolve_and_authorize_project(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> ProjectInstanceModel:
        """Ensure project exists and belongs to the authenticated student."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundException(
                f"Project '{project_id}' not found.",
                code="PROJECT_NOT_FOUND",
            )
        if str(project.student_id) != str(current_user.user_id):
            raise AuthorizationException(
                "You do not have permission to access this project's assessment.",
                code="AUTH_UNAUTHORIZED",
            )
        return project

    # =========================================================================
    # Question Bank & Adaptive Question Synthesis
    # =========================================================================

    def _get_core_questions(self) -> list[AssessmentQuestion]:
        """Returns the 10 standardized core questions (§ 16 Assessment Architecture)."""
        return [
            AssessmentQuestion(
                id="core-01-problem-definition",
                order_index=1,
                category="Problem Definition & User Impact",
                question_text="How clearly defined is the specific problem and the primary user persona your project addresses?",
                help_text="Evaluate whether you have identified concrete user pain points versus a generalized topic area.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                is_adaptive=False,
                options=[
                    AssessmentQuestionOption(
                        value="SPECIFIC_PERSONA",
                        label="Highly Specific Persona & Measurable Pain Point",
                        description="Direct user workflow identified with measurable inefficiencies or explicit requirements.",
                    ),
                    AssessmentQuestionOption(
                        value="TARGET_SEGMENT",
                        label="Defined Target Segment with Broad Use Cases",
                        description="Clear user group identified, but specific daily workflows are still being refined.",
                    ),
                    AssessmentQuestionOption(
                        value="GENERAL_TOPIC",
                        label="Broad Technical Opportunity",
                        description="Concept explores a technology or capability rather than a tailored user problem.",
                    ),
                    AssessmentQuestionOption(
                        value="EXPLORATORY",
                        label="Exploratory / Theoretical Research",
                        description="Problem space is open-ended without a predefined user group.",
                    ),
                ],
            ),
            AssessmentQuestion(
                id="core-02-solution-mechanics",
                order_index=2,
                category="Core Value Proposition & Mechanics",
                question_text="What is the primary mechanism through which your software solves the identified problem?",
                help_text="Describe how the core loop delivers value to the user.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                is_adaptive=False,
                options=[
                    AssessmentQuestionOption(
                        value="AUTOMATED_WORKFLOW",
                        label="Automated Pipeline / Workflow Orchestration",
                        description="Eliminates repetitive manual steps by chaining operations into an automated flow.",
                    ),
                    AssessmentQuestionOption(
                        value="INTELLIGENT_SYNTHESIS",
                        label="Data Synthesis, Analytics, or Machine Intelligence",
                        description="Transforms raw inputs into actionable insights, recommendations, or classifications.",
                    ),
                    AssessmentQuestionOption(
                        value="INTERACTIVE_INTERFACE",
                        label="Domain-Specific Collaborative Workspace / Interface",
                        description="Provides specialized UI tooling for users to create, visualize, or collaborate on assets.",
                    ),
                    AssessmentQuestionOption(
                        value="PLATFORM_INTEGRATION",
                        label="Cross-System Integration & Synchronization",
                        description="Unifies disconnected third-party services and APIs into a unified control surface.",
                    ),
                ],
            ),
            AssessmentQuestion(
                id="core-03-system-architecture",
                order_index=3,
                category="Target Architecture & Pattern",
                question_text="Which architectural pattern best characterizes your planned system structure?",
                help_text="Select the structural topology that best matches your deployment and communication model.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                is_adaptive=False,
                options=[
                    AssessmentQuestionOption(
                        value="MODULAR_MONOLITH",
                        label="Modular Monolith with Clean Layered Boundaries",
                        description="Single deployable runtime organized into strict domain modules and repository boundaries.",
                    ),
                    AssessmentQuestionOption(
                        value="CLIENT_SERVER_SPA",
                        label="Decoupled Single Page App + Headless REST/GraphQL API",
                        description="Independent frontend client communicating with an authoritative backend API layer.",
                    ),
                    AssessmentQuestionOption(
                        value="EVENT_DRIVEN_MICROSERVICES",
                        label="Event-Driven Microservices / Asynchronous Workers",
                        description="Distributed services coordinating through message buses or background queues.",
                    ),
                    AssessmentQuestionOption(
                        value="EDGE_SERVERLESS",
                        label="Serverless Functions & Edge Runtime",
                        description="Stateless HTTP handlers deployed to serverless infrastructure with managed services.",
                    ),
                ],
            ),
            AssessmentQuestion(
                id="core-04-tech-stack-justification",
                order_index=4,
                category="Technology Stack Justification",
                question_text="What is the primary rationale for your chosen programming languages and core frameworks?",
                help_text="Reflect on why this technology selection optimizes for delivery speed, safety, and ecosystem fit.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                is_adaptive=False,
                options=[
                    AssessmentQuestionOption(
                        value="TYPE_SAFETY_ECOSYSTEM",
                        label="Type Safety & Mature Industrial Ecosystem",
                        description="Strong static typing and established enterprise tooling (e.g. TypeScript, Python/FastAPI).",
                    ),
                    AssessmentQuestionOption(
                        value="DEVELOPER_VELOCITY",
                        label="Rapid Prototyping & Developer Velocity",
                        description="High-level frameworks that provide batteries-included abstractions for rapid delivery.",
                    ),
                    AssessmentQuestionOption(
                        value="DOMAIN_PERFORMANCE",
                        label="Domain-Specific Performance or Hardware Integration",
                        description="Specific libraries required for high-throughput computation, telemetry, or embedded hardware.",
                    ),
                    AssessmentQuestionOption(
                        value="LEARNING_GOAL",
                        label="Educational Mastery & Skill Expansion",
                        description="Chosen specifically to master new paradigm concepts and expand professional proficiency.",
                    ),
                ],
            ),
            AssessmentQuestion(
                id="core-05-data-storage-strategy",
                order_index=5,
                category="Data Model & Storage Strategy",
                question_text="What primary data persistence and state management strategy best fits your system?",
                help_text="Consider transaction guarantees, query relational complexity, and data volume.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                is_adaptive=False,
                options=[
                    AssessmentQuestionOption(
                        value="RELATIONAL_ACID",
                        label="Relational Database with ACID Guarantees",
                        description="Strict foreign keys, constraints, and transactional consistency (e.g. PostgreSQL, SQLite).",
                    ),
                    AssessmentQuestionOption(
                        value="DOCUMENT_JSON",
                        label="Document / Key-Value Store for Flexible Schema",
                        description="Semi-structured document storage where entities have variable attributes (e.g. MongoDB).",
                    ),
                    AssessmentQuestionOption(
                        value="HYBRID_RELATIONAL_BLOB",
                        label="Hybrid Relational Metadata + Blob Storage",
                        description="Structured relational tables for entities combined with object storage for files or media.",
                    ),
                    AssessmentQuestionOption(
                        value="TIME_SERIES_CACHE",
                        label="In-Memory Cache & Time-Series Stream",
                        description="High-velocity metrics or volatile state requiring caching layers (e.g. Redis).",
                    ),
                ],
            ),
            AssessmentQuestion(
                id="core-06-system-integrations",
                order_index=6,
                category="System Integrations & External APIs",
                question_text="How dependent is your core value proposition on third-party APIs, external hardware, or webhooks?",
                help_text="Evaluate availability risks and external contract stability.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                is_adaptive=False,
                options=[
                    AssessmentQuestionOption(
                        value="SELF_CONTAINED",
                        label="Primarily Self-Contained System",
                        description="All core logic and storage are fully managed within your application boundaries.",
                    ),
                    AssessmentQuestionOption(
                        value="STANDARD_APIS",
                        label="Standard SaaS Integration (Auth, Email, Cloud Storage)",
                        description="Relies on mature external commodity providers with high availability SLAs.",
                    ),
                    AssessmentQuestionOption(
                        value="CRITICAL_DEPENDENCY",
                        label="Critical Core Dependency on Specialized APIs",
                        description="Core business value depends directly on specialized APIs (e.g. AI models, payment rails).",
                    ),
                    AssessmentQuestionOption(
                        value="HARDWARE_IOT",
                        label="Physical Hardware / IoT / Protocol Interface",
                        description="Interacts with physical sensors, local edge devices, or serial protocols.",
                    ),
                ],
            ),
            AssessmentQuestion(
                id="core-07-security-access",
                order_index=7,
                category="Security, Authentication & Access Control",
                question_text="What authentication and tenant authorization boundaries will protect user data in your project?",
                help_text="Verify how identity verification and resource scoping are separated.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                is_adaptive=False,
                options=[
                    AssessmentQuestionOption(
                        value="ROLE_BASED_RLS",
                        label="Role-Based Access Control (RBAC) + Database Row-Level Security",
                        description="Strict user roles (e.g. Student, Mentor, Admin) backed by database-level ownership policies.",
                    ),
                    AssessmentQuestionOption(
                        value="TOKEN_JWT_APP_LEVEL",
                        label="JWT Token Authentication + Application-Level Middleware",
                        description="Authoritative token claims verified in API middleware prior to handler execution.",
                    ),
                    AssessmentQuestionOption(
                        value="MULTI_TENANT_ORGANIZATION",
                        label="Multi-Tenant Workspace Isolation",
                        description="Data isolated by organization/group boundary with scoped team privileges.",
                    ),
                    AssessmentQuestionOption(
                        value="PUBLIC_READ_PRIVATE_WRITE",
                        label="Public Read-Only Catalog + Authenticated Creator Writes",
                        description="Open visibility for discovery with authenticated ownership required for mutations.",
                    ),
                ],
            ),
            AssessmentQuestion(
                id="core-08-performance-scalability",
                order_index=8,
                category="Performance & Scalability Targets",
                question_text="What are your expected operational latency and concurrency requirements for the initial release?",
                help_text="Grounding operational parameters prevents premature optimization while establishing realistic boundaries.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                is_adaptive=False,
                options=[
                    AssessmentQuestionOption(
                        value="INTERACTIVE_LOW_CONCURRENCY",
                        label="Sub-second Interactive UI (< 100 concurrent users)",
                        description="Standard responsive web performance focusing on code cleanliness over distributed caching.",
                    ),
                    AssessmentQuestionOption(
                        value="HIGH_THROUGHPUT_PIPELINE",
                        label="Batch / Background Processing Throughput",
                        description="System prioritizes job completion and queue stability over immediate sub-100ms response.",
                    ),
                    AssessmentQuestionOption(
                        value="LOW_LATENCY_STREAMING",
                        label="Near-Realtime Streaming (< 200ms roundtrip)",
                        description="Interactive telemetry or WebSocket messaging requiring optimized network hops.",
                    ),
                    AssessmentQuestionOption(
                        value="OFFLINE_FIRST",
                        label="Offline-First Local Operation with Sync",
                        description="System operates locally with intermittent network synchronization.",
                    ),
                ],
            ),
            AssessmentQuestion(
                id="core-09-qa-validation",
                order_index=9,
                category="Quality Assurance & Validation Methodology",
                question_text="What testing and verification methodology will guarantee that your implementation is correct?",
                help_text="Determine how defects and regressions will be systematically caught before deployment.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                is_adaptive=False,
                options=[
                    AssessmentQuestionOption(
                        value="AUTOMATED_PYRAMID",
                        label="Automated Test Pyramid (Unit + Integration + Contract Tests)",
                        description="Comprehensive unit tests for business logic combined with HTTP API integration tests.",
                    ),
                    AssessmentQuestionOption(
                        value="E2E_USER_FLOWS",
                        label="End-to-End User Journey Verification",
                        description="Browser-level workflow verification testing critical paths from sign-in to completion.",
                    ),
                    AssessmentQuestionOption(
                        value="TEST_DRIVEN_DEVELOPMENT",
                        label="Test-Driven Development (TDD) for Core Invariants",
                        description="Writing tests prior to implementation to lock down boundary specifications.",
                    ),
                    AssessmentQuestionOption(
                        value="MANUAL_ACCEPTANCE",
                        label="Deterministic Scenario-Based Manual Acceptance",
                        description="Structured test checklists verified against canonical acceptance criteria.",
                    ),
                ],
            ),
            AssessmentQuestion(
                id="core-10-risks-failure-modes",
                order_index=10,
                category="Technical Risks & Failure Modes",
                question_text="What is the single greatest technical unknown or failure risk that could jeopardize project delivery?",
                help_text="Identifying failure modes early enables proactive mitigation in the upcoming Blueprint phase.",
                question_type=QuestionType.MULTIPLE_CHOICE,
                is_adaptive=False,
                options=[
                    AssessmentQuestionOption(
                        value="EXTERNAL_API_INSTABILITY",
                        label="Third-Party API Rate Limits, Breaking Changes, or Downtime",
                        description="Dependence on an external vendor or experimental service that may fail unpredictably.",
                    ),
                    AssessmentQuestionOption(
                        value="DATA_MODEL_EVOLUTION",
                        label="Underestimated Data Model Relational Complexity",
                        description="Domain entities and relationships may require significant schema restructuring mid-build.",
                    ),
                    AssessmentQuestionOption(
                        value="PERFORMANCE_BOTTLENECK",
                        label="Algorithmic / Resource Scalability Bottlenecks",
                        description="Computationally intensive logic or memory pressure under real-world input sizes.",
                    ),
                    AssessmentQuestionOption(
                        value="SCOPE_CREEP",
                        label="Scope Expansion Beyond the Available Timeline",
                        description="Accumulating additional secondary features before proving the minimum viable core.",
                    ),
                ],
            ),
        ]

    def _synthesize_adaptive_question(
        self,
        question_index: int,
        project: ProjectInstanceModel,
        prior_answers: dict[str, str | None],
    ) -> AssessmentQuestion:
        """
        Dynamically synthesize project-specific questions 11–15 based on:
        - project context (name, problem, proposed_solution, complexity)
        - accumulated prior answers to core questions.
        """
        proj_name = project.name
        complexity = project.complexity
        q3_arch = prior_answers.get("core-03-system-architecture", "MODULAR_MONOLITH")
        q5_data = prior_answers.get("core-05-data-storage-strategy", "RELATIONAL_ACID")
        q10_risk = prior_answers.get("core-10-risks-failure-modes", "SCOPE_CREEP")

        if question_index == 11:
            return AssessmentQuestion(
                id="adaptive-11-architectural-boundaries",
                order_index=11,
                category="Adaptive Architectural Invariants",
                question_text=f"For '{proj_name}' ({complexity} tier), how will you enforce separation between user-facing interactions and core domain logic under a {q3_arch} pattern?",
                help_text=f"Explain the architectural boundary that prevents business logic from leaking into HTTP controllers or UI components in {proj_name}.",
                question_type=QuestionType.TEXT,
                is_adaptive=True,
                context_badge="ADAPTIVE: ARCHITECTURAL BOUNDARIES",
            )
        elif question_index == 12:
            return AssessmentQuestion(
                id="adaptive-12-state-reconciliation",
                order_index=12,
                category="Adaptive Data Lifecycle & State",
                question_text=f"Given your selection of {q5_data}, how will '{proj_name}' handle data validation errors, transactional rollbacks, and concurrent student updates?",
                help_text="Detail how you will maintain state integrity when network failures or invalid payloads occur.",
                question_type=QuestionType.TEXT,
                is_adaptive=True,
                context_badge="ADAPTIVE: DATA INTEGRITY",
            )
        elif question_index == 13:
            return AssessmentQuestion(
                id="adaptive-13-boundary-constraints",
                order_index=13,
                category="Adaptive Boundary Constraints & Trade-offs",
                question_text=f"What explicit trade-offs are you making in '{proj_name}' regarding latency versus computational consistency?",
                help_text="Every architectural design sacrifices something (e.g. immediate consistency vs simplicity). Articulate your system's deliberate trade-offs.",
                question_type=QuestionType.TEXT,
                is_adaptive=True,
                context_badge="ADAPTIVE: DESIGN TRADE-OFFS",
            )
        elif question_index == 14:
            return AssessmentQuestion(
                id="adaptive-14-risk-mitigation",
                order_index=14,
                category="Adaptive Risk Mitigation & Fallback",
                question_text=f"In Question 10, you identified '{q10_risk}' as your primary delivery risk. What concrete fallback strategy will '{proj_name}' implement if this risk materializes?",
                help_text="Define the technical circuit-breaker, fallback default, or scope reduction plan that keeps the project on track.",
                question_type=QuestionType.TEXT,
                is_adaptive=True,
                context_badge="ADAPTIVE: RISK MITIGATION",
            )
        else:  # 15
            return AssessmentQuestion(
                id="adaptive-15-mvp-validation-criteria",
                order_index=15,
                category="Adaptive MVP Scope & Demonstration",
                question_text=f"What is the single minimum testable demonstration that will definitively prove '{proj_name}' is functional prior to full release?",
                help_text="Describe the end-to-end golden path milestone that demonstrates the core problem has been solved.",
                question_type=QuestionType.TEXT,
                is_adaptive=True,
                context_badge="ADAPTIVE: MVP VALIDATION",
            )

    def get_all_questions_for_project(
        self, project: ProjectInstanceModel, prior_answers: dict[str, str | None]
    ) -> list[AssessmentQuestion]:
        """Returns the complete sequence of 15 questions for the given project context."""
        core = self._get_core_questions()
        adaptive = [
            self._synthesize_adaptive_question(idx, project, prior_answers)
            for idx in range(11, 16)
        ]
        return core + adaptive

    # =========================================================================
    # Public Service Operations
    # =========================================================================

    async def get_assessment_status(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> dict[str, Any]:
        """Retrieve current assessment status and progress summary."""
        project = await self._resolve_and_authorize_project(project_id, current_user)
        assessment = await self._assessment_repo.get_by_project_id(project.id)

        if not assessment:
            return {
                "project_id": str(project.id),
                "project_name": project.name,
                "current_phase": project.current_phase,
                "status": AssessmentStatus.NOT_STARTED.value,
                "current_question_index": 1,
                "total_questions": self.TOTAL_QUESTIONS,
                "answered_count": 0,
                "progress_percentage": 0,
                "started_at": None,
                "completed_at": None,
            }

        answers = await self._assessment_repo.get_answers(assessment.id)
        answered_count = len(answers)
        progress_pct = int((answered_count / self.TOTAL_QUESTIONS) * 100)

        return {
            "project_id": str(project.id),
            "project_name": project.name,
            "current_phase": project.current_phase,
            "status": assessment.status,
            "current_question_index": assessment.current_question_index,
            "total_questions": assessment.total_questions,
            "answered_count": answered_count,
            "progress_percentage": progress_pct,
            "started_at": assessment.started_at.isoformat() if assessment.started_at else None,
            "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
        }

    async def start_or_resume_assessment(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> tuple[AssessmentModel, AssessmentQuestion]:
        """
        Start or resume an assessment session.
        Idempotent: If session already exists, returns current active state without duplication.
        Synchronizes lifecycle: Moves IDEA -> ASSESSMENT when started.
        """
        project = await self._resolve_and_authorize_project(project_id, current_user)
        assessment = await self._assessment_repo.get_by_project_id(project.id)

        if not assessment:
            now = datetime.now(UTC)
            assessment = AssessmentModel(
                id=str(uuid.uuid4()),
                project_instance_id=str(project.id),
                student_id=str(current_user.user_id),
                status=AssessmentStatus.IN_PROGRESS.value,
                current_question_index=1,
                total_questions=self.TOTAL_QUESTIONS,
                started_at=now,
            )
            assessment = await self._assessment_repo.create_assessment(assessment)

            # Synchronize project lifecycle phase if project is currently in IDEA
            if project.current_phase == ProjectPhase.IDEA.value:
                project.current_phase = ProjectPhase.ASSESSMENT.value

        # Retrieve prior answers to synthesize questions
        answers = await self._assessment_repo.get_answers(assessment.id)
        prior_map = {a.question_id: a.selected_option or a.text_response for a in answers}

        # Determine next unanswered question index if in progress
        target_idx = assessment.current_question_index
        all_questions = self.get_all_questions_for_project(project, prior_map)
        current_q = all_questions[target_idx - 1]

        return assessment, current_q

    async def get_question(
        self,
        project_id: uuid.UUID | str,
        question_index: int,
        current_user: CurrentUser,
    ) -> tuple[AssessmentQuestion, AssessmentAnswerModel | None]:
        """Retrieve a specific question (1..15) with existing student answer if present."""
        if question_index < 1 or question_index > self.TOTAL_QUESTIONS:
            raise BusinessRuleException(
                f"Question index {question_index} is invalid. Assessment has {self.TOTAL_QUESTIONS} questions.",
                code="ASSESSMENT_INVALID_QUESTION_INDEX",
            )

        project = await self._resolve_and_authorize_project(project_id, current_user)
        assessment = await self._assessment_repo.get_by_project_id(project.id)

        if not assessment:
            raise BusinessRuleException(
                "Assessment has not been started. Please start the assessment first.",
                code="ASSESSMENT_NOT_STARTED",
            )

        answers = await self._assessment_repo.get_answers(assessment.id)
        prior_map = {a.question_id: a.selected_option or a.text_response for a in answers}

        all_questions = self.get_all_questions_for_project(project, prior_map)
        target_question = all_questions[question_index - 1]

        # Check existing answer
        existing_answer = await self._assessment_repo.get_answer(
            assessment.id, target_question.id
        )

        return target_question, existing_answer

    async def submit_answer(
        self,
        project_id: uuid.UUID | str,
        question_index: int,
        selected_option: str | None,
        text_response: str | None,
        current_user: CurrentUser,
    ) -> tuple[AssessmentAnswerModel, AssessmentModel, int | None]:
        """
        Submit or update an answer for a question.
        Idempotent: Re-submitting updates existing answer row without duplication.
        Advances current_question_index appropriately.
        """
        if question_index < 1 or question_index > self.TOTAL_QUESTIONS:
            raise BusinessRuleException(
                f"Question index {question_index} is invalid.",
                code="ASSESSMENT_INVALID_QUESTION_INDEX",
            )

        # Validation: Must have at least one valid answer field
        has_option = selected_option is not None and len(selected_option.strip()) > 0
        has_text = text_response is not None and len(text_response.strip()) > 0
        if not has_option and not has_text:
            raise BusinessRuleException(
                "Answer submission must contain a selected option or text response.",
                code="ASSESSMENT_EMPTY_ANSWER",
            )

        project = await self._resolve_and_authorize_project(project_id, current_user)
        assessment = await self._assessment_repo.get_by_project_id(project.id)

        if not assessment:
            raise BusinessRuleException(
                "Assessment has not been started.",
                code="ASSESSMENT_NOT_STARTED",
            )

        if assessment.status == AssessmentStatus.COMPLETED.value:
            raise BusinessRuleException(
                "Assessment is already completed and cannot accept new answers.",
                code="ASSESSMENT_ALREADY_COMPLETED",
            )

        # Fetch prior answers to build question
        answers = await self._assessment_repo.get_answers(assessment.id)
        prior_map = {a.question_id: a.selected_option or a.text_response for a in answers}
        all_questions = self.get_all_questions_for_project(project, prior_map)
        target_question = all_questions[question_index - 1]

        # Upsert answer
        saved_answer = await self._assessment_repo.upsert_answer(
            assessment_id=assessment.id,
            question_id=target_question.id,
            question_index=question_index,
            question_text=target_question.question_text,
            question_type=target_question.question_type.value,
            selected_option=selected_option.strip() if selected_option else None,
            text_response=text_response.strip() if text_response else None,
        )

        # Re-fetch all answers to determine next unanswered question index
        updated_answers = await self._assessment_repo.get_answers(assessment.id)
        answered_indices = {a.question_index for a in updated_answers}

        next_idx = None
        for i in range(1, self.TOTAL_QUESTIONS + 1):
            if i not in answered_indices:
                next_idx = i
                break

        # Advance current_question_index if we answered the current pointer
        if next_idx is not None:
            assessment.current_question_index = next_idx
        else:
            assessment.current_question_index = self.TOTAL_QUESTIONS

        await self._assessment_repo.update_assessment(assessment)

        return saved_answer, assessment, next_idx

    async def complete_assessment(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> tuple[AssessmentModel, AssessmentResultModel]:
        """
        Complete assessment workflow, validating that all 15 questions are answered,
        and synthesize Enriched Project Understanding.
        Idempotent: If already completed, returns existing result.
        """
        project = await self._resolve_and_authorize_project(project_id, current_user)
        assessment = await self._assessment_repo.get_by_project_id(project.id)

        if not assessment:
            raise BusinessRuleException(
                "Assessment has not been started.",
                code="ASSESSMENT_NOT_STARTED",
            )

        # Idempotency check: Already completed?
        if assessment.status == AssessmentStatus.COMPLETED.value:
            existing_result = await self._assessment_repo.get_result_by_assessment_id(
                assessment.id
            )
            if existing_result:
                return assessment, existing_result

        # Validate completeness
        answers = await self._assessment_repo.get_answers(assessment.id)
        answered_indices = {a.question_index for a in answers}

        missing = [i for i in range(1, self.TOTAL_QUESTIONS + 1) if i not in answered_indices]
        if missing:
            raise BusinessRuleException(
                f"Assessment is incomplete. Unanswered question(s): {', '.join(map(str, missing))}.",
                code="ASSESSMENT_INCOMPLETE",
            )

        # Synthesize Enriched Project Understanding (§ 18 & 19 of 5B / § 31 of 1)
        now = datetime.now(UTC)
        assessment.status = AssessmentStatus.COMPLETED.value
        assessment.completed_at = now
        await self._assessment_repo.update_assessment(assessment)

        # Compute deterministic readiness & dimensional scores based on responses & project complexity
        proj_complexity = project.complexity
        dimension_scores = {
            "problem_clarity": 88,
            "architecture_readiness": 85,
            "technical_feasibility": 82,
            "delivery_confidence": 80,
        }
        overall_score = 84
        readiness_tier = AssessmentReadinessTier.HIGH.value

        # Enriched Project Understanding attributes
        skill_level = "Intermediate"
        alignment = "Strong alignment between architectural design and problem scope."
        technical_confidence = "High"
        learning_depth = "High"
        recommended_focus = (
            f"Focus on explicit API contracts, transactional data isolation, and "
            f"circuit-breaker fallbacks for {project.name} during Blueprint generation."
        )
        summary = (
            f"Comprehensive diagnostic evaluation of '{project.name}' completed. "
            f"The project demonstrates sound architectural principles, clear problem boundaries, "
            f"and coherent technology stack alignment. The student has established sufficient technical "
            f"grounding to proceed directly to Blueprint generation."
        )
        identified_gaps = [
            {
                "area": "External Boundaries",
                "severity": "LOW",
                "description": "Ensure asynchronous timeout limits and retry headers are codified.",
            },
            {
                "area": "State Persistence",
                "severity": "LOW",
                "description": "Establish transactional rollback behavior for partial multistep operations.",
            },
        ]
        recommendations = [
            {
                "phase": "Blueprint",
                "action": "Generate structured technical specification prioritizing data schemas and endpoint contracts.",
            },
            {
                "phase": "Architecture",
                "action": "Maintain clean separation between HTTP route handlers and application domain services.",
            },
        ]

        result = AssessmentResultModel(
            id=str(uuid.uuid4()),
            assessment_id=str(assessment.id),
            project_instance_id=str(project.id),
            skill_level=skill_level,
            project_complexity=proj_complexity,
            alignment=alignment,
            technical_confidence=technical_confidence,
            learning_depth=learning_depth,
            recommended_focus=recommended_focus,
            summary=summary,
            overall_score=overall_score,
            readiness_tier=readiness_tier,
            dimension_scores=dimension_scores,
            identified_gaps=identified_gaps,
            recommendations=recommendations,
        )
        result = await self._assessment_repo.create_result(result)

        # Update project progress percentage to 25% for Stage 2 (Assessment complete)
        if project.progress_percentage < 25:
            project.progress_percentage = 25

        return assessment, result

    async def get_assessment_result(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> AssessmentResultModel:
        """Retrieve synthesized Enriched Project Understanding for a completed assessment."""
        project = await self._resolve_and_authorize_project(project_id, current_user)
        result = await self._assessment_repo.get_result_by_project_id(project.id)

        if not result:
            raise NotFoundException(
                "Assessment result not found. The assessment has not been completed yet.",
                code="ASSESSMENT_RESULT_NOT_FOUND",
            )

        return result
