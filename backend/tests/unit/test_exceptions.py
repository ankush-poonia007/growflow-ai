"""
Unit tests for the centralized exception hierarchy.
"""

from __future__ import annotations

import pytest

from backend.app.shared.exceptions import (
    AIException,
    AuthenticationException,
    AuthorizationException,
    BusinessRuleException,
    ConflictException,
    GrowFlowException,
    InfrastructureException,
    IntegrationException,
    NotFoundException,
    RAGException,
    StorageException,
    ValidationException,
)


@pytest.mark.unit
def test_growflow_exception_base() -> None:
    """Verify base exception attributes and representation."""
    exc = GrowFlowException("Base error", code="CUSTOM_CODE", status_code=418)
    assert exc.message == "Base error"
    assert exc.code == "CUSTOM_CODE"
    assert exc.status_code == 418
    assert exc.details == []
    assert "CUSTOM_CODE" in repr(exc)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("exc_cls", "expected_code", "expected_status"),
    [
        (ValidationException, "VALIDATION_ERROR", 422),
        (AuthenticationException, "AUTH_INVALID_CREDENTIALS", 401),
        (AuthorizationException, "AUTH_UNAUTHORIZED", 403),
        (NotFoundException, "RESOURCE_NOT_FOUND", 404),
        (ConflictException, "RESOURCE_CONFLICT", 409),
        (BusinessRuleException, "BUSINESS_RULE_VIOLATION", 400),
        (IntegrationException, "INTEGRATION_ERROR", 502),
        (AIException, "AI_PROVIDER_ERROR", 502),
        (RAGException, "RAG_ERROR", 500),
        (StorageException, "STORAGE_ERROR", 500),
        (InfrastructureException, "INFRASTRUCTURE_ERROR", 500),
    ],
)
def test_subclasses_status_and_codes(
    exc_cls: type[GrowFlowException], expected_code: str, expected_status: int
) -> None:
    """Verify default error codes and HTTP status codes for all exception subclasses."""
    exc = exc_cls()
    assert exc.code == expected_code
    assert exc.status_code == expected_status
    assert issubclass(exc_cls, GrowFlowException)
