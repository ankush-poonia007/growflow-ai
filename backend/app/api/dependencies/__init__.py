"""GrowFlow API dependencies package."""

from backend.app.api.dependencies.auth import (
    CurrentUserDep,
    RequireAdmin,
    RequireMentor,
    RequireRole,
    RequireStudent,
    get_current_user,
    require_roles,
)
from backend.app.api.dependencies.config import SettingsDep, get_app_settings
from backend.app.api.dependencies.correlation import (
    CorrelationIdDep,
    RequestIdDep,
    get_current_correlation_id,
    get_current_request_id,
)
from backend.app.api.dependencies.database import DbSession, get_db_session

__all__ = [
    "CorrelationIdDep",
    "CurrentUserDep",
    "DbSession",
    "RequestIdDep",
    "RequireAdmin",
    "RequireMentor",
    "RequireRole",
    "RequireStudent",
    "SettingsDep",
    "get_app_settings",
    "get_current_correlation_id",
    "get_current_request_id",
    "get_current_user",
    "get_db_session",
    "require_roles",
]
