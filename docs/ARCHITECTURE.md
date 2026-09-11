# GrowFlow — Module Boundaries & Import Policy

**Status:** FROZEN (Gate 01)
**Authority:** Phase 6A Backend Architecture (`docs/6A_Backend_Architecture_Final.md`)

---

## Layer Dependency Rules

Imports must flow **strictly downward**. Never import upward or sideways across unrelated modules.

```
API Layer
  ↓ imports
Application Layer
  ↓ imports
Domain Layer
  ↓ imports
Infrastructure Layer (via interfaces only)
  ↓ implements
External Systems
```

### Permitted import directions

| From (importer) | May import from |
|---|---|
| `api/` | `application/`, `app/shared/`, `app/config/` |
| `application/` | `domain/`, `app/shared/`, `app/config/` |
| `domain/` | `app/shared/` only — **no infrastructure imports** |
| `infrastructure/` | `domain/` interfaces, `app/shared/`, `app/config/` |
| `workers/` | `application/`, `domain/`, `infrastructure/`, `app/shared/` |
| `shared/` | No application/domain/infrastructure imports |
| `config/` | No application/domain/infrastructure imports |

### Prohibited patterns

- Domain code importing infrastructure implementations
- API routes containing business logic or database queries
- Direct `.env` access outside `config/settings.py`
- Any module importing from `tests/`
- Circular imports between layers

---

## Package Ownership Map

```
backend/
├── app/
│   ├── config/          ← Typed settings, environment loading, validation
│   │                      Owner: Gate 02
│   ├── api/             ← HTTP transport: routing, request parsing, auth deps,
│   │   ├── routes/        serialization, HTTP status codes
│   │   ├── dependencies/  Owner: Gates 02, 04, 05+
│   │   ├── schemas/
│   │   └── responses/
│   │
│   ├── application/     ← Use cases, commands, queries, orchestration
│   │   ├── services/      Owner: Gates 05+
│   │   ├── commands/
│   │   ├── queries/
│   │   └── use_cases/
│   │
│   ├── domain/          ← Business concepts, rules, value objects, interfaces
│   │   ├── identity/      Owner: Gates 04, 05+
│   │   ├── organization/
│   │   ├── project/
│   │   ├── planning/
│   │   ├── execution/
│   │   ├── communication/
│   │   ├── knowledge/
│   │   ├── integrations/
│   │   ├── ai/
│   │   └── platform/
│   │
│   ├── infrastructure/  ← Persistence, adapters, AI gateways, external providers
│   │   ├── database/      Owner: Gate 03+
│   │   ├── repositories/
│   │   ├── ai/            Owner: Gate 09+
│   │   ├── github/        Owner: Gate 12+
│   │   ├── tavily/        Owner: Gate 09+
│   │   ├── rag/           Owner: Gate 11+
│   │   ├── storage/       Owner: Gate 11+
│   │   ├── email/         Owner: Gate 14+
│   │   └── observability/ Owner: Gate 15+
│   │
│   ├── workers/         ← Background job execution, async task runners
│   │                      Owner: Gate 08+
│   │
│   └── shared/          ← Cross-cutting: exceptions, logging, security utils,
│       ├── exceptions/    events, utilities, constants
│       ├── logging/       Owner: Gate 02+
│       ├── security/
│       ├── events/
│       ├── utilities/
│       └── constants/
│
├── tests/               ← Test suite, mirrors app structure
│   ├── unit/              Owner: per gate
│   ├── integration/
│   ├── api/
│   └── e2e/
│
├── migrations/          ← Alembic migration files
│                          Owner: Gate 03+
│
└── scripts/             ← Development and operational scripts
                           Owner: per gate as needed
```

---

## Domain Module Boundaries

Each domain module owns its own business concepts and does **not** reach into adjacent modules.

| Module | Owns | Does NOT own |
|---|---|---|
| `identity` | Users, roles, profiles, authentication state | Group membership logic |
| `organization` | Groups, group membership, mentorship assignment | Project logic |
| `project` | Project lifecycle, health, phases | Task scheduling |
| `planning` | Blueprints, milestones, features, MVPs, risks | Execution tracking |
| `execution` | Tasks, task completion, progress tracking | Blueprint generation |
| `communication` | Help requests, mentor notes, notifications | Document storage |
| `knowledge` | Document metadata, RAG retrieval contracts | AI provider calls |
| `integrations` | GitHub repository contract, OAuth contract | Business rules |
| `ai` | AI execution state, agent contracts, model selection | LLM provider calls |
| `platform` | System-level platform rules | Role business logic |

---

## AI Boundary

AI cannot directly mutate authoritative state. The enforced boundary is:

```
Application Use Case
  → AI Orchestrator
  → Agent
  → Authorized Tools (database reads, RAG retrieval)
  → Provider Gateway
  → Structured Pydantic Output
  → Pydantic Validation
  → QA / Judge
  → Deterministic Domain Service
  → Database
```

**Prohibited:** Agents writing directly to the database, bypassing authorization through tools, or persisting raw unvalidated LLM output.

---

## Configuration Boundary

`.env` is read **only** in `config/settings.py`. All other application code receives typed settings via FastAPI dependency injection.

```
.env
  → config/settings.py  (Settings, pydantic-settings)
  → FastAPI DI          (get_settings dependency)
  → Application Components
```

**Prohibited:** `os.getenv()` or `dotenv.load_dotenv()` in application, domain, or infrastructure code.

---

## Secret Handling

- Never hard-code secrets
- Never log secrets
- Never return secrets through APIs
- Never expose service-role keys to the frontend
- Never expose AI provider keys in Admin UI
- `.env` is in `.gitignore` and must never be committed

---

*This document is authoritative for import and module boundaries from Gate 01 onward.
Architecture authority: Phase 6A — `docs/6A_Backend_Architecture_Final.md`.*
