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
from backend.app.domain.identity.profile_models import (
    MentorProfile,
    StudentProfile,
    StudentTechnology,
    Technology,
    TechnologyRelationshipType,
    UserPreference,
)

__all__ = [
    "AccountStatus",
    "CurrentUser",
    "MentorProfile",
    "StudentProfile",
    "StudentTechnology",
    "Technology",
    "TechnologyRelationshipType",
    "UserPreference",
    "UserRole",
    "verify_account_active",
    "verify_resource_ownership",
    "verify_role_access",
]
