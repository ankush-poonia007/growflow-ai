"""
GrowFlow — AI Model Policy and Capability Management.

Maps logical capabilities to configured models and enforces the strict
non-downgrade capability fallback rule: REASONING >= STANDARD >= FAST.

Architecture ref:
  6E § 16 — Model policy
  6E § 17 — Model registry
  6E § 18 — Model fallback
  Gate 09 Decision A4 — Provider capability policy
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.app.infrastructure.ai.models import (
    CAPABILITY_RANKS,
    AICapabilityDowngradeException,
    ProviderCapability,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.config.settings import AISettings

logger = get_logger("growflow.infrastructure.ai.policy")


class AIModelPolicy:
    """Central authority for resolving logical capabilities and enforcing fallback constraints."""

    def __init__(self, settings: AISettings) -> None:
        self._settings = settings

    def resolve_model(self, capability: ProviderCapability) -> str:
        """Map a logical capability to its primary configured model name."""
        match capability:
            case ProviderCapability.FAST:
                return self._settings.FAST_MODEL
            case ProviderCapability.STANDARD:
                return self._settings.STANDARD_MODEL
            case ProviderCapability.REASONING:
                return self._settings.REASONING_MODEL
            case ProviderCapability.EMBEDDING:
                return self._settings.EMBEDDING_MODEL
            case _:
                return self._settings.DEFAULT_MODEL

    def infer_model_capability(self, model: str) -> ProviderCapability:
        """Infer the logical capability tier of a given model name."""
        if model == self._settings.REASONING_MODEL:
            return ProviderCapability.REASONING
        if model == self._settings.STANDARD_MODEL:
            return ProviderCapability.STANDARD
        if model == self._settings.FAST_MODEL:
            return ProviderCapability.FAST
        if model == self._settings.EMBEDDING_MODEL:
            return ProviderCapability.EMBEDDING

        # Conservative fallback heuristic for common model naming
        lower = model.lower()
        if "o1" in lower or "reasoning" in lower:
            return ProviderCapability.REASONING
        if "mini" in lower or "flash" in lower or "fast" in lower:
            return ProviderCapability.FAST
        if "embed" in lower:
            return ProviderCapability.EMBEDDING
        return ProviderCapability.STANDARD

    def resolve_fallback(
        self,
        requested_capability: ProviderCapability,
        explicit_fallback_model: str | None = None,
    ) -> str:
        """
        Resolve an eligible fallback model for the requested capability.

        Enforces: REASONING >= STANDARD >= FAST.
        Raises AICapabilityDowngradeException if the fallback model violates non-downgrade.
        """
        if requested_capability == ProviderCapability.EMBEDDING:
            # Embedding cannot substitute for LLM, and LLM cannot substitute for embedding
            return self._settings.EMBEDDING_MODEL

        fallback_model = explicit_fallback_model or self._settings.FALLBACK_MODEL
        fallback_capability = self.infer_model_capability(fallback_model)

        req_rank = CAPABILITY_RANKS.get(requested_capability, 0)
        fall_rank = CAPABILITY_RANKS.get(fallback_capability, 0)

        if fall_rank < req_rank:
            logger.warning(
                "Fallback model violates capability non-downgrade policy",
                requested_capability=requested_capability.value,
                fallback_model=fallback_model,
                fallback_capability=fallback_capability.value,
                requested_rank=req_rank,
                fallback_rank=fall_rank,
            )
            raise AICapabilityDowngradeException(
                f"Capability downgrade forbidden: requested {requested_capability.value} "
                f"cannot fallback to {fallback_model} ({fallback_capability.value})"
            )

        logger.info(
            "Capability-compliant fallback resolved",
            requested_capability=requested_capability.value,
            fallback_model=fallback_model,
            fallback_capability=fallback_capability.value,
        )
        return fallback_model
