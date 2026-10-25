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

import enum
import json
import typing
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from pydantic_core import PydanticUndefined

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


def _synthesize_mock_value(field_name: str, annotation: Any, field_info: Any) -> Any:
    """Deterministically synthesize a valid value conforming to a Pydantic field."""
    # 1. Default value if defined, not None, and not PydanticUndefined
    if field_info is not None:
        if (
            field_info.default is not None
            and field_info.default is not PydanticUndefined
            and field_info.default != ...
        ):
            return field_info.default

        # 2. Default factory
        if field_info.default_factory is not None:
            try:
                val = field_info.default_factory()
                if isinstance(val, BaseModel):
                    return val.model_dump(mode="json")
                return val
            except Exception:
                pass

    # 3. Unwrap Optional / Union
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)

    if origin is typing.Union:
        non_none_args = [a for a in args if a is not type(None)]
        if non_none_args:
            return _synthesize_mock_value(field_name, non_none_args[0], field_info)

    # 4. Enums
    if isinstance(annotation, type) and issubclass(annotation, enum.Enum):
        enum_members = list(annotation)
        if enum_members:
            return enum_members[0].value

    # 5. Nested BaseModel
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _synthesize_mock_dict(annotation)

    # 6. Lists and Sequences
    if origin in (list, typing.Sequence, typing.Iterable):
        inner_type = args[0] if args else str
        min_len = 1
        for meta in getattr(field_info, "metadata", []):
            if hasattr(meta, "min_length") and meta.min_length:
                min_len = max(min_len, meta.min_length)
        count = max(min_len, 2)
        items = []
        for i in range(count):
            if isinstance(inner_type, type) and issubclass(inner_type, BaseModel):
                item = _synthesize_mock_dict(inner_type)
                for k, v in list(item.items()):
                    if (
                        k.endswith("_id")
                        and isinstance(v, str)
                        and len(v) >= 3
                        and v[0].isalpha()
                        and v[1:].isdigit()
                    ):
                        item[k] = f"{v[0]}{i+1:02d}"
                if "priority" in item and i < 2:
                    p_info = inner_type.model_fields.get("priority")
                    if p_info and isinstance(p_info.annotation, type) and issubclass(p_info.annotation, enum.Enum):
                        if any(m.value == "P0" for m in p_info.annotation):
                            item["priority"] = "P0"
                    else:
                        item["priority"] = "P0"
                items.append(item)
            elif isinstance(inner_type, type) and issubclass(inner_type, enum.Enum):
                members = list(inner_type)
                items.append(members[i % len(members)].value)
            else:
                items.append(_synthesize_mock_value(field_name, inner_type, None))
        return items

    # 7. Dicts
    if origin is dict:
        return {}

    # 8. Primitives
    ann_str = str(annotation)
    if "str" in ann_str or annotation is str:
        for meta in getattr(field_info, "metadata", []):
            pattern = getattr(meta, "pattern", None)
            if pattern:
                import re
                match = re.match(r"\^?([A-Za-z]+)(?:\\d|\d|\.)", pattern)
                if match:
                    return f"{match.group(1)}01"
                if "F" in pattern and r"\d" in pattern:
                    return "F01"
                if "T" in pattern and r"\d" in pattern:
                    return "T01"
                if "M" in pattern and r"\d" in pattern:
                    return "M1"
                if "R" in pattern and r"\d" in pattern:
                    return "R01"
                if "C" in pattern and r"\d" in pattern:
                    return "C01"
        return f"Mock {field_name.replace('_', ' ').capitalize()}"

    if "int" in ann_str or annotation is int:
        ge = 1
        for meta in getattr(field_info, "metadata", []):
            if hasattr(meta, "ge") and meta.ge is not None:
                ge = max(ge, int(meta.ge))
        return ge

    if "float" in ann_str or annotation is float:
        return 0.95

    if "bool" in ann_str or annotation is bool:
        return True

    return f"mock_{field_name}"


def _synthesize_mock_dict(schema: type[BaseModel]) -> dict[str, Any]:
    """Recursively synthesize a mock dictionary for a Pydantic schema."""
    result: dict[str, Any] = {}
    schema_name = getattr(schema, "__name__", "")
    canonical_agent_name = None
    if schema_name == "QAJudgeAgentOutput":
        canonical_agent_name = "qa_judge_agent"
    elif schema_name.endswith("AgentOutput"):
        canonical_agent_name = f"{schema_name[:-11].lower()}_agent"

    for name, info in schema.model_fields.items():
        if name == "agent_name" and canonical_agent_name:
            result[name] = canonical_agent_name
            continue
        result[name] = _synthesize_mock_value(name, info.annotation, info)

    # Post-process known domain cross-field validation rules
    if schema_name == "TimelineAgentOutput" and "phases" in result:
        total = sum(p.get("duration_weeks", 0) for p in result["phases"])
        result["estimated_total_weeks"] = max(total, 1)

    if schema_name == "RiskAgentOutput" and "risks" in result and result["risks"]:
        # Ensure at least one risk is SECURITY
        result["risks"][0]["category"] = "SECURITY"

    if schema_name == "MilestoneAgentOutput" and "milestones" in result:
        for idx, m in enumerate(result["milestones"]):
            m["milestone_id"] = f"M{idx + 1}"

    return result


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
            self._canned_structured_responses[schema_name] = response_data.model_dump(mode="json")
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
            from backend.app.domain.ai.contracts.seeds import get_canonical_agent_output

            canonical_seed = get_canonical_agent_output(schema_name)
            if canonical_seed is not None:
                json_text = canonical_seed.model_dump_json()
            else:
                # Deterministically synthesize default payload conforming to the Pydantic schema
                mock_dict = _synthesize_mock_dict(schema)
                json_text = json.dumps(mock_dict)

        usage = AIUsageMetadata(prompt_tokens=25, completion_tokens=50, total_tokens=75)
        return ProviderRawResponse(
            text=json_text,
            usage=usage,
            latency_ms=6.0,
            raw_response={"mock": True, "schema": schema_name},
        )
