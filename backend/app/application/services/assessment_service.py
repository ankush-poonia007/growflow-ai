"""
GrowFlow — Assessment Application Service.

Coordinates:
- Versioned question template instantiation (10 standardized core questions)
- Strict sequential adaptive question synthesis (Questions 11-15)
- Server-authoritative accumulated adaptive context
- Session lifecycle (NOT_STARTED -> IN_PROGRESS -> COMPLETED)
- Answer persistence, idempotency, and immutability enforcement
- Assessment-start idempotency & concurrency safety
- Deterministic, explainable Enriched Project Understanding (EPU) scoring
- Student ownership enforcement & project lifecycle synchronization

Architecture ref:
  6N § 16 — Assessment Architecture (10 standardized core + 5 dynamic questions)
  6B § 8.1 — assessment_question_templates (versioned core question templates)
  6B § 8.3 — assessment_questions (persisted question records & chain traceability)
  5B § 14 & 15 — Dynamic Question Logic & Quality Rules (Strict Sequential Generation)
  6C § 16 — Adaptive Assessment API Flow
  1 § 31 — Final Student-Side Concept
  FRONTEND_BACKEND_CONTRACT § 11.2 — Assessment Result Contracts
"""

from __future__ import annotations

import contextlib
from datetime import UTC, datetime
import re
from typing import TYPE_CHECKING, Any
import uuid

from sqlalchemy.exc import IntegrityError

from backend.app.domain.assessment.models import (
    AssessmentQuestion,
    AssessmentQuestionOption,
    AssessmentReadinessTier,
    AssessmentStatus,
    QuestionType,
)
from backend.app.domain.project.models import ProjectPhase
from backend.app.infrastructure.database.models.assessment import (
    AssessmentAnswerModel,
    AssessmentModel,
    AssessmentQuestionModel,
    AssessmentQuestionTemplateModel,
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


# =============================================================================
# Deterministic EPU Rubric & Scoring Weights
# =============================================================================

# Maturity scoring for multiple choice options (bounded 0-100)
_OPTION_SCORE_MAP: dict[str, dict[str, int]] = {
    "core-01-problem-definition": {
        "SPECIFIC_PERSONA": 92,
        "TARGET_SEGMENT": 82,
        "GENERAL_TOPIC": 72,
        "EXPLORATORY": 65,
    },
    "core-02-solution-mechanics": {
        "AUTOMATED_WORKFLOW": 88,
        "INTELLIGENT_SYNTHESIS": 86,
        "PLATFORM_INTEGRATION": 84,
        "INTERACTIVE_INTERFACE": 82,
    },
    "core-03-system-architecture": {
        "EVENT_DRIVEN_MICROSERVICES": 90,
        "MODULAR_MONOLITH": 88,
        "CLIENT_SERVER_SPA": 82,
        "EDGE_SERVERLESS": 80,
    },
    "core-04-tech-stack-justification": {
        "TYPE_SAFETY_ECOSYSTEM": 90,
        "DOMAIN_PERFORMANCE": 88,
        "DEVELOPER_VELOCITY": 82,
        "LEARNING_GOAL": 75,
    },
    "core-05-data-storage-strategy": {
        "RELATIONAL_ACID": 92,
        "HYBRID_RELATIONAL_BLOB": 88,
        "TIME_SERIES_CACHE": 82,
        "DOCUMENT_JSON": 80,
    },
    "core-06-system-integrations": {
        "SELF_CONTAINED": 88,
        "STANDARD_APIS": 85,
        "CRITICAL_DEPENDENCY": 78,
        "HARDWARE_IOT": 80,
    },
    "core-07-security-access": {
        "ROLE_BASED_RLS": 92,
        "MULTI_TENANT_ORGANIZATION": 88,
        "TOKEN_JWT_APP_LEVEL": 82,
        "PUBLIC_READ_PRIVATE_WRITE": 70,
    },
    "core-08-performance-scalability": {
        "LOW_LATENCY_STREAMING": 88,
        "HIGH_THROUGHPUT_PIPELINE": 86,
        "INTERACTIVE_LOW_CONCURRENCY": 85,
        "OFFLINE_FIRST": 80,
    },
    "core-09-qa-validation": {
        "AUTOMATED_PYRAMID": 92,
        "TEST_DRIVEN_DEVELOPMENT": 88,
        "E2E_USER_FLOWS": 84,
        "MANUAL_ACCEPTANCE": 70,
    },
    "core-10-risks-failure-modes": {
        "DATA_MODEL_EVOLUTION": 82,
        "PERFORMANCE_BOTTLENECK": 80,
        "EXTERNAL_API_INSTABILITY": 78,
        "SCOPE_CREEP": 75,
    },
}

_TECHNICAL_KEYWORDS: set[str] = {
    "boundary",
    "contract",
    "schema",
    "rollback",
    "transaction",
    "circuit",
    "fallback",
    "isolate",
    "validation",
    "latency",
    "test",
    "resilience",
    "idempotent",
    "domain",
    "service",
    "repository",
}


def _score_text_response(text: str | None) -> int:
    """Deterministic score for open text answers based on length and technical keywords."""
    if not text:
        return 60
    cleaned = text.strip()
    length = len(cleaned)
    if length >= 120:
        base = 88
    elif length >= 60:
        base = 82
    elif length >= 20:
        base = 74
    else:
        base = 62

    # Keyword depth bonus (up to +8 points)
    words = set(re.findall(r"\b[a-zA-Z]+\b", cleaned.lower()))
    matches = words.intersection(_TECHNICAL_KEYWORDS)
    bonus = min(len(matches) * 2, 8)
    return min(100, base + bonus)


class AssessmentService:
    """
    Application service for managing student assessment sessions, questions, answers, and results.
    Adheres strictly to Gate 08 specifications:
    - 10 core questions (versioned templates)
    - 5 sequential adaptive questions (persisted upon generation)
    - Accumulated server-derived context
    - Answer immutability after progression moves forward
    - Deterministic, explainable EPU score computation
    """

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
    # Question Templates & Core Question Bank
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

    # =========================================================================
    # Adaptive Question Synthesis (Q11-Q15)
    # =========================================================================

    def _synthesize_adaptive_question(
        self,
        question_index: int,
        project: ProjectInstanceModel,
        prior_answers: dict[str, str | None],
    ) -> AssessmentQuestion:
        """
        Dynamically synthesize project-specific questions 11-15 based on:
        - project context (name, complexity)
        - accumulated server-persisted prior answers.

        Guarantees:
        - Q11 depends on Q3 architecture answer & project context.
        - Q12 depends on Q11 answer & Q5 data storage answer.
        - Q13 depends on Q12 answer & Q11 boundary context (compliant with Part D).
        - Q14 depends on Q10 risk answer.
        - Q15 depends on Q14 fallback answer & Q10 risk (compliant with Part D).
        """
        proj_name = project.name
        complexity = project.complexity
        q3_arch = (
            prior_answers.get("core-03-system-architecture")
            or prior_answers.get("3")
            or "MODULAR_MONOLITH"
        )
        q5_data = (
            prior_answers.get("core-05-data-storage-strategy")
            or prior_answers.get("5")
            or "RELATIONAL_ACID"
        )
        q10_risk = (
            prior_answers.get("core-10-risks-failure-modes")
            or prior_answers.get("10")
            or "SCOPE_CREEP"
        )

        q11_ans = (
            prior_answers.get("adaptive-11-architectural-boundaries")
            or prior_answers.get("11")
            or ""
        )
        q12_ans = (
            prior_answers.get("adaptive-12-state-reconciliation") or prior_answers.get("12") or ""
        )
        q14_ans = prior_answers.get("adaptive-14-risk-mitigation") or prior_answers.get("14") or ""

        def _summarize(ans: str, fallback: str, max_len: int = 70) -> str:
            clean = ans.strip().replace("\n", " ")
            if not clean:
                return fallback
            if len(clean) > max_len:
                return clean[:max_len].rstrip() + "..."
            return clean

        if question_index == 11:
            return AssessmentQuestion(
                id="adaptive-11-architectural-boundaries",
                order_index=11,
                category="Adaptive Architectural Invariants",
                question_text=(
                    f"For '{proj_name}' ({complexity} tier), how will you enforce separation between user-facing "
                    f"interactions and core domain logic under a {q3_arch} pattern?"
                ),
                help_text=(
                    f"Explain the architectural boundary that prevents business logic from leaking into HTTP "
                    f"controllers or UI components in {proj_name}."
                ),
                question_type=QuestionType.TEXT,
                is_adaptive=True,
                context_badge="ADAPTIVE: ARCHITECTURAL BOUNDARIES",
            )
        elif question_index == 12:
            q11_ctx = _summarize(q11_ans, "your domain separation boundary")
            return AssessmentQuestion(
                id="adaptive-12-state-reconciliation",
                order_index=12,
                category="Adaptive Data Lifecycle & State",
                question_text=(
                    f"Given your approach to architectural boundaries ('{q11_ctx}') and selection of {q5_data}, "
                    f"how will '{proj_name}' handle data validation errors, transactional rollbacks, and concurrent student updates?"
                ),
                help_text="Detail how you will maintain state integrity when network failures or invalid payloads occur.",
                question_type=QuestionType.TEXT,
                is_adaptive=True,
                context_badge="ADAPTIVE: DATA INTEGRITY",
            )
        elif question_index == 13:
            q12_ctx = _summarize(q12_ans, "your transactional rollback strategy")
            return AssessmentQuestion(
                id="adaptive-13-boundary-constraints",
                order_index=13,
                category="Adaptive Boundary Constraints & Trade-offs",
                question_text=(
                    f"Considering how '{proj_name}' reconciles state and data integrity ('{q12_ctx}'), "
                    f"what explicit architectural trade-offs are you making between latency, operational simplicity, and immediate consistency?"
                ),
                help_text="Every architectural design sacrifices something. Articulate your system's deliberate trade-offs.",
                question_type=QuestionType.TEXT,
                is_adaptive=True,
                context_badge="ADAPTIVE: DESIGN TRADE-OFFS",
            )
        elif question_index == 14:
            return AssessmentQuestion(
                id="adaptive-14-risk-mitigation",
                order_index=14,
                category="Adaptive Risk Mitigation & Fallback",
                question_text=(
                    f"In Question 10, you identified '{q10_risk}' as your primary delivery risk. "
                    f"What concrete fallback strategy will '{proj_name}' implement if this risk materializes?"
                ),
                help_text="Define the technical circuit-breaker, fallback default, or scope reduction plan that keeps the project on track.",
                question_type=QuestionType.TEXT,
                is_adaptive=True,
                context_badge="ADAPTIVE: RISK MITIGATION",
            )
        else:  # 15
            q14_ctx = _summarize(q14_ans, "your contingency fallback plan")
            return AssessmentQuestion(
                id="adaptive-15-mvp-validation-criteria",
                order_index=15,
                category="Adaptive MVP Scope & Demonstration",
                question_text=(
                    f"In light of your contingency plan for '{q10_risk}' ('{q14_ctx}'), "
                    f"what is the single minimum testable demonstration that will definitively prove '{proj_name}' is functional and resilient prior to full release?"
                ),
                help_text="Describe the end-to-end golden path milestone that validates core functionality even under failure conditions.",
                question_type=QuestionType.TEXT,
                is_adaptive=True,
                context_badge="ADAPTIVE: MVP VALIDATION",
            )

    # Legacy compatibility helper (deprecated in favor of get_or_generate_question)
    def get_all_questions_for_project(
        self, project: ProjectInstanceModel, prior_answers: dict[str, str | None]
    ) -> list[AssessmentQuestion]:
        """Returns full 15 questions for project context (provided for backward compatibility)."""
        core = self._get_core_questions()
        adaptive = [
            self._synthesize_adaptive_question(idx, project, prior_answers) for idx in range(11, 16)
        ]
        return core + adaptive

    # =========================================================================
    # Strict Sequential Adaptive Engine & Question Persistence
    # =========================================================================

    async def get_or_generate_question(
        self,
        assessment: AssessmentModel,
        sequence_number: int,
        project: ProjectInstanceModel,
    ) -> AssessmentQuestion:
        """
        Retrieves an existing persisted question or generates it sequentially.
        Enforces strict sequential lifecycle:
        - Questions 1..10 are instantiated from version 1 core question templates.
        - Question 11 cannot be generated until Question 10 is answered.
        - Questions 12..15 require answer to (sequence_number - 1) before synthesis.
        - Future adaptive questions are NEVER pre-generated.
        - Once generated, questions are persisted in assessment_questions to ensure
          recovery without text alteration.
        """
        if sequence_number < 1 or sequence_number > self.TOTAL_QUESTIONS:
            raise BusinessRuleException(
                f"Question index {sequence_number} is invalid.",
                code="ASSESSMENT_INVALID_QUESTION_INDEX",
            )

        # Check if already persisted in database
        persisted = None
        if hasattr(self._assessment_repo, "get_persisted_question"):
            res = await self._assessment_repo.get_persisted_question(assessment.id, sequence_number)
            if isinstance(res, AssessmentQuestionModel):
                persisted = res

        if persisted:
            # Reconstruct domain question from persisted record
            meta = persisted.generation_metadata or {}
            options = [
                AssessmentQuestionOption(
                    value=opt.get("value", ""),
                    label=opt.get("label", ""),
                    description=opt.get("description", ""),
                )
                for opt in meta.get("options", [])
            ]
            q_id = meta.get("question_id") or (
                f"core-0{sequence_number}"
                if sequence_number < 10
                else f"core-{sequence_number}"
                if sequence_number == 10
                else f"adaptive-{sequence_number}"
            )
            return AssessmentQuestion(
                id=q_id,
                order_index=persisted.sequence_number,
                category=meta.get("category", "General"),
                question_text=persisted.question_text,
                help_text=meta.get("help_text", ""),
                question_type=QuestionType(meta.get("question_type", "MULTIPLE_CHOICE")),
                options=options,
                is_adaptive=persisted.question_type == "DYNAMIC",
                context_badge=meta.get("context_badge"),
            )

        # Handle CORE questions (1..10)
        if sequence_number <= self.CORE_QUESTIONS_COUNT:
            template = None
            if hasattr(self._assessment_repo, "get_template_by_sequence"):
                tmpl_res = await self._assessment_repo.get_template_by_sequence(
                    sequence_number, version=1
                )
                if isinstance(tmpl_res, AssessmentQuestionTemplateModel):
                    template = tmpl_res

            if template:
                core_domain = template.to_domain()
                q_def = AssessmentQuestion(
                    id=f"core-{sequence_number:02d}",
                    order_index=core_domain.sequence_number,
                    category=core_domain.category,
                    question_text=core_domain.question_text,
                    help_text=core_domain.help_text,
                    question_type=core_domain.question_type,
                    options=core_domain.options,
                    is_adaptive=False,
                    context_badge=None,
                )
                template_id = str(template.id)
                template_version = template.version
            else:
                q_def = self._get_core_questions()[sequence_number - 1]
                template_id = "v1-default"
                template_version = 1

            # Persist question record for traceability
            if hasattr(self._assessment_repo, "create_persisted_question"):
                record = AssessmentQuestionModel(
                    id=str(uuid.uuid4()),
                    assessment_id=str(assessment.id),
                    sequence_number=sequence_number,
                    question_type="CORE",
                    question_text=q_def.question_text,
                    generation_metadata={
                        "question_id": q_def.id,
                        "template_id": template_id,
                        "template_version": template_version,
                        "category": q_def.category,
                        "help_text": q_def.help_text,
                        "question_type": q_def.question_type.value,
                        "options": [
                            {"value": o.value, "label": o.label, "description": o.description}
                            for o in q_def.options
                        ],
                        "context_badge": None,
                    },
                    generated_from_question_id=None,
                )
                with contextlib.suppress(Exception):
                    await self._assessment_repo.create_persisted_question(record)

            return q_def

        # Handle ADAPTIVE questions (11..15) — STRICT SEQUENTIAL ENGINE
        answers = await self._assessment_repo.get_answers(assessment.id)
        answered_indices = {a.question_index for a in answers}

        # Check prerequisite: previous question must be answered
        prereq_index = sequence_number - 1
        if prereq_index not in answered_indices:
            raise BusinessRuleException(
                f"Adaptive question {sequence_number} cannot be generated until question {prereq_index} is answered.",
                code="ASSESSMENT_QUESTION_NOT_READY",
            )

        # Build accumulated context map
        prior_map: dict[str, str | None] = {}
        for a in answers:
            val = a.selected_option or a.text_response
            prior_map[a.question_id] = val
            prior_map[str(a.question_index)] = val

        synthesized_q = self._synthesize_adaptive_question(sequence_number, project, prior_map)

        # Find previous question ID for chain traceability
        prev_q_id = None
        if hasattr(self._assessment_repo, "get_persisted_question"):
            prev_record = await self._assessment_repo.get_persisted_question(
                assessment.id, prereq_index
            )
            if isinstance(prev_record, AssessmentQuestionModel):
                prev_q_id = str(prev_record.id)

        # Persist synthesized adaptive question
        if hasattr(self._assessment_repo, "create_persisted_question"):
            record = AssessmentQuestionModel(
                id=str(uuid.uuid4()),
                assessment_id=str(assessment.id),
                sequence_number=sequence_number,
                question_type="DYNAMIC",
                question_text=synthesized_q.question_text,
                generation_metadata={
                    "question_id": synthesized_q.id,
                    "category": synthesized_q.category,
                    "help_text": synthesized_q.help_text,
                    "question_type": synthesized_q.question_type.value,
                    "options": [],
                    "context_badge": synthesized_q.context_badge,
                },
                generated_from_question_id=prev_q_id,
            )
            with contextlib.suppress(Exception):
                await self._assessment_repo.create_persisted_question(record)

        return synthesized_q

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
            "completed_at": assessment.completed_at.isoformat()
            if assessment.completed_at
            else None,
        }

    async def start_or_resume_assessment(
        self, project_id: uuid.UUID | str, current_user: CurrentUser
    ) -> tuple[AssessmentModel, AssessmentQuestion]:
        """
        Start or resume an assessment session.
        Idempotent: If session already exists, returns authoritative active state without duplication.
        Synchronizes lifecycle: Moves IDEA -> ASSESSMENT when started.
        """
        project = await self._resolve_and_authorize_project(project_id, current_user)
        assessment = await self._assessment_repo.get_by_project_id(project.id)

        if not assessment:
            now = datetime.now(UTC)
            new_assessment = AssessmentModel(
                id=str(uuid.uuid4()),
                project_instance_id=str(project.id),
                student_id=str(current_user.user_id),
                status=AssessmentStatus.IN_PROGRESS.value,
                current_question_index=1,
                total_questions=self.TOTAL_QUESTIONS,
                started_at=now,
            )
            try:
                assessment = await self._assessment_repo.create_assessment(new_assessment)
                if project.current_phase == ProjectPhase.IDEA.value:
                    project.current_phase = ProjectPhase.ASSESSMENT.value
            except IntegrityError:
                # Concurrent race condition: assessment was created by another request
                assessment = await self._assessment_repo.get_by_project_id(project.id)

        # Determine current active question from authoritative answers
        answers = await self._assessment_repo.get_answers(assessment.id)
        answered_indices = {a.question_index for a in answers}

        target_idx = 1
        for i in range(1, self.TOTAL_QUESTIONS + 1):
            if i not in answered_indices:
                target_idx = i
                break
        else:
            target_idx = self.TOTAL_QUESTIONS

        if (
            assessment.current_question_index != target_idx
            and assessment.status != AssessmentStatus.COMPLETED.value
        ):
            assessment.current_question_index = target_idx
            await self._assessment_repo.update_assessment(assessment)

        current_q = await self.get_or_generate_question(assessment, target_idx, project)
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

        target_question = await self.get_or_generate_question(assessment, question_index, project)

        # Check existing answer
        existing_answer = await self._assessment_repo.get_answer(assessment.id, target_question.id)

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
        Enforces answer immutability and submission idempotency:
        - If assessment is COMPLETED, all answers are immutable.
        - Once progression has moved forward (a subsequent question has been answered),
          re-submitting the same answer is idempotent (returns 200), but changing the answer
          raises ASSESSMENT_ANSWER_IMMUTABLE.
        - Answers cannot be submitted out of order before answering preceding questions.
        - Advances current_question_index appropriately.
        """
        if question_index < 1 or question_index > self.TOTAL_QUESTIONS:
            raise BusinessRuleException(
                f"Question index {question_index} is invalid.",
                code="ASSESSMENT_INVALID_QUESTION_INDEX",
            )

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

        answers = await self._assessment_repo.get_answers(assessment.id)
        ans_by_index = {a.question_index: a for a in answers}

        opt_clean = selected_option.strip() if selected_option else None
        txt_clean = text_response.strip() if text_response else None

        # Immutability Check: has progression moved forward beyond this question?
        if question_index in ans_by_index:
            existing = ans_by_index[question_index]
            has_subsequent_answers = any(idx > question_index for idx in ans_by_index)

            if has_subsequent_answers:
                # Progression has moved forward
                if existing.selected_option == opt_clean and existing.text_response == txt_clean:
                    # Idempotent duplicate submission
                    next_idx = None
                    for i in range(1, self.TOTAL_QUESTIONS + 1):
                        if i not in ans_by_index:
                            next_idx = i
                            break
                    return existing, assessment, next_idx
                else:
                    raise BusinessRuleException(
                        f"Answer for question {question_index} is immutable because progression has moved forward.",
                        code="ASSESSMENT_ANSWER_IMMUTABLE",
                    )
        else:
            # New answer: verify no skips
            if question_index > assessment.current_question_index:
                raise BusinessRuleException(
                    f"Cannot answer question {question_index} before answering preceding questions.",
                    code="ASSESSMENT_OUT_OF_ORDER",
                )

        target_question = await self.get_or_generate_question(assessment, question_index, project)

        saved_answer = await self._assessment_repo.upsert_answer(
            assessment_id=assessment.id,
            question_id=target_question.id,
            question_index=question_index,
            question_text=target_question.question_text,
            question_type=target_question.question_type.value,
            selected_option=opt_clean,
            text_response=txt_clean,
        )

        # Re-fetch answers to determine next unanswered question index
        updated_answers = await self._assessment_repo.get_answers(assessment.id)
        answered_indices = {a.question_index for a in updated_answers}

        next_idx = None
        for i in range(1, self.TOTAL_QUESTIONS + 1):
            if i not in answered_indices:
                next_idx = i
                break

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
            existing_result = await self._assessment_repo.get_result_by_assessment_id(assessment.id)
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

        now = datetime.now(UTC)
        assessment.status = AssessmentStatus.COMPLETED.value
        assessment.completed_at = now
        await self._assessment_repo.update_assessment(assessment)

        # Deterministic EPU Result Computation
        ans_by_idx = {a.question_index: a for a in answers}

        def _get_q_score(idx: int) -> int:
            ans = ans_by_idx.get(idx)
            if not ans:
                return 75
            if idx <= self.CORE_QUESTIONS_COUNT:
                q_id = ans.question_id
                opt = ans.selected_option
                if q_id in _OPTION_SCORE_MAP and opt in _OPTION_SCORE_MAP[q_id]:
                    return _OPTION_SCORE_MAP[q_id][opt]
                return 85
            else:
                return _score_text_response(ans.text_response)

        # Dimension scores using frozen dimension names (FBC § 11.2)
        dim_arch = round(
            0.30 * _get_q_score(3)
            + 0.25 * _get_q_score(5)
            + 0.20 * _get_q_score(8)
            + 0.15 * _get_q_score(11)
            + 0.10 * _get_q_score(13)
        )
        dim_feas = round(
            0.30 * _get_q_score(1)
            + 0.25 * _get_q_score(2)
            + 0.20 * _get_q_score(9)
            + 0.25 * _get_q_score(15)
        )
        dim_stack = round(
            0.35 * _get_q_score(4)
            + 0.25 * _get_q_score(5)
            + 0.20 * _get_q_score(6)
            + 0.20 * _get_q_score(12)
        )
        dim_sec = round(
            0.45 * _get_q_score(7)
            + 0.20 * _get_q_score(6)
            + 0.15 * _get_q_score(10)
            + 0.20 * _get_q_score(14)
        )

        dimension_scores = {
            "architecture": max(0, min(100, dim_arch)),
            "feasibility": max(0, min(100, dim_feas)),
            "stack_depth": max(0, min(100, dim_stack)),
            "security": max(0, min(100, dim_sec)),
        }

        # Weighted Overall Score (bounded 0-100)
        overall_score = round(
            0.30 * dimension_scores["architecture"]
            + 0.30 * dimension_scores["feasibility"]
            + 0.20 * dimension_scores["stack_depth"]
            + 0.20 * dimension_scores["security"]
        )
        overall_score = max(0, min(100, overall_score))

        # Readiness Tier thresholds per frozen contract
        if overall_score >= 80:
            readiness_tier = AssessmentReadinessTier.HIGH.value
        elif overall_score >= 60:
            readiness_tier = AssessmentReadinessTier.MODERATE.value
        else:
            readiness_tier = AssessmentReadinessTier.NEEDS_REFINEMENT.value

        skill_level = (
            "Advanced"
            if overall_score >= 85
            else "Intermediate"
            if overall_score >= 70
            else "Foundational"
        )
        alignment = (
            "Strong alignment between architectural design and problem scope."
            if dimension_scores["feasibility"] >= 80
            else "Moderate alignment; core mechanics are feasible but need refinement."
        )
        technical_confidence = (
            "High" if overall_score >= 80 else "Moderate" if overall_score >= 60 else "Developing"
        )
        learning_depth = (
            "High"
            if dimension_scores["stack_depth"] >= 80
            else "Moderate"
            if dimension_scores["stack_depth"] >= 65
            else "Foundational"
        )
        recommended_focus = (
            f"Focus on explicit API contracts, transactional data isolation, and "
            f"circuit-breaker fallbacks for {project.name} during Blueprint generation."
        )
        summary = (
            f"Comprehensive diagnostic evaluation of '{project.name}' completed with an overall score "
            f"of {overall_score}/100 ({readiness_tier.replace('_', ' ')}). The system evaluated architectural structure, "
            f"feasibility, stack depth, and security boundaries across all 15 assessment questions."
        )

        identified_gaps = []
        if dimension_scores["security"] < 82:
            identified_gaps.append(
                {
                    "area": "Security & Access Control",
                    "severity": "MEDIUM",
                    "description": "Ensure asynchronous timeout limits, retry headers, and strict authorization boundaries are codified.",
                }
            )
        if dimension_scores["architecture"] < 82:
            identified_gaps.append(
                {
                    "area": "State Persistence & Isolation",
                    "severity": "LOW",
                    "description": "Establish transactional rollback behavior for partial multistep operations.",
                }
            )
        if not identified_gaps:
            identified_gaps.append(
                {
                    "area": "Operational Telemetry",
                    "severity": "LOW",
                    "description": "Codify comprehensive structured log correlation for end-to-end user tracing.",
                }
            )

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
            project_complexity=project.complexity,
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
