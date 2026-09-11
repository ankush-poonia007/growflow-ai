"""Gate 05: create core domain tables with constraints, indexes, and RLS policies.

Revision ID: 0003_gate05_core_domain
Revises: 0002_gate04_users
Create Date: 2026-09-11 UTC

Authorised by: Gate 05 — Core Backend / Domain Foundation
Architecture ref:
  6B § 5  — Profiles & Technologies
  6B § 6  — Groups & Memberships
  6B § 7  — Project Definitions & Instances
  6B § 10 — Project Profile
  6B § 11 — Project Technologies
  6B § 20 & § 44 — Phase Model & History
  6B § 21 & § 43 — Health Model & History
  6B § 29-30 — Domain Events & Transactional Outbox
  6B § 33-34 — Foreign Key Integrity & RLS Defense in Depth
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003_gate05_core_domain"
down_revision: str | None = "0002_gate04_users"
branch_labels: str | None = None
depends_on: str | None = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. student_profiles
    # ---------------------------------------------------------
    op.create_table(
        "student_profiles",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=50), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("goals", sa.Text(), nullable=True),
        sa.Column("interests", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_student_profiles_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_student_profiles")),
    )
    op.create_index(
        op.f("ix_student_profiles_student_id"), "student_profiles", ["student_id"], unique=True
    )

    # ---------------------------------------------------------
    # 2. mentor_profiles
    # ---------------------------------------------------------
    op.create_table(
        "mentor_profiles",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("mentor_id", sa.String(length=50), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("specialization", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_mentor_profiles_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_mentor_profiles")),
    )
    op.create_index(
        op.f("ix_mentor_profiles_mentor_id"), "mentor_profiles", ["mentor_id"], unique=True
    )

    # ---------------------------------------------------------
    # 3. user_preferences
    # ---------------------------------------------------------
    op.create_table(
        "user_preferences",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("email_notifications", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("timezone", sa.String(length=50), server_default="UTC", nullable=False),
        sa.Column("preferences", JSON_TYPE, server_default="{}", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_preferences_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_user_preferences")),
    )

    # ---------------------------------------------------------
    # 4. technologies
    # ---------------------------------------------------------
    op.create_table(
        "technologies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_technologies")),
    )
    op.create_index(op.f("ix_technologies_name"), "technologies", ["name"], unique=True)
    op.create_index(op.f("ix_technologies_category"), "technologies", ["category"], unique=False)

    # ---------------------------------------------------------
    # 5. student_technologies
    # ---------------------------------------------------------
    op.create_table(
        "student_technologies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=36), nullable=False),
        sa.Column("technology_id", sa.String(length=36), nullable=False),
        sa.Column(
            "proficiency", sa.String(length=50), server_default="INTERMEDIATE", nullable=False
        ),
        sa.Column(
            "relationship_type", sa.String(length=50), server_default="KNOWN", nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_student_technologies_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["technology_id"],
            ["technologies.id"],
            name=op.f("fk_student_technologies_technology_id_technologies"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_student_technologies")),
        sa.UniqueConstraint(
            "student_id", "technology_id", "relationship_type", name="uq_student_tech_rel"
        ),
    )
    op.create_index(
        op.f("ix_student_technologies_student_id"),
        "student_technologies",
        ["student_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_student_technologies_technology_id"),
        "student_technologies",
        ["technology_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 6. groups
    # ---------------------------------------------------------
    op.create_table(
        "groups",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("mentor_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("join_code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="ACTIVE", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["mentor_id"], ["users.id"], name=op.f("fk_groups_mentor_id_users"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_groups")),
    )
    op.create_index(op.f("ix_groups_mentor_id"), "groups", ["mentor_id"], unique=False)
    op.create_index(op.f("ix_groups_join_code"), "groups", ["join_code"], unique=True)
    op.create_index(op.f("ix_groups_status"), "groups", ["status"], unique=False)

    # ---------------------------------------------------------
    # 7. group_memberships
    # ---------------------------------------------------------
    op.create_table(
        "group_memberships",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("group_id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="ACTIVE", nullable=False),
        sa.Column(
            "joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_group_memberships_group_id_groups"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_group_memberships_student_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_group_memberships")),
        sa.UniqueConstraint("group_id", "student_id", name="uq_group_student_membership"),
    )
    op.create_index(
        op.f("ix_group_memberships_group_id"), "group_memberships", ["group_id"], unique=False
    )
    op.create_index(
        op.f("ix_group_memberships_student_id"), "group_memberships", ["student_id"], unique=False
    )
    op.create_index(
        op.f("ix_group_memberships_status"), "group_memberships", ["status"], unique=False
    )

    # ---------------------------------------------------------
    # 8. project_definitions
    # ---------------------------------------------------------
    op.create_table(
        "project_definitions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_mentor_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="DRAFT", nullable=False),
        sa.Column("current_version_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["owner_mentor_id"],
            ["users.id"],
            name=op.f("fk_project_definitions_owner_mentor_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_definitions")),
    )
    op.create_index(
        op.f("ix_project_definitions_owner_mentor_id"),
        "project_definitions",
        ["owner_mentor_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_definitions_status"), "project_definitions", ["status"], unique=False
    )

    # ---------------------------------------------------------
    # 9. project_definition_versions
    # ---------------------------------------------------------
    op.create_table(
        "project_definition_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_definition_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), server_default="1", nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("problem", sa.Text(), server_default="", nullable=False),
        sa.Column("proposed_solution", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "complexity", sa.String(length=50), server_default="INTERMEDIATE", nullable=False
        ),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("duration", sa.String(length=100), server_default="", nullable=False),
        sa.Column("constraints", sa.Text(), server_default="", nullable=False),
        sa.Column("assumptions", sa.Text(), server_default="", nullable=False),
        sa.Column("technology_snapshot", JSON_TYPE, server_default="[]", nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name=op.f("fk_project_definition_versions_created_by_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["project_definition_id"],
            ["project_definitions.id"],
            name=op.f("fk_project_definition_versions_project_definition_id_project_definitions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_definition_versions")),
        sa.UniqueConstraint("project_definition_id", "version_number", name="uq_proj_def_version"),
    )
    op.create_index(
        op.f("ix_project_definition_versions_project_definition_id"),
        "project_definition_versions",
        ["project_definition_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 10. project_instances
    # ---------------------------------------------------------
    op.create_table(
        "project_instances",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("student_id", sa.String(length=36), nullable=False),
        sa.Column("group_id", sa.String(length=36), nullable=True),
        sa.Column("project_definition_id", sa.String(length=36), nullable=True),
        sa.Column("source_definition_version_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("problem", sa.Text(), server_default="", nullable=False),
        sa.Column("proposed_solution", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "complexity", sa.String(length=50), server_default="INTERMEDIATE", nullable=False
        ),
        sa.Column("current_phase", sa.String(length=50), server_default="IDEA", nullable=False),
        sa.Column("health", sa.String(length=50), server_default="HEALTHY", nullable=False),
        sa.Column("progress_percentage", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=50), server_default="ACTIVE", nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="ck_project_progress_range",
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_project_instances_group_id_groups"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_definition_id"],
            ["project_definitions.id"],
            name=op.f("fk_project_instances_project_definition_id_project_definitions"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["source_definition_version_id"],
            ["project_definition_versions.id"],
            name=op.f(
                "fk_project_instances_source_definition_version_id_project_definition_versions"
            ),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["users.id"],
            name=op.f("fk_project_instances_student_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_instances")),
    )
    op.create_index(
        op.f("ix_project_instances_student_id"), "project_instances", ["student_id"], unique=False
    )
    op.create_index(
        op.f("ix_project_instances_group_id"), "project_instances", ["group_id"], unique=False
    )
    op.create_index(
        op.f("ix_project_instances_project_definition_id"),
        "project_instances",
        ["project_definition_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_instances_current_phase"),
        "project_instances",
        ["current_phase"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_instances_health"), "project_instances", ["health"], unique=False
    )
    op.create_index(
        op.f("ix_project_instances_status"), "project_instances", ["status"], unique=False
    )

    # ---------------------------------------------------------
    # 11. project_profiles
    # ---------------------------------------------------------
    op.create_table(
        "project_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("objective", sa.Text(), server_default="", nullable=False),
        sa.Column("target_users", sa.Text(), server_default="", nullable=False),
        sa.Column("project_type", sa.String(length=100), server_default="", nullable=False),
        sa.Column("student_skill_context", sa.Text(), server_default="", nullable=False),
        sa.Column("goals", sa.Text(), server_default="", nullable=False),
        sa.Column("scope", sa.Text(), server_default="", nullable=False),
        sa.Column("expected_outcome", sa.Text(), server_default="", nullable=False),
        sa.Column("constraints", sa.Text(), server_default="", nullable=False),
        sa.Column("assumptions", sa.Text(), server_default="", nullable=False),
        sa.Column("context", sa.Text(), server_default="", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_profiles_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_profiles")),
        sa.UniqueConstraint(
            "project_instance_id", name=op.f("uq_project_profiles_project_instance_id")
        ),
    )
    op.create_index(
        op.f("ix_project_profiles_project_instance_id"),
        "project_profiles",
        ["project_instance_id"],
        unique=True,
    )

    # ---------------------------------------------------------
    # 12. project_technologies
    # ---------------------------------------------------------
    op.create_table(
        "project_technologies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("technology_id", sa.String(length=36), nullable=False),
        sa.Column("category", sa.String(length=100), server_default="", nullable=False),
        sa.Column("purpose", sa.Text(), server_default="", nullable=False),
        sa.Column("why_selected", sa.Text(), server_default="", nullable=False),
        sa.Column("appropriateness", sa.Text(), server_default="", nullable=False),
        sa.Column("student_understanding", sa.Text(), server_default="", nullable=False),
        sa.Column("usage_context", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_technologies_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["technology_id"],
            ["technologies.id"],
            name=op.f("fk_project_technologies_technology_id_technologies"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_technologies")),
        sa.UniqueConstraint("project_instance_id", "technology_id", name="uq_project_technology"),
    )
    op.create_index(
        op.f("ix_project_technologies_project_instance_id"),
        "project_technologies",
        ["project_instance_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 13. project_phase_history
    # ---------------------------------------------------------
    op.create_table(
        "project_phase_history",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("previous_phase", sa.String(length=50), nullable=False),
        sa.Column("new_phase", sa.String(length=50), nullable=False),
        sa.Column("changed_by", sa.String(length=36), nullable=False),
        sa.Column("reason", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "changed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["changed_by"],
            ["users.id"],
            name=op.f("fk_project_phase_history_changed_by_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_phase_history_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_phase_history")),
    )
    op.create_index(
        op.f("ix_project_phase_history_project_instance_id"),
        "project_phase_history",
        ["project_instance_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 14. project_health_history
    # ---------------------------------------------------------
    op.create_table(
        "project_health_history",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("previous_health", sa.String(length=50), nullable=False),
        sa.Column("new_health", sa.String(length=50), nullable=False),
        sa.Column("changed_by", sa.String(length=36), nullable=False),
        sa.Column("reason", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "changed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["changed_by"],
            ["users.id"],
            name=op.f("fk_project_health_history_changed_by_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_project_health_history_project_instance_id_project_instances"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_health_history")),
    )
    op.create_index(
        op.f("ix_project_health_history_project_instance_id"),
        "project_health_history",
        ["project_instance_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 15. domain_events (Transactional Outbox)
    # ---------------------------------------------------------
    op.create_table(
        "domain_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("actor_role", sa.String(length=50), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=True),
        sa.Column("group_id", sa.String(length=36), nullable=True),
        sa.Column("visibility", sa.String(length=50), server_default="INTERNAL", nullable=False),
        sa.Column("metadata", JSON_TYPE, server_default="{}", nullable=False),
        sa.Column("correlation_id", sa.String(length=100), server_default="", nullable=False),
        sa.Column("status", sa.String(length=50), server_default="PENDING", nullable=False),
        sa.Column(
            "occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
            name=op.f("fk_domain_events_actor_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_domain_events_group_id_groups"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_instance_id"],
            ["project_instances.id"],
            name=op.f("fk_domain_events_project_instance_id_project_instances"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_domain_events")),
    )
    op.create_index(
        op.f("ix_domain_events_event_type"), "domain_events", ["event_type"], unique=False
    )
    op.create_index(
        op.f("ix_domain_events_project_instance_id"),
        "domain_events",
        ["project_instance_id"],
        unique=False,
    )
    op.create_index(op.f("ix_domain_events_group_id"), "domain_events", ["group_id"], unique=False)
    op.create_index(op.f("ix_domain_events_status"), "domain_events", ["status"], unique=False)
    op.create_index(
        op.f("ix_domain_events_occurred_at"), "domain_events", ["occurred_at"], unique=False
    )

    # ---------------------------------------------------------
    # PostgreSQL Row Level Security (RLS) Primitives
    # ---------------------------------------------------------
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # Enable RLS on all 15 tables
        tables = [
            "student_profiles",
            "mentor_profiles",
            "user_preferences",
            "technologies",
            "student_technologies",
            "groups",
            "group_memberships",
            "project_definitions",
            "project_definition_versions",
            "project_instances",
            "project_profiles",
            "project_technologies",
            "project_phase_history",
            "project_health_history",
            "domain_events",
        ]
        for tbl in tables:
            op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY")

        # Install policies defensively if auth schema is present
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                    -- student_profiles self-access
                    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'student_profiles' AND policyname = 'student_profiles_self') THEN
                        CREATE POLICY student_profiles_self ON student_profiles
                            FOR ALL USING (user_id = auth.uid()::text);
                    END IF;

                    -- mentor_profiles self-access
                    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'mentor_profiles' AND policyname = 'mentor_profiles_self') THEN
                        CREATE POLICY mentor_profiles_self ON mentor_profiles
                            FOR ALL USING (user_id = auth.uid()::text);
                    END IF;

                    -- user_preferences self-access
                    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_preferences' AND policyname = 'user_preferences_self') THEN
                        CREATE POLICY user_preferences_self ON user_preferences
                            FOR ALL USING (user_id = auth.uid()::text);
                    END IF;

                    -- student_technologies self-access
                    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'student_technologies' AND policyname = 'student_technologies_self') THEN
                        CREATE POLICY student_technologies_self ON student_technologies
                            FOR ALL USING (student_id = auth.uid()::text);
                    END IF;

                    -- technologies read-all authenticated
                    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'technologies' AND policyname = 'technologies_read') THEN
                        CREATE POLICY technologies_read ON technologies
                            FOR SELECT USING (auth.role() = 'authenticated');
                    END IF;

                    -- groups mentor-access and student select
                    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'groups' AND policyname = 'groups_mentor_owner') THEN
                        CREATE POLICY groups_mentor_owner ON groups
                            FOR ALL USING (mentor_id = auth.uid()::text);
                    END IF;

                    -- group_memberships self or mentor
                    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'group_memberships' AND policyname = 'group_memberships_participant') THEN
                        CREATE POLICY group_memberships_participant ON group_memberships
                            FOR ALL USING (
                                student_id = auth.uid()::text OR
                                EXISTS (SELECT 1 FROM groups WHERE groups.id = group_memberships.group_id AND groups.mentor_id = auth.uid()::text)
                            );
                    END IF;

                    -- project_definitions mentor-owner
                    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'project_definitions' AND policyname = 'project_definitions_owner') THEN
                        CREATE POLICY project_definitions_owner ON project_definitions
                            FOR ALL USING (owner_mentor_id = auth.uid()::text);
                    END IF;

                    -- project_instances student-owner or group mentor
                    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'project_instances' AND policyname = 'project_instances_access') THEN
                        CREATE POLICY project_instances_access ON project_instances
                            FOR ALL USING (
                                student_id = auth.uid()::text OR
                                (group_id IS NOT NULL AND EXISTS (SELECT 1 FROM groups WHERE groups.id = project_instances.group_id AND groups.mentor_id = auth.uid()::text))
                            );
                    END IF;
                END IF;
            END
            $$;
        """)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        tables = [
            "domain_events",
            "project_health_history",
            "project_phase_history",
            "project_technologies",
            "project_profiles",
            "project_instances",
            "project_definition_versions",
            "project_definitions",
            "group_memberships",
            "groups",
            "student_technologies",
            "technologies",
            "user_preferences",
            "mentor_profiles",
            "student_profiles",
        ]
        for tbl in tables:
            op.execute(f"DROP POLICY IF EXISTS {tbl}_self ON {tbl}")
            op.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY")

    op.drop_table("domain_events")
    op.drop_table("project_health_history")
    op.drop_table("project_phase_history")
    op.drop_table("project_technologies")
    op.drop_table("project_profiles")
    op.drop_table("project_instances")
    op.drop_table("project_definition_versions")
    op.drop_table("project_definitions")
    op.drop_table("group_memberships")
    op.drop_table("groups")
    op.drop_table("student_technologies")
    op.drop_table("technologies")
    op.drop_table("user_preferences")
    op.drop_table("mentor_profiles")
    op.drop_table("student_profiles")
