# GrowFlow — Gate 10 Analysis
## Project Planning & Execution Foundation

**Branch:** `gate-10/project-planning`
**Mode:** ANALYSIS-ONLY — No code changes made
**Document:** `docs/gate10_analysis.md`
**Date:** 2026-09-20

---

## 1. Executive Summary

Gate 10 defines the canonical transition from the AI-generated and QA-approved Blueprint (Gate 09 output)
into a persistent, deterministic Student Planning System (SPS). It encompasses: idempotent materialisation
of Tasks, Milestones, Risks, and Documents from Blueprint content; full CRUD lifecycle for those entities;
a deterministic Roadmap Projection engine; a Phase Transition (BLUEPRINT to PLANNING); and all
student-facing execution management UI surfaces.

A complete audit was performed across the database, migration, domain, service, API, repository, test,
and frontend layers. Each Gate 10 component is classified as IMPLEMENTED, PARTIAL, or MISSING.
All required implementation units are enumerated in priority order.

**Overall status: SUBSTANTIALLY IMPLEMENTED — Critical gap: phase auto-transition on blueprint approval is absent**

---

## 2. Authoritative Architecture References

| Ref | Title |
|-----|-------|
| `docs/implementation/GATE_10_PLANNING_EXECUTION_SYSTEM.md` | Gate 10 specification and prerequisites |
| `docs/FRONTEND_BACKEND_CONTRACT.md` §975-1200, §1503-1650 | Execution domain API contract |
| `6B §20 & §44` | Execution entities: milestones, tasks, risks, documents |
| `6B §44` | Canonical phase model and `project_phase_history` |
| `6C §13` | Project Instance APIs |
| `6A §9` | Class-based service architecture |
| `6D §33-34` | RLS and security hardening |

---

## 3. Prerequisite Gate 09 Status

Gate 10 depends on Gate 09 (AI Blueprint & Agent System) being complete and verified.

| Prerequisite | Evidence | Status |
|---|---|---|
| `BlueprintStatus.APPROVED` lifecycle state exists | `blueprint/models.py:38` | IMPLEMENTED |
| `blueprint_service.approve_blueprint()` persists approval, emits `BlueprintApproved` event | `blueprint_service.py:387-430` | IMPLEMENTED |
| `blueprint_repository.approve_blueprint()` sets `status=APPROVED`, `approved_at=now()` | `blueprint_repository.py:145-153` | IMPLEMENTED |
| `DomainEventType.BLUEPRINT_APPROVED` defined | `domain_event.py:34` | IMPLEMENTED |
| Gate 09 Unit 6 evidence doc exists | `docs/implementation/GATE_09_UNIT_6_EVIDENCE.md` | VERIFIED |

---

## 4. Database Layer Audit

### 4.1 Migration: `0006_gate10_execution_management.py`

| Table | Key Columns | Status |
|---|---|---|
| `project_milestones` | id, project_instance_id (FK CASCADE), title, description, gate_code, target_date, status, progress_percent, deliverables (JSONB), section_order, timestamps | IMPLEMENTED |
| `project_tasks` | id, project_instance_id (FK CASCADE), milestone_id (FK SET NULL), task_code, title, description, status, priority, category, phase, due_date, dependencies (JSONB), acceptance_criteria (JSONB), completed_at, timestamps | IMPLEMENTED |
| `project_risks` | id, project_instance_id (FK CASCADE), risk_code, title, description, severity, probability, impact, status, mitigation, owner, review_date, timestamps | IMPLEMENTED |
| `project_documents` | id, project_instance_id (FK CASCADE), document_key, title, doc_type, format, content, version, status, source, timestamps | IMPLEMENTED |

Database schema is complete and production-grade.

### 4.2 RLS Policy Audit: `0008_gate12_rls_hardening.py`

All four Gate 10 tables (`project_milestones`, `project_tasks`, `project_risks`, `project_documents`) are
present in the `tables_to_enable_rls` list (migration lines 75-78). RLS is enabled on all four via
`ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY`. Granular per-row data-access policies are installed
defensively within a `DO $$ IF EXISTS pg_namespace.auth` block covering all 17 RLS tables.

**Verdict:** RLS is fully provisioned for Gate 10 tables in Gate 12 migration. IMPLEMENTED.

### 4.3 ORM Models: `backend/app/infrastructure/database/models/execution.py`

| Model | Table | Relationships | Status |
|---|---|---|---|
| `ProjectMilestoneModel` | `project_milestones` | tasks (cascade all, delete-orphan) | IMPLEMENTED |
| `ProjectTaskModel` | `project_tasks` | milestone (back_populates) | IMPLEMENTED |
| `ProjectRiskModel` | `project_risks` | none | IMPLEMENTED |
| `ProjectDocumentModel` | `project_documents` | none | IMPLEMENTED |

---

## 5. Backend Domain and Service Layer Audit

### 5.1 Idempotent Blueprint to Execution Materialisation

**File:** `backend/app/application/services/execution_service.py` — `ensure_initialized()` (lines 130-444)

| Behaviour | Implementation | Status |
|---|---|---|
| Guard: early-return if milestones OR tasks already exist | `count_by_project > 0 → return` | IMPLEMENTED |
| Guard: early-return if no blueprint with content | `latest_bp is None or no content → return` | IMPLEMENTED |
| Milestone materialisation from `content["milestones"]["milestones_schedule"]` | Lines 152-205 | IMPLEMENTED |
| Default 4-milestone fallback (M1-M4) if no blueprint schedule | Lines 183-204 | IMPLEMENTED |
| Task materialisation from `content["tasks"]["tasks_breakdown"]` | Lines 208-273 | IMPLEMENTED |
| Default 6-task fallback if no blueprint tasks | Lines 247-271 | IMPLEMENTED |
| Risk materialisation from `content["risks"]["technical_risks"]` | Lines 275-331 | IMPLEMENTED |
| Default 3-risk fallback if no blueprint risks | Lines 308-329 | IMPLEMENTED |
| Document initialisation (master_blueprint, technical_specifications, project_readme) | Lines 333-436 | IMPLEMENTED |
| Tasks linked deterministically to milestones via `milestone_keys[idx % len(milestone_keys)]` | Line 223 | IMPLEMENTED |
| All bulk_create calls are transactional (SQLAlchemy flush) | `session.add_all + flush` | IMPLEMENTED |
| Guard: `blueprint.status == APPROVED` before materialising | **NOT FOUND** | MISSING (Gap G1) |

**Critical gap (G1):** `ensure_initialized()` checks only that `latest_bp.content` is non-empty.
A blueprint in `READY_FOR_APPROVAL` state with content will also trigger materialisation, violating
the Gate 10 authority boundary which requires student explicit approval first.

**Classification: PARTIAL**

### 5.2 Phase Transition: BLUEPRINT to PLANNING

Required by Gate 10: when the blueprint is approved, the project must transition from `BLUEPRINT` to `PLANNING`.

| Check | Finding | Status |
|---|---|---|
| `ProjectPhase.PLANNING` enum value defined | `project/models.py:39` | IMPLEMENTED |
| `can_transition_phase(BLUEPRINT, PLANNING)` via canonical state machine | `CANONICAL_NEXT_PHASE` dict | IMPLEMENTED |
| `project_service.transition_phase()` method exists | `project_service.py:270-333` | IMPLEMENTED |
| `approve_blueprint()` in `blueprint_service.py` calls `transition_phase("PLANNING")` | NOT FOUND | MISSING (Gap G2) |
| Phase transition recorded in `project_phase_history` | Would be handled by `transition_phase()` | NOT TRIGGERED |

**Finding (G2):** `blueprint_service.approve_blueprint()` (lines 387-430) emits `BLUEPRINT_APPROVED` and
persists the approval timestamp but does NOT call `project_service.transition_phase()`. After blueprint
approval, the project instance remains in `BLUEPRINT` phase. The `ProjectService` reference is already
injected as `self._project_service` in `BlueprintService.__init__()`.

**Classification: MISSING — CRITICAL**

### 5.3 Task CRUD (S18 and S19)

| Operation | Service Method | Status |
|---|---|---|
| List tasks with filters (status, priority, milestone_id, phase, search) | `list_tasks()` | IMPLEMENTED |
| Get task by ID | `get_task()` | IMPLEMENTED |
| Create task | `create_task()` | IMPLEMENTED |
| Update task (partial PATCH; completed_at auto-set on COMPLETED) | `update_task()` | IMPLEMENTED |
| Delete task | `delete_task()` | IMPLEMENTED |
| Milestone progress recalculation on task change | `_recalculate_milestone_progress()` | IMPLEMENTED |
| Project progress recalculation (35% base + 65% x task completion) | `_recalculate_project_progress()` | IMPLEMENTED |
| Domain events: TASK_CREATED, TASK_UPDATED, TASK_COMPLETED | Outbox emissions | IMPLEMENTED |

### 5.4 Milestone CRUD (S20 and S21)

| Operation | Service Method | Status |
|---|---|---|
| List milestones with task grouping | `list_milestones()` | IMPLEMENTED |
| Get milestone with task breakdown | `get_milestone()` | IMPLEMENTED |
| Create milestone | `create_milestone()` | IMPLEMENTED |
| Update milestone | `update_milestone()` | IMPLEMENTED |
| Delete milestone | NOT FOUND | PARTIAL (Gap G3) |
| Domain event: MILESTONE_UPDATED | Outbox emission | IMPLEMENTED |

**Finding (G3):** `delete_milestone()` does not exist in `ExecutionService`. No route exposes DELETE for
milestones. `StudentMilestones.tsx` does not render a delete action, consistent with this gap.
May be intentional scope exclusion — requires spec confirmation.

**Classification: PARTIAL**

### 5.5 Risk CRUD (S22 and S23)

| Operation | Service Method | Status |
|---|---|---|
| List risks with filters (status, severity, search) | `list_risks()` | IMPLEMENTED |
| Get risk by ID | `get_risk()` | IMPLEMENTED |
| Create risk | `create_risk()` | IMPLEMENTED |
| Update risk | `update_risk()` | IMPLEMENTED |
| Delete risk | `delete_risk()` | IMPLEMENTED |
| Domain events: RISK_CREATED, RISK_UPDATED | Outbox emissions | IMPLEMENTED |

### 5.6 Roadmap Projection Engine (S24)

| Capability | Implementation | Status |
|---|---|---|
| Aggregate milestones and tasks into deterministic projection | `get_roadmap()` | IMPLEMENTED |
| Task classification: overdue, blocked, in_progress, upcoming, completed | Lines 966-990 | IMPLEMENTED |
| Milestone completion detection (status or all-tasks-completed) | Lines 996-999 | IMPLEMENTED |
| Summary: total/completed milestones, tasks, overdue count, overall_progress | `RoadmapSummary` | IMPLEMENTED |
| Grouped tasks response envelope | `RoadmapGroupedTasks` | IMPLEMENTED |

### 5.7 Document Lifecycle (S25 and S26)

| Operation | Status |
|---|---|
| List documents with filters (doc_type, status, search) | IMPLEMENTED |
| Get document by ID | IMPLEMENTED |
| Create document | IMPLEMENTED |
| Update document (title, content with version bump, status) | IMPLEMENTED |
| Download raw Markdown (`/download`) | IMPLEMENTED |
| Version auto-increment on content change (e.g. 1.0 to 1.1) | IMPLEMENTED |
| Domain events: DOCUMENT_CREATED, DOCUMENT_UPDATED | IMPLEMENTED |

---

## 6. API Layer Audit

**File:** `backend/app/api/routes/execution.py`
**Prefix:** `/projects/{project_id}`

| Route | Method | Handler | Status |
|---|---|---|---|
| `/tasks` | GET | `list_tasks` | IMPLEMENTED |
| `/tasks` | POST | `create_task` | IMPLEMENTED |
| `/tasks/{task_id}` | GET | `get_task` | IMPLEMENTED |
| `/tasks/{task_id}` | PATCH | `update_task` | IMPLEMENTED |
| `/tasks/{task_id}` | DELETE | `delete_task` | IMPLEMENTED |
| `/milestones` | GET | `list_milestones` | IMPLEMENTED |
| `/milestones` | POST | `create_milestone` | IMPLEMENTED |
| `/milestones/{milestone_id}` | GET | `get_milestone` | IMPLEMENTED |
| `/milestones/{milestone_id}` | PATCH | `update_milestone` | IMPLEMENTED |
| `/milestones/{milestone_id}` | DELETE | NOT REGISTERED | MISSING (Gap G3) |
| `/risks` | GET | `list_risks` | IMPLEMENTED |
| `/risks` | POST | `create_risk` | IMPLEMENTED |
| `/risks/{risk_id}` | GET | `get_risk` | IMPLEMENTED |
| `/risks/{risk_id}` | PATCH | `update_risk` | IMPLEMENTED |
| `/risks/{risk_id}` | DELETE | `delete_risk` | IMPLEMENTED |
| `/roadmap` | GET | `get_roadmap` | IMPLEMENTED |
| `/documents` | GET | `list_documents` | IMPLEMENTED |
| `/documents` | POST | `create_document` | IMPLEMENTED |
| `/documents/{document_id}` | GET | `get_document` | IMPLEMENTED |
| `/documents/{document_id}` | PATCH | `update_document` | IMPLEMENTED |
| `/documents/{document_id}/download` | GET | `download_raw_document` | IMPLEMENTED |

20 of 21 execution endpoints implemented. Auth uses `CurrentUserDep` (any authenticated user),
correct for mentor read access.

---

## 7. Repository Layer Audit

**File:** `backend/app/infrastructure/repositories/execution_repository.py`

| Repository | Implemented Methods | Missing | Status |
|---|---|---|---|
| `MilestoneRepository` | `list_by_project`, `get_by_id`, `count_by_project`, `bulk_create` | `delete_by_id` | PARTIAL |
| `TaskRepository` | `list_by_project` (filtered), `get_by_id`, `count_by_project`, `count_completed_by_project`, `bulk_create`, `delete_by_id` | none | IMPLEMENTED |
| `RiskRepository` | `list_by_project` (filtered), `get_by_id`, `count_by_project`, `bulk_create`, `delete_by_id` | none | IMPLEMENTED |
| `DocumentRepository` | `list_by_project` (filtered), `get_by_id`, `get_by_key`, `count_by_project`, `bulk_create`, `list_platform_documents`, `count_platform_documents` | none | IMPLEMENTED |

---

## 8. API Schema Audit

**File:** `backend/app/api/schemas/execution.py`

| Schema | Fields | Status |
|---|---|---|
| `TaskCreatePayload` | title, priority, phase, milestone_id, due_date, dependencies, acceptance_criteria | IMPLEMENTED |
| `TaskUpdatePayload` | all fields optional for PATCH | IMPLEMENTED |
| `TaskResponse` | id, task_code, status, completed_at, all fields | IMPLEMENTED |
| `MilestoneCreatePayload` | title, description, gate_code, target_date, deliverables | IMPLEMENTED |
| `MilestoneUpdatePayload` | all fields optional | IMPLEMENTED |
| `MilestoneResponse` | id, task_count, completed_task_count, nested tasks list | IMPLEMENTED |
| `RiskCreatePayload` | title, severity, probability, impact, mitigation, owner | IMPLEMENTED |
| `RiskUpdatePayload` | all fields optional | IMPLEMENTED |
| `RiskResponse` | id, risk_code, all fields | IMPLEMENTED |
| `RoadmapSummary` | total/completed milestones, tasks, overdue_count, blocked_count, overall_progress | IMPLEMENTED |
| `RoadmapMilestoneItem` | id, gate_code, tasks list | IMPLEMENTED |
| `RoadmapGroupedTasks` | overdue, blocked, in_progress, upcoming, completed buckets | IMPLEMENTED |
| `RoadmapResponse` | project_id, project_name, current_phase, summary, milestones, grouped_tasks | IMPLEMENTED |
| `DocumentCreatePayload` | title, doc_type, format, content | IMPLEMENTED |
| `DocumentUpdatePayload` | title, content, status (optional) | IMPLEMENTED |
| `DocumentResponse` | id, document_key, version, source, all fields | IMPLEMENTED |

All 15 schemas complete and validated.

---

## 9. Test Layer Audit

**File:** `backend/tests/api/test_execution_api.py`

| Test | Endpoint Coverage | Status |
|---|---|---|
| `test_list_tasks_success` | GET /tasks → 200 | IMPLEMENTED |
| `test_create_task_success` | POST /tasks → 201 | IMPLEMENTED |
| `test_get_task_success` | GET /tasks/{id} → 200 | IMPLEMENTED |
| `test_update_task_success` (COMPLETED) | PATCH /tasks/{id} → 200 | IMPLEMENTED |
| `test_delete_task_success` | DELETE /tasks/{id} → 200 | IMPLEMENTED |
| `test_list_milestones_success` | GET /milestones → 200, gate_code, progress | IMPLEMENTED |
| `test_get_milestone_success` | GET /milestones/{id} → 200 | IMPLEMENTED |
| `test_list_risks_success` | GET /risks → 200 with risk_code | IMPLEMENTED |
| `test_create_risk_success` | POST /risks → 201 | IMPLEMENTED |
| `test_get_roadmap_projection_success` | GET /roadmap → 200, summary, milestones, grouped_tasks | IMPLEMENTED |
| `test_list_documents_success` | GET /documents → 200, document_key | IMPLEMENTED |
| `test_download_raw_document_success` | GET /documents/{id}/download → 200 Markdown | IMPLEMENTED |
| Cross-student access forbidden (execution domain) | NOT FOUND | MISSING (Gap G4) |
| `ensure_initialized` idempotency (double-call, no duplicates) | NOT FOUND | MISSING (Gap G5) |
| `ensure_initialized` approval status guard | NOT FOUND | MISSING (Gap G6) |

**Finding (G4):** The test file header (line 11) documents `Cross-student access returns 403 Forbidden`
as a covered case, but NO such test function exists anywhere in the file. Comparable isolation tests
exist in `test_blueprint_api.py`, `test_assessment_api.py`, `test_workspace_api.py`, and
`test_core_domain_api.py` — creating an inconsistent security posture in the test suite for execution
management.

---

## 10. Frontend Layer Audit

| Page / Component | Route | API Functions Used | Status |
|---|---|---|---|
| `StudentTasks.tsx` | `/student/projects/:id/tasks` | `getTasks`, `createTask`, `updateTask` | IMPLEMENTED (Kanban + Table, create modal, quick-status toggle) |
| `StudentTaskDetail.tsx` | `/student/projects/:id/tasks/:taskId` | `getTask`, `updateTask`, `deleteTask` | IMPLEMENTED (full edit form, acceptance criteria, dependencies list) |
| `StudentMilestones.tsx` | `/student/projects/:id/milestones` | `getMilestones`, `createMilestone` | IMPLEMENTED (milestone list, status badges, create modal) |
| `StudentMilestoneDetail.tsx` | `/student/projects/:id/milestones/:id` | getMilestone, updateMilestone | IMPLEMENTED |
| `StudentRoadmap.tsx` | `/student/projects/:id/roadmap` | `getRoadmap` | IMPLEMENTED (summary panel, milestone timeline, grouped task queues) |
| `StudentProjectOverview.tsx` | `/student/projects/:id/overview` | `getProjectOverview` | IMPLEMENTED (8-phase lifecycle display, health indicator, progress bar) |
| StudentDocuments page | `/student/projects/:id/documents` | getDocuments, createDocument | UNKNOWN — no `StudentDocuments/` directory found in scan (Gap G7) |

---

## 11. Gap Classification Summary

| ID | Gap | Classification | Priority |
|---|---|---|---|
| G1 | `ensure_initialized()` does not guard `blueprint.status == APPROVED`; materialises from any blueprint with content | PARTIAL | HIGH |
| G2 | `blueprint_service.approve_blueprint()` does not call `project_service.transition_phase("PLANNING")` — project remains in BLUEPRINT phase after approval | MISSING | CRITICAL |
| G3 | No `delete_milestone` in `ExecutionService`, `MilestoneRepository`, or `execution.py` routes | PARTIAL | MEDIUM (confirm spec) |
| G4 | No cross-student access forbidden test for execution management endpoints (documented in test header, never implemented) | MISSING | HIGH |
| G5 | No idempotency test for `ensure_initialized()` — double-invocation must not duplicate entities | MISSING | HIGH |
| G6 | No approval-status guard test for `ensure_initialized()` | MISSING | MEDIUM |
| G7 | `StudentDocuments` frontend page existence unconfirmed | UNKNOWN | MEDIUM |

---

## 12. Implementation Units

### Unit 1 — Phase Auto-Transition on Blueprint Approval (CRITICAL)

**Scope:** [`blueprint_service.py`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/application/services/blueprint_service.py) — `approve_blueprint()` method (lines 387-430)

`approve_blueprint()` must call `self._project_service.transition_phase(project_id, current_user, "PLANNING")`
immediately after `blueprint_repo.approve_blueprint()`. `self._project_service` is already injected in
`BlueprintService.__init__()`. The call must complete before the outbox event is emitted to ensure
phase history is recorded atomically.

Without this, the project permanently stays in `BLUEPRINT` phase after approval. All Gate 10 routes that
check `current_phase == PLANNING` will silently see incorrect state.

---

### Unit 2 — ensure_initialized Approval Status Guard (HIGH)

**Scope:** [`execution_service.py`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/application/services/execution_service.py) — `ensure_initialized()` (lines 130-165)

After retrieving `latest_bp`, add the guard:
```python
if latest_bp.status != BlueprintStatus.APPROVED.value:
    return
```
This prevents premature materialisation for blueprints in `READY_FOR_APPROVAL` or `GENERATED` states.

---

### Unit 3 — Cross-Student Isolation Test (HIGH)

**Scope:** [`test_execution_api.py`](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/tests/api/test_execution_api.py)

Add `test_cross_student_access_returns_403` asserting that `other_token` (a student who does not own
the project) receives HTTP 403 on all write-path execution endpoints. Mirror the pattern in
`test_blueprint_api.py:353`.

---

### Unit 4 — ensure_initialized Idempotency and Guard Tests (MEDIUM-HIGH)

**Scope:** New file `backend/tests/unit/test_execution_service.py` or added to `test_execution_api.py`

Add three service-level unit tests:
1. `test_ensure_initialized_idempotent` — invoke `ensure_initialized` twice; assert entity counts
   remain unchanged on second call.
2. `test_ensure_initialized_skips_unapproved_blueprint` — invoke with `blueprint.status = READY_FOR_APPROVAL`;
   assert zero milestones, tasks, risks, documents created.
3. `test_ensure_initialized_from_blueprint_content` — invoke with approved blueprint containing known
   `milestones_schedule` and `tasks_breakdown`; assert resulting entities match expected titles and counts.

---

### Unit 5 — Milestone Delete (MEDIUM — spec confirmation required)

**Scope (conditional):** Confirm whether `DELETE /milestones/{id}` is specified in
`docs/FRONTEND_BACKEND_CONTRACT.md §1503-1650`. If specified:

1. Add `delete_by_id()` to `MilestoneRepository` (safe: `milestone_id` FK is `ondelete="SET NULL"`)
2. Add `delete_milestone()` to `ExecutionService` with post-delete project progress recalculation
3. Register `DELETE /milestones/{milestone_id}` in `execution.py`

---

### Unit 6 — StudentDocuments Frontend Page (MEDIUM)

**Scope:** Verify or implement `frontend/src/pages/Student/StudentDocuments/StudentDocuments.tsx`

If absent, implement the page consuming:
- `GET /documents` (list with doc_type and status filters)
- `POST /documents` (create new document)
- `PATCH /documents/{id}` (update title, content, status)
- `GET /documents/{id}/download` (download raw Markdown)

---

## 13. Confirmed Complete — No Gate 10 Work Required

The following are fully implemented and production-grade:

1. Database schema — All 4 Gate 10 tables with correct columns, indexes, FKs, and cascade rules
2. RLS security — All 4 tables enrolled in Gate 12 RLS hardening migration
3. ORM models — All 4 SQLAlchemy models with correct relationships
4. 4 Repositories — Complete CRUD implementations; DocumentRepository includes admin platform views
5. ExecutionService — Full Task and Risk CRUD; Milestone list/get/create/update; Document lifecycle; Roadmap projection
6. Idempotent materialisation — `ensure_initialized()` with blueprint content parsing and default fallbacks
7. Roadmap projection engine — Deterministic task classification, milestone rollup, summary aggregation
8. 20 of 21 API routes — All execution endpoints except DELETE milestone
9. All 15 API schemas — Complete Pydantic validation for every request/response type
10. 8 domain events — TASK_CREATED, TASK_UPDATED, TASK_COMPLETED, MILESTONE_UPDATED, RISK_CREATED, RISK_UPDATED, DOCUMENT_CREATED, DOCUMENT_UPDATED via Outbox
11. 12 API tests — All specified execution test cases are present and functional
12. 6 frontend pages — Tasks (Kanban + Table), Task Detail, Milestones, Milestone Detail, Roadmap, Project Overview

---

## 14. Recommended Implementation Order

```
Unit 1 — blueprint_service.py: phase auto-transition BLUEPRINT → PLANNING
         (CRITICAL: unblocks all downstream phase-gated logic)
    |
    v
Unit 2 — execution_service.py: ensure_initialized approval status guard
         (HIGH: closes premature materialisation loophole)
    |
    v
Unit 3 — test_execution_api.py: cross-student 403 isolation test
         (HIGH: security parity with other tested domains)
    |
    v
Unit 4 — test_execution_service.py: idempotency and guard unit tests
         (MEDIUM-HIGH: confidence in materialization contract)
    |
   / \
  v   v
Unit 5        Unit 6
Milestone     StudentDocuments
Delete        page (if missing)
(confirm      (MEDIUM)
spec first)
```

---

## 15. Data Flow Diagram

```
Gate 09 Output
  BlueprintSession { status: APPROVED, content: { milestones, tasks, risks, readme } }
        |
        v
  POST /api/v1/projects/{id}/blueprint/approve
  |_ blueprint_service.approve_blueprint()
      |_ blueprint_repo.approve_blueprint()      [persists APPROVED + approved_at]
      |_ [UNIT 1] project_service.transition_phase("PLANNING")
      |    |_ project.current_phase = "PLANNING"
      |    |_ project_repo.record_phase_transition()
      |    |_ outbox.emit(PROJECT_PHASE_CHANGED)
      |_ outbox.emit(BLUEPRINT_APPROVED)
        |
        v
  Student navigates to /tasks, /milestones, /roadmap
  |_ execution_service.list_tasks() / list_milestones() / get_roadmap()
      |_ ensure_initialized()
          |_ [UNIT 2] Guard: blueprint.status == APPROVED?
          |_ blueprint_repo.get_latest_by_project()
          |_ Parse content["milestones"]["milestones_schedule"]
          |     |_ milestone_repo.bulk_create([...])
          |_ Parse content["tasks"]["tasks_breakdown"]
          |     |_ task_repo.bulk_create([...])  [linked to milestones deterministically]
          |_ Parse content["risks"]["technical_risks"]
          |     |_ risk_repo.bulk_create([...])
          |_ Create default documents
                |_ document_repo.bulk_create([master_blueprint, technical_specs, readme])
        |
        v
  Student manages execution lifecycle
  |_ CRUD /tasks          → progress recalculated per task change
  |_ CRUD /milestones     → milestone status auto-updated from task completion
  |_ CRUD /risks          → risk status tracked independently
  |_ CRUD /documents      → version bumped on content update
        |
        v
  GET /api/v1/projects/{id}/roadmap
  |_ execution_service.get_roadmap()
      |_ Classify tasks: overdue | blocked | in_progress | upcoming | completed
      |_ Roll up milestone completion from task states
      |_ Compute summary: overall_progress = 35 + 0.65 * (completed/total * 100)
      |_ Return RoadmapResponse
```

---

*Analysis completed. No production code, tests, migrations, or frontend code were modified.*
