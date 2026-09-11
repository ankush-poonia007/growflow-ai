"""
GrowFlow — Correlation ID Middleware.

Extracts, sanitizes, or generates request correlation IDs.
Propagates correlation ID through contextvars and response headers.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.shared.logging.context import (
    clear_context,
    generate_correlation_id,
    set_correlation_id,
    set_request_id,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from starlette.requests import Request
    from starlette.responses import Response

# Allow alphanumeric, hyphen, underscore, dot between 1 and 64 chars
VALID_CORRELATION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{1,64}$")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware ensuring every HTTP request has a validated correlation ID
    and request ID bound to contextvars and emitted on response headers.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        raw_corr_id = request.headers.get("X-Correlation-ID")
        raw_req_id = request.headers.get("X-Request-ID")

        if raw_corr_id and VALID_CORRELATION_ID_PATTERN.match(raw_corr_id.strip()):
            correlation_id = raw_corr_id.strip()
        else:
            correlation_id = generate_correlation_id()

        if raw_req_id and VALID_CORRELATION_ID_PATTERN.match(raw_req_id.strip()):
            request_id = raw_req_id.strip()
        else:
            request_id = correlation_id

        set_correlation_id(correlation_id)
        set_request_id(request_id)

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            clear_context()
