# Gate 08 — Assessment System

## Objective
Implement frozen assessment lifecycle: questions/definitions, persistence, adaptive behavior if specified, completion, validation, and student experience.

## Prerequisites / relevant Phase 1–6 docs
Gate 07 accepted. Read assessment product docs, 6A–6D, 6H if applicable, 6C, and testing/QA.

## Exact scope / implementation units
1. Implement frozen definition/session/response/progress/completion/version models. 2. Implement server assessment orchestration and defined branching. 3. Expose save/resume/submit/result contracts and matching UI. 4. Persist frozen downstream events only. 5. Test partial resume, branching, validation, immutability, authorization, versions.

## Expected modules/files / dependencies
Assessment domain/migrations/repos/services/routes/schemas, student features, events, fixtures/E2E tests. Depends on student project context.

## DB / API / frontend / AI changes
Frozen assessment resources only. AI: no model call; only frozen inputs/events for later use.

## Security / testing / validation / recovery
Isolate by project/role, validate server-side, protect answers, audit completion as frozen. Recover save with idempotency/concurrency and clear resume state; do not silently alter submitted answers.

## Git / exclusions / checklist / next
Commit data model, service/API, UI/tests coherently. Excluded: blueprint generation, planning, RAG, connectors.
- [ ] Assessment starts, resumes, validates, completes.
- [ ] Branching/version/ownership cases pass.
- [ ] Evidence, commit, push recorded.

Allowed next gate: **Gate 09 only**.
