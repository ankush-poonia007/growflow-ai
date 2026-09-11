"""
GrowFlow — Resource and Role Authorization Foundation.

Implements application authorization policy primitives:
- Role validation
- Resource ownership validation
- Account status validation

Architecture ref:
  6D § 2  — Canonical security flow (HTTPS -> Auth -> CurrentUser -> Role -> Resource)
  6D § 16 — Role-based access control
  6D § 17 — Resource-based authorization
  6D § 21 — Project/Resource isolation (Default Deny)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.domain.identity.models import AccountStatus, CurrentUser, UserRole
from backend.app.shared.exceptions import AuthorizationException

if TYPE_CHECKING:
    from collections.abc import Iterable
    import uuid


def verify_account_active(current_user: CurrentUser) -> None:
    """
    Enforce that the authenticated user account is in ACTIVE lifecycle status.

    Raises:
        AuthorizationException: If the account is suspended or inactive (HTTP 403).
    """
    if current_user.status == AccountStatus.SUSPENDED:
        raise AuthorizationException(
            message="Account is suspended.",
            code="AUTH_ACCOUNT_SUSPENDED",
        )
    if current_user.status == AccountStatus.INACTIVE:
        raise AuthorizationException(
            message="Account is inactive.",
            code="AUTH_ACCOUNT_INACTIVE",
        )
    if not current_user.is_active:
        raise AuthorizationException(
            message="Account access restricted.",
            code="AUTH_ACCOUNT_RESTRICTED",
        )


def verify_role_access(
    current_user: CurrentUser,
    allowed_roles: Iterable[UserRole],
) -> None:
    """
    Enforce role-based access control (RBAC).

    Raises:
        AuthorizationException: If the current user's role is not in allowed_roles (HTTP 403).
    """
    roles_set = set(allowed_roles)
    if current_user.role not in roles_set:
        raise AuthorizationException(
            message=f"Role '{current_user.role.value}' is not authorized to access this resource.",
            code="AUTH_FORBIDDEN_ROLE",
        )


def verify_resource_ownership(
    current_user: CurrentUser,
    resource_owner_id: uuid.UUID | str,
    *,
    allow_admin: bool = False,
) -> None:
    """
    Enforce resource-based authorization.

    Verifies that the resource owner matches the authenticated user ID.
    By default, default-deny applies even to admin unless explicitly permitted by policy.

    Architecture ref: 6D § 17, § 23.

    Args:
        current_user: The authenticated CurrentUser identity.
        resource_owner_id: The owner user UUID of the targeted resource.
        allow_admin: Whether ADMIN role may bypass direct ownership check.

    Raises:
        AuthorizationException: If access is not authorized (HTTP 403).
    """
    if allow_admin and current_user.is_admin:
        return

    if str(current_user.user_id) != str(resource_owner_id):
        raise AuthorizationException(
            message="Access to this resource is denied.",
            code="AUTH_FORBIDDEN_RESOURCE",
        )
