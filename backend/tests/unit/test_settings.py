"""
Unit tests for typed application configuration.
"""

from __future__ import annotations

import os
from unittest.mock import patch

from pydantic import ValidationError
import pytest

from backend.app.config.settings import AppSettings, Environment, Settings, get_settings


@pytest.mark.unit
def test_valid_settings_loading() -> None:
    """Verify that settings can be instantiated and typed fields are accessible."""
    settings = get_settings()
    assert settings.app.NAME == "GrowFlow"
    assert settings.app.PORT == 8000
    assert settings.app.ENV in list(Environment)
    assert isinstance(settings.app.CORS_ORIGINS, list)
    assert len(settings.app.SECRET_KEY) > 0


@pytest.mark.unit
def test_missing_secret_key_fails_closed() -> None:
    """Verify that missing APP_SECRET_KEY raises ValidationError."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValidationError) as exc_info:
            AppSettings(_env_file=None)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("APP_SECRET_KEY",) for e in errors)


@pytest.mark.unit
def test_cors_origins_parsing() -> None:
    """Verify that comma-delimited strings are parsed into lists."""
    app_settings = AppSettings(
        APP_SECRET_KEY="test-secret-key-min-16-bytes",
        APP_CORS_ORIGINS="http://localhost:3000, https://growflow.app ",
        _env_file=None,
    )
    assert app_settings.CORS_ORIGINS == [
        "http://localhost:3000",
        "https://growflow.app",
    ]


@pytest.mark.unit
def test_five_openrouter_keys_support() -> None:
    """Verify that exactly 5 OpenRouter keys are supported in configuration."""
    settings = Settings()
    # Check that all 5 key attributes exist on AISettings
    assert hasattr(settings.ai, "OPENROUTER_API_KEY_1")
    assert hasattr(settings.ai, "OPENROUTER_API_KEY_2")
    assert hasattr(settings.ai, "OPENROUTER_API_KEY_3")
    assert hasattr(settings.ai, "OPENROUTER_API_KEY_4")
    assert hasattr(settings.ai, "OPENROUTER_API_KEY_5")
    assert isinstance(settings.ai.active_keys, list)


@pytest.mark.unit
def test_safe_dict_redacts_secrets() -> None:
    """Verify safe_dict does not contain raw secrets."""
    settings = get_settings()
    safe = settings.safe_dict()

    # Secret key should not appear
    assert "SECRET_KEY" not in safe["app"]
    assert "APP_SECRET_KEY" not in safe["app"]
    # Database URL should not be exposed
    assert "DATABASE_URL" not in safe["database"]
    # Raw API keys should not be exposed
    assert "OPENROUTER_API_KEY_1" not in safe["ai"]


@pytest.mark.unit
def test_settings_repr_does_not_leak_secrets() -> None:
    """Verify repr(settings) shows only high-level metadata."""
    settings = get_settings()
    repr_str = repr(settings)
    assert settings.app.SECRET_KEY not in repr_str
    assert "env=" in repr_str
    assert "app_name=" in repr_str
