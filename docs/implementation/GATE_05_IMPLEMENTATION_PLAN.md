# GrowFlow Gate 05 — Master Implementation Plan
## Core Backend / Domain Foundation

**Gate:** Gate 05  
**Model:** Gemini 3.8 Flash (High)  
**Branch:** `gate-05/core-backend-domain`  
**Baseline Commit:** `1cd7eae` (Gate 04 merged)  
**Status:** READY FOR AUTONOMOUS EXECUTION  

---

## A. Final Gate 05 Architecture Map

```text
Presentation / API Layer
  ├── /api/v1/users/me, /api/v1/users/me/preferences
  ├── /api/v1/students/me
  ├── /api/v1/mentors/me
  ├── /api/v1/groups, /api/v1/groups/{id}, /api/v1/groups/join, /api/v1/groups/{id}/students
  ├── /api/v1/project-definitions, /versions, /archive, /assign
  └── /api/v1/projects, /api/v1/projects/{id}, /phase, /health, /overview
        │
        ▼ (Pydantic Validation & Security Dependencies)
Application Service Layer
  ├── ProfileService (User, Student, Mentor, Preferences)
  ├── GroupService (Mentor Groups, Memberships, Join Code Verification)
  ├── ProjectDefinitionService (Definitions, Version Snapshots, Assignment)
  ├── ProjectService (Instance Creation, Phase State Machine, Health Transitions, Overview Aggregator)
  └── OutboxService (Transactional Event Emission)
        │
        ▼ (Deterministic Business Rules & Domain Invariants)
Domain Layer
  ├── Identity & Profile Domain Models & Enums
  ├── Organization Domain Models (Group, Membership)
  ├── Project Domain Models & State Machines (Phase, Health, Complexity)
  └── Domain Events & Outbox Contract
        │
        ▼ (Persistence Abstractions)
Infrastructure / Repository Layer
  ├── ProfileRepository (StudentProfile, MentorProfile, UserPreference)
  ├── TechnologyRepository (Technology, StudentTechnology)
  ├── GroupRepository (Group, GroupMembership)
  ├── ProjectDefinitionRepository (ProjectDefinition, ProjectDefinitionVersion)
  ├── ProjectRepository (ProjectInstance, ProjectProfile, ProjectTechnology, Histories)
  └── OutboxRepository (DomainEvent)
        │
        ▼ (SQLAlchemy 2.0 Async ORM Models & Alembic Migration 0003)
Database Layer (PostgreSQL / Hosted Supabase)
  └── 15 Tables + Constraints + Foreign Keys + Indexes + Row Level Security (RLS)
```

---

## B. Existing Infrastructure Reused
- **Lifespan & Composition:** FastAPI application factory `create_app()` in `backend/app/main.py`.
- **Database Engine & Unit of Work:** Async SQLAlchemy 2.0 session factory and `get_db_session()` dependency (`backend/app/api/dependencies/database.py`).
- **ORM Base:** `Base`, `TimestampMixin`, `UUIDPrimaryKeyMixin`, `utcnow()` (`backend/app/infrastructure/database/base.py`).
- **Base Repository:** `BaseRepository[ModelT]` in `backend/app/infrastructure/repositories/base.py`.
- **Authentication & RBAC:** Supabase JWT verification (`backend/app/shared/security/jwt.py`), `CurrentUser`, `UserRole`, `AccountStatus` (`backend/app/domain/identity/models.py`), `verify_account_active`, `verify_role_access`, `verify_resource_ownership` (`backend/app/domain/identity/authorization.py`), and FastAPI dependencies (`get_current_user`, `CurrentUserDep`, `RequireStudent`, `RequireMentor`, `RequireAdmin`).
- **Response & Error Envelopes:** `SuccessResponse`, `ErrorResponse`, `success_response()`, `error_response()` in `backend/app/api/responses/base.py`; centralized exception handlers in `backend/app/api/responses/handlers.py`.
- **Root Router:** `api_v1_router` in `backend/app/api/router.py`.

---

## C. Every Gate 05 Domain Entity
1. `StudentProfile`: Represents student-specific biographical and academic context.
2. `MentorProfile`: Represents mentor-specific biographical and technical specialization context.
3. `UserPreference`: Represents user notification, timezone, and UI settings.
4. `Technology`: Canonical technology catalog entry.
5. `StudentTechnology`: Student's skill association with a technology (known, worked with, interested in).
6. `Group`: Mentor-created group with unique join code for student cohorts.
7. `GroupMembership`: Student membership in a group with lifecycle timestamps.
8. `ProjectDefinition`: Reusable mentor-created project template/curriculum.
9. `ProjectDefinitionVersion`: Immutable historical snapshot of a project definition.
10. `ProjectInstance`: Independent student project instance with canonical lifecycle, health, and progress.
11. `ProjectProfile`: Detailed structured application state container for a project instance.
12. `ProjectTechnology`: Technology adoption record for a project instance with architectural rationale.
13. `ProjectPhaseHistory`: Immutable audit log of lifecycle phase transitions.
14. `ProjectHealthHistory`: Immutable audit log of health transitions.
15. `DomainEvent`: Transactional outbox event record.

---

## D. Every Database Table (15 Tables)
1. `student_profiles`
2. `mentor_profiles`
3. `user_preferences`
4. `technologies`
5. `student_technologies`
6. `groups`
7. `group_memberships`
8. `project_definitions`
9. `project_definition_versions`
10. `project_instances`
11. `project_profiles`
12. `project_technologies`
13. `project_phase_history`
14. `project_health_history`
15. `domain_events`

---

## E. Every Field, Type, Constraint, and Relationship

### 1. `student_profiles`
- `user_id`: `VARCHAR(36)` PK, FK `users.id` ON DELETE CASCADE.
- `student_id`: `VARCHAR(50)` UNIQUE NOT NULL.
- `bio`: `TEXT` NULL.
- `goals`: `TEXT` NULL.
- `interests`: `TEXT` NULL.
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `updated_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().

### 2. `mentor_profiles`
- `user_id`: `VARCHAR(36)` PK, FK `users.id` ON DELETE CASCADE.
- `mentor_id`: `VARCHAR(50)` UNIQUE NOT NULL.
- `bio`: `TEXT` NULL.
- `specialization`: `TEXT` NULL.
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `updated_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().

### 3. `user_preferences`
- `user_id`: `VARCHAR(36)` PK, FK `users.id` ON DELETE CASCADE.
- `email_notifications`: `BOOLEAN` NOT NULL DEFAULT TRUE.
- `timezone`: `VARCHAR(50)` NOT NULL DEFAULT 'UTC'.
- `preferences`: `JSONB` NOT NULL DEFAULT '{}'::jsonb.
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `updated_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().

### 4. `technologies`
- `id`: `VARCHAR(36)` PK (UUID).
- `name`: `VARCHAR(100)` UNIQUE NOT NULL.
- `category`: `VARCHAR(100)` NOT NULL.
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `updated_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().

### 5. `student_technologies`
- `id`: `VARCHAR(36)` PK (UUID).
- `student_id`: `VARCHAR(36)` NOT NULL, FK `users.id` ON DELETE CASCADE.
- `technology_id`: `VARCHAR(36)` NOT NULL, FK `technologies.id` ON DELETE RESTRICT.
- `proficiency`: `VARCHAR(50)` NOT NULL DEFAULT 'INTERMEDIATE'.
- `relationship_type`: `VARCHAR(50)` NOT NULL ('KNOWN', 'WORKED_WITH', 'INTERESTED_IN').
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `updated_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- Constraint: `UNIQUE (student_id, technology_id, relationship_type)`.

### 6. `groups`
- `id`: `VARCHAR(36)` PK (UUID).
- `mentor_id`: `VARCHAR(36)` NOT NULL, FK `users.id` ON DELETE RESTRICT.
- `name`: `VARCHAR(255)` NOT NULL.
- `join_code`: `VARCHAR(50)` UNIQUE NOT NULL.
- `status`: `VARCHAR(50)` NOT NULL DEFAULT 'ACTIVE' ('ACTIVE', 'ARCHIVED').
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `updated_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().

### 7. `group_memberships`
- `id`: `VARCHAR(36)` PK (UUID).
- `group_id`: `VARCHAR(36)` NOT NULL, FK `groups.id` ON DELETE CASCADE.
- `student_id`: `VARCHAR(36)` NOT NULL, FK `users.id` ON DELETE CASCADE.
- `status`: `VARCHAR(50)` NOT NULL DEFAULT 'ACTIVE' ('ACTIVE', 'LEFT', 'REMOVED').
- `joined_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `left_at`: `TIMESTAMPTZ` NULL.
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- Constraint: `UNIQUE (group_id, student_id)`.

### 8. `project_definitions`
- `id`: `VARCHAR(36)` PK (UUID).
- `owner_mentor_id`: `VARCHAR(36)` NOT NULL, FK `users.id` ON DELETE RESTRICT.
- `name`: `VARCHAR(255)` NOT NULL.
- `status`: `VARCHAR(50)` NOT NULL DEFAULT 'DRAFT' ('DRAFT', 'ACTIVE', 'ARCHIVED').
- `current_version_id`: `VARCHAR(36)` NULL.
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `updated_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().

### 9. `project_definition_versions`
- `id`: `VARCHAR(36)` PK (UUID).
- `project_definition_id`: `VARCHAR(36)` NOT NULL, FK `project_definitions.id` ON DELETE CASCADE.
- `version_number`: `INTEGER` NOT NULL DEFAULT 1.
- `name`: `VARCHAR(255)` NOT NULL.
- `problem`: `TEXT` NOT NULL DEFAULT ''.
- `proposed_solution`: `TEXT` NOT NULL DEFAULT ''.
- `complexity`: `VARCHAR(50)` NOT NULL DEFAULT 'INTERMEDIATE'.
- `description`: `TEXT` NOT NULL DEFAULT ''.
- `duration`: `VARCHAR(100)` NOT NULL DEFAULT ''.
- `constraints`: `TEXT` NOT NULL DEFAULT ''.
- `assumptions`: `TEXT` NOT NULL DEFAULT ''.
- `technology_snapshot`: `JSONB` NOT NULL DEFAULT '[]'::jsonb.
- `created_by`: `VARCHAR(36)` NOT NULL, FK `users.id` ON DELETE RESTRICT.
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- Constraint: `UNIQUE (project_definition_id, version_number)`.

### 10. `project_instances`
- `id`: `VARCHAR(36)` PK (UUID).
- `student_id`: `VARCHAR(36)` NOT NULL, FK `users.id` ON DELETE RESTRICT.
- `group_id`: `VARCHAR(36)` NULL, FK `groups.id` ON DELETE SET NULL.
- `project_definition_id`: `VARCHAR(36)` NULL, FK `project_definitions.id` ON DELETE SET NULL.
- `source_definition_version_id`: `VARCHAR(36)` NULL, FK `project_definition_versions.id` ON DELETE SET NULL.
- `name`: `VARCHAR(255)` NOT NULL.
- `problem`: `TEXT` NOT NULL DEFAULT ''.
- `proposed_solution`: `TEXT` NOT NULL DEFAULT ''.
- `complexity`: `VARCHAR(50)` NOT NULL DEFAULT 'INTERMEDIATE'.
- `current_phase`: `VARCHAR(50)` NOT NULL DEFAULT 'IDEA'.
- `health`: `VARCHAR(50)` NOT NULL DEFAULT 'HEALTHY'.
- `progress_percentage`: `INTEGER` NOT NULL DEFAULT 0.
- `status`: `VARCHAR(50)` NOT NULL DEFAULT 'ACTIVE'.
- `deadline`: `TIMESTAMPTZ` NULL.
- `started_at`: `TIMESTAMPTZ` NULL.
- `completed_at`: `TIMESTAMPTZ` NULL.
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `updated_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- Constraint: `CHECK (progress_percentage >= 0 AND progress_percentage <= 100)`.

### 11. `project_profiles`
- `id`: `VARCHAR(36)` PK (UUID).
- `project_instance_id`: `VARCHAR(36)` NOT NULL UNIQUE, FK `project_instances.id` ON DELETE CASCADE.
- `objective`: `TEXT` NOT NULL DEFAULT ''.
- `target_users`: `TEXT` NOT NULL DEFAULT ''.
- `project_type`: `VARCHAR(100)` NOT NULL DEFAULT ''.
- `student_skill_context`: `TEXT` NOT NULL DEFAULT ''.
- `goals`: `TEXT` NOT NULL DEFAULT ''.
- `scope`: `TEXT` NOT NULL DEFAULT ''.
- `expected_outcome`: `TEXT` NOT NULL DEFAULT ''.
- `constraints`: `TEXT` NOT NULL DEFAULT ''.
- `assumptions`: `TEXT` NOT NULL DEFAULT ''.
- `context`: `TEXT` NOT NULL DEFAULT ''.
- `version`: `INTEGER` NOT NULL DEFAULT 1.
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `updated_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().

### 12. `project_technologies`
- `id`: `VARCHAR(36)` PK (UUID).
- `project_instance_id`: `VARCHAR(36)` NOT NULL, FK `project_instances.id` ON DELETE CASCADE.
- `technology_id`: `VARCHAR(36)` NOT NULL, FK `technologies.id` ON DELETE RESTRICT.
- `category`: `VARCHAR(100)` NOT NULL DEFAULT ''.
- `purpose`: `TEXT` NOT NULL DEFAULT ''.
- `why_selected`: `TEXT` NOT NULL DEFAULT ''.
- `appropriateness`: `TEXT` NOT NULL DEFAULT ''.
- `student_understanding`: `TEXT` NOT NULL DEFAULT ''.
- `usage_context`: `TEXT` NOT NULL DEFAULT ''.
- `created_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `updated_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- Constraint: `UNIQUE (project_instance_id, technology_id)`.

### 13. `project_phase_history`
- `id`: `VARCHAR(36)` PK (UUID).
- `project_instance_id`: `VARCHAR(36)` NOT NULL, FK `project_instances.id` ON DELETE CASCADE.
- `previous_phase`: `VARCHAR(50)` NOT NULL.
- `new_phase`: `VARCHAR(50)` NOT NULL.
- `changed_by`: `VARCHAR(36)` NOT NULL, FK `users.id` ON DELETE RESTRICT.
- `reason`: `TEXT` NOT NULL DEFAULT ''.
- `changed_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().

### 14. `project_health_history`
- `id`: `VARCHAR(36)` PK (UUID).
- `project_instance_id`: `VARCHAR(36)` NOT NULL, FK `project_instances.id` ON DELETE CASCADE.
- `previous_health`: `VARCHAR(50)` NOT NULL.
- `new_health`: `VARCHAR(50)` NOT NULL.
- `changed_by`: `VARCHAR(36)` NOT NULL, FK `users.id` ON DELETE RESTRICT.
- `reason`: `TEXT` NOT NULL DEFAULT ''.
- `changed_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().

### 15. `domain_events` (Transactional Outbox)
- `id`: `VARCHAR(36)` PK (UUID).
- `event_type`: `VARCHAR(100)` NOT NULL.
- `actor_id`: `VARCHAR(36)` NULL, FK `users.id` ON DELETE SET NULL.
- `actor_role`: `VARCHAR(50)` NOT NULL.
- `resource_type`: `VARCHAR(100)` NOT NULL.
- `resource_id`: `VARCHAR(36)` NOT NULL.
- `project_instance_id`: `VARCHAR(36)` NULL, FK `project_instances.id` ON DELETE SET NULL.
- `group_id`: `VARCHAR(36)` NULL, FK `groups.id` ON DELETE SET NULL.
- `visibility`: `VARCHAR(50)` NOT NULL DEFAULT 'INTERNAL'.
- `metadata`: `JSONB` NOT NULL DEFAULT '{}'::jsonb.
- `correlation_id`: `VARCHAR(100)` NOT NULL DEFAULT ''.
- `status`: `VARCHAR(50)` NOT NULL DEFAULT 'PENDING'.
- `occurred_at`: `TIMESTAMPTZ` NOT NULL DEFAULT NOW().
- `processed_at`: `TIMESTAMPTZ` NULL.
- `attempt_count`: `INTEGER` NOT NULL DEFAULT 0.
- `last_error`: `TEXT` NULL.

---

## F. Every FK and Delete Behavior
- `CASCADE`: Used strictly where child entity existence has no independent meaning (e.g. `student_profiles` -> `users`, `mentor_profiles` -> `users`, `user_preferences` -> `users`, `project_definition_versions` -> `project_definitions`, `project_profiles` -> `project_instances`, `project_technologies` -> `project_instances`, `project_phase_history` -> `project_instances`, `project_health_history` -> `project_instances`, `group_memberships` -> `groups`/`users`).
- `RESTRICT`: Used to protect authoritative history and associations from accidental deletion (e.g. `technologies` in `student_technologies`/`project_technologies`, `owner_mentor_id` in `project_definitions`, `student_id` in `project_instances`, `changed_by` in histories).
- `SET NULL`: Used for nullable contextual links where the parent entity can be removed or unlinked without destroying the project instance (e.g. `group_id`, `project_definition_id`, `source_definition_version_id` in `project_instances`, and audit/actor/project references in `domain_events`).

---

## G. Every Required Index and Unique Constraint
- `student_profiles`: Unique `student_id`, index on `student_id`.
- `mentor_profiles`: Unique `mentor_id`, index on `mentor_id`.
- `technologies`: Unique `name`, index on `category`.
- `student_technologies`: Unique `(student_id, technology_id, relationship_type)`.
- `groups`: Unique `join_code`, indexes on `mentor_id`, `join_code`, `status`.
- `group_memberships`: Unique `(group_id, student_id)`, indexes on `group_id`, `student_id`, `status`.
- `project_definitions`: Indexes on `owner_mentor_id`, `status`.
- `project_definition_versions`: Unique `(project_definition_id, version_number)`, index on `project_definition_id`.
- `project_instances`: Indexes on `student_id`, `group_id`, `project_definition_id`, `status`, `current_phase`, `health`.
- `project_profiles`: Unique `project_instance_id`, index on `project_instance_id`.
- `project_technologies`: Unique `(project_instance_id, technology_id)`, index on `project_instance_id`.
- `project_phase_history`: Index on `project_instance_id`.
- `project_health_history`: Index on `project_instance_id`.
- `domain_events`: Indexes on `event_type`, `project_instance_id`, `group_id`, `status`, `occurred_at`.

---

## H. RLS Strategy for Every Table
- `ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;` on all 15 tables.
- Defense-in-depth policies matching Supabase `auth.uid()::text`:
  - `student_profiles`: `user_id = auth.uid()::text`
  - `mentor_profiles`: `user_id = auth.uid()::text`
  - `user_preferences`: `user_id = auth.uid()::text`
  - `student_technologies`: `student_id = auth.uid()::text`
  - `technologies`: Authenticated users can `SELECT`.
  - `groups`: `mentor_id = auth.uid()::text` OR student member can `SELECT`.
  - `group_memberships`: `student_id = auth.uid()::text` OR mentor of group can `SELECT`/`ALL`.
  - `project_definitions`: `owner_mentor_id = auth.uid()::text`.
  - `project_definition_versions`: Owner mentor can `ALL`; assigned student can `SELECT`.
  - `project_instances`: `student_id = auth.uid()::text` OR group mentor can `SELECT`.
  - `project_profiles`: Owner student can `ALL`; group mentor can `SELECT`.
  - `project_technologies`: Owner student can `ALL`; group mentor can `SELECT`.
  - `project_phase_history`: Owner student or group mentor can `SELECT`.
  - `project_health_history`: Owner student or group mentor can `SELECT`.
  - `domain_events`: Actor or associated project student/mentor can `SELECT`.

---

## I. Domain Enums and State Machines

### 1. Project Phase State Machine
Allowed transitions:
- `IDEA` → `ASSESSMENT`
- `ASSESSMENT` → `BLUEPRINT`
- `BLUEPRINT` → `PLANNING`
- `PLANNING` → `IMPLEMENTATION`
- `IMPLEMENTATION` → `TESTING`
- `TESTING` → `DEPLOYMENT`
- `DEPLOYMENT` → `COMPLETED`
Invalid jumps (e.g. `IDEA` → `IMPLEMENTATION`) are strictly rejected with `BusinessRuleException` (`PROJECT_INVALID_PHASE_TRANSITION`).

### 2. Project Health
- `HEALTHY` (default)
- `WARNING`
- `CRITICAL`
Transitions record previous and new health in `project_health_history` with audit trail and reason.

### 3. Project Complexity
- `BEGINNER`
- `INTERMEDIATE`
- `ADVANCED`

### 4. Status Enums
- `ProjectStatus`: `DRAFT`, `ACTIVE`, `PAUSED`, `COMPLETED`, `ARCHIVED`
- `ProjectDefinitionStatus`: `DRAFT`, `ACTIVE`, `ARCHIVED`
- `GroupStatus`: `ACTIVE`, `ARCHIVED`
- `GroupMembershipStatus`: `ACTIVE`, `LEFT`, `REMOVED`
- `OutboxStatus`: `PENDING`, `PUBLISHING`, `PUBLISHED`, `FAILED`

---

## J. Repository Responsibilities
- `ProfileRepository`: Manages queries and persistence for `StudentProfileModel`, `MentorProfileModel`, and `UserPreferenceModel`.
- `TechnologyRepository`: Manages queries for `TechnologyModel` catalogue and `StudentTechnologyModel` relationships.
- `GroupRepository`: Manages `GroupModel` and `GroupMembershipModel`, join code lookups, student membership checks.
- `ProjectDefinitionRepository`: Manages `ProjectDefinitionModel` and immutable `ProjectDefinitionVersionModel` snapshots.
- `ProjectRepository`: Manages `ProjectInstanceModel`, `ProjectProfileModel`, `ProjectTechnologyModel`, `ProjectPhaseHistoryModel`, `ProjectHealthHistoryModel`.
- `OutboxRepository`: Manages `DomainEventModel` persistence within active database transactions.

---

## K. Service Responsibilities
- `ProfileService`:
  - Retrieves/updates current user profile, student profile with technology proficiencies, mentor profile with specializations, and user preferences.
- `GroupService`:
  - Enforces mentor role to create groups.
  - Generates secure random unique join code.
  - Enforces student role to join groups via join code.
  - Prevents duplicate active group membership.
  - Emits `GroupCreated` and `StudentJoinedGroup` events.
- `ProjectDefinitionService`:
  - Enforces mentor role to create definitions and publish version 1.
  - Supports updating definitions by creating new immutable versions (`version_number + 1`).
  - Supports archiving definitions.
  - Implements assignment of a definition to a student/group: creates an independent `ProjectInstanceModel`, copies definition snapshot into a new `ProjectProfileModel`, and emits `ProjectDefinitionAssigned`.
  - Invariant: Updating a definition does NOT mutate existing student project instances.
- `ProjectService`:
  - Student creates standalone project instance (`IDEA`, `HEALTHY`, 0%).
  - Retrieves project instance with strict authorization check (student owner or mentor of student's group).
  - Lists projects scoped strictly to caller's identity (students see only their own; mentors see assigned group projects).
  - Updates project instance details.
  - Enforces canonical phase transitions; records phase history; emits `ProjectPhaseChanged`.
  - Updates project health; records health history; emits `ProjectHealthChanged`.
  - Overview Query Aggregator: aggregates project identity, phase, health, progress percentage, deadline, days remaining, technologies, and recent activity into canonical response contract.
- `OutboxService`:
  - Enqueues `DomainEventModel` instances atomically inside the current active database session unit of work.

---

## L. Transaction Boundaries
- All state changes (e.g. `ProjectInstance` update + `ProjectPhaseHistory` + `DomainEvent`) are executed within a single database transaction.
- Repositories call `session.add()` and `session.flush()`.
- The application unit of work (`get_session_context()`) commits or rolls back atomically.
- If an exception occurs, the transaction rolls back completely, ensuring no orphaned outbox events or partial database records.

---

## M. API Endpoints
- `GET  /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `GET  /api/v1/users/me/preferences`
- `PATCH /api/v1/users/me/preferences`
- `GET  /api/v1/students/me`
- `PATCH /api/v1/students/me`
- `GET  /api/v1/mentors/me`
- `PATCH /api/v1/mentors/me`
- `POST /api/v1/groups`
- `GET  /api/v1/groups`
- `GET  /api/v1/groups/{group_id}`
- `PATCH /api/v1/groups/{group_id}`
- `POST /api/v1/groups/join`
- `GET  /api/v1/groups/{group_id}/students`
- `POST /api/v1/project-definitions`
- `GET  /api/v1/project-definitions`
- `GET  /api/v1/project-definitions/{definition_id}`
- `PATCH /api/v1/project-definitions/{definition_id}`
- `POST /api/v1/project-definitions/{definition_id}/archive`
- `GET  /api/v1/project-definitions/{definition_id}/versions`
- `GET  /api/v1/project-definitions/{definition_id}/versions/{version_id}`
- `POST /api/v1/project-definitions/{definition_id}/assign`
- `POST /api/v1/projects`
- `GET  /api/v1/projects`
- `GET  /api/v1/projects/{project_id}`
- `PATCH /api/v1/projects/{project_id}`
- `GET  /api/v1/projects/{project_id}/overview`
- `POST /api/v1/projects/{project_id}/phase`
- `POST /api/v1/projects/{project_id}/health`

---

## N. Request / Response Schemas
- Defined in `backend/app/api/schemas/`:
  - `profile.py`: `UserUpdateSchema`, `StudentProfileSchema`, `StudentProfileUpdateSchema`, `MentorProfileSchema`, `MentorProfileUpdateSchema`, `UserPreferencesSchema`, `UserPreferencesUpdateSchema`.
  - `group.py`: `GroupCreateSchema`, `GroupUpdateSchema`, `GroupResponseSchema`, `GroupJoinSchema`, `GroupStudentResponseSchema`.
  - `project_definition.py`: `ProjectDefinitionCreateSchema`, `ProjectDefinitionUpdateSchema`, `ProjectDefinitionResponseSchema`, `ProjectDefinitionVersionResponseSchema`, `ProjectDefinitionAssignSchema`.
  - `project.py`: `ProjectCreateSchema`, `ProjectUpdateSchema`, `ProjectResponseSchema`, `ProjectPhaseTransitionSchema`, `ProjectHealthUpdateSchema`, `ProjectOverviewResponseSchema`.

---

## O. Authentication Requirements
- All endpoints require valid JWT Bearer tokens verified via `SupabaseJWTVerifier`.
- Injected `CurrentUser` must be in `AccountStatus.ACTIVE`.

---

## P. Resource Authorization Rules
- `users/me`, `users/me/preferences`, `students/me`, `mentors/me`: Self-identity only (`user_id = current_user.user_id`).
- `groups` create, update, archive: `RequireMentor`, mentor must be the owner of the group (`mentor_id = current_user.user_id`).
- `groups/join`: `RequireStudent`.
- `groups/{id}/students`: Mentor owner OR active student member.
- `project-definitions` create, update, archive, assign: `RequireMentor`, mentor must be the owner.
- `projects` create: `RequireStudent`.
- `projects/{id}` read, update, overview, phase transition:
  - Students: Must be the project owner (`student_id = current_user.user_id`).
  - Mentors: Must be the mentor of the group to which the project instance belongs.
  - Cross-student access is strictly denied (HTTP 403 `AUTH_FORBIDDEN_RESOURCE`).

---

## Q. Domain Event Contracts
Canonical fields:
`event_id`, `event_type`, `occurred_at`, `actor_id`, `actor_role`, `resource_type`, `resource_id`, `project_instance_id`, `group_id`, `visibility`, `metadata`, `correlation_id`.
Events emitted in Gate 05:
- `ProjectCreated`
- `ProjectPhaseChanged`
- `ProjectHealthChanged`
- `GroupCreated`
- `StudentJoinedGroup`
- `ProjectDefinitionCreated`
- `ProjectDefinitionAssigned`

---

## R. Transactional Outbox Behavior
- State change + `domain_events` insertion are executed within the same database transaction.
- Status starts as `PENDING`.
- No distributed event broker; atomicity guaranteed by PostgreSQL ACID transaction.

---

## S. Required Tests
- Domain unit tests: enums, invariants, state machine transitions, invalid transitions rejected.
- Repository unit/integration tests: CRUD, unique constraints, foreign keys, version snapshots.
- Service unit tests: business invariants, definition versioning independence, outbox emission.
- API tests: authentication, RBAC, resource authorization, cross-student isolation, canonical response envelope conformity.
- Database & Migration tests: migration 0003 upgrade and downgrade integrity, RLS verification.

---

## T. Migration Strategy
- Migration: `backend/migrations/versions/0003_gate05_core_domain.py`.
- Reversion: chains from `0002_gate04_users`.
- Additive only; no data loss; safely idempotent RLS policy creation.

---

## U. Git / Commit Strategy
- Feature branch: `gate-05/core-backend-domain`.
- Incremental focused commits adhering to conventional commit format (`build(gate-05): ...`, `test(gate-05): ...`).
- Human review and merge protocol.

---

## V. Gate 05 Exclusions
- Assessment system, blueprint generation, tasks/milestones/risks, documents/RAG, external integrations (GitHub/Tavily), mentor review UI, admin investigations, background worker loops, frontend UI.

---

## W. Dependencies Between Implementation Units
- Unit 01 (Domain models) → Unit 02 (ORM models) → Unit 03 (Migration) → Unit 04 (Repositories) → Unit 05 (Services) → Unit 06 (Schemas) → Unit 07 (Routes) → Unit 08 (Unit Tests) → Unit 09 (API/Integration Tests) → Unit 10 (Live Migration & Evidence).

---

## X. Architecture Risks / Ambiguities Discovered During Planning
- None unresolved. All clarifications documented in `GATE_05_ARCHITECTURE_DECISIONS.md`.
