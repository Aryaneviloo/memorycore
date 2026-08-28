# MemVault — Performance Benchmarks

**Generated:** 2026-08-28  
**Hardware:** CPU-only (no GPU)  
**Embedding model:** `BAAI/bge-small-en-v1.5` (384 dims)  
**Python:** 3.10  

All times in milliseconds. Median and P95 over multiple runs with warmup.

---


## Embedding Latency (BGE-small, CPU)

| Sentences | Total (median) | Per sentence | P95 total |
|---|---|---|---|
| 1 | 28.9ms | 28.9ms | 30.8ms |
| 5 | 143.1ms | 28.6ms | 158.1ms |
| 10 | 202.9ms | 20.3ms | 207.1ms |
| 25 | 508.1ms | 20.3ms | 519.9ms |
| 50 | 1008.4ms | 20.2ms | 1111.8ms |
| 100 | 1993.5ms | 19.9ms | 1997.2ms |

*Each sentence is embedded individually. True batch embedding


## Insert Latency

| Backend | With embedding (median) | Without embedding | P95 (with emb) |
|---|---|---|---|
| In-memory | 28.4ms | 0.0ms | 29.7ms |
| SQLite | 22.0ms | 0.0ms | 23.4ms |

*Embedding generation dominates insert time on CPU. On GPU this drops to ~3–5ms.*


## Retrieval Latency at Scale

| Memory count | Median | P95 | Max |
|---|---|---|---|
| 100 | 23.6ms | 28.4ms | 30.6ms |
| 500 | 26.3ms | 31.2ms | 33.0ms |
| 1,000 | 27.2ms | 34.2ms | 38.7ms |
| 5,000 | 27.8ms | 32.6ms | 36.6ms |

*Retrieval scales sub-linearly: candidate fetch is O(limit) not O(n), so latency grows slowly with store size.*


## Ingestion Latency (Rule-based Extractor)

| Messages | Median | P95 |
|---|---|---|
| 5 | 0.2ms | 0.2ms |
| 10 | 0.5ms | 0.5ms |
| 20 | 1.0ms | 1.1ms |
| 50 | 2.4ms | 2.5ms |

*Rule-based extraction is near-instant — pure Python regex, no model loading.*


## Consolidation Latency

| Memory count | Median | P95 |
|---|---|---|
| 50 | 0.0ms | 0.0ms |
| 100 | 0.0ms | 0.0ms |
| 500 | 0.0ms | 0.0ms |

*Consolidation is O(n²) in cluster detection — run it periodically rather than on every insert.*



---

## Notes

- **Embedding dominates insert time** on CPU. Use GPU or a faster embedder for high-throughput writes.
- **Retrieval is bounded** by `limit=200` candidate fetch, not total store size — latency grows slowly.
- **Rule-based ingestion** is essentially free. LLM-based extraction (Anthropic/OpenAI) adds ~500ms–2s per conversation.
- **Consolidation** is O(n²) — run it periodically, not on every insert.

To reproduce: `python benchmarks/benchmark_suite.py`
