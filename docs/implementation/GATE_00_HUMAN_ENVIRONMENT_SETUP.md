# Gate 00 — Human / Environment Setup

## Objective

Prepare the human-owned accounts, local tooling, secrets access, and documentation map needed to begin safely. This gate creates no application code, database, frontend, API, infrastructure, or deployment configuration.

## Why / prerequisites / sources

There is no prior implementation gate. Read the Phase 6 final consolidation, deployment/runtime, infrastructure-security, testing/QA, and repository/toolchain decisions; also index the relevant Phase 1–5 product and role-flow documents. Record their actual paths and versions in the gate evidence.

## Exact scope and units

1. Confirm the repository owner, protected branch workflow, issue/decision owner, and GitHub access.
2. Confirm approved local runtimes, package managers, database/service access, formatter/linter/test tooling, and browser support from frozen documentation.
3. Obtain secrets through the approved secret manager; verify only that access works. Create a local, ignored environment file only if the frozen setup requires it—never place values in docs or Git.
4. Create and validate the authoritative Phase 1–6 source map; identify any missing or contradictory source before code begins. Gate 00 is the only gate that creates this map.
5. Run only non-product readiness checks specified by the frozen toolchain; record versions and results.

## Expected files/modules and dependencies

Expected output is a gate evidence record and, if already prescribed by the frozen repository policy, ignored local configuration. No source modules are expected. Dependencies are human access to source documents, GitHub, approved service accounts, and local tooling.

## DB / API / frontend / AI changes

None. Do not create schemas, endpoints, UI shells, prompts, models, agents, keys, or providers.

## Security and testing

Use least privilege, MFA/approved access, secret-manager delivery, and redacted evidence. Test access and tool availability without printing secrets. Treat a missing secret, account, source document, or version mismatch as a blocker.

## Validation and recovery

Accept only when the source map is complete, required accounts/tools are available, secrets are not exposed, and the human owner signs off on unresolved decisions. On failure, revoke/rotate any accidentally exposed credential, remove only the local accidental artifact through the approved recovery process, log the gap, and stop.

## Git / exclusions / completion / next gate

Commit only an approved, non-secret readiness record if the repository policy requires it; otherwise no commit or push is expected. Excluded: all implementation work and architectural changes.

- [ ] Authoritative source map is created, validated, and lists actual paths; Gate 01 may now rely on it.
- [ ] Tooling and access are verified without secrets in Git.
- [ ] Blockers are resolved or formally escalated.
- [ ] Evidence is recorded and any required commit/push is complete.

Allowed next gate: **Gate 01 only**.
