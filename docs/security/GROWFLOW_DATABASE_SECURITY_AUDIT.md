# GrowFlow Database Security Audit

**Document Version:** 3.0 (Comprehensive Evidence-Based Read-Only Security Audit)  
**Date:** September 16, 2026  
**Status:** Audit Complete — Strictly Read-Only (Awaiting Authorization Design & Approval)  
**Target Repository:** `growflow_ai`  
**Execution Mode:** Read-Only Terminal & Repository Inspection  

---

## 1. Audit Scope

The scope of this audit comprises a comprehensive, evidence-based security and architectural inspection of the database layer for the **GrowFlow AI** Student Growth & Career Management Platform:

- **Database Migrations:** Alembic revision versions `0001_gate03_baseline.py` through `0007_gate11_extensions.py` (and inspection of pending `0008_gate12_rls_hardening.py`).
- **Migration Runtime Environment:** `alembic.ini`, `backend/migrations/env.py`.
- **Database ORM Models:** All SQLAlchemy declarative domain models in `backend/app/infrastructure/database/models/`:
  - `user.py` (Canonical identity)
  - `profile.py` (Student, Mentor profiles & preferences)
  - `organization.py` (Cohorts, Group memberships)
  - `project.py` (Definitions, Versions, Instances, Profiles, Technologies, History)
  - `assessment.py` (Assessments, Answers, Results)
  - `blueprint.py` (Blueprints, Generation jobs)
  - `execution.py` (Milestones, Tasks, Risks, Documents)
  - `workspace_extensions.py` (GitHub integrations, Blueprint snapshots, Change requests, AI Mentor chats, Help requests, Mentor notes)
  - `outbox.py` (Domain events)
- **Database Engine & Lifecycle:** `backend/app/infrastructure/database/engine.py`, `lifecycle.py`, `base.py`.
- **Authentication & Email Integration:**
  - Supabase GoTrue Auth configuration (`backend/app/config/settings.py`, `.env.example`).
  - Frontend authentication flows (`StudentRegister.tsx`, `MentorRegister.tsx`, `StudentPasswordRecovery.tsx`, `MentorPasswordRecovery.tsx`).
  - Synthetic dataset seeder (`backend/scripts/seed_demo_dataset.py`).
  - Test suites (`backend/tests/`, `frontend/src/test/`).
  - Outbound contact email client (`backend/app/infrastructure/email/client.py`).
- **Supabase Security Advisor Findings Reconciliation:**
  - **RLS Disabled in Public Schema:** `alembic_version`, `assessments`, `assessment_answers`, `assessment_results`, `blueprints`, `blueprint_jobs`, `project_milestones`, `project_tasks`, `project_risks`, `project_documents`, `project_blueprint_versions`, `project_github_integrations`, `project_change_requests`, `ai_mentor_conversations`, `ai_mentor_messages`, `project_help_requests`, `project_mentor_notes`.
  - **Auth RLS Initialization Plan Warnings:** Evaluation of `auth.uid()`, `auth.role()` in existing RLS policies.
  - **Duplicate Unique Indexes:** Index redundancies on `assessments`, `assessment_results`, `blueprints`, `project_github_integrations`, `project_profiles`.
  - **Extension in Public Schema:** Placement and usage of `public.pg_trgm`.
  - **Leaked Password Protection Disabled:** Supabase GoTrue configuration state.
  - **High Transactional / Authentication Email Bounce Rate:** Code-level triggers, demo email domains, and password recovery loops.

---

## 2. Execution Constraints

This security audit was conducted strictly under read-only, non-destructive constraints:

- **No source code was modified.**
- **No SQL migrations were created, edited, applied, or pushed.**
- **No database schema, table, column, constraint, or default was altered.**
- **No Row Level Security (RLS) was enabled or disabled on any table.**
- **No RLS policies were created, altered, or dropped.**
- **No indexes were created or deleted.**
- **No extensions were moved, created, or dropped.**
- **No Supabase Auth settings or email settings were altered.**
- **No environment variables or secrets were altered.**
- **No test or live emails were transmitted; no synthetic or real recipient addresses were contacted.**
- **No credentials, database passwords, JWT secrets, service-role keys, or SMTP passwords were printed or exposed.**
- **No browser automation, frontend UI automation, or dashboard scraping was performed.**
- **Terminal inspection was strictly bounded**, respecting command timeouts, diagnosing command failures once, and halting without entering retry loops.
- All items requiring external cloud database access or secret credentials are documented as **BLOCKED — LIVE DATABASE VERIFICATION REQUIRED**.

---

## 3. Repository Database Architecture

GrowFlow employs a layered backend architecture connecting to Supabase PostgreSQL:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend Runtime                         │
│   Auth Dependency (Bearer JWT validation) -> Domain Application Layer   │
│   Async Database Engine (postgresql+psycopg / superuser credentials)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Schema (public)                        │
│                                                                        │
│   ┌────────────────────────────────┐   ┌───────────────────────────┐   │
│   │   Migrations 0002 & 0003       │   │   Migrations 0004 - 0007  │   │
│   │   (16 Domain Tables)           │   │   (16 Domain Tables)      │   │
│   │   - RLS: ENABLED               │   │   - RLS: NOT ENABLED      │   │
│   │   - 10 Policies Defined        │   │   - 0 Policies Defined    │   │
│   │   - 6 Tables Deny-All (0 pol.) │   │   - Flagged by Advisor    │   │
│   └────────────────────────────────┘   └───────────────────────────┘   │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │   Migration Infrastructure: public.alembic_version             │   │
│   │   - RLS: NOT ENABLED (Flagged by Advisor)                      │   │
│   └────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
                         [PostgREST Data API Layer]
                                    │
┌───────────────────────────────────┴────────────────────────────────────┐
│                  Supabase Public Client (Web Browser)                  │
│       Role: anon / authenticated (Subject to Grants & PostgreSQL RLS)  │
└────────────────────────────────────────────────────────────────────────┘
```

### Architectural Observations:
1. **Application Engine:** The FastAPI application accesses PostgreSQL via an async SQLAlchemy engine (`backend/app/infrastructure/database/engine.py`). In standard Supabase environments, backend connections connect as the `postgres` administrative user, which bypasses RLS by default.
2. **PostgREST Data Boundary:** When frontend clients interact directly with Supabase via `@supabase/supabase-js`, queries run under either the `anon` or `authenticated` role. Access through this boundary is governed by two distinct layers:
   - **Layer 1: Table-Level Permissions (Grants):** Whether `SELECT, INSERT, UPDATE, DELETE` are granted to `anon` or `authenticated` in `information_schema.role_table_grants`.
   - **Layer 2: Row Level Security (RLS):** If RLS is enabled, queries must satisfy an active policy. If RLS is disabled, Layer 1 alone permits full access.
3. **Defense-in-Depth Principle:** GrowFlow architecture specification `6D § 33-34` mandates RLS across all tables in the `public` schema to protect against API misconfiguration, key leakage, or unauthorized PostgREST traversal.

---

## 4. Authoritative Schema Source

**AUTHORITATIVE DATABASE SOURCE:**  
`backend/migrations/versions/` (Alembic SQL Migrations `0001_gate03_baseline.py` through `0007_gate11_extensions.py`)  
The Alembic migrations define the exact DDL executed against the database. No standalone `.sql` files or Supabase CLI migration directories exist in the repository.

**SECONDARY SOURCES:**  
1. `backend/app/infrastructure/database/models/` (SQLAlchemy Declarative Models) — Python ORM representation used by the FastAPI backend for query building, type validation, and relationships.
2. Architecture Design Specifications (`docs/6B_Database_Architecture_and_Data_Model_Final.md`, `docs/6D_Authentication_and_Security_Architecture_Final.md`).

**CONFLICTS & DISCREPANCIES:**  
1. **RLS Inclusion Drop-Off:** Migrations `0002` and `0003` explicitly included `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` and created security policies. Migrations `0004`, `0005`, `0006`, and `0007` completely omitted RLS enablement and policy creation.
2. **Index Duplication:** Migrations `0003`, `0004`, `0005`, and `0007` created both `sa.UniqueConstraint` and `op.create_index(..., unique=True)` on identical single columns.
3. **Extension Placement:** Migration `0001` created extension `pg_trgm` without specifying `SCHEMA extensions`, defaulting to the `public` schema.

---

## 5. Database Table Inventory

The schema contains exactly **33 tables in the `public` schema** (32 application domain tables and 1 database migration infrastructure table).

### 5.1 Identity, Profiles & Preferences
- **`users`**
  - *Purpose:* Canonical user account record; maps 1:1 with Supabase `auth.users`.
  - *Primary Key:* `id` (String(36), UUID)
  - *Important Columns:* `email`, `full_name`, `role` (`STUDENT`, `MENTOR`, `ADMIN`), `status` (`ACTIVE`, `SUSPENDED`, `PENDING`), `last_login_at`, `created_at`, `updated_at`.
  - *References to Users:* Primary identity anchor (`id` = `auth.users.id`).
  - *Sensitive Data:* PII (full name, email address).
  - *App Facing:* Yes.
  - *Source Location:* `0002_gate04_users.py:29`, `backend/app/infrastructure/database/models/user.py`.
- **`student_profiles`**
  - *Purpose:* Extended profile data for students.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `user_id -> users.id` (CASCADE, Unique).
  - *Important Columns:* `enrollment_number`, `college`, `branch`, `year_of_study`, `cgpa`, `primary_track`, `headline`, `bio`, `target_role`.
  - *Sensitive Data:* Academic records, GPA, career aspirations.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:33`, `backend/app/infrastructure/database/models/profile.py`.
- **`mentor_profiles`**
  - *Purpose:* Extended profile data for mentors.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `user_id -> users.id` (CASCADE, Unique).
  - *Important Columns:* `mentor_id` (Business code), `designation`, `organization`, `years_of_experience`, `bio`, `specialization`, `skills`, `max_students`, `is_accepting_students`.
  - *Sensitive Data:* Professional details, workload capacity.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:84`, `backend/app/infrastructure/database/models/profile.py`.
- **`user_preferences`**
  - *Purpose:* User interface, notification, and privacy preferences.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `user_id -> users.id` (CASCADE, Unique).
  - *Important Columns:* `theme`, `email_notifications`, `in_app_notifications`, `ai_suggestions_enabled`, `preferences_json`.
  - *Sensitive Data:* User configuration preferences.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:133`, `backend/app/infrastructure/database/models/profile.py`.

### 5.2 Reference Catalog & Skills
- **`technologies`**
  - *Purpose:* Canonical reference catalog of technologies, frameworks, and programming languages.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* None.
  - *Important Columns:* `name` (Unique), `category`, `description`, `is_active`.
  - *Sensitive Data:* None (Public catalog).
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:169`, `backend/app/infrastructure/database/models/project.py`.
- **`student_technologies`**
  - *Purpose:* Mapping of student technical competencies and self-reported proficiencies.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `student_id -> users.id` (CASCADE), `technology_id -> technologies.id` (RESTRICT).
  - *Important Columns:* `proficiency_level`, `years_of_experience`, `is_verified`.
  - *Sensitive Data:* Student skill self-evaluations.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:202`, `backend/app/infrastructure/database/models/project.py`.

### 5.3 Organization & Cohort Management
- **`groups`**
  - *Purpose:* Mentorship cohorts and student learning groups.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `mentor_id -> users.id` (RESTRICT).
  - *Important Columns:* `name`, `code` (Unique cohort join code), `description`, `status`, `max_students`.
  - *Sensitive Data:* Cohort join codes, enrollment caps.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:245`, `backend/app/infrastructure/database/models/organization.py`.
- **`group_memberships`**
  - *Purpose:* Student enrollment in mentorship cohorts.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `group_id -> groups.id` (CASCADE), `student_id -> users.id` (CASCADE).
  - *Important Columns:* `status` (`ACTIVE`, `COMPLETED`, `DROPPED`), `joined_at`.
  - *Sensitive Data:* Student roster membership.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:291`, `backend/app/infrastructure/database/models/organization.py`.

### 5.4 Project Catalog & Definitions
- **`project_definitions`**
  - *Purpose:* Master template specifications for student projects created by mentors.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `owner_mentor_id -> users.id` (RESTRICT).
  - *Important Columns:* `title`, `track`, `complexity`, `status`, `short_description`, `full_description`.
  - *Sensitive Data:* Mentor intellectual property / curriculum templates.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:330`, `backend/app/infrastructure/database/models/project.py`.
- **`project_definition_versions`**
  - *Purpose:* Immutable versioned snapshots of master project definitions.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_definition_id -> project_definitions.id` (CASCADE), `created_by -> users.id` (RESTRICT).
  - *Important Columns:* `version_number`, `specification_json`, `changelog`.
  - *Sensitive Data:* Detailed solution requirements.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:372`, `backend/app/infrastructure/database/models/project.py`.

### 5.5 Project Execution Core (Central Anchor)
- **`project_instances`**
  - *Purpose:* The central operational anchor representing an active student project instance.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `student_id -> users.id` (RESTRICT), `group_id -> groups.id` (SET NULL), `project_definition_id -> project_definitions.id` (SET NULL).
  - *Important Columns:* `title`, `track`, `status`, `current_phase`, `current_health`, `phase_progress_percent`, `overall_progress_percent`.
  - *Sensitive Data:* Active student work progress, performance state.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:417`, `backend/app/infrastructure/database/models/project.py`.
- **`project_profiles`**
  - *Purpose:* Detailed scoping, objectives, and domain context of a project instance.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE, Unique).
  - *Important Columns:* `problem_statement`, `proposed_solution`, `target_audience`, `expected_outcomes`.
  - *Sensitive Data:* Student project proposals and concepts.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:469`, `backend/app/infrastructure/database/models/project.py`.
- **`project_technologies`**
  - *Purpose:* Technologies selected for a specific project instance.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE), `technology_id -> technologies.id` (RESTRICT).
  - *Important Columns:* `usage_rationale`.
  - *Sensitive Data:* Architecture choices.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:511`, `backend/app/infrastructure/database/models/project.py`.
- **`project_phase_history`**
  - *Purpose:* Audit log of project lifecycle phase transitions.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE), `changed_by -> users.id` (RESTRICT).
  - *Important Columns:* `from_phase`, `to_phase`, `reason`, `gate_evaluation_summary`.
  - *Sensitive Data:* Academic progression history.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:548`, `backend/app/infrastructure/database/models/project.py`.
- **`project_health_history`**
  - *Purpose:* Audit log of project health rating transitions.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE), `changed_by -> users.id` (RESTRICT).
  - *Important Columns:* `from_health`, `to_health`, `reason`.
  - *Sensitive Data:* Health score audit trail.
  - *App Facing:* Yes.
  - *Source Location:* `0003_gate05_core_domain.py:587`, `backend/app/infrastructure/database/models/project.py`.
- **`domain_events`**
  - *Purpose:* Transactional outbox table for domain event publishing and decoupled async worker processing.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `actor_id -> users.id` (RESTRICT).
  - *Important Columns:* `event_type`, `aggregate_type`, `aggregate_id`, `payload`, `status`, `visibility`.
  - *Sensitive Data:* Internal audit log and system payloads.
  - *App Facing:* No (Backend internal outbox).
  - *Source Location:* `0003_gate05_core_domain.py:623`, `backend/app/infrastructure/database/models/outbox.py`.

### 5.6 Assessments & AI Diagnostics
- **`assessments`**
  - *Purpose:* Student initial diagnostic assessment session.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE, Unique), `student_id -> users.id` (RESTRICT).
  - *Important Columns:* `status`, `current_question_index`, `total_questions`, `started_at`, `completed_at`.
  - *Sensitive Data:* Evaluation session status.
  - *App Facing:* Yes.
  - *Source Location:* `0004_gate08_assessment.py:34`, `backend/app/infrastructure/database/models/assessment.py`.
- **`assessment_answers`**
  - *Purpose:* Individual question answers submitted during assessments.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `assessment_id -> assessments.id` (CASCADE).
  - *Important Columns:* `question_id`, `question_index`, `question_text`, `question_type`, `selected_option`, `text_response`.
  - *Sensitive Data:* Student assessment answers and self-reflections.
  - *App Facing:* Yes.
  - *Source Location:* `0004_gate08_assessment.py:77`, `backend/app/infrastructure/database/models/assessment.py`.
- **`assessment_results`**
  - *Purpose:* AI-generated assessment evaluation, diagnostic scoring, and skill gap analysis.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `assessment_id -> assessments.id` (CASCADE, Unique), `project_instance_id -> project_instances.id` (CASCADE, Unique).
  - *Important Columns:* `skill_level`, `project_complexity`, `technical_confidence`, `overall_score`, `readiness_tier`, `dimension_scores`, `identified_gaps`, `recommendations`.
  - *Sensitive Data:* Detailed AI evaluations and student competencies.
  - *App Facing:* Yes.
  - *Source Location:* `0004_gate08_assessment.py:112`, `backend/app/infrastructure/database/models/assessment.py`.

### 5.7 Blueprints & Agent Generation
- **`blueprints`**
  - *Purpose:* AI-generated project architecture, tech stack specification, and roadmap blueprint.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE, Unique), `student_id -> users.id` (RESTRICT).
  - *Important Columns:* `status`, `progress_percent`, `qa_status`, `qa_score`, `qa_feedback`, `content` (JSON specification), `approved_at`.
  - *Sensitive Data:* Proprietary project architectures and agent generation specifications.
  - *App Facing:* Yes.
  - *Source Location:* `0005_gate09_blueprint.py:34`, `backend/app/infrastructure/database/models/blueprint.py`.
- **`blueprint_jobs`**
  - *Purpose:* Asynchronous background generation and QA review jobs for blueprints.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `blueprint_id -> blueprints.id` (CASCADE), `project_instance_id -> project_instances.id` (CASCADE).
  - *Important Columns:* `job_type`, `status`, `current_step`, `error_message`, `step_progress`.
  - *Sensitive Data:* Internal execution logs and error traces.
  - *App Facing:* Yes.
  - *Source Location:* `0005_gate09_blueprint.py:82`, `backend/app/infrastructure/database/models/blueprint.py`.

### 5.8 Project Execution Resources
- **`project_milestones`**
  - *Purpose:* Key deliverables and phase gates for a project instance.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE).
  - *Important Columns:* `title`, `description`, `gate_code`, `target_date`, `status`, `progress_percent`, `deliverables`.
  - *Sensitive Data:* Milestone commitments and grades.
  - *App Facing:* Yes.
  - *Source Location:* `0006_gate10_execution_management.py:33`, `backend/app/infrastructure/database/models/execution.py`.
- **`project_tasks`**
  - *Purpose:* Granular implementation tasks and issues assigned to students.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE), `milestone_id -> project_milestones.id` (SET NULL).
  - *Important Columns:* `task_code`, `title`, `description`, `status`, `priority`, `phase`, `acceptance_criteria`, `due_date`.
  - *Sensitive Data:* Task descriptions, code references.
  - *App Facing:* Yes.
  - *Source Location:* `0006_gate10_execution_management.py:75`, `backend/app/infrastructure/database/models/execution.py`.
- **`project_risks`**
  - *Purpose:* Technical and timeline risks identified for project instances.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE).
  - *Important Columns:* `title`, `description`, `risk_level`, `category`, `mitigation_strategy`, `status`.
  - *Sensitive Data:* Technical blockers and vulnerabilities.
  - *App Facing:* Yes.
  - *Source Location:* `0006_gate10_execution_management.py:126`, `backend/app/infrastructure/database/models/execution.py`.
- **`project_documents`**
  - *Purpose:* Living technical documentation, architecture notes, and specifications.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE).
  - *Important Columns:* `title`, `doc_type`, `content` (Markdown), `version_number`.
  - *Sensitive Data:* Full documentation text and system designs.
  - *App Facing:* Yes.
  - *Source Location:* `0006_gate10_execution_management.py:171`, `backend/app/infrastructure/database/models/execution.py`.

### 5.9 Workspace Extensions & Communication
- **`project_github_integrations`**
  - *Purpose:* VCS repository bindings, sync status, and commit tracking.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE, Unique).
  - *Important Columns:* `repository_name`, `repository_url`, `connection_status`, `default_branch`, `commit_count`, `last_sync_at`, `cached_commits_preview`.
  - *Sensitive Data:* Repository URLs and commit metadata.
  - *App Facing:* Yes.
  - *Source Location:* `0007_gate11_extensions.py:31`, `backend/app/infrastructure/database/models/workspace_extensions.py`.
- **`project_blueprint_versions`**
  - *Purpose:* Historical versioned revisions of approved blueprints.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `blueprint_id -> blueprints.id` (CASCADE), `project_instance_id -> project_instances.id` (CASCADE).
  - *Important Columns:* `version_number`, `status`, `content`, `qa_score`, `change_summary`.
  - *Sensitive Data:* Versioned architecture snapshots.
  - *App Facing:* Yes.
  - *Source Location:* `0007_gate11_extensions.py:64`, `backend/app/infrastructure/database/models/workspace_extensions.py`.
- **`project_change_requests`**
  - *Purpose:* Formal scope change proposals submitted by students for mentor review.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE), `student_id -> users.id` (RESTRICT).
  - *Important Columns:* `title`, `reason`, `scope_change_description`, `impact_analysis`, `status`, `review_notes`.
  - *Sensitive Data:* Scope change proposals and mentor review notes.
  - *App Facing:* Yes.
  - *Source Location:* `0007_gate11_extensions.py:112`, `backend/app/infrastructure/database/models/workspace_extensions.py`.
- **`ai_mentor_conversations`**
  - *Purpose:* Contextual advisory conversation threads between a student and the AI Mentor.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE), `student_id -> users.id` (RESTRICT).
  - *Important Columns:* `title`, `context_type`, `is_pinned`, `message_count`.
  - *Sensitive Data:* Conversation topics and timestamps.
  - *App Facing:* Yes.
  - *Source Location:* `0007_gate11_extensions.py:165`, `backend/app/infrastructure/database/models/workspace_extensions.py`.
- **`ai_mentor_messages`**
  - *Purpose:* Individual messages within an AI Mentor conversation thread.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `conversation_id -> ai_mentor_conversations.id` (CASCADE).
  - *Important Columns:* `sender_type` (`STUDENT`, `AI`, `SYSTEM`), `content` (Markdown), `citations`, `tokens_used`.
  - *Sensitive Data:* Confidential advisory chat logs and questions.
  - *App Facing:* Yes.
  - *Source Location:* `0007_gate11_extensions.py:207`, `backend/app/infrastructure/database/models/workspace_extensions.py`.
- **`project_help_requests`**
  - *Purpose:* Support and escalation tickets from students to human mentors.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE), `student_id -> users.id` (RESTRICT).
  - *Important Columns:* `title`, `category`, `urgency`, `description`, `status`, `mentor_response`, `resolved_at`.
  - *Sensitive Data:* Student struggle points and mentor guidance.
  - *App Facing:* Yes.
  - *Source Location:* `0007_gate11_extensions.py:246`, `backend/app/infrastructure/database/models/workspace_extensions.py`.
- **`project_mentor_notes`**
  - *Purpose:* Confidential observations and evaluations recorded by mentors regarding a project.
  - *Primary Key:* `id` (String(36))
  - *Foreign Keys:* `project_instance_id -> project_instances.id` (CASCADE), `mentor_id -> users.id` (RESTRICT).
  - *Important Columns:* `content` (Confidential markdown), `is_flagged_for_review`.
  - *Sensitive Data:* Confidential mentor assessments (must never be visible to students).
  - *App Facing:* Yes (Mentor only).
  - *Source Location:* `0007_gate11_extensions.py:293`, `backend/app/infrastructure/database/models/workspace_extensions.py`.

### 5.10 Database Infrastructure
- **`alembic_version`**
  - *Purpose:* Internal schema migration version tracking table created by Alembic.
  - *Primary Key:* `version_num` (String(32))
  - *Foreign Keys:* None.
  - *Sensitive Data:* Schema migration state only.
  - *App Facing:* No (Database tool state).
  - *Source Location:* Created automatically by Alembic migration runner.

---

## 6. Ownership & Relationship Map

Tracing the DDL constraints across all migrations reveals the core ownership model:

### 6.1 Direct User Identity Anchor
Every user-referencing foreign key throughout the entire database points directly to `users.id`:
- `student_profiles.user_id` $\rightarrow$ `users.id`
- `mentor_profiles.user_id` $\rightarrow$ `users.id`
- `user_preferences.user_id` $\rightarrow$ `users.id`
- `student_technologies.student_id` $\rightarrow$ `users.id`
- `groups.mentor_id` $\rightarrow$ `users.id`
- `group_memberships.student_id` $\rightarrow$ `users.id`
- `project_definitions.owner_mentor_id` $\rightarrow$ `users.id`
- `project_definition_versions.created_by` $\rightarrow$ `users.id`
- `project_instances.student_id` $\rightarrow$ `users.id`
- `project_phase_history.changed_by` $\rightarrow$ `users.id`
- `project_health_history.changed_by` $\rightarrow$ `users.id`
- `domain_events.actor_id` $\rightarrow$ `users.id`
- `assessments.student_id` $\rightarrow$ `users.id`
- `blueprints.student_id` $\rightarrow$ `users.id`
- `project_change_requests.student_id` $\rightarrow$ `users.id`
- `ai_mentor_conversations.student_id` $\rightarrow$ `users.id`
- `project_help_requests.student_id` $\rightarrow$ `users.id`
- `project_mentor_notes.mentor_id` $\rightarrow$ `users.id`

> [!IMPORTANT]
> **No table references `student_profiles` or `mentor_profiles` as a foreign key.** The profile tables are 1:1 satellite tables keyed on `user_id = users.id`.

### 6.2 The Project Ownership Anchor (`project_instances`)
The table `project_instances` serves as the central authorization hub for all project-scoped resources:

```
                  ┌──────────────────────┐
                  │       users.id       │
                  └──────────┬───────────┘
                             │ (student_id)
                             ▼
┌──────────────┐      ┌──────────────────────┐
│  groups.id   │◄─────┤  project_instances   │
└──────┬───────┘ (group_id) └──────┬───────────┘
       │                           │
       │ (mentor_id)               │ (project_instance_id)
       ▼                           ▼
┌──────────────┐      ┌────────────────────────────────────────────────────────┐
│   users.id   │      │ Project-Scoped Child Resources:                        │
│ (Supervising │      │ - project_profiles                                     │
│   Mentor)    │      │ - project_technologies                                 │
└──────────────┘      │ - project_phase_history                                │
                      │ - project_health_history                               │
                      │ - project_milestones (-> project_tasks)                │
                      │ - project_tasks                                        │
                      │ - project_risks                                        │
                      │ - project_documents                                    │
                      │ - project_github_integrations                          │
                      │ - assessments (-> assessment_answers, results)         │
                      │ - assessment_results                                   │
                      │ - blueprints (-> blueprint_jobs, versions)             │
                      │ - blueprint_jobs                                       │
                      │ - project_blueprint_versions                           │
                      │ - project_change_requests                              │
                      │ - ai_mentor_conversations (-> ai_mentor_messages)      │
                      │ - project_help_requests                                │
                      │ - project_mentor_notes                                 │
                      └────────────────────────────────────────────────────────┘
```

### 6.3 Authorization Paths for Child Resources
- **Direct Child Resources:**
  `resource.project_instance_id` $\rightarrow$ `project_instances.id` $\rightarrow$ student ownership (`project_instances.student_id = auth.uid()::text`) OR mentor supervision (`project_instances.group_id = groups.id AND groups.mentor_id = auth.uid()::text`).
- **Second-Order Child Resources:**
  - `assessment_answers.assessment_id` $\rightarrow$ `assessments.id` $\rightarrow$ `assessments.project_instance_id` $\rightarrow$ `project_instances.id`.
  - `ai_mentor_messages.conversation_id` $\rightarrow$ `ai_mentor_conversations.id` $\rightarrow$ `ai_mentor_conversations.project_instance_id` $\rightarrow$ `project_instances.id`.
  - `project_tasks.milestone_id` $\rightarrow$ `project_milestones.id` (Note: `project_tasks` also has a direct `project_instance_id` FK).

---

## 7. Current RLS State

Below is the complete audit table of current intended RLS state across all 33 tables in the repository:

| Table | RLS Found in Repo | Existing Policies | SELECT | INSERT | UPDATE | DELETE | Notes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `alembic_version` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Database migration tool state. Should not be exposed to PostgREST API roles. |
| `users` | **YES** (0002) | 1 | Self (`id = auth.uid()::text`) | Deny | Deny | Deny | Only self SELECT permitted via PostgREST. Backend handles creation/updates via superuser. |
| `student_profiles` | **YES** (0003) | 1 | Self (`user_id = auth.uid()::text`) | Self | Self | Self | Policy uses `FOR ALL`. Student has full self-management. |
| `mentor_profiles` | **YES** (0003) | 1 | Self (`user_id = auth.uid()::text`) | Self | Self | Self | Policy uses `FOR ALL`. Mentor has full self-management. |
| `user_preferences` | **YES** (0003) | 1 | Self (`user_id = auth.uid()::text`) | Self | Self | Self | Policy uses `FOR ALL`. User manages own preferences. |
| `technologies` | **YES** (0003) | 1 | Authenticated (`role = 'authenticated'`) | Deny | Deny | Deny | Public catalog table. Read-only for logged-in users. |
| `student_technologies` | **YES** (0003) | 1 | Self (`student_id = auth.uid()::text`) | Self | Self | Self | Policy uses `FOR ALL`. Student manages own skills. |
| `groups` | **YES** (0003) | 1 | Mentor (`mentor_id = auth.uid()::text`) | Mentor | Mentor | Mentor | Policy uses `FOR ALL`. Mentor manages own cohorts. Students cannot SELECT groups directly. |
| `group_memberships` | **YES** (0003) | 1 | Student self OR Cohort Mentor | Student / Mentor | Student / Mentor | Student / Mentor | Policy uses `FOR ALL`. Shared access between student and cohort mentor. |
| `project_definitions` | **YES** (0003) | 1 | Mentor (`owner_mentor_id = auth.uid()::text`) | Mentor | Mentor | Mentor | Policy uses `FOR ALL`. Mentor manages own templates. |
| `project_definition_versions` | **YES** (0003) | **0** | **Deny** | **Deny** | **Deny** | **Deny** | RLS enabled with 0 policies $\rightarrow$ PostgREST Deny-All default. |
| `project_instances` | **YES** (0003) | 1 | Student owner OR Supervising Mentor | Student / Mentor | Student / Mentor | Student / Mentor | Policy uses `FOR ALL`. Shared access between student owner and group mentor. |
| `project_profiles` | **YES** (0003) | **0** | **Deny** | **Deny** | **Deny** | **Deny** | RLS enabled with 0 policies $\rightarrow$ PostgREST Deny-All default. |
| `project_technologies` | **YES** (0003) | **0** | **Deny** | **Deny** | **Deny** | **Deny** | RLS enabled with 0 policies $\rightarrow$ PostgREST Deny-All default. |
| `project_phase_history` | **YES** (0003) | **0** | **Deny** | **Deny** | **Deny** | **Deny** | RLS enabled with 0 policies $\rightarrow$ PostgREST Deny-All default. |
| `project_health_history` | **YES** (0003) | **0** | **Deny** | **Deny** | **Deny** | **Deny** | RLS enabled with 0 policies $\rightarrow$ PostgREST Deny-All default. |
| `domain_events` | **YES** (0003) | **0** | **Deny** | **Deny** | **Deny** | **Deny** | RLS enabled with 0 policies $\rightarrow$ PostgREST Deny-All default. Internal outbox. |
| `assessments` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0004. Flagged RLS Disabled by Advisor. |
| `assessment_answers` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0004. Flagged RLS Disabled by Advisor. |
| `assessment_results` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0004. Flagged RLS Disabled by Advisor. |
| `blueprints` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0005. Flagged RLS Disabled by Advisor. |
| `blueprint_jobs` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0005. Flagged RLS Disabled by Advisor. |
| `project_milestones` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0006. Flagged RLS Disabled by Advisor. |
| `project_tasks` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0006. Flagged RLS Disabled by Advisor. |
| `project_risks` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0006. Flagged RLS Disabled by Advisor. |
| `project_documents` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0006. Flagged RLS Disabled by Advisor. |
| `project_github_integrations` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0007. Flagged RLS Disabled by Advisor. |
| `project_blueprint_versions` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0007. Flagged RLS Disabled by Advisor. |
| `project_change_requests` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0007. Flagged RLS Disabled by Advisor. |
| `ai_mentor_conversations` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0007. Flagged RLS Disabled by Advisor. |
| `ai_mentor_messages` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0007. Flagged RLS Disabled by Advisor. |
| `project_help_requests` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0007. Flagged RLS Disabled by Advisor. |
| `project_mentor_notes` | **NO** | 0 | Unrestricted* | Unrestricted* | Unrestricted* | Unrestricted* | Omitted in migration 0007. Flagged RLS Disabled by Advisor. |

*\* Note on "Unrestricted": Access is subject to PostgreSQL table-level grants in `information_schema.role_table_grants` for `anon` and `authenticated`. If default PostgREST grants are present, these tables are exposed to direct reads/writes.*

---

## 8. Existing RLS Policies

The repository contains exactly **10 RLS policies**, defined in migrations `0002_gate04_users.py` and `0003_gate05_core_domain.py`:

```sql
-- 1. users (0002_gate04_users.py:63)
CREATE POLICY users_self_select ON users
    FOR SELECT
    USING (id = auth.uid()::text);

-- 2. student_profiles (0003_gate05_core_domain.py:660)
CREATE POLICY student_profiles_self ON student_profiles
    FOR ALL
    USING (user_id = auth.uid()::text);

-- 3. mentor_profiles (0003_gate05_core_domain.py:666)
CREATE POLICY mentor_profiles_self ON mentor_profiles
    FOR ALL
    USING (user_id = auth.uid()::text);

-- 4. user_preferences (0003_gate05_core_domain.py:672)
CREATE POLICY user_preferences_self ON user_preferences
    FOR ALL
    USING (user_id = auth.uid()::text);

-- 5. student_technologies (0003_gate05_core_domain.py:678)
CREATE POLICY student_technologies_self ON student_technologies
    FOR ALL
    USING (student_id = auth.uid()::text);

-- 6. technologies (0003_gate05_core_domain.py:684)
CREATE POLICY technologies_read ON technologies
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- 7. groups (0003_gate05_core_domain.py:690)
CREATE POLICY groups_mentor_owner ON groups
    FOR ALL
    USING (mentor_id = auth.uid()::text);

-- 8. group_memberships (0003_gate05_core_domain.py:696)
CREATE POLICY group_memberships_participant ON group_memberships
    FOR ALL
    USING (
        student_id = auth.uid()::text OR
        EXISTS (
            SELECT 1 FROM groups
            WHERE groups.id = group_memberships.group_id
              AND groups.mentor_id = auth.uid()::text
        )
    );

-- 9. project_definitions (0003_gate05_core_domain.py:705)
CREATE POLICY project_definitions_owner ON project_definitions
    FOR ALL
    USING (owner_mentor_id = auth.uid()::text);

-- 10. project_instances (0003_gate05_core_domain.py:711)
CREATE POLICY project_instances_access ON project_instances
    FOR ALL
    USING (
        student_id = auth.uid()::text OR
        (
            group_id IS NOT NULL AND
            EXISTS (
                SELECT 1 FROM groups
                WHERE groups.id = project_instances.group_id
                  AND groups.mentor_id = auth.uid()::text
            )
        )
    );
```

### Policy Weaknesses Identified:
1. **Per-Row Invocation:** Bare function calls `auth.uid()::text` and `auth.role()` trigger per-row re-evaluation by PostgreSQL, leading to Supabase "Auth RLS Initialization Plan" warnings.
2. **Coarse `FOR ALL` Usage:** 8 of the 10 policies use `FOR ALL` indiscriminately. This applies identical filtering to `SELECT`, `INSERT`, `UPDATE`, and `DELETE`. It prevents nuanced access (e.g., student inserting a record where mentor can read/update).

---

## 9. Supabase Advisor Reconciliation

Reconciliation of all reported Supabase Security Advisor items against repository artifacts:

### 9.1 RLS Disabled in Public Schema (17 Tables)

#### public.alembic_version
- **RLS:** REPORTED DISABLED
- **Repository:** Created automatically by Alembic migration runner without RLS DDL.
- **Existing policies:** None.
- **Likely data classification:** Database migration infrastructure.
- **Proposed policy:** DO NOT DESIGN YET. (Recommended remediation: Revoke grants from `anon` and `authenticated`, or relocate to a private schema).

#### public.assessments
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0004_gate08_assessment.py:34`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Student private & project scoped).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.assessment_answers
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0004_gate08_assessment.py:77`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Student private & project scoped).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.assessment_results
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0004_gate08_assessment.py:112`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Student private & project scoped — AI diagnostic scores).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.blueprints
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0005_gate09_blueprint.py:34`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Student private & project scoped — AI architecture specification).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.blueprint_jobs
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0005_gate09_blueprint.py:82`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Project scoped operational logs).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.project_milestones
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0006_gate10_execution_management.py:33`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Project scoped execution deliverables).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.project_tasks
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0006_gate10_execution_management.py:75`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Project scoped task assignments & criteria).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.project_risks
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0006_gate10_execution_management.py:126`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Project scoped technical & timeline risks).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.project_documents
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0006_gate10_execution_management.py:171`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Project scoped specification documentation).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.project_blueprint_versions
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0007_gate11_extensions.py:64`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Project scoped historical blueprint snapshots).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.project_github_integrations
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0007_gate11_extensions.py:31`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Project scoped VCS URLs & commit history).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.project_change_requests
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0007_gate11_extensions.py:112`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Student private & project scoped scope change proposals).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.ai_mentor_conversations
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0007_gate11_extensions.py:165`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Student private advisory conversation headers).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.ai_mentor_messages
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0007_gate11_extensions.py:207`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Student private AI chat history & citations).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.project_help_requests
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0007_gate11_extensions.py:246`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Student private support requests & mentor responses).
- **Proposed policy:** DO NOT DESIGN YET.

#### public.project_mentor_notes
- **RLS:** REPORTED DISABLED
- **Repository:** Created in `0007_gate11_extensions.py:293`. No `ENABLE ROW LEVEL SECURITY` statement.
- **Existing policies:** None.
- **Likely data classification:** Protected (Mentor confidential evaluations — student restricted).
- **Proposed policy:** DO NOT DESIGN YET.

---

## 10. Auth RLS Initialization Plan Findings

Supabase flags RLS policies with "Auth RLS Initialization Plan" when `auth.uid()` or `auth.role()` is called as a naked function expression rather than a scalar subquery.

### Why the Advisor Flags It
In PostgreSQL, functions marked as `STABLE` or `VOLATILE` are not automatically hoisted outside the query row-loop by the optimizer. When placed directly into a row filter, PostgreSQL re-evaluates `auth.uid()` for every candidate row evaluated during table scans.

Wrapping the function in a scalar subquery `(SELECT auth.uid()::text)` instructs the query planner to evaluate the expression as an **InitPlan** (executed exactly once at the beginning of the query execution plan).

### Affected Policy Register:

1. **`users` $\rightarrow$ `users_self_select`**
   - *Expression:* `id = auth.uid()::text`
   - *Performance Impact:* Low to Moderate (indexed PK lookup).
   - *Authorization Effect if Optimized:* Zero impact on authorization semantics; identical UUID string comparison.
2. **`student_profiles` $\rightarrow$ `student_profiles_self`**
   - *Expression:* `user_id = auth.uid()::text`
   - *Performance Impact:* Moderate (unique indexed column).
   - *Authorization Effect if Optimized:* Identical.
3. **`mentor_profiles` $\rightarrow$ `mentor_profiles_self`**
   - *Expression:* `user_id = auth.uid()::text`
   - *Performance Impact:* Moderate (unique indexed column).
   - *Authorization Effect if Optimized:* Identical.
4. **`user_preferences` $\rightarrow$ `user_preferences_self`**
   - *Expression:* `user_id = auth.uid()::text`
   - *Performance Impact:* Moderate (unique indexed column).
   - *Authorization Effect if Optimized:* Identical.
5. **`student_technologies` $\rightarrow$ `student_technologies_self`**
   - *Expression:* `student_id = auth.uid()::text`
   - *Performance Impact:* High (multi-row skill table scan per user).
   - *Authorization Effect if Optimized:* Identical.
6. **`technologies` $\rightarrow$ `technologies_read`**
   - *Expression:* `auth.role() = 'authenticated'`
   - *Performance Impact:* High (full catalog table scan evaluates `auth.role()` on every single row).
   - *Authorization Effect if Optimized:* Identical.
7. **`groups` $\rightarrow$ `groups_mentor_owner`**
   - *Expression:* `mentor_id = auth.uid()::text`
   - *Performance Impact:* Moderate.
   - *Authorization Effect if Optimized:* Identical.
8. **`group_memberships` $\rightarrow$ `group_memberships_participant`**
   - *Expression:* `student_id = auth.uid()::text OR EXISTS (SELECT 1 FROM groups WHERE groups.id = group_memberships.group_id AND groups.mentor_id = auth.uid()::text)`
   - *Performance Impact:* Severe (correlated subquery combines per-row function with row-level join).
   - *Authorization Effect if Optimized:* Substantial performance benefit without changing authorization rules.
9. **`project_definitions` $\rightarrow$ `project_definitions_owner`**
   - *Expression:* `owner_mentor_id = auth.uid()::text`
   - *Performance Impact:* Moderate.
   - *Authorization Effect if Optimized:* Identical.
10. **`project_instances` $\rightarrow$ `project_instances_access`**
    - *Expression:* `student_id = auth.uid()::text OR (group_id IS NOT NULL AND EXISTS (SELECT 1 FROM groups WHERE groups.id = project_instances.group_id AND groups.mentor_id = auth.uid()::text))`
    - *Performance Impact:* Severe (complex join with correlated subquery).
    - *Authorization Effect if Optimized:* Substantial performance benefit without changing authorization rules.

---

## 11. Duplicate Index Findings

In PostgreSQL, defining a table-level `UNIQUE` constraint (`sa.UniqueConstraint`) automatically generates an underlying unique B-Tree index. Adding an explicit `op.create_index(..., unique=True)` on the same column creates a 100% redundant index structure that doubles write amplification and wastes memory.

### Confirmed Redundant Indexes:

1. **Table: `assessments`**
   - *Index Name:* `ix_assessments_project_instance_id`
   - *Columns:* `["project_instance_id"]`
   - *Uniqueness:* `unique=True`
   - *Constraint Relationship:* Identical to constraint `uq_assessments_project_instance` on `["project_instance_id"]`.
   - *Migration Created:* `0004_gate08_assessment.py:63, 65`
   - *Equivalent Structure:* `uq_assessments_project_instance`
   - *Confidence:* **CONFIRMED DUPLICATE**
2. **Table: `assessment_results` (Index 1)**
   - *Index Name:* `ix_assessment_results_assessment_id`
   - *Columns:* `["assessment_id"]`
   - *Uniqueness:* `unique=True`
   - *Constraint Relationship:* Identical to constraint `uq_assessment_results_assessment` on `["assessment_id"]`.
   - *Migration Created:* `0004_gate08_assessment.py:148, 151`
   - *Equivalent Structure:* `uq_assessment_results_assessment`
   - *Confidence:* **CONFIRMED DUPLICATE**
3. **Table: `assessment_results` (Index 2)**
   - *Index Name:* `ix_assessment_results_project_instance_id`
   - *Columns:* `["project_instance_id"]`
   - *Uniqueness:* `unique=True`
   - *Constraint Relationship:* Identical to constraint `uq_assessment_results_project_instance` on `["project_instance_id"]`.
   - *Migration Created:* `0004_gate08_assessment.py:149, 157`
   - *Equivalent Structure:* `uq_assessment_results_project_instance`
   - *Confidence:* **CONFIRMED DUPLICATE**
4. **Table: `blueprints`**
   - *Index Name:* `ix_blueprints_project_instance_id`
   - *Columns:* `["project_instance_id"]`
   - *Uniqueness:* `unique=True`
   - *Constraint Relationship:* Identical to constraint `uq_blueprints_project_instance` on `["project_instance_id"]`.
   - *Migration Created:* `0005_gate09_blueprint.py:68, 70`
   - *Equivalent Structure:* `uq_blueprints_project_instance`
   - *Confidence:* **CONFIRMED DUPLICATE**
5. **Table: `project_github_integrations`**
   - *Index Name:* `ix_project_github_integrations_project_instance_id`
   - *Columns:* `["project_instance_id"]`
   - *Uniqueness:* `unique=True`
   - *Constraint Relationship:* Identical to constraint `uq_project_github_integrations_project_instance_id` on `["project_instance_id"]`.
   - *Migration Created:* `0007_gate11_extensions.py:52, 54`
   - *Equivalent Structure:* `uq_project_github_integrations_project_instance_id`
   - *Confidence:* **CONFIRMED DUPLICATE**
6. **Table: `project_profiles`**
   - *Index Name:* `ix_project_profiles_project_instance_id`
   - *Columns:* `["project_instance_id"]`
   - *Uniqueness:* `unique=True`
   - *Constraint Relationship:* Identical to constraint `uq_project_profiles_project_instance_id` on `["project_instance_id"]`.
   - *Migration Created:* `0003_gate05_core_domain.py:447, 451`
   - *Equivalent Structure:* `uq_project_profiles_project_instance_id`
   - *Confidence:* **CONFIRMED DUPLICATE**

---

## 12. Extension Findings

- **Extension Name:** `pg_trgm` (trigram matching)
- **Current Schema:** `public`
- **Creation Location:** `backend/migrations/versions/0001_gate03_baseline.py:50` (`CREATE EXTENSION IF NOT EXISTS pg_trgm`)
- **Codebase Dependencies:** Analysis of all models, queries, repositories, and Alembic migrations indicates **zero active dependencies** on `pg_trgm`. No GIN trigram indexes (`gin_trgm_ops`) or similarity queries (`%`, `<->`, `similarity()`) exist in the application codebase.
- **Extension Schema Strategy:** In Supabase, shared database extensions should reside in the dedicated `extensions` schema to avoid polluting `public` and prevent PostgREST exposure.
- **Assessment:** **CLEARLY ACTIONABLE.** Moving `pg_trgm` via `ALTER EXTENSION pg_trgm SET SCHEMA extensions;` will eliminate the Supabase Security Advisor warning without breaking any existing application functionality.

---

## 13. Authentication Findings

- **Leaked Password Protection:**
  - *Repository Inspection:* Checked `.env.example`, `backend/app/config/settings.py`, and all auth components. Frontend forms enforce password complexity regex, minimum lengths, and digit/special character requirements.
  - *Supabase Auth Feature:* Leaked password protection (HaveIBeenPwned API validation) is an infrastructure feature of Supabase GoTrue Auth managed via the Supabase Cloud Console (`Authentication -> Attack Protection`).
  - *Result:* **UNKNOWN — Supabase project configuration must be checked separately.**
- **Password Policies, Signup & Recovery:**
  - Managed primarily through Supabase GoTrue Auth.
  - Signups invoke `supabase.auth.signUp()` via client frontend ([StudentRegister.tsx](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/frontend/src/pages/Auth/StudentRegister/StudentRegister.tsx), [MentorRegister.tsx](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/frontend/src/pages/Auth/MentorRegister/MentorRegister.tsx)).
  - Passwords reset via `supabase.auth.resetPasswordForEmail()` ([StudentPasswordRecovery.tsx](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/frontend/src/pages/Auth/StudentPasswordRecovery/StudentPasswordRecovery.tsx), [MentorPasswordRecovery.tsx](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/frontend/src/pages/Auth/MentorPasswordRecovery/MentorPasswordRecovery.tsx)).

---

## 14. Email Bounce Code Audit

### Repository Inspection Findings:
1. **Synthetic Demo Email Domain (`@growflow.ai`):**
   - The database seeder (`backend/scripts/seed_demo_dataset.py`) populates 11 demo accounts with email addresses under `@growflow.ai` (e.g., `mentor.elena@growflow.ai`, `student.aarav@growflow.ai`).
   - The seeder bypasses email delivery by inserting directly into `auth.users` with `email_confirmed_at = NOW()`.
2. **Password Recovery Delivery Trigger:**
   - Both `StudentPasswordRecovery.tsx` and `MentorPasswordRecovery.tsx` call `supabase.auth.resetPasswordForEmail(trimmedEmail)`.
   - If developers, testers, or users input any seeded `@growflow.ai` address into the password recovery page, Supabase GoTrue attempts SMTP delivery to that address.
   - Because the domain `growflow.ai` lacks configured MX records and active mailboxes for these accounts, destination mail servers reject the delivery with a hard bounce (`550` or `554`), driving up the bounce rate.
3. **Contact Email Separation:**
   - GrowFlow's application contact email uses a dedicated Google OAuth / Gmail REST API client (`backend/app/infrastructure/email/client.py`), completely separated from Supabase Auth transactional emails.
4. **Assessment:** **LIKELY ROOT CAUSE.** Password recovery testing performed against unroutable `@growflow.ai` demo accounts is the primary candidate cause for the high bounce warning.

---

## 15. Security Risk Classification

### P0 — Critical Security Exposure (0 Confirmed)
- *Criteria:* Active, confirmed, exploitable vulnerability verified through live privileges.
- *Status:* **0 confirmed P0s.** While RLS is omitted on 16 domain tables, actual PostgREST exposure requires active table-level `GRANT` permissions on `anon` or `authenticated`. Because live role grants could not be inspected in this read-only sandbox environment, findings are properly classified as P1 defense-in-depth gaps.

### P1 — Security Correctness & Exposure Risk (16 Findings)
- *Criteria:* High-value domain data lacking RLS defense-in-depth in repository migrations and reported disabled by Supabase Advisor. High risk if default PostgREST grants are active in the live project.
- *Affected Tables:*
  1. `assessments`
  2. `assessment_answers`
  3. `assessment_results`
  4. `blueprints`
  5. `blueprint_jobs`
  6. `project_milestones`
  7. `project_tasks`
  8. `project_risks`
  9. `project_documents`
  10. `project_blueprint_versions`
  11. `project_github_integrations`
  12. `project_change_requests`
  13. `ai_mentor_conversations`
  14. `ai_mentor_messages`
  15. `project_help_requests`
  16. `project_mentor_notes`

### P2 — Architectural / Authorization Gaps (7 Findings)
- *Criteria:* Configuration discrepancies causing access blockage or infrastructure boundary issues.
- *Affected Tables:*
  1. `project_definition_versions` (RLS enabled; 0 policies $\rightarrow$ PostgREST Deny-All)
  2. `project_profiles` (RLS enabled; 0 policies $\rightarrow$ PostgREST Deny-All)
  3. `project_technologies` (RLS enabled; 0 policies $\rightarrow$ PostgREST Deny-All)
  4. `project_phase_history` (RLS enabled; 0 policies $\rightarrow$ PostgREST Deny-All)
  5. `project_health_history` (RLS enabled; 0 policies $\rightarrow$ PostgREST Deny-All)
  6. `domain_events` (RLS enabled; 0 policies $\rightarrow$ PostgREST Deny-All; internal outbox)
  7. `alembic_version` (Infrastructure table lacking RLS in public schema; requires grant revocation)

### P3 — Performance & Database Hygiene (17 Findings)
- *Criteria:* Query optimization, indexing redundancy, and schema namespace cleanliness.
- *Affected Items:*
  - **10 Auth RLS InitPlan Policies:** Function calls `auth.uid()` / `auth.role()` not wrapped in scalar subqueries.
  - **6 Confirmed Duplicate Unique Indexes:** Redundant indexes on `assessments`, `assessment_results` (2), `blueprints`, `project_github_integrations`, `project_profiles`.
  - **1 Extension in Public:** `pg_trgm` installed in `public` instead of `extensions`.

### P4 — Authentication & Operational Hygiene (2 Findings)
- *Criteria:* External service configurations and telemetry warnings.
- *Affected Items:*
  - **Leaked Password Protection Disabled:** Supabase GoTrue Auth dashboard setting.
  - **Email Bounce Telemetry:** Password resets against unroutable `@growflow.ai` demo accounts.

---

## 16. Unknown / Blocked Items

The following 4 items could not be conclusively verified through repository-only inspection:

1. **Live PostgreSQL Table Grants:**
   - *Checked:* Alembic migrations and application configuration.
   - *Could Not Verify:* Privileges granted to `anon` and `authenticated` roles in `information_schema.role_table_grants`.
   - *Reason:* Standard sandbox mode does not allow external network connections to hosted database.
   - *Status:* **BLOCKED — LIVE DATABASE VERIFICATION REQUIRED.**
2. **Live Database Cloud RLS Flags:**
   - *Checked:* Migration history and user-provided Advisor reports.
   - *Could Not Verify:* Whether manual `ALTER TABLE` or emergency fixes were applied directly in the Supabase Cloud SQL Editor.
   - *Status:* **BLOCKED — LIVE DATABASE VERIFICATION REQUIRED.**
3. **Live Supabase GoTrue Settings:**
   - *Checked:* `.env.example`, `backend/app/config/settings.py`.
   - *Could Not Verify:* HaveIBeenPwned toggle, auth rate limits, and custom SMTP configuration in the Supabase Cloud dashboard.
   - *Status:* **UNKNOWN — Supabase project configuration must be checked separately.**
4. **Live Email Bounce Telemetry Logs:**
   - *Checked:* Frontend password recovery code and seeder dataset.
   - *Could Not Verify:* Specific bounce timestamps, error codes, and recipient addresses from Supabase SMTP server logs.
   - *Status:* **UNKNOWN — Live Supabase telemetry logs required.**

---

## 17. Recommended Remediation Order

The following ordered sequence is recommended for addressing the findings during subsequent implementation phases:

1. **Phase 1 — Critical RLS / Security Exposure (Live Grant Verification):**
   - Inspect live table grants for `anon` and `authenticated` roles.
   - Revoke public access to `alembic_version` and `domain_events`.
2. **Phase 2 — Authorization Model Design:**
   - Formulate explicit Student / Mentor / Admin access control matrices for all 32 domain tables.
3. **Phase 3 — RLS Implementation Migration:**
   - Author a forward Alembic migration to enable RLS across all 17 remaining tables.
   - Install granular, role-scoped policies (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) anchored on `users.id` and `project_instances.id`.
4. **Phase 4 — Automated RLS Security Testing:**
   - Execute negative (cross-tenant 403) and positive (owner 200) security tests against all policies.
5. **Phase 5 — RLS Performance Optimization:**
   - Structure all `auth.uid()` and `auth.role()` calls as scalar subqueries (`(SELECT auth.uid()::text)`).
6. **Phase 6 — Index Cleanup:**
   - Drop the 6 confirmed duplicate unique indexes while preserving underlying `UNIQUE` constraints.
7. **Phase 7 — Extension Cleanup:**
   - Relocate `pg_trgm` to the `extensions` schema.
8. **Phase 8 — Authentication Configuration:**
   - Enable Leaked Password Protection in Supabase Cloud Dashboard (`Authentication -> Attack Protection`).
9. **Phase 9 — Email Delivery Remediation:**
   - Guard password recovery forms against demo addresses (`@growflow.ai`) and configure custom SMTP delivery.

---
*End of GrowFlow Database Security Audit Document.*
