"""
GrowFlow — Contact API Request & Response Schemas.

Enforces strict input validation, length bounds, and email verification
for public contact submissions per Phase 6A/6C specifications.
"""

from __future__ import annotations

from enum import StrEnum
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

# RFC 5322 compatible email format check
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class DiscussionTopic(StrEnum):
    """Supported contact inquiry topics matching P04 specification."""

    GENERAL = "general"
    PRODUCT = "product"
    PROJECT = "project"
    MENTORSHIP = "mentorship"
    ENGINEERING = "engineering"
    FEEDBACK = "feedback"
    OTHER = "other"


class ContactRequestSchema(BaseModel):
    """Inbound contact form request payload with anti-header injection validation."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Visitor full name (2-100 characters)",
        examples=["Jane Doe"],
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=254,
        description="Visitor valid email address for Reply-To",
        examples=["jane.doe@example.com"],
    )
    discussion_topic: DiscussionTopic = Field(
        ...,
        description="Primary category of inquiry",
        examples=[DiscussionTopic.ENGINEERING],
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Inquiry message content (10-2000 characters)",
        examples=["Interested in understanding how the multi-agent architecture handles state."],
    )

    @field_validator("name", mode="after")
    @classmethod
    def validate_no_crlf_in_name(cls, v: str) -> str:
        """Prevent CRLF / header injection attempts in the name field."""
        if "\r" in v or "\n" in v:
            raise ValueError("Name must not contain line breaks.")
        return v

    @field_validator("email", mode="after")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format and prevent CRLF."""
        if "\r" in v or "\n" in v:
            raise ValueError("Email must not contain line breaks.")
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email address format.")
        return v


class ContactResponseData(BaseModel):
    """Payload data embedded in the canonical success response."""

    submission_id: str = Field(description="Unique tracking ID for the submission")
    status: str = Field(description="Processing status of the inquiry")
    timestamp: str = Field(description="ISO-8601 submission timestamp")
