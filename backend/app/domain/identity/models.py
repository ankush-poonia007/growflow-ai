"""
GrowFlow — Identity Domain Models.

Defines the canonical application identity types used throughout
the authentication and authorization boundary.

Architecture ref:
  6D § 7  — Canonical roles: ADMIN, MENTOR, STUDENT
  6D § 8  — Account statuses: ACTIVE, INACTIVE, SUSPENDED
  6D § 14 — Authentication dependency and CurrentUser
  6D § 15 — Authorization context
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import uuid


class UserRole(StrEnum):
    """
    Canonical GrowFlow application roles.

    Roles are backend-enforced authorization attributes.
    They are never sourced from or trusted based on client-supplied values.
    Architecture ref: 6D § 7.
    """

    ADMIN = "ADMIN"
    MENTOR = "MENTOR"
    STUDENT = "STUDENT"


class AccountStatus(StrEnum):
    """
    Canonical application account lifecycle states.

    - ACTIVE: normal access per role
    - INACTIVE: login/access restricted by account policy
    - SUSPENDED: access denied until explicitly restored by admin

    Architecture ref: 6D § 8.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


@dataclass(frozen=True)
class CurrentUser:
    """
    Immutable request-scoped authenticated identity.

    Produced by get_current_user() after successful JWT verification,
    database lookup, and account status validation.

    Architecture ref: 6D § 14-15 — Authentication dependency,
    Authorization context.

    Fields:
        user_id:    GrowFlow application UUID (same as Supabase auth sub).
        email:      User's email address from the verified JWT / application record.
        role:       Application role (ADMIN, MENTOR, STUDENT).
        status:     Account lifecycle status.
        full_name:  Display name; may be empty for newly linked accounts.
    """

    user_id: uuid.UUID
    email: str
    role: UserRole
    status: AccountStatus
    full_name: str = field(default="")

    @property
    def is_active(self) -> bool:
        """True when the account is in ACTIVE status."""
        return self.status == AccountStatus.ACTIVE

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_mentor(self) -> bool:
        return self.role == UserRole.MENTOR

    @property
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT

    def __repr__(self) -> str:
        return f"<CurrentUser user_id={self.user_id} role={self.role} status={self.status}>"
