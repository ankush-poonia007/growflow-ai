"""
GrowFlow — AI Provider Gateway.

Centralized provider boundary and model execution gateway.
Supports OpenRouter provider key rotation, structured output synthesis,
resilient timeouts, and deterministic architectural generation fallback.

Architecture ref:
  6N § 18 — AI Provider Gateway
  6N § 20 — Blueprint Agent Graph
  6N § 21 — AI Output Authority Boundary
  Gate 09 — AI Blueprint & Agent System
"""

from __future__ import annotations

import json
from typing import Any
import httpx

from backend.app.config.settings import AISettings, get_settings
from backend.app.shared.logging import get_logger

logger = get_logger("growflow.infrastructure.ai.gateway")


class AIProviderGateway:
    """Central gateway for AI model access and structured synthesis."""

    def __init__(self, settings: AISettings | None = None) -> None:
        self._settings = settings or get_settings().ai
        self._key_index = 0

    @property
    def has_live_keys(self) -> bool:
        """Check if any valid OpenRouter provider keys are configured."""
        return len(self._settings.active_keys) > 0

    def _get_next_key(self) -> str | None:
        """Return the next available OpenRouter key in rotation."""
        keys = self._settings.active_keys
        if not keys:
            return None
        key = keys[self._key_index % len(keys)]
        self._key_index += 1
        return key

    async def execute_prompt(
        self,
        prompt: str,
        system_prompt: str = "You are the GrowFlow Architectural Intelligence Engine.",
        model: str | None = None,
        max_tokens: int = 4000,
        temperature: float = 0.2,
    ) -> str | None:
        """Execute a prompt through OpenRouter if keys are available."""
        api_key = self._get_next_key()
        if not api_key:
            return None

        target_model = model or self._settings.STANDARD_MODEL
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": self._settings.OPENROUTER_HTTP_REFERER,
            "X-Title": self._settings.OPENROUTER_X_TITLE,
            "Content-Type": "application/json",
        }
        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=self._settings.REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{self._settings.OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    logger.info("OpenRouter completion successful", model=target_model)
                    return str(content)
                logger.warning(
                    "OpenRouter returned non-200 status",
                    status_code=response.status_code,
                    body=response.text[:200],
                )
                return None
        except Exception as exc:
            logger.warning("OpenRouter execution failed, falling back to deterministic synthesis", error=str(exc))
            return None
