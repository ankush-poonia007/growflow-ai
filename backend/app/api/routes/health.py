"""
GrowFlow — Operational Health and Readiness Endpoints.

Implements liveness, readiness, and aggregated health checks
per Phase 6A, 6C, and 6J architecture specifications.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from backend.app.api.dependencies.config import (  # noqa: TC001 — FastAPI runtime dependency injection
    SettingsDep,
)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/live",
    summary="Process Liveness Probe",
    description="Confirms that the FastAPI process is running and responding.",
    status_code=status.HTTP_200_OK,
)
async def liveness_probe() -> dict[str, Any]:
    """Liveness probe confirming application process is running."""
    return {
        "status": "alive",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/ready",
    summary="Application Readiness Probe",
    description="Verifies that core runtime dependencies and configuration are ready.",
    status_code=status.HTTP_200_OK,
)
async def readiness_probe(settings: SettingsDep) -> JSONResponse:
    """Readiness probe verifying runtime readiness without checking unconfigured external services."""
    now_iso = datetime.now(UTC).isoformat()

    # Verify that configuration is valid and secret key is present
    if not settings.app.SECRET_KEY:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "reason": "Application secret key is unconfigured.",
                "timestamp": now_iso,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ready",
            "environment": settings.app.ENV.value,
            "timestamp": now_iso,
        },
    )


@router.get(
    "",
    summary="Aggregated Health Status",
    description="Provides an aggregated overview of runtime health without exposing sensitive details.",
    status_code=status.HTTP_200_OK,
)
async def health_overview(settings: SettingsDep) -> dict[str, Any]:
    """Aggregated operational health check."""
    # Gate 03: include database connectivity status (non-secret boolean).
    from backend.app.infrastructure.database import lifecycle as db_lifecycle

    db_configured = bool(settings.database.DATABASE_URL)
    db_connected = db_lifecycle.is_initialised()

    db_status: str
    if db_connected:
        db_status = "connected"
    elif not db_configured:
        db_status = "unconfigured"
    else:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "service": settings.app.NAME,
        "version": "0.1.0",
        "environment": settings.app.ENV.value,
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": {
            "runtime": {"status": "healthy"},
            "configuration": {
                "status": "healthy",
                "configured": True,
            },
            "database": {
                "status": db_status,
                "configured": db_configured,
                "connected": db_connected,
            },
        },
    }
