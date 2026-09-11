# Gate 05 — Architecture Decisions & Clarifications Record

**Gate:** Gate 05 — Core Backend / Domain Foundation  
**Status:** ACCEPTED / IMPLEMENTATION BASELINE  
**Authority Reference:** `docs/implementation/GATE_05_CORE_BACKEND_DOMAIN.md`, `docs/6A_Backend_Architecture_Final.md`, `docs/6B_Database_Architecture_and_Data_Model_Final.md`, `docs/6C_API_Architecture_Final.md`, `docs/6D_Authentication_and_Security_Architecture_Final.md`, `docs/6H_Event_Driven_Runtime_Background_Jobs_and_Reliability_Architecture_Final.md`

---

## 1. ADR-05-01: Profile Primary Key and Platform Identifiers

### Context
`docs/6B_Database_Architecture_and_Data_Model_Final.md` § 5.2 and § 5.3 specify:
- `student_profiles`: `user_id` (FK to users), `student_id` (unique platform/student identifier)
- `mentor_profiles`: `user_id` (FK to users), `mentor_id` (unique platform/mentor identifier)

### Discovered Need
In relational modeling, assigning a redundant surrogate synthetic UUID `id` to 1-to-1 profile extension tables adds unnecessary join indirection. Making `user_id` the Primary Key (which is also a Foreign Key to `users.id` ON DELETE CASCADE) guarantees strict 1-to-1 cardinality at the database level.

### Decision & Clarification
- `student_profiles.user_id` is the Primary Key (`VARCHAR(36)`), referencing `users.id` with `ON DELETE CASCADE`.
- `student_id` is a `VARCHAR(50) UNIQUE NOT NULL` platform identifier (e.g. `STU-<random8>`).
- `mentor_profiles.user_id` is the Primary Key (`VARCHAR(36)`), referencing `users.id` with `ON DELETE CASCADE`.
- `mentor_id` is a `VARCHAR(50) UNIQUE NOT NULL` platform identifier (e.g. `MEN-<random8>`).
- `user_preferences.user_id` is the Primary Key (`VARCHAR(36)`), referencing `users.id` with `ON DELETE CASCADE`.

### Impact & Classification
- **Type:** Clarification
- **Database:** Eliminates surrogate key overhead; guarantees 1:1 user-to-profile integrity.
- **API / Domain:** Cleanly aligns domain identity with `user_id`.
- **Security:** RLS policies can directly compare `user_id = auth.uid()::text`.
- **Future Gates:** Perfectly compatible with frontend profile queries.

---

## 2. ADR-05-02: Canonical Enums for Project Phase, Health, Complexity, and Statuses

### Context
`docs/6B_Database_Architecture_and_Data_Model_Final.md` defines the canonical project lifecycle in § 44, health model in § 43, complexity in § 7.2, and project definition/instance statuses in § 7.1/§ 7.3.

### Decision & Clarification
We standardize the following canonical `StrEnum` types across domain and database constraints:
1. `ProjectPhase`:
   - `IDEA`
   - `ASSESSMENT`
   - `BLUEPRINT`
   - `PLANNING`
   - `IMPLEMENTATION`
   - `TESTING`
   - `DEPLOYMENT`
   - `COMPLETED`
2. `ProjectHealth`:
   - `HEALTHY`
   - `WARNING`
   - `CRITICAL`
3. `ProjectComplexity`:
   - `BEGINNER`
   - `INTERMEDIATE`
   - `ADVANCED`
4. `ProjectStatus`:
   - `DRAFT`
   - `ACTIVE`
   - `PAUSED`
   - `COMPLETED`
   - `ARCHIVED`
5. `ProjectDefinitionStatus`:
   - `DRAFT`
   - `ACTIVE`
   - `ARCHIVED`
6. `GroupStatus`:
   - `ACTIVE`
   - `ARCHIVED`
7. `GroupMembershipStatus`:
   - `ACTIVE`
   - `LEFT`
   - `REMOVED`
8. `TechnologyRelationshipType`:
   - `KNOWN`
   - `WORKED_WITH`
   - `INTERESTED_IN`
9. `OutboxStatus`:
   - `PENDING`
   - `PUBLISHING`
   - `PUBLISHED`
   - `FAILED`

### Impact & Classification
- **Type:** Clarification
- **Database:** CHECK constraints enforce these string values.
- **API / Domain:** Enums ensure strict compile-time and runtime validation.
- **Future Gates:** Consistent contract across student, mentor, and admin flows.

---

## 3. ADR-05-03: Transactional Outbox Storage Schema

### Context
`docs/6B_Database_Architecture_and_Data_Model_Final.md` § 30 states:
"Exact outbox implementation may use the `domain_events` persistence model or a dedicated outbox table if operational requirements make that cleaner during implementation."
`docs/6H_Event_Driven_Runtime_Background_Jobs_and_Reliability_Architecture_Final.md` § 7 & § 13 defines the canonical event contract and outbox fields.

### Decision & Clarification
We unify domain event logging and transactional outbox delivery inside the single canonical `domain_events` table:
- Core event fields: `id`, `event_type`, `occurred_at`, `actor_id`, `actor_role`, `resource_type`, `resource_id`, `project_instance_id`, `group_id`, `visibility`, `metadata`, `correlation_id`.
- Outbox operational fields: `status` (`PENDING`, `PUBLISHING`, `PUBLISHED`, `FAILED`), `published_at`, `attempt_count`, `last_error`.
- Invariant: A business transaction writes its state change and enqueues `domain_events` with `status='PENDING'` within the same `AsyncSession` transaction.

### Impact & Classification
- **Type:** Clarification
- **Database:** Single normalized table, avoiding redundant dual-writes.
- **Reliability:** Guarantees zero lost events; atomic commit with business state.
- **Future Gates (Gate 15):** The background outbox publisher simply polls `domain_events WHERE status = 'PENDING'` and dispatches to handlers.

---

## 4. ADR-05-04: Row Level Security (RLS) Defense-in-Depth Policies

### Context
`docs/6B` § 33-34 and `docs/6D` § 33-34 mandate RLS as defense-in-depth across all application tables.

### Decision & Clarification
Every Gate 05 table has RLS enabled via `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`.
PostgreSQL RLS policies are installed using conditional PostgreSQL PL/pgSQL blocks (`IF EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth')`):
- `student_profiles`: `user_id = auth.uid()::text`
- `mentor_profiles`: `user_id = auth.uid()::text`
- `user_preferences`: `user_id = auth.uid()::text`
- `student_technologies`: `student_id = auth.uid()::text`
- `technologies`: Authenticated users can `SELECT`; only service-role can mutate.
- `groups`: `mentor_id = auth.uid()::text` OR student member can `SELECT`.
- `group_memberships`: `student_id = auth.uid()::text` OR mentor of group can `SELECT`/`ALL`.
- `project_definitions`: `owner_mentor_id = auth.uid()::text`.
- `project_definition_versions`: Owner mentor can `ALL`; students can `SELECT` when assigned.
- `project_instances`: `student_id = auth.uid()::text` OR group mentor can `SELECT`.
- `project_profiles`: Owner student can `ALL`; group mentor can `SELECT`.
- `project_technologies`: Owner student can `ALL`; group mentor can `SELECT`.
- `project_phase_history`: Owner student or mentor can `SELECT`.
- `project_health_history`: Owner student or mentor can `SELECT`.
- `domain_events`: Actor or associated project student/mentor can `SELECT`.

### Impact & Classification
- **Type:** Clarification
- **Security:** Strict defense-in-depth preventing cross-tenant leakage even if application layers were compromised.
