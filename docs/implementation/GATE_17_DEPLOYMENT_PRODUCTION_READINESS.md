# Gate 17 — Deployment & Production Readiness
## Objective
Verify the production environment, rehearse the frozen build/migration/rollback procedure, perform the staged release, and complete smoke, monitoring, and operational handoff. Gate 17 consumes Gate 16's release evidence; only this gate may release after explicit approval.
## Prerequisites / relevant Phase 1–6 docs
Gate 16 accepted plus designated-owner approval. Read 6L, 6M, 6J, 6H, testing/QA criteria and Gate 16 report.
## Exact scope / units
Verify parity/secrets/identity/network/backups/capacity/alerts/runbooks; build/version/sign frozen artifacts; rehearse migration/rollback pre-production; deploy through defined pipeline and run health/migration/smoke/authorization/journey/worker/integration checks; stabilization monitoring/handoff.
## Expected modules / dependencies
Frozen manifests/pipeline/runbooks/environment templates/release evidence only; depends on approval, environments, rollback capability.
## DB / API / frontend / AI
No features: approved artifacts/config and versioned migrations only.
## Security / test / validation / recovery
Least privilege, secret manager, verified artifacts, audit and data safeguards; validate restores/alarms/flags. Halt rollout and use frozen rollback/forward plan on failed smoke/SLO/security signal.
## Git / exclusions / checklist / final state
Tag/release/commit/push only through approved protection. Excluded: post-release features or undocumented environment changes.
- [ ] Approval, rehearsal, secure deploy, smoke and stabilization pass.
- [ ] Release evidence/tag/push and handoff recorded.
Allowed next state: **GrowFlow V1 production operation**.
