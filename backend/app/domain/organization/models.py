"""
GrowFlow — Organization Domain Models.

Defines domain entities and enums for mentor groups and student group memberships.

Architecture ref:
  6B § 6.1 — groups
  6B § 6.2 — group_memberships
  6C § 11  — Group APIs
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    import uuid


class GroupStatus(StrEnum):
    """Lifecycle status of a mentor group."""

    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class GroupMembershipStatus(StrEnum):
    """Membership state of a student in a group."""

    ACTIVE = "ACTIVE"
    LEFT = "LEFT"
    REMOVED = "REMOVED"


@dataclass
class Group:
    """Mentor-managed student group."""

    id: uuid.UUID
    mentor_id: uuid.UUID
    name: str
    join_code: str
    status: GroupStatus = GroupStatus.ACTIVE
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class GroupMembership:
    """Student membership within a mentor group."""

    id: uuid.UUID
    group_id: uuid.UUID
    student_id: uuid.UUID
    status: GroupMembershipStatus = GroupMembershipStatus.ACTIVE
    joined_at: datetime | None = None
    left_at: datetime | None = None
    created_at: datetime | None = None
