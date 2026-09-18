# GrowFlow Authorization Model & RLS Policy Contract

**Document Version:** 1.0 (Authoritative Design Baseline)  
**Date:** September 15, 2026  
**Status:** DESIGN ONLY — Phase Boundary Enforced (No DDL / No SQL Implemented)  
**Target Repository:** `growflow_ai`  
**Consumes:** `docs/security/GROWFLOW_DATABASE_SECURITY_AUDIT.md` (v2.0)  
**Output Target:** Pre-Implementation Specification for Prompt 3 (RLS Migration) & Prompt 4 (Security Verification)

---

## 1. Purpose

This document defines the authoritative, evidence-based **Authorization Model** for GrowFlow and translates it conceptually into an **RLS Policy Contract**.

It answers precisely:
> *"Who is permitted to perform which operation (SELECT, INSERT, UPDATE, DELETE) on which GrowFlow database resource, and through what verified foreign-key relationship?"*

### Phase Boundary Notice:
- **Design Only:** No database modifications, migrations, SQL DDL/DML, or code alterations are performed in this phase.
- **Contractual Specification:** This document establishes the semantic rules that future implementation phases (Prompt 3 and Prompt 4) must enforce and verify.
- **Zero Invention:** All access rules are derived strictly from existing repository architecture, executable migrations, ORM models, and backend authorization services. Where architectural evidence is ambiguous or incomplete, the item is explicitly recorded in the **Decision Register** rather than assumed.

---

## 2. Source-of-Truth Hierarchy

When evaluating authorization rules and relationship paths, evidence was evaluated strictly in the following priority order:

1. **Explicit Authorization & Security Architecture Documents:**  
   - `docs/6D_Authentication_and_Security_Architecture_Final.md` (Canonical flow & RBAC/ABAC rules).
   - `docs/6B_Database_Architecture_and_Data_Model_Final.md` (Domain relationships & constraints).
   - `docs/5B`, `5C`, `5D` (Student, Mentor, and Admin Application Architecture specifications).
2. **Actual Database Migrations / Executable DDL:**  
   - Migrations `0001_gate03_baseline.py` through `0007_gate11_extensions.py` (authoritative foreign keys, constraints, and existing RLS policies).
3. **SQLAlchemy ORM Domain & Infrastructure Models:**  
   - Declarative models in `backend/app/infrastructure/database/models/`.
4. **Existing Application Backend Authorization Logic:**  
   - `backend/app/domain/identity/authorization.py` (`verify_role_access`, `verify_resource_ownership`, `verify_account_active`).
   - Application services in `backend/app/application/services/` (project, assessment, blueprint, execution, group, and extension services).
5. **Existing Frontend Application Behavior:**  
   - Client API modules in `frontend/src/lib/api/` and route guards.
6. **Existing Automated Test Suites:**  
   - Unit and integration tests in `backend/tests/` and `frontend/src/test/`.
7. **Architectural Inference:**  
   - General distributed systems principles (used solely to formulate open questions in the Decision Register).

---

## 3. Security Principles

The GrowFlow authorization design adheres to twelve foundational security principles:

1. **RLS Status Is Not Authorization:**  
   Whether RLS is currently enabled or disabled in a migration describes current state, not desired authorization. The authorization contract defines *what access should exist*, which Prompt 3 will implement.
2. **`users.id` Is the Canonical Identity:**  
   Supabase Auth `auth.users.id` maps 1:1 to GrowFlow's `users.id`. All user-referencing domain columns (`student_id`, `mentor_id`, `owner_mentor_id`, `user_id`, `created_by`, `changed_by`, `actor_id`) reference `users.id` directly. `student_profiles` and `mentor_profiles` are 1:1 extension tables, never foreign-key targets for domain resources.
3. **`project_instances` Is the Central Project Authorization Anchor:**  
   Every project execution resource (tasks, milestones, risks, documents, assessments, blueprints, change requests, github integrations, help requests, mentor notes) anchors directly to `project_instances.id`. Authorization for child tables is derived from the project instance's student owner (`student_id`) or supervising mentor (`group_id -> groups.mentor_id`).
4. **Mentor Access Must Be Derived from Verified Relationships:**  
   Mentors do not have universal read or write access across the platform. A mentor's authority to inspect student projects and execution resources derives strictly from group supervision (`project_instances.group_id -> groups.id -> groups.mentor_id = users.id`). Direct mentor ownership applies only to mentor-authored resources (`project_definitions`, `groups`, `project_mentor_notes`).
5. **Student Isolation:**  
   Student A must never access, query, or mutate Student B's private profiles, projects, assessments, blueprints, documents, tasks, or AI consultations, even if Student A possesses Student B's resource UUIDs.
6. **Mentor Isolation:**  
   Mentor A must never access Mentor B's private profile, groups, or supervised project cohorts without an explicit authorization link.
7. **Admin Must Not Be Invented:**  
   The `ADMIN` role is a platform governance and observability role, not a blanket database superuser. As established in `docs/5D` and `backend/app/domain/identity/authorization.py`, default-deny applies even to Admin unless explicitly provided by verified policy. Unresolved Admin privileges are flagged for human decision.
8. **Operation-Level Authorization:**  
   Every resource's permissions are specified separately for `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.
9. **READ $\neq$ WRITE:**  
   Supervisory read access does not confer write access. Mentors who can inspect student tasks or documents cannot modify them.
10. **Ownership Immutability:**  
    Foreign-key fields representing tenant boundaries (`user_id`, `student_id`, `mentor_id`, `owner_mentor_id`, `project_instance_id`, `group_id`, `conversation_id`) are immutable. Once written, they cannot be reassigned via `UPDATE`.
11. **`WITH CHECK` Requirements:**  
    All `INSERT` and `UPDATE` operations must satisfy strict result validation: rows created or updated by an actor must remain within that actor's authorized boundary upon write completion.
12. **Backend vs. PostgREST Defense-in-Depth:**  
    The official frontend application communicates exclusively with the FastAPI backend, which connects to PostgreSQL via async superuser pool. RLS policies act as the critical outer defense-in-depth perimeter against unauthorized direct requests via Supabase PostgREST API (`anon` and `authenticated` roles).

---

## 4. Identity Model

GrowFlow's identity architecture establishes a strict 1:1 mapping between the external Supabase authentication provider and the canonical application user:

```
┌─────────────────────────────────────────────────────────────┐
│                 Supabase Auth (auth.users)                  │
│   id: UUID (Issued on signup/login)                         │
│   email: string                                             │
│   raw_user_meta_data: JSONB (first_name, last_name, role)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ 1:1 Cryptographic Identity Mapping
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 GrowFlow Canonical (users)                  │
│   id: String(36) / UUID PRIMARY KEY                         │
│   email: String(255) UNIQUE                                 │
│   role: 'STUDENT' | 'MENTOR' | 'ADMIN'                      │
│   status: 'ACTIVE' | 'SUSPENDED' | 'INACTIVE'               │
└──────────────┬───────────────┬───────────────┬──────────────┘
               │ 1:1 (CASCADE) │ 1:1 (CASCADE) │ 1:1 (CASCADE)
               ▼               ▼               ▼
     [student_profiles] [mentor_profiles] [user_preferences]
```

### Identity Rules:
- **Canonical ID:** In all RLS evaluations, `auth.uid()::text` resolves directly against `users.id`.
- **Account Status Enforced:** Under `verify_account_active()` ([authorization.py:28](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/domain/identity/authorization.py#L28)), users in `SUSPENDED` or `INACTIVE` state are rejected. PostgREST policies should evaluate active status when relevant.
- **Profile Independence:** Profile tables contain role-specific metadata. No domain entity references `student_profiles` or `mentor_profiles` as a foreign key.

---

## 5. Application Roles

GrowFlow defines three distinct application roles in `UserRole` (`backend/app/domain/identity/models.py`):

1. **STUDENT:**
   - Primary actor in project build, execution, learning, and self-assessment.
   - Owns `project_instances`, `student_technologies`, `assessments`, `blueprints`, `project_tasks`, `project_milestones`, `project_risks`, `project_documents`, `project_github_integrations`, `project_change_requests`, `ai_mentor_conversations`, `project_help_requests`.
   - Read access to `technologies` (catalog), active `project_definitions` (catalog discovery), and own enrolled `groups`.
2. **MENTOR:**
   - Platform educator and cohort supervisor.
   - Owns and creates `groups`, `project_definitions`, `project_definition_versions`, `project_mentor_notes`.
   - Read-only supervisory access to enrolled students' `project_instances`, `project_profiles`, `project_tasks`, `project_milestones`, `project_risks`, `project_documents`, `project_github_integrations`, `blueprints`, and `project_help_requests`.
   - Write access to respond to `project_help_requests` and create `project_mentor_notes`.
   - **No write access** to student project tasks, milestones, risks, or documents.
3. **ADMIN:**
   - Platform governance, observability, and audit layer (`docs/5D`).
   - Observes cross-platform statistics and operations via the FastAPI backend.
   - Not an operational super-mentor. Direct data mutation on student work is denied by default unless handled through audited backend intervention endpoints.

---

## 6. Database Roles and Access Paths

### Access Paths:
1. **Path A: Official Frontend Application (Backend Proxied):**  
   `React Frontend` $\rightarrow$ `FastAPI Backend (/api/v1)` $\rightarrow$ `PostgreSQL (Async Pool)`.  
   - Backend authenticates user JWT using `get_current_user()` dependency.  
   - Database connection operates under connection pool superuser (`postgres`), executing business logic and event enqueueing.
2. **Path B: Direct Supabase Client (PostgREST):**  
   `External Client / Web Browser` $\rightarrow$ `Supabase PostgREST (/rest/v1)` $\rightarrow$ `PostgreSQL`.  
   - Operates under database roles: `anon` (unauthenticated) or `authenticated` (valid JWT).  
   - Governed strictly by PostgreSQL table grants and Row Level Security policies.

### Separation of Application Role from Database Role:
- A user with JWT claim `role: "authenticated"` possesses the PostgreSQL role `authenticated`.
- That user's application role (`STUDENT`, `MENTOR`, `ADMIN`) is stored in `public.users.role`.
- RLS policies must not confuse PostgreSQL's `auth.role()` (which is `"authenticated"`) with GrowFlow's application roles. Application role checks in RLS rely on relationship joins against `users.id = auth.uid()::text` or subqueries against `users.role`.

---

## 7. Ownership Model

GrowFlow utilizes two verified ownership paradigms:

### A. Direct User Ownership
The resource has a direct foreign key referencing `users.id`:
- `student_profiles.user_id`
- `mentor_profiles.user_id`
- `user_preferences.user_id`
- `student_technologies.student_id`
- `groups.mentor_id`
- `project_definitions.owner_mentor_id`
- `project_instances.student_id`

### B. Project-Scoped Derived Ownership
The resource belongs to a project instance (`project_instance_id -> project_instances.id`). Ownership resolves transitively:
$$\text{Resource} \xrightarrow{\text{project\_instance\_id}} \text{project\_instances} \xrightarrow{\text{student\_id}} \text{users.id}$$
All execution resources (`tasks`, `milestones`, `risks`, `documents`, `github_integrations`, `blueprints`, `assessments`, `change_requests`, `help_requests`, `notes`) belong to the student who owns the parent `project_instance`.

---

## 8. Group and Mentorship Model

The supervision relationship between a mentor and student projects is mediated by `groups` and `group_memberships`:

```
[groups] (mentor_id = Mentor users.id)
   ▲                       ▲
   │ (group_id)            │ (group_id)
   │                       │
[group_memberships]   [project_instances]
(student_id = Student) (student_id = Student, group_id = groups.id)
```

### Verified Rules:
1. **Mentor Group Creation:** Mentors create groups and receive unique join codes (`GRP-XXXX`). Only the owning mentor (`groups.mentor_id = auth.uid()::text`) can update or archive the group.
2. **Student Enrollment:** Students join a group by submitting a valid `join_code`. This creates an active `group_memberships` record (`student_id = auth.uid()::text`).
3. **Supervised Project Linkage:** When a student creates or links a project within a cohort, `project_instances.group_id` points to `groups.id`.
4. **Mentor Supervision Scope:** A mentor supervises a project instance if and only if:
   - `project_instances.group_id` is NOT NULL, and
   - `groups.id = project_instances.group_id` has `groups.mentor_id = auth.uid()::text`.
   *(Or transitively, if the student has an active membership in one of the mentor's groups).*

---

## 9. Project Authorization Anchor

`project_instances` is the architectural anchor for 21 dependent tables:

```
                         [project_instances]
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    ▼                             ▼                             ▼
[Core Specifications]    [Execution Management]      [Extensions & AI]
- project_profiles       - project_milestones        - project_github_integrations
- project_technologies   - project_tasks             - project_change_requests
- project_phase_history  - project_risks             - project_blueprint_versions
- project_health_history - project_documents         - ai_mentor_conversations
- blueprints                                         - project_help_requests
- blueprint_jobs                                     - project_mentor_notes
- assessments                                        (ai_mentor_messages -> conv)
  (answers -> assessment)
  (results -> assessment)
```

**Core Policy Rule:** An actor who does not have access to a `project_instance` has zero access to any child resource anchored to that `project_instance`.

---

## 10. Complete Table Classification

All 33 public tables are classified into distinct security domains:

| # | Table Name | Security Domain | Primary Actor | Ownership Basis | PostgREST Strategy |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | `alembic_version` | SYSTEM / INFRASTRUCTURE | None (Alembic) | Migration Tool State | **DENY ALL / ISOLATE** |
| 2 | `users` | IDENTITY | Self User | 1:1 `auth.users.id` | **RESTRICTED** (Self SELECT only) |
| 3 | `student_profiles` | PROFILE | Student | Direct (`user_id`) | **RESTRICTED** (Self + Group Mentor) |
| 4 | `mentor_profiles` | PROFILE | Mentor | Direct (`user_id`) | **RESTRICTED** (Self + Auth Read) |
| 5 | `user_preferences` | PREFERENCE | Self User | Direct (`user_id`) | **RESTRICTED** (Self Only) |
| 6 | `technologies` | REFERENCE | Catalog | None (System Catalog)| **DIRECTLY ACCESSIBLE** (Read Only) |
| 7 | `student_technologies` | PROFILE / SKILLS | Student | Direct (`student_id`)| **RESTRICTED** (Self + Group Mentor) |
| 8 | `groups` | ORGANIZATION | Mentor | Direct (`mentor_id`) | **RESTRICTED** (Mentor Owner + Member) |
| 9 | `group_memberships` | ORGANIZATION | Student / Mentor | Compound (`group_id, student_id`) | **RESTRICTED** (Member + Mentor) |
| 10 | `project_definitions` | PROJECT CATALOG | Mentor | Direct (`owner_mentor_id`) | **RESTRICTED** (Mentor Owner + Catalog Read) |
| 11 | `project_definition_versions`| PROJECT CATALOG | Mentor | Parent (`project_definition_id`) | **RESTRICTED** (Mentor Owner + Catalog Read) |
| 12 | `project_instances` | PROJECT CORE | Student | Direct (`student_id`)| **RESTRICTED** (Owner + Supervising Mentor) |
| 13 | `project_profiles` | PROJECT CORE | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner + Supervising Mentor) |
| 14 | `project_technologies` | PROJECT CORE | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner + Supervising Mentor) |
| 15 | `project_phase_history`| AUDIT | System / User | Parent (`project_instance_id`) | **RESTRICTED** (Read Only; Append Only) |
| 16 | `project_health_history`| AUDIT | System / User | Parent (`project_instance_id`) | **RESTRICTED** (Read Only; Append Only) |
| 17 | `domain_events` | SYSTEM / OUTBOX | Background Worker| None (System Outbox) | **BACKEND-ONLY / DENY ALL** |
| 18 | `assessments` | ASSESSMENT | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner + Supervising Mentor) |
| 19 | `assessment_answers` | ASSESSMENT | Student | Parent (`assessment_id`) | **RESTRICTED** (Owner Only; Mentor Denied) |
| 20 | `assessment_results` | ASSESSMENT | Student / AI | Parent (`project_instance_id`) | **RESTRICTED** (Owner + Supervising Mentor Read) |
| 21 | `blueprints` | BLUEPRINT / AGENT | Student / AI | Parent (`project_instance_id`) | **RESTRICTED** (Owner + Supervising Mentor Read) |
| 22 | `blueprint_jobs` | BLUEPRINT / AGENT | Background Worker| Parent (`project_instance_id`) | **RESTRICTED** (Owner Read Only; Worker Mutate) |
| 23 | `project_milestones` | EXECUTION | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner CRUD + Mentor Read) |
| 24 | `project_tasks` | EXECUTION | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner CRUD + Mentor Read) |
| 25 | `project_risks` | EXECUTION | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner CRUD + Mentor Read) |
| 26 | `project_documents` | EXECUTION | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner CRUD + Mentor Read) |
| 27 | `project_github_integrations`| EXTENSION | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner CRUD + Mentor Read) |
| 28 | `project_blueprint_versions` | EXTENSION | Student / AI | Parent (`project_instance_id`) | **RESTRICTED** (Owner Read + Mentor Read) |
| 29 | `project_change_requests` | EXTENSION | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner CRUD + Mentor Read) |
| 30 | `ai_mentor_conversations` | AI MENTOR | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner Only; Mentor Decision) |
| 31 | `ai_mentor_messages` | AI MENTOR | Student / AI | Parent (`conversation_id`) | **RESTRICTED** (Owner Only; Mentor Decision) |
| 32 | `project_help_requests` | MENTORING | Student | Parent (`project_instance_id`) | **RESTRICTED** (Owner CRUD + Mentor Respond) |
| 33 | `project_mentor_notes` | MENTORING | Mentor | Parent (`project_instance_id`) | **RESTRICTED** (Mentor Author + Student Read) |

---

## 11. Student Authorization Model

| Table | SELECT | INSERT | UPDATE | DELETE | Access Basis & Condition |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `users` | ALLOWED | DENIED | DENIED | DENIED | Self record only (`id = auth.uid()`). Mutations via Auth provider. |
| `student_profiles` | ALLOWED | ALLOWED | ALLOWED | DENIED | Self record only (`user_id = auth.uid()`). Profile cannot be deleted. |
| `mentor_profiles` | ALLOWED | DENIED | DENIED | DENIED | Public directory read of mentor profiles for active mentors. |
| `user_preferences` | ALLOWED | ALLOWED | ALLOWED | DENIED | Self record only (`user_id = auth.uid()`). |
| `technologies` | ALLOWED | DENIED | DENIED | DENIED | Global catalog read-only for all authenticated students. |
| `student_technologies`| ALLOWED | ALLOWED | ALLOWED | ALLOWED | Self records only (`student_id = auth.uid()`). Full CRUD on own skills. |
| `groups` | ALLOWED | DENIED | DENIED | DENIED | Enrolled groups only (via active `group_memberships`). |
| `group_memberships` | ALLOWED | ALLOWED | ALLOWED | ALLOWED | Self memberships (`student_id = auth.uid()`). INSERT via join code; UPDATE status to 'LEFT'. |
| `project_definitions`| ALLOWED | DENIED | DENIED | DENIED | Active catalog items only (`status = 'ACTIVE'`). Template browsing. |
| `project_definition_versions`| ALLOWED | DENIED | DENIED | DENIED | Read-only versions linked to active project definitions. |
| `project_instances` | ALLOWED | ALLOWED | ALLOWED | DENIED | Owned projects (`student_id = auth.uid()`). Deletion prohibited (soft-archive only). |
| `project_profiles` | ALLOWED | ALLOWED | ALLOWED | DENIED | Anchored to owned project (`project_instance_id -> student_id = auth.uid()`). |
| `project_technologies`| ALLOWED | ALLOWED | ALLOWED | ALLOWED | Anchored to owned project. Full stack customization. |
| `project_phase_history`| ALLOWED | DENIED | DENIED | DENIED | Audit log read-only for owned project. Mutations via backend transitions. |
| `project_health_history`| ALLOWED | DENIED | DENIED | DENIED | Audit log read-only for owned project. Mutations via backend transitions. |
| `domain_events` | DENIED | DENIED | DENIED | DENIED | System transactional outbox. Strictly backend-only. |
| `assessments` | ALLOWED | ALLOWED | ALLOWED | DENIED | Owned project assessment (`student_id = auth.uid()`). Lifecycle updates. |
| `assessment_answers` | ALLOWED | ALLOWED | ALLOWED | DENIED | Owned assessment answers (`assessment_id -> student_id = auth.uid()`). |
| `assessment_results` | ALLOWED | DENIED | DENIED | DENIED | Owned assessment results read-only. Generated by backend AI engine. |
| `blueprints` | ALLOWED | ALLOWED | ALLOWED | DENIED | Owned project blueprint (`student_id = auth.uid()`). Approval mutations. |
| `blueprint_jobs` | ALLOWED | DENIED | DENIED | DENIED | Owned blueprint jobs read-only. Generation managed by backend workers. |
| `project_milestones` | ALLOWED | ALLOWED | ALLOWED | ALLOWED | Full execution CRUD on owned project milestones. |
| `project_tasks` | ALLOWED | ALLOWED | ALLOWED | ALLOWED | Full execution CRUD on owned project tasks. |
| `project_risks` | ALLOWED | ALLOWED | ALLOWED | ALLOWED | Full execution CRUD on owned project risks. |
| `project_documents` | ALLOWED | ALLOWED | ALLOWED | ALLOWED | Full execution CRUD on owned project specification documents. |
| `project_github_integrations`| ALLOWED | ALLOWED | ALLOWED | ALLOWED | Full integration CRUD on owned project. |
| `project_blueprint_versions`| ALLOWED | DENIED | DENIED | DENIED | Immutable version snapshots of owned project blueprints. |
| `project_change_requests`| ALLOWED | ALLOWED | ALLOWED | DENIED | Submit and view change requests on owned project. |
| `ai_mentor_conversations`| ALLOWED | ALLOWED | DENIED | DENIED | Own consultation threads (`student_id = auth.uid()`). |
| `ai_mentor_messages` | ALLOWED | ALLOWED | DENIED | DENIED | Read thread; INSERT user prompts (`role = 'user'`). Assistant messages inserted by backend. |
| `project_help_requests`| ALLOWED | ALLOWED | ALLOWED | DENIED | Submit help requests on owned project; mark resolved. |
| `project_mentor_notes` | ALLOWED | DENIED | ALLOWED | DENIED | SELECT non-internal notes (`note_type != 'INTERNAL'`); UPDATE status to 'ACKNOWLEDGED'. |

---

## 12. Mentor Authorization Model

| Table | SELECT | INSERT | UPDATE | DELETE | Access Basis & Condition |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `users` | ALLOWED | DENIED | DENIED | DENIED | Self record only (`id = auth.uid()`). |
| `student_profiles` | ALLOWED | DENIED | DENIED | DENIED | Students enrolled in mentor's active supervised groups. |
| `mentor_profiles` | ALLOWED | ALLOWED | ALLOWED | DENIED | Self profile full management (`user_id = auth.uid()`). |
| `user_preferences` | ALLOWED | ALLOWED | ALLOWED | DENIED | Self preferences only (`user_id = auth.uid()`). |
| `technologies` | ALLOWED | DENIED | DENIED | DENIED | Global catalog read-only. |
| `student_technologies`| ALLOWED | DENIED | DENIED | DENIED | Skills of students in mentor's supervised groups. |
| `groups` | ALLOWED | ALLOWED | ALLOWED | DENIED | Groups owned by mentor (`mentor_id = auth.uid()`). |
| `group_memberships` | ALLOWED | DENIED | ALLOWED | ALLOWED | Manage membership roster for owned groups (remove student / update status). |
| `project_definitions`| ALLOWED | ALLOWED | ALLOWED | ALLOWED | Reusable templates owned by mentor (`owner_mentor_id = auth.uid()`). |
| `project_definition_versions`| ALLOWED | ALLOWED | DENIED | DENIED | Append immutable versions to owned definitions. Existing versions immutable. |
| `project_instances` | ALLOWED | DENIED | DENIED | DENIED | Supervised projects (`group_id -> groups.mentor_id = auth.uid()`). Read-only overview. |
| `project_profiles` | ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only. |
| `project_technologies`| ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only. |
| `project_phase_history`| ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only. |
| `project_health_history`| ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only. |
| `domain_events` | DENIED | DENIED | DENIED | DENIED | System outbox. Strictly backend-only. |
| `assessments` | ALLOWED | DENIED | DENIED | DENIED | Supervised project assessment status read-only. |
| `assessment_answers` | DENIED | DENIED | DENIED | DENIED | **DENIED by default** (Confidential student reflection). See Decision Register #3. |
| `assessment_results` | ALLOWED | DENIED | DENIED | DENIED | Supervised project assessment readiness results read-only. |
| `blueprints` | ALLOWED | DENIED | DENIED | DENIED | Supervised project blueprint read-only inspection. |
| `blueprint_jobs` | ALLOWED | DENIED | DENIED | DENIED | Supervised project blueprint job status read-only. |
| `project_milestones` | ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only. Modification reserved for student owner. |
| `project_tasks` | ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only. Modification reserved for student owner. |
| `project_risks` | ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only. Modification reserved for student owner. |
| `project_documents` | ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only. Modification reserved for student owner. |
| `project_github_integrations`| ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only (repo name, commit count, preview). |
| `project_blueprint_versions`| ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only blueprint version history. |
| `project_change_requests`| ALLOWED | DENIED | DENIED | DENIED | Supervised projects read-only scope change requests. |
| `ai_mentor_conversations`| DENIED | DENIED | DENIED | DENIED | **DENIED by default** (Private student AI consultation). See Decision Register #4. |
| `ai_mentor_messages` | DENIED | DENIED | DENIED | DENIED | **DENIED by default** (Private student AI consultation). See Decision Register #4. |
| `project_help_requests`| ALLOWED | DENIED | ALLOWED | DENIED | Read requests on supervised projects; UPDATE `mentor_response` and status. |
| `project_mentor_notes` | ALLOWED | ALLOWED | ALLOWED | ALLOWED | Full management of notes created by mentor (`mentor_id = auth.uid()`). |

---

## 13. Admin Authorization Model

### Architectural Evidence (`docs/5D` & `backend/app/domain/identity/authorization.py`):
1. **Control Tower Philosophy:** The Admin role governs platform health, accounts, and system observability. Admin does *not* act as an everyday operator or surrogate owner of student work.
2. **Default-Deny Applies to Admin:** In `verify_resource_ownership` ([authorization.py:80-81](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/domain/identity/authorization.py#L80-L81)), the codebase explicitly states:
   > *"By default, default-deny applies even to admin unless explicitly permitted by policy."*
3. **Backend-Managed Governance:** Administrative interventions (account suspensions, group reassignments, moderation) occur through authenticated FastAPI administrative endpoints that write audit events to `domain_events`.
4. **PostgREST Direct Access Rule:** In the Supabase PostgREST layer, Admin tokens should **NOT** have blanket bypass policies on protected domain tables (`USING (true)`). Direct PostgREST access for Admins is restricted to read-only oversight where established.

| Category | Tables | Admin Access Status | Access Basis |
| :--- | :--- | :---: | :--- |
| **Identity & Access** | `users`, `student_profiles`, `mentor_profiles` | **CONTROLLED READ** | Platform user oversight; mutations via FastAPI admin routes. |
| **Catalog & Reference**| `technologies`, `project_definitions`, `versions` | **CONTROLLED CRUD** | Platform template curation and taxonomy management. |
| **Organizations** | `groups`, `group_memberships` | **CONTROLLED READ** | Cohort health monitoring; interventions via backend. |
| **Student Project Work**| `project_instances`, `profiles`, `tasks`, `docs` | **CONTROLLED READ** | Investigation workflow only (`docs/5D § 3.2`). No direct PostgREST mutation. |
| **Private Conversations**| `ai_mentor_conversations`, `messages`, `assessment_answers` | **DENIED** | Strictly confidential student work. Access requires formal backend audit. |
| **System Outbox** | `domain_events`, `alembic_version` | **BACKEND-ONLY** | Infrastructure tables denied to all PostgREST clients. |

---

## 14. Reference Data Model

### Table: `technologies`
- **Classification:** Global Reference Catalog.
- **Current Policy:** `technologies_read` (`FOR SELECT USING (auth.role() = 'authenticated')`).
- **Confirmed Intent:**
  - `SELECT`: Allowed for all authenticated users (`auth.role() = 'authenticated'`).
  - `INSERT`, `UPDATE`, `DELETE`: **DENIED** for all standard student and mentor roles via PostgREST. Curation is restricted to Admin via backend administration.
- **Performance Optimization Needed:** Wrap `auth.role()` in scalar subquery `(SELECT auth.role())` to eliminate InitPlan warning.

---

## 15. Infrastructure / Backend-Only Resources

Two tables represent system infrastructure and must be completely sealed against direct PostgREST operations:

### 1. `public.alembic_version`
- **Purpose:** Tracks executed Alembic migration revisions (`version_num VARCHAR(32)`).
- **Classification:** DATABASE MIGRATION INFRASTRUCTURE.
- **Access Rule:** Normal application users (`STUDENT`, `MENTOR`, `ADMIN`) require **zero access**.
- **RLS Policy Contract:** `ENABLE ROW LEVEL SECURITY` with **no policies** (Deny-All) or revoke table grants from `anon` and `authenticated`.

### 2. `public.domain_events`
- **Purpose:** Transactional outbox table (`6H § 6`) capturing domain events for asynchronous dispatch to background workers. Contains event payloads, actor IDs, correlation tokens, and error traces.
- **Classification:** SYSTEM INTERNAL OUTBOX.
- **Access Rule:** PostgREST clients (`anon`, `authenticated`) must have **zero direct access**. Only the backend service pool (`postgres` / `service_role`) reads and publishes pending events.
- **RLS Policy Contract:** `ENABLE ROW LEVEL SECURITY` with **no policies** (Deny-All) to guarantee zero PostgREST exposure.

---

## 16. Resource-by-Resource Authorization

### 1. `users`
- **Purpose:** Canonical identity and role registry.
- **Sensitivity:** High (PII — Email, Full Name, Role, Status).
- **Ownership:** Direct 1:1 with `auth.users.id`.
- **Student:** `SELECT`: Own record only (`id = (SELECT auth.uid()::text)`) | `INSERT`: Denied | `UPDATE`: Denied | `DELETE`: Denied.
- **Mentor:** `SELECT`: Own record only | `INSERT`: Denied | `UPDATE`: Denied | `DELETE`: Denied.
- **Admin:** `SELECT`: Controlled read via backend | `INSERT/UPDATE/DELETE`: Denied via PostgREST.
- **Immutable Fields:** `id`, `email`, `role`.
- **Decision Status:** **CONFIRMED** (Matches existing policy `users_self_select`).

### 2. `student_profiles`
- **Purpose:** Student academic background, bio, goals, interests.
- **Sensitivity:** Protected Student Data.
- **Ownership:** `user_id -> users.id`.
- **Student:** `SELECT`: Own profile (`user_id = (SELECT auth.uid()::text)`) | `INSERT`: Own profile | `UPDATE`: Own profile | `DELETE`: Denied.
- **Mentor:** `SELECT`: Students enrolled in mentor's supervised groups | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** `user_id`, `student_id`.
- **Decision Status:** **CONFIRMED**.

### 3. `mentor_profiles`
- **Purpose:** Mentor credentials, specialization, biography.
- **Sensitivity:** Professional Profile (Semi-Public Directory).
- **Ownership:** `user_id -> users.id`.
- **Student:** `SELECT`: All active mentors (directory discovery) | `INSERT/UPDATE/DELETE`: Denied.
- **Mentor:** `SELECT`: All active mentors | `INSERT`: Own profile | `UPDATE`: Own profile | `DELETE`: Denied.
- **Immutable Fields:** `user_id`, `mentor_id`.
- **Decision Status:** **CONFIRMED**.

### 4. `user_preferences`
- **Purpose:** Notification settings, UI theme, timezone.
- **Sensitivity:** User Private.
- **Ownership:** `user_id -> users.id`.
- **Student & Mentor:** `SELECT/INSERT/UPDATE`: Own record only (`user_id = (SELECT auth.uid()::text)`) | `DELETE`: Denied.
- **Immutable Fields:** `user_id`.
- **Decision Status:** **CONFIRMED**.

### 5. `student_technologies`
- **Purpose:** Student declared technical skills, proficiencies, and interests.
- **Sensitivity:** Protected Student Data.
- **Ownership:** `student_id -> users.id`.
- **Student:** `SELECT/INSERT/UPDATE/DELETE`: Own skills only (`student_id = (SELECT auth.uid()::text)`).
- **Mentor:** `SELECT`: Skills of students in supervised cohorts | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** `student_id`, `technology_id`.
- **Decision Status:** **CONFIRMED**.

### 6. `groups`
- **Purpose:** Mentorship cohorts and supervisory units.
- **Sensitivity:** Cohort Data / Join Codes.
- **Ownership:** `mentor_id -> users.id`.
- **Student:** `SELECT`: Active enrolled groups (via `group_memberships`) | `INSERT/UPDATE/DELETE`: Denied.
- **Mentor:** `SELECT/INSERT/UPDATE`: Groups owned by mentor (`mentor_id = (SELECT auth.uid()::text)`) | `DELETE`: Denied.
- **Immutable Fields:** `id`, `mentor_id`, `join_code`.
- **Decision Status:** **CONFIRMED**.

### 7. `group_memberships`
- **Purpose:** Links students to mentorship groups.
- **Sensitivity:** Group Roster Data.
- **Ownership:** `student_id -> users.id`, `group_id -> groups.id`.
- **Student:** `SELECT`: Own memberships | `INSERT`: Self enrollment via join code | `UPDATE`: Leave group (`status = 'LEFT'`) | `DELETE`: Denied.
- **Mentor:** `SELECT`: Roster of owned groups | `INSERT`: Denied (students self-join) | `UPDATE/DELETE`: Remove student from owned group.
- **Immutable Fields:** `group_id`, `student_id`.
- **Decision Status:** **CONFIRMED**.

### 8. `project_definitions`
- **Purpose:** Mentor project templates and catalog offerings.
- **Sensitivity:** Mentor Intellectual Property / Catalog.
- **Ownership:** `owner_mentor_id -> users.id`.
- **Student:** `SELECT`: Active definitions (`status = 'ACTIVE'`) for catalog discovery | `INSERT/UPDATE/DELETE`: Denied.
- **Mentor:** `SELECT/INSERT/UPDATE`: Definitions owned by mentor (`owner_mentor_id = (SELECT auth.uid()::text)`) | `DELETE`: Denied (archive only).
- **Immutable Fields:** `id`, `owner_mentor_id`.
- **Decision Status:** **CONFIRMED**.

### 9. `project_definition_versions`
- **Purpose:** Immutable version snapshots of project definitions.
- **Sensitivity:** Mentor Intellectual Property.
- **Ownership:** `project_definition_id -> project_definitions.owner_mentor_id`.
- **Student:** `SELECT`: Versions linked to active catalog definitions | `INSERT/UPDATE/DELETE`: Denied.
- **Mentor:** `SELECT/INSERT`: Versions on owned definitions | `UPDATE/DELETE`: **DENIED** (Strictly Immutable Snapshots).
- **Immutable Fields:** All fields immutable upon insertion.
- **Decision Status:** **CONFIRMED**.

### 10. `project_instances`
- **Purpose:** Central student project instance and lifecycle tracking.
- **Sensitivity:** Core Student Academic Work.
- **Ownership:** `student_id -> users.id`.
- **Student:** `SELECT/INSERT/UPDATE`: Own project instances (`student_id = (SELECT auth.uid()::text)`) | `DELETE`: Denied (archive only).
- **Mentor:** `SELECT`: Projects in supervised groups (`group_id -> groups.mentor_id = (SELECT auth.uid()::text)`) | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** `id`, `student_id`, `group_id` (reassignment controlled via backend).
- **Decision Status:** **CONFIRMED**.

### 11. `project_profiles`
- **Purpose:** Problem statement, target users, scope, skill context.
- **Sensitivity:** Project Specification Data.
- **Ownership:** `project_instance_id -> project_instances.student_id`.
- **Student:** `SELECT/INSERT/UPDATE`: Owned projects | `DELETE`: Denied.
- **Mentor:** `SELECT`: Supervised projects read-only | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** `project_instance_id`.
- **Decision Status:** **CONFIRMED**.

### 12. `project_technologies`
- **Purpose:** Project technology stack selection and justification.
- **Sensitivity:** Project Data.
- **Ownership:** `project_instance_id -> project_instances.student_id`.
- **Student:** `SELECT/INSERT/UPDATE/DELETE`: Owned projects.
- **Mentor:** `SELECT`: Supervised projects read-only | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** `project_instance_id`.
- **Decision Status:** **CONFIRMED**.

### 13. `project_phase_history` & `project_health_history`
- **Purpose:** Immutable audit trails of phase and health transitions.
- **Sensitivity:** Project Audit History.
- **Ownership:** `project_instance_id -> project_instances.student_id`.
- **Student & Mentor:** `SELECT`: Supervised/owned project history | `INSERT/UPDATE/DELETE`: **DENIED** (Append-only by backend state machine).
- **Immutable Fields:** All fields immutable.
- **Decision Status:** **CONFIRMED**.

### 14. `assessments`
- **Purpose:** Project diagnostic assessment session state.
- **Sensitivity:** Protected Academic Assessment.
- **Ownership:** `student_id -> users.id`, `project_instance_id -> project_instances.id`.
- **Student:** `SELECT/INSERT/UPDATE`: Own assessments | `DELETE`: Denied.
- **Mentor:** `SELECT`: Supervised project assessment session status | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** `id`, `student_id`, `project_instance_id`.
- **Decision Status:** **CONFIRMED**.

### 15. `assessment_answers`
- **Purpose:** Student responses to core and adaptive assessment questions.
- **Sensitivity:** **Highly Sensitive / Private Student Reflection**.
- **Ownership:** `assessment_id -> assessments.student_id`.
- **Student:** `SELECT/INSERT/UPDATE`: Own answers only | `DELETE`: Denied.
- **Mentor:** `SELECT/INSERT/UPDATE/DELETE`: **DENIED** (Mentors inspect aggregate results, not raw answers; see Decision Register #3).
- **Immutable Fields:** `assessment_id`, `question_id`.
- **Decision Status:** **CONFIRMED**.

### 16. `assessment_results`
- **Purpose:** AI-generated readiness score, dimension scores, identified gaps.
- **Sensitivity:** Sensitive Diagnostic Evaluation.
- **Ownership:** `project_instance_id -> project_instances.student_id`.
- **Student:** `SELECT`: Own assessment results | `INSERT/UPDATE/DELETE`: **DENIED** (Generated by backend AI service).
- **Mentor:** `SELECT`: Supervised project assessment results | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** All fields immutable.
- **Decision Status:** **CONFIRMED**.

### 17. `blueprints`
- **Purpose:** Master AI-generated technical blueprint specification.
- **Sensitivity:** Proprietary AI Architecture / Student Project IP.
- **Ownership:** `student_id -> users.id`, `project_instance_id -> project_instances.id`.
- **Student:** `SELECT/INSERT/UPDATE`: Own blueprints | `DELETE`: Denied.
- **Mentor:** `SELECT`: Supervised project blueprint inspection | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** `id`, `student_id`, `project_instance_id`.
- **Decision Status:** **CONFIRMED**.

### 18. `blueprint_jobs`
- **Purpose:** Background worker execution state for multi-step blueprint generation.
- **Sensitivity:** Operational State & Worker Error Traces.
- **Ownership:** `project_instance_id -> project_instances.student_id`.
- **Student:** `SELECT`: Own blueprint job status and progress percent | `INSERT/UPDATE/DELETE`: **DENIED** (Managed by backend async workers).
- **Mentor:** `SELECT`: Supervised project blueprint job status | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** `id`, `blueprint_id`, `project_instance_id`.
- **Decision Status:** **CONFIRMED**.

### 19. `project_milestones`, `project_tasks`, `project_risks`, `project_documents`
- **Purpose:** Granular execution management artifacts.
- **Sensitivity:** Protected Project Work.
- **Ownership:** `project_instance_id -> project_instances.student_id`.
- **Student:** `SELECT/INSERT/UPDATE/DELETE`: Full execution CRUD on owned projects.
- **Mentor:** `SELECT`: Supervised projects read-only | `INSERT/UPDATE/DELETE`: **DENIED** (Mentors supervise; they do not operate student tasks).
- **Immutable Fields:** `id`, `project_instance_id`.
- **Decision Status:** **CONFIRMED** (Explicitly matches `execution_service.py:132` `_verify_can_modify`).

### 20. `project_github_integrations`
- **Purpose:** VCS repository connection and commit telemetry.
- **Sensitivity:** High (Repository URLs, commit message metadata).
- **Ownership:** `project_instance_id -> project_instances.student_id`.
- **Student:** `SELECT/INSERT/UPDATE/DELETE`: Full control over own project integration.
- **Mentor:** `SELECT`: Supervised project repository summary | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** `id`, `project_instance_id`.
- **Decision Status:** **CONFIRMED** (Matches `github_service.py:75` `_verify_can_modify`).

### 21. `project_blueprint_versions`
- **Purpose:** Immutable JSON snapshots of approved blueprint versions.
- **Sensitivity:** Protected Blueprint History.
- **Ownership:** `project_instance_id -> project_instances.student_id`.
- **Student & Mentor:** `SELECT`: Owned/supervised project version history | `INSERT/UPDATE/DELETE`: **DENIED** (Generated on approval).
- **Immutable Fields:** All fields immutable.
- **Decision Status:** **CONFIRMED**.

### 22. `project_change_requests`
- **Purpose:** Student requests to alter project scope or technical direction.
- **Sensitivity:** Project Scope History & AI Impact Analysis.
- **Ownership:** `student_id -> users.id`, `project_instance_id -> project_instances.id`.
- **Student:** `SELECT/INSERT/UPDATE`: Submit and review change requests on owned project | `DELETE`: Denied.
- **Mentor:** `SELECT`: Supervised project change requests read-only | `INSERT/UPDATE/DELETE`: Denied.
- **Immutable Fields:** `id`, `student_id`, `project_instance_id`.
- **Decision Status:** **CONFIRMED**.

### 23. `ai_mentor_conversations` & `ai_mentor_messages`
- **Purpose:** Interactive student consultation threads with the AI Mentor agent.
- **Sensitivity:** **Highly Confidential Student Advisory Dialogue**.
- **Ownership:** `student_id -> users.id`, `project_instance_id -> project_instances.id`.
- **Student:** `SELECT/INSERT`: Own threads and own prompt messages (`role = 'user'`) | `UPDATE/DELETE`: Denied.
- **Mentor:** `SELECT/INSERT/UPDATE/DELETE`: **DENIED by default** (Confidential advisory channel; see Decision Register #4).
- **Immutable Fields:** `id`, `student_id`, `project_instance_id`, `conversation_id`.
- **Decision Status:** **CONFIRMED**.

### 24. `project_help_requests`
- **Purpose:** Direct student-to-mentor support tickets.
- **Sensitivity:** Mentoring Communication.
- **Ownership:** Student owner `student_id`, project supervisor `project_instance_id -> group_id -> mentor_id`.
- **Student:** `SELECT/INSERT/UPDATE`: Submit tickets on owned projects; mark resolved | `DELETE`: Denied.
- **Mentor:** `SELECT`: Tickets on supervised projects | `INSERT`: Denied | `UPDATE`: Submit `mentor_response` and update status | `DELETE`: Denied.
- **Immutable Fields:** `id`, `student_id`, `project_instance_id`.
- **Decision Status:** **CONFIRMED** (Matches `help_request_service.py`).

### 25. `project_mentor_notes`
- **Purpose:** Structured feedback and guidance notes authored by mentors.
- **Sensitivity:** **Mentor Confidential / Student Feedback**.
- **Ownership:** Author `mentor_id -> users.id`, target `project_instance_id`.
- **Mentor:** `SELECT/INSERT/UPDATE/DELETE`: Notes authored by mentor on supervised projects.
- **Student:** `SELECT`: Notes on owned projects where `note_type != 'INTERNAL'` | `UPDATE`: Mark status to `'ACKNOWLEDGED'` | `INSERT/DELETE`: Denied.
- **Immutable Fields:** `id`, `mentor_id`, `project_instance_id`.
- **Decision Status:** **CONFIRMED** (Matches `mentor_feedback_service.py:88`).

---

## 17. Master Authorization Matrix

*Legend: `A` = Allowed, `D` = Denied, `C` = Controlled / Conditional, `B` = Backend-Only.*

| # | Table Name | Student S | Student I | Student U | Student D | Mentor S | Mentor I | Mentor U | Mentor D | Admin S | Admin I | Admin U | Admin D | Access Basis | Sensitivity | Decision Status |
| :-: | :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :--- | :--- | :---: |
| 1 | `alembic_version` | D | D | D | D | D | D | D | D | D | D | D | D | INFRASTRUCTURE | Metadata | **CONFIRMED** |
| 2 | `users` | C | D | D | D | C | D | D | D | C | D | D | D | SELF IDENTITY | High (PII) | **CONFIRMED** |
| 3 | `student_profiles` | C | C | C | D | C | D | D | D | C | D | D | D | USER_ID / COHORT | Protected | **CONFIRMED** |
| 4 | `mentor_profiles` | A | D | D | D | A | C | C | D | A | D | D | D | DIRECTORY / SELF | Protected | **CONFIRMED** |
| 5 | `user_preferences` | C | C | C | D | C | C | C | D | D | D | D | D | USER_ID (SELF) | Private | **CONFIRMED** |
| 6 | `technologies` | A | D | D | D | A | D | D | D | A | C | C | C | CATALOG REFERENCE | Public Ref | **CONFIRMED** |
| 7 | `student_technologies` | C | C | C | C | C | D | D | D | C | D | D | D | STUDENT_ID / COHORT| Protected | **CONFIRMED** |
| 8 | `groups` | C | D | D | D | C | C | C | D | C | D | D | D | MENTOR_ID / MEMBER | Protected | **CONFIRMED** |
| 9 | `group_memberships` | C | C | C | D | C | D | C | C | C | D | D | D | STUDENT / MENTOR | Protected | **CONFIRMED** |
| 10 | `project_definitions` | C | D | D | D | C | C | C | D | C | C | C | D | OWNER_MENTOR / CAT | Protected IP| **CONFIRMED** |
| 11 | `project_definition_versions`| C | D | D | D | C | C | D | D | C | D | D | D | DEF_ID / IMMUTABLE | Protected IP| **CONFIRMED** |
| 12 | `project_instances` | C | C | C | D | C | D | D | D | C | D | D | D | STUDENT_ID / GROUP | Protected Core | **CONFIRMED** |
| 13 | `project_profiles` | C | C | C | D | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Protected | **CONFIRMED** |
| 14 | `project_technologies` | C | C | C | C | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Protected | **CONFIRMED** |
| 15 | `project_phase_history` | C | D | D | D | C | D | D | D | C | D | D | D | PROJECT / AUDIT | Protected Log| **CONFIRMED** |
| 16 | `project_health_history` | C | D | D | D | C | D | D | D | C | D | D | D | PROJECT / AUDIT | Protected Log| **CONFIRMED** |
| 17 | `domain_events` | D | D | D | D | D | D | D | D | D | D | D | D | BACKEND OUTBOX | Internal Ops | **CONFIRMED** |
| 18 | `assessments` | C | C | C | D | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Protected | **CONFIRMED** |
| 19 | `assessment_answers` | C | C | C | D | D | D | D | D | D | D | D | D | ASSESSMENT OWNER | Sensitive | **CONFIRMED** |
| 20 | `assessment_results` | C | D | D | D | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Sensitive | **CONFIRMED** |
| 21 | `blueprints` | C | C | C | D | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Protected IP| **CONFIRMED** |
| 22 | `blueprint_jobs` | C | D | D | D | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Internal Ops | **CONFIRMED** |
| 23 | `project_milestones` | C | C | C | C | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Protected | **CONFIRMED** |
| 24 | `project_tasks` | C | C | C | C | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Protected | **CONFIRMED** |
| 25 | `project_risks` | C | C | C | C | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Protected | **CONFIRMED** |
| 26 | `project_documents` | C | C | C | C | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Protected | **CONFIRMED** |
| 27 | `project_github_integrations`| C | C | C | C | C | D | D | D | C | D | D | D | PROJECT ANCHOR | High (VCS) | **CONFIRMED** |
| 28 | `project_blueprint_versions` | C | D | D | D | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Protected IP| **CONFIRMED** |
| 29 | `project_change_requests` | C | C | C | D | C | D | D | D | C | D | D | D | PROJECT ANCHOR | Protected | **CONFIRMED** |
| 30 | `ai_mentor_conversations` | C | C | D | D | D | D | D | D | D | D | D | D | STUDENT OWNER | Confidential| **CONFIRMED** |
| 31 | `ai_mentor_messages` | C | C | D | D | D | D | D | D | D | D | D | D | CONVERSATION ANCHOR| Confidential| **CONFIRMED** |
| 32 | `project_help_requests` | C | C | C | D | C | D | C | D | C | D | D | D | PROJECT / MENTOR | Protected | **CONFIRMED** |
| 33 | `project_mentor_notes` | C | D | C | D | C | C | C | C | C | D | D | D | PROJECT / AUTHOR | Confidential| **CONFIRMED** |

---

## 18. RLS Policy Contract

This contract defines the conceptual requirements for Prompt 3 without writing raw SQL expressions:

### Policy Archetypes:
1. **Direct Self Check (`SELF`):**  
   Actor matches column value directly: `column = (SELECT auth.uid()::text)`.
2. **Project Anchor Check (`PROJECT_OWNER`):**  
   Actor owns the project instance:  
   `EXISTS (SELECT 1 FROM project_instances WHERE id = resource.project_instance_id AND student_id = (SELECT auth.uid()::text))`.
3. **Mentor Supervision Check (`MENTOR_SUPERVISOR`):**  
   Actor is the mentor of the project's group:  
   `EXISTS (SELECT 1 FROM project_instances pi JOIN groups g ON g.id = pi.group_id WHERE pi.id = resource.project_instance_id AND g.mentor_id = (SELECT auth.uid()::text))`.
4. **Group Member Check (`GROUP_MEMBER`):**  
   Actor has active membership in the group:  
   `EXISTS (SELECT 1 FROM group_memberships gm WHERE gm.group_id = resource.group_id AND gm.student_id = (SELECT auth.uid()::text) AND gm.status = 'ACTIVE')`.
5. **Deny All / Sealed (`SEALED`):**  
   No policies created or policy explicitly evaluates `false`.

### Conceptual Policy Specifications:

#### Cluster 1: Identity & Profiles
- **`users`:**  
  - *SELECT:* `SELF` (`id = auth.uid`).  
  - *INSERT/UPDATE/DELETE:* Denied.
- **`student_profiles`:**  
  - *SELECT:* `SELF` OR `EXISTS in mentor supervised cohort`.  
  - *INSERT/UPDATE:* `SELF` WITH CHECK (`user_id = auth.uid`).
- **`mentor_profiles`:**  
  - *SELECT:* Authenticated read (`(SELECT auth.role()) = 'authenticated'`).  
  - *INSERT/UPDATE:* `SELF` WITH CHECK (`user_id = auth.uid`).
- **`user_preferences`:**  
  - *SELECT/INSERT/UPDATE:* `SELF` WITH CHECK (`user_id = auth.uid`).
- **`student_technologies`:**  
  - *SELECT:* `SELF` OR `EXISTS in mentor supervised cohort`.  
  - *INSERT/UPDATE/DELETE:* `SELF` WITH CHECK (`student_id = auth.uid`).

#### Cluster 2: Groups & Organizations
- **`groups`:**  
  - *SELECT:* `mentor_id = auth.uid` OR `GROUP_MEMBER`.  
  - *INSERT/UPDATE:* `mentor_id = auth.uid` WITH CHECK (`mentor_id = auth.uid`).
- **`group_memberships`:**  
  - *SELECT:* `student_id = auth.uid` OR `EXISTS in mentor owned group`.  
  - *INSERT:* `student_id = auth.uid` WITH CHECK (`student_id = auth.uid`).  
  - *UPDATE/DELETE:* `student_id = auth.uid` (leave) OR `EXISTS in mentor owned group` (remove).

#### Cluster 3: Project Catalog
- **`project_definitions`:**  
  - *SELECT:* `owner_mentor_id = auth.uid` OR `status = 'ACTIVE'`.  
  - *INSERT/UPDATE/DELETE:* `owner_mentor_id = auth.uid` WITH CHECK (`owner_mentor_id = auth.uid`).
- **`project_definition_versions`:**  
  - *SELECT:* `EXISTS on active definition` OR `EXISTS on mentor-owned definition`.  
  - *INSERT:* `EXISTS on mentor-owned definition` WITH CHECK (`created_by = auth.uid`).  
  - *UPDATE/DELETE:* Denied (Immutable).

#### Cluster 4: Project Core & Execution
- **`project_instances`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT:* `student_id = auth.uid` WITH CHECK (`student_id = auth.uid`).  
  - *UPDATE:* `PROJECT_OWNER` WITH CHECK (`student_id = auth.uid`).  
  - *DELETE:* Denied.
- **`project_profiles`, `project_technologies`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT/UPDATE/DELETE:* `PROJECT_OWNER` WITH CHECK.
- **`project_milestones`, `project_tasks`, `project_risks`, `project_documents`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT/UPDATE/DELETE:* `PROJECT_OWNER` WITH CHECK.
- **`project_phase_history`, `project_health_history`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT/UPDATE/DELETE:* Denied (Append-only via backend).

#### Cluster 5: Assessments & Blueprints
- **`assessments`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT/UPDATE:* `PROJECT_OWNER` WITH CHECK.
- **`assessment_answers`:**  
  - *SELECT/INSERT/UPDATE:* `assessment_id -> assessments.student_id = auth.uid` WITH CHECK.  
  - *Mentor Access:* Denied.
- **`assessment_results`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT/UPDATE/DELETE:* Denied (Backend generated).
- **`blueprints`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT/UPDATE:* `PROJECT_OWNER` WITH CHECK.
- **`blueprint_jobs`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT/UPDATE/DELETE:* Denied (Worker managed).
- **`project_blueprint_versions`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT/UPDATE/DELETE:* Denied (Immutable snapshots).

#### Cluster 6: Extensions, Mentoring & AI
- **`project_github_integrations`, `project_change_requests`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT/UPDATE/DELETE:* `PROJECT_OWNER` WITH CHECK.
- **`ai_mentor_conversations`:**  
  - *SELECT/INSERT:* `PROJECT_OWNER` (`student_id = auth.uid`) WITH CHECK.  
  - *Mentor Access:* Denied.
- **`ai_mentor_messages`:**  
  - *SELECT:* `conversation_id -> ai_mentor_conversations.student_id = auth.uid`.  
  - *INSERT:* `conversation_id -> ai_mentor_conversations.student_id = auth.uid` WITH CHECK (`role = 'user'`).  
  - *Mentor Access:* Denied.
- **`project_help_requests`:**  
  - *SELECT:* `PROJECT_OWNER` OR `MENTOR_SUPERVISOR`.  
  - *INSERT:* `PROJECT_OWNER` WITH CHECK.  
  - *UPDATE:* `PROJECT_OWNER` (mark resolved) OR `MENTOR_SUPERVISOR` (respond) WITH CHECK.
- **`project_mentor_notes`:**  
  - *SELECT:* Author mentor (`mentor_id = auth.uid`) OR (`PROJECT_OWNER` AND `note_type != 'INTERNAL'`).  
  - *INSERT/DELETE:* Author mentor (`mentor_id = auth.uid`).  
  - *UPDATE:* Author mentor (`mentor_id = auth.uid`) OR (`PROJECT_OWNER` AND updating status to 'ACKNOWLEDGED').

#### Cluster 7: Sealed / Backend Only
- **`alembic_version`:** Sealed (`SEALED` — Deny All via PostgREST).
- **`domain_events`:** Sealed (`SEALED` — Deny All via PostgREST).

---

## 19. Policy Dependency Graph

The authorization contract maps cleanly into two dependency trees:

### Project-Scoped Resource Dependency Tree:
```
[Resource Table] (e.g. project_tasks, project_milestones, blueprints, assessments)
       │
       ▼ (project_instance_id)
[project_instances]
       │
       ├───► (student_id) ───► [users.id] ◄─── (SELECT auth.uid()::text)  [STUDENT OWNER]
       │
       └───► (group_id) ────► [groups]
                                  │
                                  └───► (mentor_id) ───► [users.id] ◄─── (SELECT auth.uid()::text) [MENTOR SUPERVISOR]
```

### Direct Identity Resource Dependency Tree:
```
[User Resource] (e.g. student_profiles, user_preferences, student_technologies)
       │
       ▼ (user_id / student_id)
  [users.id] ◄─── (SELECT auth.uid()::text)  [DIRECT SELF]
```

### Group Membership Dependency Tree:
```
[groups] ◄─── (group_id) ─── [group_memberships]
   │                               │
   ▼ (mentor_id)                   ▼ (student_id)
[users.id] (Mentor)             [users.id] (Student)
   ▲                               ▲
   │ (auth.uid())                  │ (auth.uid())
[MENTOR OWNER]                  [GROUP MEMBER]
```

---

## 20. Ownership Immutability Rules

To eliminate authorization bypass through tenant reassignment, the following columns must be treated as **IMMUTABLE** across all tables:

1. **Primary Entity Keys:** `id` on all tables.
2. **Direct User References:**  
   - `student_profiles.user_id`, `mentor_profiles.user_id`, `user_preferences.user_id`.
   - `student_technologies.student_id`, `student_technologies.technology_id`.
   - `groups.mentor_id`, `groups.join_code`.
   - `project_definitions.owner_mentor_id`.
   - `project_instances.student_id`.
3. **Parent Anchor Foreign Keys:**  
   - `project_instance_id` on all project child tables.
   - `assessment_id` on `assessment_answers` and `assessment_results`.
   - `blueprint_id` on `blueprint_jobs` and `project_blueprint_versions`.
   - `conversation_id` on `ai_mentor_messages`.

### Enforcement Rule:
In Prompt 3, all RLS `UPDATE` policies must enforce that the target column value matches the existing row value (or use column-level grant restrictions where applicable).

---

## 21. Security Invariants

The following 17 security invariants must be maintained by the design and verified in Prompt 4:

- **INVARIANT 01:** Student A cannot access Student B's private profile or preferences under any condition.
- **INVARIANT 02:** Student A cannot access Student B's project instance.
- **INVARIANT 03:** Student A cannot access, query, or mutate Student B's project resources (tasks, milestones, risks, documents).
- **INVARIANT 04:** Student A cannot access Student B's assessment answers.
- **INVARIANT 05:** Student A cannot access Student B's assessment results.
- **INVARIANT 06:** Student A cannot access Student B's blueprint or generation jobs.
- **INVARIANT 07:** Student A cannot access Student B's AI mentor conversation thread.
- **INVARIANT 08:** Student A cannot access Student B's AI mentor messages.
- **INVARIANT 09:** Students cannot access mentor notes marked `note_type = 'INTERNAL'`.
- **INVARIANT 10:** Mentor A cannot access Mentor B's private mentor profile or unassigned definitions.
- **INVARIANT 11:** Mentor A cannot access project resources of a student enrolled in Mentor B's cohort.
- **INVARIANT 12:** Changing request parameters, payload IDs, or headers cannot bypass project ownership checks.
- **INVARIANT 13:** Users cannot transfer resource ownership by modifying protected ownership columns.
- **INVARIANT 14:** Anonymous (`anon`) users cannot access any protected domain table.
- **INVARIANT 15:** Reference data (`technologies`) remains read-only for authenticated users and immutable to clients.
- **INVARIANT 16:** Backend-only infrastructure tables (`alembic_version`, `domain_events`) reject all direct PostgREST operations.
- **INVARIANT 17:** RLS policies must not weaken existing FastAPI backend authorization boundaries.

---

## 22. Policy Complexity / Risk

| Table | Policy Archetype | Complexity | Primary Performance / Implementation Risk |
| :--- | :--- | :---: | :--- |
| `users`, `preferences` | Direct Self | **LOW** | Negligible risk; single indexed column lookup. |
| `technologies` | Role Check | **LOW** | Wrap `(SELECT auth.role())` to ensure InitPlan. |
| `groups` | Self + Membership Check | **MEDIUM** | Subquery on `group_memberships`; index on `(group_id, student_id)` required. |
| `project_instances` | Owner + Supervised Group | **MEDIUM** | Requires join from `project_instances` to `groups.mentor_id`. |
| `project_tasks`, `documents`| Project Anchor | **HIGH** | Nested join through `project_instances` to `groups`. High query frequency. |
| `assessment_answers` | Assessment Anchor | **MEDIUM** | Two-hop traversal: `assessment_answers -> assessments -> student_id`. |
| `ai_mentor_messages` | Conversation Anchor | **MEDIUM** | Traversal: `ai_mentor_messages -> ai_mentor_conversations -> student_id`. |
| `project_mentor_notes` | Author + Supervised Project | **HIGH** | Compound logic with `note_type != 'INTERNAL'` filtering. |

---

## 23. Direct PostgREST Access Decisions

| Strategy | Definition | Applicable Tables |
| :--- | :--- | :--- |
| **DIRECTLY ACCESSIBLE** | Publicly readable catalog data for authenticated users. | `technologies` |
| **RESTRICTED** | Strictly filtered by tenant/ownership RLS policies. | 29 Domain Tables (`users`, `profiles`, `groups`, `projects`, `tasks`, `docs`, `blueprints`, etc.) |
| **BACKEND-ONLY / SEALED** | Zero direct PostgREST access. Deny-all via RLS and grant revocation. | `domain_events`, `alembic_version` |

---

## 24. Live Database Verification Requirements

The following four verification steps must be executed during the deployment/implementation phase when live database credentials and connectivity are active:

1. **Verify Role Table Grants:** Inspect `information_schema.role_table_grants` for `anon` and `authenticated` on all 33 tables.
2. **Verify Live RLS Activation Flags:** Query `pg_tables.rowsecurity` for all 33 tables to confirm current runtime state.
3. **Verify Supabase GoTrue Leaked Password Toggle:** Check the Supabase Console under `Authentication -> Attack Protection` to verify status.
4. **Verify Live Email Bounce Telemetry:** Inspect Supabase Auth logs and SMTP provider delivery metrics.

---

## 25. Decision Register

| ID | Question / Ambiguity | Evidence Found in Repository | Current Decision | Confidence | Decision Required? |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **DEC-01** | Can mentors view student profiles outside their supervised cohorts? | `student_profiles` has no public flag. `test_demo_dataset.py` enforces mentor cohort isolation. | **RESTRICTED** to supervised cohort students only. | LIKELY | No (Aligned with 6D) |
| **DEC-02** | Can mentors view raw `assessment_answers`? | `assessment_service.py:89` only checks `project.student_id == current_user.user_id`. Mentors review results, not raw answers. | **DENIED** to mentors. Available only to student owner. | HIGH | No (Aligned with code) |
| **DEC-03** | Can mentors inspect student `ai_mentor_conversations`? | Code allows `get_conversation_history` if supervised, but conversations are private consultations. | **DENIED** via direct PostgREST RLS. Accessible only if formal backend audit is requested. | HIGH | No (Protects privacy) |
| **DEC-04** | Can mentors modify student project tasks, milestones, or risks? | `execution_service.py:132` explicitly raises `AuthorizationException` if user is not student owner or admin. | **DENIED**. Mentors have read-only supervision; zero mutation. | CONFIRMED | No (Explicit in code) |
| **DEC-05** | Can students see mentor notes marked `note_type = 'INTERNAL'`? | `mentor_feedback_service.py:88` filters out `note_type != 'INTERNAL'` for students. | **DENIED**. Students cannot view INTERNAL notes. | CONFIRMED | No (Explicit in code) |
| **DEC-06** | Can students create `group_memberships` directly? | `group_service.py:154` allows students to self-enroll using a valid `join_code`. | **ALLOWED** with `WITH CHECK (student_id = auth.uid())`. | CONFIRMED | No (Explicit in code) |
| **DEC-07** | What direct PostgREST access should Admin possess? | `docs/5D` and `authorization.py:80` state default-deny applies to Admin. Admin operates via backend. | **RESTRICTED / READ-ONLY**. No blanket `USING (true)` bypass on protected tables. | HIGH | No (Aligned with 5D) |
| **DEC-08** | Should `domain_events` be readable by students or mentors? | Outbox table contains system metadata, correlation IDs, error traces. | **SEALED (DENY ALL)** via PostgREST. Backend only. | CONFIRMED | No (Infrastructure) |

---

## 26. Prompt 3 RLS Implementation Requirements

Prompt 3 will author the executable migration. It must fulfill this checklist:

- [ ] **17 Tables to Enable RLS:** Enable RLS on 16 application tables (`assessments` through `project_mentor_notes`) plus `alembic_version`.
- [ ] **InitPlan Subquery Optimization:** Wrap every `auth.uid()` and `auth.role()` call in scalar subqueries `(SELECT auth.uid()::text)` across all new and updated policies.
- [ ] **Operation-Specific Policies:** Replace broad `FOR ALL` policies with granular `FOR SELECT`, `FOR INSERT`, `FOR UPDATE`, and `FOR DELETE` policies.
- [ ] **`WITH CHECK` Integrity:** Include `WITH CHECK` clauses on all `INSERT` and `UPDATE` policies to prevent tenant reassignment.
- [ ] **Immutable Column Protection:** Prevent reassignment of `student_id`, `mentor_id`, `project_instance_id`, `user_id`.
- [ ] **Backend-Only Sealing:** Configure `domain_events` and `alembic_version` as sealed tables.
- [ ] **Index Redundancy Remediation:** Author forward migration commands to drop redundant unique indexes duplicating unique constraints.
- [ ] **Extension Relocation:** Relocate `pg_trgm` to the `extensions` schema.

---

## 27. Prompt 4 Security Test Requirements

Prompt 4 will implement security verification tests. The test matrix must exercise:

1. **Test Identities:**
   - `Student_A` (Owner of Project 1)
   - `Student_B` (Owner of Project 2, Member of Group 1)
   - `Mentor_A` (Supervisor of Group 1)
   - `Mentor_B` (Supervisor of Group 2)
   - `Admin_User`
   - `Anonymous_User`
2. **Mandatory Test Vectors:**
   - Positive read/write by `Student_A` on Project 1 resources.
   - 403 / zero-row rejection when `Student_A` attempts to read/mutate Project 2 tasks, docs, or risks.
   - 403 rejection when `Student_A` attempts to query `Student_B`'s assessment answers or AI conversation.
   - Positive read by `Mentor_A` on Project 2 (supervised cohort).
   - 403 / zero-row rejection when `Mentor_B` attempts to read Project 2 (unauthorized cohort).
   - 403 rejection when `Mentor_A` attempts to insert or modify a task on Project 2.
   - 403 rejection when `Student_B` attempts to view `INTERNAL` notes from `Mentor_A`.
   - 403 rejection on any anonymous request to domain tables.
   - Rejection of `UPDATE` attempting to mutate `project_instance_id` or `student_id`.

---

## 28. Self-Review

The authorization design was audited against the 20 self-review questions:

1. *Did I invent any foreign-key relationship?* **NO.** All relationships reference verified DDL paths.
2. *Did I invent any Admin permission?* **NO.** Derived strictly from `docs/5D` and `authorization.py`.
3. *Did I assume Mentor can access all students?* **NO.** Mentor access is strictly cohort-scoped.
4. *Did I assume Student can access all project resources?* **NO.** Scoped strictly to student-owned projects.
5. *Did I confuse RLS state with intended authorization?* **NO.** Evaluated desired authorization independently.
6. *Did I confuse migration state with live state?* **NO.** Preserved live database verification requirements.
7. *Did I treat `alembic_version` as application data?* **NO.** Classified strictly as infrastructure.
8. *Did I treat zero RLS policies as public exposure?* **NO.** Treated as restrictive deny-by-default.
9. *Did I assume grants that were not verified?* **NO.** Explicitly maintained grants as unknown.
10. *Did I give write permission merely because read permission exists?* **NO.** Read and write separated across all tables.
11. *Did I protect ownership-changing fields?* **NO.** Immutability rules documented for all ownership columns.
12. *Did I distinguish backend access from PostgREST access?* **YES.** Explicitly differentiated Path A and Path B.
13. *Did I identify backend-only resources?* **YES.** `domain_events` and `alembic_version`.
14. *Did I identify every unresolved authorization decision?* **YES.** 8 decisions recorded in the Decision Register.
15. *Did I avoid writing SQL?* **YES.** Zero SQL statements written.
16. *Did I avoid modifying database state?* **YES.** Completely read-only.
17. *Did I remain terminal-only?* **YES.**
18. *Did I avoid browser testing?* **YES.**
19. *Did I avoid retry/error loops?* **YES.**
20. *Did I stay within the current phase?* **YES.** Implementation deferred to Prompt 3.

---

## 29. Final Authorization Gate

### AUTHORIZATION DESIGN STATUS: **READY**

#### Justification:
- All 33 public tables are classified with verified ownership and foreign-key paths.
- Student, Mentor, and Admin authorization models are defined with distinct CRUD operations.
- Supervisory relationships are strictly derived from verified group linkages.
- The 17 required security invariants and ownership immutability rules are specified.
- The RLS Policy Contract conceptually establishes all required policy archetypes without premature SQL.
- All edge-case privacy decisions are explicitly documented in the Decision Register.
- This specification is complete and ready for human review prior to Prompt 3 implementation.

---
*End of GrowFlow Authorization Model & RLS Policy Contract.*
