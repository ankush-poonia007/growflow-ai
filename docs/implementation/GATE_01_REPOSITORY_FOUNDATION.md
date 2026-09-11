# Gate 01 — Repository & Folder Structure

## Objective
Establish the frozen repository layout, developer controls, and documentation boundary; do not build product behavior.

## Prerequisites and sources
Gate 00 accepted. Read the actual paths in its source map for the repository/codebase plan, Phase 6A, 6L, testing/QA, and source-of-truth hierarchy.

## Scope and units
1. Create only approved top-level backend, frontend, shared/configuration, test, operational, and documentation layout. 2. Add prescribed dependency manifests, ignore rules, sanitized environment example, README, format/lint/type/test controls. 3. Add the frozen CI validation skeleton if defined. 4. Document module/import/ownership boundaries.

## Expected files, dependencies, and changes
Expected: repository metadata, README, ignore/environment template, manifests/lockfiles, tooling config, documented tree and test roots under names prescribed by source docs. Depends on Gate 00 tooling. **DB/API/frontend/AI:** no feature schemas, routes, UI, providers, agents, or RAG; only approved empty layout.

## Security, testing, validation, recovery
Protect secrets/local state in ignore rules; pin dependencies as specified. Prove a clean checkout can install and run foundation checks. Revert a focused configuration commit on failure; escalate tool conflicts rather than substituting architecture.

## Git, exclusions, completion, next
Commit layout/tooling in reviewable units and push only passing changes. Excluded: application behavior, migrations, auth, UI design, deployment.
- [ ] Approved tree and boundaries documented.
- [ ] Sanitized configuration/ignore policy verified.
- [ ] Clean foundation checks pass; evidence, commit, push recorded.

Allowed next gate: **Gate 02 only**.
