# GrowFlow Gate 09 — Unit 5 Analysis
## Real-Time SSE & Blueprint Generation Event Streaming

---

### 1. Executive Summary

This document establishes the authoritative implementation-readiness analysis for **Gate 09 — Unit 5: Real-Time Server-Sent Events (SSE) & Blueprint Generation Event Streaming**.

Unit 5 is strictly a transport and presentation layer designed to bridge the durable background execution of Unit 4 ([BlueprintWorker](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/domain/ai/orchestration/worker.py) and [WorkflowEventPublisher](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/domain/ai/orchestration/events.py)) to the student-facing browser client via Server-Sent Events (SSE). 

#### Core Architectural Findings
1. **Existing Handoff from Unit 4:** Unit 4 established an internal event protocol ([WorkflowEventPublisher](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/domain/ai/orchestration/events.py#L50-L53)) and typed event catalog ([WorkflowEvent](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/domain/ai/orchestration/events.py#L36-L48)). The durable execution state is reliably tracked in `blueprint_jobs`, `blueprints`, and `agent_executions`.
2. **Current Delivery Model:** Currently, Unit 4 operates with an in-memory event publisher ([NoOpEventPublisher](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/domain/ai/orchestration/events.py#L56-L61) in production, [InMemoryEventPublisher](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/domain/ai/orchestration/events.py#L63-L73) in tests), while the prototype SSE endpoint in [blueprint.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/api/routes/blueprint.py#L223-L272) polls the database every 1 second.
3. **No External Message Broker Required:** Consistent with the modular monolith architecture and explicit project constraints (Rule 0: no Redis, Celery, RabbitMQ, or RQ), Unit 5 will implement an in-process, non-blocking pub/sub broadcast manager (`BlueprintEventManager`) using standard Python `asyncio` primitives (`asyncio.Queue`, `asyncio.Event`, and bounded ring buffers).
4. **Dual Contract Compatibility:** The existing frontend ([StudentBlueprint.tsx](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/frontend/src/pages/Student/StudentBlueprint/StudentBlueprint.tsx) and [client.ts](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/frontend/src/lib/api/client.ts)) already contains an `EventSource` subscriber listening for `event: update` with a `BlueprintStatusResponse` payload. Unit 5 will emit an enriched, client-safe public event projection that is **100% backward-compatible** with the existing frontend while simultaneously delivering granular lifecycle events (`job.started`, `node.started`, `node.completed`, `qa.evaluated`, `regeneration.started`, `job.completed`, `job.failed`, `job.cancelled`).
5. **No Database Migration Required:** All durable state (job status, generation number, progress percentage, QA findings, canonical content, and per-agent execution provenance) is already persisted in the existing schema (`blueprints`, `blueprint_jobs`, `agent_executions`). Real-time streaming is ephemeral transport telemetry; introducing an event table would be redundant and wasteful.
6. **Authentication via Native EventSource:** The existing backend authentication dependency ([auth.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/api/dependencies/auth.py#L70-L74)) already explicitly permits query parameter token extraction (`?token=...`) strictly for `/events` endpoints to support native browser `EventSource`, while preserving `Authorization: Bearer <token>` header support for fetch-based clients.

**Readiness Verdict:** **READY FOR UNIT 5 IMPLEMENTATION** (subject to human approval of this analysis).

---

### 2. Authoritative References
- **GrowFlow Part 6F § 4, 12–14, 31–35, 92:** Agent Dependency Graph, State Management, QA & Regeneration Topologies, Provenance.
- **GrowFlow Part 6H § 35–39:** Background Jobs, Reliability, SSE Lifecycle, Reconnection, Outbox vs Execution Stream.
- **GrowFlow Part 6C § 2, 13:** API Architecture, Canonical Dependency Boundary, Blueprint Endpoints.
- **GrowFlow Part 6D § 2, 14–16:** Authentication, Authorization Context, Project Isolation, Role Enforcement.
- **`docs/FRONTEND_BACKEND_CONTRACT.md` § 13:** Authoritative Background Job & SSE Contract (`event: update`, keepalive `: keep-alive\n\n`, `retry: 2000`).
- **`docs/gate09_unit4_analysis.md` & `docs/implementation/GATE_09_UNIT_4_EVIDENCE.md`:** Unit 4 Implementation Evidence.

---

### 3. Current Repository Audit

#### Backend File Audit
| File Path | Current Role | Unit 5 Relevance |
| :--- | :--- | :--- |
| `backend/app/domain/ai/orchestration/events.py` | Defines `WorkflowEventType`, `WorkflowEvent`, `WorkflowEventPublisher`, `NoOpEventPublisher`, `InMemoryEventPublisher`. | **Core Foundation:** Will be extended with the in-process pub/sub manager (`BlueprintEventManager`). |
| `backend/app/domain/ai/orchestration/worker.py` | Executes background job, claims leases, invokes LangGraph, calls `event_publisher.publish()`. | **Event Source:** Emits `job.started`, `job.completed`, `job.failed`, `job.cancelled`. |
| `backend/app/domain/ai/orchestration/nodes.py` | Wraps all 12 agents, checks cancellation, records provenance. | **Event Source:** Emits `node.started`, `node.completed`, `qa.evaluated`. |
| `backend/app/domain/ai/orchestration/router.py` | Pure routing node `node_regeneration_router`, evaluates QA pass/fail, routes regeneration. | **Regeneration Boundary:** Target agent and hint calculated here. |
| `backend/app/application/services/blueprint_service.py` | Manages blueprint lifecycle, starts generation, cancels generation. | **Service Layer:** Injects shared `BlueprintEventManager` into `BlueprintWorker`. |
| `backend/app/api/routes/blueprint.py` | Contains prototype `GET /events` route that currently polls database. | **Primary Route Modification:** Replace database polling with reactive subscription to `BlueprintEventManager`. |
| `backend/app/api/dependencies/auth.py` | Authenticates JWT; already supports query parameter `?token=` on `/events`. | **Auth Dependency:** Reused as-is without modification. |

#### Frontend File Audit
| File Path | Current Role | Unit 5 Relevance |
| :--- | :--- | :--- |
| `frontend/src/lib/api/client.ts` | Exports `subscribeBlueprintEvents(projectId, onUpdate, onError)`. Instantiates `new EventSource(url + '?token=' + token)`. Listens for `event: update`. | **Client Transport:** Authoritative subscriber interface; must remain 100% compatible. |
| `frontend/src/pages/Student/StudentBlueprint/StudentBlueprint.tsx` | Main blueprint workspace; invokes `startLiveTracking(pid)` on mount/generation. Updates UI state on event. Closes on terminal state. | **Client Presentation:** Receives `BlueprintStatusResponse`; transparently falls back to polling on disconnect. |
| `frontend/src/test/batch4JobsSseReliability.test.tsx` | Vitest suite verifying SSE progress advancement, terminal closure, idempotency, and polling fallback. | **Verification Benchmark:** Proves frontend contract expectations. |

---

### 4. Unit 4 Event Boundary Audit

Unit 4 established a clean, internal event catalog in `backend/app/domain/ai/orchestration/events.py`:

```python
class WorkflowEventType(StrEnum):
    JOB_STARTED = "job.started"
    NODE_STARTED = "node.started"
    NODE_COMPLETED = "node.completed"
    QA_EVALUATED = "qa.evaluated"
    REGENERATION_STARTED = "regeneration.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_CANCELLED = "job.cancelled"
```

#### Event Emission Locations in Unit 4
1. **`job.started`:** Emitted in `worker.py` immediately after lease acquisition and initial state assembly (progress: 5%).
2. **`node.started`:** Emitted in `nodes.py` before an agent executes (e.g. `idea`, `scope`, `technology`, etc.).
3. **`node.completed`:** Emitted in `nodes.py` after an agent completes execution and persists provenance.
4. **`qa.evaluated`:** Emitted in `nodes.py` after `qa_judge` completes evaluation.
5. **`regeneration.started`:** Defined in `events.py`. In Unit 4, `node_regeneration_router` is a pure synchronous function, but `nodes.py` inspects `regeneration_attempt > 0` on targeted nodes. Emitting `regeneration.started` at the router boundary or targeted node entry is required for Unit 5 visibility.
6. **`job.completed`:** Emitted in `worker.py` strictly after QA PASS and canonical database commit (progress: 100%).
7. **`job.failed`:** Emitted in `worker.py` on agent exception, unhandled worker error, or QA rejection after 2 exhausted regeneration attempts.
8. **`job.cancelled`:** Emitted in `worker.py` when cooperative cancellation is confirmed.

---

### 5. Current SSE/Streaming Audit & Delivery Model

#### Analysis of the Current Mechanism
- **Finding:** Unit 4 currently has **Model D: In-memory event publisher + durable database job/provenance state**.
- The `BlueprintWorker` invokes `self._event_publisher.publish(event)`, which currently points to `NoOpEventPublisher()` in production.
- The existing endpoint `GET /api/v1/projects/{project_id}/blueprint/events` in `blueprint.py`:
  - Enters an asynchronous polling loop: `while not await request.is_disconnected(): bp = await service.get_status(...); await asyncio.sleep(1)`.
  - Calculates a string signature from database values: `f"{bp_status_val}:{bp.progress_percent}:{bp.current_step}:{bp.updated_at}"`.
  - Emits `event: update` when the signature changes, or `: keep-alive\n\n` if unchanged.

#### Key Limitations of the Current Prototype Loop
1. **Inefficient Database Polling:** 50 active students viewing generation results in 50 repeated `SELECT` queries per second against PostgreSQL.
2. **Coarse Granularity:** A 1-second polling interval cannot observe fast transitions (e.g. parallel agents finishing in 200–500ms) or micro-steps.
3. **Disconnected from Worker Events:** Structured events already emitted by `BlueprintWorker` are discarded by `NoOpEventPublisher`.

#### Unit 5 Solution
Unit 5 replaces the database polling loop with an **event-driven, in-process broadcast subscriber** while preserving the database query strictly for:
1. Pre-flight authorization and initial state hydration on connection.
2. Reconnection fallback when an event sequence cannot be replayed from memory.

---

### 6. Authentication Strategy

#### Analysis of SSE Authentication Constraints
Native browser `EventSource` (`new EventSource(url)`) **cannot send custom HTTP headers** (such as `Authorization: Bearer <token>`).

#### Evaluated Options
| Option | Mechanism | Pros | Cons | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **A. Query Param Token** | `GET /events?token=<jwt>` | Works natively with browser `EventSource` without external libraries. | Token visible in query string / access logs if not sanitized. | **Recommended (Existing Standard)** |
| **B. Cookie-Based Auth** | `HttpOnly` cookie | Seamless with `EventSource`. | Requires separate cookie architecture, CSRF protection, conflicts with stateless JWT model. | Not Recommended |
| **C. Fetch / ReadableStream** | Custom fetch reader | Allows `Authorization` header. | Requires custom frontend stream parser; breaks existing `EventSource` in `client.ts`. | Excluded (Rule 0: No frontend changes) |

#### Existing Architecture Alignment
`backend/app/api/dependencies/auth.py` already includes a specific, secure exemption for query tokens:
```python
query_token = request.query_params.get("token")
if query_token and request.url.path.endswith("/events"):
    raw_token = query_token
else:
    raise AuthenticationException(...)
```
- Non-SSE REST endpoints strictly reject query parameter tokens (tested in `test_batch4_jobs_sse_reliability_api.py`).
- Token verification strictly enforces PyJWT signature verification, issuer check, expiration, and user account status (`ACTIVE`).
- Token lifetimes are standard Supabase session tokens (1 hour). For long generations (2–3 minutes), the token remains valid.

---

### 7. Authorization & Project Isolation

The SSE connection must strictly enforce tenant isolation before any event streaming occurs:
1. **Pre-flight Project Ownership Verification:**
   - Resolve `current_user` via `get_current_user`.
   - Call `BlueprintService._verify_project_ownership(project_id, current_user)`.
   - If `project.student_id != current_user.user_id` (and user is not admin): raise `AuthorizationException(403 Forbidden)`.
   - If project does not exist: raise `NotFoundException(404 Not Found)`.
   - If student account is `SUSPENDED` or `INACTIVE`: raise `AuthorizationException(403 Forbidden)`.
2. **Channel Scoping:**
   - Subscribers register strictly to their own `project_id`.
   - The SSE route never accepts an arbitrary `job_id` query parameter from the client; it resolves the active job directly from the authorized `project_id`.

---

### 8. Event Contract & Public SSE Event Projection

#### Security & Redaction Boundary
The SSE stream must **never** leak internal architectural secrets or private data to the browser client:
- **STRICTLY EXCLUDED:** Raw provider API keys, provider headers, internal model routing parameters, system prompts, raw student assessment answer texts, internal Python exception tracebacks, uncommitted partial blueprint outputs.
- **CLIENT-SAFE FIELDS:** Event type, event ID, timestamp, current step name, progress percent, generation number, regeneration attempt count, high-level QA score, sanitized issue counts, public status.

#### Unified Public Event Envelope (`BlueprintSSEEvent`)
To maintain 100% compatibility with the existing frontend `subscribeBlueprintEvents` while delivering rich Unit 5/6 data, each SSE message is formatted as:
```text
id: <event_id>
event: update
retry: 2000
data: <JSON_ENVELOPE>
```

#### JSON Payload Structure
```json
{
  "event_id": "proj-123_1_004",
  "event_type": "node.completed",
  "event_version": "1.0",
  "job_id": "8b066d92-1234-4567-89ab-cdef01234567",
  "project_id": "proj-123",
  "generation_number": 1,
  "timestamp": "2026-09-20T03:40:15.123Z",
  "status": "GENERATING",
  "current_step": "technology",
  "progress_percent": 35,
  "current_stage": 3,
  "generation_progress": {
    "completed_sections": ["project_profile", "tech_stack"],
    "total_sections": 10,
    "in_progress_section": "features",
    "failed_sections": []
  },
  "qa_status": "PENDING",
  "qa_score": null,
  "regeneration_attempt": 0,
  "regeneration_target": null,
  "active_job": {
    "id": "8b066d92-1234-4567-89ab-cdef01234567",
    "job_type": "FULL_GENERATION",
    "status": "RUNNING",
    "error_message": null,
    "created_at": "2026-09-20T03:39:50.000Z"
  }
}
```

---

### 9. Public Event Catalog

| Event Name | Trigger Condition | Step Name | Progress % | Key Public Payload |
| :--- | :--- | :--- | :--- | :--- |
| `job.started` | Worker claims job lease & initializes workflow | `idea` | 5% | `status: "GENERATING"`, `generation_number: 1` |
| `node.started` | Prior to executing a specific agent node | `<node_name>` | Node start % | `in_progress_section: "<section>"` |
| `node.completed` | After agent completes & persists provenance | `<node_name>` | Node end % | `completed_sections: [...]` |
| `qa.evaluated` | After QAJudgeAgent completes scoring | `qa_judge` | 90% | `qa_score: <score>`, `qa_status: "PASS" \| "FAIL"` |
| `regeneration.started`| QA failed (<75 or CRITICAL); routing to target | `regenerating_<target>` | 90% | `regeneration_target: "<agent>"`, `regeneration_attempt: <n>` |
| `job.completed` | QA passed; canonical blueprint committed to DB | `completed` | 100% | `status: "READY_FOR_APPROVAL"`, `qa_score: <score>` |
| `job.failed` | Agent error, system crash, or QA rejection | `failed` / `qa_judge` | Last % | `status: "FAILED" \| "QA_REJECTED"`, `error_message: "..."` |
| `job.cancelled` | Cooperative cancellation confirmed | `cancelled` | Last % | `status: "CANCELLED"`, `cancellation_requested: true` |

---

### 10. Event IDs & Replay Strategy

#### Event ID Structure
Each event receives a deterministic, monotonic identifier:
$$\text{event\_id} = \text{project\_id} + \text{"\_"} + \text{generation\_number} + \text{"\_"} + \text{seq}$$
Example: `proj-123_1_007`
- `project_id`: guarantees cross-project uniqueness.
- `generation_number`: binds the event strictly to the current generation job (preventing replaying events from past generations).
- `seq`: zero-padded 3-digit monotonically increasing sequence integer (`001`, `002`, ...).

#### Replay Buffer Architecture
- The in-process `BlueprintEventManager` maintains a bounded **ring buffer** per active project (maximum 50 events).
- If a client disconnects and reconnects with the standard `Last-Event-ID` header:
  1. Parse `(pid, gen, seq)` from `Last-Event-ID`.
  2. If `pid == project_id` and `gen == current_generation`: replay all buffered events where `event.seq > seq`.
  3. If `seq` is older than the oldest buffered event or buffer is empty: emit the authoritative database snapshot immediately as a baseline.

---

### 11. Reconnect Strategy & Lifecycle Handling

```text
Client Connection Request
        ↓
Pre-flight Authorization (Auth & Ownership)
        ↓
Query Current DB State (blueprints & blueprint_jobs)
        ↓
Is Generation Active (RUNNING / PENDING)?
 ├── NO (COMPLETED / FAILED / QA_REJECTED / NOT_STARTED):
 │     Emit Terminal Snapshot Event
 │     Close Stream Gracefully
 └── YES:
       Has Last-Event-ID?
        ├── YES & in buffer: Replay missed events from buffer
        └── NO or buffer expired: Emit Current State Snapshot
       Register Subscriber Queue
       Stream Live Events from BlueprintEventManager
       Emit ': keep-alive\n\n' every 15s if idle
       On Terminal Event: Emit Event & Close Stream
       On Client Disconnect: Unregister Queue Cleanly
```

#### Detailed Scenario Analysis
1. **Initial Connection:** Client connects; gets immediate snapshot of current progress (zero blank-screen delay).
2. **Temporary Network Drop:** Client disconnects; browser reconnects after 2000ms sending `Last-Event-ID`; server replays buffered events; stream continues seamlessly.
3. **Browser Refresh:** Tab reloads; establishes new connection; receives current snapshot; resumes live streaming.
4. **Backend Restart:** Server restarts; worker dies; startup recovery marks orphaned job `FAILED`; client reconnects; server queries DB, sends terminal `FAILED` event; frontend stops cleanly.
5. **Worker Finishes Before Connection:** If fast mock generation finishes before client connects, server queries DB, sees `COMPLETED`, emits `job.completed` snapshot, and closes stream. Client never hangs.
6. **Multiple Browser Tabs:** Both tabs connect; each gets an independent queue; both receive broadcast events without interfering with each other.

---

### 12. Progress Semantics

#### Deterministic Progress Schedule
| Milestone / Node | Action | Progress % | Cumulative Completed Sections |
| :--- | :--- | :--- | :--- |
| Job Claim | `job.started` | 5% | `[]` |
| `idea` | Idea synthesis | 15% | `["project_profile"]` |
| `scope` | Scope definition | 25% | `["project_profile"]` |
| `technology` | Tech stack reasoning | 35% | `["project_profile", "tech_stack"]` |
| `features` | Core features reasoning | 45% | `["project_profile", "tech_stack", "features"]` |
| `mvp` | MVP specification | 55% | `["project_profile", "tech_stack", "features", "mvp"]` |
| `specification` | Spec synthesis | 65% | `[..., "specifications"]` |
| `timeline` | Schedule synthesis | 70% | `[..., "duration"]` |
| `risk` | Risk management | 75% | `[..., "risks"]` |
| `task` | Work breakdown | 80% | `[..., "tasks"]` |
| `milestone` | Milestone breakdown | 85% | `[..., "milestones"]` |
| `readme` | Documentation | 90% | `[..., "readme"]` |
| `qa_judge` | Quality evaluation | 90% | (Evaluation phase) |
| Canonical Commit | `job.completed` | **100%** | All 10 canonical sections |

#### Invariants
- **Monotonicity during initial generation:** Progress strictly advances from 5% to 100%.
- **Regeneration stability:** When regeneration occurs, progress does **NOT** swing backward. It holds at 90% while the step indicator updates to `current_step = "regenerating_<target>"` with `regeneration_attempt = 1`. This prevents jarring progress bar jitter in the UI.
- **Terminal failure:** Terminal failures (`FAILED`, `QA_REJECTED`, `CANCELLED`) never reach 100%.

---

### 13. Regeneration Event Semantics

When QA evaluation fails (`score < 75` or `CRITICAL > 0`):
1. **`qa.evaluated`:**
   ```json
   {
     "event_type": "qa.evaluated",
     "qa_status": "FAIL",
     "qa_score": 64,
     "payload": {
       "issues_count": 2,
       "critical_count": 1,
       "summary": "Data model inconsistencies detected in database schema."
     }
   }
   ```
2. **`regeneration.started`:**
   ```json
   {
     "event_type": "regeneration.started",
     "current_step": "regenerating_specification",
     "regeneration_attempt": 1,
     "regeneration_target": "specification",
     "payload": {
       "target_agent": "specification",
       "attempt": 1,
       "max_attempts": 2,
       "hint": "Refine relational schemas to eliminate foreign key ambiguities."
     }
   }
   ```
3. **Downstream Execution:**
   - Client observes `node.started` and `node.completed` for `specification`, `timeline`, `risk`, `task`, `milestone`, `readme`.
   - `qa.evaluated` fires again.
   - If score $\ge 75$ and 0 critical findings: `job.completed` fires with `progress_percent: 100` and `status: "READY_FOR_APPROVAL"`.

---

### 14. Terminal State Semantics

#### Terminal Status Set
A blueprint generation job reaches a terminal state when status is one of:
- `COMPLETED` (mapped to `READY_FOR_APPROVAL` on the blueprint session)
- `FAILED`
- `QA_REJECTED`
- `CANCELLED`

#### Teardown Protocol
1. Backend sends the final event (`job.completed`, `job.failed`, or `job.cancelled`).
2. Backend immediately terminates the HTTP response generator, closing the TCP stream.
3. The frontend `EventSource` listener detects the terminal status, calls `es.close()`, and:
   - On success: triggers `getBlueprintContent(projectId)` to fetch the canonical Markdown document.
   - On failure/rejection/cancellation: preserves existing UI state and displays the truthful error banner.

---

### 15. Heartbeat & Keepalive Strategy

- **Risk:** Cloud proxies (Cloudflare, Render, Vercel, NGINX, AWS ALB) close idle HTTP connections after 15–60 seconds without data.
- **Specification:** The backend event generator evaluates an idle timeout of **15 seconds**.
- If no workflow event has been pulled from the subscriber queue within 15 seconds, the generator yields:
  ```text
  : keep-alive\n\n
  ```
- Standard browser `EventSource` ignores lines beginning with `:` (treated as comments), while TCP proxy keepalive timers are reset.

---

### 16. Backpressure & Resource Safety

To prevent memory leaks and worker slowdowns caused by slow or unresponsive browser clients:
1. **Bounded Subscriber Queues:** Each subscriber queue has a strict maximum size: `asyncio.Queue(maxsize=100)`.
2. **Non-Blocking Put:** When broadcasting events, `put_nowait()` is used. If a slow client's queue fills up to 100 unread messages, it is evicted immediately (`dead_queues.add(q)`).
3. **Worker Isolation:** The worker publishes to the manager in-memory. Under no circumstances can a slow client or stalled HTTP connection block the LangGraph execution worker.
4. **Subscriber Cleanup:** When `request.is_disconnected()` is detected, the subscriber queue is immediately removed from the active set and garbage-collected.
5. **Buffer Pruning:** Job buffers in `_recent_events` are automatically pruned 60 seconds after job completion.

---

### 17. Multi-Subscriber Behavior

- **Independent Subscriptions:** If a student opens the blueprint page in two browser tabs or on two devices, both connect to `/events`.
- Each connection creates an independent `asyncio.Queue`.
- Both queues receive identical broadcast events.
- Closing or refreshing one tab does not affect the other tab or the background worker.

---

### 18. Failure Mode Matrix

| Failure Mode | Detection Point | Backend Response | Frontend Response | Recovery Action |
| :--- | :--- | :--- | :--- | :--- |
| **Client network drop** | ASGI `request.is_disconnected()` | Evicts subscriber queue; worker continues uninterrupted | `es.onerror` fires | Transparent fallback to polling `GET /status` or automatic reconnect via `retry: 2000` |
| **JWT expired during stream** | Pre-flight auth or reconnect | Returns 401 Unauthorized | Auth interceptor triggers token refresh | Refreshes token and re-establishes stream |
| **Cross-project access** | Pre-flight auth check | Returns 403 Forbidden | Displays authorization error | Stream aborted immediately |
| **Worker exception** | `try...except` in `BlueprintWorker` | Emits `job.failed`; preserves canonical DB content | Receives `job.failed`; displays error banner | Previous canonical blueprint remains safe |
| **QA Rejection (2 attempts)** | `router.py` limit check | Emits `job.failed` with `reason: QA_REJECTED` | Displays QA rejection review card | Student can trigger manual retry or review findings |
| **User cancels generation** | `POST /blueprint/cancel` | Worker aborts at next node; emits `job.cancelled` | Displays cancellation banner | Previous canonical blueprint remains safe |
| **Backend server reboot** | Server restart lifecycle | Startup orphan recovery marks job `FAILED` in DB | Next reconnect reads DB snapshot showing `FAILED` | Truthful failure displayed; no zombie jobs |

---

### 19. Backend Architecture

Unit 5 introduces a lightweight, in-process event broker and refines the existing SSE route:

```
┌──────────────────────────────────────────────────────────┐
│                   BlueprintWorker                        │
└────────────────────────────┬─────────────────────────────┘
                             │ calls publish(event)
                             ▼
┌──────────────────────────────────────────────────────────┐
│          BlueprintEventManager (Protocol Implementation) │
│  - _subscribers: dict[project_id, set[asyncio.Queue]]    │
│  - _recent_events: dict[project_id, list[WorkflowEvent]] │
└──────────────┬────────────────────────────┬──────────────┘
               │ queue.put_nowait()         │ queue.put_nowait()
               ▼                            ▼
┌───────────────────────────────┐ ┌───────────────────────────────┐
│ Client 1 SSE Generator Loop   │ │ Client 2 SSE Generator Loop   │
│ (GET /blueprint/events)       │ │ (GET /blueprint/events)       │
└──────────────┬────────────────┘ └──────────────┬────────────────┘
               ▼ text/event-stream               ▼ text/event-stream
        Browser Tab 1                     Browser Tab 2
```

#### Proposed Component: `BlueprintEventManager`
- Located in: `backend/app/domain/ai/orchestration/events.py` (or supporting `manager.py`).
- Extends `WorkflowEventPublisher`.
- Provides:
  - `publish(event: WorkflowEvent) -> None`
  - `subscribe(project_id: str) -> AsyncIterator[WorkflowEvent]`
  - `get_replay_events(project_id: str, last_seq: int) -> list[WorkflowEvent]`

---

### 20. Frontend Architecture

#### Zero Frontend Modification Rule
- Unit 5 enforces **Rule 0: No frontend code changes**.
- The existing frontend in [client.ts](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/frontend/src/lib/api/client.ts) and [StudentBlueprint.tsx](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/frontend/src/pages/Student/StudentBlueprint/StudentBlueprint.tsx) will consume the Unit 5 stream without requiring any TypeScript/React modifications.
- The public SSE event envelope will populate `status`, `progress_percent`, `generation_progress`, `current_stage`, `qa_status`, and `qa_feedback` exactly matching `BlueprintStatusResponse`.

---

### 21. Database & Migration Decision

- **Verdict:** **NO DATABASE MIGRATION REQUIRED.**
- **Rationale:**
  - All persistent state requirements are already satisfied by `blueprints`, `blueprint_jobs`, and `agent_executions` (established in Unit 4 via migration `0011`).
  - Real-time workflow events are transient streaming telemetry. Storing individual `node.started` events in PostgreSQL would create unnecessary database write pressure and require retention/pruning cron jobs without providing any durability benefit.

---

### 22. Deployment Compatibility

- **Runtime Environment:** FastAPI running on Uvicorn (ASGI).
- **Hosting Targets:** Render / Railway / Docker / Linux VPS.
- **Proxy Buffering Prevention:**
  - `StreamingResponse` sets `headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}`.
  - `X-Accel-Buffering: no` instructs NGINX reverse proxies to stream chunks immediately rather than buffering the response.
- **Worker Concurrency:** Standard Python async task execution via `asyncio.create_task()`.

---

### 23. Security Analysis

1. **Information Leakage Prevention:**
   - Public event schemas are explicitly projected.
   - Raw model prompts, provider secrets, API keys, student assessment text answers, and database IDs are stripped.
2. **Access Control:**
   - Pre-flight JWT verification.
   - Pre-flight student project ownership check.
   - Fail-closed on inactive or suspended accounts.
3. **Query Parameter Token Protection:**
   - Query string tokens are restricted exclusively to routes ending in `/events`.
   - Access logging middleware should sanitize query parameters containing `token=`.

---

### 24. Test Strategy

Unit 5 verification will be implemented in `backend/tests/unit/ai/orchestration/test_sse_streaming.py` and `backend/tests/api/test_blueprint_sse_api.py`:

#### Test Scenarios
1. **Authorization & Security:**
   - Valid JWT via `Authorization: Bearer <token>` connects successfully (200 OK, `text/event-stream`).
   - Valid JWT via `?token=<jwt>` connects successfully.
   - Missing or expired token returns 401.
   - Cross-project access by Student B on Student A's project returns 403.
   - Suspended student account returns 403.
   - Nonexistent project returns 404.
2. **Event Delivery & Ordering:**
   - Connecting to active job streams `job.started` $\to$ `node.started` $\to$ `node.completed` $\to$ `job.completed` in correct sequence.
   - All events formatted as `id: ...`, `event: update`, `retry: 2000`, `data: ...`.
   - Keepalive comments `: keep-alive\n\n` emitted during idle intervals.
3. **Reconnection & Replay:**
   - Reconnecting with `Last-Event-ID` replays missed events from ring buffer.
   - Reconnecting with expired/unknown `Last-Event-ID` receives current state snapshot.
4. **Terminal States & Teardown:**
   - `job.completed` terminates stream.
   - `job.failed` terminates stream with truthful failure payload.
   - `job.cancelled` terminates stream with cancellation payload.
   - Client disconnect evicts subscriber queue without memory leaks.
5. **Multi-Subscriber Concurrency:**
   - Two concurrent subscribers to the same project receive identical broadcast events.
   - Evicting one subscriber does not disrupt the other.

---

### 25. Performance & Scale Analysis

- **1 Active Generation:** Negligible overhead (1 background task, 1 open SSE connection, ~15 events total, ~20 KB total bandwidth).
- **10 Concurrent Generations:** ~10 open SSE connections, ~150 total events over 2 minutes, ~50 KB memory for event queues. Uvicorn handles thousands of concurrent idle ASGI connections effortlessly.
- **50 Concurrent Generations:** Database query load reduced by **98%** compared to the 1-second polling prototype (queries occur only on connection/reconnection rather than continuously every second).

---

### 26. File-Level Implementation Plan

#### Backend Files
| File Path | Action | Description |
| :--- | :--- | :--- |
| `backend/app/domain/ai/orchestration/events.py` | **Modify** | Implement `BlueprintEventManager` (in-process pub/sub, ring buffer, subscriber registry) implementing `WorkflowEventPublisher`. |
| `backend/app/application/services/blueprint_service.py` | **Modify** | Inject singleton/shared `BlueprintEventManager` into `BlueprintWorker`. |
| `backend/app/api/routes/blueprint.py` | **Modify** | Refactor `GET /projects/{project_id}/blueprint/events` to subscribe to `BlueprintEventManager`, support `Last-Event-ID`, and stream typed public envelopes. |

#### Tests
| File Path | Action | Description |
| :--- | :--- | :--- |
| `backend/tests/unit/ai/orchestration/test_sse_streaming.py` | **Create** | Comprehensive unit tests for `BlueprintEventManager`, queue eviction, ring buffer replay, and keepalive timing. |
| `backend/tests/api/test_blueprint_sse_api.py` | **Create** | End-to-end API tests for SSE streaming, query token auth, cross-project denial, and terminal state teardown. |

---

### 27. Dependency Analysis

- **FastAPI / Starlette:** Native `StreamingResponse` is already present and supported.
- **Uvicorn:** Native ASGI streaming support is already present.
- **Python Standard Library:** `asyncio.Queue`, `asyncio.Event`, `collections.defaultdict` are standard.
- **Conclusion:** **ZERO new third-party dependencies required.**

---

### 28. Unit 4 Compatibility Assessment

- **Compatibility Rating:** **100% Compatible.**
- Unit 4 already calls `event_publisher.publish(WorkflowEvent(...))` at all critical lifecycle points.
- Replacing `NoOpEventPublisher()` with `BlueprintEventManager` in `BlueprintService` seamlessly activates real-time streaming without modifying agent logic, graph topology, or database schemas.

---

### 29. Unit 5 Exact Scope

- Implement in-process `BlueprintEventManager` in `events.py`.
- Refactor `GET /api/v1/projects/{project_id}/blueprint/events` to use `BlueprintEventManager`.
- Support `Last-Event-ID` reconnection and ring buffer replay.
- Implement 15-second heartbeat keepalive.
- Maintain 100% backward-compatible `BlueprintStatusResponse` projection inside `event: update`.
- Implement comprehensive unit and API test suite.

---

### 30. Unit 5 Explicit Exclusions

- **NO** external message brokers (Redis, Celery, RabbitMQ, RQ).
- **NO** database schema modifications or migrations.
- **NO** frontend code modifications.
- **NO** live LLM network calls in tests.
- **NO** changes to Unit 1, Unit 2, or Unit 3 agent implementations or prompts.
- **NO** RAG or Tavily integration.
- **NO** Gate 15 observability dashboards.

---

### 31. Implementation Sequence

The implementation will proceed in a single, controlled run:
1. **Stage 1 (Event Broker):** Extend `backend/app/domain/ai/orchestration/events.py` with `BlueprintEventManager` (bounded subscriber queues, ring buffer replay, lifecycle helpers).
2. **Stage 2 (Service Integration):** Update `BlueprintService` to instantiate `BlueprintWorker` with the active `BlueprintEventManager`.
3. **Stage 3 (SSE Route Refactoring):** Refactor `stream_blueprint_events` in `backend/app/api/routes/blueprint.py` to stream live events, format public envelopes, support `Last-Event-ID`, and yield 15s keepalives.
4. **Stage 4 (Unit & API Tests):** Create `test_sse_streaming.py` and `test_blueprint_sse_api.py`.
5. **Stage 5 (Regression & Verification):** Run full test suite (Unit 5, Unit 4, Unit 1, Unit 2, Unit 3, full backend unit suite, Ruff, Ruff format, Mypy).
6. **Stage 6 (Evidence):** Generate `docs/implementation/GATE_09_UNIT_5_EVIDENCE.md`.

---

### 32. Risks & Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| **Unbounded Queue Memory Growth** | Slow client causes queue buildup | Strictly cap `asyncio.Queue(maxsize=100)`; evict stalled subscriber queues immediately with `put_nowait()`. |
| **Reverse Proxy Idle Timeout** | Cloud proxy terminates connection | Emit `: keep-alive\n\n` comments every 15 seconds during idle periods. |
| **Client Disconnect Leak** | Zombie generator tasks consume resources | Monitor ASGI `request.is_disconnected()`; unregister queues in a `finally:` block. |
| **Frontend Contract Drift** | Existing UI breaks | Emit `event: update` with full `BlueprintStatusResponse` fields for 100% backward compatibility. |

---

### 33. Open Questions / Human Decisions

1. **Dual Event Emission vs Single Envelope:**
   - **Recommendation:** Emit `event: update` containing the full envelope with `event_type` inside data. This guarantees 100% backward compatibility with `StudentBlueprint.tsx` while providing all necessary metadata for Unit 6.
2. **Event Replay Buffer Size:**
   - **Recommendation:** 50 events per active project (requires $<10$ KB per active generation and easily covers a 2-minute workflow).

---

### 34. Unit 6 Handoff

Unit 6 (Frontend Generation & Monitoring Experience) will receive:
1. An active, low-latency SSE endpoint streaming live progress.
2. Rich lifecycle metadata (`event_type`, `regeneration_attempt`, `regeneration_target`, `qa_score`) available directly in the event stream.
3. Fully functional cancellation and recovery mechanics proven by Unit 4 and Unit 5.

---

### 35. Final Readiness Verdict

**READY FOR UNIT 5 IMPLEMENTATION**
All architectural boundaries, protocols, and security invariants have been reconciled and verified against the existing codebase.
