# Changelog

All notable changes to MemVault are documented here.

## [0.2.0] — 2026

### Added
- MCP server with 6 tools: `store_memory`, `search_memories`,
  `list_recent_memories`, `consolidate_memories`, `delete_memory`,
  `ingest_conversation`
- Tested with Claude Desktop — memories persist across sessions
- Auto-ingestion pipeline: `MemVault.ingest()` extracts memorable facts
  from raw conversations automatically
- `RuleBasedExtractor` — zero-dependency pattern-matching extraction
- `AnthropicExtractor` — LLM-powered extraction via Claude Haiku
- `BaseExtractor` ABC — bring your own extraction provider

## [0.1.1] — 2026

### Added
- `typer` and `rich` added to core dependencies (CLI now works
  without `[local]` extras)

### Fixed
- CLI entry point missing `typer` dependency

## [0.1.0] — 2026

### Added
- Core memory engine: `MemoryItem`, `MemoryQuery`, `MemoryType`
- Scoring: recency, importance, frequency, `relevance_score()`
- Decay and reinforcement: `apply_decay()`, `reinforce()`
- Storage backends: `SQLiteStorage`, `PostgresStorage`, `InMemoryStorage`
- Contract test suite — 16 tests run against all backends automatically
- BGE-small local embeddings via `sentence-transformers`
- Hybrid semantic retrieval: cosine similarity + relevance scoring
- Consolidation: near-duplicate detection and merging
- `MemVault` facade class — single-import public API
- FastAPI REST API with OpenAPI docs
- Typer CLI: `remember`, `recall`, `forget`, `consolidate`, `doctor`
- Docker + docker-compose support
- Structured logging via `structlog`
- In-process metrics + `/metrics` endpoint
- GitHub Actions CI/CD
- Published on PyPI as `eviloomemvault`