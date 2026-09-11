"""
API tests for runtime middleware (correlation, timing, security headers, CORS).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


@pytest.mark.api
def test_correlation_id_generated_if_absent(client: TestClient) -> None:
    """Verify correlation ID is generated and returned on response headers."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert "X-Correlation-ID" in response.headers
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Correlation-ID"]) > 10


@pytest.mark.api
def test_valid_correlation_id_propagated(client: TestClient) -> None:
    """Verify incoming valid correlation ID is preserved."""
    custom_id = "test-corr-abc-123"
    response = client.get(
        "/api/v1/health/live",
        headers={"X-Correlation-ID": custom_id},
    )
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == custom_id


@pytest.mark.api
def test_oversized_correlation_id_is_sanitized(client: TestClient) -> None:
    """Verify oversized or malicious correlation ID is replaced with clean UUID."""
    oversized = "a" * 200
    response = client.get(
        "/api/v1/health/live",
        headers={"X-Correlation-ID": oversized},
    )
    assert response.status_code == 200
    # Must have been replaced with a valid UUIDv4 (< 64 chars)
    assert response.headers["X-Correlation-ID"] != oversized
    assert len(response.headers["X-Correlation-ID"]) == 36


@pytest.mark.api
def test_request_timing_header(client: TestClient) -> None:
    """Verify X-Response-Time header is attached."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert "X-Response-Time" in response.headers
    assert response.headers["X-Response-Time"].endswith("ms")


@pytest.mark.api
def test_security_headers_present(client: TestClient) -> None:
    """Verify security headers are injected."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "0"
    assert "strict-origin" in response.headers["Referrer-Policy"]
    assert "accelerometer" in response.headers["Permissions-Policy"]


@pytest.mark.api
def test_cors_preflight(client: TestClient) -> None:
    """Verify CORS preflight handling."""
    response = client.options(
        "/api/v1/health/live",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
