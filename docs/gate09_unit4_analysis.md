# GrowFlow — Gate 09 — Unit 4 Analysis
# LangGraph Orchestration & Durable Execution Architecture

**Document ID:** `GF-GATE09-UNIT4-ANALYSIS`  
**Status:** READY FOR HUMAN REVIEW — ANALYSIS ONLY  
**Date:** 2026-09-20  
**Branch:** `gate-09/ai-blueprint`  
**Authoritative References:**  
- GrowFlow Part 6F — AI Agent Architecture & Orchestration (Final Frozen Specification)
- GrowFlow Part 6E — AI Provider Gateway & Model Architecture (Final Frozen Specification)
- GrowFlow Part 6G — RAG Knowledge & Document Intelligence Architecture (Final Frozen Specification)
- GrowFlow Part 6H — Event-Driven Runtime, Background Jobs & Reliability Architecture (Final Frozen Specification)
- Gate 09 Specification & Gate 09 Specification Resolution (`docs/gate09_spec_resolution.md`)
- Gate 09 Unit 1 Analysis (`docs/gate09_unit1_analysis.md`) & Evidence (`docs/implementation/GATE_09_UNIT_1_EVIDENCE.md`)
- Gate 09 Unit 2 Analysis (`docs/gate09_unit2_analysis.md`) & Evidence (`docs/implementation/GATE_09_UNIT_2_EVIDENCE.md`)
- Gate 09 Unit 3 Analysis (`docs/gate09_unit3_analysis.md`) & Evidence (`docs/implementation/GATE_09_UNIT_3_EVIDENCE.md`)
- Current Repository Implementation (`backend/app/application/services/blueprint_service.py`, `backend/app/infrastructure/database/models/blueprint.py`, `backend/app/domain/ai/`)

---

## 1. Executive Summary

Unit 4 is the architectural bridge that transforms the 12 standalone, stateless AI agents delivered in Unit 3 into a fault-tolerant, asynchronous, durable orchestration pipeline. 

Units 1, 2, and 3 are 100% verified and frozen:
- **Unit 1:** Real `AIProviderGateway` with key pooling, rotation across 5 keys, capability-based model routing, and structured JSON extraction.
- **Unit 2:** Strongly-typed Pydantic contracts for all 12 agents, `BlueprintWorkflowState` state schemas, purpose-built agent context projections, and the secure `ProjectContextBuilder`.
- **Unit 3:** 12 concrete AI agent implementations inheriting from `BaseAgent[TInput, TOutput]` delegating to `AIProviderGateway.execute_structured(...)`, returning typed Pydantic outputs and `AgentExecutionProvenance`.

Unit 4 fulfills the core Gate 09 mandate by establishing:
1. **LangGraph StateGraph Orchestration:** Implementation of the frozen 12-agent graph topology with parallel fan-out (`Technology`, `Features`, `MVP`) and fan-in (`Specification`), followed by strictly serial downstream progression and conditional QA evaluation routing.
2. **Durable Execution & Worker Engine:** Decoupling long-running generation from HTTP requests via persistent `blueprint_jobs` tracking, safe pre-node cancellation observation, and restart recovery.
3. **Targeted Regeneration Routing:** Implementation of the bounded automatic feedback loop (maximum 2 attempts) routing QA findings back to targeted upstream nodes while preserving unaffected parallel/upstream outputs.
4. **Canonical Blueprint Persistence & Versioning:** Monotonic atomic `generation_number` increments, transactional commit to `blueprints.content` *only upon QA PASS*, and non-destructive preservation of the last valid canonical blueprint on failure.
5. **Persistent Provenance:** Introduction of the `agent_executions` table to persist fine-grained execution metadata (`AgentExecutionProvenance`) for every agent execution.

**Crucial Constraint Adherence:** Zero new external infrastructure (no Redis, no Celery, no RabbitMQ). Unit 4 operates completely within GrowFlow's modular monolith architecture using PostgreSQL and Python's installed `langgraph` library (v1.2.11).

---

## 2. Current Repository Audit

A detailed audit of the repository reveals the exact delta between current code and the required Unit 4 target:

### 2.1 `BlueprintService` (`backend/app/application/services/blueprint_service.py`)
- **Current State:** Contains historical prototype code. In `start_generation()`, it spawns an unmanaged `asyncio.create_task(self._run_generation_task(...))`.
- **Pipeline Implementation:** `_execute_generation_pipeline()` uses synchronous, hardcoded dictionaries (`_synthesize_section`) and mock QA heuristics (`_evaluate_qa_judge`).
- **Database Writing:** It iteratively updates `blueprints.content` section-by-section *during* generation. If a failure occurs mid-way, partial, unvalidated AI output is permanently committed to the canonical blueprint.
- **Missing Capabilities:**
  - Zero integration with the 12 Unit 3 AI agents.
  - Zero LangGraph `StateGraph` orchestration.
  - Zero targeted regeneration loops.
  - No cancellation mechanism (`cancellation_requested` is ignored).
  - No provenance persistence.

### 2.2 Database Models (`backend/app/infrastructure/database/models/blueprint.py`)
- **`BlueprintModel`:**
  - Represents the single canonical blueprint record for a project.
  - **Gap:** Missing `generation_number`. Currently has no tracking of how many generation attempts have been initiated.
- **`BlueprintJobModel`:**
  - Tracks generation jobs (`status`, `progress_percent`, `error`).
  - **Gap:** Missing `generation_number`, missing `cancellation_requested` (boolean flag to signal cooperative cancellation to workers), and missing worker lease/lock fields.
- **`agent_executions` Table:**
  - **Gap:** Does NOT exist. Currently, `AgentExecutionProvenance` produced by Unit 3 agents is discarded upon completion of in-memory execution.

### 2.3 Dependency Environment
- **`langgraph`:** Installed in the workspace virtual environment at version **1.2.11**. `StateGraph`, `START`, `END`, and Pregel compilation are available and verified.
- **No new packages required.**

---

## 3. LangGraph Topology & Node Mapping

### 3.1 Frozen Topological Graph
The workflow topology is frozen by Gate 09 Decision A1 and GrowFlow Part 6F § 8:

```
                  START
                    │
                    ▼
               [Idea Agent]
                    │
                    ▼
              [Scope Agent]
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
  [Technology]  [Features]    [MVP]      ← Parallel Fan-Out
        │           │           │
        └───────────┼───────────┘
                    ▼
          [Specification Agent]          ← Synchronized Fan-In
                    │
                    ▼
            [Timeline Agent]
                    │
                    ▼
              [Risk Agent]
                    │
                    ▼
              [Task Agent]
                    │
                    ▼
           [Milestone Agent]
                    │
                    ▼
             [README Agent]
                    │
                    ▼
            [QA / Judge Agent]
                    │
                    ▼
            ┌───────────────┐
            │   QA Check    │
            └───┬───────┬───┘
                │       │
    PASS (≥75 & │       │ FAIL (<75 or Critical)
    0 Critical) │       ▼
                │   ┌───────────────────────────┐
                │   │ Max 2 Regen Check         │
                │   └───┬───────────────────┬───┘
                │       │ < 2               │ ≥ 2
                │       ▼                   ▼
                │   [Regen Router]     [Terminal Failure]
                │       │                   │
                │       ▼ (target node)     ▼
                │   (Loop Back)            END
                ▼
               END
```

### 3.2 Invariant Verification
1. **Parallel Execution:** `Technology`, `Features`, and `MVP` execute concurrently. LangGraph Pregel engine executes independent branches in parallel.
2. **Capability Assignment:** `MVP` and `QA/Judge` execute using `ProviderCapability.REASONING`. The other 10 agents execute using `ProviderCapability.STANDARD`.
3. **Serial Invariants:**
   - `Specification` strictly consumes `Technology` + `Features` + `MVP`.
   - `Timeline` executes *before* `Risk` (Timeline does NOT consume Risk).
   - `Risk` consumes `Timeline` + `Specification`.
   - `Task` consumes `Specification` + `Technology` + `Features` + `Timeline` + `Risk`.
   - `Task` → `Milestone` is strictly serial (`Milestone` consumes `Task`).
   - `README` consumes curated upstream outputs.
   - `QA / Judge` is strictly the final evaluation node.

### 3.3 Node Execution Contract
Every graph node follows an identical, clean lifecycle pattern:

```python
async def node_agent(state: OrchestrationState) -> dict[str, Any]:
    # 1. Cooperative cancellation check
    if state.get("cancellation_requested", False):
        return {"workflow_status": "CANCELLING"}

    # 2. Extract immutable context & prior validated outputs
    # 3. Construct typed Unit 2 input contract
    agent_input = build_agent_input(state)

    # 4. Invoke concrete Unit 3 agent
    output, provenance = await agent.execute(agent_input)

    # 5. Return state patch (merged via Annotated dictionary reducers)
    return {
        "current_step": "agent_name",
        "agent_outputs": {"agent_name": output},
        "agent_execution_metadata": {"agent_name": provenance},
    }
```

### 3.4 Parallel Merge Channel Resolution
Under LangGraph, parallel nodes (`Technology`, `Features`, `MVP`) writing to the same state keys simultaneously raise `InvalidUpdateError` unless an `Annotated` reducer is declared.  
To resolve this without altering Unit 2 contracts:
Unit 4 defines `OrchestrationState(BlueprintWorkflowState, total=False)` in `backend/app/domain/ai/orchestration/state.py` with:
```python
agent_outputs: Annotated[dict[str, Any], operator.or_]
agent_execution_metadata: Annotated[
    dict[str, AgentExecutionProvenance], operator.or_
]
```
This was tested and verified: `operator.or_` merges concurrent branch writes seamlessly into the shared state dictionary.

---

## 4. State Model & Channel Lifecycle

### 4.1 Transient Workflow State (`OrchestrationState`)
The workflow state tracks the in-flight generation in memory and checkpoints:
- **Scoping:** `project_id: UUID`, `student_id: UUID`, `generation_number: int`.
- **Tracing:** `execution_id: str`, `correlation_id: str`.
- **Foundational Context:** `project_context: ProjectBaseContext`, `assessment_context: AssessmentContext`.
- **Progression State:** `current_step: str`, `workflow_status: str`, `cancellation_requested: bool`.
- **Agent Outputs:** `agent_outputs: dict[str, Any]` (keyed by agent name: `"idea"`, `"scope"`, `"technology"`, etc.).
- **Provenance Records:** `agent_execution_metadata: dict[str, AgentExecutionProvenance]`.
- **QA Evaluation:** `qa_findings: list[QAFinding]`, `qa_score: int | None`, `qa_status: BlueprintQAStatus`.
- **Regeneration Controls:** `regeneration_attempt: int`, `regeneration_target: str | None`, `qa_feedback_hint: str | None`.
- **Lifecycle Timestamps:** `started_at: datetime`, `completed_at: datetime | None`.

### 4.2 State vs. Database Separation (6F § 13)
- LangGraph state is **transient working memory**.
- Intermediate model outputs are buffered inside `agent_outputs`.
- PostgreSQL `blueprints.content` is **never updated incrementally** during workflow execution. It is updated only upon successful QA PASS in an atomic database transaction.

---

## 5. Job Model & Lifecycle

### 5.1 Job Record Identity
Every blueprint generation run is represented by a persistent row in `blueprint_jobs`:
- `id`: UUID Primary Key.
- `blueprint_id`: Foreign Key to `blueprints.id`.
- `project_instance_id`: Foreign Key to `project_instances.id`.
- `generation_number`: Integer matching the attempt count.
- `job_type`: `FULL_GENERATION` or `TARGETED_RETRY`.
- `status`: State machine value (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`).
- `cancellation_requested`: Boolean flag (default `False`).
- `current_step`: String indicating current executing agent node.
- `progress_percent`: Integer (0 to 100).
- `error`: Text nullable error description.
- `started_at`, `completed_at`: Timestamp tracking.

### 5.2 Job Status State Machine
```
   ┌─────────┐
   │ PENDING │
   └────┬────┘
        │ (Worker picks up job)
        ▼
   ┌─────────┐
   │ RUNNING │◄────────────────────────┐
   └────┬────┘                         │
        │                              │ (Targeted Auto-Regeneration,
        ├──────────────────────────────┤  attempt < 2)
        │                              │
        ├──────────────────────────────┼─────────────────────────┐
        │                              │                         │
        ▼ (QA PASS & Persisted)        ▼ (Terminal Error /       ▼ (Cancellation
   ┌───────────┐                         QA Exhaustion ≥ 2)        Requested)
   │ COMPLETED │                  ┌────────┐               ┌────────────┐
   └───────────┘                  │ FAILED │               │ CANCELLING │
                                  └────────┘               └─────┬──────┘
                                                                 │ (Worker halts)
                                                                 ▼
                                                           ┌───────────┐
                                                           │ CANCELLED │
                                                           └───────────┘
```

---

## 6. Execution Model & Worker Architecture

### 6.1 Asynchronous HTTP 202 Pattern (6H § 33)
1. Student calls `POST /api/v1/projects/{id}/blueprint/generate`.
2. `BlueprintService.start_generation()`:
   - Validates ownership, phase, and assessment completion.
   - Acquires lock on `blueprints` row.
   - Atomically increments `generation_number`.
   - Creates `BlueprintJobModel` in status `RUNNING`.
   - Commits database transaction.
   - Spawns background worker execution.
   - Returns **HTTP 202 Accepted** immediately with `BlueprintStatusResponse`.

### 6.2 Worker Execution Loop
The worker executes asynchronously outside the HTTP request:
1. Instantiates `ProjectContextBuilder` and builds base contexts.
2. Initializes `OrchestrationState`.
3. Invokes compiled LangGraph `StateGraph.ainvoke(initial_state)`.
4. As each node completes:
   - Persists node progress to `blueprint_jobs.current_step` and `progress_percent`.
   - Persists the agent's `AgentExecutionProvenance` to the new `agent_executions` table.
5. Handles workflow termination:
   - If QA PASSED: Executes atomic canonical commit to `blueprints.content` and marks job `COMPLETED`.
   - If QA FAILED (regen exhausted): Marks blueprint `QA_REJECTED`, marks job `FAILED`, preserves previous canonical content.
   - If CANCELLED: Marks job `CANCELLED`, discards buffered outputs, preserves previous canonical content.
   - If Exception: Marks job `FAILED`, marks blueprint `FAILED`, preserves previous canonical content.

---

## 7. Persistence Model & Schema Changes

### 7.1 Entity Relationship Diagram
```
┌───────────────────────────┐
│     project_instances     │
└─────────────┬─────────────┘
              │ 1
              │
              ▼ 1 (uq_blueprints_project_instance)
┌───────────────────────────┐
│        blueprints         │
│ ───────────────────────── │
│  id                       │
│  project_instance_id (FK) │
│  student_id (FK)          │
│  generation_number (NEW)  │◄── Monotonically increments at job creation
│  status                   │
│  qa_status / qa_score     │
│  qa_feedback (JSONB)      │
│  content (JSONB)          │◄── Canonical 10 sections (committed on PASS only)
└─────────────┬─────────────┘
              │ 1
              │
              ▼ N (fk_blueprint_jobs_blueprint_id)
┌───────────────────────────┐
│      blueprint_jobs       │
│ ───────────────────────── │
│  id                       │
│  blueprint_id (FK)        │
│  project_instance_id (FK) │
│  generation_number (NEW)  │
│  cancellation_requested   │◄── Cooperative cancellation flag (NEW)
│  status                   │
│  current_step             │
│  progress_percent         │
│  error                    │
└─────────────┬─────────────┘
              │ 1
              │
              ▼ N (fk_agent_executions_blueprint_job_id)
┌───────────────────────────┐
│     agent_executions      │  (NEW TABLE FOR PROVENANCE)
│ ───────────────────────── │
│  id                       │
│  blueprint_job_id (FK)    │
│  blueprint_id (FK)        │
│  project_instance_id (FK) │
│  execution_id             │
│  correlation_id           │
│  agent_name               │
│  agent_version            │
│  prompt_version           │
│  contract_version         │
│  generation_number        │
│  regeneration_attempt     │
│  provider / model         │
│  key_alias                │
│  capability               │
│  latency_ms               │
│  prompt_tokens            │
│  completion_tokens        │
│  total_tokens             │
│  cost_usd                 │
│  retry_count              │
│  status                   │
│  error_message            │
│  started_at/completed_at  │
└───────────────────────────┘
```

---

## 8. Generation & Versioning Semantics

### 8.1 Single Canonical Record Model (Gate 09 Decision A2)
- Exactly one row exists in `blueprints` per `project_instance_id`.
- `generation_number` is stored on `blueprints` and increments monotonically at job creation.
- Canonical commit rule:
  ```sql
  UPDATE blueprints
  SET content = :validated_10_sections,
      status = 'READY_FOR_APPROVAL',
      qa_status = 'PASS',
      qa_score = :score,
      qa_feedback = :feedback,
      current_step = 'qa_judge',
      progress_percent = 100,
      updated_at = NOW()
  WHERE id = :blueprint_id
    AND status = 'GENERATING';
  ```
- **Preservation on Failure (6F § 37):** If generation fails, `blueprints.content` remains untouched. The previously approved or ready content remains live. Only `status`, `error_message`, and `qa_feedback` are updated.

---

## 9. Targeted Regeneration Routing

### 9.1 Evaluation Logic & Bounded Attempts (Gate 09 Decision A3)
- QA / Judge evaluates the entire blueprint.
- **PASS Rule:** `overall_score >= 75` AND zero `CRITICAL` findings.
- If FAIL:
  - Check `state["regeneration_attempt"]`:
    - If `regeneration_attempt >= 2`: Route to `END`. Record terminal failure `QA_REJECTED`.
    - If `regeneration_attempt < 2`:
      - Increment `state["regeneration_attempt"] += 1`.
      - Identify primary failing finding.
      - Extract `target_agent` (e.g., `"features"`, `"timeline"`, `"task"`) and `recommendation` (becomes `qa_feedback_hint`).
      - Route graph to `target_agent`.

### 9.2 Downstream Dependency Chain Invalidation
Empirical tests on LangGraph confirmed that routing back to an upstream node automatically re-executes only the targeted node and its downstream dependents:
- **Target `timeline`:** Re-executes `timeline` → `risk` → `task` → `milestone` → `readme` → `qa_judge`. (Preserves `idea`, `scope`, `technology`, `features`, `mvp`, `specification`).
- **Target `task`:** Re-executes `task` → `milestone` → `readme` → `qa_judge`. (Preserves all earlier outputs).
- **Target `features`:** Re-executes `features` → `specification` → `timeline` → `risk` → `task` → `milestone` → `readme` → `qa_judge`. (Preserves `idea`, `scope`, `technology`, `mvp`).

---

## 10. Cancellation Architecture

### 10.1 Safe Cooperative Cancellation Protocol (Gate 09 Decision A5)
1. **User Action:** Student calls `POST /api/v1/projects/{id}/blueprint/cancel`.
2. **Authorization & State Validation:**
   - Verify caller ownership.
   - If job status is already terminal (`COMPLETED`, `FAILED`, `CANCELLED`): Return current status (idempotent no-op).
   - Update `blueprint_jobs.cancellation_requested = True` and `status = 'CANCELLING'`.
   - Update `blueprints.status = 'FAILED'`, `error_message = 'Generation cancelled by user'`.
3. **Worker Check Boundaries:**
   - Evaluated before each node execution in `StateGraph`.
   - Evaluated before regeneration transitions.
   - If `cancellation_requested == True`: Node execution halts immediately. State transitions to `CANCELLED`.
4. **Mid-Provider Call Handling (6H § 41):**
   - An HTTP provider request in flight is allowed to complete.
   - The returned model payload is immediately discarded without being written to state or database.
5. **Terminal Race Prevention:**
   - Canonical commit verifies `blueprint_jobs.status == 'RUNNING'` before writing. If the job was marked `CANCELLED` or `CANCELLING`, the final commit is rejected.

---

## 11. Retry, DLQ & Process Restart Recovery

### 11.1 Layered Failure Separation
| Layer | Failure Type | Owner | Behavior |
|---|---|---|---|
| **Layer 1** | Network timeout, provider 429/500, key quota | `AIProviderGateway` (Unit 1) | Automatic key rotation across 5-key pool, exponential backoff, cooldown management. |
| **Layer 2** | Malformed JSON, Pydantic contract mismatch | `BaseAgent` / Gateway | Raises `AIStructuredOutputException`. Bounded agent attempt or graph failure. |
| **Layer 3** | Semantic contradiction, incomplete scope | QA / Judge Agent | Targeted regeneration feedback loop (max 2 attempts). |
| **Layer 4** | Server crash, unhandled worker exception | Background Worker | Job marked `FAILED`, previous canonical blueprint preserved. |
| **Layer 5** | Process restart / server reboot | Startup Recovery (`factory.py`) | `recover_orphaned_jobs()` detects stranded `RUNNING` jobs and marks them `FAILED`. |

### 11.2 Orphan Job Recovery on Startup
The existing `recover_orphaned_jobs()` in `BlueprintRepository` (invoked during FastAPI lifespan startup in `factory.py`) is enhanced to:
1. Query all `blueprint_jobs` with status `RUNNING` or `PENDING`.
2. Transition jobs to `FAILED` with error `"Execution interrupted by server restart"`.
3. Query all `blueprint_jobs` with status `CANCELLING` and transition them to `CANCELLED`.
4. Transition any linked `GENERATING` blueprints to `FAILED`.

---

## 12. Concurrency & Idempotency Guarantees

### 12.1 Preventing Concurrent Conflicting Jobs
A project must never have two concurrent background workflows competing to overwrite the canonical blueprint.
1. **Database Row Lock:** `start_generation()` executes:
   ```sql
   SELECT id, status, generation_number 
   FROM blueprints 
   WHERE project_instance_id = :project_id 
   FOR UPDATE;
   ```
2. **State Guard:**
   - If `status == 'GENERATING'` and `force_regenerate == False`: Return existing session without starting a new job (idempotent).
   - If `status == 'GENERATING'` and `force_regenerate == True`: Mark active job `CANCELLED` before starting new generation.
3. **Atomic Generation Number:** Monotonically increments inside the locked transaction:
   ```sql
   UPDATE blueprints 
   SET generation_number = generation_number + 1 
   WHERE id = :blueprint_id 
   RETURNING generation_number;
   ```

---

## 13. Provenance Persistence (`agent_executions`)

### 13.1 Mapping Unit 3 Provenance to Database
Every agent completion produces an `AgentExecutionProvenance` object. Unit 4 persists this via `AgentExecutionRepository`:
- `blueprint_job_id`: Links execution to the parent generation attempt.
- `blueprint_id`, `project_instance_id`: Scopes execution for project isolation.
- `agent_name`, `agent_version`, `prompt_version`, `contract_version`.
- `generation_number`, `regeneration_attempt`.
- `provider`, `model`, `key_alias` (safe alias e.g. `"key_1"`, raw keys rejected).
- `capability`: `"STANDARD"` or `"REASONING"`.
- `latency_ms`, `total_tokens`, `prompt_tokens`, `completion_tokens`, `cost_usd`.
- `status`: `"COMPLETED"`, `"FAILED"`, or `"CANCELLED"`.
- `started_at`, `completed_at`.

---

## 14. Security & Project Isolation

1. **Strict Ownership Validation:** Caller identity is verified against `CurrentUser` from the Supabase JWT. Students can only trigger generation on projects where `project.student_id == current_user.user_id`.
2. **Context Slicing Integrity:** The worker uses Unit 2's `ProjectContextBuilder` with the authenticated `CurrentUser`. No cross-project context can leak.
3. **Zero Direct DB Access for Agents:** Agents run as pure Python execution functions communicating with the AI gateway. They receive no database connections, ORM models, or SQL repositories.
4. **Credential Safety:** The `agent_executions` table validator strictly enforces key aliasing (`^key_\d+$`) and rejects any string resembling a live secret.

---

## 15. Database Migration Plan

Unit 4 requires an Alembic migration (`0011_gate09_agent_executions_and_generation.py`).

### 15.1 Proposed Schema Operations
```python
def upgrade() -> None:
    # 1. Alter blueprints table
    op.add_column(
        "blueprints",
        sa.Column("generation_number", sa.Integer(), nullable=False, server_default="1"),
    )

    # 2. Alter blueprint_jobs table
    op.add_column(
        "blueprint_jobs",
        sa.Column("generation_number", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "blueprint_jobs",
        sa.Column("cancellation_requested", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "blueprint_jobs",
        sa.Column("locked_by", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "blueprint_jobs",
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 3. Create agent_executions table
    op.create_table(
        "agent_executions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("blueprint_job_id", sa.String(length=36), nullable=False),
        sa.Column("blueprint_id", sa.String(length=36), nullable=False),
        sa.Column("project_instance_id", sa.String(length=36), nullable=False),
        sa.Column("execution_id", sa.String(length=36), nullable=False),
        sa.Column("correlation_id", sa.String(length=36), nullable=False),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("agent_version", sa.String(length=20), nullable=False),
        sa.Column("prompt_version", sa.String(length=20), nullable=False),
        sa.Column("contract_version", sa.String(length=20), nullable=False),
        sa.Column("generation_number", sa.Integer(), nullable=False),
        sa.Column("regeneration_attempt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("key_alias", sa.String(length=50), nullable=False),
        sa.Column("capability", sa.String(length=50), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost_usd", sa.Numeric(precision=10, scale=6), nullable=False, server_default="0.0"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["blueprint_job_id"], ["blueprint_jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["blueprint_id"], ["blueprints.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_instance_id"], ["project_instances.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_executions_blueprint_job_id", "agent_executions", ["blueprint_job_id"])
    op.create_index("ix_agent_executions_project_instance_id", "agent_executions", ["project_instance_id"])
```

---

## 16. Dependency Analysis

- **Installed:** `langgraph` version 1.2.11 is already available in `.venv`.
- **Zero new external dependencies:** No Celery, Redis, RQ, or external brokers are required.
- **`pyproject.toml`:** No changes required.

---

## 17. SSE / Event Boundary for Unit 5

Unit 4 defines an internal event listener/publisher contract (`WorkflowEventPublisher`) that decouples workflow progress from HTTP SSE streaming:
- **Event Catalogue:**
  - `job.started` (`job_id`, `project_id`, `generation_number`, `started_at`)
  - `node.started` (`job_id`, `step_name`, `progress_percent`)
  - `node.completed` (`job_id`, `step_name`, `progress_percent`, `latency_ms`)
  - `qa.evaluated` (`job_id`, `score`, `status`, `findings_count`)
  - `regeneration.started` (`job_id`, `target_agent`, `attempt_number`, `hint`)
  - `job.completed` (`job_id`, `blueprint_id`, `qa_score`)
  - `job.failed` (`job_id`, `error`)
  - `job.cancelled` (`job_id`)
- **Unit 5 Contract:** Unit 5 will subscribe to these events (or read from `ai_execution_events` / `blueprint_jobs`) and stream Server-Sent Events to the client. Unit 4 does NOT implement SSE endpoints.

---

## 18. Test Strategy

A comprehensive test suite for Unit 4 will be structured under `backend/tests/unit/ai/orchestration/`:

1. **Graph Topology & Parallelism:**
   - Verify `Technology`, `Features`, `MVP` execute concurrently without state collision.
   - Verify `Specification` synchronizes all 3 inputs before running.
   - Verify serial ordering (`Timeline` → `Risk` → `Task` → `Milestone` → `README` → `QA`).
2. **Happy Path End-to-End:**
   - Full 12-agent workflow execution using `MockAIProviderAdapter`.
   - QA score ≥ 75 and 0 Critical → returns `PASS` → atomic commit to `blueprints.content`.
3. **Targeted Regeneration:**
   - Mock QA returns score 60 and finding targeting `timeline`.
   - Verify `timeline` and its downstream nodes (`risk`, `task`, `milestone`, `readme`, `qa`) re-execute.
   - Verify `idea`, `scope`, `technology`, `features`, `mvp`, `specification` are NOT re-executed.
4. **Regeneration Bound (Max 2 Attempts):**
   - Mock QA persistently fails across 2 regeneration cycles.
   - Verify workflow halts after attempt 2.
   - Verify blueprint transitions to `QA_REJECTED`.
   - Verify previous valid blueprint content is preserved.
5. **Cancellation Scenarios:**
   - Cancel before workflow begins.
   - Cancel during node transition.
   - Cancel during regeneration cycle.
   - Verify in-flight provider outputs are discarded.
   - Verify job transitions to `CANCELLED`.
6. **Provenance Persistence:**
   - Verify all 12 executions write complete rows into `agent_executions` with correct tokens, models, and latency.
7. **Concurrency & Locking:**
   - Simultaneous generation requests for the same project instance receive idempotent responses or row-lock queuing.
   - `generation_number` increments monotonically and atomically.
8. **Startup Orphan Recovery:**
   - Verify stranded `RUNNING` jobs transition to `FAILED` with restart interruption message.

---

## 19. File-Level Implementation Plan

### A. Orchestration Engine
- `backend/app/domain/ai/orchestration/__init__.py`: Package marker and exports.
- `backend/app/domain/ai/orchestration/state.py`: `OrchestrationState` TypedDict with `Annotated` reducers.
- `backend/app/domain/ai/orchestration/nodes.py`: Node handler functions for all 12 agents.
- `backend/app/domain/ai/orchestration/router.py`: Conditional edge routing for QA evaluation and targeted regeneration.
- `backend/app/domain/ai/orchestration/graph.py`: Factory building and compiling the LangGraph `StateGraph`.

### B. Durable Execution & Worker
- `backend/app/domain/ai/orchestration/worker.py`: Background worker coordinator managing state builder, graph invocation, progress sync, and error handling.
- `backend/app/domain/ai/orchestration/events.py`: Internal event publisher protocol for Unit 5 integration.

### C. Persistence & Database
- `backend/app/infrastructure/database/models/agent_execution.py`: SQLAlchemy ORM model for `agent_executions`.
- `backend/app/infrastructure/database/models/blueprint.py`: Add `generation_number` to `BlueprintModel`; add `generation_number`, `cancellation_requested`, `locked_by`, `locked_at` to `BlueprintJobModel`.
- `backend/app/infrastructure/repositories/agent_execution_repository.py`: CRUD and batch persistence repository for provenance records.
- `backend/app/infrastructure/repositories/blueprint_repository.py`: Add atomic `increment_generation_number()`, update `recover_orphaned_jobs()` for cancellation states.
- `backend/migrations/versions/0011_gate09_agent_executions_and_generation.py`: Alembic migration script.

### D. Service Integration
- `backend/app/application/services/blueprint_service.py`: Update `start_generation()`, `retry_generation()`, and implement `cancel_generation()` to dispatch to the LangGraph worker instead of legacy prototypes.

### E. API Route Enhancement
- `backend/app/api/routes/blueprint.py`: Add `POST /projects/{project_id}/blueprint/cancel` endpoint.

### F. Tests
- `backend/tests/unit/ai/orchestration/test_graph_topology.py`
- `backend/tests/unit/ai/orchestration/test_worker_lifecycle.py`
- `backend/tests/unit/ai/orchestration/test_regeneration_loop.py`
- `backend/tests/unit/ai/orchestration/test_cancellation.py`
- `backend/tests/unit/ai/orchestration/test_provenance_persistence.py`

---

## 20. Risks & Open Questions

1. **R1: Long Execution Timeout Window (Implementation Detail):**
   - *Analysis:* Executing 12 LLM steps (even with 3 parallel) may take 30–90 seconds under live OpenRouter models.
   - *Resolution:* Because execution is completely asynchronous via HTTP 202 and background tasks, the client HTTP connection is never blocked.
2. **R2: LangGraph Checkpointer Strategy (Implementation Detail):**
   - *Analysis:* Should LangGraph's internal `MemorySaver` or Postgres checkpointer be enabled in Unit 4?
   - *Resolution:* Using our lightweight `OrchestrationState` passed to `graph.ainvoke()` coupled with explicit progress writes to `blueprint_jobs` and `agent_executions` gives 100% durability without coupling to LangGraph's experimental binary Postgres checkpointer tables.
3. **R3: Human Decision Items (Already Frozen in Spec Resolution):**
   - QA score ≥ 75 threshold: **FROZEN** (A3).
   - Maximum 2 auto-regeneration attempts: **FROZEN** (A3).
   - Serial TASK → MILESTONE: **FROZEN** (A1).
   - No unresolved architectural ambiguities remain.

---

## 21. Unit 5 Handoff

Unit 4 cleanly prepares the runtime for Unit 5 (SSE / Real-time Events):
- **Contract Defined:** Unit 4 provides `WorkflowEventPublisher` with well-defined event types (`job.started`, `node.started`, `node.completed`, `qa.evaluated`, `regeneration.started`, `job.completed`, `job.failed`, `job.cancelled`).
- **Data Source:** Unit 5 can either hook directly into the in-memory event stream or poll the updated `blueprint_jobs` / `agent_executions` records to stream SSE deltas to frontend clients.
- **Zero SSE Code in Unit 4:** Unit 4 will not touch FastAPI SSE streaming endpoints.

---

## 22. Exact Unit 4 Scope

- LangGraph `StateGraph` definition and compilation.
- 12 agent node wrappers with typed input/output mapping.
- Parallel fan-out (`Technology`, `Features`, `MVP`) and fan-in (`Specification`).
- Serial progression (`Specification` → `Timeline` → `Risk` → `Task` → `Milestone` → `README` → `QA`).
- QA evaluation router and targeted regeneration loop (max 2 attempts).
- Cooperative cancellation handler (`CANCELLING` → `CANCELLED`).
- Alembic database migration for `generation_number`, `cancellation_requested`, and `agent_executions`.
- Persistence repository for `AgentExecutionProvenance`.
- Background worker execution wiring in `BlueprintService`.
- Startup orphan recovery enhancements.
- Unit 4 test suite with mock provider (zero live network calls).

---

## 23. Exact Unit 4 Exclusions

- **NO** live OpenRouter / network calls in tests.
- **NO** external message queues (no Redis, no Celery, no RabbitMQ).
- **NO** SSE streaming implementation (Unit 5).
- **NO** frontend modifications (Unit 6).
- **NO** RAG vector database or LlamaIndex integration (deferred).
- **NO** live Tavily web searches (deferred).
- **NO** Gate 15 observability dashboards or telemetry redesign.
- **NO** modifications to Unit 1 gateway or Unit 2 contracts.
- **NO** Git commit, push, or PR.

---

## 24. Readiness Verdict

# FINAL READINESS VERDICT:
# READY FOR UNIT 4 IMPLEMENTATION

The Unit 4 architectural design is fully reconciled with frozen specifications (Part 6E, Part 6F, Part 6H, Gate 09 Resolutions), builds seamlessly on verified Unit 1, Unit 2, and Unit 3 foundations, and introduces no extraneous dependencies or breaking changes.
