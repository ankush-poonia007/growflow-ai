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
from backend.app.api.dependencies.services import (
    GroupServiceDep,
    OutboxServiceDep,
    ProfileServiceDep,
    ProjectDefinitionServiceDep,
    ProjectServiceDep,
    get_group_service,
    get_outbox_service,
    get_profile_service,
    get_project_definition_service,
    get_project_service,
)

__all__ = [
    "CorrelationIdDep",
    "CurrentUserDep",
    "DbSession",
    "GroupServiceDep",
    "OutboxServiceDep",
    "ProfileServiceDep",
    "ProjectDefinitionServiceDep",
    "ProjectServiceDep",
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
    "get_group_service",
    "get_outbox_service",
    "get_profile_service",
    "get_project_definition_service",
    "get_project_service",
    "require_roles",
]
