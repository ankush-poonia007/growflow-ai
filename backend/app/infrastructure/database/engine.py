"""
GrowFlow — SQLAlchemy Engine and Connection Foundation.

Establishes the async SQLAlchemy engine targeting hosted Supabase/PostgreSQL.
Uses psycopg (psycopg3) async driver as approved by the project dependency set.

Architecture: 6A/6B — Infrastructure layer; no business logic.
Driver: postgresql+psycopg (psycopg3 native async)
Pool: NullPool for serverless/short-lived connections; configurable for long-running.
SSL: enabled by default for hosted Supabase connections.

SAFETY RULES (enforced by this module):
- Never log the database URL, credentials, or any connection string.
- Never call destructive DDL (DROP, TRUNCATE, RESET) from this module.
- Never initiate schema changes or Alembic upgrades from this module.
- Connection string is sourced solely from typed Settings; no os.environ access.
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from backend.app.config.settings import DatabaseSettings

logger = get_logger("growflow.infrastructure.database.engine")


def build_async_engine(db_settings: DatabaseSettings) -> AsyncEngine:
    """
    Build and return a configured async SQLAlchemy engine.

    Uses the psycopg (psycopg3) async driver with project-approved pool settings.
    The DATABASE_URL is consumed from typed settings only — never logged.

    Pool strategy:
      - pool_size / max_overflow / pool_timeout / pool_recycle from settings.
      - pool_pre_ping=True for hosted connection health validation without mutations.

    Args:
        db_settings: Typed DatabaseSettings instance from the application config.

    Returns:
        Configured AsyncEngine bound to the hosted Supabase/PostgreSQL instance.

    Raises:
        ValueError: If DATABASE_URL is not configured.
    """
    if not db_settings.DATABASE_URL:
        raise ValueError(
            "DATABASE_URL is not configured. "
            "Set DATABASE_URL in the environment to connect to the hosted Supabase database."
        )

    url = db_settings.DATABASE_URL

    # Ensure the async psycopg driver prefix is present.
    # Accepts both bare postgresql:// and postgresql+psycopg:// forms.
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        url = url.replace("postgres://", "postgresql+psycopg://", 1)

    engine_kwargs: dict[str, Any] = {
        "echo": False,  # Never echo SQL; would log parameterized values.
        "pool_pre_ping": True,
        "pool_size": db_settings.POOL_SIZE,
        "max_overflow": db_settings.MAX_OVERFLOW,
        "pool_timeout": db_settings.POOL_TIMEOUT_SECONDS,
        "pool_recycle": db_settings.POOL_RECYCLE_SECONDS,
        "connect_args": {
            # psycopg3 sslmode — Supabase requires SSL.
            "sslmode": "require",
        },
    }

    engine = create_async_engine(url, **engine_kwargs)

    logger.info(
        "Async database engine created",
        pool_size=db_settings.POOL_SIZE,
        max_overflow=db_settings.MAX_OVERFLOW,
        pool_recycle=db_settings.POOL_RECYCLE_SECONDS,
        # URL intentionally omitted — never log credentials.
    )

    return engine


def build_async_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Build and return the async session factory for the given engine.

    Session configuration:
      - expire_on_commit=False: prevents lazy-load errors after commit in async context.
      - autocommit=False: explicit transaction control per use-case (6A § 26).
      - autoflush=False: prevents unintended flushes; application controls flush timing.

    Args:
        engine: The configured AsyncEngine instance.

    Returns:
        async_sessionmaker configured for GrowFlow's transaction model.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@contextlib.asynccontextmanager
async def get_session_context(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager providing a single unit-of-work session.

    Transaction boundaries:
      - Begins a transaction implicitly on entry.
      - Commits on successful exit.
      - Rolls back on any exception, then re-raises.
      - Always closes the session on exit.

    This is the primary session provider for application services and repositories.

    Args:
        session_factory: The async_sessionmaker to create sessions from.

    Yields:
        AsyncSession bound to an active transaction.
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
