"""
GrowFlow — AI Infrastructure Models and Contracts.

Defines the core capability model, health state machine enums, error classifications,
and request/response contracts for the centralized AI Provider Gateway.

Architecture ref:
  6E § 12 — Key health states
  6E § 16 — Model policy and capabilities
  6E § 18 — Model fallback
  6E § 19 — Error classification
  Gate 09 Decision A4 — Provider capability policy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from backend.app.shared.exceptions.base import AIException

if TYPE_CHECKING:
    from datetime import datetime


class ProviderCapability(StrEnum):
    """
    Authoritative logical capabilities for AI model operations.

    Ordering rule: REASONING >= STANDARD >= FAST.
    EMBEDDING is distinct and non-substitutable.
    """

    FAST = "FAST"
    STANDARD = "STANDARD"
    REASONING = "REASONING"
    EMBEDDING = "EMBEDDING"


# Numeric rank for hierarchical non-downgrade enforcement
CAPABILITY_RANKS: dict[ProviderCapability, int] = {
    ProviderCapability.FAST: 1,
    ProviderCapability.STANDARD: 2,
    ProviderCapability.REASONING: 3,
}


class KeyHealthState(StrEnum):
    """Operational health state of a provider API key in the pool."""

    ACTIVE = "ACTIVE"
    RATE_LIMITED = "RATE_LIMITED"
    COOLDOWN = "COOLDOWN"
    FAILED = "FAILED"
    DISABLED = "DISABLED"


class AIErrorCategory(StrEnum):
    """Operational classification of provider execution failures."""

    RATE_LIMITED = "RATE_LIMITED"
    TRANSIENT_SERVER = "TRANSIENT_SERVER"
    TIMEOUT = "TIMEOUT"
    AUTH_ERROR = "AUTH_ERROR"
    NON_RETRYABLE = "NON_RETRYABLE"
    SCHEMA_INVALID = "SCHEMA_INVALID"


class AIQuotaExhaustedException(AIException):
    """Raised when all provider keys are exhausted and no fallback satisfies capability."""

    def __init__(
        self,
        message: str = "AI usage limit reached. No eligible keys or fallbacks available.",
        details: list[Any] | None = None,
        code: str = "QUOTA_EXHAUSTED",
    ) -> None:
        super().__init__(message=message, details=details, code=code)


class AIProviderUnavailableException(AIException):
    """Raised when the AI provider infrastructure is unavailable."""

    def __init__(
        self,
        message: str = "AI provider service is currently unavailable.",
        details: list[Any] | None = None,
        code: str = "PROVIDER_UNAVAILABLE",
    ) -> None:
        super().__init__(message=message, details=details, code=code)


class AICapabilityDowngradeException(AIException):
    """Raised when fallback model cannot satisfy minimum requested capability."""

    def __init__(
        self,
        message: str = "Capability downgrade forbidden by policy.",
        details: list[Any] | None = None,
        code: str = "CAPABILITY_DOWNGRADE_FORBIDDEN",
    ) -> None:
        super().__init__(message=message, details=details, code=code)


class AISchemaValidationException(AIException):
    """Raised when model structured output cannot be validated against Pydantic schema."""

    def __init__(
        self,
        message: str = "AI structured output failed Pydantic schema validation.",
        details: list[Any] | None = None,
        code: str = "SCHEMA_VALIDATION_ERROR",
    ) -> None:
        super().__init__(message=message, details=details, code=code)


@dataclass
class KeyPoolEntry:
    """Represents a single API key slot within the five-key pool."""

    key_alias: str
    raw_key: str | None = field(default=None, repr=False)
    status: KeyHealthState = KeyHealthState.DISABLED
    last_used_at: datetime | None = None
    last_success_at: datetime | None = None
    failure_count: int = 0
    rate_limit_count: int = 0
    cooldown_until: datetime | None = None


@dataclass(frozen=True)
class AIUsageMetadata:
    """Token consumption and estimated cost metadata from provider responses."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float | None = None


@dataclass(frozen=True)
class AIGenerationRequest:
    """Typed parameters for invoking an AI model execution."""

    prompt: str
    system_prompt: str = "You are the GrowFlow Architectural Intelligence Engine."
    capability: ProviderCapability = ProviderCapability.STANDARD
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int = 4000
    timeout_seconds: float | None = None
    correlation_id: str | None = None
    execution_id: str | None = None


@dataclass(frozen=True)
class AIExecutionResult[T]:
    """Normalized output from the AI Provider Gateway."""

    content: T | str
    raw_text: str
    provider: str
    model: str
    capability: ProviderCapability
    key_alias: str
    latency_ms: float
    usage: AIUsageMetadata | None = None
    retry_count: int = 0
    correlation_id: str | None = None
    execution_id: str | None = None


@dataclass(frozen=True)
class ProviderRawResponse:
    """Low-level transport response from an AI provider adapter."""

    text: str
    usage: AIUsageMetadata | None = None
    latency_ms: float = 0.0
    raw_response: dict[str, Any] | None = None


class ProviderError(Exception):
    """Low-level error raised by provider adapters with classified operational metadata."""

    def __init__(
        self,
        category: AIErrorCategory,
        message: str,
        status_code: int | None = None,
        retry_after: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.message = message
        self.status_code = status_code
        self.retry_after = retry_after
        self.details = details or {}
