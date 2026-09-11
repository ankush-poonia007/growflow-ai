"""
GrowFlow — Correlation Dependency Injection.

FastAPI dependency for accessing request correlation and tracking identifiers.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from backend.app.shared.logging.context import (
    generate_correlation_id,
    get_correlation_id,
    get_request_id,
)


def get_current_correlation_id() -> str:
    """Return the current correlation ID or generate a fallback if called outside middleware."""
    corr_id = get_correlation_id()
    return corr_id if corr_id else generate_correlation_id()


def get_current_request_id() -> str:
    """Return the current request ID or generate a fallback if called outside middleware."""
    req_id = get_request_id()
    return req_id if req_id else generate_correlation_id()


CorrelationIdDep = Annotated[str, Depends(get_current_correlation_id)]
RequestIdDep = Annotated[str, Depends(get_current_request_id)]
