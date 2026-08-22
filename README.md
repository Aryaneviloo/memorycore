<div align="center">

<h1>MemVault</h1>

<p><strong>Production-grade memory infrastructure for AI agents.</strong></p>

<p>
  <a href="https://github.com/Aryaneviloo/memvault/actions/workflows/ci.yml">
    <img src="https://github.com/Aryaneviloo/memvault/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://pypi.org/project/eviloomemvault/">
    <img src="https://img.shields.io/pypi/v/eviloomemvault?color=blue" alt="PyPI">
  </a>
  <a href="https://pypi.org/project/eviloomemvault/">
    <img src="https://img.shields.io/pypi/pyversions/eviloomemvault" alt="Python">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License">
  </a>
</p>

<p>
  <a href="#quick-start">Quick Start</a> ·
  <a href="#installation">Installation</a> ·
  <a href="docs/architecture.md">Architecture</a> ·
  <a href="docs/contributing.md">Contributing</a>
</p>

</div>

---

Most AI applications are stateless. They forget users between sessions, lose context mid-conversation, and treat every interaction as if it never happened before.

**MemVault is the memory layer that fixes this.** Plug it into any AI agent or MCP-compatible client and give it persistent, semantically-searchable memory — backed by SQLite or PostgreSQL, ranked by recency, importance, and frequency, and smart enough to consolidate duplicates automatically.

```python
from memvault import MemVault

mc = MemVault()
mc.remember("User prefers Python over JavaScript", user_id="alice")

results = mc.recall("programming language preferences", user_id="alice")
# → [0.823] User prefers Python over JavaScript
```

## Features

- **Semantic retrieval** — finds memories by meaning, not keyword matching
- **Hybrid ranking** — combines embedding similarity with recency, importance, and access frequency
- **Auto-ingestion** — extract and store memorable facts from raw conversations automatically
- **MCP server** — plug into Claude Desktop, Cursor, or any MCP-compatible client with one config block
- **Multiple backends** — SQLite (zero setup), PostgreSQL (production), in-memory (tests)
- **Consolidation** — detects near-duplicate memories and merges them
- **Decay & reinforcement** — unaccessed memories fade; accessed ones strengthen
- **REST API + CLI** — use as a standalone service or a library
- **Provider-agnostic** — bring your own embedder, extractor, or storage backend

## Quick Start

### Library

```bash
pip install "eviloomemvault[local]"
```

```python
from memvault import MemVault, MemoryType

mc = MemVault()

# Store a memory
mc.remember(
    "User prefers dark mode and concise answers",
    user_id="alice",
    memory_type=MemoryType.SEMANTIC,
    importance=0.8,
)

# Retrieve by meaning
results = mc.recall("display preferences", user_id="alice")
for r in results:
    print(f"[{r.final_score:.3f}] {r.item.content}")

# Auto-ingest from a conversation
mc.ingest(
    messages=[
        {"role": "user", "content": "I've been using Rust for systems work lately."},
        {"role": "user", "content": "Python is still my go-to for AI projects."},
    ],
    user_id="alice",
)
```

### MCP Server (Claude Desktop / Cursor)

Add to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "memvault": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "memvault.mcp_server.server"],
      "env": {
        "MEMVAULT_DB": "/path/to/memvault.db",
        "HF_HUB_OFFLINE": "1",
        "PYTHONPATH": "/path/to/memvault/src"
      }
    }
  }
}
```

Restart Claude Desktop. It now has 6 memory tools and will remember things across conversations using your local database.

### REST API

```bash
# Docker (recommended)
docker compose -f docker/docker-compose.yml up

# Direct
uvicorn memvault.api.app:app --reload --port 8000
```

```bash
curl -X POST http://localhost:8000/memories \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "a1", "user_id": "alice", "content": "User prefers Python", "type": "semantic"}'

curl -X POST http://localhost:8000/memories/search \
  -H "Content-Type: application/json" \
  -d '{"text": "programming preferences", "user_id": "alice"}'
```

Interactive docs at `http://localhost:8000/docs`.

### CLI

```bash
memvault remember "User prefers dark mode" --user alice
memvault recall "display preferences" --user alice
memvault consolidate --user alice
memvault doctor
```

## Installation

```bash
# Core (REST API + CLI, no local embeddings)
pip install eviloomemvault

# With local BGE embeddings (recommended)
pip install "eviloomemvault[local]"
```

**Requirements:** Python 3.10+

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Your Application                     │
└──────────────────────────┬──────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │     MemVault Facade     │
              │  remember · recall      │
              │  ingest · consolidate   │
              └────────────┬────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼───────┐  ┌───────▼───────┐  ┌──────▼────────┐
│  Intelligence │  │    Storage    │  │  Embeddings   │
│  retrieval    │  │  SQLite       │  │  BGE-small    │
│  scoring      │  │  PostgreSQL   │  │  (pluggable)  │
│  decay        │  │  In-Memory    │  └───────────────┘
│  ingestion    │  │  (pluggable)  │
└───────────────┘  └───────────────┘

Service interfaces: REST API · CLI · MCP Server · Python SDK
```

## Memory Types

| Type | When to use | Example |
|------|-------------|---------|
| `semantic` | Stable facts and preferences | "User prefers Python over Java" |
| `episodic` | Events at a point in time | "User completed onboarding on Jan 5" |
| `procedural` | Repeatable workflows | "Always run tests before committing" |
| `working` | Short-term session context | "Currently debugging the auth module" |
| `consolidated` | Auto-generated summaries | Created by `mc.consolidate()` |

## Storage Backends

| Backend | Use case | Setup |
|---------|----------|-------|
| `SQLiteStorage` | Local dev, single-process production | Zero setup |
| `PostgresStorage` | Production, multi-process | Postgres instance |
| `InMemoryStorage` | Tests, experimentation | Zero setup |

Backends share a common interface — swap with one line:

```python
from memvault import MemVault
from memvault.storage.postgres import PostgresStorage

mc = MemVault(storage=PostgresStorage("postgresql://user:pass@host/db"))
```

## Ingestion

Extract memorable facts from conversations automatically:

```python
# Rule-based (zero dependencies, works offline)
mc.ingest(messages, user_id="alice")

# LLM-powered (higher quality, requires API key)
from memvault.ingestion.anthropic_extractor import AnthropicExtractor
mc.ingest(messages, user_id="alice", extractor=AnthropicExtractor())
```

## Retrieval Scoring

```
final_score = (similarity_weight × cosine_similarity)
            + (relevance_weight  × relevance_score)

relevance_score = 0.4 × recency
                + 0.4 × importance
                + 0.2 × frequency
```

All weights are configurable via `RetrievalConfig` and `ScoringWeights`.

## Project Structure

```
src/memvault/
├── core/               # Models, scoring, retrieval, consolidation
├── storage/            # SQLite, PostgreSQL, in-memory backends
├── embeddings/         # BGE-small and pluggable embedding providers
├── ingestion/          # Rule-based and LLM-powered fact extraction
├── api/                # FastAPI REST service
├── cli/                # Typer CLI
├── mcp_server/         # MCP server for Claude Desktop / Cursor
└── observability/      # Structured logging and metrics
```

## Roadmap

- [x] Core memory engine (scoring, retrieval, consolidation, decay)
- [x] SQLite and PostgreSQL backends
- [x] BGE-small local embeddings
- [x] REST API (FastAPI)
- [x] CLI (Typer)
- [x] Docker support
- [x] MCP server (Claude Desktop, Cursor, VS Code)
- [x] Auto-ingestion (rule-based + Anthropic extractor)
- [x] Published on PyPI
- [ ] Async storage backends
- [ ] OpenAI / Cohere embedding providers
- [ ] Semantic ingestion extractor
- [ ] pgvector support
- [ ] LangChain / LlamaIndex integration
- [ ] TypeScript SDK
- [ ] Web dashboard

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](docs/contributing.md) first.

```bash
git clone https://github.com/Aryaneviloo/memvault.git
cd memvault
pip install -e ".[local,dev]"
pytest
```

## License

Apache 2.0 — see [LICENSE](LICENSE).