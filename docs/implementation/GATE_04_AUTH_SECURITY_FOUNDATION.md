# Gate 04 — Authentication & Security Foundation

## Objective
Implement frozen identity, session/token verification, authorization, resource access, and security boundaries.

## Prerequisites / relevant Phase 1–6 docs
Gate 03 accepted. Read Gate 00-indexed 6D Auth/Security, 6B RLS, 6C API, 6M infrastructure security, 6L runtime, and Phase 1–5 role flows.

## Exact scope / implementation units
1. Integrate approved identity and verification boundary. 2. Map frozen claims to identity/role context; create no roles. 3. Centralize route/resource authorization aligned with RLS. 4. Apply frozen CORS, CSRF/session, rate-limit, validation, audit, and secret rules. 5. Test anonymous, invalid/expired, cross-role, and cross-resource denial/allowed cases.

## Expected modules/files / dependencies
Identity adapter, auth middleware, authorization policy/service, request context, audit/security utilities, API/policy tests. Depends on Gate 03 and approved identity configuration.

## DB / API / frontend / AI changes
DB: identity-to-application-subject linkage and frozen authorization/RLS policy primitives only. This linkage must not create, populate, or implement the user-profile domain; profile attributes, lifecycle, and project-domain ownership begin in Gate 05. API: frozen auth/current-user/protected boundary only. Frontend/AI: none.

## Security / testing / validation / recovery
Verify issuer/audience/signature/expiry; fail closed and never trust client roles. Validate route/resource/data authorization agreement. Rotate via secret manager and restore validated policy on failure.

## Git / exclusions / checklist / next
Commit provider boundary, policies, and tests in focused sets. Excluded: profile-domain implementation, project behavior, AI execution, mentor/admin, UI design unless frozen here.
- [ ] Identity is server-verified.
- [ ] Authorization agreement and negatives pass.
- [ ] Evidence, commit, and push are recorded.

Allowed next gate: **Gate 05 only**.
