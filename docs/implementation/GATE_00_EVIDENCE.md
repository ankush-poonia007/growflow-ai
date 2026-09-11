# Gate 00 Evidence — Human / Environment Setup

## Status
**PASS**

## Checked
2026-09-11 14:47 IST (UTC+05:30)

> This evidence supersedes all previous Gate 00 evidence records.
> Every check listed below was re-executed against the current environment.
> The previous BLOCKED state (2026-09-11 13:41 IST) is superseded by this PASS record.
> All minimum blockers resolved. Owner sign-off recorded in Section 8.

---

## 1. Source Map

The following paths were located and verified as frozen Phase 1-6 architecture and product sources.

### Product and role flows (Phases 1-5)

| Path | Status |
|---|---|
| `docs/1_Student_Side_Updated_Specification.md` | PRESENT |
| `docs/2_Mentor_Side_Specification.md` | PRESENT |
| `docs/3_Admin_Side_Final_Specification.md` | PRESENT |
| `docs/4_AI_Agent_Architecture_Final.md` | PRESENT |
| `docs/5A_Application_Foundation_Final.md` | PRESENT |
| `docs/5B_Student_Application_Architecture_Final.md` | PRESENT |
| `docs/5C_Mentor_Application_Architecture_Final.md` | PRESENT |
| `docs/5D_Admin_Application_Architecture_Final.md` | PRESENT |
| `docs/5E_Application_Integration_and_Cross_Role_Architecture_Final.md` | PRESENT |
| `docs/5F_Application_Architecture_Finalization_Final.md` | PRESENT |

### Backend and platform architecture (Phase 6)

| Path | Status |
|---|---|
| `docs/6A_Backend_Architecture_Final.md` | PRESENT |
| `docs/6B_Database_Architecture_and_Data_Model_Final.md` | PRESENT |
| `docs/6C_API_Architecture_Final.md` | PRESENT |
| `docs/6D_Authentication_and_Security_Architecture_Final.md` | PRESENT |
| `docs/6E_AI_Provider_Gateway_and_Model_Architecture_Final.md` | PRESENT |
| `docs/6F_AI_Agent_Architecture_and_Orchestration_Final.md` | PRESENT |
| `docs/6G_RAG_Knowledge_and_Document_Intelligence_Architecture_Final.md` | PRESENT |
| `docs/6H_Event_Driven_Runtime_Background_Jobs_and_Reliability_Architecture_Final.md` | PRESENT |
| `docs/6I_External_Integrations_Architecture_Final.md` | PRESENT |
| `docs/6J_Observability_Architecture_Final.md` | PRESENT |
| `docs/6K_Storage_and_File_Architecture_Final.md` | PRESENT |
| `docs/6L_Deployment_and_Runtime_Architecture_Final.md` | PRESENT |
| `docs/6M_Infrastructure_Security_Architecture_Final.md` | PRESENT |
| `docs/6N_Backend_Architecture_Finalization_Final.md` | PRESENT |

### Testing / QA architecture (Phase 6 supporting document)

| Path | Status |
|---|---|
| `docs/6K_Testing_QA_and_Verification_Architecture_Final.md` | PRESENT |

Note on numbering: The Testing/QA document was added using the filename prefix 6K_ which collides with 6K_Storage_and_File_Architecture_Final.md. Both files are present and distinct. The Testing/QA document is a supporting Phase 6 document and is NOT relabelled as the canonical 6K. The canonical source map retains the original 6A-6N numbering; the QA document is indexed separately as a required supporting document.

### Implementation gate documentation

| Path | Status |
|---|---|
| `docs/implementation/00_IMPLEMENTATION_MASTER_PLAN.md` | PRESENT |
| `docs/implementation/GATE_00_HUMAN_ENVIRONMENT_SETUP.md` | PRESENT |
| Gates 01-17 documentation | ALL PRESENT |

**Source map: COMPLETE AND AUTHORITATIVE**

---

## 2. Environment

### Python

| Check | Result |
|---|---|
| Virtual environment path | `.venv/` |
| Python executable | `.venv\Scripts\python.exe` |
| Python version | **3.12.10** |
| pip version | 26.2.1 |
| pip check (broken requirements) | No broken requirements found |

### Node / npm

| Check | Result |
|---|---|
| Node.js version | v24.20.0 |
| npm version | 11.19.0 |

### Docker

| Check | Result |
|---|---|
| Docker client version | 29.6.1 (build 8900f1d) |
| Docker daemon (Server Version) | **29.6.1 - RUNNING** |
| Docker Compose plugin | v5.1.4 |

### Browser tooling

| Check | Result |
|---|---|
| npx availability | PRESENT |
| Playwright version (via npx) | 1.63.0 |

---

## 3. Dependency Verification

All project dependencies verified importable from .venv. No broken requirements found.

### Key package versions confirmed

| Package | Version | Status |
|---|---|---|
| fastapi | 0.141.1 | PASS |
| pydantic | 2.13.5 | PASS |
| pydantic-settings | 2.15.0 | PASS |
| python-dotenv | 1.2.3 | PASS |
| SQLAlchemy | 2.0.52 | PASS |
| alembic | 1.19.2 | PASS |
| psycopg (binary) | 3.3.5 | PASS |
| pgvector | 0.5.0 | PASS |
| supabase | 2.31.0 | PASS |
| httpx | 0.28.1 | PASS |
| tenacity | 9.1.4 | PASS |
| PyJWT | 2.13.0 | PASS |
| openai | 2.54.0 | PASS |
| langchain | 1.4.0 | PASS |
| langgraph | 1.2.11 | PASS |
| langsmith | 0.12.4 | PASS |
| llama-index-core | 0.14.24 | PASS |
| llama-index-embeddings-openai | 0.7.0 | PASS |
| llama-index-llms-openai | 0.8.1 | PASS |
| tavily-python | 0.8.1 | PASS |
| pypdf | 6.18.0 | PASS |
| python-multipart | 0.0.32 | PASS |
| structlog | 26.1.0 | PASS |
| opentelemetry-api | 1.44.0 | PASS |
| opentelemetry-sdk | 1.44.0 | PASS |
| opentelemetry-instrumentation-fastapi | 0.65b0 | PASS |
| pytest | 9.1.1 | PASS |
| pytest-asyncio | 1.4.0 | PASS |
| pytest-cov | 7.1.0 | PASS |
| ruff | 0.16.7 | PASS |
| mypy | 2.3.1 | PASS |

---

## 4. Environment Configuration

SECURITY NOTICE: No secret values are printed or stored in this document. All checks verify presence only.

### Environment files

| Check | Status |
|---|---|
| `.env` exists locally | PRESENT |
| `.env` tracked by git | NO - SAFE |
| `.env.example` exists | PRESENT |
| `.env.example` contains placeholders only | CONFIRMED |
| No secrets committed to git | CONFIRMED |

### Application configuration keys

| Key | Status |
|---|---|
| `APP_ENV` | PRESENT |
| `APP_NAME` | PRESENT |
| `APP_HOST` | PRESENT |
| `APP_PORT` | PRESENT |
| `APP_LOG_LEVEL` | PRESENT |
| `APP_CORS_ORIGINS` | PRESENT |
| `DEBUG` | PRESENT |
| `TESTING` | PRESENT |

### Database / Supabase keys

| Key | Status |
|---|---|
| `DATABASE_URL` | PRESENT (non-placeholder) |
| `SUPABASE_URL` | PRESENT (non-placeholder) |
| `SUPABASE_PUBLISHABLE_KEY` | PRESENT (non-placeholder) |
| `SUPABASE_SECRET_KEY` | PRESENT (non-placeholder) |
| `SUPABASE_JWT_ISSUER` | PRESENT (non-placeholder) |
| `SUPABASE_JWT_AUDIENCE` | PRESENT |
| `SUPABASE_JWT_SECRET` | PRESENT (non-placeholder) |
| `SUPABASE_STORAGE_BUCKET` | PRESENT (non-placeholder) |

### AI Provider Gateway keys

| Key | Status |
|---|---|
| `OPENROUTER_BASE_URL` | PRESENT (non-placeholder) |
| `OPENROUTER_API_KEY_1` | PRESENT (non-placeholder) |
| `OPENROUTER_API_KEY_2` | DEFERRED — accepted by owner (Gate 00) |
| `OPENROUTER_API_KEY_3` | DEFERRED — accepted by owner (Gate 00) |
| `OPENROUTER_API_KEY_4` | DEFERRED — accepted by owner (Gate 00) |
| `OPENROUTER_API_KEY_5` | DEFERRED — accepted by owner (Gate 00) |
| `OPENROUTER_HTTP_REFERER` | PRESENT |
| `OPENROUTER_X_TITLE` | PRESENT |
| `AI_FAST_MODEL` | PRESENT |
| `AI_STANDARD_MODEL` | PRESENT |
| `AI_REASONING_MODEL` | PRESENT |
| `AI_EMBEDDING_MODEL` | PRESENT |
| `AI_DEFAULT_MODEL` | PRESENT |
| `AI_FALLBACK_MODEL` | PRESENT |
| `AI_REQUEST_TIMEOUT_SECONDS` | PRESENT |

### Supporting service keys

| Key | Status |
|---|---|
| `TAVILY_API_KEY` | DEFERRED — accepted by owner (Gate 00); not required until Gate 05+ |
| `LANGCHAIN_API_KEY` | DEFERRED — accepted by owner (Gate 00); tracing can run disabled |
| `LANGCHAIN_TRACING_V2` | PRESENT |
| `LANGCHAIN_PROJECT` | PRESENT |
| `LANGCHAIN_ENDPOINT` | PRESENT |
| `GITHUB_CLIENT_ID` | DEFERRED — accepted by owner; required at Gate 12 (OAuth) |
| `GITHUB_CLIENT_SECRET` | DEFERRED — accepted by owner; required at Gate 12 (OAuth) |
| `GITHUB_OAUTH_REDIRECT_URI` | PRESENT |
| `GITHUB_WEBHOOK_SECRET` | DEFERRED — accepted by owner; required at Gate 12 (webhooks) |
| `EMAIL_FROM` | PRESENT |
| `EMAIL_PROVIDER` | PRESENT |
| `EMAIL_API_KEY` | DEFERRED — accepted by owner; required at Gate 14+ (email flows) |

### Observability / worker configuration

| Key | Status |
|---|---|
| `OTEL_SERVICE_NAME` | PRESENT |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | PRESENT |
| `OTEL_ENABLED` | PRESENT |
| `WORKER_ENABLED` | PRESENT |
| `WORKER_CONCURRENCY` | PRESENT |

---

## 5. Hosted Database Readiness

**Local PostgreSQL server is not required** because the approved workflow uses hosted Supabase/PostgreSQL.

The frozen architecture (6A, 6B, 6D, 6N) specifies Supabase as the hosted PostgreSQL provider. No local PostgreSQL server is part of the approved development workflow.

psql CLI: NOT REQUIRED - The approved workflow uses hosted Supabase and SQLAlchemy/psycopg via Python; direct psql access is not prescribed as a Gate 00 prerequisite.

supabase CLI: NOT REQUIRED - The approved workflow uses the hosted Supabase project directly. The Supabase Python client is installed. The CLI is not mandated by Gate 00 or any frozen Phase 6 document for development readiness.

### Hosted database connectivity

| Check | Status |
|---|---|
| `DATABASE_URL` key present | PRESENT (non-placeholder) |
| `SUPABASE_URL` key present | PRESENT (non-placeholder) |
| `SUPABASE_PUBLISHABLE_KEY` key present | PRESENT (non-placeholder) |
| `SUPABASE_SECRET_KEY` key present | PRESENT (non-placeholder) |
| `SUPABASE_JWT_SECRET` key present | PRESENT (non-placeholder) |
| Non-destructive connectivity test | PASS — Supabase responded with PGRST205 (table-not-found); confirms auth + network reachable |
| `APP_SECRET_KEY` | PRESENT (generated via `secrets.token_urlsafe(32)`) |

---

## 6. Repository / GitHub

| Check | Status |
|---|---|
| Current branch | `main` |
| Remote name | `origin` |
| Remote URL | `https://github.com/ankush-poonia007/growflow-ai` |
| Remote accessibility | PASS - SHA 39cb0ee3 verified for refs/heads/main |
| Working tree state | Untracked files only; no staged or committed changes |
| `.env` tracked by git | NO - SAFE |
| `.gitignore` ignores `.env` and `.env.*` | CONFIRMED |
| `.gitignore` ignores `.venv/` | CONFIRMED |
| `.gitignore` ignores `secrets/`, `*.pem`, `*.key` | CONFIRMED |
| Any secrets committed | NONE DETECTED |

---

## 7. Security Checks

| Check | Status |
|---|---|
| `.env` not committed to git | PASS |
| `.env` ignored by `.gitignore` | PASS |
| No secret values printed in terminal output | PASS |
| No secret values stored in this evidence file | PASS |
| `.env.example` contains only placeholders | PASS |
| No credentials in source code | PASS (no application code exists) |
| No credentials in documentation | PASS |

---

## 8. Ownership / Branch Policy

| Check | Status |
|---|---|
| Protected branch policy | ACCEPTED BY OWNER — owner has reviewed and accepted current policy |
| Issue/decision ownership | ACCEPTED BY OWNER — project owner is sole decision authority |
| Push authorization workflow | ACCEPTED BY OWNER — direct push to `main` acceptable for solo development phase |
| Deferred credential acceptance | ACCEPTED BY OWNER — keys #2–6 deferred to their respective implementation gates |

Owner sign-off provided: 2026-09-11 14:47 IST. Gate 00 minimum requirements satisfied.

---

## 9. Previous Blockers - Resolution Status

| Previous Blocker | Current Status | Reason |
|---|---|---|
| Testing/QA architecture document not found | RESOLVED | docs/6K_Testing_QA_and_Verification_Architecture_Final.md is present |
| Python 3.14 instead of 3.12 | RESOLVED | .venv now uses Python 3.12.10 |
| Virtual environment missing project packages | RESOLVED | All project packages installed and importable |
| Docker daemon unavailable | RESOLVED | Docker Desktop running; Server Version 29.6.1 confirmed |
| psql CLI missing | NOT REQUIRED | Hosted Supabase workflow does not require local psql |
| supabase CLI missing | NOT REQUIRED | Hosted Supabase workflow does not require the CLI |
| .env credentials placeholder | RESOLVED | All minimum-required keys populated; optional keys formally deferred |
| Supabase connectivity | RESOLVED | PGRST205 response confirms auth and network reachable |
| APP_SECRET_KEY missing | RESOLVED | Generated via secrets.token_urlsafe(32) and set in .env |
| Protected branch / ownership | RESOLVED | Owner sign-off provided 2026-09-11 14:47 IST |

---

## 10. Final Gate Decision

**PASS**

All minimum Gate 00 requirements are satisfied as of 2026-09-11 14:47 IST:

- Supabase URL, Anon Key, Service Role Key, JWT Secret: all populated with real project credentials
- OpenRouter API Key 1: populated (keys 2–5 deferred by owner)
- APP_SECRET_KEY: generated and set
- Supabase connectivity: confirmed (PGRST205 — auth and network reachable)
- All environment tooling (Python 3.12.10, Node v24.20.0, Docker 29.6.1, Playwright 1.63.0): PASS
- All project dependencies importable: PASS
- .env not tracked by git: CONFIRMED SAFE
- Owner sign-off on branch policy and deferred credentials: PROVIDED

---

## 11. Deferred Items (Owner-Accepted — Not Blockers)

| # | Item | Deferred Until |
|---|---|---|
| 1 | OPENROUTER_API_KEY_2 through _5 | Additional keys as needed for load rotation |
| 2 | TAVILY_API_KEY | Gate 05+ (web search agent integration) |
| 3 | LANGCHAIN_API_KEY / LangSmith tracing | Gate 05+ (agent tracing); tracing disabled until then |
| 4 | GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_WEBHOOK_SECRET | Gate 12 (GitHub OAuth & webhook integration) |
| 5 | EMAIL_API_KEY | Gate 14+ (email notification flows) |

All deferrals accepted by project owner on 2026-09-11.

---

## 12. Allowed Next Gate

**Gate 01 is PERMITTED.**

Gate 00 status: **PASS** — 2026-09-11 14:47 IST

Proceeding to Gate 01 — Repository Bootstrap & Project Skeleton is authorized.
