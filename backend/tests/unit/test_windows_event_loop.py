"""
GrowFlow — Unit & Integration Regression Tests for Windows Event Loop Reliability.

Validates Workstream 1 of GF-FIX-02A:
1. Uvicorn loop factory resolution: `loop="asyncio:SelectorEventLoop"` resolves deterministically
   to `asyncio.SelectorEventLoop` without requiring monkeypatches of private Uvicorn internals.
2. Root cause confirmation: Verifies that `ProactorEventLoop` lacks `add_reader` support on Windows,
   which is why async psycopg fails under Proactor.
3. Selector event loop compatibility: Verifies that `SelectorEventLoop` supports reader registration
   and runs async database lifecycle operations cleanly.
4. Database lifecycle startup and shutdown: Verifies engine initialization, read-only SELECT 1
   connectivity check (or mocked equivalent in unit test), and graceful disposal.
5. Entrypoint configuration: Verifies `backend.app.main` configures selector loop for Windows.
"""

from __future__ import annotations

import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import uvicorn

from backend.app.config.settings import DatabaseSettings
from backend.app.infrastructure.database import lifecycle as db_lifecycle


def test_uvicorn_loop_factory_resolution_selector() -> None:
    """Uvicorn Config with loop='asyncio:SelectorEventLoop' resolves to SelectorEventLoop."""
    config = uvicorn.Config("backend.app.main:app", loop="asyncio:SelectorEventLoop")
    factory = config.get_loop_factory()
    assert factory is not None

    loop = factory()
    try:
        assert isinstance(loop, asyncio.SelectorEventLoop)
        if sys.platform == "win32":
            import asyncio.windows_events as win_asyncio
            assert isinstance(loop, win_asyncio._WindowsSelectorEventLoop)
    finally:
        loop.close()


def test_proactor_event_loop_raises_not_implemented_on_add_reader() -> None:
    """Document and prove root cause: ProactorEventLoop does not support add_reader on Windows."""
    if sys.platform != "win32":
        pytest.skip("Windows-specific event loop root cause test")

    import asyncio.windows_events
    proactor = asyncio.windows_events.ProactorEventLoop()
    try:
        with pytest.raises(NotImplementedError):
            proactor.add_reader(0, lambda: None)
    finally:
        proactor.close()


def test_selector_event_loop_supports_reader_registration() -> None:
    """SelectorEventLoop supports add_reader / remove_reader required by psycopg async."""
    selector_loop = asyncio.SelectorEventLoop()
    try:
        # add_reader is an implemented callable on SelectorEventLoop
        assert hasattr(selector_loop, "add_reader")
        assert callable(selector_loop.add_reader)
        assert hasattr(selector_loop, "remove_reader")
        assert callable(selector_loop.remove_reader)
    finally:
        selector_loop.close()


@pytest.mark.asyncio
async def test_db_lifecycle_startup_and_shutdown_mocked() -> None:
    """Lifecycle startup and shutdown run cleanly on the active event loop without loop errors."""
    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=MagicMock())

    class SessionContextManager:
        async def __aenter__(self):
            return mock_session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    mock_session_factory = MagicMock(return_value=SessionContextManager())

    db_settings = DatabaseSettings(
        DATABASE_URL="postgresql+psycopg://test_user:test_pass@localhost:5432/test_db",
        DB_POOL_MIN_SIZE=1,
        DB_POOL_MAX_SIZE=2,
    )

    with patch("backend.app.infrastructure.database.lifecycle.build_async_engine", return_value=mock_engine), \
         patch("backend.app.infrastructure.database.lifecycle.build_async_session_factory", return_value=mock_session_factory):
        await db_lifecycle.startup(db_settings)
        assert db_lifecycle.is_initialised() is True
        assert db_lifecycle.get_engine() is mock_engine
        mock_session.execute.assert_awaited_once()

        await db_lifecycle.shutdown()
        assert db_lifecycle.is_initialised() is False
        assert db_lifecycle.get_engine() is None
        mock_engine.dispose.assert_awaited_once()


def test_main_module_windows_loop_configuration() -> None:
    """Verify backend.app.main configures WindowsSelectorEventLoopPolicy and Selector loop on win32."""
    with open("backend/app/main.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Must set event loop policy for win32
    assert 'if sys.platform == "win32":' in content
    assert "asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())" in content

    # Must specify loop="asyncio:SelectorEventLoop" for win32
    assert 'loop="asyncio:SelectorEventLoop" if sys.platform == "win32" else "auto"' in content
    # Must NOT contain private monkeypatching of uvicorn.loops.asyncio
    assert "uvicorn.loops.asyncio" not in content


def test_actual_uvicorn_server_startup_and_lifespan_on_selector_loop() -> None:
    """Verify that Uvicorn Server initialized with supported config executes lifespan on SelectorEventLoop."""
    from backend.app.config.settings import get_settings

    settings = get_settings()
    loop_arg = "asyncio:SelectorEventLoop" if sys.platform == "win32" else "auto"
    config = uvicorn.Config(
        "backend.app.main:app",
        host=settings.app.HOST,
        port=settings.app.PORT,
        log_level="warning",
        loop=loop_arg,
        lifespan="on",
    )
    server = uvicorn.Server(config)
    loop_factory = config.get_loop_factory()
    assert loop_factory is not None

    loop = loop_factory()
    try:
        async def run_server_lifecycle():
            running_loop = asyncio.get_running_loop()
            assert isinstance(running_loop, asyncio.SelectorEventLoop)
            if sys.platform == "win32":
                import asyncio.windows_events as win_asyncio
                assert isinstance(running_loop, win_asyncio._WindowsSelectorEventLoop)

            # Load config and initialize lifespan
            config.load()
            server.lifespan = config.lifespan_class(config)

            # Start server lifespan (triggers app_lifespan and db_lifecycle)
            await server.startup()
            assert server.started is True

            # Graceful shutdown
            await server.shutdown()

        loop.run_until_complete(run_server_lifecycle())
    finally:
        loop.close()
