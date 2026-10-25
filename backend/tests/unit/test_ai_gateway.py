"""
GrowFlow — Unit Tests for AI Provider Gateway.

Comprehensive test suite validating:
1. Capability resolution and model mapping
2. Valid capability-compliant fallback
3. Capability downgrade forbidden enforcement (REASONING >= STANDARD >= FAST)
4. Health-aware round-robin key rotation
5. Rate-limited key exclusion (429)
6. Cooldown expiration and automatic key recovery
7. Authentication failure permanent exclusion (401)
8. Disabled key handling
9. Transient retry with exponential backoff
10. Retry exhaustion and rotation
11. Quota exhaustion error handling
12. Provider unavailable error handling
13. Request timeout handling
14. Structured output synthesis and Pydantic validation
15. Malformed structured output schema violation handling
16. Mock provider fault injection and inspection
17. Observability and token usage metadata propagation
18. Secret protection and non-leakage
19. Backward compatibility for legacy execute_prompt and has_live_keys

Architecture ref:
  6E § 10, § 12, § 13, § 16, § 18, § 19, § 20, § 21, § 22, § 44, § 89, § 90
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field
import pytest

from backend.app.config.settings import AISettings
from backend.app.infrastructure.ai.adapters.mock import MockAIProviderAdapter
from backend.app.infrastructure.ai.gateway import AIProviderGateway
from backend.app.infrastructure.ai.key_pool import APIKeyPoolManager
from backend.app.infrastructure.ai.models import (
    AICapabilityDowngradeException,
    AIErrorCategory,
    AIGenerationRequest,
    AIProviderUnavailableException,
    AIQuotaExhaustedException,
    AISchemaValidationException,
    KeyHealthState,
    ProviderCapability,
)
from backend.app.infrastructure.ai.policy import AIModelPolicy


# Test schema for structured output validation
class SampleBlueprintOutput(BaseModel):
    title: str
    version: int = 1
    tags: list[str] = Field(default_factory=list)


def create_test_settings(
    keys: list[str | None] | None = None,
    mock_provider: bool = True,
    fallback_model: str = "openai/gpt-4o-mini",
) -> AISettings:
    """Helper to construct controlled AISettings fixtures."""
    effective_keys = keys if keys is not None else ["sk-key-1", "sk-key-2", None, None, None]
    return AISettings(
        OPENROUTER_API_KEY_1=effective_keys[0],
        OPENROUTER_API_KEY_2=effective_keys[1] if len(effective_keys) > 1 else None,
        OPENROUTER_API_KEY_3=effective_keys[2] if len(effective_keys) > 2 else None,
        OPENROUTER_API_KEY_4=effective_keys[3] if len(effective_keys) > 3 else None,
        OPENROUTER_API_KEY_5=effective_keys[4] if len(effective_keys) > 4 else None,
        AI_FAST_MODEL="openai/gpt-4o-mini",
        AI_STANDARD_MODEL="openai/gpt-4o",
        AI_REASONING_MODEL="openai/o1",
        AI_EMBEDDING_MODEL="openai/text-embedding-3-small",
        AI_DEFAULT_MODEL="openai/gpt-4o",
        AI_FALLBACK_MODEL=fallback_model,
        AI_REQUEST_TIMEOUT_SECONDS=10,
        AI_MAX_RETRIES=2,
        AI_RETRY_INITIAL_DELAY_SECONDS=1,
        AI_RETRY_MAX_DELAY_SECONDS=2,
        AI_RATE_LIMIT_COOLDOWN_SECONDS=60,
        AI_TRANSIENT_COOLDOWN_SECONDS=30,
        AI_MOCK_PROVIDER=mock_provider,
    )


# ──────────────────────────────────────────────────────────────
# 1. Capability Resolution Tests
# ──────────────────────────────────────────────────────────────


def test_capability_resolution() -> None:
    """Validate that logical capabilities resolve to their configured model names."""
    settings = create_test_settings()
    policy = AIModelPolicy(settings)

    assert policy.resolve_model(ProviderCapability.FAST) == "openai/gpt-4o-mini"
    assert policy.resolve_model(ProviderCapability.STANDARD) == "openai/gpt-4o"
    assert policy.resolve_model(ProviderCapability.REASONING) == "openai/o1"
    assert policy.resolve_model(ProviderCapability.EMBEDDING) == "openai/text-embedding-3-small"


# ──────────────────────────────────────────────────────────────
# 2. Valid Capability Fallback Tests
# ──────────────────────────────────────────────────────────────


def test_valid_capability_fallback() -> None:
    """STANDARD capability can safely fall back to STANDARD or REASONING model."""
    settings = create_test_settings(fallback_model="openai/gpt-4o")
    policy = AIModelPolicy(settings)

    # STANDARD -> STANDARD is valid
    resolved = policy.resolve_fallback(ProviderCapability.STANDARD)
    assert resolved == "openai/gpt-4o"

    # FAST -> STANDARD is valid (upgrade)
    resolved_fast = policy.resolve_fallback(
        ProviderCapability.FAST, explicit_fallback_model="openai/gpt-4o"
    )
    assert resolved_fast == "openai/gpt-4o"


# ──────────────────────────────────────────────────────────────
# 3. Capability Downgrade Forbidden Tests
# ──────────────────────────────────────────────────────────────


def test_capability_downgrade_forbidden() -> None:
    """REASONING request attempting fallback to FAST model is strictly rejected."""
    # Default fallback is gpt-4o-mini (FAST)
    settings = create_test_settings(fallback_model="openai/gpt-4o-mini")
    policy = AIModelPolicy(settings)

    with pytest.raises(AICapabilityDowngradeException) as exc_info:
        policy.resolve_fallback(ProviderCapability.REASONING)

    assert "Capability downgrade forbidden" in str(exc_info.value)
    assert exc_info.value.code == "CAPABILITY_DOWNGRADE_FORBIDDEN"


def test_standard_downgrade_to_fast_forbidden() -> None:
    """STANDARD request attempting fallback to FAST model is rejected."""
    settings = create_test_settings(fallback_model="openai/gpt-4o-mini")
    policy = AIModelPolicy(settings)

    with pytest.raises(AICapabilityDowngradeException):
        policy.resolve_fallback(ProviderCapability.STANDARD)


# ──────────────────────────────────────────────────────────────
# 4. Round-Robin Key Selection Tests
# ──────────────────────────────────────────────────────────────


def test_health_aware_round_robin_selection() -> None:
    """Healthy keys in pool rotate sequentially in round-robin fashion."""
    settings = create_test_settings(keys=["key-a", "key-b", "key-c", None, None])
    pool = APIKeyPoolManager(settings)

    k1 = pool.get_next_key()
    assert k1.key_alias == "key_1"
    assert k1.status == KeyHealthState.ACTIVE

    k2 = pool.get_next_key()
    assert k2.key_alias == "key_2"
    assert k2.status == KeyHealthState.ACTIVE

    k3 = pool.get_next_key()
    assert k3.key_alias == "key_3"
    assert k3.status == KeyHealthState.ACTIVE

    # Cycles back to key_1
    k4 = pool.get_next_key()
    assert k4.key_alias == "key_1"


# ──────────────────────────────────────────────────────────────
# 5. Rate-Limited Key Exclusion Tests
# ──────────────────────────────────────────────────────────────


def test_rate_limited_key_skipped_in_rotation() -> None:
    """A key marked RATE_LIMITED is immediately excluded from active selection."""
    settings = create_test_settings(keys=["key-a", "key-b", None, None, None])
    pool = APIKeyPoolManager(settings)

    # Both key_1 and key_2 start active
    k1 = pool.get_next_key()
    assert k1.key_alias == "key_1"

    # Mark key_1 rate-limited
    pool.record_rate_limit("key_1", retry_after=60.0)

    # Next selections must skip key_1 and only select key_2
    for _ in range(3):
        selected = pool.get_next_key()
        assert selected.key_alias == "key_2"


# ──────────────────────────────────────────────────────────────
# 6. Cooldown Expiration & Recovery Tests
# ──────────────────────────────────────────────────────────────


def test_cooldown_expiration_and_recovery() -> None:
    """A key in COOLDOWN automatically recovers to ACTIVE once cooldown_until passes."""
    settings = create_test_settings(keys=["key-a", None, None, None, None])
    pool = APIKeyPoolManager(settings)

    # Mark key_1 in cooldown, with timestamp in the past
    pool.record_rate_limit("key_1", retry_after=10.0)
    entry = pool._pool[0]
    assert entry.status == KeyHealthState.RATE_LIMITED

    # Manually backdate cooldown_until to the past
    entry.cooldown_until = datetime.now(UTC) - timedelta(seconds=5)

    # Selecting next key recovers key_1 back to ACTIVE
    k = pool.get_next_key()
    assert k.key_alias == "key_1"
    assert k.status == KeyHealthState.ACTIVE
    assert k.cooldown_until is None


# ──────────────────────────────────────────────────────────────
# 7. Authentication Failure Permanent Exclusion Tests
# ──────────────────────────────────────────────────────────────


def test_auth_error_marks_key_permanently_failed() -> None:
    """HTTP 401/403 marks key FAILED, permanently excluding it from rotation."""
    settings = create_test_settings(keys=["bad-key", "good-key", None, None, None])
    pool = APIKeyPoolManager(settings)

    # Mark key_1 failed due to auth error
    pool.record_failure("key_1", AIErrorCategory.AUTH_ERROR)

    entry_1 = pool._pool[0]
    assert entry_1.status == KeyHealthState.FAILED

    # Rotation now only selects good-key
    for _ in range(3):
        k = pool.get_next_key()
        assert k.key_alias == "key_2"


# ──────────────────────────────────────────────────────────────
# 8. Disabled Key Handling Tests
# ──────────────────────────────────────────────────────────────


def test_disabled_keys_handling() -> None:
    """Empty and placeholder keys are initialized as DISABLED."""
    settings = create_test_settings(keys=["real-key", "", "your-placeholder-key", None, None])
    pool = APIKeyPoolManager(settings)

    assert pool._pool[0].status == KeyHealthState.ACTIVE
    assert pool._pool[1].status == KeyHealthState.DISABLED
    assert pool._pool[2].status == KeyHealthState.DISABLED
    assert pool._pool[3].status == KeyHealthState.DISABLED
    assert pool._pool[4].status == KeyHealthState.DISABLED


# ──────────────────────────────────────────────────────────────
# 9. Transient Server Error Retry Tests
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_transient_retry_with_mock_adapter() -> None:
    """Transient server error (502) triggers retry and succeeds on subsequent attempt."""
    settings = create_test_settings(keys=["key-a", None, None, None, None])
    mock_adapter = MockAIProviderAdapter(settings=settings)

    # Simulate single 502 failure, then recover
    mock_adapter.simulate_server_error(status_code=502, times=1)

    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter)
    req = AIGenerationRequest(prompt="Test transient retry", capability=ProviderCapability.STANDARD)

    result = await gateway.execute(req)

    assert result.content == mock_adapter.default_text
    assert result.retry_count == 1
    assert mock_adapter.call_count == 2


# ──────────────────────────────────────────────────────────────
# 10. Retry Exhaustion and Key Rotation Tests
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_retry_exhaustion_triggers_key_rotation() -> None:
    """When a key exhausts its retry attempts, gateway rotates to the next healthy key."""
    settings = create_test_settings(keys=["key-a", "key-b", None, None, None])
    mock_adapter = MockAIProviderAdapter(settings=settings)

    # Inject 2 server errors (exhausting max retries of key_1 = 2), then succeed on key_2
    mock_adapter.simulate_server_error(status_code=503, times=2)

    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter)
    req = AIGenerationRequest(prompt="Test retry exhaustion rotation")

    result = await gateway.execute(req)

    assert result.key_alias == "key_2"
    assert result.retry_count >= 2


# ──────────────────────────────────────────────────────────────
# 11. Quota Exhaustion Tests
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_quota_exhausted_when_all_keys_in_cooldown() -> None:
    """When all keys in the pool are rate-limited or cooling down, raises AIQuotaExhaustedException."""
    settings = create_test_settings(keys=["key-a", "key-b", None, None, None])
    pool = APIKeyPoolManager(settings)

    # Mark both keys as rate-limited
    pool.record_rate_limit("key_1", retry_after=60.0)
    pool.record_rate_limit("key_2", retry_after=60.0)

    mock_adapter = MockAIProviderAdapter(settings=settings)
    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter, key_pool=pool)

    req = AIGenerationRequest(prompt="Test quota exhaustion")

    with pytest.raises(AIQuotaExhaustedException) as exc_info:
        await gateway.execute(req)

    assert exc_info.value.code == "QUOTA_EXHAUSTED"


# ──────────────────────────────────────────────────────────────
# 12. Provider Unavailable Tests
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_provider_unavailable_when_no_active_keys() -> None:
    """When all configured keys are FAILED or DISABLED, raises AIProviderUnavailableException."""
    settings = create_test_settings(keys=[None, None, None, None, None])
    mock_adapter = MockAIProviderAdapter(settings=settings)
    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter)

    req = AIGenerationRequest(prompt="Test no keys available")

    with pytest.raises(AIProviderUnavailableException) as exc_info:
        await gateway.execute(req)

    assert exc_info.value.code == "PROVIDER_UNAVAILABLE"


# ──────────────────────────────────────────────────────────────
# 13. Request Timeout Handling Tests
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_timeout_handling_triggers_rotation() -> None:
    """Request timeout on key_1 triggers rotation to key_2."""
    settings = create_test_settings(keys=["key-a", "key-b", None, None, None])
    mock_adapter = MockAIProviderAdapter(settings=settings)

    # Inject timeout on first 2 calls (exhausting key_1), succeeding on key_2
    mock_adapter.simulate_timeout(times=2)

    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter)
    req = AIGenerationRequest(prompt="Test timeout rotation")

    result = await gateway.execute(req)
    assert result.key_alias == "key_2"


# ──────────────────────────────────────────────────────────────
# 14. Structured Output Synthesis Tests
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_structured_output_synthesis() -> None:
    """Structured generation validates model JSON into a typed Pydantic instance."""
    settings = create_test_settings()
    mock_adapter = MockAIProviderAdapter(settings=settings)

    canned = SampleBlueprintOutput(title="Architecture Spec", version=2, tags=["backend", "ai"])
    mock_adapter.register_structured_response("SampleBlueprintOutput", canned)

    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter)

    result = await gateway.execute_structured(
        schema=SampleBlueprintOutput,
        prompt="Generate sample blueprint",
        capability=ProviderCapability.STANDARD,
    )

    assert isinstance(result.content, SampleBlueprintOutput)
    assert result.content.title == "Architecture Spec"
    assert result.content.version == 2
    assert result.content.tags == ["backend", "ai"]
    assert result.capability == ProviderCapability.STANDARD


# ──────────────────────────────────────────────────────────────
# 15. Malformed Structured Output Error Handling Tests
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_malformed_structured_output_raises_exception() -> None:
    """Malformed JSON output raises AISchemaValidationException."""
    settings = create_test_settings()
    mock_adapter = MockAIProviderAdapter(settings=settings)

    # Inject invalid unparseable JSON
    mock_adapter.simulate_malformed_json(times=1)

    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter)

    with pytest.raises(AISchemaValidationException) as exc_info:
        await gateway.execute_structured(
            schema=SampleBlueprintOutput,
            prompt="Generate blueprint",
        )

    assert exc_info.value.code == "SCHEMA_VALIDATION_ERROR"


# ──────────────────────────────────────────────────────────────
# 16. Mock Provider Inspection Tests
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mock_provider_inspection_state() -> None:
    """Mock provider accurately records invocations, prompts, and models."""
    settings = create_test_settings()
    mock_adapter = MockAIProviderAdapter(settings=settings)
    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter)

    req = AIGenerationRequest(
        prompt="Inspectable prompt",
        capability=ProviderCapability.FAST,
        correlation_id="corr-123",
    )
    result = await gateway.execute(req)

    assert mock_adapter.call_count == 1
    assert mock_adapter.last_prompt == "Inspectable prompt"
    assert mock_adapter.last_model == "openai/gpt-4o-mini"
    assert len(mock_adapter.invocations) == 1
    assert mock_adapter.invocations[0]["correlation_id"] == "corr-123"
    assert result.correlation_id == "corr-123"


# ──────────────────────────────────────────────────────────────
# 17. Observability and Token Metadata Propagation Tests
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_metadata_propagation() -> None:
    """AIExecutionResult carries token usage, latency, provider, and model metadata."""
    settings = create_test_settings()
    mock_adapter = MockAIProviderAdapter(settings=settings)
    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter)

    req = AIGenerationRequest(prompt="Token metadata test")
    result = await gateway.execute(req)

    assert result.provider == "mock"
    assert result.model == "openai/gpt-4o"
    assert result.latency_ms > 0
    assert result.usage is not None
    assert result.usage.prompt_tokens == 15
    assert result.usage.completion_tokens == 30
    assert result.usage.total_tokens == 45


# ──────────────────────────────────────────────────────────────
# 18. Secret Protection Tests
# ──────────────────────────────────────────────────────────────


def test_secret_protection_in_pool_and_status() -> None:
    """Raw API keys are never exposed in get_pool_status or string representations."""
    settings = create_test_settings(keys=["super-secret-key-12345", None, None, None, None])
    pool = APIKeyPoolManager(settings)

    pool_status = pool.get_pool_status()
    assert len(pool_status) == 5

    # Check that raw secret does not appear anywhere in pool_status
    status_str = str(pool_status)
    assert "super-secret-key-12345" not in status_str
    assert pool_status[0]["key_alias"] == "key_1"
    assert pool_status[0]["has_key"] is True


# ──────────────────────────────────────────────────────────────
# 19. Backward Compatibility Tests
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_backward_compatibility_has_live_keys() -> None:
    """has_live_keys returns True when keys exist, False when none configured."""
    settings_with_keys = create_test_settings(keys=["key-a", None, None, None, None])
    gateway_live = AIProviderGateway(settings=settings_with_keys)
    assert gateway_live.has_live_keys is True

    settings_empty = create_test_settings(keys=[None, None, None, None, None])
    gateway_empty = AIProviderGateway(settings=settings_empty)
    assert gateway_empty.has_live_keys is False


@pytest.mark.asyncio
async def test_backward_compatibility_execute_prompt() -> None:
    """Legacy execute_prompt returns string on success and None on failure."""
    settings = create_test_settings(keys=["key-a", None, None, None, None])
    mock_adapter = MockAIProviderAdapter(settings=settings)
    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter)

    # Success case
    response = await gateway.execute_prompt(
        prompt="Explain photosynthesis",
        system_prompt="You are an expert tutor.",
    )
    assert response == mock_adapter.default_text

    # Failure case: offline gateway returns None without raising
    settings_offline = create_test_settings(keys=[None, None, None, None, None])
    gateway_offline = AIProviderGateway(settings=settings_offline)
    offline_resp = await gateway_offline.execute_prompt(prompt="Hello")
    assert offline_resp is None


# ──────────────────────────────────────────────────────────────
# 20. Resilient Fallback & Schema Synthesis Tests (Fix 2)
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_openrouter_all_keys_failure_recovers_to_mock_fallback() -> None:
    """When live OpenRouter keys are exhausted or rejected, gateway degrades to MockAIProviderAdapter."""
    from backend.app.domain.ai.contracts.agents import IdeaAgentOutput
    from backend.app.infrastructure.ai.adapters.openrouter import OpenRouterAdapter

    settings = AISettings(
        OPENROUTER_API_KEY_1="sk-bad-1",
        OPENROUTER_API_KEY_2="sk-bad-2",
        MOCK_PROVIDER=False,
        MOCK_FALLBACK=True,
    )
    gateway = AIProviderGateway(settings=settings)
    assert isinstance(gateway.adapter, OpenRouterAdapter)

    # Simulate all keys having transitioned to FAILED
    for entry in gateway.key_pool._pool:
        entry.status = KeyHealthState.FAILED

    # Structured execution should seamlessly degrade to mock provider
    result = await gateway.execute_structured(
        schema=IdeaAgentOutput,
        prompt="Design resilient system architecture",
    )
    assert result.provider == "mock"
    assert result.is_degraded is True
    assert isinstance(result.content, IdeaAgentOutput)
    assert result.content.agent_name == "idea_agent"


@pytest.mark.asyncio
async def test_unregistered_pydantic_schema_synthesis_without_undefined_error() -> None:
    """Mock adapter recursively synthesizes arbitrary schemas with required fields without PydanticUndefined error."""
    class SubItem(BaseModel):
        code: str = Field(..., pattern=r"^F\d{2}$")
        count: int = Field(..., ge=1)

    class ComplexRequiredSchema(BaseModel):
        name: str
        required_int: int
        sub_items: list[SubItem] = Field(..., min_length=2)

    adapter = MockAIProviderAdapter()
    raw_resp = await adapter.generate_structured(
        prompt="Synthesize schema",
        system_prompt="Test system",
        model="mock-model",
        api_key="mock-key",
        key_alias="key_1",
        schema=ComplexRequiredSchema,
    )

    # Verify no PydanticUndefinedType serialization error occurred
    assert "PydanticUndefined" not in raw_resp.text
    validated = ComplexRequiredSchema.model_validate_json(raw_resp.text)
    assert isinstance(validated, ComplexRequiredSchema)
    assert len(validated.sub_items) >= 2


@pytest.mark.asyncio
async def test_execute_prompt_recovers_via_mock_fallback_when_keys_failed() -> None:
    """execute_prompt returns mock completion when live OpenRouter keys have failed."""
    settings = AISettings(
        OPENROUTER_API_KEY_1="sk-key-1",
        OPENROUTER_API_KEY_2="sk-key-2",
        MOCK_PROVIDER=False,
        MOCK_FALLBACK=True,
    )
    gateway = AIProviderGateway(settings=settings)

    # Fail all keys
    for entry in gateway.key_pool._pool:
        entry.status = KeyHealthState.FAILED

    response = await gateway.execute_prompt(prompt="Mentor advice query")
    assert response is not None
    assert "Mock deterministic architectural completion" in response


# ──────────────────────────────────────────────────────────────
# 21. Explicit Fallback Policy & Degradation Identification (Fix 2A)
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_live_provider_success_is_not_degraded() -> None:
    """Successful primary provider execution explicitly marks result as not degraded."""
    settings = create_test_settings(keys=["key-a", None, None, None, None])
    mock_adapter = MockAIProviderAdapter(settings=settings)
    gateway = AIProviderGateway(settings=settings, adapter=mock_adapter)

    req = AIGenerationRequest(prompt="Normal operation")
    result = await gateway.execute(req)

    assert result.is_degraded is False
    assert result.content == mock_adapter.default_text


@pytest.mark.asyncio
async def test_fallback_disabled_raises_unavailable_when_keys_fail() -> None:
    """When fallback is explicitly disabled, key exhaustion raises AIProviderUnavailableException."""
    from backend.app.domain.ai.contracts.agents import IdeaAgentOutput

    settings = AISettings(
        OPENROUTER_API_KEY_1="sk-key-1",
        MOCK_PROVIDER=False,
        MOCK_FALLBACK=False,
    )
    gateway = AIProviderGateway(settings=settings, app_env="development")
    assert gateway.is_fallback_enabled is False

    # Fail all keys
    for entry in gateway.key_pool._pool:
        entry.status = KeyHealthState.FAILED

    with pytest.raises(AIProviderUnavailableException) as exc_info:
        await gateway.execute_structured(
            schema=IdeaAgentOutput,
            prompt="Design architecture",
        )
    assert exc_info.value.code == "PROVIDER_UNAVAILABLE"


@pytest.mark.asyncio
async def test_production_environment_blocks_accidental_fallback() -> None:
    """In production, fallback is disabled by default even if environment alias is omitted or empty."""
    from backend.app.config.settings import Environment
    from backend.app.domain.ai.contracts.agents import IdeaAgentOutput

    # Default settings in production (MOCK_FALLBACK is None)
    settings = AISettings(
        OPENROUTER_API_KEY_1="sk-live-prod-key",
        MOCK_PROVIDER=False,
    )
    gateway = AIProviderGateway(settings=settings, app_env=Environment.PRODUCTION)
    assert gateway.is_fallback_enabled is False

    # Fail all keys
    for entry in gateway.key_pool._pool:
        entry.status = KeyHealthState.FAILED

    with pytest.raises(AIProviderUnavailableException) as exc_info:
        await gateway.execute_structured(
            schema=IdeaAgentOutput,
            prompt="Production prompt",
        )
    assert exc_info.value.code == "PROVIDER_UNAVAILABLE"


@pytest.mark.asyncio
async def test_production_fallback_disallowed_even_with_override_flags() -> None:
    """In production, mock fallback is disallowed unconditionally, even if override flags are configured."""
    from backend.app.config.settings import Environment
    from backend.app.domain.ai.contracts.agents import IdeaAgentOutput

    settings_override = AISettings(
        OPENROUTER_API_KEY_1="sk-key-1",
        MOCK_PROVIDER=False,
        MOCK_FALLBACK=True,
        ALLOW_PRODUCTION_MOCK_FALLBACK=True,
    )
    gateway = AIProviderGateway(settings=settings_override, app_env=Environment.PRODUCTION)
    # Must remain False per Gate B policy
    assert gateway.is_fallback_enabled is False

    # Fail keys
    for entry in gateway.key_pool._pool:
        entry.status = KeyHealthState.FAILED

    # Must raise AIProviderUnavailableException rather than returning synthetic mock output
    with pytest.raises(AIProviderUnavailableException) as exc_info:
        await gateway.execute_structured(schema=IdeaAgentOutput, prompt="Production test")
    assert exc_info.value.code == "PROVIDER_UNAVAILABLE"


@pytest.mark.asyncio
async def test_consumer_preserves_degraded_state() -> None:
    """Downstream agent consumer does not drop is_degraded state in execution provenance."""
    from backend.app.domain.ai.agents.idea import IdeaAgent
    from backend.tests.unit.ai.fixtures import make_idea_input

    settings = AISettings(
        OPENROUTER_API_KEY_1="sk-bad-1",
        MOCK_PROVIDER=False,
        MOCK_FALLBACK=True,
    )
    gateway = AIProviderGateway(settings=settings, app_env="development")
    for entry in gateway.key_pool._pool:
        entry.status = KeyHealthState.FAILED

    agent = IdeaAgent(gateway=gateway)
    input_data = make_idea_input()
    output, provenance = await agent.execute(input_data)
    assert provenance.provider == "mock"
    assert provenance.is_degraded is True


@pytest.mark.asyncio
async def test_missing_provider_configuration_no_fallback() -> None:
    """When no keys are configured and fallback is disabled, raises immediately with clear error."""
    settings = create_test_settings(
        keys=[None, None, None, None, None],
        mock_provider=False,
    )
    settings.MOCK_FALLBACK = False

    gateway = AIProviderGateway(settings=settings, app_env="development")
    assert gateway.has_live_keys is False
    assert gateway.is_fallback_enabled is False

    with pytest.raises(AIProviderUnavailableException) as exc_info:
        await gateway.execute(AIGenerationRequest(prompt="Test unconfigured"))
    assert exc_info.value.code == "PROVIDER_UNAVAILABLE"


# ──────────────────────────────────────────────────────────────
# 22. Runtime Mock Independence from Test Fixtures (Fix 2A)
# ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_runtime_mock_generation_when_test_fixtures_blocked() -> None:
    """Mock adapter generates valid structured output for all 12 agent contracts even if backend.tests is blocked."""
    import sys
    from unittest.mock import patch

    from backend.app.domain.ai.contracts.agents import (
        FeaturesAgentOutput,
        IdeaAgentOutput,
        MVPAgentOutput,
        MilestoneAgentOutput,
        ReadmeAgentOutput,
        RiskAgentOutput,
        ScopeAgentOutput,
        SpecificationAgentOutput,
        TaskAgentOutput,
        TechnologyAgentOutput,
        TimelineAgentOutput,
    )
    from backend.app.domain.ai.contracts.qa import QAJudgeAgentOutput

    agent_contracts = [
        IdeaAgentOutput,
        FeaturesAgentOutput,
        ScopeAgentOutput,
        TechnologyAgentOutput,
        MVPAgentOutput,
        TaskAgentOutput,
        TimelineAgentOutput,
        RiskAgentOutput,
        MilestoneAgentOutput,
        SpecificationAgentOutput,
        ReadmeAgentOutput,
        QAJudgeAgentOutput,
    ]

    adapter = MockAIProviderAdapter()

    # Deliberately block backend.tests to prove runtime isolation
    with patch.dict(sys.modules, {"backend.tests": None, "backend.tests.unit.ai.fixtures": None}):
        for contract in agent_contracts:
            raw_resp = await adapter.generate_structured(
                prompt=f"Generate {contract.__name__}",
                system_prompt="Deterministic runtime test",
                model="mock-model",
                api_key="mock-key",
                key_alias="key_1",
                schema=contract,
            )
            validated = contract.model_validate_json(raw_resp.text)
            assert isinstance(validated, contract)


@pytest.mark.asyncio
async def test_runtime_mock_arbitrary_nested_pydantic_schema_synthesis() -> None:
    """Mock adapter dynamically synthesizes deeply nested schemas with complex constraints and enums."""
    from enum import Enum

    class Priority(str, Enum):
        LOW = "low"
        MEDIUM = "medium"
        CRITICAL = "critical"

    class DeepChild(BaseModel):
        child_id: str = Field(..., pattern=r"^C\d+$")
        scores: list[float] = Field(..., min_length=1)
        priority: Priority

    class ParentModel(BaseModel):
        title: str = Field(..., min_length=3)
        children: list[DeepChild] = Field(..., min_length=2)
        metadata_map: dict[str, str]

    adapter = MockAIProviderAdapter()
    raw = await adapter.generate_structured(
        prompt="Generate deeply nested schema",
        system_prompt="System",
        model="mock",
        api_key="mock",
        key_alias="k1",
        schema=ParentModel,
    )
    validated = ParentModel.model_validate_json(raw.text)
    assert isinstance(validated, ParentModel)
    assert len(validated.children) >= 2
    assert isinstance(validated.children[0].priority, Priority)
