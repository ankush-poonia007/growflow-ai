"""
GrowFlow — Correlation and Request Context.

Stores correlation ID and request ID in asyncio contextvars
for propagation across asynchronous execution boundaries and logging.
"""

from __future__ import annotations

from contextvars import ContextVar
import uuid

_correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_correlation_id() -> str | None:
    """Return the current correlation ID, or None if outside a request context."""
    return _correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context."""
    _correlation_id_ctx.set(correlation_id)


def get_request_id() -> str | None:
    """Return the current request ID, or None if outside a request context."""
    return _request_id_ctx.get()


def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context."""
    _request_id_ctx.set(request_id)


def clear_context() -> None:
    """Reset the context variables."""
    _correlation_id_ctx.set(None)
    _request_id_ctx.set(None)


def generate_correlation_id() -> str:
    """Generate a standard UUIDv4 correlation ID."""
    return str(uuid.uuid4())
