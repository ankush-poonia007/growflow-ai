"""
GrowFlow — Application Factory & Lifecycle Composition.

Separates application creation, middleware, exception boundaries,
and routing from the thin ASGI entrypoint in main.py.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from backend.app.api.middleware import register_middleware
from backend.app.api.responses.handlers import register_exception_handlers
from backend.app.api.router import api_router, api_v1_router
from backend.app.api.routes import health
from backend.app.config.settings import Environment, Settings, get_settings
from backend.app.infrastructure.database import lifecycle as db_lifecycle
from backend.app.shared.logging import get_logger, setup_logging

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def app_lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifecycle context manager.

    Initializes logging, validates runtime settings, and safely teardown resources.
    Startup performs no destructive DB operations, migrations, or external calls.
    """
    settings = get_settings()
    setup_logging(settings)
    logger = get_logger("growflow.lifecycle")

    logger.info(
        "Application starting up",
        app=settings.app.NAME,
        env=settings.app.ENV.value,
        port=settings.app.PORT,
    )

    # Gate 03: initialise database engine and session factory.
    # If DATABASE_URL is not configured the lifecycle logs a warning and
    # continues — this allows tests without a live database to still boot.
    try:
        await db_lifecycle.startup(settings.database)
        # Gate 14 / Batch 4: Recover orphaned RUNNING blueprint jobs on startup
        session_factory = db_lifecycle.get_session_factory()
        if session_factory:
            try:
                async with session_factory() as session:
                    from backend.app.infrastructure.repositories.blueprint_repository import (
                        BlueprintRepository,
                    )

                    repo = BlueprintRepository(session)
                    recovered = await repo.recover_orphaned_jobs(
                        error_message="Execution interrupted by server restart"
                    )
                    await session.commit()
                    if recovered > 0:
                        logger.warning(
                            "Recovered orphaned blueprint generation jobs on startup",
                            recovered_count=recovered,
                        )
            except Exception as rec_exc:
                logger.error(
                    "Failed to recover orphaned blueprint jobs during startup",
                    error=str(rec_exc),
                )
    except Exception as exc:
        logger.error(
            "Database startup failed — application will start without DB connectivity",
            error=str(exc),
        )

    try:
        yield
    finally:
        logger.info("Application shutting down")
        await db_lifecycle.shutdown()


def create_app(settings: Settings | None = None) -> FastAPI:
    """
    Application factory building the complete FastAPI runtime.

    Composes configuration, logging, exception handlers, middleware,
    and the /api/v1 router foundation.
    """
    app_settings = settings or get_settings()

    is_production = app_settings.app.ENV == Environment.PRODUCTION

    app = FastAPI(
        title=app_settings.app.NAME,
        version="0.1.0",
        description="GrowFlow — AI-Powered Internship Project Platform API",
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
        lifespan=app_lifespan,
    )

    # 1. Register global exception handlers
    register_exception_handlers(app)

    # 2. Register runtime middleware (security, timing, correlation, CORS)
    register_middleware(app, app_settings)

    # 3. Mount API v1 router (/api/v1/...) and /api router
    app.include_router(api_v1_router)
    app.include_router(api_router)

    # 4. Mount convenience top-level health probe (/health/...)
    app.include_router(health.router)

    # 5. Root service metadata endpoint
    @app.get("/", tags=["Root"], include_in_schema=False)
    async def root_info() -> dict[str, str]:
        return {
            "name": app_settings.app.NAME,
            "version": "0.1.0",
            "status": "running",
            "api": "/api/v1",
        }

    return app
