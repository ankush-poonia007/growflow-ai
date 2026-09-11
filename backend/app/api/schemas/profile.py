"""
GrowFlow — Profile API Request & Response Schemas.

Architecture ref:
  6C § 10 — User and Profile APIs
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Pydantic runtime schema validation
from typing import Any

from pydantic import BaseModel, Field


class UserUpdateSchema(BaseModel):
    """Payload to update current user's profile display details."""

    full_name: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=1024)


class UserResponseSchema(BaseModel):
    """Response schema for current user identity."""

    id: str
    email: str
    full_name: str
    role: str
    status: str
    avatar_url: str | None = None
    last_login_at: datetime | None = None
    created_at: datetime | None = None


class TechnologySkillSchema(BaseModel):
    """Skill mapping for student profile."""

    technology_id: str
    proficiency: str = Field(default="INTERMEDIATE")
    relationship_type: str = Field(default="KNOWN")


class StudentProfileUpdateSchema(BaseModel):
    """Payload to update student profile context."""

    bio: str | None = None
    goals: str | None = None
    interests: str | None = None
    technologies: list[TechnologySkillSchema] | None = None


class StudentProfileResponseSchema(BaseModel):
    """Response schema for student profile."""

    user_id: str
    student_id: str
    bio: str | None = None
    goals: str | None = None
    interests: str | None = None
    technologies: list[dict[str, Any]] = Field(default_factory=list)


class MentorProfileUpdateSchema(BaseModel):
    """Payload to update mentor profile context."""

    bio: str | None = None
    specialization: str | None = None


class MentorProfileResponseSchema(BaseModel):
    """Response schema for mentor profile."""

    user_id: str
    mentor_id: str
    bio: str | None = None
    specialization: str | None = None


class UserPreferencesUpdateSchema(BaseModel):
    """Payload to update user preferences."""

    email_notifications: bool | None = None
    timezone: str | None = None
    preferences: dict[str, Any] | None = None


class UserPreferencesResponseSchema(BaseModel):
    """Response schema for user preferences."""

    user_id: str
    email_notifications: bool
    timezone: str
    preferences: dict[str, Any] = Field(default_factory=dict)
