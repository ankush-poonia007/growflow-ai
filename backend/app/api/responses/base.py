"""
GrowFlow — Canonical API Response Contracts.

Defines the standard success and error response schemas per Phase 6A/6C specifications.
All standard JSON endpoints adhere to these canonical contracts.
"""

from __future__ import annotations

from typing import Any, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class SuccessResponse[DataT](BaseModel):
    """Canonical success response envelope."""

    success: bool = True
    message: str
    data: DataT | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ErrorDetail(BaseModel):
    """Detailed field-level validation or domain error information."""

    field: str | None = None
    message: str
    type: str | None = None


class ErrorInfo(BaseModel):
    """Machine-readable error information."""

    code: str
    details: list[Any] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Canonical error response envelope."""

    success: bool = False
    message: str
    data: None = None
    error: ErrorInfo


def success_response(
    message: str,
    data: Any = None,
    metadata: dict[str, Any] | None = None,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Construct a canonical JSON success response."""
    payload = {
        "success": True,
        "message": message,
        "data": jsonable_encoder(data) if data is not None else {},
        "metadata": metadata or {},
    }
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers=headers,
    )


def error_response(
    message: str,
    code: str,
    details: list[Any] | None = None,
    status_code: int = 400,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Construct a canonical JSON error response."""
    payload = {
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": code,
            "details": jsonable_encoder(details) if details else [],
        },
    }
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers=headers,
    )
