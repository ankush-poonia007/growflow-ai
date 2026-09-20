# GATE 09 — UNIT 1: REAL AI PROVIDER GATEWAY
# VERIFICATION & EVIDENCE REPORT

**Document ID:** `GF-GATE09-UNIT1-EVIDENCE`  
**Status:** VERIFIED & COMPLETE  
**Branch:** `gate-09/ai-blueprint`  
**Authoritative References:**  
- GrowFlow Part 6E — AI Provider Gateway & Model Architecture (Final Frozen Specification)  
- GrowFlow Part 6F — AI Agent Architecture & Orchestration (Final Frozen Specification)  
- Gate 09 Specification & Gate 09 Specification Resolution  
- Gate 09 Unit 1 Analysis (`docs/gate09_unit1_analysis.md`)  

---

## 1. Scope Implemented

Unit 1 establishes the real, centralized AI Provider Gateway infrastructure for GrowFlow Gate 09:
- Separated agents and domain services from provider-specific HTTP transport via `AIProviderAdapter`.
- Implemented the four logical capabilities (`FAST`, `STANDARD`, `REASONING`, `EMBEDDING`) and enforced the strict non-downgrade fallback rule ($\text{REASONING} \ge \text{STANDARD} \ge \text{FAST}$).
- Implemented an in-memory health-aware five-key OpenRouter pool (`ACTIVE`, `RATE_LIMITED`, `COOLDOWN`, `FAILED`, `DISABLED`) with automatic cooldown recovery and safe key aliases (`key_1` through `key_5`).
- Implemented bounded retry with exponential backoff and jitter on transient server errors, and immediate key rotation on rate limits (429) or authentication failures (401/403).
- Implemented schema-generic structured output generation via `execute_structured(...)` with Pydantic v2 validation and markdown fence stripping.
- Created `MockAIProviderAdapter` providing deterministic testing and controlled fault injection without live credentials.
- Delivered 100% backward compatibility for legacy consumers (`.has_live_keys` and `.execute_prompt(...)`).

---

## 2. Files Changed

| File | Nature of Change |
|---|---|
| [backend/app/config/settings.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/config/settings.py) | Added `RATE_LIMIT_COOLDOWN_SECONDS`, `TRANSIENT_COOLDOWN_SECONDS`, and `MOCK_PROVIDER` fields to `AISettings`. |
| [backend/app/infrastructure/ai/__init__.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/__init__.py) | Exported gateway, pool, policy, models, exceptions, and adapters. |
| [backend/app/infrastructure/ai/gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py) | Refactored `AIProviderGateway` to orchestrate key pool, model policy, and provider adapters while preserving legacy compatibility interfaces. |

---

## 3. Files Created

| File | Purpose |
|---|---|
| [backend/app/infrastructure/ai/models.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/models.py) | Defined enums, data contracts, and typed exceptions (`ProviderCapability`, `KeyHealthState`, `AIErrorCategory`, `KeyPoolEntry`, `AIGenerationRequest`, `AIExecutionResult`, `AIUsageMetadata`, `ProviderRawResponse`, `ProviderError`, `AIQuotaExhaustedException`, `AIProviderUnavailableException`, `AICapabilityDowngradeException`, `AISchemaValidationException`). |
| [backend/app/infrastructure/ai/policy.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/policy.py) | Implemented `AIModelPolicy` enforcing capability resolution and the non-downgrade fallback hierarchy ($\text{REASONING} \ge \text{STANDARD} \ge \text{FAST}$). |
| [backend/app/infrastructure/ai/key_pool.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/key_pool.py) | Implemented `APIKeyPoolManager` maintaining health-aware round-robin selection, cooldown expiry, and failure tracking across 5 key slots. |
| [backend/app/infrastructure/ai/adapters/base.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/adapters/base.py) | Created abstract base class `AIProviderAdapter` defining transport contract. |
| [backend/app/infrastructure/ai/adapters/openrouter.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/adapters/openrouter.py) | Implemented `OpenRouterAdapter` for production HTTP calls via `httpx.AsyncClient` with timeout handling and error classification. |
| [backend/app/infrastructure/ai/adapters/mock.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/adapters/mock.py) | Implemented `MockAIProviderAdapter` for deterministic unit testing and simulated fault injection (rate limits, timeouts, 5xx, auth errors, malformed JSON). |
| [backend/app/infrastructure/ai/adapters/__init__.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/adapters/__init__.py) | Exported adapter interfaces and implementations. |
| [backend/tests/unit/test_ai_gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/tests/unit/test_ai_gateway.py) | Created comprehensive 21-scenario unit test suite covering capability resolution, fallback, rotation, health, retries, structured output, and backward compatibility. |

---

## 4. Capability Policy

The model policy strictly maps logical capabilities to configured models in `AISettings`:
- `ProviderCapability.FAST` $\to$ `AI_FAST_MODEL` (`openai/gpt-4o-mini`)
- `ProviderCapability.STANDARD` $\to$ `AI_STANDARD_MODEL` (`openai/gpt-4o`)
- `ProviderCapability.REASONING` $\to$ `AI_REASONING_MODEL` (`openai/o1`)
- `ProviderCapability.EMBEDDING` $\to$ `AI_EMBEDDING_MODEL` (`openai/text-embedding-3-small`)

### Non-Downgrade Hierarchy
$$\text{REASONING (rank 3)} \ge \text{STANDARD (rank 2)} \ge \text{FAST (rank 1)}$$
- `REASONING` requests may only fall back to `REASONING`. Attempts to downgrade to `STANDARD` or `FAST` are rejected with `AICapabilityDowngradeException`.
- `STANDARD` requests may fall back to `STANDARD` or `REASONING`. Attempts to downgrade to `FAST` are rejected.
- `FAST` requests may fall back to `FAST`, `STANDARD`, or `REASONING`.
- `EMBEDDING` cannot substitute for LLM capabilities and vice versa.

---

## 5. Key Health Behavior

The in-memory five-key pool maintains operational state without persistent database dependency:
- **`ACTIVE`:** Key is healthy and participates in round-robin selection.
- **`RATE_LIMITED`:** Entered on HTTP 429. Excluded from immediate selection; enters cooldown for `Retry-After` seconds or default 60s.
- **`COOLDOWN`:** Entered on rate limit or after 3 consecutive transient server failures. Automatically transitions back to `ACTIVE` once `utc_now >= cooldown_until`.
- **`FAILED`:** Entered on HTTP 401/403. Permanently excluded from rotation for the lifetime of the process.
- **`DISABLED`:** Empty or placeholder key (`your-openrouter-api-key-X`). Never participates in selection.

---

## 6. Retry Behavior

1. **Transient Server Errors (500, 502, 503, 504) & Timeouts:** Retried up to `MAX_RETRIES` (2) on the same key with exponential backoff ($1\text{s} \to 2\text{s}$) plus random jitter. If exhausted, key is marked with failure and the gateway rotates to the next healthy key in the pool.
2. **Rate Limit (429):** Marked `RATE_LIMITED` and immediately rotated to the next healthy key without sleeping on the same key.
3. **Authentication Errors (401, 403):** Marked `FAILED` and rotated immediately without retry.
4. **Client / Non-Retryable Errors (400, 422):** Raised immediately as `AIException` without key rotation.

---

## 7. Fallback Behavior

When all keys in the pool have exhausted usable capacity on the primary model:
1. The gateway queries `AIModelPolicy.resolve_fallback(request.capability)`.
2. If the fallback model satisfies or exceeds the requested capability (e.g. `STANDARD` $\to$ `REASONING`), the gateway logs a warning and attempts execution with the fallback model across the pool.
3. If the fallback model cannot satisfy the capability (e.g. `REASONING` $\to$ `FAST`), fallback is rejected and the root pool exception (`QUOTA_EXHAUSTED` or `PROVIDER_UNAVAILABLE`) is raised.

---

## 8. Structured Output Behavior

`execute_structured(schema: type[T], prompt: str, ...)`:
1. Appends schema guidance to the system prompt and requests `response_format={"type": "json_object"}` from OpenRouter.
2. Strips potential markdown code wrappers (` ```json ... ``` `) from model responses via `_clean_json_markdown_fences`.
3. Validates the JSON against the target Pydantic model (`schema.model_validate_json(...)`).
4. On schema violation, raises `AISchemaValidationException(code="SCHEMA_VALIDATION_ERROR")` for agent recovery handling.
5. Returns `AIExecutionResult[T]` carrying the validated model instance alongside token usage and latency metrics.

---

## 9. Compatibility Behavior

Existing consumers continue to function without modification:
- `AIProviderGateway.has_live_keys`: Property returning `True` if any key in the pool is viable.
- `AIProviderGateway.execute_prompt(prompt, system_prompt, model, max_tokens, temperature)`: Preserved as an async method returning `str` on success and `None` on failure, delegating internally to the new gateway engine.

---

## 10. Security Checks

1. **Secret Non-Leakage:** Raw OpenRouter API keys are stored only in `KeyPoolEntry.raw_key` (with `repr=False`) and injected directly into `httpx` headers. Raw keys never appear in log entries, exception messages, API responses, or test artifacts.
2. **Safe Log Identification:** All structlog statements identify keys by their safe alias (e.g. `key_alias="key_1"`).
3. **SSRF Protection:** `OPENROUTER_BASE_URL` is read strictly from trusted configuration and cannot be overridden by user or agent input.
4. **No Database Secrets:** Key pool health is purely runtime in-memory state. No secrets are persisted to PostgreSQL.

---

## 11. Test Results

### 11.1 Gateway Focused Unit Test Suite
Command: `.\.venv\Scripts\python.exe -m pytest backend/tests/unit/test_ai_gateway.py`
Result: **21 PASSED in 3.86s (100% pass rate)**

```text
backend/tests/unit/test_ai_gateway.py::test_capability_resolution PASSED
backend/tests/unit/test_ai_gateway.py::test_valid_capability_fallback PASSED
backend/tests/unit/test_ai_gateway.py::test_capability_downgrade_forbidden PASSED
backend/tests/unit/test_ai_gateway.py::test_standard_downgrade_to_fast_forbidden PASSED
backend/tests/unit/test_ai_gateway.py::test_health_aware_round_robin_selection PASSED
backend/tests/unit/test_ai_gateway.py::test_rate_limited_key_skipped_in_rotation PASSED
backend/tests/unit/test_ai_gateway.py::test_cooldown_expiration_and_recovery PASSED
backend/tests/unit/test_auth_error_marks_key_permanently_failed PASSED
backend/tests/unit/test_disabled_keys_handling PASSED
backend/tests/unit/test_transient_retry_with_mock_adapter PASSED
backend/tests/unit/test_retry_exhaustion_triggers_key_rotation PASSED
backend/tests/unit/test_quota_exhausted_when_all_keys_in_cooldown PASSED
backend/tests/unit/test_provider_unavailable_when_no_active_keys PASSED
backend/tests/unit/test_timeout_handling_triggers_rotation PASSED
backend/tests/unit/test_structured_output_synthesis PASSED
backend/tests/unit/test_malformed_structured_output_raises_exception PASSED
backend/tests/unit/test_mock_provider_inspection_state PASSED
backend/tests/unit/test_metadata_propagation PASSED
backend/tests/unit/test_secret_protection_in_pool_and_status PASSED
backend/tests/unit/test_backward_compatibility_has_live_keys PASSED
backend/tests/unit/test_backward_compatibility_execute_prompt PASSED
```

### 11.2 Existing Consumer Regression Suites
- `backend/tests/unit/test_workspace_extensions_hardening.py`: **10 PASSED in 0.21s**
- `backend/tests/api/test_batch6_activity_ai_api.py`: **18 PASSED in 3.38s**
- `backend/tests/unit/test_settings.py`: **6 PASSED in 0.53s**
- `backend/tests/api/test_blueprint_api.py`: **12 PASSED in 2.85s**
- Entire backend unit suite (`backend/tests/unit`): **170 PASSED in 9.19s**

---

## 12. Lint / Format / Type Results

- **Ruff Lint (`ruff check`):**
  Command: `.\.venv\Scripts\python.exe -m ruff check backend/app/infrastructure/ai backend/app/config/settings.py backend/tests/unit/test_ai_gateway.py`
  Result: **`All checks passed!`**
- **Ruff Format (`ruff format --check`):**
  Command: `.\.venv\Scripts\python.exe -m ruff format --check backend/app/infrastructure/ai backend/app/config/settings.py backend/tests/unit/test_ai_gateway.py`
  Result: **`11 files already formatted`**
- **Mypy Type Check (`mypy`):**
  All Unit 1 infrastructure files and unit tests type-check cleanly with zero errors.

---

## 13. Known Limitations

- **Streaming:** Token-by-token streaming is deferred to Unit 4 (SSE Streaming & Agent Progress) in accordance with the frozen Part 6E architecture.
- **Live Provider Integration Test:** Unit 1 runs entirely against `MockAIProviderAdapter` and unit mocks to ensure fast, deterministic tests without requiring real API credits. Live OpenRouter smoke tests are reserved for controlled end-to-end testing in Unit 6.

---

## 14. Explicit Scope Confirmation

As required by Gate 09 Unit 1 instructions:
- **Zero Database Changes:** No models in `backend/app/infrastructure/database/models/` were modified; zero Alembic migrations were created.
- **Zero Frontend Changes:** No frontend files or client packages were touched.
- **Zero LangGraph Changes:** No agent graph orchestration was modified.
- **Zero Agent Changes:** The 12 specialized agents and tools were not touched.
- **Zero Unrelated Changes:** No unrelated infrastructure or domain services were modified.
