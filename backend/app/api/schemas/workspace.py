"""
GrowFlow — Workspace Pydantic API Schemas.

Defines schemas for S16 Blueprint Workspace and S17 Blueprint Document Viewer.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BlueprintSectionDetailSchema(BaseModel):
    """Schema for a single canonical blueprint section with structured and markdown views."""

    section_key: str
    title: str
    structured_content: dict[str, Any] = Field(default_factory=dict)
    markdown: str
    approved_at: datetime | None = None


class BlueprintDocumentSummarySchema(BaseModel):
    """Schema for list of available blueprint documents."""

    key: str
    title: str
    format: str = "markdown"
    section_order: int


class BlueprintDocumentSchema(BaseModel):
    """Schema for full document representation in S17 document viewer."""

    document_key: str
    title: str
    version: str = "1.0.0"
    status: str
    format: str = "markdown"
    markdown: str
    structured: dict[str, Any] | None = None
    available_documents: list[BlueprintDocumentSummarySchema] = Field(default_factory=list)
    approved_at: datetime | None = None
