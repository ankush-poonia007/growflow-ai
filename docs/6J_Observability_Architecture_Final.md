# GrowFlow — Phase 6J
# Observability, Monitoring, Logging & AI Evaluation Architecture
## Final Specification

**Status:** Architecturally FROZEN  
**Phase:** Phase 6 — Infrastructure & Runtime Architecture  
**Subphase:** 6J — Observability  
**Project:** GrowFlow  
**Architecture Style:** Modular Monolith + Async Workers + AI Orchestration  
**Primary Backend:** FastAPI  
**Primary Database:** PostgreSQL / Supabase  
**AI Orchestration:** LangGraph  
**RAG:** LlamaIndex + PostgreSQL/pgvector  
**AI Tracing/Evaluation:** LangSmith-compatible architecture  
**Event Runtime:** Transactional Outbox + Background Workers + Domain Events

---

# 1. Purpose

This document defines the complete observability architecture for GrowFlow.

Observability exists to make the platform understandable in production without turning observability into a second application.

The system must provide enough visibility to answer:

- Is GrowFlow healthy?
- Which subsystem is failing?
- Which request caused the failure?
- Which background job or event caused it?
- Which AI execution produced a bad result?
- Which agent failed?
- Which provider/key/model was involved?
- How long did the operation take?
- How much AI usage/cost was consumed?
- Are RAG retrievals functioning correctly?
- Are GitHub/Tavily/email integrations degrading?
- Are users experiencing failures even when infrastructure appears healthy?
- Are AI outputs passing quality gates?
- Can an administrator investigate safely without unrestricted access to private content?

Observability is therefore treated as a cross-cutting platform capability spanning:

```text
Application
    ↓
API
    ↓
Domain Services
    ↓
Events / Workers
    ↓
AI / Agents / RAG
    ↓
External Integrations
    ↓
Database / Storage
```

The architecture prioritizes:

1. structured telemetry,
2. correlation,
3. actionable alerts,
4. AI-specific tracing,
5. privacy-aware logging,
6. measurable quality,
7. low operational complexity.

---

# 2. Architectural Principles

## 2.1 Observability is cross-cutting

Observability must not be implemented independently inside every module.

Shared infrastructure should provide:

- structured logging,
- request correlation,
- trace propagation,
- metrics,
- error classification,
- audit integration,
- AI execution telemetry,
- job telemetry,
- integration telemetry.

Individual modules emit domain-specific information through these shared mechanisms.

---

## 2.2 Structured telemetry over ad-hoc logging

Production code must not depend on arbitrary `print()` statements or inconsistent text logs.

Preferred model:

```text
Application Event
        ↓
Structured Telemetry
        ↓
Log / Metric / Trace / Audit
```

Every important event should have machine-readable fields.

---

## 2.3 Correlation is mandatory

A failure must be traceable across layers.

Example:

```text
HTTP Request
    ↓
request_id
    ↓
application operation
    ↓
AI execution
    ↓
LangGraph run
    ↓
agent execution
    ↓
provider request
    ↓
worker/job
    ↓
database persistence
```

The same correlation context must survive asynchronous boundaries.

---

## 2.4 Observability must not become a privacy leak

Logs are not a dumping ground for:

- passwords,
- access tokens,
- refresh tokens,
- OAuth secrets,
- API keys,
- private document contents,
- full assessment answers,
- arbitrary RAG chunks,
- unrestricted project source code,
- private GitHub data,
- sensitive user content.

Telemetry should use metadata and identifiers wherever possible.

---

## 2.5 AI observability is first-class

GrowFlow is an AI-heavy platform.

Normal application telemetry alone is insufficient.

AI observability must cover:

- AI execution,
- agent execution,
- model/provider selection,
- token usage,
- latency,
- retries,
- failures,
- structured-output validation,
- QA results,
- regeneration,
- tool calls,
- RAG retrieval,
- evidence provenance,
- AI quality signals,
- cost.

---

# 3. Observability Domains

GrowFlow observability is divided into:

```text
1. Application Observability
2. API Observability
3. Database Observability
4. Worker / Job Observability
5. Event Observability
6. AI Provider Observability
7. Agent Observability
8. RAG Observability
9. Integration Observability
10. Storage Observability
11. Security Observability
12. Audit Observability
13. User Experience / Reliability Observability
14. AI Quality Evaluation
15. Platform / Infrastructure Health
```

These domains share common correlation and telemetry conventions.

---

# 4. Telemetry Model

GrowFlow uses three primary observability signals:

```text
Logs
Metrics
Traces
```

with two related governance signals:

```text
Audit Events
AI Evaluation Results
```

They serve different purposes.

| Signal | Primary purpose |
|---|---|
| Logs | Detailed event/error context |
| Metrics | Trends, rates, saturation, health |
| Traces | End-to-end causality and latency |
| Audit Events | Security/governance history |
| AI Evaluation | Output quality and AI behavior |

No single signal replaces the others.

---

# 5. Correlation Architecture

## 5.1 Required identifiers

Where applicable, telemetry should support:

- `request_id`
- `correlation_id`
- `trace_id`
- `span_id`
- `user_id`
- `role`
- `group_id`
- `project_instance_id`
- `project_definition_id`
- `execution_id`
- `agent_execution_id`
- `job_id`
- `event_id`
- `document_id`
- `document_version_id`
- `rag_job_id`
- `integration_sync_id`

Not every identifier belongs in every log.

Only identifiers relevant to the operation should be emitted.

---

## 5.2 Request correlation

Each inbound request receives or propagates a correlation identifier.

Example:

```text
HTTP Request
request_id = req_123

        ↓

Application Service
correlation_id = corr_456

        ↓

AI Execution
execution_id = ai_789

        ↓

Agent
agent_execution_id = agent_101

        ↓

Worker
job_id = job_202
```

Correlation identifiers must be propagated into background work.

---

## 5.3 Trace propagation

Where tracing is supported, spans should represent major execution boundaries:

```text
HTTP
 ├── Authentication
 ├── Authorization
 ├── Application Service
 │    ├── Repository
 │    └── Domain Operation
 ├── AI Execution
 │    ├── Agent
 │    ├── Tool
 │    ├── RAG
 │    └── Provider
 └── Persistence
```

Asynchronous workers should create linked traces rather than losing the originating correlation context.

---

# 6. Structured Logging

## 6.1 Logging standard

All application logs should be structured.

Recommended conceptual format:

```json
{
  "timestamp": "...",
  "level": "INFO",
  "service": "growflow-api",
  "module": "blueprint",
  "event": "blueprint_generation_started",
  "request_id": "...",
  "correlation_id": "...",
  "project_instance_id": "...",
  "execution_id": "...",
  "message": "Blueprint generation started"
}
```

Exact logging library may be selected during implementation.

---

## 6.2 Log levels

### DEBUG

Development and targeted troubleshooting.

Must not normally be enabled at high production volume.

### INFO

Normal meaningful lifecycle events.

Examples:

- request completed,
- job started,
- job completed,
- AI execution started,
- AI execution completed,
- integration sync completed.

### WARNING

Unexpected but recoverable conditions.

Examples:

- provider retry,
- integration degradation,
- stale execution detected,
- delayed worker,
- RAG indexing retry.

### ERROR

Operation failed and requires attention.

Examples:

- database operation failure,
- AI execution failure,
- failed document processing,
- integration failure after retries.

### CRITICAL

Platform-level or severe security/reliability failure.

Examples:

- database unavailable,
- authentication infrastructure unavailable,
- widespread worker failure,
- severe security event.

---

# 7. Sensitive Data Logging Policy

The following must never appear in ordinary application logs:

```text
Passwords
Authentication tokens
Refresh tokens
OAuth authorization codes
API keys
Provider secrets
Database credentials
Encryption keys
Signed URL secrets
Private document contents
Full user assessment responses
Full AI prompts containing private content
Full AI outputs containing private project content
Private GitHub source code
```

Instead log:

```text
document_id
execution_id
content_hash
content_length
provider
model
token counts
latency
status
error code
```

---

# 8. Error Logging

Every application error should have:

- error class,
- stable error code,
- severity,
- operation,
- correlation identifier,
- affected resource identifier where appropriate,
- retryability,
- sanitized message.

Example:

```json
{
  "event": "ai_execution_failed",
  "error_code": "AI_PROVIDER_TIMEOUT",
  "retryable": true,
  "execution_id": "...",
  "provider": "...",
  "model": "...",
  "latency_ms": 12000
}
```

Do not log raw exception objects if they can contain secrets or user content.

Stack traces may be retained in protected telemetry where operationally necessary.

---

# 9. API Observability

API telemetry should capture:

- HTTP method,
- route template,
- status code,
- latency,
- request size,
- response size where appropriate,
- authenticated role,
- resource scope,
- error code,
- rate-limit outcome.

Avoid logging:

- authorization headers,
- cookies containing secrets,
- raw request bodies,
- raw response bodies.

---

# 10. Core API Metrics

Recommended metrics include:

```text
http_requests_total
http_request_duration
http_errors_total
http_5xx_total
http_4xx_total
http_rate_limit_total
http_in_flight_requests
```

Useful dimensions:

- route,
- method,
- status class,
- role where safe,
- error code.

Do not use unrestricted user IDs as high-cardinality metric labels.

---

# 11. Database Observability

Database telemetry must monitor:

- connection health,
- connection pool utilization,
- query latency,
- transaction latency,
- failed transactions,
- deadlocks,
- lock contention,
- slow queries,
- migration status,
- storage growth,
- index health,
- RLS-related failures.

---

## 11.1 Database metrics

Examples:

```text
db_connections
db_pool_utilization
db_query_duration
db_transaction_duration
db_query_errors
db_deadlocks
db_lock_wait_time
```

---

## 11.2 Query logging

Do not log every SQL statement in normal production operation.

Targeted slow-query diagnostics may be enabled when required.

Query telemetry must avoid exposing private parameter values.

---

# 12. Background Worker Observability

Workers are responsible for:

- AI execution,
- document processing,
- RAG indexing,
- GitHub synchronization,
- email delivery,
- event handling,
- reconciliation,
- cleanup.

Each job should have a lifecycle:

```text
QUEUED
   ↓
STARTED
   ↓
RUNNING
   ↓
SUCCEEDED
```

or:

```text
RUNNING
   ↓
RETRYING
   ↓
FAILED
   ↓
DLQ
```

Telemetry must expose each transition.

---

# 13. Worker Metrics

Recommended metrics:

```text
jobs_queued
jobs_started
jobs_completed
jobs_failed
jobs_retried
jobs_dead_lettered
job_duration
job_queue_delay
worker_active_jobs
worker_capacity
```

Important dimensions:

- job type,
- outcome,
- retry count,
- priority where applicable.

---

# 14. Event Observability

The transactional outbox is part of the runtime architecture.

Observability must track:

- event creation,
- event publishing,
- handler execution,
- handler success,
- handler retry,
- handler failure,
- DLQ movement,
- duplicate delivery,
- idempotent suppression.

Metrics:

```text
events_created
events_processed
events_failed
events_retried
events_dlq
events_duplicate_suppressed
event_processing_latency
outbox_backlog
```

---

# 15. AI Provider Observability

The AI Provider Gateway is the single provider communication boundary.

Every provider call should produce sanitized telemetry containing:

- provider,
- logical capability,
- selected model,
- key identifier or safe key slot,
- execution ID,
- latency,
- timeout,
- retry count,
- status,
- token usage where available,
- estimated cost,
- fallback occurrence,
- rate-limit occurrence.

Never log the actual provider key.

---

# 16. AI Provider Metrics

Recommended metrics:

```text
ai_requests_total
ai_requests_success
ai_requests_failed
ai_request_duration
ai_provider_timeout
ai_provider_rate_limit
ai_provider_retry
ai_provider_fallback
ai_tokens_input
ai_tokens_output
ai_cost_estimated
ai_quota_exhausted
```

Provider and model should be bounded dimensions.

---

# 17. Five-Key AI Pool Observability

GrowFlow uses exactly five provider API keys.

Telemetry should show the operational state of each key without revealing the key.

Example:

```text
key_slot = 1
state = ACTIVE
```

Possible states:

```text
ACTIVE
RATE_LIMITED
COOLDOWN
FAILED
DISABLED
```

Metrics can expose:

```text
ai_key_active
ai_key_rate_limited
ai_key_cooldown
ai_key_failed
```

Actual credentials must never enter telemetry.

---

# 18. AI Execution Observability

Every significant AI workflow should have a persisted execution record.

Important fields include:

- execution ID,
- project instance,
- execution type,
- trigger,
- status,
- started time,
- completed time,
- duration,
- provider/model,
- token usage,
- estimated cost,
- retry count,
- QA outcome,
- regeneration count,
- failure code,
- correlation ID.

This allows the Admin AI Observatory to answer:

> What happened during this AI operation?

without requiring unrestricted inspection of raw private content.

---

# 19. Agent Observability

Each agent execution should expose:

- agent type,
- execution ID,
- parent execution,
- status,
- start/end,
- duration,
- model/capability,
- input context metadata,
- output validation status,
- tool calls,
- retry count,
- QA result,
- failure reason.

The twelve canonical agents remain:

```text
Idea
Scope
Technology
Features
Specification
MVP
Timeline
Risk
Task
Milestone
README
QA/Judge
```

---

# 20. Agent Metrics

Recommended metrics:

```text
agent_executions_total
agent_execution_duration
agent_execution_failures
agent_schema_validation_failures
agent_qa_failures
agent_regenerations
agent_tool_calls
agent_tool_failures
```

Useful dimensions:

- agent type,
- outcome,
- failure category.

---

# 21. AI Graph Observability

LangGraph workflow execution should expose:

```text
Workflow
 ├── Idea
 ├── Scope
 ├── Technology
 ├── Features
 ├── MVP
 ├── Specification
 ├── Timeline
 ├── Risk
 ├── Task
 ├── Milestone
 ├── README
 └── QA
```

Parallel branches must remain distinguishable.

The observability system should answer:

- Which node failed?
- Which nodes completed?
- Which nodes were retried?
- Which output failed validation?
- Why was regeneration triggered?
- How long did each node take?

---

# 22. QA/Judge Observability

QA/Judge is an operationally critical component.

Telemetry must record:

- QA execution,
- checks executed,
- pass/fail,
- failure categories,
- targeted regeneration request,
- regeneration count,
- final outcome.

Example categories:

```text
SCHEMA_INVALID
INCOMPLETE
CONTRADICTORY
OUT_OF_SCOPE
TECH_STACK_MISMATCH
TIMELINE_INCONSISTENCY
DEPENDENCY_ERROR
RISK_COVERAGE_GAP
README_INCONSISTENCY
UNSUPPORTED_CLAIM
```

---

# 23. AI Mentor Observability

AI Mentor is an application capability rather than a separate agent.

Telemetry should capture:

- interaction ID,
- project scope,
- authorized tools,
- execution duration,
- provider/model,
- tool calls,
- response generation status,
- error category.

The system must not automatically persist complete private conversations into ordinary logs.

Conversation persistence, if enabled by the product architecture, belongs to the canonical application data model rather than logs.

---

# 24. RAG Observability

RAG operations should be observable at metadata level.

Track:

- ingestion jobs,
- parsing status,
- chunk count,
- embedding status,
- indexing status,
- retrieval latency,
- retrieval count,
- empty retrievals,
- retrieval failures,
- embedding failures,
- stale-version detection.

---

# 25. RAG Metrics

Recommended:

```text
rag_ingestion_total
rag_ingestion_failures
rag_parse_duration
rag_chunk_count
rag_embedding_duration
rag_embedding_failures
rag_index_duration
rag_retrieval_total
rag_retrieval_duration
rag_empty_retrieval
rag_retrieval_errors
```

Useful metadata:

```text
project_instance_id
document_type
document_version
embedding_model
```

Do not use raw document contents as metric labels.

---

# 26. Retrieval Quality

Where evaluation infrastructure is available, measure:

- retrieval relevance,
- citation correctness,
- source coverage,
- empty retrieval rate,
- hallucination indicators,
- answer-grounding quality.

These belong to AI evaluation rather than ordinary infrastructure metrics.

---

# 27. Tavily Observability

Tavily is used for current web research where required.

Track:

- search count,
- latency,
- failures,
- retries,
- timeout,
- result count,
- evidence extraction status,
- citation/provenance persistence.

Do not automatically treat web evidence as authoritative.

---

# 28. GitHub Observability

GitHub integration is monitoring-only.

Track:

- synchronization start/end,
- API latency,
- API failures,
- rate limiting,
- repository availability,
- commit retrieval,
- branch retrieval,
- pull request/issue monitoring where applicable,
- checkpoint progression.

Never log repository private contents unnecessarily.

---

# 29. Email Observability

Email is an optional delivery channel.

Track:

```text
email_queued
email_sent
email_failed
email_retry
email_provider_timeout
```

Telemetry should use recipient identifiers only where operationally necessary and should avoid logging message bodies.

---

# 30. Storage Observability

Storage telemetry covers:

- upload attempts,
- successful uploads,
- failed uploads,
- file size,
- MIME validation failures,
- scan failures,
- parsing failures,
- storage errors,
- download failures,
- signed URL generation failures,
- deletion failures,
- object count,
- storage consumption.

Do not log private file content.

---

# 31. Security Observability

Security events must be separately identifiable.

Examples:

```text
AUTH_FAILURE
AUTHORIZATION_DENIED
RESOURCE_SCOPE_DENIED
RLS_DENIED
RATE_LIMIT_TRIGGERED
INVALID_UPLOAD
MALWARE_DETECTED
SSRF_BLOCKED
INVALID_OAUTH_STATE
TOKEN_FAILURE
SUSPICIOUS_TOOL_REQUEST
PROMPT_INJECTION_DETECTED
```

Security events should integrate with the audit architecture.

---

# 32. Audit vs Application Logs

These are different systems conceptually.

### Application logs

Operational troubleshooting.

### Audit events

Security/governance history.

Audit events should answer:

- who acted,
- what happened,
- when,
- against which resource,
- from which role,
- whether authorization succeeded,
- relevant security metadata.

Examples:

```text
USER_ACTIVATED
USER_SUSPENDED
GROUP_CREATED
PROJECT_CREATED
PROJECT_CHANGE_APPROVED
CONTROLLED_INVESTIGATION_STARTED
DOCUMENT_ACCESSED
RAG_REINDEX_REQUESTED
SECURITY_POLICY_CHANGED
```

---

# 33. Admin Observability Architecture

Admin receives a dedicated observability surface.

Primary sections:

```text
AI Usage
Agent Executions
AI Traces
AI Quality
System Health
Security & Audit
```

The Admin UI should expose operational metadata first.

Sensitive private content should require controlled investigation according to the already-defined authorization workflow:

```text
Request
   ↓
Authorization
   ↓
Minimum Required Data
   ↓
Inspection
   ↓
Audit Log
```

---

# 34. AI Usage Observatory

Admin should be able to inspect:

- executions over time,
- provider usage,
- model usage,
- token consumption,
- estimated cost,
- failures,
- retries,
- fallback frequency,
- quota exhaustion.

Do not expose provider API keys.

---

# 35. Agent Execution Observatory

Admin should be able to filter:

- agent,
- status,
- date range,
- project scope,
- execution type,
- failure category.

A selected execution should show:

```text
Execution
 ├── Workflow
 ├── Agent sequence
 ├── Timings
 ├── Validation
 ├── QA
 ├── Regeneration
 ├── Tool calls
 └── Final outcome
```

---

# 36. AI Trace Observatory

Tracing should provide a causality view:

```text
Request
  ↓
Application Service
  ↓
AI Execution
  ↓
Agent
  ↓
Tool
  ↓
RAG / Provider
  ↓
Validation
  ↓
QA
  ↓
Persistence
```

This is intended for troubleshooting and evaluation.

---

# 37. AI Quality Observatory

AI quality must not be reduced to one opaque score.

Expose multiple signals:

- schema validity,
- QA pass rate,
- regeneration rate,
- unsupported-claim rate,
- contradiction rate,
- retrieval quality,
- tool error rate,
- human feedback where available,
- task/blueprint consistency,
- execution failure rate.

Quality signals should remain interpretable.

---

# 38. Evaluation Architecture

AI evaluation should operate separately from production execution where practical.

Evaluation sources may include:

```text
Offline test datasets
Golden examples
Synthetic test cases
Regression suites
Human review
Production telemetry samples
```

Production evaluation must respect privacy and authorization constraints.

---

# 39. AI Evaluation Categories

Evaluation should cover:

### Structured Output

- schema correctness,
- required fields,
- type validity.

### Content Quality

- completeness,
- relevance,
- consistency,
- project alignment.

### Safety

- prompt injection resistance,
- authorization compliance,
- data leakage prevention.

### RAG

- retrieval relevance,
- grounding,
- citation accuracy.

### Planning

- dependency correctness,
- milestone/task coherence,
- timeline consistency.

### Risk

- risk coverage,
- mitigation quality,
- unsupported assumptions.

---

# 40. Regression Evaluation

Every significant AI architecture change should be evaluated against a controlled test set.

Examples:

- prompt changes,
- model changes,
- agent changes,
- tool changes,
- RAG changes,
- embedding changes,
- provider changes.

The goal is to detect quality regressions before broad deployment.

---

# 41. AI Evaluation Metadata

Evaluation records should contain:

```text
evaluation_id
execution_id
test_case_id
model
provider
agent
evaluation_type
metric
score
threshold
pass/fail
created_at
```

Where possible, store references rather than duplicating sensitive content.

---

# 42. Alerting Architecture

Alerts should be based on actionable conditions rather than every error.

Examples:

### Critical

- database unavailable,
- authentication unavailable,
- all AI provider keys exhausted,
- worker fleet unavailable,
- storage unavailable.

### High

- sustained API 5xx increase,
- sustained AI failure rate,
- RAG ingestion outage,
- GitHub integration outage,
- rapidly growing outbox/DLQ backlog.

### Medium

- elevated latency,
- increased provider retries,
- increased QA regeneration,
- email delivery degradation.

---

# 43. Alert Fatigue Prevention

Do not create an alert for every individual failure.

Prefer:

```text
Rate
Threshold
Duration
Impact
```

Example:

> Alert when AI execution failure rate exceeds an agreed threshold for a sustained interval.

Not:

> Alert on every single AI failure.

---

# 44. Health Checks

GrowFlow should provide health endpoints with different purposes.

### Liveness

Answers:

> Is the process alive?

### Readiness

Answers:

> Can the process safely serve traffic?

### Dependency health

Checks important dependencies such as:

- PostgreSQL,
- AI provider gateway,
- worker runtime,
- storage,
- RAG infrastructure,
- required external integrations.

Health checks must not expose secrets.

---

# 45. Dependency Degradation

The platform should distinguish:

```text
Healthy
Degraded
Unavailable
```

Example:

```text
Database: HEALTHY
AI Provider: DEGRADED
GitHub: HEALTHY
Tavily: HEALTHY
Email: UNAVAILABLE
```

A non-critical integration failure should not falsely mark the entire application as unavailable.

---

# 46. User Experience Reliability

Technical health does not guarantee a good user experience.

Track meaningful user-facing outcomes such as:

- assessment submission success,
- blueprint generation success,
- document generation success,
- task creation success,
- AI Mentor response success,
- GitHub connection success,
- notification delivery success.

This creates a distinction between:

```text
Infrastructure Healthy
```

and:

```text
User Workflow Healthy
```

Both matter.

---

# 47. SLA / SLO-Oriented Thinking

GrowFlow should eventually define service-level objectives around important workflows.

Potential categories:

```text
API availability
API latency
AI workflow completion
Background job completion
Document processing
RAG availability
Notification delivery
GitHub synchronization
```

Exact numerical targets should be finalized using real workload and deployment characteristics rather than arbitrary values now.

---

# 48. Performance Observability

Monitor:

- API latency,
- DB latency,
- worker queue delay,
- AI provider latency,
- agent latency,
- RAG retrieval latency,
- document processing latency,
- integration latency.

End-to-end workflow duration is especially important for long-running AI workflows.

---

# 49. Capacity Observability

Track resource pressure:

```text
CPU
Memory
DB connections
Worker concurrency
Queue depth
Storage usage
AI quota
External API limits
```

Capacity alerts should occur before hard failure where possible.

---

# 50. High-Cardinality Data Policy

Do not place high-cardinality identifiers into metrics indiscriminately.

Avoid labels such as:

```text
user_id
document_id
execution_id
request_id
```

for every metric.

These belong primarily in logs/traces/persisted execution records.

Metrics should use bounded dimensions.

---

# 51. Observability Storage

Observability data should be separated conceptually from canonical application state.

Canonical business state remains in PostgreSQL.

Telemetry may use:

- structured log storage,
- tracing backend,
- metrics backend,
- LangSmith-compatible AI tracing,
- PostgreSQL for selected execution/audit records.

Observability infrastructure must not become the source of truth for business entities.

---

# 52. Retention

Retention should differ by telemetry type.

Conceptually:

```text
Operational logs → shorter retention
Detailed traces → shorter/controlled retention
Metrics → medium/long retention
Audit events → longer retention
AI execution metadata → product-defined retention
Evaluation results → longer retention where useful
```

Exact retention periods should be determined during deployment and compliance review.

Do not retain private content indefinitely merely because telemetry exists.

---

# 53. Cost Control

Observability itself has cost.

Control:

- log volume,
- trace sampling,
- payload size,
- retention,
- metric cardinality,
- AI trace payloads,
- repeated diagnostics.

Detailed tracing can be sampled for normal traffic while retaining complete traces for:

- failures,
- AI executions,
- controlled debugging,
- evaluation workloads.

---

# 54. AI Trace Sampling

AI workflows are valuable enough that trace retention should be stronger than ordinary HTTP traffic.

Recommended principle:

```text
Normal API traffic → sampled traces
AI workflow failures → retain
AI QA failures → retain
AI regeneration → retain
Security events → retain
Evaluation runs → retain
```

Private content still follows the data-minimization rules.

---

# 55. Observability and Privacy

Telemetry must preserve the same authorization boundaries as the application.

A mentor must not gain access to:

- unrelated project telemetry,
- another group's private project data,
- admin-only platform telemetry.

A student must only see telemetry relevant to their authorized project/application experience.

Admin access is broad but still subject to controlled investigation for deeper private content.

---

# 56. Observability and RLS

Where observability records are stored in PostgreSQL and exposed through application APIs:

- RLS should apply where appropriate,
- application authorization remains mandatory,
- admin observability APIs must not bypass security,
- raw telemetry tables must not be directly exposed to clients.

---

# 57. Observability and AI Authorization

AI tools must not use telemetry to bypass project authorization.

For example:

```text
AI Mentor → execution history
```

must still be filtered to the current authorized project.

Admin AI access follows Admin authorization and controlled investigation rules.

---

# 58. Failure Correlation Example

Suppose blueprint generation fails.

Expected observability chain:

```text
POST /projects/{id}/blueprint
        │
        ├── request_id
        │
        └── correlation_id
                │
                ▼
        blueprint service
                │
                ▼
        AI execution
                │
                ├── provider call
                │
                ├── Idea agent
                ├── Scope agent
                ├── parallel agents
                └── QA/Judge
                        │
                        ▼
                  QA failure
                        │
                        ▼
                 regeneration
                        │
                        ▼
                    failure
                        │
                        ▼
               persisted execution
                        │
                        ▼
                 SSE / notification
```

An operator should be able to reconstruct this sequence without reading private content.

---

# 59. Stale Execution Observability

GrowFlow protects against stale AI execution.

Telemetry should identify:

```text
execution_version
project_version
expected_version
actual_version
stale = true/false
```

When stale output is rejected, record:

```text
STALE_EXECUTION_REJECTED
```

This is operationally important because it distinguishes safe rejection from unexpected failure.

---

# 60. Cancellation Observability

For cancellable AI/background work, record:

- cancellation requested,
- cancellation acknowledged,
- worker stopped,
- partial result discarded,
- cleanup completed.

Example:

```text
AI_EXECUTION_CANCEL_REQUESTED
AI_EXECUTION_CANCELLED
```

---

# 61. Browser Disconnect Observability

A browser disconnect must not automatically imply execution failure.

Telemetry should distinguish:

```text
CLIENT_DISCONNECTED
EXECUTION_CONTINUES
EXECUTION_SUCCEEDED
```

from:

```text
EXECUTION_FAILED
```

The persisted execution remains authoritative.

---

# 62. Reconciliation Observability

Startup and periodic reconciliation jobs should report:

- stale queued jobs,
- orphaned executions,
- unprocessed outbox events,
- stuck RAG jobs,
- stale document processing,
- integration checkpoints,
- incomplete notifications.

Reconciliation results should be measurable and auditable.

---

# 63. Deployment Observability

Deployment/runtime telemetry should include:

- application version,
- environment,
- deployment identifier,
- startup success,
- migration status,
- worker version,
- configuration validation,
- dependency readiness.

Never log secrets during configuration validation.

---

# 64. Configuration Drift

Important operational configuration should be observable through safe metadata:

```text
environment
app version
feature flags
AI capability configuration
worker configuration
RAG configuration
integration availability
```

Secret values must never be displayed.

---

# 65. Observability Dashboard Hierarchy

Recommended platform hierarchy:

```text
System Overview
    ↓
System Health
    ↓
Application
    ↓
Workers / Events
    ↓
AI Infrastructure
    ↓
RAG
    ↓
Integrations
    ↓
Storage
    ↓
Security / Audit
```

For AI:

```text
AI Overview
    ↓
Usage
    ↓
Executions
    ↓
Traces
    ↓
Agents
    ↓
QA / Quality
    ↓
Evaluation
```

---

# 66. Student-Facing Observability

Students should not see internal infrastructure telemetry.

They may see user-oriented statuses such as:

```text
Generating blueprint…
Processing document…
Syncing GitHub…
AI Mentor temporarily unavailable.
```

Where appropriate:

- progress,
- status,
- retry state,
- actionable error,
- recovery guidance.

Avoid exposing internal provider names, key states, stack traces, or infrastructure details.

---

# 67. Mentor-Facing Observability

Mentors should see project-relevant operational information where it helps them supervise students.

Examples:

- blueprint generation status,
- blocked AI workflow,
- GitHub sync status,
- document processing status,
- project risk changes.

They should not receive unrestricted internal infrastructure telemetry.

---

# 68. Admin-Facing Observability

Admin receives the broadest platform observability but still under authorization and privacy rules.

Admin can inspect:

- platform health,
- AI usage,
- agent executions,
- traces,
- quality,
- jobs,
- events,
- integrations,
- storage,
- security,
- audit.

Private content requires controlled investigation where applicable.

---

# 69. Notification Integration

Observability events should feed the notification system only when an event is user-actionable.

Examples:

```text
Blueprint generation failed
Document processing failed
GitHub connection degraded
AI Mentor unavailable
```

Internal low-level telemetry should not generate user notifications.

---

# 70. Activity Integration

Activity timeline should use canonical domain events rather than arbitrary log entries.

Therefore:

```text
Domain Event
   ├── Activity Projection
   ├── Notification Projection
   └── Operational Telemetry
```

Application logs remain separate.

---

# 71. Testing Observability

Observability itself must be tested.

Test:

- correlation propagation,
- sanitized logging,
- error classification,
- metric emission,
- trace creation,
- async correlation,
- worker telemetry,
- AI execution telemetry,
- RAG telemetry,
- security event telemetry,
- audit generation,
- privacy boundaries.

---

# 72. Failure Injection

Test scenarios should include:

```text
Database unavailable
AI provider timeout
AI rate limit
All AI keys exhausted
Worker crash
Outbox backlog
DLQ accumulation
RAG embedding failure
Storage failure
GitHub rate limit
Tavily timeout
Email provider failure
Browser disconnect
AI execution cancellation
Stale AI output
```

The expected telemetry must remain coherent.

---

# 73. Observability Security Tests

Verify that:

- secrets are not logged,
- authorization failures do not leak resource data,
- private documents are not exposed through traces,
- AI prompts are sanitized,
- tool parameters are controlled,
- admin investigation is audited,
- logs cannot be used to bypass RLS,
- telemetry endpoints are protected.

---

# 74. Operational Runbook Integration

Critical alerts should eventually map to runbooks.

Example:

```text
ALERT:
AI_PROVIDER_ALL_KEYS_EXHAUSTED

Runbook:
1. Verify provider health
2. Inspect key states
3. Check rate-limit/quota telemetry
4. Confirm fallback state
5. Verify deterministic platform functions
6. Wait for cooldown/recovery
7. Escalate if persistent
```

Runbooks are operational documentation, not application logic.

---

# 75. Observability Invariants

The following are non-negotiable:

1. Every meaningful request is correlatable.
2. Async work preserves correlation.
3. AI executions are traceable.
4. Agent executions are distinguishable.
5. QA failures are observable.
6. Provider failures are observable.
7. RAG failures are observable.
8. Integration degradation is observable.
9. Worker failures are observable.
10. Security events are distinguishable.
11. Audit events remain separate from ordinary logs.
12. Secrets never enter telemetry.
13. Private content is minimized.
14. Metrics avoid uncontrolled cardinality.
15. User-facing telemetry is simplified.
16. Admin observability respects authorization.
17. Observability never becomes a bypass around application security.
18. Business state remains in canonical PostgreSQL.
19. AI quality is measurable independently of infrastructure health.
20. Failure recovery remains observable.

---

# 76. Relationship to Other Phase 6 Subphases

## 6A — Backend Architecture

Defines the application layers and shared infrastructure into which observability is integrated.

## 6B — Database Architecture

Defines canonical persistence, audit/execution records, RLS, and database telemetry boundaries.

## 6C — API Architecture

Defines API routes, responses, errors, status codes, SSE, and request-level observability.

## 6D — Authentication & Security

Defines identity, authorization, RLS, security controls, and security telemetry requirements.

## 6E — AI Provider Gateway

Provides provider/model/key telemetry and AI usage/cost information.

## 6F — Agent Execution Infrastructure

Provides agent, graph, tool, QA, regeneration, and execution telemetry.

## 6G — RAG & Document Intelligence

Provides ingestion, retrieval, embedding, and indexing telemetry.

## 6H — Events, Jobs & Reliability

Provides worker, event, outbox, retry, DLQ, cancellation, and reconciliation telemetry.

## 6I — External Integrations

Provides GitHub, Tavily, OAuth, email, and outbound integration telemetry.

## 6K — Storage & File Architecture

Provides upload, object storage, parsing, scanning, download, deletion, and storage telemetry.

## 6L — Deployment & Runtime

Consumes health, resource, deployment, startup, and runtime telemetry.

## 6M — Infrastructure Security

Defines infrastructure-level security monitoring and incident telemetry.

## 6N — Backend Architecture Finalization

Will consolidate observability into the final backend architecture and ensure all cross-cutting runtime concerns have a coherent implementation boundary.

---

# 77. Explicit Non-Goals

GrowFlow observability does **not** introduce:

- a custom observability platform,
- unnecessary microservices,
- Kafka solely for telemetry,
- a dedicated event-sourcing system,
- unrestricted log storage,
- raw private-content logging,
- unrestricted AI prompt retention,
- custom distributed tracing infrastructure,
- arbitrary metric cardinality,
- autonomous remediation by Admin AI,
- observability-driven business-state mutation,
- a second source of truth for application state.

Use mature infrastructure/services where appropriate.

---

# 78. Recommended Initial Technology Direction

The architecture remains provider/tool conscious rather than tightly coupled to one vendor.

Initial direction:

```text
Application logs
    → structured logging backend

Metrics
    → Prometheus-compatible metrics / managed equivalent

Tracing
    → OpenTelemetry-compatible instrumentation

AI tracing/evaluation
    → LangSmith-compatible integration

Application execution records
    → PostgreSQL

Audit records
    → PostgreSQL / dedicated secure audit storage as needed
```

Exact hosted products may be finalized during deployment architecture.

The architecture should avoid unnecessary vendor lock-in where practical.

---

# 79. Final Observability Architecture

```text
                         ┌───────────────────────┐
                         │      GrowFlow UI      │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       FastAPI         │
                         │ Request Correlation   │
                         └───────────┬───────────┘
                                     │
             ┌───────────────────────┼────────────────────────┐
             │                       │                        │
             ▼                       ▼                        ▼
      Application Logs          Metrics                  Traces
             │                       │                        │
             └───────────────────────┼────────────────────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │  Application Services │
                         └───────────┬───────────┘
                                     │
       ┌─────────────────────────────┼──────────────────────────┐
       │                             │                          │
       ▼                             ▼                          ▼
    PostgreSQL                  Event/Workers                AI Runtime
       │                             │                          │
       │                             │             ┌────────────┼────────────┐
       │                             │             │            │            │
       │                             │             ▼            ▼            ▼
       │                             │          Agents         RAG        Provider
       │                             │             │            │            │
       │                             │             └────────────┼────────────┘
       │                             │                          │
       │                             ▼                          ▼
       │                       Job Telemetry             AI Telemetry
       │
       ├── Audit
       ├── Execution Metadata
       └── Domain State

External Integrations ───────────────► Integration Telemetry

Storage ─────────────────────────────► Storage Telemetry

Security Controls ───────────────────► Security + Audit Telemetry

                         ┌─────────────────────────────┐
                         │     Admin Observability     │
                         │ Health / Usage / Traces /   │
                         │ Agents / Quality / Audit    │
                         └─────────────────────────────┘
```

---

# 80. Final Decision Summary

The following decisions are frozen for GrowFlow 6J:

| Area | Frozen Decision |
|---|---|
| Logging | Structured logs |
| Metrics | Metrics-first operational monitoring |
| Tracing | Distributed tracing with correlation |
| AI tracing | First-class |
| Agent tracing | First-class |
| RAG telemetry | First-class |
| Worker telemetry | First-class |
| Event telemetry | First-class |
| Integration telemetry | First-class |
| Security telemetry | First-class |
| Audit | Separate from application logs |
| Correlation | Mandatory across async boundaries |
| Secrets | Never logged |
| Private content | Minimized / controlled |
| AI quality | Separate evaluation layer |
| Admin observability | Broad metadata-first visibility |
| Deep private inspection | Controlled investigation |
| Canonical business state | PostgreSQL |
| High-cardinality metrics | Restricted |
| Alerting | Actionable thresholds |
| Health | Liveness + readiness + dependency health |
| Failure recovery | Observable |
| Vendor coupling | Provider-neutral architecture |
| Complexity | No unnecessary observability platform |

---

# 81. Freeze Statement

This document is the **FINAL and ARCHITECTURALLY FROZEN specification for GrowFlow Phase 6J — Observability, Monitoring, Logging & AI Evaluation Architecture**.

It is intended to be consumed by:

- backend architecture,
- API implementation,
- AI infrastructure,
- agent orchestration,
- RAG infrastructure,
- worker/runtime infrastructure,
- external integrations,
- storage,
- security,
- deployment,
- testing,
- frontend/admin observability surfaces,
- final backend architecture finalization.

No implementation should begin by inventing a parallel observability architecture.

Any future change should be treated as an explicit architectural change and evaluated against:

- security,
- privacy,
- reliability,
- AI quality,
- performance,
- operational cost,
- consistency with the canonical GrowFlow architecture.

**Status: FROZEN.**
