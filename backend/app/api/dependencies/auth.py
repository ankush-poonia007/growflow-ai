"""
GrowFlow — Authentication & Authorization FastAPI Dependencies.

Provides centralized FastAPI dependency injection for:
- get_current_user: Token extraction, cryptographic verification, DB lookup, account validation
- RequireStudent: Enforces STUDENT role
- RequireMentor: Enforces MENTOR role
- RequireAdmin: Enforces ADMIN role
- RequireRole: Enforces custom role sets

Architecture ref:
  6C § 2  — Canonical dependency boundary
  6D § 2  — HTTPS -> Auth -> CurrentUser -> Role -> Resource
  6D § 14 — get_current_user() specification
  6D § 16 — Role-based access control
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from backend.app.api.dependencies.config import (  # noqa: TC001 — FastAPI runtime dependency injection
    SettingsDep,
)
from backend.app.api.dependencies.database import (  # noqa: TC001 — FastAPI runtime dependency injection
    DbSession,
)
from backend.app.domain.identity import (
    CurrentUser,
    UserRole,
    verify_account_active,
    verify_role_access,
)
from backend.app.infrastructure.repositories.user_repository import UserRepository
from backend.app.shared.exceptions import AuthenticationException
from backend.app.shared.security.jwt import SupabaseJWTVerifier


async def get_current_user(
    request: Request,
    db: DbSession,
    settings: SettingsDep,
) -> CurrentUser:
    """
    FastAPI dependency resolving the authenticated CurrentUser identity.

    Extracts the Bearer token from the Authorization header, cryptographically
    validates it against the configured Supabase JWT secret, retrieves the corresponding
    application user record from the database, enforces account lifecycle rules, and
    returns the canonical CurrentUser identity.

    Raises:
        AuthenticationException: If the token is missing, malformed, expired,
            invalid, or if the user is not found in the database (HTTP 401).
        AuthorizationException: If the user's account is suspended or inactive (HTTP 403).
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise AuthenticationException(
            message="Authorization header is missing.",
            code="AUTH_MISSING_TOKEN",
        )

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationException(
            message="Authorization header must follow 'Bearer <token>' format.",
            code="AUTH_INVALID_TOKEN_FORMAT",
        )

    raw_token = parts[1]

    # 1. Cryptographic JWT verification (PyJWT HS256)
    verifier = SupabaseJWTVerifier(settings=settings)
    verified_token = verifier.verify(raw_token)

    # 2. Application identity lookup (GrowFlow users table)
    user_repo = UserRepository(session=db)
    user_record = await user_repo.get_by_id(verified_token.user_id)
    if user_record is None:
        raise AuthenticationException(
            message="User account not found in application database.",
            code="AUTH_USER_NOT_FOUND",
        )

    current_user = user_record.to_current_user()

    # 3. Account status validation (fail closed on SUSPENDED / INACTIVE)
    verify_account_active(current_user)

    return current_user


# Type alias for standard authenticated endpoint dependency
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


class RequireRole:
    """
    Reusable dependency callable enforcing role-based access control.

    Example:
        @router.get("/mentor-only")
        async def endpoint(user: Annotated[CurrentUser, Depends(RequireRole(UserRole.MENTOR))]):
            ...
    """

    def __init__(self, *allowed_roles: UserRole) -> None:
        self.allowed_roles = set(allowed_roles)

    def __call__(self, current_user: CurrentUserDep) -> CurrentUser:
        verify_role_access(current_user, self.allowed_roles)
        return current_user


def require_roles(*allowed_roles: UserRole) -> RequireRole:
    """Helper factory creating a RequireRole dependency callable."""
    return RequireRole(*allowed_roles)


# Canonical pre-configured role dependencies
RequireStudent = Annotated[CurrentUser, Depends(RequireRole(UserRole.STUDENT))]
RequireMentor = Annotated[CurrentUser, Depends(RequireRole(UserRole.MENTOR))]
RequireAdmin = Annotated[CurrentUser, Depends(RequireRole(UserRole.ADMIN))]
