# MemVault Roadmap

This is the public roadmap for MemVault. Items are roughly ordered by
priority, but the order can shift based on community interest and contributions.

## v0.3.0 — Intelligence

- [ ] **SemanticExtractor** — use BGE-small to extract facts by meaning,
      not pattern matching. Zero extra dependencies since BGE is already loaded.
- [ ] **OpenAI embedding provider** — `OpenAIEmbedder(api_key=...)`
- [ ] **Cohere embedding provider** — `CohereEmbedder(api_key=...)`
- [ ] **Ollama embedding provider** — local LLMs, fully offline
- [ ] **Contradiction detection** — flag when new memory conflicts with existing one

## v0.4.0 — Scale

- [ ] **Async storage backends** — `AsyncSQLiteStorage`, `AsyncPostgresStorage`
      using `aiosqlite` and `asyncpg`. Critical for production FastAPI usage.
- [ ] **pgvector adapter** — native vector search inside PostgreSQL,
      replaces Python-side cosine similarity at scale
- [ ] **Qdrant adapter** — vector database backend
- [ ] **Chroma adapter** — local vector database backend
- [ ] **Batch APIs** — `remember_many()`, `delete_many()`, `search_many()`

## v0.5.0 — Integrations

- [ ] **LangChain integration** — `MemVaultRetriever`, `MemVaultMemory`
- [ ] **LlamaIndex integration** — `MemVaultQueryEngine`
- [ ] **TypeScript SDK** — thin HTTP wrapper around the REST API
- [ ] **OpenAI ingestion extractor** — `OpenAIExtractor(api_key=...)`

## v1.0.0 — Production

- [ ] **Async-first facade** — `await mc.remember(...)`, `await mc.recall(...)`
- [ ] **Temporal memory** — keep history instead of overwriting,
      track how preferences change over time
- [ ] **Reflection engine** — nightly autonomous maintenance
      (summarize, decay, strengthen, forget)
- [ ] **Web dashboard** — visualize memories, decay graphs, namespaces
- [ ] **Cross-agent shared memory** — multiple agents reading/writing
      the same memory pool with proper isolation

## Ideas under consideration

- Memory graphs — connect memories into a knowledge graph
- Episodic replay — replay a conversation session from stored memories
- Multi-tenant SaaS mode — built-in auth, billing hooks, tenant isolation
- gRPC interface alongside REST

---

**Want to work on something here?** Open an issue and mention which item
you'd like to tackle. We'll discuss approach and assign it to you.

**Have an idea not listed?** Open a
[GitHub Discussion](https://github.com/Aryaneviloo/memvault/discussions).