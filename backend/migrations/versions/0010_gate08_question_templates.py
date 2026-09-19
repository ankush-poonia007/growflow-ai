"""Gate 08: create assessment_question_templates and assessment_questions tables.

Revision ID: 0010_gate08_question_templates
Revises: 0009_gate13_notifications
Create Date: 2026-09-19 UTC

Authorised by: Gate 08 — Assessment System
Architecture ref:
  6B § 8.1 — assessment_question_templates (versioned core question templates)
  6B § 8.3 — assessment_questions (persisted generated/instantiated assessment questions)
  5B § 14 & 15 — Dynamic Question Logic & Quality Rules
  6C § 16 — Adaptive Assessment API Flow
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0010_gate08_question_templates"
down_revision: str | None = "0009_gate13_notifications"
branch_labels: str | None = None
depends_on: str | None = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")

# Canonical Version 1 Core Question Templates
CORE_QUESTION_TEMPLATES_V1 = [
    {
        "id": "c1000000-0000-4000-a000-000000000001",
        "version": 1,
        "sequence_number": 1,
        "category": "Problem Definition & User Impact",
        "question_text": "How clearly defined is the specific problem and the primary user persona your project addresses?",
        "help_text": "Evaluate whether you have identified concrete user pain points versus a generalized topic area.",
        "question_type": "MULTIPLE_CHOICE",
        "options": [
            {
                "value": "SPECIFIC_PERSONA",
                "label": "Highly Specific Persona & Measurable Pain Point",
                "description": "Direct user workflow identified with measurable inefficiencies or explicit requirements.",
            },
            {
                "value": "TARGET_SEGMENT",
                "label": "Defined Target Segment with Broad Use Cases",
                "description": "Clear user group identified, but specific daily workflows are still being refined.",
            },
            {
                "value": "GENERAL_TOPIC",
                "label": "Broad Technical Opportunity",
                "description": "Concept explores a technology or capability rather than a tailored user problem.",
            },
            {
                "value": "EXPLORATORY",
                "label": "Exploratory / Theoretical Research",
                "description": "Problem space is open-ended without a predefined user group.",
            },
        ],
    },
    {
        "id": "c1000000-0000-4000-a000-000000000002",
        "version": 1,
        "sequence_number": 2,
        "category": "Core Value Proposition & Mechanics",
        "question_text": "What is the primary mechanism through which your software solves the identified problem?",
        "help_text": "Describe how the core loop delivers value to the user.",
        "question_type": "MULTIPLE_CHOICE",
        "options": [
            {
                "value": "AUTOMATED_WORKFLOW",
                "label": "Automated Pipeline / Workflow Orchestration",
                "description": "Eliminates repetitive manual steps by chaining operations into an automated flow.",
            },
            {
                "value": "INTELLIGENT_SYNTHESIS",
                "label": "Data Synthesis, Analytics, or Machine Intelligence",
                "description": "Transforms raw inputs into actionable insights, recommendations, or classifications.",
            },
            {
                "value": "INTERACTIVE_INTERFACE",
                "label": "Domain-Specific Collaborative Workspace / Interface",
                "description": "Provides specialized UI tooling for users to create, visualize, or collaborate on assets.",
            },
            {
                "value": "PLATFORM_INTEGRATION",
                "label": "Cross-System Integration & Synchronization",
                "description": "Unifies disconnected third-party services and APIs into a unified control surface.",
            },
        ],
    },
    {
        "id": "c1000000-0000-4000-a000-000000000003",
        "version": 1,
        "sequence_number": 3,
        "category": "Target Architecture & Pattern",
        "question_text": "Which architectural pattern best characterizes your planned system structure?",
        "help_text": "Select the structural topology that best matches your deployment and communication model.",
        "question_type": "MULTIPLE_CHOICE",
        "options": [
            {
                "value": "MODULAR_MONOLITH",
                "label": "Modular Monolith with Clean Layered Boundaries",
                "description": "Single deployable runtime organized into strict domain modules and repository boundaries.",
            },
            {
                "value": "CLIENT_SERVER_SPA",
                "label": "Decoupled Single Page App + Headless REST/GraphQL API",
                "description": "Independent frontend client communicating with an authoritative backend API layer.",
            },
            {
                "value": "EVENT_DRIVEN_MICROSERVICES",
                "label": "Event-Driven Microservices / Asynchronous Workers",
                "description": "Distributed services coordinating through message buses or background queues.",
            },
            {
                "value": "EDGE_SERVERLESS",
                "label": "Serverless Functions & Edge Runtime",
                "description": "Stateless HTTP handlers deployed to serverless infrastructure with managed services.",
            },
        ],
    },
    {
        "id": "c1000000-0000-4000-a000-000000000004",
        "version": 1,
        "sequence_number": 4,
        "category": "Technology Stack Justification",
        "question_text": "What is the primary rationale for your chosen programming languages and core frameworks?",
        "help_text": "Reflect on why this technology selection optimizes for delivery speed, safety, and ecosystem fit.",
        "question_type": "MULTIPLE_CHOICE",
        "options": [
            {
                "value": "TYPE_SAFETY_ECOSYSTEM",
                "label": "Type Safety & Mature Industrial Ecosystem",
                "description": "Strong static typing and established enterprise tooling (e.g. TypeScript, Python/FastAPI).",
            },
            {
                "value": "DEVELOPER_VELOCITY",
                "label": "Rapid PrototypING & Developer Velocity",
                "description": "High-level frameworks that provide batteries-included abstractions for rapid delivery.",
            },
            {
                "value": "DOMAIN_PERFORMANCE",
                "label": "Domain-Specific Performance or Hardware Integration",
                "description": "Specific libraries required for high-throughput computation, telemetry, or embedded hardware.",
            },
            {
                "value": "LEARNING_GOAL",
                "label": "Educational Mastery & Skill Expansion",
                "description": "Chosen specifically to master new paradigm concepts and expand professional proficiency.",
            },
        ],
    },
    {
        "id": "c1000000-0000-4000-a000-000000000005",
        "version": 1,
        "sequence_number": 5,
        "category": "Data Model & Storage Strategy",
        "question_text": "What primary data persistence and state management strategy best fits your system?",
        "help_text": "Consider transaction guarantees, query relational complexity, and data volume.",
        "question_type": "MULTIPLE_CHOICE",
        "options": [
            {
                "value": "RELATIONAL_ACID",
                "label": "Relational Database with ACID Guarantees",
                "description": "Strict foreign keys, constraints, and transactional consistency (e.g. PostgreSQL, SQLite).",
            },
            {
                "value": "DOCUMENT_JSON",
                "label": "Document / Key-Value Store for Flexible Schema",
                "description": "Semi-structured document storage where entities have variable attributes (e.g. MongoDB).",
            },
            {
                "value": "HYBRID_RELATIONAL_BLOB",
                "label": "Hybrid Relational Metadata + Blob Storage",
                "description": "Structured relational tables for entities combined with object storage for files or media.",
            },
            {
                "value": "TIME_SERIES_CACHE",
                "label": "In-Memory Cache & Time-Series Stream",
                "description": "High-velocity metrics or volatile state requiring caching layers (e.g. Redis).",
            },
        ],
    },
    {
        "id": "c1000000-0000-4000-a000-000000000006",
        "version": 1,
        "sequence_number": 6,
        "category": "System Integrations & External APIs",
        "question_text": "How dependent is your core value proposition on third-party APIs, external hardware, or webhooks?",
        "help_text": "Evaluate availability risks and external contract stability.",
        "question_type": "MULTIPLE_CHOICE",
        "options": [
            {
                "value": "SELF_CONTAINED",
                "label": "Primarily Self-Contained System",
                "description": "All core logic and storage are fully managed within your application boundaries.",
            },
            {
                "value": "STANDARD_APIS",
                "label": "Standard SaaS Integration (Auth, Email, Cloud Storage)",
                "description": "Relies on mature external commodity providers with high availability SLAs.",
            },
            {
                "value": "CRITICAL_DEPENDENCY",
                "label": "Critical Core Dependency on Specialized APIs",
                "description": "Core business value depends directly on specialized APIs (e.g. AI models, payment rails).",
            },
            {
                "value": "HARDWARE_IOT",
                "label": "Physical Hardware / IoT / Protocol Interface",
                "description": "Interacts with physical sensors, local edge devices, or serial protocols.",
            },
        ],
    },
    {
        "id": "c1000000-0000-4000-a000-000000000007",
        "version": 1,
        "sequence_number": 7,
        "category": "Security, Authentication & Access Control",
        "question_text": "What authentication and tenant authorization boundaries will protect user data in your project?",
        "help_text": "Verify how identity verification and resource scoping are separated.",
        "question_type": "MULTIPLE_CHOICE",
        "options": [
            {
                "value": "ROLE_BASED_RLS",
                "label": "Role-Based Access Control (RBAC) + Database Row-Level Security",
                "description": "Strict user roles (e.g. Student, Mentor, Admin) backed by database-level ownership policies.",
            },
            {
                "value": "TOKEN_JWT_APP_LEVEL",
                "label": "JWT Token Authentication + Application-Level Middleware",
                "description": "Authoritative token claims verified in API middleware prior to handler execution.",
            },
            {
                "value": "MULTI_TENANT_ORGANIZATION",
                "label": "Multi-Tenant Workspace Isolation",
                "description": "Data isolated by organization/group boundary with scoped team privileges.",
            },
            {
                "value": "PUBLIC_READ_PRIVATE_WRITE",
                "label": "Public Read-Only Catalog + Authenticated Creator Writes",
                "description": "Open visibility for discovery with authenticated ownership required for mutations.",
            },
        ],
    },
    {
        "id": "c1000000-0000-4000-a000-000000000008",
        "version": 1,
        "sequence_number": 8,
        "category": "Performance & Scalability Targets",
        "question_text": "What are your expected operational latency and concurrency requirements for the initial release?",
        "help_text": "Grounding operational parameters prevents premature optimization while establishing realistic boundaries.",
        "question_type": "MULTIPLE_CHOICE",
        "options": [
            {
                "value": "INTERACTIVE_LOW_CONCURRENCY",
                "label": "Sub-second Interactive UI (< 100 concurrent users)",
                "description": "Standard responsive web performance focusing on code cleanliness over distributed caching.",
            },
            {
                "value": "HIGH_THROUGHPUT_PIPELINE",
                "label": "Batch / Background Processing Throughput",
                "description": "System prioritizes job completion and queue stability over immediate sub-100ms response.",
            },
            {
                "value": "LOW_LATENCY_STREAMING",
                "label": "Near-Realtime Streaming (< 200ms roundtrip)",
                "description": "Interactive telemetry or WebSocket messaging requiring optimized network hops.",
            },
            {
                "value": "OFFLINE_FIRST",
                "label": "Offline-First Local Operation with Sync",
                "description": "System operates locally with intermittent network synchronization.",
            },
        ],
    },
    {
        "id": "c1000000-0000-4000-a000-000000000009",
        "version": 1,
        "sequence_number": 9,
        "category": "Quality Assurance & Validation Methodology",
        "question_text": "What testing and verification methodology will guarantee that your implementation is correct?",
        "help_text": "Determine how defects and regressions will be systematically caught before deployment.",
        "question_type": "MULTIPLE_CHOICE",
        "options": [
            {
                "value": "AUTOMATED_PYRAMID",
                "label": "Automated Test Pyramid (Unit + Integration + Contract Tests)",
                "description": "Comprehensive unit tests for business logic combined with HTTP API integration tests.",
            },
            {
                "value": "E2E_USER_FLOWS",
                "label": "End-to-End User Journey Verification",
                "description": "Browser-level workflow verification testing critical paths from sign-in to completion.",
            },
            {
                "value": "TEST_DRIVEN_DEVELOPMENT",
                "label": "Test-Driven Development (TDD) for Core Invariants",
                "description": "Writing tests prior to implementation to lock down boundary specifications.",
            },
            {
                "value": "MANUAL_ACCEPTANCE",
                "label": "Deterministic Scenario-Based Manual Acceptance",
                "description": "Structured test checklists verified against canonical acceptance criteria.",
            },
        ],
    },
    {
        "id": "c1000000-0000-4000-a000-000000000010",
        "version": 1,
        "sequence_number": 10,
        "category": "Technical Risks & Failure Modes",
        "question_text": "What is the single greatest technical unknown or failure risk that could jeopardize project delivery?",
        "help_text": "Identifying failure modes early enables proactive mitigation in the upcoming Blueprint phase.",
        "question_type": "MULTIPLE_CHOICE",
        "options": [
            {
                "value": "EXTERNAL_API_INSTABILITY",
                "label": "Third-Party API Rate Limits, Breaking Changes, or Downtime",
                "description": "Dependence on an external vendor or experimental service that may fail unpredictably.",
            },
            {
                "value": "DATA_MODEL_EVOLUTION",
                "label": "Underestimated Data Model Relational Complexity",
                "description": "Domain entities and relationships may require significant schema restructuring mid-build.",
            },
            {
                "value": "PERFORMANCE_BOTTLENECK",
                "label": "Algorithmic / Resource Scalability Bottlenecks",
                "description": "Computationally intensive logic or memory pressure under real-world input sizes.",
            },
            {
                "value": "SCOPE_CREEP",
                "label": "Scope Expansion Beyond the Available Timeline",
                "description": "Accumulating additional secondary features before proving the minimum viable core.",
            },
        ],
    },
]


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. assessment_question_templates
    # ---------------------------------------------------------
    templates_table = op.create_table(
        "assessment_question_templates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("help_text", sa.Text(), nullable=True),
        sa.Column(
            "question_type", sa.String(length=50), nullable=False, server_default="MULTIPLE_CHOICE"
        ),
        sa.Column("options", JSON_TYPE, nullable=False, server_default="[]"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assessment_question_templates")),
        sa.UniqueConstraint("version", "sequence_number", name="uq_template_version_seq"),
    )
    op.create_index(
        op.f("ix_assessment_question_templates_version"),
        "assessment_question_templates",
        ["version"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assessment_question_templates_sequence_number"),
        "assessment_question_templates",
        ["sequence_number"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 2. assessment_questions
    # ---------------------------------------------------------
    op.create_table(
        "assessment_questions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("assessment_id", sa.String(length=36), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("question_type", sa.String(length=50), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("generation_metadata", JSON_TYPE, nullable=False, server_default="{}"),
        sa.Column("generated_from_question_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["assessments.id"],
            name=op.f("fk_assessment_questions_assessment_id_assessments"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["generated_from_question_id"],
            ["assessment_questions.id"],
            name=op.f("fk_assessment_questions_generated_from_question_id"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assessment_questions")),
        sa.UniqueConstraint("assessment_id", "sequence_number", name="uq_assessment_question_seq"),
    )
    op.create_index(
        op.f("ix_assessment_questions_assessment_id"),
        "assessment_questions",
        ["assessment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_assessment_questions_sequence_number"),
        "assessment_questions",
        ["sequence_number"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 3. Seed Version 1 Core Question Templates
    # ---------------------------------------------------------
    op.bulk_insert(
        templates_table,
        [
            {
                "id": t["id"],
                "version": t["version"],
                "sequence_number": t["sequence_number"],
                "question_text": t["question_text"],
                "active": True,
                "category": t["category"],
                "help_text": t["help_text"],
                "question_type": t["question_type"],
                "options": t["options"],
            }
            for t in CORE_QUESTION_TEMPLATES_V1
        ],
    )

    # ---------------------------------------------------------
    # 4. PostgreSQL Row Level Security (RLS)
    # ---------------------------------------------------------
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE assessment_question_templates ENABLE ROW LEVEL SECURITY")
        op.execute("ALTER TABLE assessment_questions ENABLE ROW LEVEL SECURITY")
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                    -- Templates: readable by any authenticated user
                    DROP POLICY IF EXISTS assessment_question_templates_select ON assessment_question_templates;
                    CREATE POLICY assessment_question_templates_select ON assessment_question_templates
                        FOR SELECT
                        USING (true);

                    -- Persisted questions: scoped to assessment student owner
                    DROP POLICY IF EXISTS assessment_questions_select ON assessment_questions;
                    CREATE POLICY assessment_questions_select ON assessment_questions
                        FOR SELECT
                        USING (
                            EXISTS (
                                SELECT 1 FROM assessments a
                                WHERE a.id = assessment_questions.assessment_id
                                  AND a.student_id = (SELECT auth.uid()::text)
                            )
                        );

                    DROP POLICY IF EXISTS assessment_questions_insert ON assessment_questions;
                    CREATE POLICY assessment_questions_insert ON assessment_questions
                        FOR INSERT
                        WITH CHECK (
                            EXISTS (
                                SELECT 1 FROM assessments a
                                WHERE a.id = assessment_questions.assessment_id
                                  AND a.student_id = (SELECT auth.uid()::text)
                            )
                        );
                END IF;
            END
            $$;
        """)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                    DROP POLICY IF EXISTS assessment_questions_insert ON assessment_questions;
                    DROP POLICY IF EXISTS assessment_questions_select ON assessment_questions;
                    DROP POLICY IF EXISTS assessment_question_templates_select ON assessment_question_templates;
                END IF;
            END
            $$;
        """)

    op.drop_table("assessment_questions")
    op.drop_table("assessment_question_templates")
