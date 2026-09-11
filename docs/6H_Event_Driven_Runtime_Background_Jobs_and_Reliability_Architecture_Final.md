# GrowFlow — Part 6H
# Event-Driven Runtime, Background Jobs & Reliability Architecture — Final Specification

**Status:** FROZEN  
**Part:** 6H  
**System:** GrowFlow  
**Scope:** Domain events, transactional outbox, event publication, event handlers, background jobs, worker architecture, job lifecycle, retries, idempotency, dead-letter handling, scheduling, long-running execution, AI/RAG/document/GitHub/email workloads, SSE integration, cancellation, concurrency, stale execution protection, transaction boundaries, recovery, reconciliation, observability, graceful shutdown, testing, and operational reliability.

---

# 1. Purpose

Part 6H defines how GrowFlow executes work that must continue beyond a single HTTP request and how important application changes propagate safely across the platform.

GrowFlow already established:

- Modular Monolith;
- PostgreSQL/Supabase;
- FastAPI;
- layered architecture;
- application services;
- domain services;
- transactional state;
- internal domain events;
- background workers;
- AI/agent execution;
- RAG/document processing;
- centralized notifications;
- SSE;
- correlation IDs;
- idempotency;
- failure isolation.

6H turns those architectural decisions into one coherent runtime model.

The primary objective is:

> **Make asynchronous and event-driven behavior reliable without introducing unnecessary distributed infrastructure.**

---

# 2. Core Reliability Principles

1. PostgreSQL remains the authoritative transactional store.
2. Core state changes happen inside application/domain transactions.
3. Important domain events are recorded reliably with their state change.
4. The transactional outbox prevents database/event publication inconsistency.
5. Background workers execute long-running work outside request lifecycles.
6. Jobs are persisted before workers begin meaningful work.
7. Every retryable operation is bounded.
8. Idempotency is mandatory for externally repeatable operations.
9. A browser disconnect must not destroy long-running server work.
10. SSE is a delivery mechanism, not the execution mechanism.
11. Event handlers must be independently failure-tolerant.
12. One failed handler must not corrupt canonical state.
13. Stale AI/agent results must not overwrite newer project state.
14. Authorization is revalidated for sensitive background work where required.
15. Secrets are never placed in events, queues, logs, or job payloads.
16. Events contain identifiers and safe metadata, not unnecessary private content.
17. No Kafka/RabbitMQ/Kubernetes/service mesh is required initially.
18. No event sourcing is introduced.
19. The outbox is for reliable event delivery, not for storing the entire history of the system.
20. Workers remain part of the modular monolith deployment model unless scale later proves otherwise.

---

# 3. Runtime Architecture

The final runtime model is:

```text
                         CLIENT
                           │
                           ▼
                         FastAPI
                           │
                           ▼
                    Application Service
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
          DB Transaction         Job Record
                 │                   │
                 ▼                   │
        Domain State Change          │
                 │                   │
                 ▼                   │
       Transactional Outbox          │
                 │                   │
                 └─────────┬─────────┘
                           ▼
                    Commit Transaction
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
       Outbox Publisher              Worker System
             │                           │
             ▼                           ▼
       Domain Events              Background Jobs
             │                           │
             ▼               ┌───────────┼───────────┐
       Event Handlers         ▼           ▼           ▼
             │              AI/RAG    GitHub      Email/Docs
             ▼
 Notifications / Activity /
 Derived State / Audit / Metrics
```

---

# 4. Synchronous vs Asynchronous Work

Not every operation needs a worker.

## Synchronous

Suitable for:

- authentication;
- authorization;
- simple reads;
- simple CRUD;
- small deterministic state changes;
- lightweight queries;
- simple notification reads.

## Asynchronous

Suitable for:

- blueprint generation;
- agent workflows;
- AI Mentor long responses where execution is substantial;
- document parsing;
- embeddings;
- RAG indexing;
- large file processing;
- GitHub synchronization;
- email delivery;
- complex notifications;
- long-running integrations;
- bulk/rebuild operations;
- maintenance/reconciliation.

The decision should be based on execution time, resource consumption, external dependencies and failure behavior.

---

# 5. Job vs Event

These concepts are deliberately separate.

## Job

A request to perform work.

Example:

```text
GenerateBlueprintJob
```

## Event

A statement that something happened.

Example:

```text
BlueprintGenerationCompleted
```

Relationship:

```text
Command
 ↓
Job
 ↓
Work
 ↓
State Change
 ↓
Event
```

A job is not automatically an event.

An event does not automatically imply another job.

---

# 6. Domain Events

A domain event represents a meaningful system occurrence.

Existing examples include:

```text
TaskCompleted
TaskBlocked
MilestoneCompleted
ProjectProgressChanged
ProjectPhaseChanged
ProjectHealthChanged
RiskCreated
RiskUpdated
RiskResolved
HelpRequestCreated
HelpRequestStarted
HelpRequestResolved
MentorNoteCreated
BlueprintGenerationStarted
BlueprintGenerationCompleted
BlueprintGenerationFailed
AgentExecutionStarted
AgentExecutionCompleted
GitHubActivityDetected
DocumentUploaded
DocumentIndexCompleted
DocumentIndexFailed
AccountStatusChanged
SecurityEventDetected
```

The final event catalogue can grow as implementation identifies additional meaningful events.

---

# 7. Event Contract

A canonical event contains:

```text
event_id
event_type
occurred_at
actor_id
actor_role
resource_type
resource_id
project_id
group_id
visibility
metadata
correlation_id
```

Optional fields may include:

```text
causation_id
event_version
```

These are useful when event chains become more complex.

---

# 8. Event IDs

Every event has a unique ID.

Purpose:

- deduplication;
- tracing;
- handler idempotency;
- debugging;
- audit correlation.

Events must not depend on array position or timestamp alone for identity.

---

# 9. Correlation IDs

Every request/execution chain receives a correlation ID.

Example:

```text
HTTP Request
   ↓ correlation_id = C123
Application Service
   ↓
Job
   ↓
Agent Execution
   ↓
Domain Event
   ↓
Notification
```

This allows the entire operation to be traced.

---

# 10. Causation IDs

Where useful:

```text
Event B
caused by
Event A
```

can be represented through a causation identifier.

Example:

```text
TaskCompleted
   ↓
ProjectProgressChanged
```

This makes event chains easier to understand.

---

# 11. Transactional Outbox

The outbox is the reliability mechanism for important internal events.

Correct pattern:

```text
BEGIN TRANSACTION
    Update domain state
    Insert domain event/outbox record
COMMIT
```

Then:

```text
Outbox Publisher
 ↓
Publish/process event
```

This prevents:

```text
Database commit ✓
Event lost ✗
```

---

# 12. Why Outbox Instead of Direct Publication

Avoid:

```text
DB commit
 ↓
send event
```

because the application can crash between the two operations.

Instead:

```text
DB state
+
outbox event
```

are committed atomically.

---

# 13. Outbox Storage

The existing `domain_events` architecture can support the event/outbox model.

The exact schema may include operational fields such as:

```text
published_at
attempt_count
last_error
next_attempt_at
status
```

These details belong to implementation.

---

# 14. Outbox Lifecycle

Conceptually:

```text
PENDING
 ↓
PUBLISHING
 ↓
PUBLISHED
```

Failure:

```text
PENDING
 ↓
FAILED
 ↓
RETRY
```

Permanent failure may move to:

```text
DEAD_LETTER
```

The exact status model can be implemented as fields rather than a large state machine if appropriate.

---

# 15. Outbox Publisher

A lightweight worker periodically reads unpublished events:

```text
domain_events
      ↓
unpublished events
      ↓
publisher
      ↓
event handlers / internal dispatch
```

The publisher should process events in bounded batches.

---

# 16. Event Ordering

Global ordering is not required.

Where ordering matters, preserve logical ordering within the relevant aggregate/resource.

Example:

```text
TaskStarted
 ↓
TaskCompleted
```

must not be processed as:

```text
TaskCompleted
 ↓
TaskStarted
```

Handlers should also be resilient to duplicate or delayed delivery.

---

# 17. At-Least-Once Delivery

The initial system should prefer:

> **At-least-once internal event delivery + idempotent handlers**

rather than attempting complex exactly-once distributed semantics.

This is simpler and more reliable for the modular monolith.

---

# 18. Idempotent Event Handlers

A handler may receive the same event twice.

Example:

```text
NotificationHandler(Event123)
NotificationHandler(Event123)
```

The second processing should not create duplicate effects.

A handler may use:

```text
event_id
handler_name
```

as a processing key.

---

# 19. Event Handler Failure

If one handler fails:

```text
TaskCompleted
 ├── Activity Handler ✓
 ├── Notification Handler ✗
 └── Analytics Handler ✓
```

the task completion remains valid.

The failed notification handler retries independently.

---

# 20. Event Handler Isolation

Handlers should avoid large shared transactions.

A handler generally performs:

```text
Event
 ↓
Handler
 ↓
Small deterministic operation
```

If another handler fails, it does not roll back the original domain event.

---

# 21. Notification Event Handling

Example:

```text
HelpRequestCreated
      ↓
Notification Handler
      ↓
Create mentor notification
      ↓
Optional email job
```

The Notification Service remains centralized.

---

# 22. Activity Event Handling

Domain events feed the canonical activity system.

Example:

```text
TaskCompleted
      ↓
Activity Projection
      ↓
Student Activity
Mentor Activity
Admin Activity
```

Different roles receive projections according to authorization.

---

# 23. Audit Event Handling

Security-sensitive events may also produce audit records.

Example:

```text
Admin Investigation Authorized
       ↓
Audit Event
```

Audit records are append-oriented.

---

# 24. Domain Event vs Audit Event

They are not identical.

**Domain event:**

> Something meaningful happened in the application.

**Audit event:**

> A security/governance-relevant action needs a durable audit record.

Some actions generate both.

---

# 25. Background Worker Architecture

The initial worker architecture is:

```text
FastAPI Application
       │
       ├── API processes
       │
       └── Worker process(es)
               │
               ├── AI jobs
               ├── RAG jobs
               ├── document jobs
               ├── GitHub jobs
               ├── email jobs
               └── maintenance jobs
```

Workers share the same application/domain modules.

---

# 26. Modular Monolith Worker Principle

Workers are not separate microservices.

They reuse:

- domain services;
- repositories;
- authorization components where required;
- settings;
- integration adapters;
- AI gateway;
- RAG service.

This prevents business logic duplication.

---

# 27. Worker Types

Logical worker categories:

```text
AI Worker
Document Worker
RAG Worker
Integration Worker
Notification Worker
Maintenance Worker
```

They may initially run in one worker process with controlled job routing.

Separate processes can be introduced later only if operationally justified.

---

# 28. Job Record

Long-running work must have persistent execution/job state.

Existing AI execution records handle AI workloads.

For generic background operations, a job model may contain:

```text
job_id
job_type
status
created_at
started_at
completed_at
attempt_count
max_attempts
correlation_id
resource_id
payload/reference
error_code
error_message
```

The exact generic job table is an implementation decision.

Do not introduce a generic job table if existing domain-specific execution tables already provide the required lifecycle.

---

# 29. Avoid Generic Job Overengineering

Not every asynchronous operation needs:

```text
UniversalJobFramework
```

Prefer existing execution models when appropriate.

Examples:

```text
ai_executions → AI
rag_index_jobs → RAG
```

A generic job abstraction should only cover truly shared operational behavior.

---

# 30. Job Lifecycle

Common lifecycle:

```text
QUEUED
 ↓
RUNNING
 ↓
COMPLETED
```

Failure:

```text
RUNNING
 ↓
FAILED
 ↓
RETRY
```

Other states:

```text
CANCELLED
RATE_LIMITED
QUOTA_EXHAUSTED
PROVIDER_UNAVAILABLE
```

AI already has specialized execution states defined in 6E/6F.

---

# 31. Job State Ownership

The component that owns the business operation owns its authoritative execution state.

Examples:

```text
AI → AI Execution Service
RAG → RAG Index Job
GitHub → GitHub Integration Job
```

Avoid duplicating the same status in multiple unrelated tables.

---

# 32. Job Creation

Correct:

```text
POST request
 ↓
Validate
 ↓
Authorize
 ↓
Create execution/job
 ↓
Commit
 ↓
Return 202
```

Worker begins afterward.

---

# 33. HTTP 202 Pattern

For long-running operations:

```http
POST /api/v1/...
```

returns:

```text
202 Accepted
```

with an execution identifier.

The client can then:

```text
GET status
```

or:

```text
SSE stream
```

---

# 34. Browser Disconnect

If the browser disconnects:

```text
Browser ✗
Server Job ✓
```

The execution continues unless explicitly cancelled.

This is mandatory for:

- blueprint generation;
- agent workflows;
- RAG indexing;
- long-running document processing.

---

# 35. SSE

Server-Sent Events provide live execution updates:

```text
Worker
 ↓
Execution Events
 ↓
SSE
 ↓
Browser
```

SSE does not own job state.

---

# 36. SSE Reconnection

The client may reconnect after disconnect.

The server should use persisted execution state/events to reconstruct the current state rather than assuming the browser remained connected.

---

# 37. SSE Event Types

Possible execution stream events:

```text
execution.started
agent.started
agent.completed
agent.failed
progress.updated
qa.started
qa.completed
execution.completed
execution.failed
execution.cancelled
```

The exact public SSE contract belongs to API implementation.

---

# 38. SSE and Outbox

Not every internal event must become an SSE event.

A dedicated execution-event stream can be persisted for AI execution where useful.

The existing:

```text
ai_execution_events
```

supports this purpose.

The system can transform internal execution state into SSE without exposing all internal domain events.

---

# 39. Cancellation

Long-running work should support cancellation where safe.

Flow:

```text
User
 ↓
Cancel Request
 ↓
Authorization
 ↓
Mark execution CANCEL_REQUESTED/CANCELLED
 ↓
Worker observes cancellation
 ↓
Stops at safe boundary
```

The exact state machine can avoid introducing an unnecessary extra state if implementation can reliably use `CANCELLED`.

---

# 40. Cancellation Safety

Cancellation must not leave:

- half-persisted blueprint state;
- invalid document versions;
- partial task state;
- corrupted RAG indexes.

Core persistence operations remain transactional.

---

# 41. AI Cancellation

AI execution cancellation should stop further model/tool work where possible.

If a provider call cannot be interrupted:

```text
current provider call finishes
 ↓
worker checks cancellation
 ↓
no additional work
```

---

# 42. Retry Policy

Retries must be:

- bounded;
- failure-aware;
- idempotent;
- delayed;
- observable.

Never retry every failure blindly.

---

# 43. Retry Categories

## Retryable

Examples:

- temporary network timeout;
- transient provider outage;
- temporary vector-store error;
- temporary object-storage error;
- temporary email provider error.

## Non-Retryable

Examples:

- invalid input;
- authorization failure;
- unsupported file;
- malformed content;
- permanent provider rejection;
- policy violation.

---

# 44. Exponential Backoff

A bounded exponential backoff can be used:

```text
attempt 1 → short delay
attempt 2 → longer delay
attempt 3 → longer delay
...
```

Jitter should be added to avoid synchronized retry storms.

Exact numerical values are configuration.

---

# 45. Maximum Attempts

Every retryable operation has a maximum attempt count.

After exhaustion:

```text
FAILED
```

or:

```text
DEAD_LETTER
```

depending on the job/event type.

No infinite retry loops.

---

# 46. Dead-Letter Handling

Dead-letter state identifies work that could not be completed automatically.

It should retain:

```text
job/event ID
failure reason
attempt count
last error
timestamps
correlation ID
```

It must not contain secrets.

---

# 47. Dead-Letter Operations

Admin/system operations may support:

```text
Inspect
Retry
Resolve
Ignore/Archive
```

according to the operational type.

Sensitive payloads remain governed by existing admin privacy controls.

---

# 48. Provider Rate Limits

AI provider rate limits are primarily managed by the AI Provider Gateway.

Worker behavior:

```text
Provider Rate Limited
 ↓
Gateway controls retry/cooldown
 ↓
Execution reflects RATE_LIMITED where appropriate
```

Workers should not independently rotate API keys.

---

# 49. AI Quota Exhaustion

If all five configured AI keys have exhausted usable capacity:

```text
Gateway
 ↓
QUOTA_EXHAUSTED
```

The AI execution stops further LLM attempts.

The worker does not:

- search for unauthorized credentials;
- invent another provider;
- retry forever.

Core platform functionality remains available.

---

# 50. RAG Retry

RAG indexing retries transient:

- parser infrastructure failures;
- embedding timeouts;
- vector-store transient failures;
- storage transient failures.

It does not endlessly retry invalid documents.

---

# 51. Document Retry

Document processing should preserve the uploaded version even if processing fails.

```text
Document ✓
Processing ✗
```

A retry operates against the same version unless content changes.

---

# 52. GitHub Job Retry

GitHub monitoring jobs may retry transient API/network errors.

Authentication failures require explicit reconnection/re-authentication rather than blind retry.

---

# 53. Email Retry

Email delivery is external and should be asynchronous.

```text
Notification Created
 ↓
Email Job
 ↓
Provider
```

Temporary provider failures retry.

Permanent delivery rejection becomes a controlled failure.

In-app notification remains authoritative.

---

# 54. Scheduled Jobs

Periodic maintenance can include:

- stale execution reconciliation;
- failed index detection;
- outbox retry;
- dead-letter monitoring;
- GitHub synchronization;
- cleanup;
- health checks.

Scheduling should use the chosen worker/job infrastructure rather than introducing a separate scheduling platform unnecessarily.

---

# 55. Scheduled Job Idempotency

A scheduled job may run twice.

Therefore:

```text
same logical time window
+
same resource
```

must not create duplicate effects.

---

# 56. Worker Concurrency

Concurrency must be bounded.

Separate limits may exist for:

```text
AI
RAG
documents
GitHub
email
maintenance
```

Exact limits depend on deployment capacity.

---

# 57. Resource Isolation

A large AI workload should not starve:

- authentication;
- normal API requests;
- notification processing;
- critical maintenance.

Worker pools/concurrency controls should preserve platform responsiveness.

---

# 58. AI Concurrency

AI concurrency must account for:

- provider rate limits;
- five-key pool capacity;
- model limits;
- token consumption;
- server resources.

The Provider Gateway remains the authority for provider access.

---

# 59. RAG Concurrency

RAG indexing should avoid overwhelming:

- CPU;
- memory;
- embedding provider;
- vector store;
- object storage.

Batch processing is preferred over uncontrolled parallelism.

---

# 60. Document Concurrency

Large PDF/code/document processing may be resource-heavy.

Worker limits prevent one project from consuming the entire processing capacity.

---

# 61. Fairness

Where useful, workloads can be bounded per project/user.

This is especially relevant for:

- large indexing operations;
- repeated AI generations;
- bulk uploads.

Exact quotas belong to configuration/product policy.

---

# 62. Stale AI Execution

A long-running AI execution may start from:

```text
Project version N
```

while the project changes to:

```text
Project version N+1
```

before completion.

The old execution must not blindly overwrite the new state.

---

# 63. Stale Execution Protection

Before persistence:

```text
Execution Context
        ↓
Compare expected project/version state
        ↓
Current state compatible?
     /        \
   YES         NO
    ↓           ↓
Persist      Mark stale/reconcile
```

---

# 64. Project Change During Blueprint Generation

Example:

```text
Blueprint generation started
 ↓
Student changes project scope
 ↓
Generation continues or is cancelled
 ↓
Completion detects changed project state
```

The system must prevent obsolete output from becoming the active blueprint without reconciliation.

---

# 65. Project Change Workflow

Existing canonical workflow remains:

```text
Impact Analysis
      ↓
Confirmation
      ↓
Regeneration
      ↓
QA
      ↓
Persistence
```

6H adds runtime protection around that workflow.

---

# 66. Version/Generation Identity

Long-running execution should retain enough context to identify:

```text
project_id
project state/version at start
blueprint version if applicable
assessment version/context
execution_id
correlation_id
```

This supports stale-result detection.

---

# 67. Valid State Preservation

If a new generation fails:

```text
Current valid blueprint
       ↓
Generation failure
       ↓
Current blueprint remains active
```

Never replace valid state with partial output.

---

# 68. Atomic Persistence

When validated AI output becomes authoritative:

```text
BEGIN TRANSACTION
    Persist structured result
    Update related state
    Create document version
    Create relevant events
COMMIT
```

The exact transaction boundary depends on the operation.

---

# 69. AI Does Not Own Transactions

AI/agents produce proposed/validated output.

They do not directly manage the canonical DB transaction.

Correct:

```text
AI
 ↓
Pydantic
 ↓
QA
 ↓
Domain Service
 ↓
Transaction
 ↓
PostgreSQL
```

---

# 70. RAG Transaction Boundaries

RAG indexing is derived data.

A typical document flow:

```text
Document Version
 ↓
Index Job
 ↓
Parse/Chunk/Embed
 ↓
Vector Index
 ↓
Mark RAG Ready
```

Canonical document version does not depend on vector indexing success.

---

# 71. Outbox + Transaction Boundary

For a task completion:

```text
BEGIN
    Task status = COMPLETED
    Update milestone/progress if required
    Create TaskCompleted event
COMMIT
```

Then:

```text
TaskCompleted
 ↓
Notifications
Activity
Analytics
```

---

# 72. Eventual Consistency

Derived systems may update shortly after canonical state.

Examples:

```text
Task completed
 ↓
Activity projection updates
 ↓
Notification appears
```

The canonical task state remains immediately authoritative.

---

# 73. User Experience of Eventual Consistency

UI should not pretend every derived view updates atomically.

SSE/activity refresh mechanisms can reduce visible delay.

But canonical API responses remain authoritative.

---

# 74. Failure Recovery After Restart

If the application/worker crashes:

```text
Queued jobs
Running jobs
Pending outbox events
```

must be recoverable.

Startup/recovery logic should identify abandoned work.

---

# 75. Abandoned Job Recovery

Example:

```text
Job = RUNNING
Worker crashes
```

After a timeout:

```text
RUNNING
 ↓
Detected abandoned
 ↓
Retry/requeue
```

Only jobs safe to retry should be requeued automatically.

---

# 76. Lease/Claim Model

Workers should claim jobs atomically.

Conceptually:

```text
QUEUED
 ↓
Worker claims
 ↓
RUNNING
```

Another worker should not process the same job simultaneously.

The exact database locking/claim mechanism belongs to implementation.

---

# 77. Worker Heartbeats

For sufficiently long jobs, workers may update:

```text
last_heartbeat_at
```

This helps distinguish:

```text
still running
```

from:

```text
abandoned
```

Do not add heartbeats to trivial jobs.

---

# 78. Graceful Shutdown

When a worker shuts down:

1. stop accepting new work;
2. finish safe in-flight work where possible;
3. release/reconcile claims;
4. preserve execution state;
5. exit cleanly.

Do not silently lose claimed jobs.

---

# 79. Deployment During Active Jobs

Deployments must not invalidate running work.

A rolling/restart-safe model should ensure:

```text
Worker A stops
 ↓
Job remains recoverable
 ↓
Worker B can resume/retry
```

Long-running AI work should use persisted state rather than process memory as the sole source of truth.

---

# 80. Worker Memory

Do not store essential execution state only in:

```text
Python process memory
```

Persist important state in PostgreSQL.

Memory may contain transient working context only.

---

# 81. Large Payloads

Do not put huge document contents or model outputs directly into:

- events;
- queue messages;
- logs.

Prefer:

```text
database record
+
object-storage reference
```

where appropriate.

---

# 82. Secret Handling

Never put these in jobs/events:

- API keys;
- OAuth client secrets;
- provider credentials;
- access tokens;
- passwords.

Workers obtain secrets through centralized typed configuration/secret management.

---

# 83. Job Payload Security

Prefer IDs/references:

```text
project_id
document_id
execution_id
```

rather than copying sensitive content into job payloads.

Workers load authorized data through application services.

---

# 84. Re-Authorization

Background work may outlive the original HTTP request.

Therefore, sensitive operations should revalidate relevant authorization/state before performing external or privileged actions.

Do not assume:

> "The user was authorized when the job was created, therefore it is always authorized."

---

# 85. Account Suspension During Job

If a user's account becomes suspended while sensitive work is queued:

```text
Queued Job
 ↓
Worker authorization/state check
 ↓
Suspended
 ↓
Cancel/stop according to job policy
```

This is especially relevant to user-triggered AI and integration operations.

---

# 86. Project Access Revocation

If a mentor loses access to a group/project while an operation is pending:

```text
Worker
 ↓
Authorization check
 ↓
Access revoked
 ↓
Do not continue privileged operation
```

---

# 87. Event Visibility

Events may have visibility metadata such as:

```text
STUDENT
MENTOR
ADMIN
SYSTEM
PRIVATE
```

Consumers must apply authorization before exposing event-derived information.

---

# 88. Event Data Minimization

Prefer:

```text
event_type
resource_id
project_id
actor_id
safe metadata
```

over embedding full private documents or conversations.

---

# 89. Event Versioning

Events may evolve.

Where an event contract is persisted or consumed asynchronously, include a version where useful.

Example:

```text
TaskCompleted v1
TaskCompleted v2
```

Handlers can migrate deliberately rather than guessing payload structure.

---

# 90. Backward Compatibility

When event schemas change:

- preserve required fields;
- version breaking changes;
- update handlers;
- test old/new payload behavior where necessary.

Do not silently change event semantics.

---

# 91. Event Processing Table

If required by implementation, maintain a lightweight handler-processing record:

```text
event_id
handler_name
processed_at
status
```

This supports idempotency.

Do not introduce it if an equivalent mechanism already exists.

---

# 92. Notification Reliability

Notifications should be created from canonical events.

Example:

```text
TaskBlocked
 ↓
Notification Service
 ↓
In-app notification
```

Email is secondary.

A failed email must not delete the in-app notification.

---

# 93. Activity Reliability

Activity should be derived from canonical events rather than every role implementing its own activity writes.

This preserves the one canonical activity/event architecture.

---

# 94. Health Calculation

Project health remains deterministic.

Events may trigger recalculation:

```text
TaskCompleted
 ↓
Progress recalculation
 ↓
Phase evaluation
 ↓
Health evaluation
```

AI does not directly set health.

---

# 95. At-Risk Calculation

At-risk signals can be recalculated after relevant events:

```text
Deadline approaching
Task delayed
Inactivity
Blocked task
Risk created
```

The ranking remains transparent/deterministic.

---

# 96. Event-Triggered Derived State

Appropriate derived operations include:

```text
TaskCompleted
 → progress update

MilestoneCompleted
 → phase evaluation

TaskBlocked
 → risk/at-risk evaluation

HelpRequestCreated
 → mentor notification
```

The exact mapping belongs to application/domain services.

---

# 97. Avoid Event Chains Becoming Loops

Example danger:

```text
Event A
 ↓
Handler
 ↓
Event B
 ↓
Handler
 ↓
Event A
```

Handlers should have explicit responsibilities and loop prevention.

Correlation/causation IDs help diagnose accidental cycles.

---

# 98. Event Handler Transaction Rules

A handler should:

1. validate event;
2. load necessary state;
3. enforce relevant invariants;
4. perform its small operation;
5. commit;
6. emit additional events only when meaningful.

Avoid huge multi-domain handler transactions.

---

# 99. Error Classification

Errors should map to machine-readable categories:

```text
VALIDATION_ERROR
AUTHORIZATION_ERROR
NOT_FOUND
CONFLICT
TRANSIENT_INTEGRATION_ERROR
RATE_LIMITED
QUOTA_EXHAUSTED
PARSER_ERROR
EMBEDDING_ERROR
VECTOR_STORE_ERROR
TIMEOUT
INTERNAL_ERROR
```

These integrate with existing exception/error architecture.

---

# 100. Observability

Every job/event chain should expose:

```text
correlation_id
execution_id/job_id
event_id where applicable
project_id
user_id where appropriate
job type
status
duration
attempt
error code
```

---

# 101. Metrics

Useful metrics include:

## Jobs

- queued count;
- running count;
- success rate;
- failure rate;
- retry count;
- execution duration;
- abandoned jobs.

## Events

- pending outbox count;
- publication latency;
- handler failures;
- retry count;
- dead-letter count.

## AI

- execution duration;
- model latency;
- provider failures;
- token usage;
- quota exhaustion;
- agent failures.

## RAG

- indexing latency;
- queue depth;
- failure rate;
- stale indexes.

---

# 102. Queue Depth

Queue depth is an important operational signal.

Example:

```text
AI queue = 500
RAG queue = 3
```

This may indicate AI capacity pressure rather than a platform-wide failure.

---

# 103. Backpressure

When capacity is exhausted:

```text
New workload
 ↓
Queue/bound
```

Do not allow unlimited in-memory accumulation.

The API should return an appropriate controlled response when configured capacity limits are reached.

---

# 104. Rate Limiting

Rate limiting exists at multiple layers:

```text
API rate limit
AI execution limit
Provider rate limit
Worker concurrency limit
```

They serve different purposes.

---

# 105. Health Checks

System health should distinguish:

```text
API
Database
Storage
AI Gateway
RAG/Vector
Workers
GitHub
OAuth
Email
```

A failure in one integration should not necessarily make the entire API unhealthy.

---

# 106. Readiness vs Liveness

Conceptually:

**Liveness**

> Is the process alive?

**Readiness**

> Can the process safely accept work?

A worker may be alive but temporarily unable to accept more jobs due to resource constraints.

---

# 107. Graceful Degradation

Examples:

```text
Email unavailable
→ In-app notifications still work

RAG unavailable
→ Structured project information can still work

GitHub unavailable
→ Project execution continues

AI provider unavailable
→ Deterministic platform functions continue
```

This is a core reliability objective.

---

# 108. AI Failure Isolation

AI failure must not break:

- authentication;
- project reads;
- task completion;
- milestone state;
- mentor notes;
- help requests;
- basic notifications.

AI is an enhancement layer, not the authoritative core.

---

# 109. RAG Failure Isolation

RAG failure must not break:

- document access;
- project state;
- task execution;
- normal project management.

Only knowledge retrieval becomes degraded.

---

# 110. GitHub Failure Isolation

GitHub outage must not prevent:

- project updates;
- task completion;
- mentor communication;
- normal project access.

GitHub-derived information may temporarily be stale.

---

# 111. Email Failure Isolation

Email is optional.

If email fails:

```text
In-app notification = remains
Email = failed/retry
```

---

# 112. Startup Reconciliation

After startup, the system may reconcile:

- stale running jobs;
- pending outbox events;
- stale RAG jobs;
- incomplete storage/index relationships;
- failed external operations.

This is maintenance/recovery logic, not a separate service.

---

# 113. Periodic Reconciliation

Periodic checks may identify:

```text
RUNNING job without heartbeat
Current document without current RAG index
Outbox event stuck pending
RAG chunk without active document
Storage object without metadata
```

The system can repair or flag these conditions.

---

# 114. Transactional Outbox Cleanup

Published events may eventually be archived/cleaned according to retention requirements.

Do not delete events immediately if operational debugging/audit requirements need them.

---

# 115. Event Retention

Retention should consider:

- debugging;
- analytics;
- audit requirements;
- storage cost;
- privacy.

Domain event retention is not automatically identical to audit retention.

---

# 116. Worker Logging

Workers should log structured events:

```text
job_started
job_retry
job_completed
job_failed
job_cancelled
```

Include identifiers, not sensitive payloads.

---

# 117. Error Logging

Log:

```text
error_code
exception type
correlation_id
job_id
execution_id
resource IDs
attempt
```

Avoid:

```text
API keys
tokens
passwords
OAuth secrets
full sensitive documents
```

---

# 118. Distributed Tracing

Full distributed tracing infrastructure is not necessary initially.

Correlation IDs + LangSmith + structured application logs provide the initial observability layer.

OpenTelemetry-style tracing can be added where useful without changing business architecture.

---

# 119. LangSmith Relationship

LangSmith observes:

```text
AI Execution
 ↓
LangGraph
 ↓
Agent
 ↓
Tool
 ↓
RAG
 ↓
Model
```

Application observability observes:

```text
API
 ↓
Job
 ↓
Database
 ↓
Worker
```

These complement each other.

---

# 120. AI Execution Trace

A useful relationship is:

```text
GrowFlow execution_id
        ↕
LangSmith trace/run IDs
```

This allows application operations to be connected to AI-level traces.

---

# 121. Worker Security

Workers have privileged access to internal services.

Therefore:

- workers run with least privilege;
- secrets are injected securely;
- worker endpoints are not publicly exposed unnecessarily;
- job payloads are validated;
- authorization is rechecked for sensitive work;
- logs avoid secrets.

---

# 122. Worker Isolation

A worker must not automatically receive:

```text
all database tables
all project data
all secrets
all provider credentials
```

It uses the repositories/services required for its job.

---

# 123. Database Connections

Workers should use controlled connection pools.

Long-running jobs must not hold database transactions open during:

```text
LLM calls
HTTP calls
file parsing
embedding generation
```

---

# 124. Long External Calls

Never do:

```text
BEGIN TRANSACTION
 ↓
LLM call for 2 minutes
 ↓
COMMIT
```

Prefer:

```text
Load state
 ↓
External work
 ↓
Revalidate state
 ↓
Short transaction
 ↓
Persist
```

---

# 125. Job Transaction Pattern

Preferred:

```text
1. Claim job
2. Load required state
3. Perform external/CPU-heavy work
4. Validate result
5. Re-check relevant state
6. Persist atomically
7. Emit events
8. Mark execution complete
```

---

# 126. Retry and External Side Effects

Retries can duplicate external actions.

Therefore, external operations should use idempotency mechanisms where supported.

Examples:

```text
Email send ID
External webhook ID
GitHub synchronization cursor
Document index version/hash
AI execution ID
```

---

# 127. GitHub Synchronization Cursor

GitHub monitoring should track enough state to avoid repeatedly processing the same activity.

Possible mechanisms:

```text
last_checked_at
last_event_id
cursor
content/activity hash
```

The exact strategy depends on GitHub API behavior.

---

# 128. RAG Index Cursor/Identity

RAG uses:

```text
document_version_id
content_hash
embedding/index configuration
```

as its synchronization identity.

---

# 129. Notification Idempotency

Notifications should have a deterministic uniqueness strategy where duplicate event delivery could otherwise create duplicate notifications.

Example conceptual key:

```text
event_id + recipient_id + notification_type
```

---

# 130. Activity Idempotency

Activity projection should similarly avoid duplicate activity entries from repeated event handling.

---

# 131. Health Recalculation Idempotency

Recalculating health should be deterministic:

```text
same canonical state
→ same result
```

Repeated execution should not produce divergent state.

---

# 132. Agent Regeneration Reliability

Agent regeneration remains bounded.

```text
QA Failure
 ↓
Targeted regeneration
 ↓
QA
```

If the retry/regeneration budget is exhausted:

```text
Execution FAILED
```

The previous valid output remains intact.

---

# 133. Provider Retry vs Agent Regeneration

These are different:

### Provider retry

Transient infrastructure/provider problem.

### Agent regeneration

AI output failed QA/business requirements.

### Workflow recovery

Worker/application failure.

They must not be conflated.

---

# 134. Recovery Hierarchy

```text
Provider failure
 → Provider Gateway retry

Agent output failure
 → QA-targeted regeneration

Worker/process failure
 → Job recovery/retry

Invalid business result
 → Execution failure; preserve valid state
```

---

# 135. Partial Workflow Recovery

LangGraph execution should persist enough execution state to determine where recovery is possible.

However, recovery must not replay unsafe side effects blindly.

---

# 136. Agent Checkpoints

Where supported/useful, workflow checkpoints can record:

```text
completed agent
agent output reference
workflow state
execution metadata
```

Large raw outputs should use appropriate storage rather than oversized event payloads.

---

# 137. Recovery After Agent Failure

Example:

```text
Idea ✓
Scope ✓
Technology ✓
Features ✗
```

The workflow can retry/regenerate the failed portion where safe.

It does not need to rerun every successful agent automatically.

---

# 138. QA Failure Recovery

Example:

```text
Features ✓
Specification ✓
Timeline ✓
QA ✗
```

QA identifies targeted failure.

Only affected agents should regenerate where dependency rules allow.

---

# 139. Blueprint Persistence Safety

Only after:

```text
structured output valid
+
QA pass
+
state compatibility
```

can the final blueprint become active.

---

# 140. Project Change + Worker Safety

If a project change is confirmed while another generation is running:

```text
Old execution
 ↓
detect conflict
 ↓
cancel/stale
 ↓
new generation
```

The old result cannot overwrite the new project plan.

---

# 141. Concurrency on Same Project

Potential conflict:

```text
Student completes Task A
+
AI project-change execution
```

Both operate against the same project.

The domain layer must enforce transaction/invariant rules.

AI workflows use version checks before final persistence.

---

# 142. Optimistic Concurrency

Where useful, use:

```text
version number
updated_at
generation version
```

to detect concurrent modification.

Do not introduce locking everywhere.

---

# 143. Pessimistic Locking

Use database locks only where the business invariant genuinely requires them.

Examples might include highly contended state transitions.

Avoid broad locks around AI/external operations.

---

# 144. No Long-Lived Locks

Never hold a database lock while waiting for:

- LLM response;
- Tavily;
- GitHub;
- email;
- storage;
- embedding provider.

---

# 145. Atomic State Transitions

Important transitions such as:

```text
Task → COMPLETED
Help Request → RESOLVED
Project Phase → TESTING
Project Health → AT_RISK
```

must be validated and persisted atomically according to their domain rules.

---

# 146. Event Emission After State Transition

Events represent successful state changes.

Do not emit:

```text
TaskCompleted
```

before the transaction actually commits.

The outbox solves this.

---

# 147. Failed Transaction

If:

```text
Task update ✗
```

then:

```text
TaskCompleted event
```

must not be published.

Atomic DB + outbox transaction ensures this.

---

# 148. Worker Retry After Commit

If state committed successfully but worker crashes before marking the job complete:

```text
State ✓
Job status stale
```

The operation must be idempotent so retry does not corrupt state.

---

# 149. Exactly-Once Illusion Avoidance

Do not rely on:

> "This job will only ever execute once."

Assume duplicate delivery/execution can occur and design safe operations.

---

# 150. Operational Admin Visibility

Admin should be able to observe appropriate operational metadata:

- running jobs;
- failed jobs;
- queue pressure;
- event failures;
- AI execution state;
- RAG indexing state;
- integration failures;
- system health.

This belongs to the already defined Admin architecture.

---

# 151. Admin Actions

Operational actions may include controlled:

```text
Retry failed job
Inspect failure metadata
Re-index document
Reconcile stale execution
```

These actions must be authorized and audited where required.

Admin still cannot:

- impersonate users;
- arbitrarily mutate project progress;
- bypass authorization;
- access private content by default.

---

# 152. Operational Alerts

Useful alerts include:

```text
Outbox backlog high
Worker unavailable
Dead-letter count increasing
AI provider unavailable
AI quota exhausted
RAG queue stalled
RAG failures increasing
Storage failure
Database health issue
GitHub integration failing
```

Exact thresholds are operational configuration.

---

# 153. Deployment Topology

Initial deployment can be:

```text
                Load Balancer / Platform
                         │
                ┌────────┴────────┐
                ▼                 ▼
             FastAPI            Worker
                │                 │
                └────────┬────────┘
                         ▼
                    PostgreSQL
                         │
               ┌─────────┼─────────┐
               ▼         ▼         ▼
           Storage     Vector    External
                       Store     Integrations
```

FastAPI and worker processes use the same modular-monolith codebase.

---

# 154. Scaling Path

If workload increases:

```text
One Worker
    ↓
Multiple Worker Processes
    ↓
Specialized Worker Pools
```

without immediately becoming:

```text
Microservices
Kafka
Kubernetes
Service Mesh
```

Scaling follows measured bottlenecks.

---

# 155. Worker Specialization Threshold

Specialization is justified when:

- AI workloads starve other jobs;
- RAG has distinct resource requirements;
- document parsing requires isolation;
- GitHub workloads need different concurrency;
- deployment cost/latency requires independent scaling.

Until then, keep the worker architecture simple.

---

# 156. Queue Technology

The exact queue/job technology is intentionally left as an implementation decision.

It must satisfy:

- durable job state;
- retries;
- delayed execution;
- concurrency controls;
- worker claiming;
- recovery.

Do not select a distributed message platform merely because it is popular.

---

# 157. Database-Backed Work

Because GrowFlow already uses PostgreSQL, a database-backed job/outbox approach can be appropriate for initial scale.

This keeps:

```text
transaction
+
outbox
+
job state
```

close to the canonical data.

A dedicated queue can be added later if measurable load requires it.

---

# 158. Outbox Does Not Equal Event Sourcing

GrowFlow does not reconstruct application state from events.

Instead:

```text
PostgreSQL state = authority
Events = reliable notifications of changes
```

This distinction remains permanent.

---

# 159. No Kafka Initially

Kafka is explicitly excluded from the initial architecture.

Reasons:

- unnecessary operational complexity;
- low initial platform scale;
- modular monolith;
- PostgreSQL already authoritative;
- outbox provides required reliability.

Reconsider only if measured event throughput/retention/streaming requirements justify it.

---

# 160. No RabbitMQ Initially

A dedicated broker is not mandatory for V1.

If the selected worker implementation later requires one, that becomes a technology decision justified by actual requirements.

---

# 161. No Kubernetes Initially

Workers do not require Kubernetes.

Deployment remains platform-appropriate and simple.

---

# 162. No Microservices Initially

The architecture remains:

```text
Modular Monolith
+
Worker Processes
```

not:

```text
12 Agents = 12 Services
```

or:

```text
RAG Service = separate microservice
```

---

# 163. Agent Architecture Boundary

The 12 agents remain logical components within the AI architecture.

They are not deployed independently.

```text
LangGraph
 ↓
Agent Nodes
```

not:

```text
Agent Microservices
```

---

# 164. Event-Driven Agent Operations

Agent execution can emit events:

```text
AgentExecutionStarted
AgentExecutionCompleted
AgentExecutionFailed
```

These support observability and UI streaming.

They do not make agents independent services.

---

# 165. RAG Event-Driven Operations

Document upload can trigger:

```text
DocumentUploaded
 ↓
RAG Index Job
```

This is an appropriate asynchronous event-driven flow.

---

# 166. Blueprint Event-Driven Operations

Blueprint generation:

```text
BlueprintGenerationRequested
 ↓
AI Execution Job
 ↓
Agent Workflow
 ↓
QA
 ↓
BlueprintGenerationCompleted
```

The request itself remains an application command.

---

# 167. Project Lifecycle Events

Canonical lifecycle transitions may emit:

```text
ProjectPhaseChanged
ProjectHealthChanged
ProjectCompleted
```

Derived services can respond.

The lifecycle state remains owned by the domain.

---

# 168. Notification Pipeline

```text
Domain Event
 ↓
Notification Handler
 ↓
Notification Service
 ↓
In-App Notification
 ↓
Optional Email Job
```

Email does not block the domain transaction.

---

# 169. Activity Pipeline

```text
Domain Event
 ↓
Activity Projection
 ↓
Role-specific view
```

Student, Mentor and Admin views use the same canonical source with authorization-aware projections.

---

# 170. Analytics Pipeline

Appropriate operational/product analytics can consume events.

Analytics must not become authoritative for core project state.

---

# 171. Security Events

Security-sensitive events may include:

```text
UnauthorizedAccessAttempt
AccountSuspended
AdminInvestigationCreated
AdminInvestigationAuthorized
SensitiveInspectionPerformed
OAuthFailure
RateLimitTriggered
```

The exact event set belongs to implementation.

---

# 172. Security Event Handling

Security events can feed:

- audit;
- alerts;
- security dashboards;
- operational analysis.

Do not expose sensitive security details to ordinary users.

---

# 173. Error Propagation to User

Users should see meaningful states:

```text
Processing
Completed
Failed
Retrying
Cancelled
```

They should not receive raw stack traces/provider internals.

---

# 174. Error Codes

Existing centralized error handling remains authoritative.

Examples:

```text
AI_QUOTA_EXHAUSTED
AI_PROVIDER_UNAVAILABLE
RAG_INDEX_FAILED
DOCUMENT_PARSE_FAILED
JOB_CANCELLED
STALE_EXECUTION
INTEGRATION_TIMEOUT
```

---

# 175. Recovery UI

For relevant failures, UI can provide:

```text
Retry
View details
Contact mentor
Try again later
```

depending on the operation.

The UI should not expose infrastructure internals unnecessarily.

---

# 176. Job Progress

Long-running jobs may expose meaningful progress:

```text
0–100%
```

or stage-based progress:

```text
Parsing
Embedding
Indexing
```

Progress should not be fabricated.

If exact percentage is unavailable, use stage/status.

---

# 177. AI Progress

AI workflows can report:

```text
Starting
Planning
Agents executing
QA
Regeneration
Finalizing
```

This is preferable to fake percentage completion.

---

# 178. RAG Progress

RAG can report:

```text
Uploading
Parsing
Chunking
Embedding
Indexing
Ready
```

---

# 179. Document Progress

Large document processing can expose stage state without pretending to know exact completion percentage.

---

# 180. Worker Backpressure UX

If system capacity is temporarily constrained:

```text
Execution queued
```

is preferable to failing immediately when safe.

If limits are hard:

```text
Capacity temporarily unavailable
```

with retry guidance.

---

# 181. Job Priorities

Priority may be introduced for operational needs.

Potential priority classes:

```text
CRITICAL
NORMAL
LOW
```

Use sparingly.

Student-facing AI should not starve system-critical maintenance.

---

# 182. Avoid Priority Complexity

V1 does not require a complex scheduler.

Start with simple FIFO/queue behavior plus bounded worker pools unless real requirements demand priority scheduling.

---

# 183. Timeouts

Different operations have different timeouts:

```text
HTTP request
database operation
provider call
parser
embedding
job
```

A job timeout should not automatically equal every underlying timeout.

---

# 184. Timeout Recovery

On timeout:

```text
Classify
 ↓
Retry if transient/idempotent
 ↓
Otherwise fail
```

Do not automatically retry operations with unknown external side effects.

---

# 185. External Integration Boundary

All external operations remain behind adapters:

```text
OpenRouterGateway
TavilyAdapter
GitHubAdapter
EmailAdapter
StorageAdapter
VectorStoreAdapter
EmbeddingAdapter
```

Workers call application services/adapters, not provider-specific code scattered throughout jobs.

---

# 186. Worker Dependency Direction

Correct:

```text
Worker
 ↓
Application Service
 ↓
Domain
 ↓
Repository / Adapter
```

Avoid:

```text
Worker
 ↓
raw SQL
 ↓
external API
 ↓
business logic
```

---

# 187. Worker Single Responsibility

A worker handler should coordinate a job.

It should not become a giant class containing:

- database logic;
- AI prompts;
- GitHub logic;
- document parsing;
- notification formatting.

Those remain separate components.

---

# 188. Worker Configuration

Typed settings control:

- worker concurrency;
- retry limits;
- timeouts;
- polling intervals;
- batch sizes;
- provider configuration;
- storage;
- RAG;
- email.

No direct `.env` reads in workers.

---

# 189. Graceful Failure During Startup

If an optional external integration is unavailable:

```text
Application starts
Integration marked degraded
```

unless that dependency is genuinely required for safe startup.

---

# 190. Critical Startup Dependencies

Potentially critical:

```text
PostgreSQL
configuration/secrets
authentication infrastructure
```

Optional/degraded:

```text
email
GitHub
Tavily
AI provider
RAG vector infrastructure
```

Exact readiness policy belongs to deployment.

---

# 191. Testing — Unit

Test:

- event creation;
- event contracts;
- handlers;
- retry classification;
- idempotency;
- state transitions;
- stale execution checks;
- cancellation;
- concurrency logic.

---

# 192. Testing — Integration

Test:

- DB transaction + outbox;
- worker claim;
- retry;
- event handling;
- RAG job processing;
- AI execution persistence;
- storage integration;
- external adapters.

---

# 193. Testing — API

Test:

- 202 execution responses;
- status endpoints;
- cancellation;
- authorization;
- SSE connection;
- reconnection;
- error contracts.

---

# 194. Testing — E2E

Critical scenarios:

```text
Create Project
 ↓
Generate Blueprint
 ↓
Worker executes
 ↓
SSE updates
 ↓
QA
 ↓
Persistence
 ↓
Notification
```

and:

```text
Upload Document
 ↓
RAG Index Job
 ↓
Ready
 ↓
AI Mentor Retrieval
```

---

# 195. Failure Injection Tests

Simulate:

- worker crash;
- DB timeout;
- provider timeout;
- provider quota exhaustion;
- RAG failure;
- object-storage failure;
- duplicate event;
- duplicate job;
- stale project version;
- browser disconnect.

Expected recovery must be deterministic.

---

# 196. Duplicate Event Test

Send:

```text
TaskCompleted(event_id=123)
```

twice.

Expected:

```text
One effective notification
One activity effect
No duplicate state corruption
```

---

# 197. Worker Crash Test

```text
Job RUNNING
 ↓
Worker killed
 ↓
Recovery process
 ↓
Job retried/reconciled
```

No silent permanent loss.

---

# 198. Stale Execution Test

```text
Execution starts at version 5
Project changes to version 6
Execution completes
```

Expected:

```text
Execution cannot overwrite incompatible version 6 state.
```

---

# 199. Quota Exhaustion Test

All five AI keys become unusable.

Expected:

```text
No further unauthorized calls
Execution = QUOTA_EXHAUSTED
Clear user-facing failure
Core platform continues
```

---

# 200. RAG Failure Test

Vector/index infrastructure unavailable.

Expected:

```text
Documents remain available
Project state remains available
RAG request fails/degrades clearly
No fabricated answer
```

---

# 201. Event Ordering Test

Test relevant aggregate sequences:

```text
TaskStarted
TaskCompleted
```

and ensure handlers tolerate duplicate/delayed delivery.

---

# 202. Security Tests

Verify:

- unauthorized job creation;
- unauthorized cancellation;
- unauthorized event access;
- cross-project job execution;
- account suspension;
- revoked group access;
- secret leakage in logs;
- secret leakage in event payloads.

---

# 203. Load Testing

Measure:

- API responsiveness while workers are busy;
- AI queue behavior;
- RAG indexing throughput;
- event backlog;
- worker recovery;
- database connection usage.

Architecture decisions should be revisited only from measured evidence.

---

# 204. Operational Runbook

The project should eventually document procedures for:

```text
Worker outage
Outbox backlog
Dead-letter recovery
AI provider outage
AI quota exhaustion
RAG indexing backlog
Storage outage
GitHub outage
Database degradation
```

These are implementation/deployment operational artifacts, not new application architecture.

---

# 205. Backup and Recovery

Canonical recovery priority:

```text
PostgreSQL
 ↓
Object Storage
 ↓
Derived RAG index rebuild
```

The vector index is rebuildable.

The database and document content are therefore higher-priority backup targets.

---

# 206. RPO/RTO

Exact:

```text
RPO
RTO
```

are deployment decisions.

The architecture supports recovery without requiring the vector index to be treated as the primary data source.

---

# 207. Disaster Recovery Principle

If derived systems are lost:

```text
Rebuild derived systems
```

rather than attempting to reconstruct canonical project state from AI/RAG traces.

---

# 208. No Event Sourcing

GrowFlow does not reconstruct current state from domain events.

Canonical state remains:

```text
PostgreSQL
```

Events provide:

```text
reliable propagation
+
activity
+
notifications
+
integration triggers
+
observability
```

---

# 209. No Distributed Transactions

Avoid transactions spanning:

```text
PostgreSQL + OpenRouter
PostgreSQL + GitHub
PostgreSQL + email
PostgreSQL + vector store
```

Use:

```text
short DB transaction
+
durable job/event
+
idempotent external operation
```

---

# 210. Saga-Like Workflows

Complex workflows can use application-level compensation/recovery where necessary.

Do not introduce a heavyweight distributed saga framework unless the system actually develops multi-step cross-system transactional requirements.

---

# 211. Example — Blueprint Generation

Complete runtime:

```text
Student
 ↓
POST Generate Blueprint
 ↓
Authorization
 ↓
Create AI Execution = QUEUED
 ↓
Create relevant event/outbox record
 ↓
202 Accepted
 ↓
Worker claims execution
 ↓
LangGraph
 ↓
12 Agents
 ↓
Pydantic Validation
 ↓
QA/Judge
 ↓
State/version check
 ↓
Domain Service
 ↓
PostgreSQL transaction
 ↓
Document versions
 ↓
Events
 ↓
Execution = COMPLETED
 ↓
SSE
 ↓
Student UI
```

---

# 212. Example — Document Upload

```text
Student
 ↓
Upload
 ↓
Authorization
 ↓
Store file
 ↓
Document Version
 ↓
RAG Index Job = QUEUED
 ↓
202/processing status
 ↓
Worker
 ↓
Parse
 ↓
Chunk
 ↓
Embed
 ↓
LlamaIndex
 ↓
Vector Store
 ↓
RAG READY
 ↓
DocumentIndexCompleted
 ↓
Notification/activity if applicable
```

---

# 213. Example — Task Completion

```text
Student
 ↓
Complete Task
 ↓
Authorization
 ↓
Task Domain Service
 ↓
Transaction
    Task = COMPLETED
    Progress recalculation
    Milestone evaluation
    Domain event/outbox
COMMIT
 ↓
Event Handler
 ├── Activity
 ├── Notification if applicable
 ├── At-risk evaluation
 └── Analytics
```

---

# 214. Example — Help Request

```text
Student
 ↓
Create Help Request
 ↓
Transaction
 ↓
HelpRequestCreated
 ↓
Notification Service
 ↓
Mentor In-App Notification
 ↓
Optional Email Job
```

---

# 215. Example — GitHub Monitoring

```text
Scheduled GitHub Job
 ↓
GitHub Adapter
 ↓
Fetch monitoring data
 ↓
Deduplicate/synchronize
 ↓
Persist activity
 ↓
GitHubActivityDetected
 ↓
Activity/At-Risk/AI context
```

GitHub remains monitoring-only.

---

# 216. Example — Project Change

```text
Change Request
 ↓
AI/analysis job
 ↓
Impact analysis
 ↓
Await confirmation
 ↓
Confirmation
 ↓
Regeneration job
 ↓
QA
 ↓
Version check
 ↓
Persist
 ↓
Events
```

---

# 217. Complete Runtime Architecture

```text
                           CLIENT
                              │
                              ▼
                           FASTAPI
                              │
                              ▼
                    AUTH + AUTHORIZATION
                              │
                              ▼
                     APPLICATION SERVICE
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
       Synchronous        Job Creation      Domain State
             │                │                │
             │                ▼                ▼
             │          Execution State    PostgreSQL
             │                │                │
             │                │          Transactional
             │                │             Outbox
             │                │                │
             └────────────────┼────────────────┘
                              │
                              ▼
                          COMMIT
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
             WORKERS                    OUTBOX
                │                           │
      ┌─────────┼─────────┐                 ▼
      ▼         ▼         ▼            EVENT HANDLERS
      AI       RAG     Integrations         │
      │         │         │                 ├── Notifications
      │         │         │                 ├── Activity
      │         │         │                 ├── Audit
      │         │         │                 ├── Analytics
      │         │         │                 └── Derived State
      │         │         │
      ▼         ▼         ▼
 LangGraph  LlamaIndex  Adapters
      │         │         │
      ▼         ▼         ▼
 Provider   Vector      External
 Gateway    Store       Providers
      │
      ▼
    Models

                   SSE
                    ▲
                    │
             Persisted Execution
                    │
                 Workers
```

---

# 218. Responsibility Matrix

| Component | Primary Responsibility |
|---|---|
| FastAPI | HTTP transport |
| Application Services | Use-case orchestration |
| Domain Services | Business rules/state transitions |
| PostgreSQL | Canonical state |
| Transactional Outbox | Reliable event persistence |
| Event Publisher | Event dispatch |
| Event Handlers | Derived reactions |
| Workers | Asynchronous execution |
| AI Execution Service | AI workflow state |
| LangGraph | Agent orchestration |
| LlamaIndex | Knowledge/RAG workflow |
| RAG Service | Retrieval abstraction |
| Provider Gateway | AI provider access |
| Integration Adapters | External systems |
| Notification Service | Notifications |
| Activity Projection | Role-based activity |
| Audit Service | Security/governance audit |
| SSE | Live client delivery |
| LangSmith | AI tracing/evaluation |

---

# 219. Non-Negotiable Reliability Rules

1. Canonical state lives in PostgreSQL.
2. Important domain events use transactional persistence.
3. Outbox prevents state/event inconsistency.
4. Events are at-least-once.
5. Handlers are idempotent.
6. Jobs are persisted.
7. Long-running work survives browser disconnect.
8. SSE never owns execution state.
9. Retries are bounded.
10. Backoff uses jitter where appropriate.
11. Permanent failures do not retry forever.
12. Dead-letter handling exists for unrecoverable asynchronous work.
13. External side effects are idempotent where possible.
14. Secrets never enter job/event payloads.
15. Workers use centralized configuration.
16. Workers do not contain duplicated business logic.
17. AI never directly mutates authoritative state.
18. RAG is derived.
19. Stale AI executions cannot overwrite newer project state.
20. Long external calls never hold DB transactions open.
21. Authorization is revalidated for sensitive background work.
22. Worker concurrency is bounded.
23. AI/RAG/GitHub/email failures are isolated.
24. Core platform remains functional during optional integration failures.
25. No global exactly-once guarantee is assumed.
26. No event sourcing.
27. No distributed transactions.
28. No Kafka initially.
29. No RabbitMQ initially.
30. No Kubernetes initially.
31. No microservices initially.
32. Recovery is based on persisted state.
33. Derived indexes can be rebuilt.
34. Operational behavior is observable.
35. Failure must preserve the last valid state.

---

# 220. Explicit Non-Goals

6H does **not** introduce:

- Kafka;
- RabbitMQ;
- NATS;
- Kubernetes;
- service mesh;
- microservices;
- event sourcing;
- distributed transactions;
- complex workflow platform;
- heavyweight saga framework;
- autonomous infrastructure management;
- unrestricted event payloads;
- infinite retries;
- exactly-once distributed semantics;
- separate agent services;
- separate RAG microservice;
- direct AI database access;
- direct worker raw SQL scattered throughout handlers.

---

# 221. Implementation Boundary

The architecture is frozen, but these implementation values remain open:

- exact worker/queue library;
- exact database job-claim mechanism;
- exact worker process topology;
- exact polling interval;
- exact retry counts;
- exact exponential-backoff values;
- exact timeout values;
- exact dead-letter retention;
- exact concurrency limits;
- exact job priority behavior;
- exact heartbeat interval;
- exact stale-job timeout;
- exact event-processing table implementation;
- exact outbox cleanup policy;
- exact scheduling implementation;
- exact SSE event schema;
- exact deployment platform;
- exact monitoring/alerting provider.

These should be selected during implementation based on actual project requirements and measured behavior.

---

# 222. Relationship to Previous Architecture Parts

## 6A — Backend

6H runs through the existing:

```text
API → Application → Domain → Data Access → Infrastructure
```

architecture.

## 6B — Database

6H relies on PostgreSQL transactions, domain events, execution records and job metadata.

## 6C — API

6H implements the:

```text
POST → 202 → execution status/SSE
```

pattern.

## 6D — Security

6H inherits:

```text
Authentication
→ Authorization
→ Resource Scope
→ Action Permission
```

and revalidates where required.

## 6E — AI Provider Gateway

6H executes AI work through the gateway and respects:

```text
retry
rate limit
cooldown
quota exhaustion
five-key pool
```

rules.

## 6F — Agents

6H provides the worker/runtime environment for:

```text
LangGraph
12 agents
QA
regeneration
recovery
```

## 6G — RAG

6H executes:

```text
document processing
embedding
indexing
re-indexing
maintenance
```

as background work.

---

# 223. Final Runtime Principle

GrowFlow's runtime architecture can be summarized as:

> **HTTP requests initiate bounded application operations. Canonical state changes occur transactionally in PostgreSQL. Important events are persisted through the transactional outbox. Background workers perform long-running work. Events trigger independent derived reactions. Retries are bounded and idempotent. AI/RAG/integration workloads remain isolated from the core platform. Persisted execution state survives browser/process failure. Stale work cannot overwrite newer project state.**

---

# 224. Part 6H Freeze Statement

**Part 6H — Event-Driven Runtime, Background Jobs & Reliability Architecture is architecturally FROZEN.**

GrowFlow now has a complete runtime model for:

- domain events;
- event contracts;
- transactional outbox;
- event publishing;
- event handlers;
- at-least-once delivery;
- handler idempotency;
- background workers;
- asynchronous jobs;
- AI execution;
- RAG indexing;
- document processing;
- GitHub monitoring;
- email delivery;
- retries;
- exponential backoff;
- dead-letter handling;
- cancellation;
- SSE;
- browser disconnect recovery;
- worker crash recovery;
- stale execution protection;
- concurrency;
- optimistic concurrency;
- transaction boundaries;
- external side-effect safety;
- authorization revalidation;
- graceful shutdown;
- startup reconciliation;
- observability;
- operational Admin visibility;
- testing/failure injection;
- disaster/rebuild principles.

The final runtime boundary is:

```text
PostgreSQL = Canonical State
Outbox = Reliable Event Persistence
Events = Propagation
Workers = Asynchronous Execution
Domain Services = State Authority
AI/RAG/Integrations = Controlled Workloads
SSE = Live Delivery
LangSmith = AI Observability
```

**6H is ready for the next architecture phase.**
