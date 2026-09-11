"""
GrowFlow — FastAPI Database Session Dependencies.

Provides FastAPI Dependency Injection for async database sessions and
repositories. Integrates with the application lifecycle managed in
backend.app.infrastructure.database.lifecycle.

Architecture: 6A § 18 — DI supplies database sessions and repositories.

Session lifecycle per request:
  - A new AsyncSession is opened per request.
  - Committed on success, rolled back on exception.
  - Session is always closed after the request completes.

The session dependency is safe-to-inject even before the database is
initialised (raises a clear 503 rather than an obscure attribute error).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.infrastructure.database import lifecycle
from backend.app.shared.logging import get_logger

logger = get_logger("growflow.api.dependencies.database")


async def get_db_session() -> AsyncSession:  # type: ignore[return]
    """
    FastAPI dependency that yields an async database session.

    The session is scoped to the lifetime of a single HTTP request.
    It commits on successful response and rolls back on any unhandled
    exception. The session is always closed after yield.

    Raises:
        HTTPException 503: If the database session factory has not been
            initialised yet (e.g. startup failure or missing config).
    """
    session_factory = lifecycle.get_session_factory()
    if session_factory is None:
        logger.error("Database session factory not initialised")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available",
        )

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type alias for dependency injection throughout the API layer.
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
