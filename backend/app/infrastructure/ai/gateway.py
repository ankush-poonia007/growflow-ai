"""
GrowFlow — AI Provider Gateway.

Centralized provider boundary and model execution gateway.
Separates agents from provider-specific HTTP transport, manages a health-aware
five-key OpenRouter pool, enforces capability non-downgrade fallback, supports
structured Pydantic generation, and captures execution/usage metadata.

Architecture ref:
  6E § 6  — AI Provider Gateway
  6E § 7  — Provider Abstraction
  6E § 10 — Five-Key API Pool
  6E § 12 — Key Health States
  6E § 13 — Key Selection Strategy
  6E § 18 — Model Fallback
  6E § 20 — Retry Policy
  6E § 21 — Rate Limits and Cooldowns
  6E § 22 — Quota Exhaustion
  6E § 44 — Structured Output Contracts
  Gate 09 Decision A4 — Provider capability policy
"""

from __future__ import annotations

import asyncio
import json
import random
from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel, ValidationError

from backend.app.config.settings import AISettings, get_settings
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.adapters.openrouter import OpenRouterAdapter

if TYPE_CHECKING:
    from backend.app.infrastructure.ai.adapters.base import AIProviderAdapter
from backend.app.infrastructure.ai.key_pool import APIKeyPoolManager
from backend.app.infrastructure.ai.models import (
    AICapabilityDowngradeException,
    AIErrorCategory,
    AIExecutionResult,
    AIGenerationRequest,
    AIProviderUnavailableException,
    AIQuotaExhaustedException,
    AISchemaValidationException,
    ProviderCapability,
    ProviderError,
)
from backend.app.infrastructure.ai.policy import AIModelPolicy
from backend.app.shared.exceptions.base import AIException
from backend.app.shared.logging import get_logger
from backend.app.shared.logging.context import get_correlation_id

logger = get_logger("growflow.infrastructure.ai.gateway")

T = TypeVar("T", bound=BaseModel)


def _clean_json_markdown_fences(raw: str) -> str:
    """Strip markdown code block wrappers (e.g. ```json ... ```) from model responses."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


class AIProviderGateway:
    """Central gateway controlling all external AI model access and structured synthesis."""

    def __init__(
        self,
        settings: AISettings | None = None,
        adapter: AIProviderAdapter | None = None,
        key_pool: APIKeyPoolManager | None = None,
        policy: AIModelPolicy | None = None,
    ) -> None:
        self._settings = settings or get_settings().ai
        self._policy = policy or AIModelPolicy(self._settings)
        self._key_pool = key_pool or APIKeyPoolManager(self._settings)

        if adapter is not None:
            self._adapter = adapter
        elif self._settings.MOCK_PROVIDER:
            self._adapter = MockAIProviderAdapter(self._settings)
        else:
            self._adapter = OpenRouterAdapter(self._settings)

    @property
    def has_live_keys(self) -> bool:
        """Check if any provider keys in the pool are configured and potentially viable."""
        return self._key_pool.has_live_keys

    @property
    def key_pool(self) -> APIKeyPoolManager:
        """Provide access to the underlying key pool manager for status/observability."""
        return self._key_pool

    @property
    def policy(self) -> AIModelPolicy:
        """Provide access to the active model capability policy."""
        return self._policy

    @property
    def adapter(self) -> AIProviderAdapter:
        """Provide access to the active provider adapter."""
        return self._adapter

    async def execute(
        self,
        request: AIGenerationRequest,
    ) -> AIExecutionResult[str]:
        """Execute a text generation request with health-aware key selection, bounded retry, and fallback."""
        return await self._execute_internal(request=request, schema=None)

    async def execute_structured(
        self,
        schema: type[T],
        prompt: str,
        system_prompt: str = "You are the GrowFlow Architectural Intelligence Engine.",
        capability: ProviderCapability = ProviderCapability.STANDARD,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        timeout_seconds: float | None = None,
        correlation_id: str | None = None,
        execution_id: str | None = None,
    ) -> AIExecutionResult[T]:
        """Execute a structured generation request and validate the output against a Pydantic schema."""
        request = AIGenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            capability=capability,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            correlation_id=correlation_id,
            execution_id=execution_id,
        )
        return await self._execute_internal(request=request, schema=schema)

    async def _execute_internal(
        self,
        request: AIGenerationRequest,
        schema: type[T] | None = None,
    ) -> AIExecutionResult[Any]:
        """Internal execution engine coordinating models, keys, retries, and fallback."""
        correlation_id = request.correlation_id or get_correlation_id()
        timeout = request.timeout_seconds or float(self._settings.REQUEST_TIMEOUT_SECONDS)

        # 1. Resolve initial target model from capability or explicit request
        primary_model = request.model or self._policy.resolve_model(request.capability)
        candidate_models = [primary_model]

        total_retries = 0
        last_error: Exception | None = None

        for model_idx, target_model in enumerate(candidate_models):
            # Attempt to execute across healthy keys in the pool
            # Bounded by total slots in pool (5)
            max_key_rotations = 5
            rotations = 0

            while rotations < max_key_rotations:
                try:
                    key_entry = self._key_pool.get_next_key()
                except (AIQuotaExhaustedException, AIProviderUnavailableException) as pool_err:
                    # Check if fallback model is available and capability-compliant
                    if model_idx == 0:
                        try:
                            fallback_model = self._policy.resolve_fallback(request.capability)
                            if (
                                fallback_model != primary_model
                                and fallback_model not in candidate_models
                            ):
                                logger.warning(
                                    "Primary model capacity exhausted in key pool; evaluating fallback model",
                                    requested_capability=request.capability.value,
                                    primary_model=primary_model,
                                    fallback_model=fallback_model,
                                )
                                candidate_models.append(fallback_model)
                                break  # Break to next model candidate
                        except AICapabilityDowngradeException:
                            logger.info(
                                "No capability-compliant fallback available; raising pool error",
                                error=pool_err.message,
                            )
                        except Exception as fb_err:
                            logger.warning("Model fallback evaluation failed", error=str(fb_err))
                    raise pool_err

                raw_api_key = key_entry.raw_key
                key_alias = key_entry.key_alias

                if not raw_api_key:
                    rotations += 1
                    continue

                # Key attempt loop for transient retries on this specific key
                key_attempts = 0
                max_key_attempts = self._settings.MAX_RETRIES

                while key_attempts < max_key_attempts:
                    key_attempts += 1
                    try:
                        if schema is None:
                            raw_resp = await self._adapter.generate_text(
                                prompt=request.prompt,
                                system_prompt=request.system_prompt,
                                model=target_model,
                                api_key=raw_api_key,
                                key_alias=key_alias,
                                max_tokens=request.max_tokens,
                                temperature=request.temperature,
                                timeout_seconds=timeout,
                                correlation_id=correlation_id,
                            )
                            parsed_content: Any = raw_resp.text
                        else:
                            raw_resp = await self._adapter.generate_structured(
                                prompt=request.prompt,
                                system_prompt=request.system_prompt,
                                model=target_model,
                                api_key=raw_api_key,
                                key_alias=key_alias,
                                schema=schema,
                                max_tokens=request.max_tokens,
                                temperature=request.temperature,
                                timeout_seconds=timeout,
                                correlation_id=correlation_id,
                            )
                            cleaned_json = _clean_json_markdown_fences(raw_resp.text)
                            try:
                                parsed_content = schema.model_validate_json(cleaned_json)
                            except (ValidationError, json.JSONDecodeError) as val_err:
                                logger.warning(
                                    "AI structured output failed Pydantic schema validation",
                                    key_alias=key_alias,
                                    model=target_model,
                                    schema=schema.__name__,
                                    error=str(val_err),
                                )
                                raise AISchemaValidationException(
                                    f"Structured response failed validation for {schema.__name__}: {val_err}"
                                ) from val_err

                        # Execution succeeded on this key!
                        self._key_pool.record_success(key_alias)
                        logger.info(
                            "AI execution completed successfully",
                            model=target_model,
                            key_alias=key_alias,
                            provider=self._adapter.provider_name,
                            latency_ms=round(raw_resp.latency_ms, 2),
                            retries=total_retries,
                        )

                        return AIExecutionResult(
                            content=parsed_content,
                            raw_text=raw_resp.text,
                            provider=self._adapter.provider_name,
                            model=target_model,
                            capability=request.capability,
                            key_alias=key_alias,
                            latency_ms=raw_resp.latency_ms,
                            usage=raw_resp.usage,
                            retry_count=total_retries,
                            correlation_id=correlation_id,
                            execution_id=request.execution_id,
                        )

                    except ProviderError as pe:
                        last_error = pe
                        total_retries += 1

                        if pe.category == AIErrorCategory.RATE_LIMITED:
                            # Mark key rate-limited and immediately rotate to next key (do not retry same key)
                            self._key_pool.record_rate_limit(key_alias, retry_after=pe.retry_after)
                            break  # Exit key attempt loop $\to$ rotate to next key

                        if pe.category == AIErrorCategory.AUTH_ERROR:
                            # Mark key permanently FAILED and rotate to next key
                            self._key_pool.record_failure(key_alias, pe.category)
                            break  # Exit key attempt loop $\to$ rotate to next key

                        if pe.category in (
                            AIErrorCategory.TRANSIENT_SERVER,
                            AIErrorCategory.TIMEOUT,
                        ):
                            self._key_pool.record_failure(key_alias, pe.category)
                            if key_attempts < max_key_attempts:
                                delay = min(
                                    self._settings.RETRY_INITIAL_DELAY_SECONDS
                                    * (2 ** (key_attempts - 1)),
                                    self._settings.RETRY_MAX_DELAY_SECONDS,
                                ) + random.uniform(0, 0.25)
                                logger.warning(
                                    "Transient error on key; applying exponential backoff retry",
                                    key_alias=key_alias,
                                    attempt=key_attempts,
                                    max_attempts=max_key_attempts,
                                    delay_seconds=round(delay, 2),
                                    category=pe.category.value,
                                )
                                await asyncio.sleep(delay)
                                continue
                            # Key attempts exhausted $\to$ rotate to next key
                            break

                        if pe.category == AIErrorCategory.NON_RETRYABLE:
                            # Terminal client or invalid request error; do not retry
                            logger.error("Non-retryable provider error", error=pe.message)
                            raise AIException(pe.message, code="AI_PROVIDER_ERROR") from pe

                    except AISchemaValidationException:
                        # Schema validation failure: do not blindly retry keys; re-raise for agent handling
                        raise

                rotations += 1

        # If loop completed without returning, raise last classified failure or general exception
        if isinstance(last_error, AIException):
            raise last_error
        if isinstance(last_error, ProviderError):
            raise AIException(last_error.message, code="AI_PROVIDER_ERROR") from last_error

        raise AIProviderUnavailableException(
            "AI Provider Gateway exhausted all retry attempts and eligible keys without success."
        )

    # ──────────────────────────────────────────────────────────────
    # Backward Compatibility Interface for Existing Services
    # ──────────────────────────────────────────────────────────────

    async def execute_prompt(
        self,
        prompt: str,
        system_prompt: str = "You are the GrowFlow Architectural Intelligence Engine.",
        model: str | None = None,
        max_tokens: int = 4000,
        temperature: float = 0.2,
    ) -> str | None:
        """
        Legacy compatibility method consumed by mentor_ai_service, ai_mentor_service, and blueprint_service.

        Returns:
            str with completion text on success, or None on failure (matching legacy contract).
        """
        if not self.has_live_keys:
            return None

        request = AIGenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            capability=ProviderCapability.STANDARD,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        try:
            result = await self.execute(request)
            return str(result.content)
        except Exception as exc:
            logger.warning(
                "execute_prompt failed, returning None for backward compatibility",
                error=str(exc),
            )
            return None
