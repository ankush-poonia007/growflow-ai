# Gate 07 — Student Core Flow

## Objective
Deliver the frozen student journey from authenticated profile/workspace through project creation and management using real contracts.

## Prerequisites / relevant Phase 1–6 docs
Gate 06 accepted. Read student Phase 1–5 flows and 6A–6D, 6C API, 6J observability, testing/QA.

## Exact scope / implementation units
1. Complete frozen core operations needed by student journey. 2. Build contract-backed pages/forms, route guards, navigation/states. 3. Wire server validation, authorization, events, approved notices. 4. Add E2E happy and validation/recovery paths.

## Expected modules/files / dependencies
Student UI features, core handlers/routes/contracts, frozen core-field migrations, event/notice adapters, unit/integration/E2E tests. Depends on Gates 04–06.

## DB / API / frontend / AI changes
Only frozen core-journey fields/contracts/screens. No assessment, AI, planning, RAG, mentor/admin, external connectors.

## Security / testing / validation / recovery
Test RLS/direct-object access, validation, duplicate/idempotent action and safe errors. Use frozen transaction/compensation rules and preserve user input on retry.

## Git / exclusions / checklist / next
Commit vertical slices with tests. Excluded: later product systems.
- [ ] Defined student journey works end-to-end.
- [ ] Authorization, failure states and E2E evidence pass.
- [ ] Evidence, commit, push recorded.

Allowed next gate: **Gate 08 only**.
