"""
GrowFlow — AI Infrastructure Package.

Provides the centralized AI Provider Gateway, key pool management,
model capability policies, and provider adapters.
"""

from backend.app.infrastructure.ai.adapters.base import AIProviderAdapter
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.adapters.openrouter import OpenRouterAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.key_pool import APIKeyPoolManager
from backend.app.infrastructure.ai.models import (
    AICapabilityDowngradeException,
    AIErrorCategory,
    AIExecutionResult,
    AIGenerationRequest,
    AIProviderUnavailableException,
    AIQuotaExhaustedException,
    AISchemaValidationException,
    AIUsageMetadata,
    KeyHealthState,
    KeyPoolEntry,
    ProviderCapability,
)
from backend.app.infrastructure.ai.policy import AIModelPolicy

__all__ = [
    "AICapabilityDowngradeException",
    "AIErrorCategory",
    "AIExecutionResult",
    "AIGenerationRequest",
    "AIModelPolicy",
    "AIProviderAdapter",
    "AIProviderGateway",
    "AIProviderUnavailableException",
    "AIQuotaExhaustedException",
    "AISchemaValidationException",
    "AIUsageMetadata",
    "APIKeyPoolManager",
    "KeyHealthState",
    "KeyPoolEntry",
    "MockAIProviderAdapter",
    "OpenRouterAdapter",
    "ProviderCapability",
]
