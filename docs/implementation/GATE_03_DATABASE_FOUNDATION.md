# Gate 03 — Database Foundation

## Objective
Implement frozen connectivity, migrations, data-access, ownership, and isolation foundation.

## Prerequisites / relevant Phase 1–6 docs
Gate 02 accepted. Read the Gate 00 source map entries for 6B Database, 6D security/RLS, 6H workers/events, 6K storage, 6L runtime, and testing/QA.

## Exact scope / implementation units
1. Configure approved database connectivity, pooling, lifecycle, and migration tool. 2. Add only frozen foundation objects (extensions/enums/tenancy/audit primitives where specified) in compatible ordered migrations. 3. Establish repository/unit-of-work transaction and canonical ownership rules. 4. Add frozen RLS/policy scaffolding. 5. Test fresh/upgrade migrations, transactions, policies, and failure recovery.

## Expected modules/files / dependencies
Database adapter, migration directory, transaction/data-access utilities, policy definitions, fixtures, tests—under Gate 01 layout. Depends on Gate 02 and approved database access.

## DB / API / frontend / AI changes
DB: frozen foundations only; no feature entities unless frozen tenancy/security requires them. API/frontend/AI: none.

## Security / testing / validation / recovery
Least-privileged connections and parameterized access; prove allowed and denied policy cases. Validate clean and upgrade paths. On failure use the frozen forward-fix/restore procedure; never hand-edit production state.

## Git / exclusions / checklist / next
Commit migration and policy tests atomically; push after clean validation. Excluded: auth UI, domain features, production seeding.
- [ ] Fresh/upgrade migration and policy negatives pass.
- [ ] Transaction/test isolation works.
- [ ] Evidence, commit, and push are recorded.

Allowed next gate: **Gate 04 only**.
