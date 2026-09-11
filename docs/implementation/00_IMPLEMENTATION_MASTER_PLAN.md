# GrowFlow Phase 7 — Implementation Master Plan

## Purpose and authority

This plan turns the frozen Phase 1–6 architecture into a controlled build sequence. It is an orchestration document, not a redesign or substitute for the architecture. Where this plan and a frozen Phase 1–6 document differ, the frozen document wins; stop and reconcile the plan before implementing.

**Execution invariant:** one gate at a time: read its source map, implement only its units, run its checks, record evidence, commit, push, then open the allowed next gate. A gate is complete only when it is implemented, tested, validated, documented, committed, and pushed.

## Required source map

Gate 00 creates and validates a read-only index of the actual repository paths for the following frozen sources. Do not rewrite them: product scope and role flows (Phases 1–5); Phase 6 final consolidation; backend, database, API, auth/security, AI gateway, agents, RAG, workers/events, integrations, observability, storage, deployment/runtime, and infrastructure-security documents (6A–6M); and the testing/QA architecture. Gate 01 and every later gate must use this validated map and name the exact paths consulted in its implementation record.

## Gate flow

| Gate | Focus | Depends on | Completion output | May open |
|---|---|---:|---|---|
| 00 | Human/environment setup | — | verified local readiness, source index | 01 |
| 01 | Repository foundation | 00 | agreed code/document layout and controls | 02 |
| 02 | Backend foundation | 01 | runnable service foundation | 03 |
| 03 | Database foundation | 02 | migrations, access foundation, testable data layer | 04 |
| 04 | Authentication/security | 03 | authenticated, authorized boundary | 05 |
| 05 | Core backend domain | 04 | project/profile/domain backbone | 06 |
| 06 | Frontend foundation + Stitch integration | 05 | usable shell and contract-ready UI | 07 |
| 07 | Student core flow | 06 | end-to-end student project flow | 08 |
| 08 | Assessment system | 07 | persisted, validated assessment flow | 09 |
| 09 | AI blueprint/agent system | 08 | governed blueprint generation | 10 |
| 10 | Planning/execution system | 09 | milestones/tasks/progress execution flow | 11 |
| 11 | Documents/storage/RAG | 10 | project-isolated document knowledge flow | 12 |
| 12 | External integrations | 11 | bounded, recoverable connectors | 13 |
| 13 | Mentor application | 12 | mentor workflows and authorization | 14 |
| 14 | Admin application + AI observatory | 13 | governed administrative operations | 15 |
| 15 | Observability/reliability/security hardening | 14 | measurable resilient system | 16 |
| 16 | Full-system verification | 15 | release evidence and defect disposition | 17 |
| 17 | Deployment/production readiness | 16 | deployable, rollback-ready release | V1 |

## Standard Antigravity execution protocol

1. Inspect the repository and the named frozen sources; quote the exact source paths in the gate record.
2. Confirm prerequisites and the previous gate’s evidence. If absent, stop rather than guessing.
3. Execute one implementation unit at a time. Do not add future features, placeholders, alternative architecture, or unrelated refactors.
4. Run the gate’s automated and manual checks. Fix only defects within the approved scope.
5. Update the gate evidence: changed files, commands/checks, results, known limitations, and source documents consulted.
6. Commit a focused change set using the gate/unit convention; push only after local validation and required review.

## Shared controls

- Never commit secrets, production data, credentials, generated local state, or unreviewed schema changes.
- Use the frozen contracts for role boundaries, data ownership, API behavior, AI governance, RAG isolation, events, and runtime operations.
- Any ambiguity, incompatible source, failed migration, security concern, or scope expansion is a **stop-and-escalate** event. Capture facts, restore the last known-good state, and request an architectural decision.
- No gate authorizes production deployment. Gate 17 alone authorizes the approved release procedure.

## Commit and push convention

Use small, reversible commits: `build(gate-XX): <verified unit>`; keep documentation/evidence in the same commit when it describes that change. Before pushing, verify the working tree contains only the gate scope, tests pass, and the commit references its evidence. Use the repository’s frozen branch/protection policy; do not bypass it.

## Definition of done

Every gate file supplies its detailed checklist. The master completion condition is: all gates have accepted evidence, all release-blocking issues are closed or formally deferred by the architecture owner, and the Gate 17 rollback-tested release procedure is accepted.
