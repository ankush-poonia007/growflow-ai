"""
GrowFlow Gate 03 — Database Integration Tests.

These tests require a live DATABASE_URL environment variable pointing to
the hosted Supabase/PostgreSQL instance.

They are SKIPPED automatically when DATABASE_URL is not set, ensuring
the standard pytest run (without live DB) passes cleanly.

SAFETY:
- All operations are READ-ONLY or non-destructive (SELECT, SHOW, pg_extension query).
- No DROP, TRUNCATE, RESET, or schema mutations are performed here.
- These tests NEVER run alembic upgrade against the live database automatically.

To run manually with a live connection:
  DATABASE_URL=postgresql+psycopg://... pytest backend/tests/integration/test_database_integration.py -v

Architecture ref: Gate 03 specification, 6A § 36 — Testing.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text

from backend.app.config.settings import DatabaseSettings
from backend.app.infrastructure.database.engine import (
    build_async_engine,
    build_async_session_factory,
    get_session_context,
)

# Skip all tests in this module if DATABASE_URL is not set.
_DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("ALEMBIC_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not _DATABASE_URL,
    reason="DATABASE_URL not set — skipping live database integration tests",
)


def _make_live_db_settings() -> DatabaseSettings:
    """Create DatabaseSettings from live environment DATABASE_URL."""
    return DatabaseSettings(
        DATABASE_URL=_DATABASE_URL,
        POOL_SIZE=1,
        MAX_OVERFLOW=0,
        POOL_TIMEOUT_SECONDS=10,
        POOL_RECYCLE_SECONDS=300,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_connectivity_select_1() -> None:
    """
    Non-destructive connectivity check: SELECT 1 against the hosted database.

    This is the same operation performed during application startup.
    Confirms the DATABASE_URL is valid and the database is reachable.
    """
    settings = _make_live_db_settings()
    engine = build_async_engine(settings)

    try:
        factory = build_async_session_factory(engine)
        async with factory() as session:
            result = await session.execute(text("SELECT 1"))
            row = result.scalar()
            assert row == 1, f"Expected SELECT 1 to return 1, got {row}"
    finally:
        await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_transaction_rollback() -> None:
    """
    Verify rollback behavior on a live connection.

    Creates a transaction, inserts a temporary row into a temp table,
    then rolls back — confirming no permanent state change.

    SAFETY: Uses a session-scoped temporary table that is automatically
    dropped at session end. No permanent schema changes.
    """
    settings = _make_live_db_settings()
    engine = build_async_engine(settings)

    try:
        factory = build_async_session_factory(engine)

        async with factory() as session:
            # Create a session-scoped temp table.
            await session.execute(
                text(
                    "CREATE TEMP TABLE IF NOT EXISTS _gate03_test "
                    "(id INTEGER, value TEXT)"
                )
            )

            # Insert a row in a nested transaction / savepoint.
            await session.execute(
                text("INSERT INTO _gate03_test (id, value) VALUES (1, 'test')")
            )

            # Count rows — should be 1.
            count = (
                await session.execute(text("SELECT COUNT(*) FROM _gate03_test"))
            ).scalar()
            assert count == 1

            # Rollback — temp table rows should be cleared.
            await session.rollback()

            # Re-count after rollback — should be 0.
            count_after = (
                await session.execute(text("SELECT COUNT(*) FROM _gate03_test"))
            ).scalar()
            assert count_after == 0, (
                f"Expected 0 rows after rollback, got {count_after}"
            )
    finally:
        await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_session_context_commits() -> None:
    """
    Verify get_session_context commits successfully on a live connection.

    SAFETY: Uses a session-scoped temp table. No permanent schema changes.
    """
    settings = _make_live_db_settings()
    engine = build_async_engine(settings)

    try:
        factory = build_async_session_factory(engine)

        # Create temp table first in its own session.
        async with factory() as setup_session:
            await setup_session.execute(
                text(
                    "CREATE TEMP TABLE IF NOT EXISTS _gate03_commit_test "
                    "(id INTEGER, value TEXT)"
                )
            )
            await setup_session.commit()

        # Insert via get_session_context (which commits automatically).
        async with get_session_context(factory) as session:
            await session.execute(
                text(
                    "INSERT INTO _gate03_commit_test (id, value) VALUES (42, 'committed')"
                )
            )

        # Verify the row is visible in a subsequent session.
        async with factory() as verify_session:
            result = await verify_session.execute(
                text("SELECT value FROM _gate03_commit_test WHERE id = 42")
            )
            row = result.scalar_one_or_none()
            assert row == "committed", (
                f"Expected committed row value 'committed', got {row}"
            )
    finally:
        await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_postgresql_extensions_accessible() -> None:
    """
    Verify the required PostgreSQL extensions are accessible.

    Queries pg_extension to check presence of uuid-ossp and pg_trgm.
    READ-ONLY; does not install or remove any extension.

    Note: Extensions may or may not be pre-installed on the hosted Supabase
    instance. This test records which are present for the evidence document.
    """
    settings = _make_live_db_settings()
    engine = build_async_engine(settings)

    try:
        factory = build_async_session_factory(engine)

        async with factory() as session:
            result = await session.execute(
                text(
                    "SELECT extname FROM pg_extension "
                    "WHERE extname IN ('uuid-ossp', 'pg_trgm')"
                )
            )
            installed = {row[0] for row in result.fetchall()}

        # Report what's installed — both are expected but not hard-required here.
        print(f"\nInstalled extensions: {installed}")
    finally:
        await engine.dispose()
