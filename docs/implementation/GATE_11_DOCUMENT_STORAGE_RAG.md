# Gate 11 — Documents + Storage + RAG
## Objective
Implement frozen document lifecycle, storage, ingestion/indexing, project-isolated retrieval, citations/provenance and UI.
## Prerequisites / relevant Phase 1–6 docs
Gate 10 accepted; read 6G, 6K, 6B, 6D, 6H, 6C, 6J and document product docs.
## Exact scope / units
Metadata/status/version/deletion and secure storage keys; authorized document APIs/UI; parse/chunk/embed/index/reindex/delete/reconcile jobs; filtered retrieval/citations; lifecycle/failure/isolation tests.
## Expected modules / dependencies
Document domain/migrations, storage/parser/retrieval adapters, workers, API/UI, telemetry/tests; depends on project, identity, workers, approved services.
## DB / API / frontend / AI
Frozen metadata/vector structures and document/retrieval contracts; AI retrieval only within frozen RAG boundary.
## Security / test / validation / recovery
Authorized scoped keys, validation, retention/encryption policy; prove object/metadata and cross-project negatives. Idempotent jobs, quarantine/DLQ, reconciliation, staged delete.
## Git / exclusions / checklist / next
Commit lifecycle/storage, pipeline, retrieval/UI/tests separately. Excluded: connectors, mentor/admin.
- [ ] Authorized lifecycle and isolated cited retrieval pass.
- [ ] Evidence, commit, push recorded.
Allowed next gate: **Gate 12 only**.
