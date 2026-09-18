"""
GrowFlow — Group API Request & Response Schemas.

Architecture ref:
  6C § 11 — Group APIs
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003 — Pydantic runtime schema validation

from pydantic import BaseModel, Field


class GroupCreateSchema(BaseModel):
    """Payload to create a new mentor group."""

    name: str = Field(min_length=1, max_length=255)


class GroupUpdateSchema(BaseModel):
    """Payload to update an existing group."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    status: str | None = Field(default=None)


class GroupJoinSchema(BaseModel):
    """Payload for a student to join a group via join code."""

    join_code: str = Field(min_length=3, max_length=50)


class GroupResponseSchema(BaseModel):
    """Response schema for a group."""

    id: str
    mentor_id: str
    name: str
    join_code: str
    status: str
    mentor_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GroupMembershipResponseSchema(BaseModel):
    """Response schema for group membership."""

    id: str
    group_id: str
    student_id: str
    status: str
    joined_at: datetime | None = None
    left_at: datetime | None = None
    group_name: str | None = None
    mentor_name: str | None = None
    join_code: str | None = None


class GroupStudentResponseSchema(BaseModel):
    """Response schema for a student enrolled in a group."""

    student_id: str
    email: str
    full_name: str
    status: str
    joined_at: datetime | None = None
