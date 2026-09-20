"""
GrowFlow — Provider Adapter Abstract Base Class.

Defines the low-level transport interface for AI model communication.
Separates provider-specific wire protocols, HTTP details, and vendor payloads
from the centralized AI Provider Gateway.

Architecture ref:
  6E § 7  — Provider abstraction
  6E § 80 — External integration boundaries
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import BaseModel

    from backend.app.infrastructure.ai.models import ProviderRawResponse


class AIProviderAdapter(ABC):
    """Abstract interface that all provider integration adapters must implement."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Normalized name of the provider adapter (e.g. 'openrouter', 'mock')."""
        ...

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        api_key: str,
        key_alias: str,
        max_tokens: int = 4000,
        temperature: float = 0.2,
        timeout_seconds: float = 60.0,
        correlation_id: str | None = None,
    ) -> ProviderRawResponse:
        """
        Execute a standard completion request through the provider.

        Raises:
            ProviderError: On classified communication, rate limit, auth, or server errors.
        """
        ...

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        api_key: str,
        key_alias: str,
        schema: type[BaseModel],
        max_tokens: int = 4000,
        temperature: float = 0.2,
        timeout_seconds: float = 60.0,
        correlation_id: str | None = None,
    ) -> ProviderRawResponse:
        """
        Execute a structured JSON synthesis request conforming to the specified Pydantic schema.

        Raises:
            ProviderError: On classified communication, rate limit, auth, or server errors.
        """
        ...
