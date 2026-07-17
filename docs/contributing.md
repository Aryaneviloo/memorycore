# Contributing to MemoryCore

## Setup

```bash
git clone https://github.com/Aryaneviloo/memorycore.git
cd memorycore
python -m venv venv
source venv/bin/activate
pip install -e ".[local,dev]"
```

## Running tests

```bash
pytest                    # core suite
pytest -v --tb=short      # verbose
```

With PostgreSQL:
```bash
docker compose -f docker/docker-compose.yml up postgres -d
TEST_POSTGRES_DSN="postgresql://memorycore:memorycore@localhost:5433/memorycore" pytest
```

## Code style

```bash
ruff check .        # lint
ruff format .       # format
```

## Pull request guidelines

- Tests required for new features
- Contract tests must pass on all backends
- Keep commits small and descriptive
- Update docs if you change public interfaces

## Adding a new storage backend

1. Create `src/memorycore/storage/<name>.py`
2. Implement all six methods from `StorageBackend`
3. Add `"<name>"` to the fixture in `test_storage_contract.py`
4. All 16 contract tests run automatically

## Adding a new embedding provider

1. Create `src/memorycore/embeddings/<name>.py`
2. Implement `embed()`, `embed_query()`, `dimensions`
3. Register in `provider.py`