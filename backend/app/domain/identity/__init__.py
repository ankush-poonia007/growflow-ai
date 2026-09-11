"""
GrowFlow — Domain Identity Package.

Exports canonical roles, account lifecycle states, CurrentUser identity representation,
and authorization verification functions.
"""

from backend.app.domain.identity.authorization import (
    verify_account_active,
    verify_resource_ownership,
    verify_role_access,
)
from backend.app.domain.identity.models import AccountStatus, CurrentUser, UserRole

__all__ = [
    "AccountStatus",
    "CurrentUser",
    "UserRole",
    "verify_account_active",
    "verify_resource_ownership",
    "verify_role_access",
]
