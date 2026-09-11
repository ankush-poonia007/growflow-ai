"""
GrowFlow — Database Lifecycle Management.

Manages the async engine and session factory as application-scoped singletons
integrated with the FastAPI lifespan context manager.

This module is the single owner of the engine and session factory singletons.
It is called from the application factory's lifespan hook (factory.py).

SAFETY RULES (enforced by this module):
- No schema mutation, DDL, or Alembic upgrade is ever called here.
- No database URL is logged.
- The connectivity check (ping) is a read-only SELECT 1; it is non-destructive.
- Startup failure is logged and re-raised so the operator is informed immediately.
- Teardown always disposes the engine to return pooled connections cleanly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import text

from backend.app.infrastructure.database.engine import (
    build_async_engine,
    build_async_session_factory,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

    from backend.app.config.settings import DatabaseSettings


logger = get_logger("growflow.infrastructure.database.lifecycle")

# Module-level singletons — owned exclusively by this module.
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def startup(db_settings: DatabaseSettings) -> None:
    """
    Initialise the database engine and session factory.

    Called once during application startup from the FastAPI lifespan hook.
    Performs a non-destructive SELECT 1 connectivity check against the
    hosted Supabase instance to confirm the configuration is valid.

    Args:
        db_settings: Typed database configuration from application settings.

    Raises:
        ValueError: If DATABASE_URL is not configured.
        Exception: If the hosted database cannot be reached at startup.
    """
    global _engine, _session_factory

    if not db_settings.DATABASE_URL:
        logger.warning(
            "DATABASE_URL not configured — database engine not initialised. "
            "Gate 03 connectivity requires DATABASE_URL."
        )
        return

    logger.info("Initialising database engine and session factory")

    _engine = build_async_engine(db_settings)
    _session_factory = build_async_session_factory(_engine)

    # Non-destructive connectivity check — SELECT 1.
    try:
        async with _session_factory() as session:
            await session.execute(text("SELECT 1"))
        logger.info("Database connectivity confirmed (SELECT 1 succeeded)")
    except Exception as exc:
        logger.error(
            "Database connectivity check failed during startup",
            error=str(exc),
            # Connection string intentionally omitted.
        )
        # Dispose partially-initialized engine before re-raising.
        await _engine.dispose()
        _engine = None
        _session_factory = None
        raise


async def shutdown() -> None:
    """
    Gracefully dispose the database engine on application shutdown.

    Closes all pooled connections and releases resources. Called from
    the FastAPI lifespan hook's finally block.
    """
    global _engine, _session_factory

    if _engine is not None:
        logger.info("Disposing database engine")
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database engine disposed")


def get_engine() -> AsyncEngine | None:
    """Return the current engine singleton, or None if not initialised."""
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession] | None:
    """Return the current session factory singleton, or None if not initialised."""
    return _session_factory


def is_initialised() -> bool:
    """Return True if the engine and session factory are ready."""
    return _engine is not None and _session_factory is not None
