# Gate 03 — Database Foundation Evidence

**Branch:** `gate-03/database-foundation`
**Commit:** `d17b90b`
**Status:** IMPLEMENTATION COMPLETE — awaiting review

---

## Pre-flight Checks

| Check | Result |
|---|---|
| Gate 02 merged into `main` | ✅ Verified — commit `b6f8603` present |
| Clean working tree on `main` before branch | ✅ `git status` clean |
| Branch created from `main` | ✅ `gate-03/database-foundation` |
| No local PostgreSQL installed | ✅ Using hosted Supabase only |
| No destructive DDL executed | ✅ None — SELECT 1 probe only |
| No secrets committed | ✅ `.env` unchanged; DATABASE_URL in environment only |

---

## Unit 01 — Repository Audit

**Pre-existing state:**
- `backend/app/infrastructure/database/__init__.py`: empty (1 line)
- `backend/app/infrastructure/database/`: only `__init__.py`
- `backend/app/infrastructure/repositories/`: only `__init__.py`
- No `alembic.ini`, no `backend/migrations/` content (only `.gitkeep`)
- No existing Alembic configuration
- No existing ORM models

**Conclusion:** Clean slate. No conflicts with Gate 03 implementation.

---

## Unit 02 — Database Engine and Session Factory

**Files created:**
- `backend/app/infrastructure/database/engine.py`

**Implementation:**
- `build_async_engine()` — creates `AsyncEngine` with psycopg3 async driver
  - URL normalisation: `postgresql://` or `postgres://` → `postgresql+psycopg://`
  - Pool: configurable via `DatabaseSettings` (size, overflow, timeout, recycle)
  - SSL: `sslmode=require` via `connect_args` for hosted Supabase
  - `pool_pre_ping=True` — non-destructive health validation
  - Never logs DATABASE_URL or credentials
- `build_async_session_factory()` — returns `async_sessionmaker[AsyncSession]`
  - `expire_on_commit=False`, `autocommit=False`, `autoflush=False`
- `get_session_context()` — async context manager for unit-of-work sessions
  - Commits on success, rolls back on exception, always closes

**Validation:** 5 engine tests + 2 session factory tests + 3 transaction tests — all passed.

---

## Unit 03 — Declarative Base and Mixins

**Files created:**
- `backend/app/infrastructure/database/base.py`

**Implementation:**
- `Base(DeclarativeBase)` — canonical SQLAlchemy ORM base for all GrowFlow models
- `TimestampMixin` — UTC `created_at`/`updated_at` with `server_default=func.now()`
- `UUIDPrimaryKeyMixin` — UUID primary key with Python-side `uuid.uuid4()` default
- `utcnow()` — timezone-aware UTC datetime utility

**Architecture compliance:** 6B section 9 (UUID PKs), 6B section 51 (UTC timestamps).

---

## Unit 04 — Alembic Migration Environment

**Files created:**
- `alembic.ini` — Alembic configuration (at repository root)
- `backend/migrations/env.py` — async migration runner
- `backend/migrations/script.py.mako` — migration template
- `backend/migrations/versions/__init__.py`

**Implementation:**
- `alembic.ini`: `script_location = backend/migrations`, UTC timestamps, env-var URL interpolation
- `env.py`:
  - `_get_database_url()` — resolves URL from env vars (ALEMBIC_DATABASE_URL or DATABASE_URL), raises `ValueError` if absent
  - `run_migrations_offline()` — SQL generation without live connection
  - `run_migrations_online()` + `_run_async_migrations()` — async execution via psycopg3
  - `NullPool` for CLI migration runs (no idle connections held after migration completes)
  - `Base.metadata` imported for autogenerate support

**Alembic commands:**
```bash
alembic upgrade head    # apply all pending migrations
alembic current         # show current revision
alembic history         # list all applied migrations
alembic revision --autogenerate -m "description"  # generate migration
```

---

## Unit 05 — Baseline Migration

**File created:**
- `backend/migrations/versions/0001_gate03_baseline.py`

**Migration identity:**
```python
revision: str = "0001_gate03_baseline"
down_revision: str | None = None  # initial migration, no parent
```

**upgrade() operations (idempotent, non-destructive):**
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

**downgrade() operations (guarded):**
```sql
DROP EXTENSION IF EXISTS pg_trgm;
DROP EXTENSION IF EXISTS "uuid-ossp";
```

**Safety:** `IF NOT EXISTS` / `IF EXISTS` guards — safe on hosted Supabase where extensions may be pre-installed.

> **Note:** This migration has NOT been applied to the hosted Supabase instance.
> It requires explicit `alembic upgrade head` by the operator with `DATABASE_URL` set.
> It is NOT auto-applied at application startup.

---

## Unit 06 — Database Lifecycle Management

**Files created/modified:**
- `backend/app/infrastructure/database/lifecycle.py` (NEW)
- `backend/app/factory.py` (MODIFIED — lifecycle hooks added)

**Implementation:**
- `startup(db_settings)` — builds engine + session factory, runs `SELECT 1` probe
  - Graceful skip if `DATABASE_URL` not configured (logs warning, does not raise)
  - On probe failure: disposes engine, resets singletons to `None`, re-raises
- `shutdown()` — disposes engine, resets singletons
- `get_engine()`, `get_session_factory()`, `is_initialised()` — state accessors

**FastAPI integration in `factory.py`:**
- `await db_lifecycle.startup(settings.database)` called in `app_lifespan()` before yield
- Startup errors are caught and logged; application boots even without DB connectivity
- `await db_lifecycle.shutdown()` always called in `finally` block

---

## Unit 07 — Database Exception Mapping

**File created:**
- `backend/app/infrastructure/database/exceptions.py`

**Mapping:**

| SQLAlchemy Exception | GrowFlow Exception | HTTP Status |
|---|---|---|
| `IntegrityError` | `ConflictException` | 409 |
| `NoResultFound` | `NotFoundException` | 404 |
| `OperationalError` | `InfrastructureException` | 500 |
| `SQLAlchemyError` (generic) | `InfrastructureException` | 500 |

**Safety:** No credentials, query text, or raw SQL parameters exposed in raised exceptions.

---

## Unit 08 — FastAPI Database Session Dependency

**Files created/modified:**
- `backend/app/api/dependencies/database.py` (NEW)
- `backend/app/api/dependencies/__init__.py` (MODIFIED — exports added)

**Implementation:**
- `get_db_session()` — async generator dependency
  - Returns `HTTP 503` if session factory not initialised at startup
  - Yields `AsyncSession`, commits on success, rolls back on exception, closes always
- `DbSession = Annotated[AsyncSession, Depends(get_db_session)]` — type alias for clean injection syntax

**Usage in routes (Gate 05+):**
```python
from backend.app.api.dependencies import DbSession

@router.get("/projects")
async def list_projects(db: DbSession) -> list[ProjectResponse]:
    ...
```

---

## Unit 09 — Repository Base Class

**Files created/modified:**
- `backend/app/infrastructure/repositories/base.py` (NEW)
- `backend/app/infrastructure/repositories/__init__.py` (MODIFIED)

**Implementation:**
- `BaseRepository[ModelT]` — typed generic base with injected `AsyncSession`
- `get_by_id(entity_id: UUID | str)` — scalar PK lookup
- `get_all()` — all entities (callers must add pagination)
- `add(entity)` — adds + flush + refresh; no commit (caller controls transaction)
- `delete(entity)` — deletes + flush; no commit

**Architecture compliance:** 6A section 7 — repositories own persistence; no business logic, HTTP formatting, or AI calls.

---

## Unit 10 — Health Endpoint Database Status

**File modified:**
- `backend/app/api/routes/health.py`

**Health `/health` response now includes:**
```json
{
  "checks": {
    "database": {
      "status": "connected | disconnected | unconfigured",
      "configured": true | false,
      "connected": true | false
    }
  }
}
```

**Safety:** No DATABASE_URL, host, port, or credentials in the response.

---

## Test Results

### Unit Tests — `backend/tests/unit/test_database.py`

**33 tests total:**

| Test Class | Count | Status |
|---|---|---|
| `TestBuildAsyncEngine` | 5 | ✅ All passed |
| `TestBuildAsyncSessionFactory` | 2 | ✅ All passed |
| `TestGetSessionContext` | 3 | ✅ All passed |
| `TestDatabaseLifecycle` | 5 | ✅ All passed |
| `TestDatabaseExceptions` | 6 | ✅ All passed |
| `TestDatabaseBase` | 2 | ✅ All passed |
| `TestAlembicConfiguration` | 6 | ✅ All passed |
| `TestHealthDatabaseStatus` | 3 | ✅ All passed |
| `TestDbSessionDependency` | 1 | ✅ All passed |

### Integration Tests — `backend/tests/integration/test_database_integration.py`

| Test | Status |
|---|---|
| `test_live_connectivity_select_1` | SKIPPED (DATABASE_URL not set) |
| `test_live_transaction_rollback` | SKIPPED (DATABASE_URL not set) |
| `test_live_session_context_commits` | SKIPPED (DATABASE_URL not set) |
| `test_live_postgresql_extensions_accessible` | SKIPPED (DATABASE_URL not set) |

### Full Suite Result
```
======================== 70 passed, 4 skipped in 2.66s ========================
```

**Gate 02 regression:** 0 tests broken.

### Code Quality
```
ruff check backend/ --fix --unsafe-fixes
Found 0 errors remaining.
```

---

## Files Changed Summary

| File | Action | Description |
|---|---|---|
| `alembic.ini` | NEW | Alembic configuration at repo root |
| `backend/app/factory.py` | MODIFIED | Database lifecycle hooks in lifespan |
| `backend/app/api/dependencies/database.py` | NEW | DbSession FastAPI dependency |
| `backend/app/api/dependencies/__init__.py` | MODIFIED | DbSession export added |
| `backend/app/api/routes/health.py` | MODIFIED | Database status in health overview |
| `backend/app/infrastructure/database/__init__.py` | MODIFIED | Public API exports |
| `backend/app/infrastructure/database/base.py` | NEW | Base, TimestampMixin, UUIDPrimaryKeyMixin |
| `backend/app/infrastructure/database/engine.py` | NEW | Engine/session factory/context manager |
| `backend/app/infrastructure/database/exceptions.py` | NEW | SQLAlchemy exception mapping |
| `backend/app/infrastructure/database/lifecycle.py` | NEW | Engine/session-factory singletons + probe |
| `backend/app/infrastructure/repositories/__init__.py` | MODIFIED | BaseRepository export |
| `backend/app/infrastructure/repositories/base.py` | NEW | Generic async BaseRepository |
| `backend/migrations/__init__.py` | NEW | Package marker |
| `backend/migrations/env.py` | NEW | Alembic async migration environment |
| `backend/migrations/script.py.mako` | NEW | Migration file template |
| `backend/migrations/versions/__init__.py` | NEW | Package marker |
| `backend/migrations/versions/0001_gate03_baseline.py` | NEW | Baseline: enable extensions |
| `backend/tests/unit/test_database.py` | NEW | 33 unit tests |
| `backend/tests/integration/test_database_integration.py` | NEW | 4 integration tests |

---

## Pending Actions Before Merge

1. **Review this evidence document** — confirm all implementation decisions are correct.

2. **Apply baseline migration to hosted Supabase** (recommended before merge):
   ```powershell
   $env:DATABASE_URL = "postgresql+psycopg://USER:PASS@HOST:5432/DATABASE"
   .venv\Scripts\alembic.exe upgrade head
   .venv\Scripts\alembic.exe current
   ```

3. **Run integration tests with live DATABASE_URL** to confirm hosted connectivity:
   ```powershell
   $env:DATABASE_URL = "postgresql+psycopg://..."
   .venv\Scripts\python.exe -m pytest backend/tests/integration/test_database_integration.py -v
   ```

4. **Merge `gate-03/database-foundation` → `main`** after review approval.
