# Contributing to MemVault

Thank you for your interest in contributing. MemVault is an open-source project
and all contributions are welcome — bug reports, documentation improvements,
new features, and performance work.

## Getting started

```bash
git clone https://github.com/Aryaneviloo/memvault.git
cd memvault
python -m venv venv
source venv/bin/activate
pip install -e ".[local,dev]"
```

## Running tests

```bash
# Core suite
pytest

# Verbose with short tracebacks
pytest -v --tb=short

# With PostgreSQL backend
docker compose -f docker/docker-compose.yml up postgres -d
TEST_POSTGRES_DSN="postgresql://memvault:memvault@localhost:5433/memvault" pytest
```

## Code style

```bash
ruff check .        # lint
ruff format .       # format
```

All PRs must pass `ruff check` and the full test suite before merging.

## What we're looking for

Good first issues are labeled [`good first issue`](https://github.com/Aryaneviloo/memvault/labels/good%20first%20issue).

High-impact areas:
- **New embedding providers** — OpenAI, Cohere, Voyage, Ollama
- **New storage adapters** — pgvector, Qdrant, Chroma
- **Async backends** — asyncpg, aiosqlite
- **LangChain / LlamaIndex integration**
- **Benchmarks and performance work**

## Adding a storage backend

1. Create `src/memvault/storage/<name>.py`
2. Implement all six methods from `StorageBackend` (ABC in `base.py`)
3. Add `"<name>"` to the fixture params in `tests/test_storage_contract.py`
4. The 16 contract tests run automatically against your backend

## Adding an embedding provider

1. Create `src/memvault/embeddings/<name>.py`
2. Implement `embed()`, `embed_query()`, and `dimensions` from `BaseEmbedder`
3. Register in `provider.py`

## Adding an ingestion extractor

1. Create `src/memvault/ingestion/<name>.py`
2. Implement `extract(messages) -> list[ExtractedFact]` from `BaseExtractor`

## Pull request process

- Open an issue before starting significant work
- Keep PRs focused — one feature or fix per PR
- Write tests for new functionality
- Update docs if you change a public interface
- All CI checks must pass

## Commit style

Use short, imperative commit messages:
```
Add OpenAI embedding provider
Fix soft-delete bug in PostgresStorage
Update retrieval scoring weights
```

## Questions

Open a [GitHub Discussion](https://github.com/Aryaneviloo/memvault/discussions)
or comment on the relevant issue.