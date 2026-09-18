# GrowFlow Database Security & Backend Handoff Guide

**Document Version:** 1.0  
**Status:** IMPLEMENTATION FROZEN / PRODUCTION DEPLOYED & CATALOG VERIFIED  
**Author:** AI Security & Architecture Pair-Programmer  
**Audience:** Backend Engineers, System Architects, DevOps, Security Engineers  
**Target Repository:** `growflow_ai`  
**Authoritative Migration:** [`backend/migrations/versions/0008_gate12_rls_hardening.py`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/migrations/versions/0008_gate12_rls_hardening.py)  
**Authoritative Design:** [`docs/security/GROWFLOW_AUTHORIZATION_MODEL.md`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/docs/security/GROWFLOW_AUTHORIZATION_MODEL.md)  
**Historical Audit:** [`docs/security/GROWFLOW_DATABASE_SECURITY_AUDIT.md`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/docs/security/GROWFLOW_DATABASE_SECURITY_AUDIT.md)  

---

## 1. Executive Summary

GrowFlow is an AI-powered Student Growth and Career Management Platform. The system utilizes a multi-tiered architecture comprising a React/TypeScript frontend client, a FastAPI Python backend service, and a managed Supabase PostgreSQL database platform.

Between Phases 1 and 6 of the GrowFlow Security Track, a comprehensive database security audit, authorization design, forward migration hardening, and production catalog verification were executed to eliminate critical defense-in-depth gaps flagged by the Supabase Security Advisor and architectural audits.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SUPABASE AUTH (GoTrue)                          │
│   Issues signed JWTs containing user UUID (sub) and role               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               LAYER 1: POSTGRESQL TABLE GRANTS (Perimeter)             │
│   anon: NO table privileges                                            │
│   authenticated: SELECT, INSERT, UPDATE, DELETE (Application tables)   │
│   sealed tables: NO privileges granted to PostgREST roles              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│           LAYER 2: ROW LEVEL SECURITY (RLS Defense-in-Depth)           │
│   33 / 33 Tables Protected | 88 Active Policies | 2 Sealed Tables      │
│   All policies InitPlan-optimized: (SELECT auth.uid()::text)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│          LAYER 3: FASTAPI BACKEND APPLICATION AUTHORIZATION            │
│   Dependency-injected JWT validation, Canonical user_id lookup,        │
│   Role checks (Student/Mentor/Admin), Field-level immutability         │
└────────────────────────────────────────────────────────────────────────┘
```

### Current Status Indicators
- **DATABASE SECURITY IMPLEMENTATION:** `DEPLOYED + CATALOG VERIFIED`
- **DATABASE MIGRATION (0008):** `FROZEN`
- **AUTHORIZATION CONTRACT:** `FROZEN`
- **RUNTIME TENANT ISOLATION (STUDENT A/B, MENTOR A/B):** `NOT YET VERIFIED`

### Primary Objectives Accomplished
1. **Eliminated Public Exposure Risk:** Enabled Row Level Security (RLS) across all 33 tables in the `public` schema.
2. **Replaced Broad Policies with Granular RLS:** Authoritative installation of 88 operation-specific policies (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) with strict `WITH CHECK` predicates.
3. **Optimized Policy Query Planning:** Converted 100% of Auth helper function calls into scalar subqueries (`(SELECT auth.uid()::text)` and `(SELECT auth.role())`), preventing catastrophic per-row `InitPlan` re-evaluation overhead.
4. **Cleaned Redundant B-Tree Indexes:** Removed 6 duplicate unique indexes that mirrored table-level `sa.UniqueConstraint` definitions.
5. **Relocated Extension Namespace:** Moved `pg_trgm` out of `public` into the dedicated `extensions` schema.
6. **Hardened PostgreSQL Role Grants:** Revoked dangerous permissions (`TRUNCATE`, `TRIGGER`, `REFERENCES`) from `authenticated` and cleared all table access from `anon`.
7. **Sealed Core Infrastructure:** Enforced strict Deny-All access on `domain_events` and `alembic_version` against external PostgREST callers.

> [!IMPORTANT]
> **Key Takeaway for Backend Engineers:**  
> The database layer now enforces strict defense-in-depth isolation against direct PostgREST calls. However, because the FastAPI backend connects to PostgreSQL as a privileged database role that bypasses RLS, **the backend application layer is solely and strictly responsible for application-level authorization, tenant isolation, and field-level immutability**. RLS does NOT relieve the backend of validating identities and authorization boundaries.

---

## 2. Before vs After Architecture Comparison

| Architectural Aspect | BEFORE Hardening (Migrations 0001–0007) | AFTER Hardening (Migration 0008 & Production Deployment) |
|---|---|---|
| **RLS Coverage** | 16 / 33 tables enabled (Migrations 0004–0007 completely omitted RLS) | **33 / 33 tables enabled (100% complete coverage)** |
| **Active Policies** | 10 broad policies (mostly `FOR ALL USING (...)`) | **88 granular, operation-specific policies** |
| **RLS Policy Performance** | Bare `auth.uid()::text` and `auth.role()` executed per candidate row | **100% InitPlan-optimized scalar subqueries `(SELECT auth.uid()::text)`** |
| **Deny-by-Default Tables** | 6 domain tables had RLS enabled with 0 policies (PostgREST lock-out) | **5 domain tables received operational policies; 1 (`domain_events`) intentionally sealed** |
| **Infrastructure Protection** | `alembic_version` had RLS disabled in `public` schema | **`alembic_version` RLS enabled with 0 policies (Deny-All via PostgREST)** |
| **Role Table Grants (`anon`)** | Standard Supabase broad table privileges | **Zero table privileges granted in `public` schema** |
| **Role Table Grants (`authenticated`)** | Possessed `ALL` privileges including `TRUNCATE`, `TRIGGER`, `REFERENCES` | **Restricted strictly to `SELECT, INSERT, UPDATE, DELETE` on application tables** |
| **PostgreSQL Extensions** | `pg_trgm` installed in `public` schema | **Relocated to dedicated `extensions` schema** |
| **Index Hygiene** | 6 confirmed duplicate unique B-Tree indexes wasting disk & write I/O | **6 redundant indexes dropped; underlying `sa.UniqueConstraint` intact** |
| **Authorization Semantics** | Broad `FOR ALL` policies allowed unintended mutations if `USING` passed | **Distinct `SELECT`, `INSERT`, `UPDATE`, `DELETE` policies with tailored `WITH CHECK` clauses** |

---

## 3. Complete Production Database Inventory

The production database contains exactly **33 tables** in the `public` schema. All 33 tables have Row Level Security enabled.

| # | Table Name | Schema Category | RLS Enabled | Active Policies | Primary Ownership / Anchor Column | PostgREST Client Access |
|:---:|---|---|:---:|:---:|---|---|
| 1 | `alembic_version` | Migration Infrastructure | **YES** | 0 | None (Tool State) | **SEALED (Deny-All)** |
| 2 | `users` | Identity Foundation | **YES** | 1 | `id` (= `auth.users.id`) | Self `SELECT` only |
| 3 | `student_profiles` | Domain Profile | **YES** | 3 | `user_id` $\rightarrow$ `users.id` | Self manage; Cohort Mentor read |
| 4 | `mentor_profiles` | Domain Profile | **YES** | 3 | `user_id` $\rightarrow$ `users.id` | Self manage; Authenticated read |
| 5 | `user_preferences` | Domain Preference | **YES** | 3 | `user_id` $\rightarrow$ `users.id` | Self manage only |
| 6 | `technologies` | Reference Catalog | **YES** | 1 | None (Global Catalog) | Authenticated read-only |
| 7 | `student_technologies` | Domain Skills | **YES** | 4 | `student_id` $\rightarrow$ `users.id` | Student manage; Cohort Mentor read |
| 8 | `groups` | Cohort Organization | **YES** | 4 | `mentor_id` $\rightarrow$ `users.id` | Mentor owner manage; Member read |
| 9 | `group_memberships` | Cohort Organization | **YES** | 3 | `student_id` $\rightarrow$ `users.id` | Student join; Mentor supervise |
| 10 | `project_definitions` | Project Catalog | **YES** | 4 | `owner_mentor_id` $\rightarrow$ `users.id` | Mentor owner manage; Student read |
| 11 | `project_definition_versions`| Project Catalog | **YES** | 1 | `project_definition_id` | Authenticated read-only |
| 12 | `project_instances` | Project Core Anchor | **YES** | 3 | `student_id` $\rightarrow$ `users.id` | Student owner; Cohort Mentor supervise |
| 13 | `project_profiles` | Project Core | **YES** | 3 | `project_instance_id` | Student owner manage; Mentor read |
| 14 | `project_technologies` | Project Core | **YES** | 4 | `project_instance_id` | Student owner manage; Mentor read |
| 15 | `project_phase_history` | Project Audit Trail | **YES** | 1 | `project_instance_id` | Student / Cohort Mentor read-only |
| 16 | `project_health_history` | Project Audit Trail | **YES** | 1 | `project_instance_id` | Student / Cohort Mentor read-only |
| 17 | `domain_events` | System Outbox | **YES** | 0 | None (Internal System Outbox) | **SEALED (Deny-All)** |
| 18 | `assessments` | Assessment Lifecycle | **YES** | 3 | `student_id` $\rightarrow$ `users.id` | Student owner; Cohort Mentor read |
| 19 | `assessment_answers` | Assessment Responses | **YES** | 3 | `assessment_id` $\rightarrow$ `assessments` | **Student owner ONLY (Mentor BLOCKED)** |
| 20 | `assessment_results` | Assessment Diagnostics | **YES** | 1 | `project_instance_id` | Student owner & Cohort Mentor read |
| 21 | `blueprints` | AI Blueprint Engine | **YES** | 3 | `student_id` $\rightarrow$ `users.id` | Student owner; Cohort Mentor read |
| 22 | `blueprint_jobs` | AI Async Processing | **YES** | 1 | `project_instance_id` | Student owner & Cohort Mentor read |
| 23 | `project_milestones` | Execution Management | **YES** | 4 | `project_instance_id` | Student manage; Cohort Mentor read |
| 24 | `project_tasks` | Execution Management | **YES** | 4 | `project_instance_id` | Student manage; Cohort Mentor read |
| 25 | `project_risks` | Execution Management | **YES** | 4 | `project_instance_id` | Student manage; Cohort Mentor read |
| 26 | `project_documents` | Execution Management | **YES** | 4 | `project_instance_id` | Student manage; Cohort Mentor read |
| 27 | `project_github_integrations`| Extended Integrations | **YES** | 4 | `project_instance_id` | Student manage; Cohort Mentor read |
| 28 | `project_blueprint_versions` | Extended Integrations | **YES** | 1 | `project_instance_id` | Student / Cohort Mentor read-only |
| 29 | `project_change_requests` | Extended Scope | **YES** | 3 | `student_id` $\rightarrow$ `users.id` | Student manage; Cohort Mentor read |
| 30 | `ai_mentor_conversations` | AI Communication | **YES** | 2 | `student_id` $\rightarrow$ `users.id` | **Student owner ONLY (Mentor BLOCKED)** |
| 31 | `ai_mentor_messages` | AI Communication | **YES** | 2 | `conversation_id` | **Student owner ONLY (Mentor BLOCKED)** |
| 32 | `project_help_requests` | Extended Support | **YES** | 3 | `student_id` $\rightarrow$ `users.id` | Student create; Mentor respond |
| 33 | `project_mentor_notes` | Extended Mentorship | **YES** | 5 | `mentor_id` / `project_instance_id` | Mentor manage; Student non-INTERNAL |

---

## 4. Row-Level Security (RLS) Architecture

Row-Level Security in GrowFlow provides an in-database, zero-trust perimeter that evaluates authorization predicates on every query row when accessed via PostgREST or unprivileged database roles.

### 1. Identity Anchors
- **Supabase Auth (`auth.users`):** Authenticates user credentials and signs JSON Web Tokens (JWTs).
- **Session Identity (`auth.uid()`):** Resolves the current actor's UUID from the JWT `sub` claim.
- **Session Role (`auth.role()`):** Resolves the database role (`authenticated` or `anon`).
- **GrowFlow Canonical User (`public.users.id`):** Mirrors `auth.users.id` with a 1:1 UUID match. Every user-referencing column across the entire database points to `public.users.id`.

### 2. Role Boundaries
- **Student Role:**
  - Has full operational permissions (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) on their own profile, skills, projects, tasks, milestones, risks, documents, and assessments.
  - Can read reference catalogs and mentor definitions.
  - Strictly isolated from other students' projects and records.
- **Mentor Role:**
  - Has full ownership over their own profile, mentored cohorts (`groups`), and project definitions (`project_definitions`).
  - Granted **read-only supervision** (`SELECT`) over project instances and child execution resources belonging to students actively enrolled in their cohorts.
  - **Mutation Boundaries:** Mentors CANNOT update or delete student tasks, milestones, risks, documents, or blueprints.
  - Permitted to write evaluations and feedback via `project_mentor_notes` and respond to `project_help_requests`.
- **Admin Role:**
  - Admin governance operates through authenticated FastAPI backend endpoints.
  - Admin does NOT receive blanket bypass policies (`USING(true)`) in RLS. PostgREST queries remain bounded by role semantics.
- **Anonymous Role (`anon`):**
  - All protected application domain data, student files, execution metrics, and infrastructure metadata are denied.

---

## 5. Authorization Relationships & Derivation

Every project-scoped resource derives authorization through a strictly verified foreign-key chain:

```
                  ┌──────────────────────┐
                  │   auth.users (JWT)   │
                  └──────────┬───────────┘
                             │ (sub = id)
                             ▼
                  ┌──────────────────────┐
                  │     public.users     │
                  └───────┬──────┬───────┘
                          │      │
            ┌─────────────┘      └─────────────┐
            ▼                                  ▼
┌────────────────────────┐         ┌────────────────────────┐
│    student_profiles    │         │    mentor_profiles     │
│  (user_id = users.id)  │         │  (user_id = users.id)  │
└────────────────────────┘         └───────────┬────────────┘
                                               │ (mentor_id)
                                               ▼
                                   ┌────────────────────────┐
                                   │         groups         │
                                   └───────────┬────────────┘
                                               │ (group_id)
                                               ▼
┌────────────────────────┐         ┌────────────────────────┐
│   group_memberships    │◄────────┤   project_instances    │
│ (student_id, group_id) │         │ (student_id, group_id) │
└────────────────────────┘         └───────────┬────────────┘
                                               │ (project_instance_id)
                                               ▼
                                   ┌────────────────────────┐
                                   │ Project-Scoped Resources│
                                   │ Tasks, Milestones,     │
                                   │ Risks, Documents, etc. │
                                   └────────────────────────┘
```

### Derivation Rules
1. **Direct Student Ownership:**  
   `project_instances.student_id = (SELECT auth.uid()::text)`
2. **Supervising Mentor Cohort Path:**  
   `project_instances.group_id IS NOT NULL`  
   AND `EXISTS (SELECT 1 FROM groups WHERE groups.id = project_instances.group_id AND groups.mentor_id = (SELECT auth.uid()::text))`
3. **Child Resource Project Linkage:**  
   Child resources (`project_tasks`, `project_milestones`, `project_documents`, etc.) link via `project_instance_id -> project_instances.id`.
4. **Group Membership Enrollment:**  
   Students join cohorts via `group_memberships`. Active enrollment requires `group_memberships.status = 'ACTIVE'`.

> [!CAUTION]
> **CRITICAL SECURITY RULE FOR BACKEND ENGINEERS:**  
> **NEVER TRUST CLIENT-SUPPLIED OWNERSHIP IDS.**  
> Never accept `student_id`, `user_id`, or `mentor_id` in request payloads as proof of ownership. The backend must derive the actor's identity strictly from the verified JWT payload and verify that the target resource belongs to that actor before performing operations.

---

## 6. Final Policy Inventory (88 Active Policies)

Below is the verified production policy inventory implemented in Migration 0008:

| Table Name | Active Policy Count | Policy Names & Authorization Patterns |
|---|:---:|---|
| `users` | 1 | `users_self_select` (Self SELECT only) |
| `student_profiles` | 3 | `student_profiles_select` (Self + Cohort Mentor), `student_profiles_insert_self`, `student_profiles_update_self` |
| `mentor_profiles` | 3 | `mentor_profiles_select` (Authenticated read), `mentor_profiles_insert_self`, `mentor_profiles_update_self` |
| `user_preferences` | 3 | `user_preferences_select` (Self only), `user_preferences_insert_self`, `user_preferences_update_self` |
| `technologies` | 1 | `technologies_select` (Authenticated read-only catalog) |
| `student_technologies` | 4 | `student_technologies_select` (Self + Mentor), `student_technologies_insert_student`, `student_technologies_update_student`, `student_technologies_delete_student` |
| `groups` | 4 | `groups_select` (Mentor owner + Enrolled student), `groups_insert_mentor`, `groups_update_mentor`, `groups_delete_mentor` |
| `group_memberships` | 3 | `group_memberships_select` (Student self + Cohort Mentor), `group_memberships_insert_student`, `group_memberships_update_participant` |
| `project_definitions` | 4 | `project_definitions_select` (Owner mentor + Authenticated active), `project_definitions_insert_mentor`, `project_definitions_update_mentor`, `project_definitions_delete_mentor` |
| `project_definition_versions` | 1 | `project_definition_versions_select` (Authenticated read-only) |
| `project_instances` | 3 | `project_instances_select` (Student owner + Supervising mentor), `project_instances_insert_student`, `project_instances_update_student` |
| `project_profiles` | 3 | `project_profiles_select` (Student owner + Mentor), `project_profiles_insert_student`, `project_profiles_update_student` |
| `project_technologies` | 4 | `project_technologies_select` (Student owner + Mentor), `project_technologies_insert_student`, `project_technologies_update_student`, `project_technologies_delete_student` |
| `project_phase_history` | 1 | `project_phase_history_select` (Student owner + Supervising mentor read-only) |
| `project_health_history` | 1 | `project_health_history_select` (Student owner + Supervising mentor read-only) |
| `assessments` | 3 | `assessments_select` (Student owner + Supervising mentor), `assessments_insert_student`, `assessments_update_student` |
| `assessment_answers` | 3 | `assessment_answers_select_student`, `assessment_answers_insert_student`, `assessment_answers_update_student` (**Student Only**) |
| `assessment_results` | 1 | `assessment_results_select` (Student owner + Supervising mentor read-only) |
| `blueprints` | 3 | `blueprints_select` (Student owner + Supervising mentor), `blueprints_insert_student`, `blueprints_update_student` |
| `blueprint_jobs` | 1 | `blueprint_jobs_select` (Student owner + Supervising mentor read-only) |
| `project_milestones` | 4 | `project_milestones_select` (Student + Mentor), `project_milestones_insert_student`, `project_milestones_update_student`, `project_milestones_delete_student` |
| `project_tasks` | 4 | `project_tasks_select` (Student + Mentor), `project_tasks_insert_student`, `project_tasks_update_student`, `project_tasks_delete_student` |
| `project_risks` | 4 | `project_risks_select` (Student + Mentor), `project_risks_insert_student`, `project_risks_update_student`, `project_risks_delete_student` |
| `project_documents` | 4 | `project_documents_select` (Student + Mentor), `project_documents_insert_student`, `project_documents_update_student`, `project_documents_delete_student` |
| `project_github_integrations` | 4 | `project_github_integrations_select` (Student + Mentor), `project_github_integrations_insert_student`, `project_github_integrations_update_student`, `project_github_integrations_delete_student` |
| `project_blueprint_versions` | 1 | `project_blueprint_versions_select` (Student owner + Supervising mentor read-only) |
| `project_change_requests` | 3 | `project_change_requests_select` (Student + Mentor), `project_change_requests_insert_student`, `project_change_requests_update_student` |
| `ai_mentor_conversations` | 2 | `ai_mentor_conversations_select_student`, `ai_mentor_conversations_insert_student` (**Student Only**) |
| `ai_mentor_messages` | 2 | `ai_mentor_messages_select_student`, `ai_mentor_messages_insert_student` (**Student Only**) |
| `project_help_requests` | 3 | `project_help_requests_select` (Student + Mentor), `project_help_requests_insert_student`, `project_help_requests_update_student` |
| `project_mentor_notes` | 5 | `project_mentor_notes_select_student` (Non-INTERNAL), `project_mentor_notes_select_mentor`, `project_mentor_notes_insert_mentor`, `project_mentor_notes_update_mentor`, `project_mentor_notes_delete_mentor` |
| `domain_events` | **0** | **Client Sealed** (PostgREST Deny-All) |
| `alembic_version` | **0** | **Client Sealed** (PostgREST Deny-All) |

---

## 7. RLS Policy Patterns & InitPlan Optimizations

### 1. The InitPlan Scalar Subquery Pattern
In PostgreSQL, calling `auth.uid()` directly inside a policy causes the query executor to evaluate the function for every single candidate row. To eliminate this overhead, all 88 policies in Migration 0008 wrap authentication helpers in scalar subqueries:

```sql
-- RECOMMENDED & ENFORCED PATTERN:
USING (student_id = (SELECT auth.uid()::text))

-- PROHIBITED BARE PATTERN:
USING (student_id = auth.uid()::text)
```

The subquery allows the PostgreSQL query planner to compute the value once as an `InitPlan` and reuse it across the entire scan.

### 2. Standard Archetype Patterns

#### Pattern A: Direct Self-Ownership
Used for personal profiles and user preferences:
```sql
CREATE POLICY user_preferences_select ON user_preferences
    FOR SELECT USING (user_id = (SELECT auth.uid()::text));
```

#### Pattern B: Direct Project Ownership
Used for core project instance creation and mutation:
```sql
CREATE POLICY project_instances_update_student ON project_instances
    FOR UPDATE
    USING (student_id = (SELECT auth.uid()::text))
    WITH CHECK (student_id = (SELECT auth.uid()::text));
```

#### Pattern C: Supervising Mentor Read Access
Allows mentors to supervise student project instances within their cohorts:
```sql
CREATE POLICY project_instances_select ON project_instances
    FOR SELECT
    USING (
        student_id = (SELECT auth.uid()::text) OR
        (
            group_id IS NOT NULL AND
            EXISTS (
                SELECT 1 FROM groups g
                WHERE g.id = project_instances.group_id
                  AND g.mentor_id = (SELECT auth.uid()::text)
            )
        )
    );
```

#### Pattern D: Project-Scoped Child Resource
Used for tasks, milestones, risks, and documents:
```sql
CREATE POLICY project_tasks_select ON project_tasks
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM project_instances pi
            WHERE pi.id = project_tasks.project_instance_id
              AND (
                  pi.student_id = (SELECT auth.uid()::text) OR
                  (
                      pi.group_id IS NOT NULL AND
                      EXISTS (
                          SELECT 1 FROM groups g
                          WHERE g.id = pi.group_id
                            AND g.mentor_id = (SELECT auth.uid()::text)
                      )
                  )
              )
        )
    );
```

#### Pattern E: Infrastructure Sealing
Tables requiring absolute client isolation enable RLS with zero policies:
```sql
ALTER TABLE domain_events ENABLE ROW LEVEL SECURITY;
-- No CREATE POLICY statements. PostgREST callers receive empty results or 403 Forbidden.
```

---

## 8. Confidential & Sealed Resources

Special authorization boundaries are enforced on six high-sensitivity resources:

### 1. `assessment_answers` (Student Private)
- Contains raw student responses to diagnostic questions.
- **Rule:** Accessible strictly by the student author. Supervising mentors can inspect high-level scores and generated plans via `assessment_results`, but **mentors have zero access to raw answers**.

### 2. `project_mentor_notes` (Role Segregated)
- Contains mentor evaluations, actionable feedback, and internal supervisory notes.
- **Rule:**
  - Mentors can create, view, update, and delete notes for projects in their supervised cohorts.
  - Students can view notes ONLY if `note_type != 'INTERNAL'`.
  - Notes marked `INTERNAL` are strictly invisible to students in both RLS and backend endpoints.

### 3. `ai_mentor_conversations` & `ai_mentor_messages` (Student Private)
- Contains confidential student conversations with the AI Advisory Agent.
- **Rule:** Accessible exclusively by the owning student (`student_id = (SELECT auth.uid()::text)`). Mentors have zero read or write permissions.

### 4. `domain_events` (Sealed Outbox)
- Contains asynchronous domain event payloads and messaging traces.
- **Rule:** Backend-internal transactional outbox. RLS is enabled with zero policies. Client table grants are revoked.

### 5. `alembic_version` (Sealed Migration Tracking)
- Contains database migration state.
- **Rule:** Migration executor only. RLS is enabled with zero policies. Client table grants are revoked.

---

## 9. PostgreSQL Grant Perimeter & Privileges

PostgreSQL enforces authorization through two sequential layers:
1. **Layer 1: Table Grants (`GRANT / REVOKE`):** Determines whether a database role has permission to execute an SQL verb (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, `TRIGGER`) on a table.
2. **Layer 2: Row Level Security (RLS):** Determines which specific rows within that table the query can read or modify.

### Production Grant Configuration
During production deployment, table-level grants were hardened:

- **`anon` Role:**  
  All table-level grants on all 33 tables in the `public` schema were revoked. Anonymous callers have zero direct table access.
- **`authenticated` Role:**  
  Granted `SELECT`, `INSERT`, `UPDATE`, `DELETE` exclusively on the 31 application domain tables.
- **Revoked Dangerous Verbs:**  
  Privileges for `TRUNCATE`, `TRIGGER`, and `REFERENCES` were permanently revoked from `authenticated`.
- **Sealed Resources:**  
  `domain_events` and `alembic_version` have zero grants issued to `anon` or `authenticated`.

---

## 10. Summary of Removed Artifacts

During the execution of Migration 0008 and the production security pass, the following redundant, insecure, or obsolete artifacts were permanently removed:

### 1. Six Redundant B-Tree Indexes Removed
PostgreSQL automatically constructs a unique B-Tree index when a table-level `sa.UniqueConstraint` is declared. Creating a secondary `CREATE UNIQUE INDEX` on the same column wastes storage and degrades write performance. The following duplicate indexes were dropped:

```sql
DROP INDEX IF EXISTS public.ix_assessments_project_instance_id;
DROP INDEX IF EXISTS public.ix_assessment_results_assessment_id;
DROP INDEX IF EXISTS public.ix_assessment_results_project_instance_id;
DROP INDEX IF EXISTS public.ix_blueprints_project_instance_id;
DROP INDEX IF EXISTS public.ix_project_github_integrations_project_instance_id;
DROP INDEX IF EXISTS public.ix_project_profiles_project_instance_id;
```
*Note: In all six cases, the underlying unique constraint (e.g. `uq_assessments_project_instance`) remains active and enforces uniqueness.*

### 2. Extension Namespace Cleanup
`pg_trgm` was moved out of `public` into `extensions`:
```sql
ALTER EXTENSION pg_trgm SET SCHEMA extensions;
```

### 3. Ten Legacy Broad Policies Replaced
Ten legacy policies from migrations 0002 and 0003 (e.g., `student_profiles_self`, `groups_mentor_owner`, `project_instances_access`) that relied on broad `FOR ALL` statements and bare `auth.uid()` functions were dropped and replaced by the 88 granular policies.

---

## 11. Migration 0008 Governance & Freeze Rules

- **File:** [`backend/migrations/versions/0008_gate12_rls_hardening.py`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/migrations/versions/0008_gate12_rls_hardening.py)
- **Revision ID:** `0008_gate12_rls_hardening`
- **Revises (Parent):** `0007_gate11_extensions`
- **Status:** **FROZEN (DO NOT MODIFY)**

### Freeze Rules for Developers
1. **Never edit `0008_gate12_rls_hardening.py` directly.** It represents an applied, catalog-verified production migration.
2. **Never modify historical migrations (0001–0007).**
3. **If a schema or policy change is required in future work:**  
   You must author a **new forward Alembic migration** (e.g., `0009_...`) following the change procedure in Section 21.

---

## 12. Critical Backend Development Requirements

When backend development resumes, all engineers must build endpoints to conform to these rules:

1. **Authentication Dependency Injection:**  
   Every protected FastAPI route must declare the authentication dependency (e.g., `Depends(get_current_user)`). Never expose unprotected endpoints that touch domain data.
2. **Derive Identity from Verified JWT:**  
   Always extract `user_id` from the decoded Supabase JWT `sub` claim. Never accept client-supplied `user_id`, `student_id`, or `mentor_id` as proof of who is calling.
3. **Canonical User Resolution:**  
   Map `jwt.sub` to `users.id` in `public.users`. Verify that the account status is `ACTIVE`.
4. **Enforce Role Boundaries in Python:**  
   Verify that `user.role == UserRole.STUDENT` or `UserRole.MENTOR` before executing role-specific logic. Do not rely on database RLS to reject invalid roles.
5. **Enforce Cohort Supervision Paths:**  
   When a mentor accesses a student project, the backend service must query `groups` and `group_memberships` to verify that the student is an active member of a cohort owned by that mentor.
6. **Protect Confidential Data Paths:**  
   Backend query filters must explicitly exclude `assessment_answers` from mentor queries and exclude `note_type == 'INTERNAL'` from student queries.
7. **Service-Role Isolation:**  
   `SUPABASE_SECRET_KEY` (service-role) bypasses RLS. It must strictly reside in server-side environment variables and must never be leaked or forwarded to client applications.

---

## 13. Ownership Immutability & Backend Governance

A fundamental security principle established in Phase 4.1 and Phase 4.2:

> [!WARNING]
> **RLS DOES NOT PREVENT RELATIONSHIP REASSIGNMENT.**  
> PostgreSQL RLS `WITH CHECK` clauses evaluate the validity of the final row state. RLS cannot compare the `OLD` row value with the `NEW` row value during an `UPDATE`. Consequently, RLS alone does NOT prove that a student cannot reassign a task or document to a different project instance that they also own.

### Backend Responsibilities for Invariant 13 (INV-13)
The FastAPI backend application layer and domain models are the authoritative enforcers of field-level immutability:
- **Immutable Columns:** Once set, the following fields must be marked read-only in Pydantic update schemas:
  - `student_id`
  - `mentor_id`
  - `project_instance_id`
  - `group_id`
  - `note_type` (on `project_mentor_notes`)
- **Validation Rule:** Backend service handlers must reject any update request that attempts to alter these foreign-key references.

---

## 14. Production Verification Performed

During the security deployment verification, the following catalog checks were executed:
- **RLS Enabled:** Verified in PostgreSQL system catalog (`pg_tables` / `pg_class.relrowsecurity`) that all 33 tables have `rowsecurity = true`.
- **Policy Count:** Verified that exactly 88 active policies exist across 31 tables in `pg_policies`.
- **Grant Inspection:** Verified that `information_schema.role_table_grants` reflects the revocation of `anon` privileges and the restriction of `authenticated` privileges.
- **Index Catalog Check:** Verified that the 6 duplicate indexes were dropped while the 6 unique constraints remain present in `pg_constraint`.
- **Extension Catalog Check:** Verified that `pg_extension` records `pg_trgm` residing in the `extensions` schema.
- **Infrastructure Sealing:** Confirmed zero policies on `domain_events` and `alembic_version`.

---

## 15. Pending & Unverified Items (Explicit Limitations)

The following items have **NOT** been verified at runtime and remain open operational milestones:

1. **Runtime Student A/B Isolation:**  
   `PENDING.` Direct multi-tenant test suites executing concurrent queries under mock Student A and Student B JWT sessions have not been executed against a live non-bypass database.
2. **Runtime Mentor Supervision Boundaries:**  
   `PENDING.` Cross-cohort negative authorization tests (Mentor A attempting to query Mentor B's cohort) have not been run against live PostgREST.
3. **Runtime Ownership Reassignment Testing:**  
   `PENDING.` Live execution of backend integration tests validating rejection of immutable field reassignment.
4. **Live GoTrue Password Protection (CFG-01):**  
   `PENDING.` The HaveIBeenPwned leaked password protection setting resides in the Supabase Cloud Console and has not been verified via API.
5. **Live SMTP Telemetry (OPS-01):**  
   `PENDING.` Supabase Auth SMTP delivery logs have not been inspected to confirm bounce rates or resolve unroutable `@growflow.ai` addresses.

### Why Runtime Testing Was Deferred
- The available connection string in `.env` connects as the PostgreSQL superuser (`postgres`) with `BYPASSRLS`. Executing queries through this role bypasses RLS and provides no evidence of tenant isolation.
- To prevent corrupting production, no test users (`Student A`, `Mentor B`) or temporary test fixtures were inserted into the live hosted Supabase database.
- Genuine runtime testing requires provisioning a disposable staging database or dedicated test environment where non-bypass roles can be exercised safely.

---

## 16. The 17 Security Invariants

All future application code must uphold these 17 invariants defined in [`docs/security/GROWFLOW_AUTHORIZATION_MODEL.md`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/docs/security/GROWFLOW_AUTHORIZATION_MODEL.md):

1. **INV-01 (Canonical User Reference):** All user references point to `users.id` (1:1 with `auth.users.id`).
2. **INV-02 (Student Ownership Isolation):** Student access is bounded strictly to owned resources (`student_id = auth.uid()`).
3. **INV-03 (Mentor Supervision Path):** Mentor access requires an explicit cohort linkage (`groups.mentor_id = auth.uid()`).
4. **INV-04 (Group Boundary Integrity):** Students join cohorts only via valid `group_memberships`.
5. **INV-05 (Project Anchor Integrity):** All 13 project-scoped resources link directly to `project_instances.id`.
6. **INV-06 (Execution Resource Isolation):** Milestones, tasks, risks, and docs cannot be accessed across project instances.
7. **INV-07 (Assessment Answer Confidentiality):** `assessment_answers` are student-private; mentors have zero access.
8. **INV-08 (Assessment Results Separation):** Mentors can read AI scores/diagnostics in `assessment_results`, never raw answers.
9. **INV-09 (Blueprint Confidentiality):** Blueprints and jobs are student-owned; mentors have read-only access.
10. **INV-10 (AI Thread Confidentiality):** AI conversations and messages are strictly confidential to the student owner.
11. **INV-11 (Mentor Note Classification):** Students cannot view mentor notes where `note_type == 'INTERNAL'`.
12. **INV-12 (Mentor Mutation Boundary):** Mentors cannot update or delete student tasks, milestones, risks, docs, or blueprints.
13. **INV-13 (Ownership Immutability):** Core foreign keys (`student_id`, `mentor_id`, `project_instance_id`) cannot be reassigned (Backend-enforced).
14. **INV-14 (Admin Explicit Boundary):** Admin operations operate via backend business logic, not blanket PostgREST bypasses.
15. **INV-15 (System Outbox Sealing):** `domain_events` has zero client access (PostgREST Deny-All).
16. **INV-16 (Migration Tracking Sealing):** `alembic_version` has zero client access (PostgREST Deny-All).
17. **INV-17 (Public Catalog Access):** `technologies` and active `project_definitions` are read-only to authenticated users.

---

## 17. Security Anti-Patterns (What NOT to Do)

When developing or maintaining backend code, **NEVER**:

- ❌ **DO NOT disable RLS to resolve query errors:** If an API query fails with missing rows, fix the policy or backend query relationship. Never run `ALTER TABLE ... DISABLE ROW LEVEL SECURITY`.
- ❌ **DO NOT add `USING (true)` or `WITH CHECK (true)`:** Blanket bypasses completely destroy tenant isolation.
- ❌ **DO NOT use broad `FOR ALL` policies:** Always specify explicit operations (`FOR SELECT`, `FOR INSERT`, `FOR UPDATE`, `FOR DELETE`).
- ❌ **DO NOT expose `SUPABASE_SECRET_KEY`:** Never pass service-role keys to frontend clients or include them in client bundles.
- ❌ **DO NOT trust client payload IDs:** Never use `request.body.student_id` or `request.body.user_id` as the authorization anchor.
- ❌ **DO NOT reassign ownership fields in update endpoints:** Never allow clients to change `project_instance_id` or `student_id`.
- ❌ **DO NOT re-grant `TRUNCATE`, `TRIGGER`, or `REFERENCES` to `authenticated`:** Keep the grant perimeter strictly limited.
- ❌ **DO NOT expose `domain_events` or `alembic_version` to PostgREST:** Infrastructure tables must remain sealed.
- ❌ **DO NOT modify Migration 0008 directly:** Migration 0008 is frozen. Always create a new forward migration for schema changes.

---

## 18. Backend Development Checklist

Before merging any new backend API endpoint or service handler, verify:

- [ ] **Authentication Required:** Does the route require a verified JWT?
- [ ] **Identity Derivation:** Is `user_id` derived directly from `jwt.sub`?
- [ ] **Role Validation:** Is the caller's role explicitly verified (`STUDENT`, `MENTOR`, `ADMIN`)?
- [ ] **Ownership Verification:** Does the query verify that the caller owns the resource or actively supervises the student?
- [ ] **Confidentiality Check:** If querying assessments, are `assessment_answers` hidden from mentors?
- [ ] **Mentor Notes Check:** If querying notes, are `INTERNAL` notes stripped from student responses?
- [ ] **Immutability Guard:** Are `student_id`, `mentor_id`, and `project_instance_id` excluded from update schemas?
- [ ] **Defense-in-Depth:** Does the endpoint operate correctly even if called via a direct PostgREST client?
- [ ] **No Secret Leaks:** Does the endpoint avoid logging or returning tokens, hashed passwords, or service keys?

---

## 19. Frontend Integration Implications

Frontend engineers currently working on client applications must design interfaces under the following assumptions:

1. **Mentors and Students See Different Data:**  
   Never assume an endpoint or Supabase query returns identical structures for students and mentors. Mentors will receive empty results when querying `assessment_answers` or `ai_mentor_conversations`.
2. **Direct PostgREST Mutations Are Constrained:**  
   Frontend components using the Supabase client directly must adhere to RLS policies. An `INSERT` or `UPDATE` on `project_tasks` without a valid `project_instance_id` linking to an owned project will fail with a policy check violation.
3. **No Service-Role Operations from Browser:**  
   Administrative operations (such as cohort reassignment or account suspension) must call backend FastAPI routes, never direct Supabase clients.
4. **Internal Notes Visibility:**  
   The student dashboard must not render UI elements expecting `INTERNAL` mentor notes. The backend and RLS will exclude them.

---

## 20. Current Freeze State Summary

```
========================================================================
             GROWFLOW DATABASE SECURITY FREEZE REGISTER
========================================================================
  DATABASE SECURITY MIGRATION (0008) : FROZEN
  AUTHORIZATION CONTRACT (PHASE 2)   : FROZEN
  TOTAL PUBLIC TABLES                : 33
  RLS COVERAGE                       : 33 / 33 TABLES (100%)
  ACTIVE POLICIES                    : 88 (ALL INITPLAN-OPTIMIZED)
  SEALED RESOURCES                   : 2 (domain_events, alembic_version)
  REDUNDANT UNIQUE INDEXES           : 6 PERMANENTLY DROPPED
  EXTENSION PLACEMENT                : pg_trgm RELOCATED TO extensions
  PRODUCTION DATABASE                : DEPLOYED & CATALOG VERIFIED
  PRODUCTION APPLICATION DATA        : UNTOUCHED (NO TEST FIXTURES)
  RUNTIME NON-BYPASS VERIFICATION    : PENDING (STAGING MILESTONE)
========================================================================
```

---

## 21. Future Security Change Procedure

If future business requirements demand altering an authorization rule or database security policy, engineers must follow this structured change control workflow:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Formal Change Request & Threat Model Review             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Update docs/security/GROWFLOW_AUTHORIZATION_MODEL.md     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Author Forward Migration (e.g., 0009_update_policy.py)   │
│    - Maintain InitPlan optimization: (SELECT auth.uid())    │
│    - Implement symmetrical downgrade() logic                │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Test in Disposable Staging Environment (Non-Bypass Role) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Peer Security Review & Production Release Deployment     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Update This Handoff Document & Freeze Registry           │
└─────────────────────────────────────────────────────────────┘
```

---

## 22. Backend Development Resume Plan

When backend engineering resumes, execute the following step-by-step onboarding plan:

- [ ] **Step 1: Read This Handoff Guide**  
  Thoroughly review [`docs/database/GROWFLOW_DATABASE_SECURITY_AND_BACKEND_HANDOFF.md`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/docs/database/GROWFLOW_DATABASE_SECURITY_AND_BACKEND_HANDOFF.md).
- [ ] **Step 2: Read Authoritative Authorization Model**  
  Review [`docs/security/GROWFLOW_AUTHORIZATION_MODEL.md`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/docs/security/GROWFLOW_AUTHORIZATION_MODEL.md) for detailed CRUD matrices across all 33 tables.
- [ ] **Step 3: Inspect Authoritative Migration 0008**  
  Examine SQL DDL and policy definitions in [`backend/migrations/versions/0008_gate12_rls_hardening.py`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/migrations/versions/0008_gate12_rls_hardening.py).
- [ ] **Step 4: Inspect Supabase Auth Configuration**  
  Review JWT decoding, issuer settings, and role mapping in `backend/app/config/settings.py`.
- [ ] **Step 5: Verify FastAPI JWT Dependency**  
  Ensure authentication dependencies validate Supabase JWT signatures and extract `sub` correctly.
- [ ] **Step 6: Implement Service-Layer Role Checks**  
  Verify that services check `user.role` against domain models (`Student`, `Mentor`, `Admin`).
- [ ] **Step 7: Enforce Field-Level Immutability (INV-13)**  
  Verify that Pydantic update schemas forbid mutation of `student_id`, `mentor_id`, and `project_instance_id`.
- [ ] **Step 8: Set Up Disposable Test Database**  
  Provision a local Docker PostgreSQL container or Supabase branching database for integration tests.
- [ ] **Step 9: Create Non-Bypass Test Harness**  
  Configure tests to execute queries under the unprivileged `authenticated` role with transaction-scoped claims (`SET LOCAL request.jwt.claim.sub = '...'`).
- [ ] **Step 10: Execute Student A/B and Mentor A/B Runtime Tests**  
  Validate that cross-student and cross-cohort read/write attempts return zero rows or 403 Forbidden.
- [ ] **Step 11: Execute End-to-End Defense-in-Depth Tests**  
  Verify that backend application authorization and database RLS work cohesively in tandem.
- [ ] **Step 12: Final Track Verification Sign-Off**  
  Update this document with runtime verification results upon successful test suite completion.
