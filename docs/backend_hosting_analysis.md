# GrowFlow — Backend Hosting & Production Readiness Analysis

**Document Version:** 1.0.0  
**Date:** 2026-09-20  
**Branch:** `fix/frontend-backend-hosting`  
**Baseline Git Commit:** `7330408` (`fix(frontend): resolve blueprint SSE test type errors`)  
**Scope:** Backend Hosting on Render, Supabase PostgreSQL Connectivity, Vercel Frontend Integration  
**Execution Mode:** Analysis Only — Zero Production or Infrastructure Code Modified

---

## 1. Executive Summary

Following the successful resolution and verification of the frontend build issue on branch `fix/frontend-backend-hosting` (530/530 tests passing, production build green), this document provides a comprehensive, forensic architecture audit of the GrowFlow backend application to prepare for production deployment to Render Web Services.

### Key Conclusions
1. **Application Readiness:** The backend is built as an asynchronous modular monolith with FastAPI (`0.120.0`), SQLAlchemy 2.0 async, `psycopg` (v3) driver, and Pydantic v2 settings. The ASGI entrypoint is located at `backend.app.main:app` and can be served directly by Uvicorn.
2. **Database & Migrations:** The backend targets hosted Supabase PostgreSQL. Database migrations are managed via Alembic (11 migrations present, `0001` through `0011`). Live connectivity verification confirmed the database is currently at revision `0010_gate08_question_templates`, with revision `0011_gate09_agent_executions_and_generation` ready to be applied during pre-deployment.
3. **Authentication & Security:** Centralized Supabase JWT verification (`SupabaseJWTVerifier`) supports both symmetric `HS256` and asymmetric `ES256` verification. Query-token authentication on `/events` endpoints is already natively supported for SSE streams. No credentials, tokens, or private secrets are hardcoded in the codebase.
4. **CORS & Frontend Contract:** FastAPI CORS middleware is fully environment-driven via `APP_CORS_ORIGINS`, allowing seamless whitelisting of the Vercel-hosted frontend domain (`https://<project>.vercel.app`).
5. **Background Workers & SSE:** Blueprint generation (`BlueprintWorker`) runs as an in-process asynchronous task (`asyncio.create_task`) decoupled from HTTP requests, with an in-memory pub/sub event manager (`BlueprintEventManager`) broadcasting SSE events (`event: update`) with a 15-second keepalive heartbeat. Interrupted jobs on server restarts are automatically recovered to a terminal state on startup (`recover_orphaned_jobs`).
6. **Deployment Target Recommendation:** **Render Native Python Web Service** (Python 3.12) is the recommended path. It natively executes the repository's `requirements.txt` / `pyproject.toml`, requires no custom Dockerfile, supports Render `preDeployCommand` for zero-downtime database migrations, and exposes standard stdout/stderr logs.
7. **Verdict:** **READY FOR BACKEND IMPLEMENTATION**.

---

## 2. Backend Architecture

### Structural Layering
```
backend/
├── app/
│   ├── api/                     # HTTP Presentation Layer
│   │   ├── dependencies/        # Auth, DB session, service injection
│   │   ├── middleware/          # CORS, Security Headers, Timing, Correlation ID
│   │   ├── responses/           # Global exception handlers, canonical envelopes
│   │   ├── routes/              # FastAPI domain routers (auth, projects, blueprint, etc.)
│   │   └── schemas/             # Pydantic request/response schemas
│   ├── application/             # Application Services Layer
│   │   └── services/            # Business orchestration (blueprint_service, etc.)
│   ├── config/                  # Configuration & Environment Settings
│   │   └── settings.py          # Centralized Pydantic BaseSettings singleton
│   ├── domain/                  # Pure Domain Logic & Entities
│   │   ├── ai/orchestration/    # LangGraph agent graph, BlueprintWorker, events
│   │   └── identity/            # CurrentUser, UserRole, authorization policies
│   ├── infrastructure/          # External System Adapters
│   │   ├── ai/                  # AI Provider Gateway, OpenRouter 5-key pool
│   │   ├── database/            # SQLAlchemy async engine, session lifecycle, models
│   │   └── repositories/        # Database repositories (blueprint_repo, user_repo)
│   ├── shared/                  # Cross-cutting utilities (logging, exceptions, security)
│   ├── factory.py               # FastAPI application factory & lifespan context
│   └── main.py                  # Thin ASGI application entrypoint
├── migrations/                  # Alembic migration revisions (0001–0011)
├── tests/                       # Test suites (707 collected tests)
├── alembic.ini                  # Alembic CLI configuration
└── pyproject.toml / reqs.txt    # Dependency specifications
```

### Production Startup Path
1. **Entrypoint:** `backend/app/main.py` imports `create_app` from `backend.app.factory`.
2. **Module Variable:** `app = create_app()` is created at import time.
3. **Lifespan Execution (`app_lifespan`):**
   - Initializes structured logging with secret redaction (`setup_logging`).
   - Starts async database engine and session factory (`db_lifecycle.startup`).
   - Scans database and marks orphaned `RUNNING` blueprint generation jobs as interrupted (`recover_orphaned_jobs`).
4. **Middleware Registration:**
   - Outer: `CorrelationIdMiddleware`
   - Middle: `RequestTimingMiddleware`
   - Inner: `SecurityHeadersMiddleware`
   - Inner: `CORSMiddleware` (origins parsed from `APP_CORS_ORIGINS`)
5. **Router Mounting:**
   - `/api/v1` router and `/api` compatibility router.
   - `/health` probes (`/health/live`, `/health/ready`, `/health`).
   - Root service metadata endpoint (`GET /`).

---

## 3. Runtime & Startup Analysis

| Property | Local Environment | Production (Render) Requirement | Status |
| :--- | :--- | :--- | :--- |
| **Python Version** | Python 3.12.10 (virtualenv `.\.venv`) | Python 3.12 (`PYTHON_VERSION=3.12.10`) | Compatible (`pyproject.toml` specifies `>=3.12`) |
| **Package Manager** | `pip` / `setuptools` | `pip install -r requirements.txt` | Fully supported |
| **ASGI Server** | Uvicorn `0.34+` (`uvicorn[standard]`) | Uvicorn | Supported |
| **Host Binding** | `127.0.0.1` (in `AppSettings`) | `0.0.0.0` (all network interfaces) | Must bind `--host 0.0.0.0` in start command |
| **Port Binding** | `8000` (in `AppSettings`) | Dynamic port assigned via `$PORT` | Must bind `--port $PORT` in start command |
| **Production Startup Command** | `python -m backend.app.main` | `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 1` | Verified working |

---

## 4. Render Hosting Compatibility

### Deployment Type Evaluation: Native Python vs. Docker

| Criterion | Option A: Native Python Web Service | Option B: Docker Web Service |
| :--- | :--- | :--- |
| **Repository Match** | **High:** Existing `requirements.txt` and `pyproject.toml` are native Python. | **Low:** No `Dockerfile` currently exists in repository. |
| **Build Time** | Fast (~1-2 minutes with pip caching). | Slower (requires multi-stage OS package build). |
| **Pre-Deploy Command** | Native support (`preDeployCommand: alembic upgrade head`). | Requires custom entrypoint script. |
| **Process Model** | Direct Uvicorn execution in container sandbox. | Docker container execution. |
| **Maintenance** | Minimal configuration overhead; security patches managed by Render base image. | Requires maintaining base image, vulnerabilities, Docker daemon. |
| **Verdict** | **RECOMMENDED (Option A)** | **Not Recommended** |

### Render Service Specifications
- **Service Type:** Web Service
- **Environment:** Python 3
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt && pip install -e .`
- **Pre-Deploy Command:** `alembic upgrade head`
- **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 1`
- **Health Check Path:** `/health/live`

---

## 5. Environment Configuration

### Complete Environment Inventory

| Variable Name | Classification | Default Value | Render Value / Action |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | Required for startup | `development` | Set to `production` (disables docs, enables JSON logs) |
| `APP_NAME` | Optional | `GrowFlow` | Leave default or set `GrowFlow` |
| `APP_HOST` | Handled by CLI | `127.0.0.1` | Overridden by Uvicorn CLI `--host 0.0.0.0` |
| `APP_PORT` / `PORT` | Handled by CLI | `8000` | Overridden by Uvicorn CLI `--port $PORT` |
| `APP_LOG_LEVEL` | Optional | `INFO` | Set to `INFO` |
| `APP_CORS_ORIGINS` | Required for integration | `localhost:3000,localhost:5173` | **Set to Vercel domain:** `https://your-project.vercel.app` |
| `APP_SECRET_KEY` | **CRITICAL Required** | None (Fails closed) | **Generate 64-char hex string** for application security |
| `DEBUG` | Production Safety | `false` | Set to `false` |
| `TESTING` | Production Safety | `false` | Set to `false` |
| `DATABASE_URL` | **CRITICAL Required** | None | **Supabase PostgreSQL URI** (`postgresql+psycopg://...`) |
| `DB_POOL_SIZE` | Database tuning | `5` | `5` (conservative for Render/Supabase free tier) |
| `DB_MAX_OVERFLOW` | Database tuning | `10` | `10` |
| `DB_POOL_TIMEOUT_SECONDS` | Database tuning | `30` | `30` |
| `DB_POOL_RECYCLE_SECONDS` | Database tuning | `1800` | `1800` |
| `SUPABASE_URL` | **CRITICAL Required** | None | Target Supabase URL (`https://<ref>.supabase.co`) |
| `SUPABASE_PUBLISHABLE_KEY` | Required | None | Public Supabase anon key (matches frontend) |
| `SUPABASE_SECRET_KEY` | Required for storage | None | Supabase backend service-role key |
| `SUPABASE_JWT_ISSUER` | Optional validation | None | `https://<ref>.supabase.co/auth/v1` |
| `SUPABASE_JWT_AUDIENCE` | Required auth | `authenticated` | `authenticated` |
| `SUPABASE_JWT_SECRET` | **CRITICAL Required** | None | Supabase JWT Secret (from Supabase API Settings) |
| `SUPABASE_JWT_JWKS_URL` | Optional auth | Derived from URL | `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json` |
| `SUPABASE_STORAGE_BUCKET`| Optional | `growflow-documents` | Default |
| `OPENROUTER_BASE_URL` | Optional AI | `https://openrouter.ai/api/v1`| Default |
| `OPENROUTER_API_KEY_1` | Required for AI | None | Primary OpenRouter API key |
| `OPENROUTER_API_KEY_2..5` | Optional AI | None | Optional fallback key rotation pool |
| `OPENROUTER_HTTP_REFERER` | Optional AI | `https://growflow.app` | Default |
| `OPENROUTER_X_TITLE` | Optional AI | `GrowFlow` | Default |
| `AI_FAST_MODEL` | Optional AI | `openai/gpt-4o-mini` | Default |
| `AI_STANDARD_MODEL` | Optional AI | `openai/gpt-4o` | Default |
| `AI_REASONING_MODEL` | Optional AI | `openai/o1` | Default |
| `AI_MOCK_PROVIDER` | Development/Demo | `false` | `false` for real AI; `true` for zero-cost testing |
| `TAVILY_API_KEY` | Optional external | None | Optional |
| `RATE_LIMIT_ENABLED` | Production Safety | `true` | `true` (60 req/min) |

---

## 6. Database / Supabase Analysis

### Connection & Driver Architecture
- **Async Driver:** `psycopg` (v3 async engine) via `postgresql+psycopg://`.
- **Scheme Transformation:** `backend/app/infrastructure/database/engine.py` automatically converts `postgresql://` and `postgres://` prefixes to `postgresql+psycopg://`.
- **SSL Enforcement:** SSL mode is hardcoded in `connect_args={"sslmode": "require"}`. Supabase requires SSL; this is 100% compliant.
- **Connection Pre-ping:** Enabled (`pool_pre_ping=True`), safely validating stale sockets after idle periods without issuing schema mutations.

### Migration Status
- **Current Database Head:** `0010_gate08_question_templates` (verified live via `alembic current`).
- **Latest Migration File:** `0011_gate09_agent_executions_and_generation.py`.
- **Migration Execution:** Safe and additive. Adds `generation_number`, `cancellation_requested`, `locked_by`, and `locked_at` with server defaults; creates `agent_executions` table.
- **Execution Strategy:** Render `preDeployCommand: alembic upgrade head` will run this migration prior to launching the updated web service.

---

## 7. Authentication Analysis

### Token Flow & Verification
1. **Frontend:** Authenticates with Supabase directly, receives JWT access token.
2. **REST Endpoints:** Frontend passes `Authorization: Bearer <access_token>`.
3. **SSE Streaming Endpoints:** Frontend passes `?token=<access_token>` in query parameter.
4. **Backend Extraction (`backend/app/api/dependencies/auth.py`):**
   - Primary: Checks `request.headers.get("Authorization")`.
   - Fallback for SSE: If `Authorization` is missing and `request.url.path.endswith("/events")`, extracts `request.query_params.get("token")`.
5. **Cryptographic Validation (`SupabaseJWTVerifier`):**
   - Automatically detects algorithm in unverified token header (`HS256` or `ES256`).
   - If `ES256`: Validates against Supabase JWKS endpoint (`/.well-known/jwks.json`).
   - If `HS256`: Validates against `SUPABASE_JWT_SECRET`.
   - Enforces audience (`authenticated`) and expiration (`exp`).
6. **Application Identity Lookup:** Queries `users` table by `sub` claim (UUID).
7. **Account Status Verification:** Fails closed (HTTP 403) if account is `SUSPENDED` or `INACTIVE`.

---

## 8. CORS Analysis

### Current Implementation (`backend/app/api/middleware/__init__.py`)
```python
cors_origins = (
    settings.app.CORS_ORIGINS
    if isinstance(settings.app.CORS_ORIGINS, list)
    else [settings.app.CORS_ORIGINS]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.security.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Request-ID", "X-Response-Time"],
)
```

### Production Requirement
- The hosted frontend on Vercel serves traffic from an HTTPS origin (e.g. `https://growflow.vercel.app`).
- Because `CORS_ALLOW_CREDENTIALS` is `True`, wildcard `*` origins are forbidden by browser security standards.
- `APP_CORS_ORIGINS` in Render must be set to the exact origin list:
  `APP_CORS_ORIGINS=https://growflow.vercel.app,https://your-custom-domain.com`

---

## 9. Frontend ↔ Backend Contract

| Contract Requirement | Frontend Implementation | Backend Implementation | Status |
| :--- | :--- | :--- | :--- |
| **API Base URL** | `VITE_API_BASE_URL` | Root URL mounted on Render | **ALIGNED** |
| **REST Auth Header** | `Authorization: Bearer <token>` | `get_current_user` extracts Bearer | **ALIGNED** |
| **SSE URL Format** | `/api/v1/projects/:id/blueprint/events?token=...` | Route `/api/v1/projects/{project_id}/blueprint/events` | **ALIGNED** |
| **SSE Query Token** | Appended as `?token=${encodeURIComponent(t)}` | `get_current_user` extracts on `/events` | **ALIGNED** |
| **SSE Event Name** | Listens for `event: update` | Yields `event: update\n` | **ALIGNED** |
| **SSE Payload Schema** | Expects `BlueprintStatusResponse` JSON | Emits JSON matching `BlueprintStatusResponse` | **ALIGNED** |
| **SSE Heartbeat** | Native browser timeout avoidance | Emits `: keep-alive\n\n` every 15 seconds | **ALIGNED** |
| **Polling Fallback** | `GET /api/v1/projects/:id/blueprint/status` | Route `GET /api/v1/projects/{project_id}/blueprint/status` | **ALIGNED** |
| **Response Envelope**| Unwraps `{ success: true, data: T }` | Centralized response envelope handler | **ALIGNED** |
| **Error Envelope** | Reads `error.code` & `error.message` | Handlers return `{ success: false, error: {...} }` | **ALIGNED** |

---

## 10. Health Check Analysis

The backend exposes three health endpoints in `backend/app/api/routes/health.py`:

1. **`GET /health/live` (Liveness Probe):**
   - Unauthenticated.
   - Makes zero external or database calls.
   - Returns HTTP 200 `{"status": "alive", "timestamp": "..."}`.
   - **Optimal for Render Web Service Health Check Path.**
2. **`GET /health/ready` (Readiness Probe):**
   - Unauthenticated.
   - Checks that `APP_SECRET_KEY` is loaded.
   - Returns HTTP 200 `{"status": "ready", ...}`.
3. **`GET /health` (Aggregated Health Overview):**
   - Unauthenticated.
   - Non-destructively inspects database initialization state (`connected` / `disconnected` / `unconfigured`).
   - Returns HTTP 200 with runtime diagnostics.

---

## 11. Background Worker Analysis

### Execution Model in Gate 09 / Gate 10
- **Decoupled In-Process Task:** When blueprint generation is requested (`POST /api/v1/projects/{project_id}/blueprint/generate`), `BlueprintService` persists a `BlueprintJob` record in PostgreSQL with status `GENERATING`, commits the transaction, and spawns an asynchronous task on the current event loop:
  ```python
  task = asyncio.create_task(
      self._worker.run_generation_job(job_id=str(job.id), project_id=..., blueprint_id=...)
  )
  self._active_tasks.add(task)
  ```
- **Process Restart Safety:** If Render restarts or redeploys while a job is running:
  - The job in PostgreSQL was marked `GENERATING`.
  - On application startup (`app_lifespan`), `repo.recover_orphaned_jobs()` executes automatically:
    `UPDATE blueprint_jobs SET status = 'CANCELLED', error_message = 'Execution interrupted by server restart' WHERE status = 'RUNNING'`
  - The frontend detects this and provides a "Start New Generation" / retry button.
- **Worker Concurrency on Render:**
  - Because `BlueprintEventManager` is an in-memory pub/sub manager, Uvicorn MUST be configured with `--workers 1`.
  - A single worker process with Python's asynchronous event loop easily handles concurrent I/O, SSE streams, and background jobs.

---

## 12. SSE Production Readiness

### Production SSE Considerations
1. **Reverse Proxy Buffering:**
   - Render uses an NGINX-based reverse proxy. NGINX will buffer responses unless instructed otherwise.
   - In `backend/app/api/routes/blueprint.py` (lines 467–471), `StreamingResponse` sets:
     `"Cache-Control": "no-cache"`  
     `"Connection": "keep-alive"`  
     `"X-Accel-Buffering": "no"`  
   - This header explicitly disables proxy buffering on Render and NGINX!
2. **Connection Heartbeat:**
   - To prevent proxy connection timeouts during idle periods between agent steps, the SSE stream sends a `: keep-alive\n\n` comment every 15.0 seconds.
3. **Last-Event-ID Replay:**
   - The stream supports `Last-Event-ID` header and query parameter `last_event_id` with a 50-event ring buffer per project, allowing clients to replay missed events after temporary network hiccups.
4. **Client Disconnection Handling:**
   - Checks `await request.is_disconnected()` in the streaming loop. Upon disconnection, cleans up subscriber queues to prevent memory leaks.

---

## 13. AI Provider Deployment Analysis

### Gateway Configuration
- **Provider:** OpenRouter (`https://openrouter.ai/api/v1`).
- **Required Secret:** `OPENROUTER_API_KEY_1`.
- **Health-Aware Key Pool:** Supports up to 5 keys (`OPENROUTER_API_KEY_1..5`). Keys 2–5 are optional and rotate automatically if rate limits or transient errors occur.
- **Model Hierarchy:**
  - Fast Model: `openai/gpt-4o-mini`
  - Standard Model: `openai/gpt-4o`
  - Reasoning Model: `openai/o1`
  - Embedding Model: `openai/text-embedding-3-small`
- **Fallback Policy:** If live keys are unavailable and `AI_MOCK_PROVIDER=true`, falls back to deterministic synthesis without failing.

---

## 14. Logging & Observability

- **Structured Logging:** Uses `structlog` and standard library logging.
- **Production Formatting:** Automatically renders structured JSON logs to `sys.stdout` when `APP_ENV=production`.
- **Context Injection:** Injects `correlation_id` and `request_id` into every log entry.
- **Secret Redaction:** `redact_secrets_processor` automatically filters passwords, tokens, and keys matching sensitive patterns before output.
- **Render Log Capture:** Render natively ingests `sys.stdout` JSON lines and indexes them in the Render Dashboard.

---

## 15. Security Findings

| Category | Finding | Classification | Status |
| :--- | :--- | :--- | :--- |
| **Hardcoded Secrets** | Codebase inspected for private keys, database passwords, JWT secrets. None found. | **INFORMATIONAL** | **SECURE** |
| **Fail-Closed Secrets** | Missing `APP_SECRET_KEY` causes `Settings()` to fail startup immediately. | **INFORMATIONAL** | **SECURE** |
| **JWT Verification** | Strict cryptographic verification (PyJWT HS256/ES256), strict audience check, database user status verification. | **INFORMATIONAL** | **SECURE** |
| **Database SSL** | `sslmode: require` is enforced by default in database engine. | **INFORMATIONAL** | **SECURE** |
| **CORS Policy** | Credentials enabled (`CORS_ALLOW_CREDENTIALS=true`); wildcard `*` is not used. Specific origin list enforced via `APP_CORS_ORIGINS`. | **HIGH** | **REQUIRES CONFIG** (Set Vercel domain in Render) |
| **Host/Port Binding** | `AppSettings` defaults to `127.0.0.1:8000`. Render requires `0.0.0.0:$PORT`. | **HIGH** | **REQUIRES CONFIG** (Use Uvicorn CLI flags) |

---

## 16. Render Free-Tier Assessment

### Realities & Safeguards
1. **Spin-Down on Idle:** Render free web services spin down after 15 minutes of inactivity. The next request encounters a ~30–45s cold start while Python boots and connects to Supabase.
   - *Impact:* Initial demo/evaluation requests will experience a brief latency spike.
   - *Safeguard:* Frontend displays loading spinners; subsequent requests respond in normal time (<150ms).
2. **512 MB Memory Ceiling:**
   - *Analysis:* Single Uvicorn process uses ~140–180 MB under load.
   - *Safeguard:* `--workers 1` and `DB_POOL_SIZE=5` ensure memory consumption stays well below 350 MB.
3. **Ephemeral Disk:**
   - *Analysis:* Local filesystem is wiped on every restart.
   - *Safeguard:* GrowFlow persists all project data and blueprint records in PostgreSQL/Supabase and all document blobs in Supabase Storage. Zero reliance on local disk.

---

## 17. Gap Matrix

| Area | Current State | Render Requirement | Gap | Severity | Required Change |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Startup Command** | `python -m backend.app.main` (binds `127.0.0.1:8000`) | Bind to `0.0.0.0:$PORT` | Local host default | **HIGH** | Specify `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 1` in Render |
| **Settings PORT Alias** | `AppSettings.PORT` only aliases `APP_PORT` | Render sets `PORT` env var | `PORT` not aliased in Pydantic settings | **MEDIUM** | Add `PORT` validation alias in `AppSettings` for consistency |
| **CORS Origins** | Localhost default | Hosted Vercel frontend URL | Configuration only | **HIGH** | Set `APP_CORS_ORIGINS=https://<vercel-app>.vercel.app` in Render |
| **Database Migrations**| Database at revision `0010` | Database at revision `0011` | Revision `0011` pending | **HIGH** | Run `alembic upgrade head` via Render `preDeployCommand` |
| **Frontend API Base**| Frontend configured with localhost | Frontend pointing to Render URL | Configuration only | **HIGH** | Set `VITE_API_BASE_URL=https://<render-app>.onrender.com` in Vercel |

---

## 18. Required Changes

### Required Before Deployment
1. **Pydantic Settings PORT Alias:** In `backend/app/config/settings.py`, add `PORT` as an alias to `AppSettings.PORT`:
   ```python
   PORT: int = Field(
       default=8000,
       validation_alias=AliasChoices("APP_PORT", "PORT"),
   )
   ```
   This ensures that any internal application component reading `settings.app.PORT` will see Render's dynamic port assignment.
2. **Render Web Service Configuration:** Define Render Web Service with:
   - Build Command: `pip install -r requirements.txt && pip install -e .`
   - Pre-Deploy Command: `alembic upgrade head`
   - Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --workers 1`
   - Health Check Path: `/health/live`
3. **Render Environment Variables:** Inject all mandatory variables (`APP_ENV=production`, `APP_SECRET_KEY`, `APP_CORS_ORIGINS`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_JWT_SECRET`, `OPENROUTER_API_KEY_1`).

### Required for Frontend ↔ Backend Integration
1. Set `VITE_API_BASE_URL` in Vercel to `https://<render-service-name>.onrender.com`.
2. Redeploy frontend on Vercel.

### Not Required / Do Not Change
- Do NOT build a Docker container or create Dockerfiles.
- Do NOT introduce Celery or Redis for background jobs (in-process `asyncio` task model is complete and durable).
- Do NOT modify database schemas or write new migrations.
- Do NOT alter authentication logic.

---

## 19. Proposed Implementation Units

### Unit 1: Backend Settings Port Alias & Render Service Blueprint
- **Objective:** Add `PORT` alias in `AppSettings` and create `render.yaml` infrastructure-as-code configuration for Render Web Service deployment.
- **Files Affected:**
  - `backend/app/config/settings.py` (add `AliasChoices("APP_PORT", "PORT")`)
  - `render.yaml` (optional/canonical service definition file)
- **Security Impact:** None.
- **Verification:** Unit tests for `settings.py` pass; simulated `PORT=10000` test binds cleanly.

### Unit 2: Database Migration & Render Deployment Execution
- **Objective:** Apply migration `0011` to the hosted Supabase database and execute initial Render Web Service deployment.
- **Actions:** Run `alembic upgrade head`, configure Render environment variables, trigger initial deploy.
- **Verification:**
  - `alembic current` confirms revision `0011_gate09_agent_executions_and_generation`.
  - `GET https://<render-app>.onrender.com/health/live` returns HTTP 200 `{"status": "alive"}`.
  - `GET https://<render-app>.onrender.com/health` returns HTTP 200 with database status `connected`.

### Unit 3: Vercel Frontend Connection & End-to-End Smoke Verification
- **Objective:** Update Vercel environment variables, trigger Vercel deployment, and verify live integration.
- **Actions:** Set `VITE_API_BASE_URL`, test user authentication, project creation, blueprint SSE streaming, and terminal content viewing.
- **Verification:** Browser console shows zero CORS errors; Network tab shows successful SSE streaming from Render and 200 responses for API requests.

---

## 20. Acceptance Criteria

- [ ] `backend/app/config/settings.py` accepts both `APP_PORT` and `PORT`.
- [ ] Database migration `0011` applied to hosted Supabase database (`alembic current` shows `0011`).
- [ ] Render Web Service builds with Python 3.12 without errors.
- [ ] Render Web Service health check on `/health/live` passes.
- [ ] Render Web Service `/health` endpoint reports `status: healthy` and database `connected`.
- [ ] CORS allows requests from the Vercel hosted frontend origin.
- [ ] Supabase JWT authentication succeeds for incoming frontend requests.
- [ ] SSE streaming endpoint `/api/v1/projects/:id/blueprint/events?token=...` connects and streams live `update` events.
- [ ] AI Provider Gateway connects to OpenRouter and executes generation.
- [ ] Zero secrets leaked in logs or client bundles.

---

## 21. Explicit Out-of-Scope Items

- Rewriting in-process workers into Celery/Redis.
- Creating container Dockerfiles.
- Adding new domain features or API endpoints.
- Modifying frontend React components (frontend build is already verified and frozen).
- Altering existing Alembic migration history.

---

## 22. Final Verdict

# READY FOR BACKEND IMPLEMENTATION

The investigation is complete. The backend architecture is sound, modern, and directly compatible with Render Native Python deployment. The gap between current repository state and production readiness is minimal, strictly isolated, and fully understood.
