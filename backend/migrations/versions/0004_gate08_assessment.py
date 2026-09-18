"""Gate 08: create assessment, assessment_answers, and assessment_results tables.

Revision ID: 0004_gate08_assessment
Revises: 0003_gate05_core_domain
Create Date: 2026-09-13 UTC

Authorised by: Gate 08 — Assessment System
Architecture ref:
  6N § 16 — Assessment Architecture
  5B § 18 & 19 — AI Assessment & Enriched Project Understanding
  1 § 31 — Final Student-Side Concept
  6B § 7 — Project Instances
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0004_gate08_assessment"
down_revision: str | None = "0003_gate05_core_domain"
branch_labels: str | None = None
depends_on: str | None = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. assessments
    # ---------------------------------------------------------
    op.create_table(
        "assessments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="NOT_STARTED"),
        sa.Column("current_question_index", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("total_questions", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_assessments_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_assessments_student_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assessments")),
        sa.UniqueConstraint("project_instance_id", name="uq_assessments_project_instance"),
    )
    op.create_index(
        op.f("ix_assessments_project_instance_id"),
        "assessments",
        ["project_instance_id"],
        unique=True,
    )
    op.create_index(op.f("ix_assessments_student_id"), "assessments", ["student_id"], unique=False)
    op.create_index(op.f("ix_assessments_status"), "assessments", ["status"], unique=False)

    # ---------------------------------------------------------
    # 2. assessment_answers
    # ---------------------------------------------------------
    op.create_table(
        "assessment_answers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("assessment_id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=100), nullable=False),
        sa.Column("question_index", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=50), nullable=False),
        sa.Column("selected_option", sa.String(length=255), nullable=True),
        sa.Column("text_response", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["assessments.id"],
            name=op.f("fk_assessment_answers_assessment_id_assessments"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assessment_answers")),
        sa.UniqueConstraint("assessment_id", "question_id", name="uq_assessment_answer"),
    )
    op.create_index(
        op.f("ix_assessment_answers_assessment_id"),
        "assessment_answers",
        ["assessment_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 3. assessment_results
    # ---------------------------------------------------------
    op.create_table(
        "assessment_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("assessment_id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("skill_level", sa.String(length=50), nullable=False),
        sa.Column("project_complexity", sa.String(length=50), nullable=False),
        sa.Column("alignment", sa.String(length=255), nullable=False),
        sa.Column("technical_confidence", sa.String(length=50), nullable=False),
        sa.Column("learning_depth", sa.String(length=50), nullable=False),
        sa.Column("recommended_focus", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("readiness_tier", sa.String(length=50), nullable=False),
        sa.Column("dimension_scores", JSON_TYPE, nullable=False),
        sa.Column("identified_gaps", JSON_TYPE, nullable=False),
        sa.Column("recommendations", JSON_TYPE, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["assessments.id"],
            name=op.f("fk_assessment_results_assessment_id_assessments"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_assessment_results_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assessment_results")),
        sa.UniqueConstraint("assessment_id", name="uq_assessment_results_assessment"),
        sa.UniqueConstraint("project_instance_id", name="uq_assessment_results_project_instance"),
    )
    op.create_index(
        op.f("ix_assessment_results_assessment_id"),
        "assessment_results",
        ["assessment_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_assessment_results_project_instance_id"),
        "assessment_results",
        ["project_instance_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("assessment_results")
    op.drop_table("assessment_answers")
    op.drop_table("assessments")
