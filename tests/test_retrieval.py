from datetime import datetime, timedelta, timezone

import pytest

from memorycore.core.models import MemoryItem, MemoryQuery, MemoryType
from memorycore.core.retrieval import RetrievalConfig, RetrievalResult, retrieve
from memorycore.embeddings.local import LocalEmbedder
from memorycore.storage.memory import InMemoryStorage
from memorycore.storage.base import EmbeddingStorageWrapper

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)

@pytest.fixture(scope="module")
def embedder():
    return LocalEmbedder()


@pytest.fixture
def store(embedder):
    backend = InMemoryStorage()
    return EmbeddingStorageWrapper(backend=backend, embedder=embedder)



def make_item(content: str, **overrides) -> MemoryItem:
    defaults = dict(
        agent_id = "agent-1",
        user_id = "user-1",
        type = MemoryType.EPISODIC,
        content = content,
        created_at = NOW,
    ) 

    defaults.update(overrides)
    return MemoryItem(**defaults)


def test_retrieve_returns_semantically_similar_results(store, embedder):
    store.insert(make_item("User enjoys writing Python code"))
    store.insert(make_item("The user had pasta for lunch"))
    store.insert(make_item("User prefers statically typed language"))

    query = MemoryQuery(text="programmming language preference", user_id="user-1")
    results = retrieve(query, store._backend, embedder, now=NOW)


    assert len(results) >0

    contents = [r.item.content for r in results]
    assert "The user had pasta for lunch" not in contents[:2]


def test_retrieve_resukts_have_scores(store, embedder):
    store.insert(make_item("User likes clean code"))

    query = MemoryQuery(text="coding style", user_id="user-1")
    results = retrieve(query, store._backend, embedder, now=NOW)

    
    assert len(results) > 0
    top = results[0]
    assert isinstance(top, RetrievalResult)
    assert 0 <= top.similarity <= 1
    assert 0 <= top.relevance <= 1
    assert top.final_score > 0


def test_retieves_top_k(store, embedder):
    for i in range(20):
        store.insert(make_item(f"User fact number {i} about swimming"))

        query = MemoryQuery(text="swimming", user_id="user-1", top_k=3)
        results = retrieve(query, store._backend, embedder, now=NOW)

        assert len(results) <= 3



def test_retrieve_filters_low_similarity(store, embedder):
    store.insert(make_item("completely unrelated xyzzy foobar content"))

    query = MemoryQuery(text="machine learning algorithms", user_id="user-1")
    config = RetrievalConfig(min_similarity=0.8)
    results = retrieve(query, store._backend, embedder, config=config, now=NOW)

    for r in results:
        assert r.similarity >= 0.8


def test_retrieve_ranks_recent_higher_when_equally_similar(embedder):
    backend = InMemoryStorage()
    store = EmbeddingStorageWrapper(backend=backend, embedder=embedder)

    old = make_item(
        "User likes Python",
        created_at=NOW - timedelta(days=60),
        importance=0.5,
    )
    recent = make_item(
        "User likes Python",
        created_at=NOW - timedelta(days=1),
        importance=0.5,
    )

    store.insert(old)
    store.insert(recent)

    query = MemoryQuery(text="Python preference", user_id="user-1", top_k=10)
    results = retrieve(query, backend, embedder, now=NOW)

    assert len(results) >= 1
    result_ids = [r.item.id for r in results]
    if len(results) >= 2:
        assert results[0].item.id == recent.id


def test_retrieve_returns_empty_for_no_matches(store, embedder):
    query = MemoryQuery(
        text="something completely irrelevant xyzzy",
        user_id="user-1",
        agent_id="nonexistent-agent",
    )
    results = retrieve(query, store._backend, embedder, now=NOW)
    assert results == []


def test_retrieve_skips_items_without_embeddings(embedder):
    backend = InMemoryStorage()

    # Insert directly into backend, bypassing the wrapper (no embedding generated)
    item = make_item("No embedding memory")
    backend.insert(item)
    assert item.embedding is None

    query = MemoryQuery(text="memory", user_id="user-1")
    results = retrieve(query, backend, embedder, now=NOW)


    assert all(r.item.embedding is not None for r in results)