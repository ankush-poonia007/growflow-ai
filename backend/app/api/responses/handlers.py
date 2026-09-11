"""
GrowFlow — Global Exception Handlers.

Translates domain exceptions, validation failures, HTTP errors,
and unexpected server exceptions into canonical API error responses.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.api.responses.base import error_response
from backend.app.shared.exceptions.base import GrowFlowException
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from fastapi import FastAPI, Request

logger = get_logger("growflow.exceptions")


async def growflow_exception_handler(_request: Request, exc: GrowFlowException) -> Any:
    """Handle all typed GrowFlow domain and application exceptions."""
    logger.warning(
        "Application exception handled",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
    )
    return error_response(
        message=exc.message,
        code=exc.code,
        details=exc.details,
        status_code=exc.status_code,
    )


async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> Any:
    """Handle FastAPI and Pydantic input validation failures."""
    details: list[dict[str, Any]] = []
    for err in exc.errors():
        loc = ".".join(str(item) for item in err.get("loc", []) if item != "body")
        details.append(
            {
                "field": loc or "root",
                "message": err.get("msg", "Invalid value"),
                "type": err.get("type", "validation_error"),
            }
        )

    logger.info("Request validation failed", error_count=len(details))
    return error_response(
        message="Request validation failed.",
        code="VALIDATION_ERROR",
        details=details,
        status_code=422,
    )


async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> Any:
    """Handle standard HTTP exceptions."""
    code = "HTTP_ERROR"
    if exc.status_code == 404:
        code = "NOT_FOUND"
    elif exc.status_code == 401:
        code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        code = "FORBIDDEN"
    elif exc.status_code == 405:
        code = "METHOD_NOT_ALLOWED"

    message = str(exc.detail) if exc.detail else "An HTTP error occurred."
    logger.info("HTTP exception handled", status_code=exc.status_code, code=code)
    return error_response(
        message=message,
        code=code,
        status_code=exc.status_code,
        headers=exc.headers,
    )


async def unhandled_exception_handler(_request: Request, exc: Exception) -> Any:
    """
    Catch-all for unhandled exceptions.

    Logs full diagnostic traceback server-side with correlation context.
    Returns safe generic message to client without disclosing internal details.
    """
    logger.exception("Unhandled server exception", exc_info=exc)
    return error_response(
        message="An internal server error occurred.",
        code="INTERNAL_SERVER_ERROR",
        status_code=500,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI application."""
    app.add_exception_handler(GrowFlowException, growflow_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
