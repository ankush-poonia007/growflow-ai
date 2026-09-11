"""
GrowFlow — Profile & Preference Domain Models.

Defines domain entities and enums for student profiles, mentor profiles,
user preferences, and technology catalog mappings.

Architecture ref:
  6B § 5.2 — student_profiles
  6B § 5.3 — mentor_profiles
  6B § 5.4 — user_preferences
  6B § 5.5 — technologies
  6B § 5.6 — student_technologies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime
    import uuid


class TechnologyRelationshipType(StrEnum):
    """Types of relationships a student has with a technology."""

    KNOWN = "KNOWN"
    WORKED_WITH = "WORKED_WITH"
    INTERESTED_IN = "INTERESTED_IN"


@dataclass
class StudentProfile:
    """Domain representation of a student profile."""

    user_id: uuid.UUID
    student_id: str
    bio: str | None = None
    goals: str | None = None
    interests: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class MentorProfile:
    """Domain representation of a mentor profile."""

    user_id: uuid.UUID
    mentor_id: str
    bio: str | None = None
    specialization: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class UserPreference:
    """Domain representation of user-level preferences."""

    user_id: uuid.UUID
    email_notifications: bool = True
    timezone: str = "UTC"
    preferences: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Technology:
    """Canonical technology catalogue entity."""

    id: uuid.UUID
    name: str
    category: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class StudentTechnology:
    """Student technology skill relationship."""

    id: uuid.UUID
    student_id: uuid.UUID
    technology_id: uuid.UUID
    proficiency: str = "INTERMEDIATE"
    relationship_type: TechnologyRelationshipType = TechnologyRelationshipType.KNOWN
    created_at: datetime | None = None
    updated_at: datetime | None = None
