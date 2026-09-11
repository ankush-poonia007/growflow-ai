"""
API tests for health, liveness, and readiness endpoints.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.testclient import TestClient
import pytest

from backend.app.factory import create_app

if TYPE_CHECKING:
    from backend.app.config.settings import Settings


@pytest.mark.api
def test_liveness_probe(client: TestClient) -> None:
    """Verify liveness probe returns 200 alive."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "timestamp" in data


@pytest.mark.api
def test_top_level_liveness_probe(client: TestClient) -> None:
    """Verify top-level /health/live works identically."""
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


@pytest.mark.api
def test_readiness_probe_healthy(client: TestClient) -> None:
    """Verify readiness probe returns 200 ready when properly configured."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "environment" in data
    assert "timestamp" in data


@pytest.mark.api
def test_top_level_readiness_probe(client: TestClient) -> None:
    """Verify top-level /health/ready works identically."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


@pytest.mark.api
def test_health_overview(client: TestClient) -> None:
    """Verify aggregated health endpoint returns expected components."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "GrowFlow"
    assert "version" in data
    assert "environment" in data
    assert data["checks"]["runtime"]["status"] == "healthy"
    assert data["checks"]["configuration"]["status"] == "healthy"


@pytest.mark.api
def test_readiness_fails_when_unconfigured(test_settings: Settings) -> None:
    """Verify readiness probe returns 503 when critical config is missing."""
    test_settings.app.SECRET_KEY = ""
    unready_app = create_app(settings=test_settings)
    with TestClient(unready_app) as unready_client:
        response = unready_client.get("/api/v1/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "not_ready"
