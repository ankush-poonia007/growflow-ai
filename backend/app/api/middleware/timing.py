"""
GrowFlow — Request Timing and Access Logging Middleware.

Measures request latency, records structured access logs,
and attaches performance headers to HTTP responses.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from starlette.requests import Request
    from starlette.responses import Response

logger = get_logger("growflow.access")


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Measures request execution time and emits structured access telemetry."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Response-Time"] = f"{elapsed_ms:.2f}ms"

        # Log access event without logging request body or sensitive credentials
        logger.info(
            "HTTP request completed",
            method=method,
            path=path,
            status_code=response.status_code,
            duration_ms=round(elapsed_ms, 2),
        )

        return response
