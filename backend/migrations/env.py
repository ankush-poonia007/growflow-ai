"""
GrowFlow — Alembic Migration Environment.

Configures Alembic to use:
  - The async psycopg driver via run_async_migrations helper.
  - GrowFlow's typed Settings for DATABASE_URL (no direct os.environ in business code).
  - GrowFlow's SQLAlchemy Base metadata for autogenerate support.

SAFETY RULES:
  - DATABASE_URL is never logged. Only masked connectivity status is reported.
  - No DROP, TRUNCATE, or RESET is called from this env.
  - Applied migrations are never rewritten or reversed without explicit review.

Architecture ref: 6B § 50 — Migration Strategy; 6A — Infrastructure layer.
"""

from __future__ import annotations

from logging.config import fileConfig
import os
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# Ensure repository root is on sys.path so that 'backend' is resolved
# when invoked directly or without an explicit PYTHONPATH.
_REPO_ROOT = str(Path(__file__).resolve().parents[2])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# ---------------------------------------------------------------------------
# Alembic Config object — access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import GrowFlow's Base metadata for autogenerate support.
# Future domain models that inherit from Base will be detected automatically.
# ---------------------------------------------------------------------------
from backend.app.infrastructure.database.base import Base  # noqa: E402
import backend.app.infrastructure.database.models  # noqa: F401, E402

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Resolve DATABASE_URL from the environment.
# The alembic.ini references %(DATABASE_URL)s; we also allow it to be passed
# directly via environment variable at the CLI level or loaded via typed settings.
# ---------------------------------------------------------------------------


def _get_database_url() -> str:
    """
    Resolve the database URL for Alembic migrations.

    Priority:
    1. ALEMBIC_DATABASE_URL — a migration-specific override (useful for CI).
    2. DATABASE_URL — the standard application environment variable.
    3. GrowFlow typed settings (loads from .env).
    4. alembic.ini sqlalchemy.url (only if neither env var is set).

    The URL is converted to the async psycopg driver prefix so Alembic's
    async runner can use it correctly.

    NEVER log this URL — it contains credentials.
    """
    url = os.environ.get("ALEMBIC_DATABASE_URL") or os.environ.get("DATABASE_URL")

    if not url:
        try:
            from backend.app.config import get_settings

            url = get_settings().database.DATABASE_URL
        except Exception:
            pass

    if not url:
        # Fall back to the alembic.ini value (may contain the %(DATABASE_URL)s
        # substitution which evaluates to empty string if the env var is absent).
        ini_url = config.get_main_option("sqlalchemy.url", default="")
        if ini_url and "%(DATABASE_URL)s" not in ini_url:
            url = ini_url

    if not url:
        raise ValueError(
            "DATABASE_URL is required for Alembic migrations. "
            "Set DATABASE_URL in the environment before running 'alembic upgrade'."
        )

    # Ensure the async psycopg driver prefix is used for the async runner.
    # Sync prefix (postgresql://) is accepted and transparently converted.
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        url = url.replace("postgres://", "postgresql+psycopg://", 1)

    return url


# ---------------------------------------------------------------------------
# Offline migration mode — generates SQL without a live connection.
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Generates migration SQL without connecting to the database.
    Useful for reviewing SQL before applying it in production.
    """
    url = _get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Include schemas visible to the migration tool.
        include_schemas=False,
        # Compare server defaults to detect changes.
        compare_server_defaults=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration mode — connects to the database and applies migrations.
# ---------------------------------------------------------------------------


async def _run_async_migrations() -> None:
    """
    Core async migration runner.

    Creates a fresh async engine for migrations only — independent of the
    application runtime engine. Uses NullPool so no idle connections remain
    after the migration CLI exits.
    """
    url = _get_database_url()

    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
        connect_args={"sslmode": "require"},
        echo=False,  # Never echo SQL — would log parameterized values.
    )

    async with connectable.connect() as connection:
        await connection.run_sync(_run_migrations_with_connection)

    await connectable.dispose()


def _run_migrations_with_connection(sync_connection: object) -> None:
    """Configure context and run migrations using the provided sync connection."""
    context.configure(
        connection=sync_connection,  # type: ignore[arg-type]
        target_metadata=target_metadata,
        compare_server_defaults=True,
        include_schemas=False,
        # Render AS UUID for autogenerate where UUID columns are used.
        render_as_batch=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using the async engine.

    This is the standard path for 'alembic upgrade head' and similar commands.
    """
    import asyncio
    import sys

    # On Windows, psycopg async requires SelectorEventLoop instead of ProactorEventLoop.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(_run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point — Alembic calls this module; we dispatch based on mode.
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
