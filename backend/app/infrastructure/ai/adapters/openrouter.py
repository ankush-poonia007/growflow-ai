"""
GrowFlow — OpenRouter AI Provider Adapter.

Handles low-level HTTP transport to the OpenRouter chat completions endpoint,
including attribution headers, timeout handling, error classification, and usage extraction.

Architecture ref:
  6E § 8  — OpenRouter architecture
  6E § 19 — Provider error classification
  6E § 56 — Token usage
  6E § 75 — Provider security
"""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING, Any

import httpx

from backend.app.infrastructure.ai.adapters.base import AIProviderAdapter
from backend.app.infrastructure.ai.models import (
    AIErrorCategory,
    AIUsageMetadata,
    ProviderError,
    ProviderRawResponse,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from pydantic import BaseModel

    from backend.app.config.settings import AISettings

logger = get_logger("growflow.infrastructure.ai.adapters.openrouter")


class OpenRouterAdapter(AIProviderAdapter):
    """Production provider adapter communicating with OpenRouter via HTTP."""

    def __init__(self, settings: AISettings) -> None:
        self._settings = settings

    @property
    def provider_name(self) -> str:
        return "openrouter"

    def _build_headers(
        self,
        api_key: str,
        correlation_id: str | None = None,
    ) -> dict[str, str]:
        """Construct required OpenRouter headers without leaking credentials to logs."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": self._settings.OPENROUTER_HTTP_REFERER,
            "X-Title": self._settings.OPENROUTER_X_TITLE,
            "Content-Type": "application/json",
        }
        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id
        return headers

    def _extract_usage(self, data: dict[str, Any]) -> AIUsageMetadata | None:
        """Extract token usage metrics from the OpenRouter response body."""
        usage = data.get("usage")
        if not usage or not isinstance(usage, dict):
            return None

        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or 0)
        total_tokens = int(usage.get("total_tokens") or (prompt_tokens + completion_tokens))

        return AIUsageMetadata(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    def _parse_retry_after(self, response: httpx.Response) -> float | None:
        """Extract and parse the Retry-After header in seconds if available."""
        header_val = response.headers.get("Retry-After")
        if not header_val:
            return None
        try:
            return max(1.0, float(header_val.strip()))
        except ValueError:
            return None

    def _handle_http_error(
        self,
        response: httpx.Response,
        key_alias: str,
        model: str,
    ) -> None:
        """Map HTTP error status codes to classified ProviderError instances."""
        status = response.status_code
        retry_after = self._parse_retry_after(response)

        # Truncate body for safe diagnostics without risking large payload dumps
        body_snippet = response.text[:200] if response.text else ""

        if status == 429:
            logger.warning(
                "OpenRouter returned 429 Too Many Requests",
                key_alias=key_alias,
                model=model,
                retry_after=retry_after,
            )
            raise ProviderError(
                category=AIErrorCategory.RATE_LIMITED,
                message="OpenRouter rate limit reached",
                status_code=429,
                retry_after=retry_after,
                details={"snippet": body_snippet},
            )

        if status in (401, 403):
            logger.error(
                "OpenRouter authentication failed",
                key_alias=key_alias,
                status_code=status,
            )
            raise ProviderError(
                category=AIErrorCategory.AUTH_ERROR,
                message=f"OpenRouter authentication rejected with status {status}",
                status_code=status,
                details={"snippet": body_snippet},
            )

        if status in (500, 502, 503, 504):
            logger.warning(
                "OpenRouter server-side error",
                key_alias=key_alias,
                model=model,
                status_code=status,
            )
            raise ProviderError(
                category=AIErrorCategory.TRANSIENT_SERVER,
                message=f"OpenRouter upstream server error {status}",
                status_code=status,
                details={"snippet": body_snippet},
            )

        if status in (400, 422):
            logger.warning(
                "OpenRouter bad request / unprocessable entity",
                key_alias=key_alias,
                model=model,
                status_code=status,
            )
            raise ProviderError(
                category=AIErrorCategory.NON_RETRYABLE,
                message=f"OpenRouter rejected request with status {status}",
                status_code=status,
                details={"snippet": body_snippet},
            )

        # Fallback for unexpected status codes
        raise ProviderError(
            category=AIErrorCategory.TRANSIENT_SERVER,
            message=f"OpenRouter returned unexpected HTTP status {status}",
            status_code=status,
            details={"snippet": body_snippet},
        )

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
        """Execute a completion request against OpenRouter chat completions endpoint."""
        url = f"{self._settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
        headers = self._build_headers(api_key, correlation_id=correlation_id)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning(
                "OpenRouter request timed out",
                key_alias=key_alias,
                model=model,
                timeout_seconds=timeout_seconds,
                elapsed_ms=round(elapsed_ms, 2),
            )
            raise ProviderError(
                category=AIErrorCategory.TIMEOUT,
                message=f"OpenRouter call timed out after {timeout_seconds}s",
            ) from exc
        except httpx.NetworkError as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning(
                "OpenRouter network connection error",
                key_alias=key_alias,
                model=model,
                error=str(exc),
            )
            raise ProviderError(
                category=AIErrorCategory.TRANSIENT_SERVER,
                message=f"OpenRouter network connection failed: {exc}",
            ) from exc

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if response.status_code != 200:
            self._handle_http_error(response, key_alias=key_alias, model=model)

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = self._extract_usage(data)
            return ProviderRawResponse(
                text=str(content),
                usage=usage,
                latency_ms=elapsed_ms,
                raw_response=data,
            )
        except (KeyError, IndexError, ValueError) as exc:
            logger.error(
                "OpenRouter response format malformed",
                key_alias=key_alias,
                model=model,
                error=str(exc),
            )
            raise ProviderError(
                category=AIErrorCategory.NON_RETRYABLE,
                message=f"Malformed response structure from OpenRouter: {exc}",
            ) from exc

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
        """Execute a structured JSON synthesis request conforming to a Pydantic schema."""
        url = f"{self._settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
        headers = self._build_headers(api_key, correlation_id=correlation_id)

        # Inject strict JSON schema guidance into system prompt
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        augmented_system_prompt = (
            f"{system_prompt}\n\n"
            f"You MUST reply with a valid JSON object strictly matching the following JSON Schema:\n"
            f"{schema_json}\n\n"
            f"Do not include any conversational preamble, commentary, or markdown fences. Return pure JSON only."
        )

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": augmented_system_prompt},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning(
                "OpenRouter structured request timed out",
                key_alias=key_alias,
                model=model,
                timeout_seconds=timeout_seconds,
            )
            raise ProviderError(
                category=AIErrorCategory.TIMEOUT,
                message=f"OpenRouter structured call timed out after {timeout_seconds}s",
            ) from exc
        except httpx.NetworkError as exc:
            logger.warning(
                "OpenRouter network error during structured call",
                key_alias=key_alias,
                model=model,
                error=str(exc),
            )
            raise ProviderError(
                category=AIErrorCategory.TRANSIENT_SERVER,
                message=f"OpenRouter network connection failed: {exc}",
            ) from exc

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if response.status_code != 200:
            self._handle_http_error(response, key_alias=key_alias, model=model)

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = self._extract_usage(data)
            return ProviderRawResponse(
                text=str(content),
                usage=usage,
                latency_ms=elapsed_ms,
                raw_response=data,
            )
        except (KeyError, IndexError, ValueError) as exc:
            logger.error(
                "OpenRouter structured response payload invalid",
                key_alias=key_alias,
                model=model,
                error=str(exc),
            )
            raise ProviderError(
                category=AIErrorCategory.NON_RETRYABLE,
                message=f"Malformed response payload from OpenRouter: {exc}",
            ) from exc
