# Gate 12 — External Integrations
## Objective
Add only frozen connectors through secure, asynchronous, observable, recoverable flows.
## Prerequisites / relevant Phase 1–6 docs
Gate 11 accepted; read 6I, 6E where relevant, 6H, 6D, 6J, 6L and connector contracts.
## Exact scope / units
Approved adapter/interface/config; authorized connect/status/sync/action APIs/UI; webhook/polling/outbox/idempotency/rate-limit/retry/DLQ/reconcile; mocks/contracts/failure tests.
## Expected modules / dependencies
Per-provider adapters/config/schemas/jobs, API/UI, webhook, telemetry/audit, tests; depends on security/events/observability.
## DB / API / frontend / AI
Frozen connection/sync states and approved features only; AI may use only 6E/6F-authorized integration.
## Security / test / validation / recovery
Scoped encrypted credentials, webhook verification, consent/redaction; test outage/rate-limit/duplicate/partial sync. Disable safely and reconcile; never replay irreversible effect blindly.
## Git / exclusions / checklist / next
Commit one connector/interface unit at a time. Excluded: new providers, mentor/admin beyond shared primitives.
- [ ] Each connector is frozen, isolated, authorized, recoverable.
- [ ] Evidence, commit, push recorded.
Allowed next gate: **Gate 13 only**.
