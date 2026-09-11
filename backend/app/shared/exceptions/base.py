"""
GrowFlow — Centralized Exception Hierarchy.

All application and domain exceptions inherit from GrowFlowException.
Global exception handlers translate these into canonical API error responses.
"""

from __future__ import annotations

from typing import Any


class GrowFlowException(Exception):  # noqa: N818 — Frozen architecture name per Phase 6A Section 22
    """Base exception for all domain and application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        details: list[Any] | None = None,
        status_code: int = 500,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details if details is not None else []
        self.status_code = status_code

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} code={self.code} message={self.message}>"


class ValidationException(GrowFlowException):
    """Input or contract validation failure."""

    def __init__(
        self,
        message: str = "Validation failed.",
        details: list[Any] | None = None,
        code: str = "VALIDATION_ERROR",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=422,
        )


class AuthenticationException(GrowFlowException):
    """Authentication failed or credentials invalid."""

    def __init__(
        self,
        message: str = "Authentication failed.",
        details: list[Any] | None = None,
        code: str = "AUTH_INVALID_CREDENTIALS",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=401,
        )


class AuthorizationException(GrowFlowException):
    """Access denied or permission boundary violation."""

    def __init__(
        self,
        message: str = "Access denied.",
        details: list[Any] | None = None,
        code: str = "AUTH_UNAUTHORIZED",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=403,
        )


class NotFoundException(GrowFlowException):
    """Requested resource was not found."""

    def __init__(
        self,
        message: str = "Resource not found.",
        details: list[Any] | None = None,
        code: str = "RESOURCE_NOT_FOUND",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=404,
        )


class ConflictException(GrowFlowException):
    """Resource state conflict or duplicate detected."""

    def __init__(
        self,
        message: str = "Resource conflict.",
        details: list[Any] | None = None,
        code: str = "RESOURCE_CONFLICT",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=409,
        )


class BusinessRuleException(GrowFlowException):
    """Deterministic business logic rule violation."""

    def __init__(
        self,
        message: str = "Business rule violation.",
        details: list[Any] | None = None,
        code: str = "BUSINESS_RULE_VIOLATION",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=400,
        )


class IntegrationException(GrowFlowException):
    """External third-party service integration failure."""

    def __init__(
        self,
        message: str = "Integration service failure.",
        details: list[Any] | None = None,
        code: str = "INTEGRATION_ERROR",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=502,
        )


class AIException(GrowFlowException):
    """AI provider or model gateway execution failure."""

    def __init__(
        self,
        message: str = "AI service failure.",
        details: list[Any] | None = None,
        code: str = "AI_PROVIDER_ERROR",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=502,
        )


class RAGException(GrowFlowException):
    """RAG index or retrieval failure."""

    def __init__(
        self,
        message: str = "RAG retrieval failure.",
        details: list[Any] | None = None,
        code: str = "RAG_ERROR",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=500,
        )


class StorageException(GrowFlowException):
    """Object storage access or operation failure."""

    def __init__(
        self,
        message: str = "Storage operation failure.",
        details: list[Any] | None = None,
        code: str = "STORAGE_ERROR",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=500,
        )


class InfrastructureException(GrowFlowException):
    """Core infrastructure or connection failure."""

    def __init__(
        self,
        message: str = "Infrastructure failure.",
        details: list[Any] | None = None,
        code: str = "INFRASTRUCTURE_ERROR",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            details=details,
            status_code=500,
        )
