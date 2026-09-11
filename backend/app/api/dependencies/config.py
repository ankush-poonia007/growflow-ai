"""
GrowFlow — Configuration Dependency Injection.

FastAPI dependency for accessing typed settings in route handlers.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from backend.app.config.settings import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_app_settings() -> Settings:
    """Return the active application settings singleton."""
    return get_settings()
