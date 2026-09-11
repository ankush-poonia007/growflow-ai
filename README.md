# GrowFlow

> AI-powered internship project execution platform.

GrowFlow guides student interns through the full lifecycle of a software project — from onboarding assessment through domain-adapted planning, task execution, progress tracking, risk management, and mentor collaboration — using structured AI assistance governed by deterministic business rules.

---

## Architecture Overview

GrowFlow is a **FastAPI modular monolith** with a layered backend:

```
Frontend (React/Next.js — Gate 06+)
  ↓
FastAPI API Layer
  ↓
Application Layer  (use cases, commands, queries)
  ↓
Domain Layer       (business rules, value objects)
  ↓
Infrastructure     (PostgreSQL/Supabase, AI Gateway, external adapters)
  ↓
PostgreSQL/Supabase + OpenRouter + GitHub + Tavily + Resend
```

**AI is governed** — agents operate through authorized tools with Pydantic-validated structured output, a QA/Judge layer, and deterministic domain services. AI cannot arbitrarily mutate authoritative project state.

**Architecture authority:** `docs/` — frozen Phase 1–6 documentation. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for module boundaries and import rules.

---

## Repository Structure

```
growflow-ai/
├── backend/
│   ├── app/
│   │   ├── config/          ← Typed settings (Gate 02)
│   │   ├── api/             ← Routes, schemas, responses, dependencies
│   │   ├── application/     ← Use cases, commands, queries, services
│   │   ├── domain/          ← Business concepts and rules
│   │   │   ├── identity/
│   │   │   ├── organization/
│   │   │   ├── project/
│   │   │   ├── planning/
│   │   │   ├── execution/
│   │   │   ├── communication/
│   │   │   ├── knowledge/
│   │   │   ├── integrations/
│   │   │   ├── ai/
│   │   │   └── platform/
│   │   ├── infrastructure/  ← Database, AI gateway, adapters
│   │   ├── workers/         ← Background job runners
│   │   └── shared/          ← Exceptions, logging, security, events, utilities
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   ├── api/
│   │   └── e2e/
│   ├── migrations/          ← Alembic migrations (Gate 03+)
│   └── scripts/             ← Development scripts
│
├── frontend/                ← React/Next.js application (Gate 06+)
├── docs/                    ← Frozen architecture + implementation gates
│   └── implementation/      ← Gate specifications and evidence
├── scripts/                 ← Repository-level scripts
├── .github/workflows/       ← CI foundation
├── .env.example             ← Environment template (copy to .env, add real values)
├── requirements.txt         ← Python dependencies
├── pyproject.toml           ← Tooling configuration (ruff, mypy, pytest)
└── README.md
```

---

## Development Baseline

| Tool | Version | Notes |
|---|---|---|
| Python | 3.12.x | Required |
| Node.js | 18+ | For frontend (Gate 06+) |
| Docker Desktop | 24+ | Available; not required for Gate 01–02 |
| PostgreSQL | via Supabase | Hosted — no local PostgreSQL required |

---

## Environment Setup

### 1. Clone

```bash
git clone https://github.com/ankush-poonia007/growflow-ai.git
cd growflow-ai
```

### 2. Python virtual environment

```bash
py -3.12 -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
copy .env.example .env
# Edit .env — add your real Supabase URL, keys, and other credentials.
# NEVER commit .env to Git.
```

### 5. Verify installation

```bash
pip check
ruff check backend/
pytest backend/tests/ --collect-only
```

---

## Hosted Supabase / PostgreSQL

GrowFlow uses **hosted Supabase** as its PostgreSQL provider. No local PostgreSQL server is required.

Set the following in your `.env`:

```
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_PUBLISHABLE_KEY=your-supabase-anon-key
SUPABASE_SECRET_KEY=your-backend-only-service-role-key
SUPABASE_JWT_SECRET=your-backend-only-jwt-verification-secret
```

**Backend-only secrets** (`SUPABASE_SECRET_KEY`, `SUPABASE_JWT_SECRET`) must **never** reach the frontend.

---

## Running the Backend

> ⚠️ **Not yet implemented.** The backend application is established in Gate 02.

Once Gate 02 is complete:

```bash
# Development server
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

# API docs (once running)
http://127.0.0.1:8000/docs
```

---

## Running the Frontend

> ⚠️ **Not yet implemented.** The frontend is established in Gate 06.

---

## Running Tests

```bash
# Run all tests
pytest backend/tests/

# Run by category
pytest backend/tests/ -m unit
pytest backend/tests/ -m integration
pytest backend/tests/ -m api

# With coverage
pytest backend/tests/ --cov=backend/app --cov-report=html

# Discover only (Gate 01 — no product tests yet)
pytest backend/tests/ --collect-only
```

---

## Code Quality

```bash
# Lint
ruff check backend/

# Format check
ruff format backend/ --check

# Auto-fix and format
ruff check backend/ --fix
ruff format backend/

# Type checking
mypy backend/app/
```

---

## Documentation

| Document | Purpose |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Module boundaries and import policy |
| [`docs/6A_Backend_Architecture_Final.md`](docs/6A_Backend_Architecture_Final.md) | Backend architecture (frozen) |
| [`docs/6B_Database_Architecture_and_Data_Model_Final.md`](docs/6B_Database_Architecture_and_Data_Model_Final.md) | Database architecture (frozen) |
| [`docs/6C_API_Architecture_Final.md`](docs/6C_API_Architecture_Final.md) | API architecture (frozen) |
| `docs/6D–6N_*.md` | Auth, AI, agents, RAG, workers, integrations, observability, storage, deployment, security (frozen) |
| [`docs/implementation/00_IMPLEMENTATION_MASTER_PLAN.md`](docs/implementation/00_IMPLEMENTATION_MASTER_PLAN.md) | Implementation gate orchestration |
| `docs/implementation/GATE_XX_*.md` | Per-gate specifications |
| `docs/implementation/GATE_XX_EVIDENCE.md` | Per-gate completion evidence |

---

## Implementation Gates

GrowFlow is built in 18 controlled gates. Each gate must be fully implemented, validated, and reviewed before the next gate begins.

| Gate | Focus | Status |
|---|---|---|
| 00 | Human/environment setup | ✅ PASS |
| 01 | Repository foundation | ✅ PASS |
| 02 | Backend foundation | 🔒 Requires Gate 01 human review |
| 03 | Database foundation | 🔒 Pending |
| 04 | Authentication/security | 🔒 Pending |
| 05 | Core backend domain | 🔒 Pending |
| 06 | Frontend foundation | 🔒 Pending |
| 07–17 | Features, AI, integrations, deployment | 🔒 Pending |

---

## Security

> ⚠️ **CRITICAL:** Never commit `.env` or any real credentials to Git.

- `.env` is listed in `.gitignore` and will never be tracked
- `.env.example` contains only placeholders — it is safe to commit
- Backend-only secrets must never be exposed to the frontend
- AI provider keys are managed by the AI Provider Gateway (Gate 09+)
- All secrets in production use deployment-environment secret facilities

---

## Contributing / Branch Workflow

GrowFlow uses a **feature-branch workflow** with one branch per implementation gate:

```
gate-01/repository-foundation  →  PR  →  main
gate-02/backend-foundation      →  PR  →  main
...
```

- Commits follow: `build(gate-XX): <verified unit>`
- No direct pushes to `main`
- Each PR requires human review before merge
- Gate N+1 begins only after explicit human authorization post-merge

---

*GrowFlow — Phase 7 Implementation | Gate 01: Repository Bootstrap & Project Skeleton*
