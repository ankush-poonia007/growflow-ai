# GrowFlow — Phase 6L
# Deployment, Infrastructure & Runtime Architecture
## Final Specification

**Status:** Architecturally FROZEN  
**Phase:** Phase 6 — Infrastructure & Runtime Architecture  
**Subphase:** 6L — Deployment & Runtime  
**Project:** GrowFlow  
**Architecture Style:** Modular Monolith + Async Workers + Managed Infrastructure  
**Primary Backend:** FastAPI  
**Primary Database:** PostgreSQL / Supabase  
**Frontend:** Separate Client Application  
**AI Runtime:** LangGraph + AI Provider Gateway  
**Background Runtime:** Worker-based asynchronous execution

---

# 1. Purpose

This document defines how the already-frozen GrowFlow architecture is packaged, deployed, started, operated, upgraded, monitored, and recovered across environments.

The goal is not to introduce a new infrastructure architecture.

The goal is to provide a practical runtime boundary for:

- local development,
- testing,
- staging,
- production,
- API runtime,
- background workers,
- PostgreSQL/Supabase,
- object storage,
- RAG/vector infrastructure,
- AI providers,
- external integrations,
- observability,
- security controls,
- backups,
- migrations,
- deployments,
- rollback,
- recovery.

The architecture remains intentionally simple:

```text
Frontend
   ↓
FastAPI API
   ↓
Application / Domain
   ↓
PostgreSQL / Supabase

FastAPI
   ↓
Transactional Outbox
   ↓
Background Workers
   ├── AI
   ├── RAG
   ├── Documents
   ├── GitHub
   └── Email

External Services
   ├── AI Provider
   ├── Tavily
   ├── GitHub
   └── OAuth / Email

Observability
   ├── Logs
   ├── Metrics
   ├── Traces
   └── AI Evaluation
```

---

# 2. Deployment Principles

## 2.1 Modular Monolith First

GrowFlow is deployed as a modular monolith rather than microservices.

The primary application boundary is:

```text
FastAPI Application
```

Internal modules remain logically separated.

Do not deploy every domain module as a separate service.

---

## 2.2 Workers Are Separate Runtime Processes

Background processing should run separately from the request-serving API.

Conceptually:

```text
API Process
    +
Worker Process(es)
```

This prevents long-running AI/document/RAG operations from consuming API worker capacity.

Workers use the same application/domain codebase while running different runtime entry points.

---

## 2.3 Managed Infrastructure Where Practical

Prefer managed services for infrastructure that does not create product differentiation.

Examples:

- PostgreSQL/Supabase,
- object storage,
- managed deployment platform,
- managed observability,
- managed email,
- external AI providers.

Do not build custom infrastructure merely to reproduce commodity capabilities.

---

# 3. Environment Model

GrowFlow should support:

```text
Development
Testing
Staging
Production
```

Each environment must have independent configuration and appropriate data boundaries.

---

# 4. Development Environment

Development should support:

- local FastAPI,
- local or development database,
- local worker,
- local frontend,
- local object-storage-compatible workflow,
- test AI provider configuration,
- development OAuth configuration,
- development observability.

Production credentials must never be reused in development.

---

# 5. Testing Environment

Automated tests should run against isolated resources.

The test environment must not depend on:

- production data,
- production storage,
- production AI keys,
- production OAuth credentials.

Where external services are difficult to test safely, use controlled mocks/fakes at the adapter boundary.

---

# 6. Staging Environment

Staging should approximate production architecture closely enough to validate:

- migrations,
- API behavior,
- workers,
- AI workflows,
- RAG,
- object storage,
- integrations,
- observability,
- deployment process.

Staging must remain isolated from production credentials and private data.

---

# 7. Production Environment

Production consists conceptually of:

```text
                     ┌───────────────────┐
                     │      Frontend     │
                     └─────────┬─────────┘
                               │ HTTPS
                               ▼
                     ┌───────────────────┐
                     │    FastAPI API    │
                     └─────────┬─────────┘
                               │
              ┌────────────────┼─────────────────┐
              │                │                 │
              ▼                ▼                 ▼
        PostgreSQL          Outbox          Object Storage
              │                │
              │                ▼
              │             Workers
              │                │
              │       ┌────────┼────────┐
              │       │        │        │
              ▼       ▼        ▼        ▼
            State     AI       RAG   Integrations
```

---

# 8. Runtime Components

The deployment must account for:

1. Frontend runtime
2. FastAPI API runtime
3. Background worker runtime
4. PostgreSQL/Supabase
5. Object storage
6. pgvector/RAG storage
7. AI Provider Gateway
8. External integrations
9. Observability infrastructure
10. Secret/configuration management
11. Backup/recovery mechanisms

---

# 9. Frontend Deployment

The frontend is a separate client application.

Production frontend requirements:

- HTTPS,
- environment-specific configuration,
- API base URL configuration,
- secure authentication flow,
- no server secrets,
- no provider API keys,
- no database credentials,
- no object-storage master credentials.

Frontend configuration must only contain values intended for client exposure.

---

# 10. Backend Deployment

The FastAPI application should run as a production ASGI service.

Conceptually:

```text
Reverse Proxy / Platform
        ↓
ASGI Server
        ↓
FastAPI
```

Development server configuration must not be reused blindly in production.

---

# 11. API Scaling

The API should be horizontally scalable when required:

```text
             ┌── API Instance 1
Load Balancer┼── API Instance 2
             └── API Instance N
```

The application should remain stateless at the process level.

Durable state belongs in:

- PostgreSQL,
- object storage,
- external services,
- persisted execution/job state.

Do not rely on local process memory for canonical application state.

---

# 12. Worker Deployment

Workers run independently from API processes.

Conceptually:

```text
Worker Pool
 ├── Worker 1
 ├── Worker 2
 └── Worker N
```

The number of workers should be configurable.

Scaling must respect:

- database capacity,
- AI provider quotas,
- external API rate limits,
- memory requirements,
- job concurrency,
- storage throughput.

More workers are not automatically better.

---

# 13. Worker Classes

Workers may process:

```text
AI execution
Document processing
RAG indexing
GitHub synchronization
Email delivery
Event handlers
Cleanup
Reconciliation
```

A single worker runtime may initially process multiple job types.

Separate worker pools should only be introduced when workload isolation requires them.

---

# 14. Worker Concurrency

Concurrency must be bounded.

Controls should exist for:

- total worker concurrency,
- per-job-type concurrency,
- AI concurrency,
- document-processing concurrency,
- RAG concurrency,
- external integration concurrency.

This prevents resource exhaustion.

---

# 15. API vs Worker Responsibilities

## API

Handles:

- authentication,
- authorization,
- validation,
- short operations,
- job submission,
- status retrieval,
- SSE streaming.

## Worker

Handles:

- long-running AI workflows,
- document processing,
- RAG indexing,
- integration synchronization,
- email delivery,
- retries,
- reconciliation,
- cleanup.

---

# 16. Long-Running Operations

Long-running operations should not hold an HTTP request open unnecessarily.

Preferred flow:

```text
POST /operation
      ↓
Validate + Authorize
      ↓
Create Execution / Job
      ↓
Return 202 Accepted
      ↓
Worker Executes
      ↓
Persist State
      ↓
SSE / Polling / Notification
```

This applies particularly to:

- blueprint generation,
- document processing,
- RAG indexing,
- large exports,
- integration synchronization.

---

# 17. SSE Runtime

SSE is used for appropriate real-time progress delivery.

Architecture:

```text
Worker
  ↓
Persisted execution state
  ↓
Event/progress channel
  ↓
SSE endpoint
  ↓
Frontend
```

The worker must not depend on an active browser connection.

If the browser disconnects:

```text
Execution continues
```

unless the user explicitly cancels it.

---

# 18. Runtime State

Canonical runtime state must be persisted.

Examples:

```text
Job status
Execution status
Processing status
RAG status
Integration checkpoint
Notification status
```

In-memory state may optimize processing but cannot be the only copy of important state.

---

# 19. Configuration Architecture

All runtime configuration must flow through the centralized configuration system defined in Phase 6A.

Application code must not read `.env` files directly.

Conceptually:

```text
Environment / Secret Manager
          ↓
Configuration Layer
          ↓
Typed Settings
          ↓
Application Components
```

---

# 20. Configuration Categories

Configuration includes:

### Application

- environment,
- host,
- port,
- debug mode,
- API version.

### Database

- connection configuration,
- pool settings,
- timeout settings.

### Workers

- concurrency,
- polling,
- retry configuration.

### AI

- provider endpoints,
- model policies,
- timeout,
- key slots,
- rate limits.

### RAG

- embedding configuration,
- chunking configuration,
- indexing concurrency.

### Storage

- bucket/storage configuration,
- limits,
- signed URL expiry.

### Integrations

- GitHub,
- Tavily,
- OAuth,
- email.

### Observability

- log level,
- trace configuration,
- metrics,
- AI tracing.

Secrets are handled separately.

---

# 21. Secret Management

Secrets must never be committed to source control.

Examples:

```text
Database credentials
Supabase service credentials
AI provider keys
Tavily key
OAuth client secrets
GitHub integration secrets
Email credentials
Signing secrets
```

Secrets should be injected through:

- deployment environment,
- secret manager,
- managed platform secret storage.

---

# 22. Secret Rotation

The runtime must support secret rotation without architectural redesign.

Rotation should include:

- AI provider keys,
- OAuth secrets,
- database/service credentials,
- signing secrets,
- integration credentials.

The five AI provider keys remain managed by the AI Provider Gateway.

---

# 23. Database Deployment

PostgreSQL/Supabase remains the canonical persistence layer.

Production database requirements:

- managed PostgreSQL where practical,
- TLS,
- backups,
- connection controls,
- migrations,
- monitoring,
- RLS,
- appropriate indexing,
- connection pool management.

---

# 24. Database Connection Pooling

API and workers must use bounded connection pools.

Do not allow:

```text
API instances × unlimited connections
```

to exhaust PostgreSQL.

Capacity planning must account for:

```text
API replicas
Worker replicas
Worker concurrency
Admin/operational access
Migration connections
```

---

# 25. Database Migrations

Schema changes must use version-controlled migrations.

Migration flow:

```text
Migration File
      ↓
Test
      ↓
Staging
      ↓
Backup/Recovery Readiness
      ↓
Production
```

Do not rely on manual production schema edits.

---

# 26. Migration Safety

Migrations should be designed to minimize downtime.

For significant changes:

```text
Expand
   ↓
Deploy compatible application
   ↓
Backfill
   ↓
Switch usage
   ↓
Contract / cleanup
```

Destructive changes should not be performed before dependent application code is safely migrated.

---

# 27. Deployment Strategy

The preferred strategy is controlled incremental deployment.

Conceptually:

```text
Build
 ↓
Automated Tests
 ↓
Security Checks
 ↓
Artifact Creation
 ↓
Staging Deployment
 ↓
Smoke Tests
 ↓
Production Deployment
 ↓
Health Verification
```

---

# 28. Application Artifact

The backend should be deployed as a reproducible artifact.

Containerization is appropriate where supported.

The artifact should contain:

- application code,
- dependency definitions,
- runtime configuration hooks.

Secrets must not be baked into the image.

---

# 29. Container Architecture

If containers are used:

```text
API Image
Worker Image
```

may share a common base/build pipeline while using different entry points.

The container should:

- run as non-root where feasible,
- use minimal runtime dependencies,
- expose only required ports,
- avoid writable persistent filesystem assumptions,
- receive configuration externally.

---

# 30. Runtime Hardening

Production runtime should use:

- least privilege,
- non-root execution,
- read-only filesystem where practical,
- bounded resources,
- minimal packages,
- controlled outbound network access,
- secure TLS configuration.

Infrastructure security details are governed by 6M.

---

# 31. Resource Limits

Define limits for:

```text
CPU
Memory
Disk
Worker concurrency
Request size
Upload size
Job duration
AI execution duration
```

Limits prevent a single operation from exhausting the platform.

---

# 32. Autoscaling

Autoscaling may be used when supported and useful.

Scale based on meaningful signals such as:

```text
API CPU/load
Request latency
Worker queue depth
Worker utilization
```

Do not autoscale solely because an AI job exists.

AI provider quotas and database capacity must remain constraints.

---

# 33. Database-Aware Scaling

Scaling API/workers must not outpace PostgreSQL capacity.

Example:

```text
More API replicas
      ↓
More DB connections
      ↓
Potential DB saturation
```

Therefore replica counts and pool sizes must be coordinated.

---

# 34. AI-Aware Scaling

AI worker concurrency must account for:

- five-key provider pool,
- provider rate limits,
- model limits,
- token throughput,
- cost,
- execution latency.

The worker runtime must not attempt to defeat provider quotas by uncontrolled concurrency.

---

# 35. RAG-Aware Scaling

RAG jobs may be CPU/memory/storage intensive.

Control:

- parsing concurrency,
- embedding concurrency,
- indexing concurrency,
- document size,
- batch size.

RAG processing must not starve API capacity.

---

# 36. External Integration Runtime

External calls should occur through adapters.

Examples:

```text
GitHub Adapter
Tavily Adapter
Email Adapter
OAuth Adapter
AI Provider Gateway
```

External calls must have:

- timeout,
- retry policy,
- rate-limit handling,
- error classification,
- observability.

---

# 37. Network Architecture

Conceptually:

```text
Internet
   ↓
HTTPS
   ↓
Frontend
   ↓
HTTPS
   ↓
API
   ├── PostgreSQL
   ├── Object Storage
   ├── AI Provider
   ├── Tavily
   ├── GitHub
   └── Email
```

The exact cloud/network topology may vary.

The application should not expose PostgreSQL directly to the public internet unless the selected managed service architecture explicitly requires a secure managed endpoint.

---

# 38. HTTPS

Production client-to-server traffic must use HTTPS.

TLS must cover:

- frontend,
- API,
- external service communication where applicable,
- database/storage connections where supported.

HTTP should redirect to HTTPS where appropriate.

---

# 39. CORS

CORS must be explicitly configured for approved frontend origins.

Do not use permissive wildcard configuration in production when credentials are involved.

Development origins may differ from production.

---

# 40. Health Endpoints

The runtime should provide:

```text
Liveness
Readiness
Dependency Health
```

Health responses must not disclose secrets.

Readiness should prevent traffic from reaching an instance that cannot safely operate.

---

# 41. Startup Sequence

A production process should roughly:

```text
Start
 ↓
Load configuration
 ↓
Validate required configuration
 ↓
Initialize application components
 ↓
Initialize observability
 ↓
Initialize DB/storage clients
 ↓
Register routes/services
 ↓
Readiness
```

Workers additionally initialize:

```text
Worker runtime
 ↓
Job/event consumers
 ↓
Reconciliation checks
 ↓
Ready
```

---

# 42. Startup Reconciliation

Workers should reconcile potentially stale runtime state after restart.

Examples:

- stuck jobs,
- stale AI executions,
- unprocessed outbox events,
- stale RAG jobs,
- incomplete document processing,
- expired temporary artifacts.

This is governed by 6H.

---

# 43. Graceful Shutdown

API shutdown should:

1. stop accepting new work,
2. allow in-flight short requests to finish where practical,
3. close connections,
4. flush important telemetry,
5. terminate cleanly.

Worker shutdown should:

1. stop accepting new jobs,
2. finish or safely checkpoint current work,
3. mark/requeue interrupted work according to job semantics,
4. close resources,
5. flush telemetry.

---

# 44. Deployment Health Verification

After deployment verify:

```text
API reachable
Authentication works
Database reachable
Migrations correct
Workers running
Storage accessible
AI provider gateway operational
RAG infrastructure operational
External integrations operational/degraded as expected
Observability active
```

Smoke tests should cover critical user flows.

---

# 45. Critical Smoke Tests

At minimum:

```text
Login
Project access
Assessment submission
Blueprint execution start
Execution status retrieval
Document access
Task access
AI Mentor request
Notification path
GitHub connection path where enabled
Admin health access
```

External services may be validated through safe health checks rather than destructive operations.

---

# 46. Rollback

Rollback must be possible for application deployments.

Conceptually:

```text
New Version
   ↓
Health Failure
   ↓
Rollback Application Artifact
   ↓
Verify
```

Database rollback is more complex and should not rely on blind reverse migrations.

Prefer forward-compatible migrations.

---

# 47. Database Rollback Strategy

For dangerous schema changes:

```text
Expand
 ↓
Deploy
 ↓
Verify
 ↓
Contract later
```

This reduces the need for destructive database rollback.

If data migration has occurred, restoration should use:

- backups,
- controlled recovery,
- forward correction,
rather than assuming schema reversal is safe.

---

# 48. Blue/Green or Canary Deployment

These strategies may be adopted if deployment scale justifies them.

They are not mandatory for the initial architecture.

The application must remain deployable safely without introducing unnecessary infrastructure.

---

# 49. Feature Flags

Feature flags may control gradual release of risky features.

Examples:

```text
New AI workflow
New RAG behavior
New integration
Experimental UI
```

Flags should be:

- centrally configured,
- auditable where important,
- environment-aware,
- fail-safe.

Feature flags must not replace authorization.

---

# 50. Scheduled Runtime Jobs

Some jobs are periodic:

```text
Reconciliation
Cleanup
Expired export cleanup
Temporary-file cleanup
Integration synchronization
Operational checks
```

Use the existing worker/job architecture rather than introducing a second scheduling platform unnecessarily.

---

# 51. Backup Architecture

Backups must cover:

### PostgreSQL

- automated backups,
- point-in-time recovery where available,
- restoration testing.

### Object Storage

- provider-supported durability,
- versioning/backup where appropriate,
- recovery procedure.

### Configuration

- infrastructure configuration,
- deployment configuration,
- non-secret configuration.

Secrets remain managed through the secret system.

---

# 52. Restore Testing

A backup that has never been restored is not a verified recovery mechanism.

Periodic restore testing should validate:

```text
Database restore
Object recovery
Application startup
Migration compatibility
RAG rebuild
Critical workflow recovery
```

---

# 53. Disaster Recovery Priorities

Priority order:

```text
1. Database availability/recovery
2. API recovery
3. Object storage availability
4. Worker recovery
5. Authentication
6. AI provider gateway
7. RAG rebuild
8. Non-critical integrations
```

Exact RTO/RPO targets are deployment decisions and should be established based on actual operational requirements.

---

# 54. Dependency Failure Isolation

A failure in one dependency must not unnecessarily destroy the whole platform.

Examples:

### Email unavailable

Core project functionality continues.

### GitHub unavailable

Project management continues; GitHub monitoring is degraded.

### Tavily unavailable

AI workflows requiring current research may degrade/fail safely; deterministic functionality continues.

### AI provider unavailable

AI features degrade; deterministic project state remains usable.

### RAG unavailable

AI retrieval degrades; canonical documents remain available.

---

# 55. AI Provider Failure

When all five provider keys are unavailable:

```text
AI Request
   ↓
Gateway
   ↓
No usable key
   ↓
QUOTA_EXHAUSTED / PROVIDER_UNAVAILABLE
```

The system must stop unauthorized retry loops.

Core application functionality must continue where possible.

---

# 56. Worker Failure

If a worker crashes:

```text
Job remains recoverable
      ↓
Retry / reconciliation
      ↓
Execution resumes or fails safely
```

Important work must not exist only in worker memory.

---

# 57. Object Storage Failure

If object storage is unavailable:

- new uploads may be rejected or queued,
- existing DB-only workflows may continue,
- document access may degrade,
- RAG processing should pause safely.

The system must avoid corrupting document metadata.

---

# 58. Deployment and Observability

Every deployment should expose safe metadata:

```text
application version
commit/build identifier
environment
deployment timestamp
worker version
migration version
```

Observability should allow operators to correlate failures with deployments.

---

# 59. Deployment Logging

Deployment logs should include:

- deployment start/end,
- build result,
- migration result,
- startup result,
- health result,
- rollback result.

Never include secret values.

---

# 60. Runtime Monitoring

Production monitoring should cover:

```text
API
Database
Workers
Outbox
Jobs
AI
RAG
Storage
GitHub
Tavily
Email
Security
```

Detailed observability requirements are defined in 6J.

---

# 61. Security Runtime Boundary

Production deployment must enforce:

- HTTPS,
- secret isolation,
- least privilege,
- private database/storage access,
- secure CORS,
- rate limiting,
- secure headers,
- resource limits,
- controlled outbound requests,
- secure container/runtime configuration.

6M remains the authoritative infrastructure-security specification.

---

# 62. File and Storage Runtime

Object storage should remain externally durable.

Workers may use ephemeral scratch storage for:

- parsing,
- scanning,
- extraction,
- exports.

Scratch storage must have:

- capacity limits,
- cleanup,
- isolation,
- no assumption of persistence.

6K defines the canonical storage architecture.

---

# 63. RAG Runtime

RAG processing should run through worker infrastructure.

Conceptually:

```text
Document Ready
     ↓
RAG Job
     ↓
Parse / Chunk
     ↓
Embed
     ↓
Index
     ↓
Ready
```

RAG failures must not corrupt canonical document state.

---

# 64. AI Runtime

AI workloads run through:

```text
Worker
   ↓
LangGraph
   ↓
Agent
   ↓
Tool
   ↓
AI Provider Gateway
   ↓
Provider
```

The gateway remains responsible for provider/key/model policies.

---

# 65. Runtime Authorization Revalidation

Background jobs must not blindly trust authorization from job creation time.

Where a job accesses protected resources, the worker should revalidate relevant authorization/resource state before sensitive operations.

Examples:

- document processing,
- AI retrieval,
- controlled investigation,
- project-change execution.

---

# 66. Stale Version Protection

Workers must verify expected resource versions before committing sensitive AI-generated or derived results.

Example:

```text
AI Execution started against Version 4
        ↓
Project changes to Version 5
        ↓
Worker finishes
        ↓
Version mismatch
        ↓
Reject stale result
```

This prevents outdated AI output from overwriting newer state.

---

# 67. Deployment of AI Workflows

AI workflow changes should be deployed with additional validation because changes may affect:

- model behavior,
- prompts,
- tools,
- agents,
- QA,
- RAG,
- provider selection.

Regression evaluation should occur before production rollout where appropriate.

---

# 68. Deployment of RAG Changes

RAG changes should consider:

- parser behavior,
- chunking,
- embedding model,
- metadata,
- retrieval filters,
- project isolation.

Embedding-model changes may require background reindexing rather than blocking deployment.

---

# 69. External Integration Configuration

Production integration credentials must be isolated per environment.

Examples:

```text
Development GitHub OAuth
Staging GitHub OAuth
Production GitHub OAuth
```

Do not accidentally share callback URLs or credentials across environments.

---

# 70. OAuth Deployment

OAuth configuration must include environment-specific:

- client IDs,
- redirect URIs,
- allowed origins,
- provider settings.

Redirect URIs must be exact and controlled.

---

# 71. Domain and DNS

Production deployment should use stable domains for:

```text
Frontend
API
OAuth callbacks where applicable
```

DNS and certificate management should be handled through the selected deployment platform/provider.

---

# 72. Environment Separation

At minimum, separate:

```text
Database
Storage
AI credentials
OAuth credentials
External integration configuration
Observability configuration
```

between production and non-production environments.

---

# 73. Development Convenience vs Production Security

Development may use relaxed settings where safe.

Production must not inherit:

- debug mode,
- permissive CORS,
- verbose private logs,
- test credentials,
- development OAuth redirects,
- local filesystem assumptions.

---

# 74. Runtime Resource Governance

Resource controls should protect against:

- oversized uploads,
- runaway AI workflows,
- infinite retries,
- excessive RAG jobs,
- unbounded exports,
- worker starvation,
- DB connection exhaustion.

Every expensive operation should have bounded behavior.

---

# 75. Timeout Architecture

Timeouts should exist at appropriate levels:

```text
HTTP request timeout
Database timeout
Storage timeout
AI provider timeout
Agent execution timeout
Job timeout
External API timeout
Export timeout
```

Timeouts should be explicit and observable.

---

# 76. Retry Architecture

Retries belong primarily to worker/external-operation boundaries.

Use:

```text
bounded retries
exponential backoff
jitter
```

Do not retry:

- permanent validation errors,
- authorization failures,
- malformed requests,
- known non-retryable provider errors.

---

# 77. Runtime Idempotency

Production runtime must assume retries and duplicate delivery can happen.

Therefore:

- jobs are idempotent,
- event handlers are idempotent,
- document processing is idempotent,
- RAG indexing is idempotent,
- notifications avoid duplicate delivery where required,
- integration synchronization uses checkpoints.

---

# 78. Operational Access

Operational access should use controlled administrative mechanisms.

Do not expose:

- direct production database credentials,
- object-storage master credentials,
- AI provider keys,
- worker internals

to normal application users.

Admin UI is not equivalent to infrastructure shell access.

---

# 79. Production Data Access

Production data access should be:

- authenticated,
- authorized,
- minimized,
- auditable where required.

The Admin application remains metadata-first and follows controlled investigation for deeper private content.

---

# 80. Deployment Testing Matrix

Before production:

| Area | Verification |
|---|---|
| API | Build + unit + integration + smoke |
| DB | Migration + constraints + RLS |
| Auth | Login + authorization |
| AI | Provider gateway + structured outputs |
| Agents | Workflow + QA |
| RAG | Ingestion + retrieval |
| Storage | Upload + download + lifecycle |
| Workers | Job execution + retry |
| Events | Outbox + handlers |
| Integrations | Safe connectivity |
| Observability | Logs + metrics + traces |
| Security | Security test suite |
| Runtime | Startup + readiness |
| Recovery | Backup/restore validation |

---

# 81. Deployment Pipeline

Recommended pipeline:

```text
Git Commit
    ↓
Static Checks
    ↓
Unit Tests
    ↓
Integration Tests
    ↓
Security Checks
    ↓
AI Evaluation / Regression where relevant
    ↓
Build Artifact
    ↓
Staging Deploy
    ↓
Smoke / Health Tests
    ↓
Production Approval
    ↓
Production Deploy
    ↓
Migration
    ↓
Health Verification
    ↓
Post-Deploy Monitoring
```

Exact CI/CD provider is not architecturally fixed.

---

# 82. Production Verification Window

After deployment, monitor:

```text
5xx rate
latency
DB health
worker queue
AI failure rate
RAG failures
storage errors
integration failures
security events
```

The system should be considered successfully deployed only after health verification passes.

---

# 83. Incident Response

When a production incident occurs:

```text
Detect
 ↓
Classify
 ↓
Contain
 ↓
Investigate
 ↓
Recover
 ↓
Verify
 ↓
Document
```

Observability from 6J supplies the telemetry.

Security incidents additionally follow 6M procedures.

---

# 84. Post-Incident Learning

Important incidents should produce:

- root-cause analysis,
- impact assessment,
- corrective actions,
- tests preventing recurrence,
- architecture review where necessary.

Do not immediately add infrastructure complexity unless the failure demonstrates a real need.

---

# 85. Deployment Documentation

Deployment documentation should include:

- environment setup,
- configuration reference,
- secret reference,
- database migration process,
- worker startup,
- storage setup,
- RAG setup,
- OAuth configuration,
- observability setup,
- backup/restore,
- rollback,
- incident procedures.

---

# 86. Final Runtime Architecture

```text
                           ┌──────────────────────┐
                           │      Frontend        │
                           │   Static/Web App     │
                           └──────────┬───────────┘
                                      │ HTTPS
                                      ▼
                           ┌──────────────────────┐
                           │  Load Balancer /     │
                           │  Managed Platform    │
                           └──────────┬───────────┘
                                      │
                           ┌──────────▼───────────┐
                           │   FastAPI API Pool   │
                           │      Stateless       │
                           └───────┬───────┬──────┘
                                   │       │
                      ┌────────────┘       └────────────┐
                      ▼                                 ▼
             ┌─────────────────┐              ┌──────────────────┐
             │   PostgreSQL    │              │  Object Storage  │
             │    / Supabase   │              │                  │
             └────────┬────────┘              └──────────────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Transactional   │
             │ Outbox / Events │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Background      │
             │ Worker Pool     │
             └───────┬─────────┘
                     │
       ┌─────────────┼──────────────────┐
       │             │                  │
       ▼             ▼                  ▼
   AI Runtime      RAG Runtime      Integrations
       │             │                  │
       ▼             ▼          ┌───────┼────────┐
   Provider       pgvector       │ GitHub│Tavily │
   Gateway                       │ Email │ OAuth │
                                 └───────┴────────┘

                 ┌───────────────────────────┐
                 │       Observability       │
                 │ Logs / Metrics / Traces   │
                 │ AI Evaluation / Audit    │
                 └───────────────────────────┘
```

---

# 87. Final Decision Summary

| Area | Frozen Decision |
|---|---|
| Architecture | Modular monolith |
| API runtime | FastAPI / ASGI |
| Worker runtime | Separate worker processes |
| Frontend | Separate client deployment |
| Canonical DB | PostgreSQL / Supabase |
| Object storage | Managed object storage |
| Vector storage | PostgreSQL + pgvector direction |
| Runtime state | Persisted |
| API scaling | Horizontally scalable |
| Worker scaling | Bounded/configurable |
| API/worker separation | Required |
| Long-running work | Async |
| Streaming | SSE |
| Configuration | Central typed settings |
| Secrets | Managed/injected |
| Database migrations | Version-controlled |
| Deployment | Automated pipeline |
| Containers | Supported/preferred where appropriate |
| Resource limits | Required |
| Autoscaling | Optional/controlled |
| AI scaling | Provider-aware |
| RAG scaling | Worker/concurrency controlled |
| Backups | Required |
| Restore testing | Required |
| Rollback | Application rollback + forward-compatible DB strategy |
| Health | Liveness + readiness + dependency health |
| Observability | 6J |
| Storage | 6K |
| Security | 6M |
| Complexity | Minimal necessary |

---

# 88. Explicit Non-Goals

GrowFlow deployment architecture does **not** introduce:

- Kubernetes by default,
- service mesh,
- microservices,
- Kafka,
- RabbitMQ,
- multi-region infrastructure by default,
- custom container orchestration,
- custom CDN,
- custom database cluster,
- custom object storage,
- custom observability platform,
- active-active multi-region deployment,
- unnecessary blue/green infrastructure,
- unnecessary canary infrastructure,
- server-side frontend secrets,
- direct public database access,
- unbounded autoscaling,
- uncontrolled worker concurrency,
- infrastructure complexity without demonstrated need.

---

# 89. Relationship to Phase 6

## 6A — Backend Architecture

Defines the modular monolith and runtime/application boundaries.

## 6B — Database Architecture

Defines PostgreSQL, migrations, RLS, persistence, and database runtime requirements.

## 6C — API Architecture

Defines API behavior, SSE, long-running operations, and HTTP boundaries.

## 6D — Authentication & Security

Defines runtime authentication, authorization, secrets, and security requirements.

## 6E — AI Provider Gateway

Defines provider/key/model runtime policies.

## 6F — Agent Execution Infrastructure

Defines LangGraph execution, workers, agents, tools, QA, and recovery.

## 6G — RAG & Document Intelligence

Defines RAG processing and vector infrastructure.

## 6H — Events, Jobs & Reliability

Defines workers, transactional outbox, retries, reconciliation, and reliability.

## 6I — External Integrations

Defines GitHub, Tavily, OAuth, email, and external adapter runtime requirements.

## 6J — Observability

Defines logs, metrics, traces, AI evaluation, health, and monitoring.

## 6K — Storage & File Architecture

Defines object storage, file processing, uploads, downloads, lifecycle, and recovery.

## 6M — Infrastructure Security

Defines infrastructure hardening, TLS, network security, secret protection, and runtime security.

## 6N — Backend Architecture Finalization

Will consolidate all Phase 6 architectural decisions into the final backend architecture.

---

# 90. Final Deployment Invariants

1. Production configuration is isolated from development.
2. Production secrets never enter source control.
3. API processes remain stateless.
4. Long-running workloads execute asynchronously.
5. Worker concurrency is bounded.
6. Database connections are bounded.
7. AI concurrency respects provider limits.
8. RAG workloads cannot starve core API capacity.
9. Canonical state remains in PostgreSQL.
10. Object storage remains behind a controlled service boundary.
11. Temporary worker storage is not canonical.
12. Migrations are version-controlled.
13. Destructive schema changes are controlled.
14. Deployments are observable.
15. Health is verified after deployment.
16. Application rollback is supported.
17. Database recovery relies on safe migration/recovery strategies.
18. Backups are tested through restoration.
19. External dependency failure is isolated where possible.
20. Security boundaries remain active in every environment.
21. Background jobs revalidate sensitive authorization/state where required.
22. Stale AI results cannot overwrite newer state.
23. Observability remains privacy-safe.
24. Infrastructure complexity is introduced only when justified by actual requirements.

---

# 91. Freeze Statement

This document is the **FINAL and ARCHITECTURALLY FROZEN specification for GrowFlow Phase 6L — Deployment, Infrastructure & Runtime Architecture**.

It supersedes the earlier numbering of the previously prepared deployment document and establishes its correct canonical position as **6L**.

It is intended to be consumed by:

- backend implementation,
- frontend deployment,
- database operations,
- AI infrastructure,
- agent execution,
- RAG,
- storage,
- external integrations,
- observability,
- security,
- CI/CD,
- testing,
- operations,
- final backend architecture finalization.

No implementation should invent a parallel deployment or runtime architecture.

Any future change must be treated as an explicit architectural change and evaluated against:

- reliability,
- security,
- scalability,
- cost,
- recoverability,
- operational simplicity,
- consistency with the canonical GrowFlow architecture.

**Status: FROZEN.**
