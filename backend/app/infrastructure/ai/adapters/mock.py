"""
GrowFlow — Mock AI Provider Adapter.

Deterministic provider adapter for testing AI Provider Gateway behaviors,
fault injection (rate limits, timeouts, 5xx errors), key rotation, fallback policies,
and structured Pydantic output validation without live network calls.

Architecture ref:
  6E § 89 — Mock provider
  6E § 90 — Required AI test scenarios
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from backend.app.infrastructure.ai.adapters.base import AIProviderAdapter
from backend.app.infrastructure.ai.models import (
    AIErrorCategory,
    AIUsageMetadata,
    ProviderError,
    ProviderRawResponse,
)
from backend.app.shared.logging import get_logger

if TYPE_CHECKING:
    from backend.app.config.settings import AISettings

logger = get_logger("growflow.infrastructure.ai.adapters.mock")


class MockAIProviderAdapter(AIProviderAdapter):
    """Deterministic mock provider adapter for testing and failure injection."""

    def __init__(
        self,
        settings: AISettings | None = None,
        default_text: str = "Mock deterministic architectural completion.",
    ) -> None:
        self._settings = settings
        self.default_text = default_text
        self.call_count = 0
        self.invocations: list[dict[str, Any]] = []
        self.last_prompt: str | None = None
        self.last_model: str | None = None
        self.last_key_alias: str | None = None

        # Fault injection state
        self._simulated_rate_limit: bool = False
        self._simulated_retry_after: float | None = None
        self._simulated_timeout: bool = False
        self._simulated_server_error: int | None = None
        self._simulated_auth_error: bool = False
        self._simulated_malformed_json: bool = False
        self._canned_structured_responses: dict[str, Any] = {}
        self._error_calls_remaining: int = 0

    @property
    def provider_name(self) -> str:
        return "mock"

    def simulate_rate_limit(self, retry_after: float = 60.0, times: int = 1) -> None:
        """Inject a simulated 429 Too Many Requests response."""
        self._simulated_rate_limit = True
        self._simulated_retry_after = retry_after
        self._error_calls_remaining = times

    def simulate_timeout(self, times: int = 1) -> None:
        """Inject a simulated request timeout."""
        self._simulated_timeout = True
        self._error_calls_remaining = times

    def simulate_server_error(self, status_code: int = 502, times: int = 1) -> None:
        """Inject a simulated transient server error (500, 502, 503)."""
        self._simulated_server_error = status_code
        self._error_calls_remaining = times

    def simulate_auth_error(self, times: int = 1) -> None:
        """Inject a simulated 401/403 authentication error."""
        self._simulated_auth_error = True
        self._error_calls_remaining = times

    def simulate_malformed_json(self, times: int = 1) -> None:
        """Inject an invalid JSON string to test schema validation recovery."""
        self._simulated_malformed_json = True
        self._error_calls_remaining = times

    def register_structured_response(
        self, schema_name: str, response_data: dict[str, Any] | BaseModel
    ) -> None:
        """Register a canned structured response for a specific schema name."""
        if isinstance(response_data, BaseModel):
            self._canned_structured_responses[schema_name] = response_data.model_dump()
        else:
            self._canned_structured_responses[schema_name] = response_data

    def reset_simulation(self) -> None:
        """Clear all active fault injections."""
        self._simulated_rate_limit = False
        self._simulated_retry_after = None
        self._simulated_timeout = False
        self._simulated_server_error = None
        self._simulated_auth_error = False
        self._simulated_malformed_json = False
        self._error_calls_remaining = 0

    def _check_and_consume_faults(self, key_alias: str, model: str) -> None:
        """Evaluate active fault injections and raise corresponding ProviderError."""
        if self._error_calls_remaining <= 0:
            self.reset_simulation()
            return

        self._error_calls_remaining -= 1

        if self._simulated_rate_limit:
            raise ProviderError(
                category=AIErrorCategory.RATE_LIMITED,
                message="Mock simulated rate limit reached",
                status_code=429,
                retry_after=self._simulated_retry_after or 60.0,
            )

        if self._simulated_timeout:
            raise ProviderError(
                category=AIErrorCategory.TIMEOUT,
                message="Mock simulated request timeout",
            )

        if self._simulated_auth_error:
            raise ProviderError(
                category=AIErrorCategory.AUTH_ERROR,
                message="Mock simulated authentication rejection",
                status_code=401,
            )

        if self._simulated_server_error is not None:
            code = self._simulated_server_error
            raise ProviderError(
                category=AIErrorCategory.TRANSIENT_SERVER,
                message=f"Mock simulated server failure {code}",
                status_code=code,
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
        self.call_count += 1
        self.last_prompt = prompt
        self.last_model = model
        self.last_key_alias = key_alias
        self.invocations.append(
            {
                "type": "text",
                "prompt": prompt,
                "model": model,
                "key_alias": key_alias,
                "correlation_id": correlation_id,
            }
        )

        self._check_and_consume_faults(key_alias=key_alias, model=model)

        usage = AIUsageMetadata(prompt_tokens=15, completion_tokens=30, total_tokens=45)
        return ProviderRawResponse(
            text=self.default_text,
            usage=usage,
            latency_ms=5.0,
            raw_response={"mock": True},
        )

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
        self.call_count += 1
        self.last_prompt = prompt
        self.last_model = model
        self.last_key_alias = key_alias
        self.invocations.append(
            {
                "type": "structured",
                "prompt": prompt,
                "model": model,
                "key_alias": key_alias,
                "schema": schema.__name__,
                "correlation_id": correlation_id,
            }
        )

        self._check_and_consume_faults(key_alias=key_alias, model=model)

        if self._simulated_malformed_json:
            self._simulated_malformed_json = False
            return ProviderRawResponse(
                text="INVALID { NOT JSON",
                usage=AIUsageMetadata(prompt_tokens=10, completion_tokens=5, total_tokens=15),
                latency_ms=4.0,
            )

        # Check registered canned response
        schema_name = schema.__name__
        if schema_name in self._canned_structured_responses:
            data = self._canned_structured_responses[schema_name]
            json_text = json.dumps(data)
        else:
            # Deterministically synthesize default payload conforming to the Pydantic schema
            mock_dict: dict[str, Any] = {}
            for field_name, field_info in schema.model_fields.items():
                annotation = field_info.annotation
                ann_str = str(annotation)
                if field_info.default is not None and field_info.default != ...:
                    mock_dict[field_name] = field_info.default
                elif "str" in ann_str:
                    mock_dict[field_name] = f"mock_{field_name}"
                elif "int" in ann_str:
                    mock_dict[field_name] = 42
                elif "float" in ann_str:
                    mock_dict[field_name] = 3.14
                elif "bool" in ann_str:
                    mock_dict[field_name] = True
                elif "list" in ann_str:
                    mock_dict[field_name] = []
                elif "dict" in ann_str:
                    mock_dict[field_name] = {}
                else:
                    mock_dict[field_name] = f"mock_{field_name}"
            json_text = json.dumps(mock_dict)

        usage = AIUsageMetadata(prompt_tokens=25, completion_tokens=50, total_tokens=75)
        return ProviderRawResponse(
            text=json_text,
            usage=usage,
            latency_ms=6.0,
            raw_response={"mock": True, "schema": schema_name},
        )
