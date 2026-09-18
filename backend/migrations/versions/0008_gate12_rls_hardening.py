"""Gate 12: Database security hardening, RLS policy implementation, and index cleanup.

Revision ID: 0008_gate12_rls_hardening
Revises: 0007_gate11_extensions
Create Date: 2026-09-15 UTC

Authorised by: Gate 12 — Database Security Hardening & Advisor Remediation
Architecture ref:
  - docs/security/GROWFLOW_DATABASE_SECURITY_AUDIT.md (v2.0)
  - docs/security/GROWFLOW_AUTHORIZATION_MODEL.md (v1.0)
  - 6D Authentication & Security Architecture § 33-34

Remediation Summary:
  1. Relocate pg_trgm extension to the extensions schema (HYG-02).
  2. Drop 6 confirmed redundant duplicate unique indexes (HYG-01).
  3. Enable Row Level Security (RLS) on remaining 17 tables (SEC-01, SEC-03).
  4. Replace existing 10 policies with InitPlan scalar subquery optimizations (PERF-01).
  5. Install granular, relationship-scoped RLS policies across all domain clusters.
  6. Seal backend-only infrastructure tables (domain_events, alembic_version) against direct PostgREST access.
"""

from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0008_gate12_rls_hardening"
down_revision: str | None = "0007_gate11_extensions"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # =========================================================================
    # PART 1: EXTENSION NAMESPACE REMEDIATION (HYG-02)
    # =========================================================================
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm') THEN
                CREATE SCHEMA IF NOT EXISTS extensions;
                ALTER EXTENSION pg_trgm SET SCHEMA extensions;
            END IF;
        END
        $$;
    """)

    # =========================================================================
    # PART 2: REDUNDANT UNIQUE INDEX CLEANUP (HYG-01)
    # Drops 6 explicit unique indexes that duplicate table-level UNIQUE constraints.
    # The underlying UNIQUE constraints remain fully intact.
    # =========================================================================
    op.execute("DROP INDEX IF EXISTS public.ix_assessments_project_instance_id")
    op.execute("DROP INDEX IF EXISTS public.ix_assessment_results_assessment_id")
    op.execute("DROP INDEX IF EXISTS public.ix_assessment_results_project_instance_id")
    op.execute("DROP INDEX IF EXISTS public.ix_blueprints_project_instance_id")
    op.execute("DROP INDEX IF EXISTS public.ix_project_github_integrations_project_instance_id")
    op.execute("DROP INDEX IF EXISTS public.ix_project_profiles_project_instance_id")

    # =========================================================================
    # PART 3: ENABLE RLS ON REMAINING 17 TABLES (SEC-01, SEC-03)
    # =========================================================================
    tables_to_enable_rls = [
        "alembic_version",
        "assessments",
        "assessment_answers",
        "assessment_results",
        "blueprints",
        "blueprint_jobs",
        "project_milestones",
        "project_tasks",
        "project_risks",
        "project_documents",
        "project_blueprint_versions",
        "project_change_requests",
        "ai_mentor_conversations",
        "ai_mentor_messages",
        "project_github_integrations",
        "project_help_requests",
        "project_mentor_notes",
    ]
    for tbl in tables_to_enable_rls:
        op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY")

    # =========================================================================
    # PART 4: INSTALL AUTHORIZATION CONTRACT POLICIES (SEC-01, SEC-02, PERF-01)
    # Defensively installed only if Supabase 'auth' schema is present.
    # =========================================================================
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN

                -- =============================================================
                -- 4.1 USERS (Identity)
                -- =============================================================
                DROP POLICY IF EXISTS users_self_select ON users;
                CREATE POLICY users_self_select ON users
                    FOR SELECT
                    USING (id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.2 STUDENT_PROFILES
                -- =============================================================
                DROP POLICY IF EXISTS student_profiles_self ON student_profiles;
                DROP POLICY IF EXISTS student_profiles_select ON student_profiles;
                DROP POLICY IF EXISTS student_profiles_insert_self ON student_profiles;
                DROP POLICY IF EXISTS student_profiles_update_self ON student_profiles;

                CREATE POLICY student_profiles_select ON student_profiles
                    FOR SELECT
                    USING (
                        user_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM group_memberships gm
                            JOIN groups g ON g.id = gm.group_id
                            WHERE gm.student_id = student_profiles.user_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                              AND gm.status = 'ACTIVE'
                        )
                    );

                CREATE POLICY student_profiles_insert_self ON student_profiles
                    FOR INSERT
                    WITH CHECK (user_id = (SELECT auth.uid()::text));

                CREATE POLICY student_profiles_update_self ON student_profiles
                    FOR UPDATE
                    USING (user_id = (SELECT auth.uid()::text))
                    WITH CHECK (user_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.3 MENTOR_PROFILES
                -- =============================================================
                DROP POLICY IF EXISTS mentor_profiles_self ON mentor_profiles;
                DROP POLICY IF EXISTS mentor_profiles_select ON mentor_profiles;
                DROP POLICY IF EXISTS mentor_profiles_insert_self ON mentor_profiles;
                DROP POLICY IF EXISTS mentor_profiles_update_self ON mentor_profiles;

                CREATE POLICY mentor_profiles_select ON mentor_profiles
                    FOR SELECT
                    USING ((SELECT auth.role()) = 'authenticated');

                CREATE POLICY mentor_profiles_insert_self ON mentor_profiles
                    FOR INSERT
                    WITH CHECK (user_id = (SELECT auth.uid()::text));

                CREATE POLICY mentor_profiles_update_self ON mentor_profiles
                    FOR UPDATE
                    USING (user_id = (SELECT auth.uid()::text))
                    WITH CHECK (user_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.4 USER_PREFERENCES
                -- =============================================================
                DROP POLICY IF EXISTS user_preferences_self ON user_preferences;
                DROP POLICY IF EXISTS user_preferences_select ON user_preferences;
                DROP POLICY IF EXISTS user_preferences_insert_self ON user_preferences;
                DROP POLICY IF EXISTS user_preferences_update_self ON user_preferences;

                CREATE POLICY user_preferences_select ON user_preferences
                    FOR SELECT
                    USING (user_id = (SELECT auth.uid()::text));

                CREATE POLICY user_preferences_insert_self ON user_preferences
                    FOR INSERT
                    WITH CHECK (user_id = (SELECT auth.uid()::text));

                CREATE POLICY user_preferences_update_self ON user_preferences
                    FOR UPDATE
                    USING (user_id = (SELECT auth.uid()::text))
                    WITH CHECK (user_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.5 TECHNOLOGIES (Catalog Reference)
                -- =============================================================
                DROP POLICY IF EXISTS technologies_read ON technologies;
                DROP POLICY IF EXISTS technologies_select ON technologies;

                CREATE POLICY technologies_select ON technologies
                    FOR SELECT
                    USING ((SELECT auth.role()) = 'authenticated');

                -- =============================================================
                -- 4.6 STUDENT_TECHNOLOGIES (Skills)
                -- =============================================================
                DROP POLICY IF EXISTS student_technologies_self ON student_technologies;
                DROP POLICY IF EXISTS student_technologies_select ON student_technologies;
                DROP POLICY IF EXISTS student_technologies_insert_student ON student_technologies;
                DROP POLICY IF EXISTS student_technologies_update_student ON student_technologies;
                DROP POLICY IF EXISTS student_technologies_delete_student ON student_technologies;

                CREATE POLICY student_technologies_select ON student_technologies
                    FOR SELECT
                    USING (
                        student_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM group_memberships gm
                            JOIN groups g ON g.id = gm.group_id
                            WHERE gm.student_id = student_technologies.student_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                              AND gm.status = 'ACTIVE'
                        )
                    );

                CREATE POLICY student_technologies_insert_student ON student_technologies
                    FOR INSERT
                    WITH CHECK (student_id = (SELECT auth.uid()::text));

                CREATE POLICY student_technologies_update_student ON student_technologies
                    FOR UPDATE
                    USING (student_id = (SELECT auth.uid()::text))
                    WITH CHECK (student_id = (SELECT auth.uid()::text));

                CREATE POLICY student_technologies_delete_student ON student_technologies
                    FOR DELETE
                    USING (student_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.7 GROUPS
                -- =============================================================
                DROP POLICY IF EXISTS groups_mentor_owner ON groups;
                DROP POLICY IF EXISTS groups_select ON groups;
                DROP POLICY IF EXISTS groups_insert_mentor ON groups;
                DROP POLICY IF EXISTS groups_update_mentor ON groups;
                DROP POLICY IF EXISTS groups_delete_mentor ON groups;

                CREATE POLICY groups_select ON groups
                    FOR SELECT
                    USING (
                        mentor_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM group_memberships gm
                            WHERE gm.group_id = groups.id
                              AND gm.student_id = (SELECT auth.uid()::text)
                              AND gm.status = 'ACTIVE'
                        )
                    );

                CREATE POLICY groups_insert_mentor ON groups
                    FOR INSERT
                    WITH CHECK (mentor_id = (SELECT auth.uid()::text));

                CREATE POLICY groups_update_mentor ON groups
                    FOR UPDATE
                    USING (mentor_id = (SELECT auth.uid()::text))
                    WITH CHECK (mentor_id = (SELECT auth.uid()::text));

                CREATE POLICY groups_delete_mentor ON groups
                    FOR DELETE
                    USING (mentor_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.8 GROUP_MEMBERSHIPS
                -- =============================================================
                DROP POLICY IF EXISTS group_memberships_participant ON group_memberships;
                DROP POLICY IF EXISTS group_memberships_select ON group_memberships;
                DROP POLICY IF EXISTS group_memberships_insert_student ON group_memberships;
                DROP POLICY IF EXISTS group_memberships_update ON group_memberships;
                DROP POLICY IF EXISTS group_memberships_delete_mentor ON group_memberships;

                CREATE POLICY group_memberships_select ON group_memberships
                    FOR SELECT
                    USING (
                        student_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM groups g
                            WHERE g.id = group_memberships.group_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY group_memberships_insert_student ON group_memberships
                    FOR INSERT
                    WITH CHECK (student_id = (SELECT auth.uid()::text));

                CREATE POLICY group_memberships_update ON group_memberships
                    FOR UPDATE
                    USING (
                        student_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM groups g
                            WHERE g.id = group_memberships.group_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        )
                    )
                    WITH CHECK (
                        student_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM groups g
                            WHERE g.id = group_memberships.group_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY group_memberships_delete_mentor ON group_memberships
                    FOR DELETE
                    USING (
                        EXISTS (
                            SELECT 1 FROM groups g
                            WHERE g.id = group_memberships.group_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.9 PROJECT_DEFINITIONS (Catalog Templates)
                -- =============================================================
                DROP POLICY IF EXISTS project_definitions_owner ON project_definitions;
                DROP POLICY IF EXISTS project_definitions_select ON project_definitions;
                DROP POLICY IF EXISTS project_definitions_insert_mentor ON project_definitions;
                DROP POLICY IF EXISTS project_definitions_update_mentor ON project_definitions;
                DROP POLICY IF EXISTS project_definitions_delete_mentor ON project_definitions;

                CREATE POLICY project_definitions_select ON project_definitions
                    FOR SELECT
                    USING (
                        owner_mentor_id = (SELECT auth.uid()::text) OR
                        status = 'ACTIVE'
                    );

                CREATE POLICY project_definitions_insert_mentor ON project_definitions
                    FOR INSERT
                    WITH CHECK (owner_mentor_id = (SELECT auth.uid()::text));

                CREATE POLICY project_definitions_update_mentor ON project_definitions
                    FOR UPDATE
                    USING (owner_mentor_id = (SELECT auth.uid()::text))
                    WITH CHECK (owner_mentor_id = (SELECT auth.uid()::text));

                CREATE POLICY project_definitions_delete_mentor ON project_definitions
                    FOR DELETE
                    USING (owner_mentor_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.10 PROJECT_DEFINITION_VERSIONS
                -- =============================================================
                DROP POLICY IF EXISTS project_definition_versions_select ON project_definition_versions;
                DROP POLICY IF EXISTS project_definition_versions_insert_mentor ON project_definition_versions;

                CREATE POLICY project_definition_versions_select ON project_definition_versions
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_definitions pd
                            WHERE pd.id = project_definition_versions.project_definition_id
                              AND (pd.owner_mentor_id = (SELECT auth.uid()::text) OR pd.status = 'ACTIVE')
                        )
                    );

                CREATE POLICY project_definition_versions_insert_mentor ON project_definition_versions
                    FOR INSERT
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_definitions pd
                            WHERE pd.id = project_definition_versions.project_definition_id
                              AND pd.owner_mentor_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.11 PROJECT_INSTANCES (Central Project Anchor)
                -- =============================================================
                DROP POLICY IF EXISTS project_instances_access ON project_instances;
                DROP POLICY IF EXISTS project_instances_select ON project_instances;
                DROP POLICY IF EXISTS project_instances_insert_student ON project_instances;
                DROP POLICY IF EXISTS project_instances_update_student ON project_instances;

                CREATE POLICY project_instances_select ON project_instances
                    FOR SELECT
                    USING (
                        student_id = (SELECT auth.uid()::text) OR
                        (group_id IS NOT NULL AND EXISTS (
                            SELECT 1 FROM groups g
                            WHERE g.id = project_instances.group_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        ))
                    );

                CREATE POLICY project_instances_insert_student ON project_instances
                    FOR INSERT
                    WITH CHECK (student_id = (SELECT auth.uid()::text));

                CREATE POLICY project_instances_update_student ON project_instances
                    FOR UPDATE
                    USING (student_id = (SELECT auth.uid()::text))
                    WITH CHECK (student_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.12 PROJECT_PROFILES
                -- =============================================================
                DROP POLICY IF EXISTS project_profiles_select ON project_profiles;
                DROP POLICY IF EXISTS project_profiles_insert_student ON project_profiles;
                DROP POLICY IF EXISTS project_profiles_update_student ON project_profiles;

                CREATE POLICY project_profiles_select ON project_profiles
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_profiles.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                CREATE POLICY project_profiles_insert_student ON project_profiles
                    FOR INSERT
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_profiles.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_profiles_update_student ON project_profiles
                    FOR UPDATE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_profiles.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    )
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_profiles.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.13 PROJECT_TECHNOLOGIES
                -- =============================================================
                DROP POLICY IF EXISTS project_technologies_select ON project_technologies;
                DROP POLICY IF EXISTS project_technologies_insert_student ON project_technologies;
                DROP POLICY IF EXISTS project_technologies_update_student ON project_technologies;
                DROP POLICY IF EXISTS project_technologies_delete_student ON project_technologies;

                CREATE POLICY project_technologies_select ON project_technologies
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_technologies.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                CREATE POLICY project_technologies_insert_student ON project_technologies
                    FOR INSERT
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_technologies.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_technologies_update_student ON project_technologies
                    FOR UPDATE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_technologies.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    )
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_technologies.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_technologies_delete_student ON project_technologies
                    FOR DELETE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_technologies.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.14 PROJECT_PHASE_HISTORY & PROJECT_HEALTH_HISTORY (Audit Logs)
                -- =============================================================
                DROP POLICY IF EXISTS project_phase_history_select ON project_phase_history;
                DROP POLICY IF EXISTS project_health_history_select ON project_health_history;

                CREATE POLICY project_phase_history_select ON project_phase_history
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_phase_history.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                CREATE POLICY project_health_history_select ON project_health_history
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_health_history.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                -- =============================================================
                -- 4.15 ASSESSMENTS
                -- =============================================================
                DROP POLICY IF EXISTS assessments_select ON assessments;
                DROP POLICY IF EXISTS assessments_insert_student ON assessments;
                DROP POLICY IF EXISTS assessments_update_student ON assessments;

                CREATE POLICY assessments_select ON assessments
                    FOR SELECT
                    USING (
                        student_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            JOIN groups g ON g.id = pi.group_id
                            WHERE pi.id = assessments.project_instance_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY assessments_insert_student ON assessments
                    FOR INSERT
                    WITH CHECK (
                        student_id = (SELECT auth.uid()::text) AND
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = assessments.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY assessments_update_student ON assessments
                    FOR UPDATE
                    USING (student_id = (SELECT auth.uid()::text))
                    WITH CHECK (student_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.16 ASSESSMENT_ANSWERS (Private Student Reflection; Mentor Denied)
                -- =============================================================
                DROP POLICY IF EXISTS assessment_answers_select_student ON assessment_answers;
                DROP POLICY IF EXISTS assessment_answers_insert_student ON assessment_answers;
                DROP POLICY IF EXISTS assessment_answers_update_student ON assessment_answers;

                CREATE POLICY assessment_answers_select_student ON assessment_answers
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM assessments a
                            WHERE a.id = assessment_answers.assessment_id
                              AND a.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY assessment_answers_insert_student ON assessment_answers
                    FOR INSERT
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM assessments a
                            WHERE a.id = assessment_answers.assessment_id
                              AND a.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY assessment_answers_update_student ON assessment_answers
                    FOR UPDATE
                    USING (
                        EXISTS (
                            SELECT 1 FROM assessments a
                            WHERE a.id = assessment_answers.assessment_id
                              AND a.student_id = (SELECT auth.uid()::text)
                        )
                    )
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM assessments a
                            WHERE a.id = assessment_answers.assessment_id
                              AND a.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.17 ASSESSMENT_RESULTS (Diagnostic Evaluation; Read-Only)
                -- =============================================================
                DROP POLICY IF EXISTS assessment_results_select ON assessment_results;

                CREATE POLICY assessment_results_select ON assessment_results
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = assessment_results.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                -- =============================================================
                -- 4.18 BLUEPRINTS
                -- =============================================================
                DROP POLICY IF EXISTS blueprints_select ON blueprints;
                DROP POLICY IF EXISTS blueprints_insert_student ON blueprints;
                DROP POLICY IF EXISTS blueprints_update_student ON blueprints;

                CREATE POLICY blueprints_select ON blueprints
                    FOR SELECT
                    USING (
                        student_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            JOIN groups g ON g.id = pi.group_id
                            WHERE pi.id = blueprints.project_instance_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY blueprints_insert_student ON blueprints
                    FOR INSERT
                    WITH CHECK (
                        student_id = (SELECT auth.uid()::text) AND
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = blueprints.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY blueprints_update_student ON blueprints
                    FOR UPDATE
                    USING (student_id = (SELECT auth.uid()::text))
                    WITH CHECK (student_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.19 BLUEPRINT_JOBS (Worker Progress; Read-Only for Clients)
                -- =============================================================
                DROP POLICY IF EXISTS blueprint_jobs_select ON blueprint_jobs;

                CREATE POLICY blueprint_jobs_select ON blueprint_jobs
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = blueprint_jobs.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                -- =============================================================
                -- 4.20 PROJECT_MILESTONES (Execution Management)
                -- =============================================================
                DROP POLICY IF EXISTS project_milestones_select ON project_milestones;
                DROP POLICY IF EXISTS project_milestones_insert_student ON project_milestones;
                DROP POLICY IF EXISTS project_milestones_update_student ON project_milestones;
                DROP POLICY IF EXISTS project_milestones_delete_student ON project_milestones;

                CREATE POLICY project_milestones_select ON project_milestones
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_milestones.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                CREATE POLICY project_milestones_insert_student ON project_milestones
                    FOR INSERT
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_milestones.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_milestones_update_student ON project_milestones
                    FOR UPDATE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_milestones.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    )
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_milestones.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_milestones_delete_student ON project_milestones
                    FOR DELETE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_milestones.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.21 PROJECT_TASKS (Execution Management)
                -- =============================================================
                DROP POLICY IF EXISTS project_tasks_select ON project_tasks;
                DROP POLICY IF EXISTS project_tasks_insert_student ON project_tasks;
                DROP POLICY IF EXISTS project_tasks_update_student ON project_tasks;
                DROP POLICY IF EXISTS project_tasks_delete_student ON project_tasks;

                CREATE POLICY project_tasks_select ON project_tasks
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_tasks.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                CREATE POLICY project_tasks_insert_student ON project_tasks
                    FOR INSERT
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_tasks.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_tasks_update_student ON project_tasks
                    FOR UPDATE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_tasks.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    )
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_tasks.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_tasks_delete_student ON project_tasks
                    FOR DELETE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_tasks.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.22 PROJECT_RISKS (Execution Management)
                -- =============================================================
                DROP POLICY IF EXISTS project_risks_select ON project_risks;
                DROP POLICY IF EXISTS project_risks_insert_student ON project_risks;
                DROP POLICY IF EXISTS project_risks_update_student ON project_risks;
                DROP POLICY IF EXISTS project_risks_delete_student ON project_risks;

                CREATE POLICY project_risks_select ON project_risks
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_risks.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                CREATE POLICY project_risks_insert_student ON project_risks
                    FOR INSERT
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_risks.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_risks_update_student ON project_risks
                    FOR UPDATE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_risks.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    )
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_risks.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_risks_delete_student ON project_risks
                    FOR DELETE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_risks.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.23 PROJECT_DOCUMENTS (Execution Management)
                -- =============================================================
                DROP POLICY IF EXISTS project_documents_select ON project_documents;
                DROP POLICY IF EXISTS project_documents_insert_student ON project_documents;
                DROP POLICY IF EXISTS project_documents_update_student ON project_documents;
                DROP POLICY IF EXISTS project_documents_delete_student ON project_documents;

                CREATE POLICY project_documents_select ON project_documents
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_documents.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                CREATE POLICY project_documents_insert_student ON project_documents
                    FOR INSERT
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_documents.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_documents_update_student ON project_documents
                    FOR UPDATE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_documents.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    )
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_documents.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_documents_delete_student ON project_documents
                    FOR DELETE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_documents.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.24 PROJECT_GITHUB_INTEGRATIONS (VCS Integration)
                -- =============================================================
                DROP POLICY IF EXISTS project_github_integrations_select ON project_github_integrations;
                DROP POLICY IF EXISTS project_github_integrations_insert_student ON project_github_integrations;
                DROP POLICY IF EXISTS project_github_integrations_update_student ON project_github_integrations;
                DROP POLICY IF EXISTS project_github_integrations_delete_student ON project_github_integrations;

                CREATE POLICY project_github_integrations_select ON project_github_integrations
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_github_integrations.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                CREATE POLICY project_github_integrations_insert_student ON project_github_integrations
                    FOR INSERT
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_github_integrations.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_github_integrations_update_student ON project_github_integrations
                    FOR UPDATE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_github_integrations.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    )
                    WITH CHECK (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_github_integrations.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_github_integrations_delete_student ON project_github_integrations
                    FOR DELETE
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_github_integrations.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.25 PROJECT_BLUEPRINT_VERSIONS (Version Snapshots; Read-Only)
                -- =============================================================
                DROP POLICY IF EXISTS project_blueprint_versions_select ON project_blueprint_versions;

                CREATE POLICY project_blueprint_versions_select ON project_blueprint_versions
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_blueprint_versions.project_instance_id
                              AND (
                                  pi.student_id = (SELECT auth.uid()::text) OR
                                  (pi.group_id IS NOT NULL AND EXISTS (
                                      SELECT 1 FROM groups g
                                      WHERE g.id = pi.group_id
                                        AND g.mentor_id = (SELECT auth.uid()::text)
                                  ))
                              )
                        )
                    );

                -- =============================================================
                -- 4.26 PROJECT_CHANGE_REQUESTS
                -- =============================================================
                DROP POLICY IF EXISTS project_change_requests_select ON project_change_requests;
                DROP POLICY IF EXISTS project_change_requests_insert_student ON project_change_requests;
                DROP POLICY IF EXISTS project_change_requests_update_student ON project_change_requests;

                CREATE POLICY project_change_requests_select ON project_change_requests
                    FOR SELECT
                    USING (
                        student_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            JOIN groups g ON g.id = pi.group_id
                            WHERE pi.id = project_change_requests.project_instance_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_change_requests_insert_student ON project_change_requests
                    FOR INSERT
                    WITH CHECK (
                        student_id = (SELECT auth.uid()::text) AND
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_change_requests.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_change_requests_update_student ON project_change_requests
                    FOR UPDATE
                    USING (student_id = (SELECT auth.uid()::text))
                    WITH CHECK (student_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.27 AI_MENTOR_CONVERSATIONS (Private Consultation; Mentor Denied)
                -- =============================================================
                DROP POLICY IF EXISTS ai_mentor_conversations_select_student ON ai_mentor_conversations;
                DROP POLICY IF EXISTS ai_mentor_conversations_insert_student ON ai_mentor_conversations;

                CREATE POLICY ai_mentor_conversations_select_student ON ai_mentor_conversations
                    FOR SELECT
                    USING (student_id = (SELECT auth.uid()::text));

                CREATE POLICY ai_mentor_conversations_insert_student ON ai_mentor_conversations
                    FOR INSERT
                    WITH CHECK (
                        student_id = (SELECT auth.uid()::text) AND
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = ai_mentor_conversations.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.28 AI_MENTOR_MESSAGES (Private Messages; Student User Role Only)
                -- =============================================================
                DROP POLICY IF EXISTS ai_mentor_messages_select_student ON ai_mentor_messages;
                DROP POLICY IF EXISTS ai_mentor_messages_insert_student ON ai_mentor_messages;

                CREATE POLICY ai_mentor_messages_select_student ON ai_mentor_messages
                    FOR SELECT
                    USING (
                        EXISTS (
                            SELECT 1 FROM ai_mentor_conversations c
                            WHERE c.id = ai_mentor_messages.conversation_id
                              AND c.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY ai_mentor_messages_insert_student ON ai_mentor_messages
                    FOR INSERT
                    WITH CHECK (
                        role = 'user' AND
                        EXISTS (
                            SELECT 1 FROM ai_mentor_conversations c
                            WHERE c.id = ai_mentor_messages.conversation_id
                              AND c.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- =============================================================
                -- 4.29 PROJECT_HELP_REQUESTS
                -- =============================================================
                DROP POLICY IF EXISTS project_help_requests_select ON project_help_requests;
                DROP POLICY IF EXISTS project_help_requests_insert_student ON project_help_requests;
                DROP POLICY IF EXISTS project_help_requests_update_student ON project_help_requests;

                CREATE POLICY project_help_requests_select ON project_help_requests
                    FOR SELECT
                    USING (
                        student_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            JOIN groups g ON g.id = pi.group_id
                            WHERE pi.id = project_help_requests.project_instance_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_help_requests_insert_student ON project_help_requests
                    FOR INSERT
                    WITH CHECK (
                        student_id = (SELECT auth.uid()::text) AND
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_help_requests.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                CREATE POLICY project_help_requests_update_student ON project_help_requests
                    FOR UPDATE
                    USING (student_id = (SELECT auth.uid()::text))
                    WITH CHECK (student_id = (SELECT auth.uid()::text));

                -- =============================================================
                -- 4.30 PROJECT_MENTOR_NOTES
                -- =============================================================
                DROP POLICY IF EXISTS project_mentor_notes_select_student ON project_mentor_notes;
                DROP POLICY IF EXISTS project_mentor_notes_select_mentor ON project_mentor_notes;
                DROP POLICY IF EXISTS project_mentor_notes_insert_mentor ON project_mentor_notes;
                DROP POLICY IF EXISTS project_mentor_notes_update_mentor ON project_mentor_notes;
                DROP POLICY IF EXISTS project_mentor_notes_delete_mentor ON project_mentor_notes;

                -- Students may only read non-INTERNAL notes on own projects
                CREATE POLICY project_mentor_notes_select_student ON project_mentor_notes
                    FOR SELECT
                    USING (
                        note_type != 'INTERNAL' AND
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            WHERE pi.id = project_mentor_notes.project_instance_id
                              AND pi.student_id = (SELECT auth.uid()::text)
                        )
                    );

                -- Mentors can view notes on supervised projects
                CREATE POLICY project_mentor_notes_select_mentor ON project_mentor_notes
                    FOR SELECT
                    USING (
                        mentor_id = (SELECT auth.uid()::text) OR
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            JOIN groups g ON g.id = pi.group_id
                            WHERE pi.id = project_mentor_notes.project_instance_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        )
                    );

                -- Mentors create notes on supervised projects
                CREATE POLICY project_mentor_notes_insert_mentor ON project_mentor_notes
                    FOR INSERT
                    WITH CHECK (
                        mentor_id = (SELECT auth.uid()::text) AND
                        EXISTS (
                            SELECT 1 FROM project_instances pi
                            JOIN groups g ON g.id = pi.group_id
                            WHERE pi.id = project_mentor_notes.project_instance_id
                              AND g.mentor_id = (SELECT auth.uid()::text)
                        )
                    );

                -- Mentors update own authored notes
                CREATE POLICY project_mentor_notes_update_mentor ON project_mentor_notes
                    FOR UPDATE
                    USING (mentor_id = (SELECT auth.uid()::text))
                    WITH CHECK (mentor_id = (SELECT auth.uid()::text));

                -- Mentors delete own authored notes
                CREATE POLICY project_mentor_notes_delete_mentor ON project_mentor_notes
                    FOR DELETE
                    USING (mentor_id = (SELECT auth.uid()::text));

            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # 1. Drop all policies created or updated in this migration
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN
                -- Users
                DROP POLICY IF EXISTS users_self_select ON users;

                -- Profiles & Preferences
                DROP POLICY IF EXISTS student_profiles_select ON student_profiles;
                DROP POLICY IF EXISTS student_profiles_insert_self ON student_profiles;
                DROP POLICY IF EXISTS student_profiles_update_self ON student_profiles;
                DROP POLICY IF EXISTS mentor_profiles_select ON mentor_profiles;
                DROP POLICY IF EXISTS mentor_profiles_insert_self ON mentor_profiles;
                DROP POLICY IF EXISTS mentor_profiles_update_self ON mentor_profiles;
                DROP POLICY IF EXISTS user_preferences_select ON user_preferences;
                DROP POLICY IF EXISTS user_preferences_insert_self ON user_preferences;
                DROP POLICY IF EXISTS user_preferences_update_self ON user_preferences;

                -- Technologies & Skills
                DROP POLICY IF EXISTS technologies_select ON technologies;
                DROP POLICY IF EXISTS student_technologies_select ON student_technologies;
                DROP POLICY IF EXISTS student_technologies_insert_student ON student_technologies;
                DROP POLICY IF EXISTS student_technologies_update_student ON student_technologies;
                DROP POLICY IF EXISTS student_technologies_delete_student ON student_technologies;

                -- Groups & Memberships
                DROP POLICY IF EXISTS groups_select ON groups;
                DROP POLICY IF EXISTS groups_insert_mentor ON groups;
                DROP POLICY IF EXISTS groups_update_mentor ON groups;
                DROP POLICY IF EXISTS groups_delete_mentor ON groups;
                DROP POLICY IF EXISTS group_memberships_select ON group_memberships;
                DROP POLICY IF EXISTS group_memberships_insert_student ON group_memberships;
                DROP POLICY IF EXISTS group_memberships_update ON group_memberships;
                DROP POLICY IF EXISTS group_memberships_delete_mentor ON group_memberships;

                -- Project Definitions
                DROP POLICY IF EXISTS project_definitions_select ON project_definitions;
                DROP POLICY IF EXISTS project_definitions_insert_mentor ON project_definitions;
                DROP POLICY IF EXISTS project_definitions_update_mentor ON project_definitions;
                DROP POLICY IF EXISTS project_definitions_delete_mentor ON project_definitions;
                DROP POLICY IF EXISTS project_definition_versions_select ON project_definition_versions;
                DROP POLICY IF EXISTS project_definition_versions_insert_mentor ON project_definition_versions;

                -- Project Core
                DROP POLICY IF EXISTS project_instances_select ON project_instances;
                DROP POLICY IF EXISTS project_instances_insert_student ON project_instances;
                DROP POLICY IF EXISTS project_instances_update_student ON project_instances;
                DROP POLICY IF EXISTS project_profiles_select ON project_profiles;
                DROP POLICY IF EXISTS project_profiles_insert_student ON project_profiles;
                DROP POLICY IF EXISTS project_profiles_update_student ON project_profiles;
                DROP POLICY IF EXISTS project_technologies_select ON project_technologies;
                DROP POLICY IF EXISTS project_technologies_insert_student ON project_technologies;
                DROP POLICY IF EXISTS project_technologies_update_student ON project_technologies;
                DROP POLICY IF EXISTS project_technologies_delete_student ON project_technologies;
                DROP POLICY IF EXISTS project_phase_history_select ON project_phase_history;
                DROP POLICY IF EXISTS project_health_history_select ON project_health_history;

                -- Assessments
                DROP POLICY IF EXISTS assessments_select ON assessments;
                DROP POLICY IF EXISTS assessments_insert_student ON assessments;
                DROP POLICY IF EXISTS assessments_update_student ON assessments;
                DROP POLICY IF EXISTS assessment_answers_select_student ON assessment_answers;
                DROP POLICY IF EXISTS assessment_answers_insert_student ON assessment_answers;
                DROP POLICY IF EXISTS assessment_answers_update_student ON assessment_answers;
                DROP POLICY IF EXISTS assessment_results_select ON assessment_results;

                -- Blueprints
                DROP POLICY IF EXISTS blueprints_select ON blueprints;
                DROP POLICY IF EXISTS blueprints_insert_student ON blueprints;
                DROP POLICY IF EXISTS blueprints_update_student ON blueprints;
                DROP POLICY IF EXISTS blueprint_jobs_select ON blueprint_jobs;

                -- Execution Management
                DROP POLICY IF EXISTS project_milestones_select ON project_milestones;
                DROP POLICY IF EXISTS project_milestones_insert_student ON project_milestones;
                DROP POLICY IF EXISTS project_milestones_update_student ON project_milestones;
                DROP POLICY IF EXISTS project_milestones_delete_student ON project_milestones;
                DROP POLICY IF EXISTS project_tasks_select ON project_tasks;
                DROP POLICY IF EXISTS project_tasks_insert_student ON project_tasks;
                DROP POLICY IF EXISTS project_tasks_update_student ON project_tasks;
                DROP POLICY IF EXISTS project_tasks_delete_student ON project_tasks;
                DROP POLICY IF EXISTS project_risks_select ON project_risks;
                DROP POLICY IF EXISTS project_risks_insert_student ON project_risks;
                DROP POLICY IF EXISTS project_risks_update_student ON project_risks;
                DROP POLICY IF EXISTS project_risks_delete_student ON project_risks;
                DROP POLICY IF EXISTS project_documents_select ON project_documents;
                DROP POLICY IF EXISTS project_documents_insert_student ON project_documents;
                DROP POLICY IF EXISTS project_documents_update_student ON project_documents;
                DROP POLICY IF EXISTS project_documents_delete_student ON project_documents;

                -- Extensions
                DROP POLICY IF EXISTS project_github_integrations_select ON project_github_integrations;
                DROP POLICY IF EXISTS project_github_integrations_insert_student ON project_github_integrations;
                DROP POLICY IF EXISTS project_github_integrations_update_student ON project_github_integrations;
                DROP POLICY IF EXISTS project_github_integrations_delete_student ON project_github_integrations;
                DROP POLICY IF EXISTS project_blueprint_versions_select ON project_blueprint_versions;
                DROP POLICY IF EXISTS project_change_requests_select ON project_change_requests;
                DROP POLICY IF EXISTS project_change_requests_insert_student ON project_change_requests;
                DROP POLICY IF EXISTS project_change_requests_update_student ON project_change_requests;

                -- AI Mentor
                DROP POLICY IF EXISTS ai_mentor_conversations_select_student ON ai_mentor_conversations;
                DROP POLICY IF EXISTS ai_mentor_conversations_insert_student ON ai_mentor_conversations;
                DROP POLICY IF EXISTS ai_mentor_messages_select_student ON ai_mentor_messages;
                DROP POLICY IF EXISTS ai_mentor_messages_insert_student ON ai_mentor_messages;

                -- Help Requests & Mentor Notes
                DROP POLICY IF EXISTS project_help_requests_select ON project_help_requests;
                DROP POLICY IF EXISTS project_help_requests_insert_student ON project_help_requests;
                DROP POLICY IF EXISTS project_help_requests_update_student ON project_help_requests;
                DROP POLICY IF EXISTS project_mentor_notes_select_student ON project_mentor_notes;
                DROP POLICY IF EXISTS project_mentor_notes_select_mentor ON project_mentor_notes;
                DROP POLICY IF EXISTS project_mentor_notes_insert_mentor ON project_mentor_notes;
                DROP POLICY IF EXISTS project_mentor_notes_update_mentor ON project_mentor_notes;
                DROP POLICY IF EXISTS project_mentor_notes_delete_mentor ON project_mentor_notes;

                -- Reinstall original 0002 / 0003 baseline policies
                CREATE POLICY users_self_select ON users
                    FOR SELECT USING (id = auth.uid()::text);
                CREATE POLICY student_profiles_self ON student_profiles
                    FOR ALL USING (user_id = auth.uid()::text);
                CREATE POLICY mentor_profiles_self ON mentor_profiles
                    FOR ALL USING (user_id = auth.uid()::text);
                CREATE POLICY user_preferences_self ON user_preferences
                    FOR ALL USING (user_id = auth.uid()::text);
                CREATE POLICY student_technologies_self ON student_technologies
                    FOR ALL USING (student_id = auth.uid()::text);
                CREATE POLICY technologies_read ON technologies
                    FOR SELECT USING (auth.role() = 'authenticated');
                CREATE POLICY groups_mentor_owner ON groups
                    FOR ALL USING (mentor_id = auth.uid()::text);
                CREATE POLICY group_memberships_participant ON group_memberships
                    FOR ALL USING (
                        student_id = auth.uid()::text OR
                        EXISTS (SELECT 1 FROM groups WHERE groups.id = group_memberships.group_id AND groups.mentor_id = auth.uid()::text)
                    );
                CREATE POLICY project_definitions_owner ON project_definitions
                    FOR ALL USING (owner_mentor_id = auth.uid()::text);
                CREATE POLICY project_instances_access ON project_instances
                    FOR ALL USING (
                        student_id = auth.uid()::text OR
                        (group_id IS NOT NULL AND EXISTS (SELECT 1 FROM groups WHERE groups.id = project_instances.group_id AND groups.mentor_id = auth.uid()::text))
                    );
            END IF;
        END
        $$;
    """)

    # 2. Disable RLS on the 17 tables where it was newly enabled
    tables_to_disable = [
        "project_mentor_notes",
        "project_help_requests",
        "project_github_integrations",
        "ai_mentor_messages",
        "ai_mentor_conversations",
        "project_change_requests",
        "project_blueprint_versions",
        "project_documents",
        "project_risks",
        "project_tasks",
        "project_milestones",
        "blueprint_jobs",
        "blueprints",
        "assessment_results",
        "assessment_answers",
        "assessments",
        "alembic_version",
    ]
    for tbl in tables_to_disable:
        op.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY")

    # 3. Re-create the 6 dropped redundant unique indexes
    op.create_index(
        "ix_project_profiles_project_instance_id",
        "project_profiles",
        ["project_instance_id"],
        unique=True,
    )
    op.create_index(
        "ix_project_github_integrations_project_instance_id",
        "project_github_integrations",
        ["project_instance_id"],
        unique=True,
    )
    op.create_index(
        "ix_blueprints_project_instance_id",
        "blueprints",
        ["project_instance_id"],
        unique=True,
    )
    op.create_index(
        "ix_assessment_results_project_instance_id",
        "assessment_results",
        ["project_instance_id"],
        unique=True,
    )
    op.create_index(
        "ix_assessment_results_assessment_id",
        "assessment_results",
        ["assessment_id"],
        unique=True,
    )
    op.create_index(
        "ix_assessments_project_instance_id",
        "assessments",
        ["project_instance_id"],
        unique=True,
    )

    # 4. Revert pg_trgm back to public schema
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm') THEN
                ALTER EXTENSION pg_trgm SET SCHEMA public;
            END IF;
        END
        $$;
    """)
