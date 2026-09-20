# GATE 09 — UNIT 1: REAL AI PROVIDER GATEWAY
# ARCHITECTURAL ANALYSIS & IMPLEMENTATION BOUNDARY REPORT

**Document ID:** `GF-GATE09-UNIT1-ANALYSIS`  
**Status:** COMPLETED — ANALYSIS ONLY  
**Branch:** `gate-09/ai-blueprint`  
**Authoritative References:**  
- GrowFlow Part 6E — AI Provider Gateway & Model Architecture (Final Frozen Specification)  
- GrowFlow Part 6F — AI Agent Architecture & Orchestration (Final Frozen Specification)  
- Gate 09 Specification & Gate 09 Specification Resolution (`gate09_spec_resolution.md`)  
- Gate 09 Analysis Report (`gate09_analysis.md`)  

---

## 1. Executive Summary

GrowFlow Gate 09 transitions the project blueprint generation pipeline from static mock synthesis into an authentic, multi-agent artificial intelligence engine. The prerequisite foundation of this entire architecture is **Unit 1: Real AI Provider Gateway**.

As mandated by GrowFlow Part 6E § 1:
> *"No application component, agent, tool, route, or worker may communicate directly with an external AI provider. All provider communication passes through the AI Provider Gateway."*

This analysis evaluates the current repository state against the frozen Part 6E specification and the explicitly approved Gate 09 decisions:
- **Decision A1:** 12-agent dependency topology with strictly serial `TASK` → `MILESTONE` execution.
- **Decision A3:** QA pass criteria (score $\ge 75$ with zero CRITICAL findings) and maximum 2 automatic targeted regeneration attempts.
- **Decision A4:** Four logical provider capabilities (`FAST`, `STANDARD`, `REASONING`, `EMBEDDING`) with strict non-downgrade capability enforcement ($\text{REASONING} \ge \text{STANDARD} \ge \text{FAST}$).
- **Decision A5:** Cooperative cancellation (`RUNNING` $\to$ `CANCELLING` $\to$ `CANCELLED`) checked at safe execution boundaries.

**Key Findings:**
1. The current `backend/app/infrastructure/ai/gateway.py` is an unhardened 99-line placeholder. It uses naive round-robin across raw string keys without health states, skips retries, lacks cooldowns, treats all errors identically, ignores capability tiers, and discards token usage.
2. The platform's existing consumers (`mentor_ai_service.py`, `ai_mentor_service.py`, and `blueprint_service.py`) and their associated test suites rely on two contracts on the gateway: `.has_live_keys` and `.execute_prompt(...)`.
3. All necessary runtime dependencies (`httpx`, `tenacity`, `openai`, `pydantic`, `pydantic-settings`, `structlog`) are already declared in `pyproject.toml` and `requirements.txt`.
4. Unit 1 can be implemented **entirely within the infrastructure layer** with **zero database migrations**, **zero frontend changes**, and **100% backward compatibility** for existing services.

**Readiness Verdict:** **`READY FOR UNIT 1 IMPLEMENTATION`**

---

## 2. Current AI Infrastructure

A rigorous inspection of the current backend repository identified the following components and configurations:

### 2.1 File Inventory
- [gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py): Implements `AIProviderGateway`. Contains an inlined OpenRouter HTTP client call via `httpx.AsyncClient`.
- [__init__.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/__init__.py): Re-exports `AIProviderGateway`.
- [settings.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/config/settings.py): Lines 88–140 define `AISettings`, including OpenRouter keys, models, timeouts, and retry settings.
- [exceptions/base.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/shared/exceptions/base.py): Defines `AIException` (code `AI_PROVIDER_ERROR`, HTTP 502) and `RAGException`.
- [logging/filters.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/shared/logging/filters.py): Implements `redact_sensitive_data` and structlog processor `redact_secrets_processor` masking sensitive patterns (`api_key`, `token`, `secret`, `authorization`).
- [logging/context.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/shared/logging/context.py): Implements `get_correlation_id()`, `set_correlation_id()`, `get_request_id()`.

### 2.2 Configuration & Environment Variables
In [settings.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/config/settings.py) and [backend/.env.example](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/.env.example):
- `OPENROUTER_BASE_URL` (default `https://openrouter.ai/api/v1`)
- `OPENROUTER_API_KEY_1` through `OPENROUTER_API_KEY_5` (five-key pool)
- `OPENROUTER_HTTP_REFERER` (`https://growflow.app`)
- `OPENROUTER_X_TITLE` (`GrowFlow`)
- `AI_FAST_MODEL` (`openai/gpt-4o-mini`)
- `AI_STANDARD_MODEL` (`openai/gpt-4o`)
- `AI_REASONING_MODEL` (`openai/o1`)
- `AI_EMBEDDING_MODEL` (`openai/text-embedding-3-small`)
- `AI_DEFAULT_MODEL` (`openai/gpt-4o`)
- `AI_FALLBACK_MODEL` (`openai/gpt-4o-mini`)
- `AI_REQUEST_TIMEOUT_SECONDS` (default `60`)
- `AI_MAX_RETRIES` (default `3`)
- `AI_RETRY_INITIAL_DELAY_SECONDS` (default `1`)
- `AI_RETRY_MAX_DELAY_SECONDS` (default `8`)

### 2.3 Existing Consumers & Invocations
| Consumer File | Calling Method / Property | Usage Context |
|---|---|---|
| [mentor_ai_service.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/application/services/mentor_ai_service.py#L160) | `.has_live_keys`, `.execute_prompt(...)` | Group AI mentor consultation & advice |
| [ai_mentor_service.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/application/services/ai_mentor_service.py#L140) | `.has_live_keys`, `.execute_prompt(...)` | Workspace AI mentor consultations |
| [blueprint_service.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/application/services/blueprint_service.py#L113) | `__init__(..., ai_gateway=...)` | Dependency injection in blueprint generation service |
| [test_batch6_activity_ai_api.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/tests/api/test_batch6_activity_ai_api.py#L496) | `MagicMock(spec=AIProviderGateway)` | Tests mocking `.has_live_keys` and `.execute_prompt` |
| [test_workspace_extensions_hardening.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/tests/unit/test_workspace_extensions_hardening.py#L695) | `MagicMock(spec=AIProviderGateway)` | Tests checking mentor offline posture and prompts |

---

## 3. 6E Compliance Matrix

The following matrix audits the codebase against each requirement of GrowFlow Part 6E:

| 6E Requirement | Current Implementation | Gap Description | Unit 1 Action | Deferred? |
|---|---|---|---|---|
| **Logical Capability vs Concrete Model** (6E § 16, § 17) | Model strings defined in `AISettings` (`FAST_MODEL`, etc.) | No enum or domain representation for capabilities; callers pass concrete model strings. | Implement `ProviderCapability` enum and `AIModelPolicy` registry. | **No** |
| **Agent / Provider Separation** (6E § 1, § 6, § 9) | Gateway exists, but is a monolith without adapter separation. | OpenRouter API calls are coupled directly inside gateway logic. | Extract `AIProviderAdapter` ABC, `OpenRouterAdapter`, and `MockAIProviderAdapter`. | **No** |
| **Five-Key Pool Management** (6E § 10, § 11) | `AISettings.active_keys` returns list of raw string keys. | No typed key pool entries, no tracking of aliases or metadata. | Implement `KeyPoolEntry` with immutable aliases (`key_1`..`key_5`) and `APIKeyPoolManager`. | **No** |
| **Key Health States** (6E § 12, § 15) | None. | Keys are never marked rate-limited, failed, or cooling down. | Implement `KeyHealthState` state machine (`ACTIVE`, `RATE_LIMITED`, `COOLDOWN`, `FAILED`, `DISABLED`). | **No** |
| **Health-Aware Key Selection** (6E § 13) | Naive round-robin `_key_index % len(keys)`. | Does not filter out degraded, rate-limited, or failed keys. | Implement health-aware round-robin selection over eligible keys. | **No** |
| **Rate-Limit & Cooldown** (6E § 21) | 429 status logged as warning; returns `None`. | No cooldown duration applied; key is reselected on next call. | Implement 429 detection, `Retry-After` parsing, `RATE_LIMITED` transition, and cooldown expiry. | **No** |
| **Bounded Retry & Backoff** (6E § 20) | None. Single HTTP request per execution. | No retries on transient errors; configured retry settings are ignored. | Implement bounded retry with exponential backoff and jitter for transient errors. | **No** |
| **Error Classification** (6E § 19) | Catch-all `except Exception: return None`. | Errors are not classified; transient errors and auth errors treated identically. | Implement `AIErrorClassifier` mapping HTTP codes and exceptions to standard categories. | **No** |
| **Capability-Aware Fallback** (6E § 18, Gate 09 A4) | None. Call returns `None` on failure. | No fallback model evaluated; no enforcement of $\text{REASONING} \ge \text{STANDARD} \ge \text{FAST}$. | Enforce capability-aware fallback; forbid capability downgrades centrally in gateway. | **No** |
| **Quota-Exhaustion Handling** (6E § 22, § 23) | None. | Exhaustion causes silent `None` response; no specific error code or state. | Raise typed `AIException(code="QUOTA_EXHAUSTED")` when all keys exhausted and fallback unavailable. | **No** |
| **Provider Abstraction** (6E § 7, § 80) | Monolithic `AIProviderGateway`. | Inflexible; cannot substitute mock or alternative provider adapters. | Create `AIProviderAdapter` abstract base class. | **No** |
| **Deterministic Mock Adapter** (6E § 89, § 90) | None in AI package; tests mock at unittest level. | Cannot run deterministic integration/agent tests against gateway. | Implement `MockAIProviderAdapter` supporting success, rate-limit, timeout, and failure simulation. | **No** |
| **Structured Output Support** (6E § 44, § 45) | `execute_prompt` returns raw `str \| None`. | No schema-enforced output generation, JSON parsing, or Pydantic validation. | Implement `execute_structured(schema: type[T], ...)` with validation and error recovery. | **No** |
| **Streaming Support** (6E § 28, § 29) | Unary only. | No streaming token generator. | Define streaming method interface on adapter; defer SSE pipeline to Unit 4. | **Deferred to Unit 4** |
| **Usage & Token Accounting** (6E § 56, § 57) | Response `usage` block is discarded in `gateway.py:86-89`. | Prompt/completion tokens not extracted; cost estimation missing. | Extract `usage` from provider response into `AIUsageMetadata`; calculate cost if pricing configured. | **No** |
| **Observability Metadata** (6E § 58, § 61) | Logs basic info/warning only. | Callers receive no metadata (latency, model, key alias, tokens). | Return `AIExecutionResult` containing content, model, provider, key alias, latency, and tokens. | **No** |
| **Security & Secret Redaction** (6E § 74, § 75, § 76) | Redaction filter exists in logging module. | No key aliases; potential risk of logging raw keys if not carefully handled. | Use immutable aliases (`key_1`) for logging; keep raw secrets confined to adapter transport. | **No** |

---

## 4. Current Gateway Gap Analysis

Evaluation of capabilities A through Z:

- **A. Provider abstraction:** **`MISSING`**  
  *Location:* [gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L27)  
  *Finding:* No `AIProviderAdapter` interface or protocol exists. `AIProviderGateway` directly handles HTTP transport.
- **B. OpenRouter adapter:** **`EXISTS BUT INCOMPLETE`**  
  *Location:* [gateway.py:78-95](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L78-L95)  
  *Finding:* HTTP headers and `/chat/completions` request body are hardcoded inside `execute_prompt`.
- **C. Mock provider:** **`MISSING`**  
  *Location:* [infrastructure/ai/](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/)  
  *Finding:* No `MockAIProviderAdapter` exists. Tests must manually inject `MagicMock` instances.
- **D. Provider capability model:** **`EXISTS BUT INCOMPLETE`**  
  *Location:* [settings.py:112-117](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/config/settings.py#L112-L117)  
  *Finding:* Settings define `FAST_MODEL`, `STANDARD_MODEL`, etc., but there is no `ProviderCapability` enum or typed representation.
- **E. Model policy:** **`MISSING`**  
  *Location:* [gateway.py:61](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L61)  
  *Finding:* Gateway accepts an arbitrary string `model: str | None`. It does not resolve logical capabilities or enforce model selection rules.
- **F. API key pool:** **`EXISTS BUT INCOMPLETE`**  
  *Location:* [settings.py:126-139](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/config/settings.py#L126-L139)  
  *Finding:* `AISettings.active_keys` provides a string list, but there are no pool entry abstractions or state tracking.
- **G. Key health state:** **`MISSING`**  
  *Location:* [gateway.py:30-46](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L30-L46)  
  *Finding:* No health states exist. All non-empty keys are treated as perpetually healthy.
- **H. Round-robin / selection:** **`EXISTS BUT INCOMPLETE`**  
  *Location:* [gateway.py:44-46](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L44-L46)  
  *Finding:* Implements `self._key_index % len(keys)` without filtering for availability or health.
- **I. Rate-limit handling:** **`MISSING`**  
  *Location:* [gateway.py:90-95](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L90-L95)  
  *Finding:* HTTP 429 is treated as a generic non-200 error. The key is not marked rate-limited, and no rotation occurs.
- **J. Cooldown:** **`MISSING`**  
  *Location:* [gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py)  
  *Finding:* No cooldown timers, timestamps, or recovery logic exist.
- **K. Retry:** **`MISSING`**  
  *Location:* [gateway.py:78-95](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L78-L95)  
  *Finding:* Executes a single `client.post`. On failure, it immediately logs and returns `None`.
- **L. Exponential backoff:** **`MISSING`**  
  *Location:* [settings.py:122-123](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/config/settings.py#L122-L123)  
  *Finding:* Delay settings exist in config but are never read or applied by the gateway.
- **M. Jitter:** **`MISSING`**  
  *Location:* [gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py)  
  *Finding:* No randomized jitter logic exists.
- **N. Error classification:** **`MISSING`**  
  *Location:* [gateway.py:96-98](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L96-L98)  
  *Finding:* Catch-all `except Exception` treats timeouts, DNS errors, 401s, 429s, and 500s identically.
- **O. Capability-aware fallback:** **`MISSING`**  
  *Location:* [gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py)  
  *Finding:* No fallback model execution logic exists.
- **P. No-downgrade enforcement:** **`MISSING`**  
  *Location:* [gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py)  
  *Finding:* Capability hierarchy is not evaluated or enforced.
- **Q. Structured output support:** **`MISSING`**  
  *Location:* [gateway.py:48-55](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L48-L55)  
  *Finding:* Gateway only provides `execute_prompt` returning `str | None`.
- **R. Streaming support:** **`NOT REQUIRED FOR UNIT 1`**  
  *Location:* [gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py)  
  *Finding:* Streaming is an SSE/API concern for blueprint progress; deferred to Unit 4.
- **S. Timeout handling:** **`EXISTS BUT INCOMPLETE`**  
  *Location:* [gateway.py:79](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L79)  
  *Finding:* Timeout argument passed to `httpx.AsyncClient`, but timeout exceptions are swallowed without triggering key rotation.
- **T. Usage metadata:** **`MISSING`**  
  *Location:* [gateway.py:86-89](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L86-L89)  
  *Finding:* Provider `usage` block (`prompt_tokens`, `completion_tokens`) is ignored.
- **U. Token accounting:** **`MISSING`**  
  *Location:* [gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py)  
  *Finding:* No token data structures or tracking exist.
- **V. Provider/model metadata:** **`MISSING`**  
  *Location:* [gateway.py:88](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L88)  
  *Finding:* Model name is logged, but no execution metadata is returned to the caller.
- **W. Correlation/execution IDs:** **`MISSING`**  
  *Location:* [gateway.py:48-55](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L48-L55)  
  *Finding:* Parameters do not accept or track correlation or execution IDs.
- **X. Logging/telemetry hooks:** **`EXISTS BUT INCOMPLETE`**  
  *Location:* [gateway.py:88, 91, 97](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py#L88)  
  *Finding:* Emits basic structlog messages, but lacks latency, key alias, and retry telemetry.
- **Y. Secret protection:** **`EXISTS BUT INCOMPLETE`**  
  *Location:* [logging/filters.py:20-50](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/shared/logging/filters.py#L20-L50)  
  *Finding:* Logging filter masks sensitive strings, but gateway does not define safe key aliases for log identification.
- **Z. Testability:** **`MISSING`**  
  *Location:* [backend/tests/](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/tests/)  
  *Finding:* No unit tests exist for `AIProviderGateway` itself.

---

## 5. Exact Unit 1 Boundary

Unit 1 delivers the hardened, capability-aware, multi-key provider infrastructure layer.

```
                      Agent Request
                            │
                            ▼
               ┌────────────────────────┐
               │   AIProviderGateway    │
               └────────────┬───────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐
│  AIModelPolicy  │ │ APIKeyPoolMgr │ │  ErrorClassifier│
│(Capability/Fall)│ │(Health/Rotate)│ │ (Retry/Cooldown)│
└─────────────────┘ └───────────────┘ └─────────────────┘
                            │
                            ▼
                 ┌────────────────────┐
                 │ AIProviderAdapter  │  (Abstract Base Class)
                 └─────────┬──────────┘
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
  ┌───────────────────┐         ┌───────────────────┐
  │ OpenRouterAdapter │         │MockAIProviderAdapt│
  └───────────────────┘         └───────────────────┘
```

### 5.1 In-Scope for Unit 1
1. **Capability Model & Policy:** `ProviderCapability` enum (`FAST`, `STANDARD`, `REASONING`, `EMBEDDING`), model mapping, and fallback validator enforcing $\text{REASONING} \ge \text{STANDARD} \ge \text{FAST}$.
2. **Key Health State Machine:** Five operational states (`ACTIVE`, `RATE_LIMITED`, `COOLDOWN`, `FAILED`, `DISABLED`), failure counting, cooldown calculation, and automatic recovery.
3. **Key Pool Manager:** Round-robin selection over healthy keys with immutable aliases (`key_1` through `key_5`).
4. **Error Classification & Retry Policy:** Categorization into `RETRYABLE`, `RATE_LIMITED`, `AUTH_FAILURE`, and `NON_RETRYABLE`, with bounded exponential backoff and jitter.
5. **Adapter Abstraction & Implementations:**
   - Abstract `AIProviderAdapter`.
   - Production `OpenRouterAdapter` using `httpx.AsyncClient`.
   - Deterministic `MockAIProviderAdapter` for tests (supporting simulated rate-limits, timeouts, and structured synthesis).
6. **Structured Output Engine:** `execute_structured(schema: type[T], ...)` returning validated Pydantic models with token and execution metadata.
7. **Consumer Backward Compatibility:** Preserving `execute_prompt(...)` and `.has_live_keys` so that existing services (`ai_mentor_service.py`, `mentor_ai_service.py`, `blueprint_service.py`) and existing tests continue to work without modification.
8. **Unit Test Suite:** Comprehensive suite in `backend/tests/unit/test_ai_gateway.py`.

### 5.2 Explicitly Out of Scope for Unit 1
- **No Database Changes:** No Alembic migrations, no new tables. Key health and pool metrics reside in memory.
- **No Frontend Changes:** Zero modifications to React or client bundles.
- **No Agent Implementations:** The 12 specialized agents belong to Units 2 & 3.
- **No LangGraph Orchestration:** StateGraph, edges, and checkpoints belong to Unit 4.
- **No SSE Streaming Endpoints:** Streaming transport belongs to Unit 4/5.
- **No RAG / LlamaIndex:** Document chunking and embedding pipelines belong to Gate 11.

---

## 6. Proposed Gateway Contract

The gateway contract completely shields agents from API keys, HTTP payloads, and vendor-specific endpoints.

### 6.1 Input Contract (`AIGenerationRequest`)
```python
@dataclass(frozen=True)
class AIGenerationRequest:
    prompt: str
    system_prompt: str = "You are the GrowFlow Architectural Intelligence Engine."
    capability: ProviderCapability = ProviderCapability.STANDARD
    model: str | None = None          # Explicit override if permitted
    schema: type[T] | None = None      # Pydantic schema for structured generation
    temperature: float = 0.2
    max_tokens: int = 4000
    timeout_seconds: float | None = None
    correlation_id: str | None = None
    execution_id: str | None = None
```

### 6.2 Output Contract (`AIExecutionResult[T]`)
```python
@dataclass(frozen=True)
class AIExecutionResult(Generic[T]):
    content: T | str                   # Validated Pydantic instance or text
    raw_text: str
    provider: str                      # e.g. "openrouter" or "mock"
    model: str                         # Concrete model executed
    capability: ProviderCapability
    key_alias: str                     # Safe alias e.g. "key_1"
    latency_ms: float
    usage: AIUsageMetadata | None
    retry_count: int = 0
    correlation_id: str | None = None
```

### 6.3 Usage Contract (`AIUsageMetadata`)
```python
@dataclass(frozen=True)
class AIUsageMetadata:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float | None = None
```

### 6.4 Public Gateway Interface
```python
class AIProviderGateway:
    def __init__(
        self,
        settings: AISettings | None = None,
        adapter: AIProviderAdapter | None = None,
    ) -> None: ...

    @property
    def has_live_keys(self) -> bool: ...

    async def execute(self, request: AIGenerationRequest) -> AIExecutionResult[str]: ...

    async def execute_structured(
        self,
        schema: type[T],
        prompt: str,
        system_prompt: str = ...,
        capability: ProviderCapability = ProviderCapability.STANDARD,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        correlation_id: str | None = None,
    ) -> AIExecutionResult[T]: ...

    # Backward-compatible method
    async def execute_prompt(
        self,
        prompt: str,
        system_prompt: str = ...,
        model: str | None = None,
        max_tokens: int = 4000,
        temperature: float = 0.2,
    ) -> str | None: ...
```

---

## 7. Key Pool / Health State Machine

The key pool operates an in-memory state machine over the five configured slots (`OPENROUTER_API_KEY_1..5`).

### 7.1 States & Transitions
```
                ┌──────────────┐
                │   DISABLED   │  (Unconfigured or placeholder)
                └──────────────┘
                       ▲
                       │ configured at startup
                       ▼
                ┌──────────────┐
        ┌──────►│    ACTIVE    │◄────────────────────────┐
        │       └──────┬───────┘                         │
        │              │                                 │
        │ 429 received │                                 │ Cooldown expired
        │              ▼                                 │ & key healthy
        │       ┌──────────────┐                         │
        │       │ RATE_LIMITED │                         │
        │       └──────┬───────┘                         │
        │              │ cooldown timer set              │
        │              ▼                                 │
        │       ┌──────────────┐                         │
        │       │   COOLDOWN   │─────────────────────────┘
        │       └──────┬───────┘
        │              │ consecutive 5xx/timeouts >= 3
        │              ▼
        │       ┌──────────────┐
        └───────│    FAILED    │  (Auth 401/403 or exhausted)
                └──────────────┘
```

### 7.2 State Rules
1. **`ACTIVE`:** Key is healthy and eligible for round-robin selection.
2. **`RATE_LIMITED`:** Entered upon receiving HTTP 429. Immediately excluded from selection. Cooldown timer set to provider's `Retry-After` header (or configured default, e.g. 60s).
3. **`COOLDOWN`:** Entered when a key accumulates transient errors or rate-limit cooldown. Excluded from rotation until `utc_now >= cooldown_until`. Automatically transitions to `ACTIVE` upon expiration.
4. **`FAILED`:** Entered upon receiving HTTP 401/403 (invalid key) or after persistent retry exhaustion across recovery windows. Permanently excluded from selection for the runtime process lifetime.
5. **`DISABLED`:** Slot is empty or contains placeholder text (e.g. `your-openrouter-api-key-X`). Never participates in selection.

### 7.3 Selection & Accounting
- Each key entry records: `key_alias`, `status`, `last_used_at`, `last_success_at`, `failure_count`, `rate_limit_count`, `cooldown_until`.
- Selection uses **health-aware round-robin**:
  1. Evaluate all keys; recover any expired `COOLDOWN` / `RATE_LIMITED` keys to `ACTIVE`.
  2. Filter keys where `status == ACTIVE`.
  3. If eligible keys exist, select `eligible_keys[index % len(eligible_keys)]` and increment rotation index.
  4. If no eligible keys exist, evaluate fallback model or raise `AIException(code="QUOTA_EXHAUSTED")`.

---

## 8. Retry / Failure Policy

Failures are categorized into distinct operational responses:

| Error Category | HTTP / Exception Pattern | Gateway Action | Key State Impact |
|---|---|---|---|
| **`RATE_LIMITED`** | HTTP 429 | Rotate immediately to next key. Do not sleep on the same key. | Key $\to$ `RATE_LIMITED` / `COOLDOWN` |
| **`TRANSIENT_SERVER`** | HTTP 500, 502, 503, 504 | Retry up to 2 times with exponential backoff + jitter. If exhausted, rotate key. | Key failure count +1; if $\ge 3$, key $\to$ `COOLDOWN` |
| **`TIMEOUT`** | `httpx.TimeoutException` | Retry once, then rotate key. | Key failure count +1; if $\ge 2$, key $\to$ `COOLDOWN` |
| **`AUTH_ERROR`** | HTTP 401, 403 | Do not retry. Rotate immediately. | Key $\to$ `FAILED` |
| **`NON_RETRYABLE`** | HTTP 400, 422 | Do not retry. Fail immediately. | None (request issue) |
| **`SCHEMA_INVALID`** | Pydantic `ValidationError` | Re-prompt with schema feedback once; if failed, raise error for agent loop. | None (model reasoning issue) |

### 8.1 Distinct Operational Levels
1. **Provider Retry:** Low-level transient connection glitch retried against the same key with exponential backoff ($1\text{s} \to 2\text{s} \to 4\text{s}$) and jitter.
2. **Key Rotation:** When a key encounters 429 or reaches transient failure threshold, it is placed into cooldown and the gateway immediately dispatches the request to the next healthy key in the pool.
3. **Model Fallback:** When all 5 keys are exhausted for the requested model, the gateway checks whether an eligible fallback model satisfies the capability contract.
4. **Terminal Provider Failure:** All keys exhausted, no eligible fallback satisfies capability, or non-retryable error encountered. Returns `QUOTA_EXHAUSTED` or `PROVIDER_UNAVAILABLE`.

### 8.2 Tenacity Evaluation
`tenacity` is declared in `requirements.txt`. It should be applied selectively for low-level HTTP transport retries on idempotent read/generation calls. However, **key rotation must not be embedded inside a static tenacity decorator**, because rotating to a different key and inspecting pool health is dynamic stateful orchestration. Unit 1 will use an async retry/rotation loop or combine tenacity for transport retries with an outer key-rotation manager.

---

## 9. Capability / Fallback Policy

GrowFlow enforces strict logical capabilities (Gate 09 Decision A4 & 6E § 18):
$$\text{REASONING} \ge \text{STANDARD} \ge \text{FAST}$$

### 9.1 Capability Hierarchy & Model Mappings
| Logical Capability | Rank | Default OpenRouter Model | Allowed Fallbacks | Forbidden Fallbacks |
|---|---|---|---|---|
| **`REASONING`** | 3 | `openai/o1` | `REASONING` | `STANDARD`, `FAST` |
| **`STANDARD`** | 2 | `openai/gpt-4o` | `STANDARD`, `REASONING` | `FAST` |
| **`FAST`** | 1 | `openai/gpt-4o-mini` | `FAST`, `STANDARD`, `REASONING` | None |
| **`EMBEDDING`** | 0 | `openai/text-embedding-3-small` | `EMBEDDING` only | Any LLM capability |

### 9.2 Centralized Enforcement
- Fallback eligibility is enforced centrally by `AIModelPolicy` inside the gateway, **never by individual agents**.
- If a `REASONING` request fails across all keys, and the configured fallback model is `AI_FALLBACK_MODEL` (`openai/gpt-4o-mini`, a `FAST` model), the fallback is **strictly rejected**:
  ```python
  if fallback_capability_rank < requested_capability_rank:
      raise AIException(
          f"Capability downgrade forbidden: requested {requested_capability.value} "
          f"cannot fallback to {fallback_model} ({fallback_capability.value})",
          code="CAPABILITY_DOWNGRADE_FORBIDDEN",
      )
  ```
- If no compliant model can execute the request, the gateway raises `AIException(code="QUOTA_EXHAUSTED")` or `AIException(code="PROVIDER_UNAVAILABLE")`.

---

## 10. Mock Provider Design

The `MockAIProviderAdapter` guarantees that unit and integration tests run fast, reliably, and deterministically without external network requests or live API keys.

### 10.1 Mock Capabilities
- **Deterministic Response Synthesis:** Returns canned text or auto-generated mock Pydantic model instances matching the requested schema.
- **Configurable Fault Injection:**
  - `set_simulated_rate_limit(after_calls: int = 0)`
  - `set_simulated_timeout(after_calls: int = 0)`
  - `set_simulated_server_error(status_code: int = 502)`
  - `set_simulated_auth_failure()`
  - `set_simulated_malformed_json()`
- **Telemetry & Inspection:**
  - `call_count: int`
  - `invocations: list[AIGenerationRequest]`
  - `last_prompt: str`
  - `last_model: str`
- **Leakage Defense:** The mock adapter is strictly prohibited in production (`APP_ENV == "production"` rejects mock instantiation).

---

## 11. Structured Output / Streaming Decision

### 11.1 Structured Output: INCLUDED in Unit 1
- **Rationale:** All 12 blueprint agents in Gate 09 generate structured Pydantic contracts (`IdeaAnalysis`, `TechStackPlan`, `TaskPlan`, etc.). Providing structured generation at the gateway layer ensures uniform schema validation, JSON repair/retry, and token tracking across all agents.
- **Implementation:** `execute_structured(schema: type[T], ...)` appends strict JSON schema instructions, requests `response_format={"type": "json_object"}` from OpenRouter, validates output via Pydantic v2, and returns a typed `AIExecutionResult[T]`.

### 11.2 Streaming Generation: DEFERRED to Unit 4
- **Rationale:** In GrowFlow Part 6E § 28, streaming is consumed by the client via Server-Sent Events (SSE) during long-running background worker executions.
- **Unit 1 Action:** Define an extensible method signature on `AIProviderAdapter` (`async def generate_stream(...)`), but defer active SSE stream handling and progress pub/sub to Unit 4.

---

## 12. Observability Boundary

Unit 1 establishes basic, robust execution telemetry without premature complexity or dashboard dependencies:
- **`correlation_id`:** Propagated from contextvars (`backend/app/shared/logging/context.py`) into execution metadata and logs.
- **`execution_id`:** Tracked when supplied by callers.
- **`provider` & `model`:** Concrete provider adapter and model name recorded on every result.
- **`capability`:** Logical capability recorded.
- **`key_alias`:** Safe alias (`key_1`..`key_5`) recorded.
- **`latency_ms`:** High-precision execution duration recorded using `time.perf_counter()`.
- **`usage`:** `prompt_tokens`, `completion_tokens`, and `total_tokens` extracted from provider response.
- **`retry_count`:** Number of retries and key rotations tracked.
- **`failure_category`:** Standard error category recorded when errors occur.

---

## 13. Security Review

1. **Secret Protection:** Raw OpenRouter API keys exist only in `AISettings` and inside the low-level `OpenRouterAdapter` HTTP client. Keys are never passed to agents, never returned in API models, and never logged.
2. **Safe Log Identification:** Structlog records log entries using `key_alias="key_1"`, completely preventing raw key leaks in log files.
3. **SSRF Defense (6E § 76):** The base URL is fixed from `AISettings.OPENROUTER_BASE_URL`. Agent prompts or user inputs cannot control or redirect outbound HTTP requests.
4. **Prompt Injection Boundary (6E § 39):** Prompts are treated as untrusted data. System prompts instruct models to generate strict JSON conforming to the schema.
5. **No Database Secrets (6E § 14):** In-memory key tracking ensures no provider API keys are ever stored in database tables.

---

## 14. Test Matrix

The Unit 1 implementation will be validated by a comprehensive suite in `backend/tests/unit/test_ai_gateway.py`:

| # | Test Scenario | Description |
|---|---|---|
| 1 | **Capability Resolution** | `FAST`, `STANDARD`, `REASONING` resolve to configured model strings. |
| 2 | **Valid Fallback** | `STANDARD` request safely falls back to `REASONING` model. |
| 3 | **Capability Downgrade Forbidden** | `REASONING` request attempting fallback to `FAST` model raises `AIException(code="CAPABILITY_DOWNGRADE_FORBIDDEN")`. |
| 4 | **Round-Robin Key Selection** | Successive requests cycle sequentially through configured keys (`key_1` $\to$ `key_2`). |
| 5 | **Rate-Limited Key Skipped** | Key receiving 429 transitions to `RATE_LIMITED` and is skipped on subsequent calls. |
| 6 | **Cooldown Expiration & Recovery** | Key in `COOLDOWN` automatically recovers to `ACTIVE` once `cooldown_until` has passed. |
| 7 | **Authentication Failure Exclusion** | Key receiving 401 transitions to `FAILED` and is permanently excluded from rotation. |
| 8 | **Disabled Key Handling** | Empty or placeholder keys are ignored during pool initialization. |
| 9 | **Transient Error Retry** | HTTP 502 triggers bounded retry with backoff on the same key. |
| 10 | **Retry Exhaustion Key Rotation** | Consecutive transient failures on one key trigger key rotation to the next slot. |
| 11 | **Quota Exhaustion** | When all 5 keys are rate-limited or failed and no fallback is eligible, raises `AIException(code="QUOTA_EXHAUSTED")`. |
| 12 | **Provider Unavailable** | When all keys fail with 5xx/timeouts and no fallback exists, raises `AIException(code="PROVIDER_UNAVAILABLE")`. |
| 13 | **Request Timeout Handling** | `httpx.TimeoutException` marks key and rotates to next available slot. |
| 14 | **Structured Output Synthesis** | Valid JSON matching Pydantic schema is parsed into a typed model instance. |
| 15 | **Malformed JSON Error Recovery** | Unparseable model response triggers recovery attempt or raises structured failure. |
| 16 | **Mock Provider Simulation** | `MockAIProviderAdapter` accurately simulates rate-limits, timeouts, and successful outputs. |
| 17 | **Metadata Propagation** | `AIExecutionResult` correctly carries `latency_ms`, `key_alias`, `tokens`, and `correlation_id`. |
| 18 | **Secret Non-Leakage** | Assert raw API keys never appear in log records, error messages, or result objects. |
| 19 | **Consumer Backward Compatibility** | Legacy `.execute_prompt(...)` and `.has_live_keys` work identically for existing services. |

---

## 15. Consumer Compatibility

To ensure zero regressions across existing tests and features:
- **`AIProviderGateway.has_live_keys`:** Preserved as a property. Returns `True` if any configured key in the pool is in `ACTIVE` or `COOLDOWN` state.
- **`AIProviderGateway.execute_prompt(...)`:** Preserved as an async method with identical signature:
  ```python
  async def execute_prompt(
      self,
      prompt: str,
      system_prompt: str = "You are the GrowFlow Architectural Intelligence Engine.",
      model: str | None = None,
      max_tokens: int = 4000,
      temperature: float = 0.2,
  ) -> str | None:
  ```
  Internally, this method constructs an `AIGenerationRequest` and returns `result.raw_text` or `None` on failure.
- **Existing Tests:** Tests using `MagicMock(spec=AIProviderGateway)` in [test_batch6_activity_ai_api.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/tests/api/test_batch6_activity_ai_api.py) and [test_workspace_extensions_hardening.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/tests/unit/test_workspace_extensions_hardening.py) continue to pass without any alterations.

---

## 16. Files To Modify

| File | Nature of Modification |
|---|---|
| [backend/app/infrastructure/ai/gateway.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/gateway.py) | Refactor `AIProviderGateway` to orchestrate key pool, model policy, and adapters, while preserving legacy compatibility methods. |
| [backend/app/infrastructure/ai/__init__.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/infrastructure/ai/__init__.py) | Re-export `AIProviderGateway`, `ProviderCapability`, `AIExecutionResult`, `AIUsageMetadata`, `OpenRouterAdapter`, and `MockAIProviderAdapter`. |
| [backend/app/config/settings.py](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/backend/app/config/settings.py) | Add cooldown configuration defaults to `AISettings` (`COOLDOWN_SECONDS: int = 60`). |

---

## 17. Files To Create

| File | Purpose |
|---|---|
| `backend/app/infrastructure/ai/models.py` | Enums and dataclasses: `ProviderCapability`, `KeyHealthState`, `AIErrorCategory`, `KeyPoolEntry`, `AIGenerationRequest`, `AIExecutionResult`, `AIUsageMetadata`. |
| `backend/app/infrastructure/ai/key_pool.py` | `APIKeyPoolManager`: Manages the five-key state machine, health transitions, cooldown expiry, and round-robin selection. |
| `backend/app/infrastructure/ai/policy.py` | `AIModelPolicy`: Resolves capabilities to models and enforces the no-downgrade fallback rule ($\text{REASONING} \ge \text{STANDARD} \ge \text{FAST}$). |
| `backend/app/infrastructure/ai/adapters/base.py` | `AIProviderAdapter`: Abstract base class defining the provider contract. |
| `backend/app/infrastructure/ai/adapters/openrouter.py` | `OpenRouterAdapter`: Production adapter communicating with OpenRouter via `httpx.AsyncClient` with usage extraction. |
| `backend/app/infrastructure/ai/adapters/mock.py` | `MockAIProviderAdapter`: Deterministic mock adapter for automated testing with fault simulation. |
| `backend/tests/unit/test_ai_gateway.py` | Complete unit test suite verifying all 19 scenarios in the test matrix. |

---

## 18. Files Explicitly Out of Scope

- `backend/app/infrastructure/database/models/*` (No ORM models touched)
- `backend/migrations/*` (No migrations created)
- `frontend/*` (No frontend files touched)
- `backend/app/application/services/blueprint_service.py` (Generation pipeline changes deferred to Units 3–5)
- `backend/app/application/services/mentor_ai_service.py` (No changes needed)
- `backend/app/application/services/ai_mentor_service.py` (No changes needed)

---

## 19. Dependencies

No new third-party dependencies are required. All necessary packages are already installed and declared in [pyproject.toml](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/pyproject.toml) and [requirements.txt](file:///d:/PROJECTS/Infosys%20SpringBoot/growflow_ai/requirements.txt):
- `httpx` (HTTP transport)
- `pydantic` & `pydantic-settings` (Schema validation & typed settings)
- `structlog` (Structured logging)
- `tenacity` (Retry primitives)
- `pytest` & `pytest-asyncio` (Unit testing)

---

## 20. Remaining Risks

1. **OpenRouter Upstream Schema Compliance:** OpenRouter models may occasionally wrap JSON responses in markdown fences (e.g. ` ```json `). The gateway structured synthesis parser must include robust markdown fence stripping before Pydantic parsing.
2. **Provider Rate Limits on Parallel Invocations:** In Gate 09 Decision A1, `TECHNOLOGY`, `FEATURES`, and `MVP` agents execute in parallel. This will issue 3 concurrent LLM calls. The five-key pool with health-aware round-robin is specifically designed to distribute this load across distinct API keys.

---

## 21. Proposed Remaining Gate 09 Units

A coherent, dependency-ordered sequence for Gate 09:

1. **Unit 1 — Real AI Provider Gateway (Current Unit):** Provider adapters, 5-key pool, health states, retry/backoff, capability fallback, structured execution, and mock adapter.
2. **Unit 2 — Agent Contracts, Pydantic Schemas & Context Builder:** Pydantic output contracts for all 12 agents, typed agent state, context builder assembling project & assessment context.
3. **Unit 3 — 12 Specialized AI Agents Implementation & Tool Bindings:** Implementation of Idea, Scope, Tech, Features, Specs, MVP, Timeline, Risk, Task, Milestone, Readme, and QA/Judge agents with typed tools.
4. **Unit 4 — LangGraph Orchestration & Durable Execution Engine:** Graph construction, parallel branches (`Tech`/`Features`/`MVP`), serial `Task` $\to$ `Milestone`, QA judge cycle with max 2 targeted regenerations, cooperative cancellation, and persistent `BlueprintJob`.
5. **Unit 5 — Real-time SSE Streaming & Event Outbox:** `/api/v1/blueprints/{id}/stream` SSE endpoint emitting granular agent progress and `BlueprintGenerated` outbox event emission.
6. **Unit 6 — Gate 09 Full Verification & Integration Hardening:** Comprehensive test execution, student isolation verification, QA threshold verification ($\ge 75$ with zero criticals), and administrative observatory verification.

---

## 22. Final Readiness Verdict

**`READY FOR UNIT 1 IMPLEMENTATION`**

The architecture is completely frozen, all dependencies are present, the boundary is precisely specified, existing consumers are fully protected by compatibility wrappers, and zero database or frontend modifications are needed. Implementation may proceed as soon as authorized.
