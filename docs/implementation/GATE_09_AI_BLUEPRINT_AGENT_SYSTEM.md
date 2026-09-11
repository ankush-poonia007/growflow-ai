# Gate 09 — AI Blueprint & Agent System
## Objective
Implement frozen provider gateway, agent contracts/orchestration, durable execution, QA/judge/regeneration, and student result flow.
## Prerequisites / relevant Phase 1–6 docs
Gate 08 accepted; read 6E AI gateway, 6F agents, 6C, 6D, 6H, 6J, 6L and blueprint specifications.
## Exact scope / units
Provider capability/key/pool/timeout/quotas; typed agent state/tools/context/graph; execution/provenance/jobs; QA/retry/cancel/regeneration/streaming; approved UI and mock-provider/contract/failure tests.
## Expected modules / dependencies
Gateway, agent graph/contracts/tools, jobs, execution migrations, status APIs/UI, foundational AI telemetry/tracing, and tests; depends on assessment, events, security, and the observability contracts already frozen in Phase 6.
## Observability boundary
Gate 09 implements only the telemetry/tracing required for safe AI execution: correlation and execution identifiers, provider/model usage and failure metadata, agent/workflow status, and privacy-safe trace linkage. It does not build the complete observability platform, dashboards, alerting, SLOs, or system-wide hardening; those are Gate 15 responsibilities.
## DB / API / frontend / AI
Frozen execution/blueprint/provenance records and initiate/status/stream/result contracts; only frozen providers/agents/tools.
## Security / test / validation / recovery
Authorize project/role/tools; redact/budget-limit/audit; prove no cross-project context. Use idempotent jobs, durable state, retry/DLQ/cancel/reconcile.
## Git / exclusions / checklist / next
Commit gateway, orchestration, persistence/UI/tests in units. Excluded: planning, RAG, connectors, mentor/admin.
- [ ] Governed durable blueprint path and failure states pass.
- [ ] Evidence, commit, push recorded.
Allowed next gate: **Gate 10 only**.
