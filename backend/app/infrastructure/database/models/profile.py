"""
GrowFlow — Profile & Technology SQLAlchemy ORM Models.

Defines ORM mappings for:
- student_profiles
- mentor_profiles
- user_preferences
- technologies
- student_technologies

Architecture ref:
  6B § 5.2 — student_profiles
  6B § 5.3 — mentor_profiles
  6B § 5.4 — user_preferences
  6B § 5.5 — technologies
  6B § 5.6 — student_technologies
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import JSON, Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.domain.identity.profile_models import (
    MentorProfile,
    StudentProfile,
    StudentTechnology,
    Technology,
    TechnologyRelationshipType,
    UserPreference,
)
from backend.app.infrastructure.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

# JSONB column type with standard JSON fallback for non-PostgreSQL dialects
JSON_TYPE = JSON().with_variant(postgresql.JSONB(), "postgresql")


class StudentProfileModel(Base, TimestampMixin):
    """SQLAlchemy model for student_profiles table."""

    __tablename__ = "student_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    student_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    interests: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_domain(self) -> StudentProfile:
        return StudentProfile(
            user_id=UUID(self.user_id),
            student_id=self.student_id,
            bio=self.bio,
            goals=self.goals,
            interests=self.interests,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class MentorProfileModel(Base, TimestampMixin):
    """SQLAlchemy model for mentor_profiles table."""

    __tablename__ = "mentor_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    mentor_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    specialization: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_domain(self) -> MentorProfile:
        return MentorProfile(
            user_id=UUID(self.user_id),
            mentor_id=self.mentor_id,
            bio=self.bio,
            specialization=self.specialization,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class UserPreferenceModel(Base, TimestampMixin):
    """SQLAlchemy model for user_preferences table."""

    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON_TYPE, default=dict, nullable=False)

    def to_domain(self) -> UserPreference:
        return UserPreference(
            user_id=UUID(self.user_id),
            email_notifications=self.email_notifications,
            timezone=self.timezone,
            preferences=self.preferences or {},
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class TechnologyModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for technologies table."""

    __tablename__ = "technologies"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    def to_domain(self) -> Technology:
        return Technology(
            id=UUID(str(self.id)),
            name=self.name,
            category=self.category,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class StudentTechnologyModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy model for student_technologies table."""

    __tablename__ = "student_technologies"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "technology_id",
            "relationship_type",
            name="uq_student_tech_rel",
        ),
    )

    student_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    technology_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("technologies.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    proficiency: Mapped[str] = mapped_column(String(50), default="INTERMEDIATE", nullable=False)
    relationship_type: Mapped[str] = mapped_column(
        String(50), default=TechnologyRelationshipType.KNOWN.value, nullable=False
    )

    def to_domain(self) -> StudentTechnology:
        return StudentTechnology(
            id=UUID(str(self.id)),
            student_id=UUID(self.student_id),
            technology_id=UUID(self.technology_id),
            proficiency=self.proficiency,
            relationship_type=TechnologyRelationshipType(self.relationship_type),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
