# Gate 05 — Core Backend / Domain Foundation

## Objective
Build frozen profiles, project/workspace ownership, canonical domain services, and API contracts, excluding later systems.

## Prerequisites / relevant Phase 1–6 docs
Gate 04 accepted. Read Phase 1–5 student/product architecture and Gate 00-indexed 6A backend, 6B database, 6C API, 6D security, 6H events.

## Exact scope / implementation units
1. Implement frozen entities, migrations, repositories, services, validation. 2. Implement defined ownership/state transitions. 3. Expose authorized contract-tested profile/project/workspace APIs. 4. Emit only frozen outbox/domain events. 5. Test rules, contracts, transactions, ownership, events.

## Expected modules/files / dependencies
Core models/schemas/migrations/repos/services/routes/contracts/events and layered tests, under Gate 01 layout. Depends on Gates 02–04.

## DB / API / frontend / AI changes
DB/API: frozen core resources only. Frontend: no production feature integration. AI: none.

## Security / testing / validation / recovery
Enforce service/data-layer ownership and test idempotency/state changes. Use additive/forward migrations and reconciliation; never delete user data to repair failure.

## Git / exclusions / checklist / next
Commit coherent resource lifecycles and tests. Excluded: assessment, blueprint, planning, RAG, integrations, mentor/admin.
- [ ] Lifecycle and ownership match frozen sources.
- [ ] Contracts, constraints, RLS, events are tested.
- [ ] Evidence, commit, and push are recorded.

Allowed next gate: **Gate 06 only**.
