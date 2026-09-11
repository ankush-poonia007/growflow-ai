# Gate 06 — Frontend Foundation + Stitch Integration

## Objective
Adapt approved Stitch output into the frozen frontend shell, with accessible responsive states and approved core contracts—without inventing workflows.

## Prerequisites / relevant Phase 1–6 docs
Gate 05 accepted. Read Phase 1–5 frontend/role flows, 6C API, 6D security, 6J observability, and approved Stitch assets; Stitch is input, not architecture authority.

## Exact scope / implementation units
1. Bootstrap approved frontend runtime, routing, layouts, tokens, asset/font policy and component boundaries. 2. Refactor approved Stitch screens into that shell. 3. Add navigation, accessibility, responsive/loading/empty/error/permission states, client config/API-auth boundary, telemetry. 4. Wire only approved Gate 05 contracts. 5. Test routes, accessibility, responsive states, auth and network errors.

## Expected modules/files / dependencies
App/router/layouts, design components/tokens, Stitch adaptation, API/auth client, state/query boundary, styles/assets, frontend tests. Depends on Gate 05 contracts and Stitch deliverables.

## DB / API / frontend / AI changes
DB: none. API: consume auth/core contracts only. Frontend: shell only. AI: none.

## Security / testing / validation / recovery
Keep tokens out of bundles/logs; enforce frozen CSP/CORS/session policies. Validate guest/auth/denied routes and failure states. Restore approved asset/adaptation revision on failure.

## Git / exclusions / checklist / next
Commit shell, design adaptation, client boundary in units. Excluded: student workflow, assessment, AI, planning, RAG, mentor/admin.
- [ ] Stitch conforms to frozen structure/design rules.
- [ ] Accessibility/shell states pass.
- [ ] Evidence, commit, push recorded.

Allowed next gate: **Gate 07 only**.
