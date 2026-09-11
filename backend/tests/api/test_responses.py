"""
API tests for canonical success and error response envelopes.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
import pytest

from backend.app.api.responses import (
    error_response,
    register_exception_handlers,
    success_response,
)
from backend.app.shared.exceptions import (
    BusinessRuleException,
    NotFoundException,
)


@pytest.mark.api
def test_canonical_success_helper() -> None:
    """Verify success_response constructor outputs canonical JSON format."""
    res = success_response(
        message="Item created.",
        data={"id": "item_123"},
        metadata={"total": 1},
        status_code=201,
    )
    assert res.status_code == 201
    import json

    body = json.loads(res.body)
    assert body["success"] is True
    assert body["message"] == "Item created."
    assert body["data"] == {"id": "item_123"}
    assert body["metadata"] == {"total": 1}


@pytest.mark.api
def test_canonical_error_helper() -> None:
    """Verify error_response constructor outputs canonical JSON format."""
    res = error_response(
        message="Operation failed.",
        code="TEST_ERROR",
        details=[{"field": "name", "issue": "required"}],
        status_code=400,
    )
    assert res.status_code == 400
    import json

    body = json.loads(res.body)
    assert body["success"] is False
    assert body["message"] == "Operation failed."
    assert body["data"] is None
    assert body["error"]["code"] == "TEST_ERROR"
    assert len(body["error"]["details"]) == 1


@pytest.mark.api
def test_domain_exception_handled_canonically() -> None:
    """Verify application exceptions return canonical error responses with correct status codes."""
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/raise-not-found")
    async def raise_not_found() -> None:
        raise NotFoundException("Project not found.")

    @test_app.get("/raise-business-error")
    async def raise_business_error() -> None:
        raise BusinessRuleException("Cannot complete task in current phase.")

    with TestClient(test_app) as tc:
        r1 = tc.get("/raise-not-found")
        assert r1.status_code == 404
        b1 = r1.json()
        assert b1["success"] is False
        assert b1["message"] == "Project not found."
        assert b1["error"]["code"] == "RESOURCE_NOT_FOUND"

        r2 = tc.get("/raise-business-error")
        assert r2.status_code == 400
        b2 = r2.json()
        assert b2["success"] is False
        assert b2["message"] == "Cannot complete task in current phase."
        assert b2["error"]["code"] == "BUSINESS_RULE_VIOLATION"


@pytest.mark.api
def test_unhandled_exception_does_not_leak_internals() -> None:
    """Verify unhandled 500 errors return safe message with no traceback leak."""
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/raise-unhandled")
    async def raise_unhandled() -> None:
        raise RuntimeError("Sensitive internal database exception: password=secret123")

    with TestClient(test_app, raise_server_exceptions=False) as tc:
        r = tc.get("/raise-unhandled")
        assert r.status_code == 500
        body = r.json()
        assert body["success"] is False
        assert body["message"] == "An internal server error occurred."
        assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
        # Verify no traceback or secret leakage
        assert "password" not in str(body)
        assert "RuntimeError" not in str(body)


@pytest.mark.api
def test_validation_error_returns_canonical_error() -> None:
    """Verify Pydantic request validation error returns 422 canonical format."""
    test_app = FastAPI()
    register_exception_handlers(test_app)

    class TestPayload(BaseModel):
        name: str
        count: int

    @test_app.post("/test-validation")
    async def test_validation(payload: TestPayload) -> dict[str, str]:
        return {"result": payload.name}

    with TestClient(test_app) as tc:
        r = tc.post("/test-validation", json={"name": "test", "count": "not_an_int"})
        assert r.status_code == 422
        body = r.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert len(body["error"]["details"]) > 0
