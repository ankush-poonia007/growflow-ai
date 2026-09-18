"""
GrowFlow — Search API Request & Response Schemas (Batch 08 / Gate 13).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchResultItemSchema(BaseModel):
    """Normalized search result item schema."""

    id: str | None = None
    title: str
    subtitle: str
    resource_type: str
    url: str
    badge: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponseDataSchema(BaseModel):
    """Response payload schema for global search."""

    query: str
    workplace: str
    total: int
    results: list[SearchResultItemSchema]
