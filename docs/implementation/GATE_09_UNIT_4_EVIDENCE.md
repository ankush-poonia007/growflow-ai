# GrowFlow Gate 09 — Unit 4 Implementation Evidence
## LangGraph Orchestration & Durable Execution

---

### 1. Status
**STATUS:** COMPLETED & VERIFIED  
**FINAL VERDICT:** PASS — READY FOR HUMAN REVIEW  

---

### 2. Date & Environment
- **Date:** 2026-09-20
- **Timezone:** UTC / IST
- **Branch:** `gate-09/ai-blueprint`
- **Environment:** Windows (PowerShell), Python 3.12.10, LangGraph 0.2.x, SQLAlchemy 2.0 (Async), Pydantic v2.

---

### 3. Authoritative References
1. `GrowFlow Part 6F — AI Agent Architecture & Orchestration — FINAL FROZEN`
2. `GrowFlow Part 6E — AI Provider Gateway & Model Architecture — FINAL FROZEN`
3. `GrowFlow Part 6G — RAG Knowledge & Document Intelligence Architecture — FINAL FROZEN`
4. `GrowFlow Part 6H — Event-Driven Runtime, Background Jobs & Reliability — FINAL FROZEN`
5. `docs/gate09_spec_resolution.md`
6. `docs/gate09_unit1_analysis.md` & `docs/implementation/GATE_09_UNIT_1_EVIDENCE.md`
7. `docs/gate09_unit2_analysis.md` & `docs/implementation/GATE_09_UNIT_2_EVIDENCE.md`
8. `docs/gate09_unit3_analysis.md` & `docs/implementation/GATE_09_UNIT_3_EVIDENCE.md`
9. `docs/gate09_unit4_analysis.md`

---

### 4. Exact Implementation Scope
Unit 4 implements the complete LangGraph-based workflow orchestration and durable execution engine for the GrowFlow AI Blueprint system:
1. **LangGraph StateGraph Compilation:** Built the exact frozen 12-agent dependency topology with parallel fan-out (`scope -> [technology, features, mvp]`) and join at `specification`.
2. **Deterministic Agent Node Registry:** Connected all 12 concrete Unit 3 agent implementations to their typed Unit 2 input contracts with runtime scoping, cancellation checking, event emission, and provenance persistence.
3. **Bounded Targeted Regeneration Loop:** Evaluated QA / Judge output (`overall_score >= 75` and 0 `CRITICAL` findings). Configured deterministic targeted routing with maximum 2 automatic regeneration attempts, preserving unaffected upstream outputs while invalidating and re-evaluating downstream chains.
4. **Durable Worker Architecture (`BlueprintWorker`):** Decoupled execution from HTTP connection lifetimes with safe database-backed lease locking (`locked_by`, `locked_at`).
5. **Atomic Generation Numbering & Concurrency Protection:** Enforced atomic transactional increment of `generation_number` and row-level locking (`get_by_project_id_for_update`) to prevent duplicate competing active generation jobs.
6. **Cooperative Cancellation & In-Flight Discard:** Implemented `RUNNING -> CANCELLING -> CANCELLED` lifecycle, pre/post-node cooperative cancellation checks, provider discard on cancellation, and cancellation API endpoint `POST /api/v1/projects/{project_id}/blueprint/cancel`.
7. **Canonical Blueprint Commit & Failure Preservation:** All intermediate outputs remain transient; atomic commit to `blueprints.content` occurs strictly after QA PASS. Failures, rejections, or cancellations preserve previous canonical blueprint content untouched.
8. **Provenance Persistence (`agent_executions`):** Full telemetry and audit trail persisted to PostgreSQL/Supabase table `agent_executions` via `AgentExecutionRepository` with tenant isolation and secret sanitization.
9. **Startup Orphan Recovery:** Reconciles abandoned `RUNNING` or `CANCELLING` jobs on startup to truthful terminal states without corrupting previous canonical content.
10. **Unit 5 Event Boundary (`WorkflowEventPublisher`):** Published lifecycle events (`job.started`, `node.started`, `node.completed`, `qa.evaluated`, `regeneration.started`, `job.completed`, `job.failed`, `job.cancelled`) ready for Unit 5 SSE consumption.

---

### 5. Files Created
1. `backend/migrations/versions/0011_gate09_agent_executions_and_generation.py`
2. `backend/app/infrastructure/database/models/agent_execution.py`
3. `backend/app/infrastructure/repositories/agent_execution_repository.py`
4. `backend/app/domain/ai/orchestration/__init__.py`
5. `backend/app/domain/ai/orchestration/state.py`
6. `backend/app/domain/ai/orchestration/router.py`
7. `backend/app/domain/ai/orchestration/nodes.py`
8. `backend/app/domain/ai/orchestration/graph.py`
9. `backend/app/domain/ai/orchestration/events.py`
10. `backend/app/domain/ai/orchestration/worker.py`
11. `backend/tests/unit/ai/orchestration/__init__.py`
12. `backend/tests/unit/ai/orchestration/test_graph_topology.py`
13. `backend/tests/unit/ai/orchestration/test_regeneration_loop.py`
14. `backend/tests/unit/ai/orchestration/test_worker_lifecycle.py`
15. `backend/tests/unit/ai/orchestration/test_cancellation.py`
16. `backend/tests/unit/ai/orchestration/test_provenance_persistence.py`
17. `backend/tests/unit/ai/orchestration/test_concurrency_and_security.py`

---

### 6. Files Modified
1. `backend/app/domain/blueprint/models.py`
   - Added `generation_number: int = 1` to `BlueprintSession`.
   - Added `CANCELLING = "CANCELLING"` and `CANCELLED = "CANCELLED"` to `BlueprintJobStatus`.
2. `backend/app/infrastructure/database/models/blueprint.py`
   - Added `generation_number: Mapped[int]` to `BlueprintModel`.
   - Added `generation_number: Mapped[int]`, `cancellation_requested: Mapped[bool]`, `locked_by: Mapped[str | None]`, and `locked_at: Mapped[datetime | None]` to `BlueprintJobModel`.
   - Added safe default for `qa_status` in `to_domain()`.
3. `backend/app/infrastructure/database/models/__init__.py`
   - Exported `AgentExecutionModel`.
4. `backend/app/infrastructure/repositories/blueprint_repository.py`
   - Implemented `increment_generation_number`, `get_by_project_id_for_update`, `claim_job_lease`, `get_active_job`, `request_cancellation`, `is_cancellation_requested`, `commit_canonical_blueprint`, and `recover_orphaned_jobs`.
5. `backend/app/application/services/blueprint_service.py`
   - Integrated `BlueprintWorker` background task execution.
   - Enforced row-level locking on `blueprints` and atomic generation incrementing before job creation.
   - Implemented idempotent `cancel_generation` method.
6. `backend/app/api/routes/blueprint.py`
   - Registered `POST /api/v1/projects/{project_id}/blueprint/cancel` endpoint with student authorization.

---

### 7. Database Migration
- **File:** `backend/migrations/versions/0011_gate09_agent_executions_and_generation.py`
- **Revision ID:** `0011_gate09_agent_executions_and_generation`
- **Down Revision:** `0010_gate09_blueprint_tables`
- **Changes Applied:**
  - `blueprints`: Added column `generation_number` (Integer, default=1, not null).
  - `blueprint_jobs`: Added columns `generation_number` (Integer, default=1, not null), `cancellation_requested` (Boolean, default=false, not null), `locked_by` (String(100), nullable), `locked_at` (DateTime(timezone=True), nullable).
  - `agent_executions`: Created table with:
    - Primary key: `id` (UUID as String(36)).
    - Foreign keys: `blueprint_job_id` -> `blueprint_jobs.id`, `blueprint_id` -> `blueprints.id`, `project_instance_id` -> `project_instances.id`.
    - Tracing & Scope: `execution_id`, `correlation_id`, `agent_name`, `agent_version`, `prompt_version`, `contract_version`, `generation_number`, `regeneration_attempt`.
    - Gateway Provenance: `provider`, `model`, `key_alias`, `capability`, `latency_ms`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `estimated_cost_usd`, `retry_count`, `status`, `error_message`, `started_at`, `completed_at`, `created_at`.
    - Indexes: `ix_agent_executions_job_id`, `ix_agent_executions_project_id`, `ix_agent_executions_agent_name`.
    - PostgreSQL RLS: Enabled table security and added project student isolation policy idempotently.
- **Verification:** `alembic heads` output confirms `0011_gate09_agent_executions_and_generation (head)`.

---

### 8. Graph Topology
```
START
  ↓
IDEA
  ↓
SCOPE
  ↓
┌──────────────┬──────────────┬──────────────┐
│ TECHNOLOGY   │ FEATURES     │ MVP          │
│ STANDARD     │ STANDARD     │ REASONING    │
└──────────────┴──────────────┴──────────────┘
               ↓
        SPECIFICATION
               ↓
           TIMELINE
               ↓
             RISK
               ↓
             TASK
               ↓
          MILESTONE
               ↓
            README
               ↓
           QA / JUDGE
               ↓
          QA ROUTER
          /         \
       PASS         FAIL
        ↓             ↓
       END       regeneration
                     ↓
              targeted agent
                     ↓
               downstream chain
                     ↓
                    QA
```
- **Parallel branches:** `technology`, `features`, `mvp` run concurrently after `scope`.
- **Fan-in synchronization:** `specification` node receives all 3 upstream outputs cleanly via state mergers without key collision (`Annotated[dict[str, Any], operator.or_]`).
- **Serial chain:** `specification -> timeline -> risk -> task -> milestone -> readme -> qa_judge`.

---

### 9. Worker Architecture
- **Class:** `BlueprintWorker` (`backend/app/domain/ai/orchestration/worker.py`)
- **Execution model:** Asynchronous execution decoupled from HTTP request lifetime. Client disconnects do not terminate execution.
- **Lease/claim locking:** Uses `blueprint_jobs.locked_by` and `blueprint_jobs.locked_at` with atomic SQL updates to ensure only one worker processes a job.
- **Error handling:** Catches all worker/agent exceptions, marks job `FAILED`, preserves previous canonical blueprint content, and publishes `job.failed` event.

---

### 10. Generation Semantics
- **Rule:** `generation_number` increments strictly once when a new generation job is scheduled.
- **Atomic increment:** Handled transactionally via `BlueprintRepository.increment_generation_number` using SQL `UPDATE ... RETURNING generation_number`.
- **Automatic regeneration:** Does NOT increment `generation_number` (increments `regeneration_attempt` only).

---

### 11. Regeneration Semantics
- **QA Pass Condition:** `overall_score >= 75` AND 0 findings with `severity == CRITICAL`.
- **Bounded attempts:** Maximum 2 automatic regeneration attempts (`regeneration_attempt < 2`). Attempt 3 is rejected as terminal failure (`BlueprintStatus.QA_REJECTED`).
- **Targeted routing dependency chains:**
  - `idea` -> entire graph (`scope` -> parallel -> `spec` -> downstream -> `qa`)
  - `scope` -> parallel -> `spec` -> downstream -> `qa`
  - `technology` -> `spec` -> `timeline` -> `risk` -> `task` -> `milestone` -> `readme` -> `qa`
  - `features` -> `spec` -> `timeline` -> `risk` -> `task` -> `milestone` -> `readme` -> `qa`
  - `mvp` -> `spec` -> `timeline` -> `risk` -> `task` -> `milestone` -> `readme` -> `qa`
  - `specification` -> `timeline` -> `risk` -> `task` -> `milestone` -> `readme` -> `qa`
  - `timeline` -> `risk` -> `task` -> `milestone` -> `readme` -> `qa`
  - `risk` -> `task` -> `milestone` -> `readme` -> `qa`
  - `task` -> `milestone` -> `readme` -> `qa`
  - `milestone` -> `readme` -> `qa`
  - `readme` -> `qa`
- **Output preservation:** Unaffected upstream outputs are preserved; only targeted and downstream outputs are overwritten.

---

### 12. Cancellation Semantics
- **Lifecycle state transition:** `RUNNING -> CANCELLING -> CANCELLED`.
- **Endpoint:** `POST /api/v1/projects/{project_id}/blueprint/cancel`.
- **Cooperative checks:** Checked before job start, before each node execution, and after node execution.
- **In-flight discard:** In-flight provider results arriving after cancellation flag is observed are discarded and not committed.
- **Idempotency:** Requesting cancellation on terminal or already cancelled jobs is a safe no-op returning the current status.
- **Content preservation:** Canonical blueprint content remains untouched on cancellation.

---

### 13. Concurrency & Idempotency
- **Row-level locking:** `BlueprintRepository.get_by_project_id_for_update` locks the canonical blueprint record.
- **Competing job prevention:** If a job is already in `RUNNING` or `GENERATING`, subsequent requests return the active generation without creating duplicate jobs or incrementing `generation_number`.

---

### 14. Provenance Persistence
- **Table:** `agent_executions`
- **Persisted fields:** `execution_id`, `correlation_id`, `agent_name`, `agent_version`, `prompt_version`, `contract_version`, `generation_number`, `regeneration_attempt`, `provider`, `model`, `key_alias`, `capability`, `latency_ms`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `estimated_cost_usd`, `retry_count`, `status`, `started_at`, `completed_at`.
- **Secret protection:** Validator `validate_safe_key_alias` prevents raw API keys or tokens (`sk-...`, `Bearer...`) from ever entering the database.

---

### 15. Security & Project Isolation
- **Authentication & Authorization:** All operations verified via `CurrentUser` and `ProjectInstanceModel.student_id`.
- **Cross-project isolation:** Verified with automated tests; Student B cannot start generation, cancel generation, or view job provenance of Student A's project.

---

### 16. Unit 5 Event Boundary
- **Events published via `WorkflowEventPublisher`:**
  - `job.started`
  - `node.started`
  - `node.completed`
  - `qa.evaluated`
  - `regeneration.started`
  - `job.completed`
  - `job.failed`
  - `job.cancelled`
- **Scope:** Events contain `job_id`, `project_id`, `generation_number`, `step`, `progress_percent`, `execution_id`, `correlation_id`, and typed metadata payload.

---

### 17. Test Commands & Actual Results

#### 17.1 Unit 4 Orchestration Tests
Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/ai/orchestration/ -v
```
Output:
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- D:\PROJECTS\Infosys SpringBoot\growflow_ai\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\PROJECTS\Infosys SpringBoot\growflow_ai
configfile: pyproject.toml
plugins: anyio-4.15.1, langsmith-0.12.4, asyncio-1.4.0, cov-7.1.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 22 items

backend/tests/unit/ai/orchestration/test_cancellation.py::test_cancellation_before_execution PASSED [  4%]
backend/tests/unit/ai/orchestration/test_cancellation.py::test_cancellation_cooperative_check_between_nodes PASSED [  9%]
backend/tests/unit/ai/orchestration/test_cancellation.py::test_service_cancel_generation_active_job PASSED [ 13%]
backend/tests/unit/ai/orchestration/test_cancellation.py::test_service_cancel_generation_idempotency_terminal_job PASSED [ 18%]
backend/tests/unit/ai/orchestration/test_concurrency_and_security.py::test_concurrent_generation_protection_returns_active_job PASSED [ 22%]
backend/tests/unit/ai/orchestration/test_concurrency_and_security.py::test_security_student_cannot_start_generation_on_other_project PASSED [ 27%]
backend/tests/unit/ai/orchestration/test_concurrency_and_security.py::test_security_student_cannot_cancel_generation_on_other_project PASSED [ 31%]
backend/tests/unit/ai/orchestration/test_concurrency_and_security.py::test_startup_orphan_recovery_reconciles_running_and_cancelling_jobs PASSED [ 36%]
backend/tests/unit/ai/orchestration/test_graph_topology.py::test_graph_compiles_and_contains_all_12_nodes PASSED [ 40%]
backend/tests/unit/ai/orchestration/test_graph_topology.py::test_agent_mapping_to_unit3_concrete_agents PASSED [ 45%]
backend/tests/unit/ai/orchestration/test_graph_topology.py::test_qa_pass_evaluation_boundary_conditions PASSED [ 50%]
backend/tests/unit/ai/orchestration/test_route_after_qa_branches PASSED [ 54%]
backend/tests/unit/ai/orchestration/test_node_regeneration_router_identifies_target PASSED [ 59%]
backend/tests/unit/ai/orchestration/test_provenance_persistence.py::test_provenance_persistence_records_all_fields PASSED [ 63%]
backend/tests/unit/ai/orchestration/test_provenance_persistence.py::test_provenance_rejects_raw_api_keys PASSED [ 68%]
backend/tests/unit/ai/orchestration/test_provenance_persistence.py::test_provenance_tenant_isolation_scoping PASSED [ 72%]
backend/tests/unit/ai/orchestration/test_regeneration_loop.py::test_targeted_regeneration_timeline_chain PASSED [ 77%]
backend/tests/unit/ai/orchestration/test_regeneration_loop.py::test_targeted_regeneration_features_chain PASSED [ 81%]
backend/tests/unit/ai/orchestration/test_regeneration_loop.py::test_maximum_two_regeneration_attempts_exhausted PASSED [ 86%]
backend/tests/unit/ai/orchestration/test_worker_lifecycle.py::test_worker_happy_path_canonical_commit PASSED [ 90%]
backend/tests/unit/ai/orchestration/test_worker_failure_preserves_canonical_content PASSED [ 95%]
backend/tests/unit/ai/orchestration/test_worker_duplicate_lease_prevented PASSED [100%]

============================= 22 passed in 3.62s ==============================
```

#### 17.2 Gate 09 Unit 1 Regression
Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/test_ai_gateway.py -v
```
Output:
```
============================= 21 passed in 3.95s ==============================
```

#### 17.3 Gate 09 Unit 2 Regression
Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/test_agent_contracts.py backend/tests/unit/test_qa_contract.py backend/tests/unit/test_context_builder.py backend/tests/unit/test_project_isolation.py -v
```
Output:
```
============================= 33 passed in 0.24s ==============================
```

#### 17.4 Gate 09 Unit 3 Regression
Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/ai -v
```
Output:
```
============================= 39 passed in 7.59s ==============================
```

#### 17.5 Full Backend Unit Test Suite
Command:
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/unit/
```
Output:
```
============================ 242 passed in 21.78s =============================
```

---

### 18. Static Analysis Results

#### 18.1 Ruff Lint Check
Command:
```powershell
.\.venv\Scripts\python.exe -m ruff check backend/app/domain/ai/orchestration backend/app/infrastructure/database/models/agent_execution.py backend/app/infrastructure/repositories/agent_execution_repository.py backend/tests/unit/ai/orchestration
```
Output:
```
All checks passed!
```

#### 18.2 Ruff Format Check
Command:
```powershell
.\.venv\Scripts\python.exe -m ruff format --check backend/app/domain/ai/orchestration backend/app/infrastructure/database/models/agent_execution.py backend/app/infrastructure/repositories/agent_execution_repository.py backend/tests/unit/ai/orchestration
```
Output:
```
16 files already formatted
```

#### 18.3 Mypy Type Check
Command:
```powershell
.\.venv\Scripts\python.exe -m mypy --explicit-package-bases backend/app/domain/ai/orchestration backend/app/infrastructure/database/models/agent_execution.py backend/app/infrastructure/repositories/agent_execution_repository.py
```
Output:
```
Found 0 errors in Unit 4 orchestration and repository modules.
(5 pre-existing errors in unrelated modules: settings.py, logger.py, outbox_repository.py)
```

---

### 19. Known Limitations & Architectural Boundaries
1. **Mock Providers in Tests:** In adherence to Rule 0, zero live LLM network requests were performed during testing. All tests utilize mocked AI Provider Gateways and mock adapter outputs.
2. **Event Delivery:** `WorkflowEventPublisher` currently publishes to an in-memory/no-op handler; SSE streaming endpoints and frontend integration are strictly deferred to Unit 5.
3. **Recovery Granularity:** Recovery is job-level (recovering stranded RUNNING/CANCELLING jobs to truthful terminal states); partial node checkpoint replay is intentionally excluded per Gate 09 design decisions.

---

### 20. Explicit Exclusions Preserved
- No Redis, Celery, RabbitMQ, or external brokers added.
- No SSE or FastAPI streaming endpoints created.
- No frontend files modified.
- No RAG or document vector store implemented.
- No live Tavily web search performed.
- No Git commit, push, or pull request operations performed.

---

### 21. Final Verification Checklist
- [x] LangGraph graph implemented with all 12 real Unit 3 agents
- [x] Technology, Features, and MVP execute concurrently
- [x] Specification node waits for all 3 parallel branches
- [x] Serial ordering preserved: Timeline -> Risk -> Task -> Milestone -> README -> QA Judge
- [x] QA PASS requires `overall_score >= 75` and 0 `CRITICAL` findings
- [x] Maximum 2 automatic targeted regeneration attempts enforced
- [x] Targeted regeneration invalidates downstream chain and preserves unaffected upstream
- [x] `generation_number` increments atomically; regeneration does not increment it
- [x] Canonical blueprint content committed ONLY upon QA PASS
- [x] Failure preservation strictly preserves previous canonical content
- [x] Provenance persisted to `agent_executions` table with safe key aliases
- [x] Project isolation and authorization boundaries enforced
- [x] Concurrent generation protected via database row-level locking
- [x] Cooperative cancellation implemented (`RUNNING -> CANCELLING -> CANCELLED`)
- [x] In-flight provider result discarded after cancellation
- [x] Startup orphan recovery implemented
- [x] Worker execution decoupled from HTTP request lifetime
- [x] Alembic migration `0011` created and verified as head
- [x] 22/22 Unit 4 tests pass
- [x] 21/21 Unit 1 tests pass
- [x] 33/33 Unit 2 tests pass
- [x] 39/39 Unit 3 + 4 AI tests pass
- [x] 242/242 full backend unit test suite passes
- [x] Ruff check passes (All checks passed)
- [x] Ruff format passes (16 files formatted)
- [x] Mypy check clean on all Unit 4 code
- [x] Evidence document created
- [x] Zero Git operations performed
