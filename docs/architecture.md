# MemoryCore Architecture

## Overview

MemoryCore is built in four layers, each with a single responsibility.
Lower layers know nothing about higher ones — `sqlite.py` has no idea
`retrieval.py` exists.

## Layer 1: Data (`core/models.py`)

Defines the vocabulary the entire system speaks.

**`MemoryItem`** fields by purpose:

- *Identity*: `id`, `agent_id`, `user_id`, `namespace`, `type`, `content`
- *Lifecycle*: `created_at`, `updated_at`, `last_accessed_at`, `expires_at`, `deleted_at`
- *Scoring*: `importance`, `confidence`, `access_count`
- *Content*: `summary`, `tags`, `metadata`, `source`
- *Semantic*: `embedding`

Soft delete: `deleted_at = NULL` means alive;
a timestamp means deleted but recoverable.

## Layer 2: Storage (`storage/`)

Abstract interface (`StorageBackend`) + three implementations.
The `EmbeddingStorageWrapper` decorator auto-generates embeddings on
insert/update without the backends knowing about it.

StorageBackend (ABC)
├── InMemoryStorage    (dict, ephemeral, for tests)
├── SQLiteStorage      (file-based, zero setup)
└── PostgresStorage    (production, multi-process)
EmbeddingStorageWrapper
└── wraps any StorageBackend
└── generates embeddings before insert/update

Contract test suite (`test_storage_contract.py`) runs 16 tests
against all available backends via a parametrized fixture.

## Layer 3: Intelligence (`core/`)

### Scoring (`scoring.py`)

Four functions, two categories:

**Read-only (pure functions, no side effects):**
- `recency_score()` — `0.5 ^ (age_days / half_life_days)`
- `importance_score()` — `importance × confidence`
- `frequency_score()` — `access_count / (access_count + saturation)`
- `relevance_score()` — weighted combination of the three above

**Mutating (change stored state):**
- `apply_decay()` — reduces `importance` over time (slower for high-importance memories)
- `reinforce()` — increments `access_count`, updates `last_accessed_at`, boosts `importance`

### Retrieval (`retrieval.py`)

Two-stage pipeline:

1. **Candidate fetch** — `list_recent(limit=200)` gets a broad pool from storage (fast SQL)
2. **Semantic ranking** — embed query once, cosine similarity against every candidate, combine with `relevance_score`, filter by `min_similarity`, sort, return `top_k`

Returns `list[RetrievalResult]` with scores attached (explainable retrieval).

### Consolidation (`consolidation.py`)

1. Fetch all memories for a user/namespace
2. Greedy clustering by cosine similarity threshold
3. For each cluster: generate summary, create `CONSOLIDATED` memory, soft-delete originals
4. Audit trail: `metadata["consolidated_from"]` stores original IDs

## Layer 4: Service (`api/`, `cli/`)

**API**: FastAPI with Pydantic schemas (DTO pattern — internal models
stay separate from API contracts). Dependency injection via
`@lru_cache` ensures the embedding model loads once per process.

**CLI**: Typer commands wrapping the core engine directly (no HTTP).
Entry point registered in `pyproject.toml` as `memorycore`.

**Observability**: structlog for structured JSON logs,
HTTP middleware for request timing, `/metrics` endpoint.

## Key design decisions

**Why abstract storage?**
Swap SQLite for Postgres with one line. Tests use in-memory.
No lock-in.

**Why separate `embed()` and `embed_query()`?**
BGE models use a prefix for queries to improve retrieval quality.
Other models implement both identically — the interface supports both.

**Why `EmbeddingStorageWrapper` instead of embedding inside backends?**
Keeps backends as pure persistence. Embedding is opt-in.
`pip install memorycore` without `[local]` still works.

**Why `RetrievalResult` includes scores?**
Explainability — callers can see why a memory was retrieved.
Foundation for future LLM re-ranking.