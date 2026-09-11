# Gate 13 — Mentor Application
## Objective
Deliver frozen mentor role/workspace, assigned project visibility, review and communication actions, and authorized AI/document access. Mentor actions do not include direct mutation of a student's execution state.
## Prerequisites / relevant Phase 1–6 docs
Gate 12 accepted; read mentor Phase 1–5 architecture, 6A–6D, 6C, 6G, 6F, 6J and testing/QA.
## Exact scope / units
Frozen assignment relationships/policies; mentor dashboard, review, feedback, and communication APIs; mentor routes/screens/states; only frozen role-scoped AI/RAG access; assignment/privacy/audit/E2E tests. Direct creation, completion, reordering, or other mutation of student execution state is explicitly out of scope.
## Expected modules / dependencies
Mentor domain/policies/migrations/services/routes, UI, authorized AI/RAG wrappers, audit/events/tests; depends on core/planning/documents/integrations.
## DB / API / frontend / AI
Frozen mentor relationships/workflows only; AI/RAG reuses approved shared boundaries.
## Security / test / validation / recovery
Default deny outside assignment; audit sensitive views/actions; prove student/mentor/admin separation. Reconcile assignment changes without losing provenance.
## Git / exclusions / checklist / next
Commit vertical slices with access tests. Excluded: direct student execution-state mutation, admin control plane, new integrations.
- [ ] Defined assigned-project workflows and privacy tests pass.
- [ ] Evidence, commit, push recorded.
Allowed next gate: **Gate 14 only**.
