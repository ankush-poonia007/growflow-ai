"""
GrowFlow — Root Test Configuration and Shared Fixtures.

Provides fixtures for typed settings, FastAPI test client, and test isolation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.testclient import TestClient
import pytest

from backend.app.config.settings import Environment, Settings, get_settings
from backend.app.factory import create_app

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> Generator[None, None]:
    """Ensure settings cache is cleared before and after each test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def test_settings() -> Settings:
    """Return test settings with deterministic testing defaults."""
    settings = get_settings()
    settings.app.ENV = Environment.TEST
    settings.app.TESTING = True
    return settings


@pytest.fixture
def app(test_settings: Settings):
    """Return configured FastAPI test application."""
    return create_app(settings=test_settings)


@pytest.fixture
def client(app) -> Generator[TestClient, None]:
    """Return HTTP test client bound to the test application."""
    with TestClient(app, base_url="http://testserver") as test_client:
        yield test_client
