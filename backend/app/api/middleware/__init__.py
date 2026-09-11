"""GrowFlow API middleware package."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.middleware.correlation import CorrelationIdMiddleware
from backend.app.api.middleware.security import SecurityHeadersMiddleware
from backend.app.api.middleware.timing import RequestTimingMiddleware
from backend.app.config.settings import Settings

__all__ = [
    "CorrelationIdMiddleware",
    "RequestTimingMiddleware",
    "SecurityHeadersMiddleware",
    "register_middleware",
]


def register_middleware(app: FastAPI, settings: Settings) -> None:
    """
    Register application middleware in explicit order of execution.

    Order:
    1. CorrelationIdMiddleware (outermost: establishes correlation context)
    2. RequestTimingMiddleware (times execution, logs request completion)
    3. SecurityHeadersMiddleware (applies security headers)
    4. CORSMiddleware (handles CORS preflights and headers)
    """
    # Middleware added later runs earlier in the request pipeline
    cors_origins = (
        settings.app.CORS_ORIGINS
        if isinstance(settings.app.CORS_ORIGINS, list)
        else [settings.app.CORS_ORIGINS]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=settings.security.CORS_ALLOW_CREDENTIALS,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID", "X-Request-ID", "X-Response-Time"],
    )
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
