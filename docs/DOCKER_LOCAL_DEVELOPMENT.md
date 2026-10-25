# GrowFlow — Docker Containerization & Local Development Guide

This guide provides the official documentation for building, running, and managing the GrowFlow platform locally using Docker and Docker Compose.

---

## 1. Overview of Services

GrowFlow's containerized development environment consists of two coordinated services:

| Service | Container Name | Port Mapping | Runtime / Base Image | Purpose |
|---|---|:---:|---|---|
| **`backend`** | `growflow-backend` | `8000:8000` | `python:3.12-slim` | FastAPI ASGI application, domain services, AI agent pipelines, and health probes. Runs as non-root user (`appuser`). |
| **`frontend`** | `growflow-frontend` | `5173:80` | `nginx:alpine` (multi-stage from `node:22-alpine`) | Serves compiled React 19 single-page application with client-side SPA route fallbacks and non-buffered `/api/` reverse proxy for Server-Sent Events (SSE). |

> **Database Architecture:**<br>
> The database is hosted externally on Supabase PostgreSQL. Containers connect to the database via standard TCP using the `DATABASE_URL` environment variable. No local PostgreSQL container is required by default, avoiding duplicate local data stores.

---

## 2. Prerequisites

Before starting, ensure you have the following installed on your machine:

- **Docker Desktop for Windows / macOS / Linux:** Version 20.10+ (Docker Engine 24+ and Docker Compose v2+ / Compose plugin v5+).
- **Git:** To clone and manage repository changes.
- **Supabase Account:** Active Supabase project with credentials (URL, anon key, and database connection string).

---

## 3. First-Time Setup & Environment Configuration

### Step 1: Prepare Environment File

Docker Compose automatically loads variables from a root `.env` file if present, or falls back to sensible local development defaults.

Copy the template to create your local `.env`:

```bash
# From repository root
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit `.env` with your project credentials:

```ini
# Application Mode
APP_ENV=development
APP_SECRET_KEY=local-dev-secret-key-at-least-32-chars-long!

# Hosted Database (Supabase PostgreSQL)
DATABASE_URL=postgresql+psycopg://postgres:[PASSWORD]@[HOST]:5432/postgres

# Supabase Client Authentication
SUPABASE_URL=https://[YOUR_PROJECT].supabase.co
SUPABASE_PUBLISHABLE_KEY=[YOUR_ANON_KEY]
SUPABASE_JWT_SECRET=[YOUR_JWT_SECRET]

# AI Provider Gateway (Optional for local development)
# If omitted or unconfigured, the gateway operates in offline mock synthesis mode.
OPENROUTER_API_KEY_1=sk-or-v1-...
```

> **Security Rule:** Never commit `.env` to Git. The `.dockerignore` and `.gitignore` files strictly exclude real environment files from build contexts and version control.

---

## 4. Normal Startup Workflow

### Start Services (Detached Mode)

```bash
docker compose up -d --build
```

Compose will:
1. Build the backend image (`python:3.12-slim`) with all production and development dependencies installed.
2. Build the frontend image using multi-stage Node 22 (`npm ci` and `npm run build`), packaging the output into a lightweight Nginx web server.
3. Start the `backend` container and await its health check (`/health/live`).
4. Start the `frontend` container once the backend reports healthy.

### Access URLs

Once running, access the platform via your host web browser:

- **Frontend Application:** [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Health Probe:** [http://localhost:8000/health/live](http://localhost:8000/health/live)
- **Backend Readiness Probe:** [http://localhost:8000/health/ready](http://localhost:8000/health/ready)

---

## 5. Service Health & Log Inspection

### View Real-Time Logs

```bash
# View combined logs
docker compose logs -f

# View backend logs only
docker compose logs -f backend

# View frontend logs only
docker compose logs -f frontend
```

### Check Container Status & Health

```bash
docker compose ps
```

Healthy containers will show `(healthy)` in the status column:
```
NAME                IMAGE                        COMMAND                  SERVICE    STATUS
growflow-backend    growflow_ai-backend          "uvicorn backend.app…"   backend    Up (healthy)
growflow-frontend   growflow_ai-frontend         "/docker-entrypoint.…"   frontend   Up (healthy)
```

---

## 6. Shutdown & Rebuild Workflow

### Stop Services

```bash
# Stop containers gracefully
docker compose down

# Stop containers and remove named volumes
docker compose down -v
```

### Rebuild After Code Changes

When you update frontend or backend source files:

```bash
# Rebuild and restart both services
docker compose up -d --build

# Rebuild only the backend
docker compose up -d --build backend

# Rebuild only the frontend
docker compose up -d --build frontend
```

---

## 7. Database Migrations

GrowFlow database migrations are managed with Alembic. Database migrations are **never run automatically on container startup** to prevent accidental schema mutations during routine restarts.

### Command Execution Mechanics
The backend Dockerfile specifies Uvicorn as a default `CMD` (not a locking `ENTRYPOINT`):
```dockerfile
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```
Because no `ENTRYPOINT` is defined, passing arguments to `docker compose run --rm backend <cmd>` completely replaces the default `uvicorn` command rather than appending to it.

Both the direct command override and the explicit `--entrypoint` override are fully supported:
- **Direct invocation:** `docker compose run --rm backend alembic <subcommand>`
- **Explicit entrypoint override:** `docker compose run --rm --entrypoint alembic backend <subcommand>`

### Safe Inspection Commands (Non-Mutating)

To verify the migration lineage and inspect pending versions without modifying the live database:

```bash
# Inspect available migration heads from disk (does not connect to database)
docker compose run --rm backend alembic heads
# Or with explicit entrypoint:
docker compose run --rm --entrypoint alembic backend heads

# View complete revision history chain (offline inspection)
docker compose run --rm backend alembic history

# Check current revision recorded on the connected database (read-only query)
docker compose run --rm backend alembic current
```

### Applying Migrations (Mutating / Operator-Initiated)

To apply pending forward migrations to your connected Supabase database using the containerized environment:

```bash
# Apply pending forward migrations
docker compose run --rm backend alembic upgrade head
# Or with explicit entrypoint:
docker compose run --rm --entrypoint alembic backend upgrade head
```

> **Safety Warning:** Never execute `alembic upgrade head` without verifying that `DATABASE_URL` targets the intended environment. Live database migrations must be performed intentionally and verified with `alembic current` afterwards.

---

## 8. Networking Architecture

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 Host Machine (Browser)                 │
                  └───────────────┬────────────────────────┬───────────────┘
                                  │                        │
                      Port 5173   │                        │  Port 8000
                    (Browser HTTP)│                        │(Direct / Docs)
                                  ▼                        ▼
┌─────────────────────────────────┴─────────┐    ┌─────────┴───────────────────────┐
│           growflow-frontend               │    │        growflow-backend         │
│             (Nginx Alpine)                │    │       (FastAPI / Uvicorn)       │
│                                           │    │                                 │
│  - Static SPA: /usr/share/nginx/html      │    │  - ASGI Port: 8000              │
│  - SPA Fallback: try_files -> index.html  │    │  - Non-root user: appuser       │
│  - Reverse Proxy:                         │    │  - Health Probes:               │
│      location /api/ -> backend:8000/api/  │    │      /health/live               │
│      (buffering disabled for SSE streams) │    │      /health/ready              │
└─────────────────────────────────┬─────────┘    └─────────┬───────────────────────┘
                                  │ (Docker Bridge Network)│
                                  └────────────────────────┤
                                                           │ External TCP
                                                           ▼
                                         ┌──────────────────────────────────┐
                                         │       Hosted Supabase Cloud      │
                                         │   PostgreSQL + Auth + Storage    │
                                         └──────────────────────────────────┘
```

### Key Networking Features:
1. **Host-Reachable Ports:** Both frontend (`5173`) and backend (`8000`) are mapped directly to `localhost`, ensuring standard developer habits and direct browser API debugging work identically to native processes.
2. **Nginx Reverse Proxy:** The frontend container reverse-proxies `/api/` calls to `http://backend:8000/api/` inside the Docker network. This prevents CORS restrictions from blocking browser requests and simplifies local networking.
3. **SSE Streaming Support:** The Nginx reverse proxy explicitly sets `proxy_buffering off;` and `proxy_read_timeout 86400s;` so that real-time Server-Sent Events (SSE) during AI blueprint generation stream immediately to the client without chunking delay.

---

## 9. Common Troubleshooting

### 1. Port Conflicts (`5173` or `8000` Already in Use)
If you already have a local process (such as a local Vite dev server or Uvicorn process) running on port 5173 or 8000:
- Stop the native local process, or
- Override host ports in `docker-compose.yml` or your local `.env`:
  ```yaml
  ports:
    - "8001:8000"  # Changes host backend port to 8001
  ```

### 2. Backend Fails to Start (Health Check Unhealthy)
Inspect backend logs for configuration or database initialization errors:
```bash
docker compose logs backend
```
- If `DATABASE_URL` is invalid, the backend will log an error but will still start in degraded offline mode.
- Ensure `APP_SECRET_KEY` has at least 32 characters if you set a custom value.

### 3. Frontend Displays White Screen or Network Error
- Confirm that the backend container is healthy: `docker compose ps`.
- Check browser console (F12) for network requests to `/api/...`.
- If you customized `VITE_API_BASE_URL` in `.env`, ensure it points to `http://localhost:8000` (host-accessible) and rebuild the frontend with `docker compose up -d --build frontend`.

---

## 10. Local Development vs. Production Deployment

| Aspect | Local Docker Compose | Cloud Production (Render / Vercel) |
|---|---|---|
| **Frontend Serving** | Multi-stage Nginx container on `localhost:5173` | Vercel Edge Network CDN with `vercel.json` rewrites |
| **Backend Serving** | Single Uvicorn worker in Python 3.12 container on `localhost:8000` | Render Python 3.12 Web Service managed by `render.yaml` |
| **AI Gateway Fallback** | Deterministic mock seeds active if OpenRouter keys are omitted | Strict fail-closed (mock fallback blocked in staging/production) |
| **Database Migrations** | Explicit one-off command: `docker compose run --rm backend alembic upgrade head` | Automated Render `preDeployCommand`: `alembic upgrade head` |
| **TLS / SSL** | Unencrypted HTTP for local development convenience | Automatic managed HTTPS certificates enforced by cloud CDNs |

---

## 11. Known Limitations

1. **Build-Time Frontend Variables:** In Vite, environment variables prefixed with `VITE_*` are compiled into the JavaScript bundle at build time. Changing `VITE_API_BASE_URL` or `VITE_SUPABASE_URL` requires rebuilding the frontend container (`docker compose build frontend`).
2. **Hot-Module Reloading (HMR):** The default Docker Compose setup packages the production static distribution for fidelity to production behavior. For active frontend code editing with hot-module reload, developers may prefer running `npm run dev` natively on the host machine.
