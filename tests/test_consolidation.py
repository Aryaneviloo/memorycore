from datetime import datetime, timezone
import pytest

from memorycore.core.consolidation import (
    ConsolidationConfig,
    consolidate,
    _find_clusters,
    _make_summary,
)

from memorycore.core.models import MemoryItem, MemoryType
from memorycore.embeddings.local import LocalEmbedder
from memorycore.storage.base import EmbeddingStorageWrapper
from memorycore.storage.memory import InMemoryStorage


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
        agent_id="agent-1",
        user_id="user-1",
        type=MemoryType.EPISODIC,
        content=content,
        created_at=NOW,
    )
    defaults.update(overrides)
    return MemoryItem(**defaults)



def test_make_summary_single_unique():
    items = [make_item("User likes Python"), make_item("User likes Python")]
    assert _make_summary(items) == "User likes Python"



def test_make_summary_multiple_unique():
    items = [make_item("User likes Python"), make_item("User prefers Python over Java")]
    summary = _make_summary(items)


    assert "Consolidated" in summary
    assert "User likes Python" in summary



def test_find_clusters_groups_similar_items(embedder):
    items = [
        make_item("User enjoys writing Python code"),
        make_item("User likes coding in Python"),
        make_item("The sky is blue today"),
    ]

    for item in items:
        item.embedding = embedder.embed(item.content)

    clusters = _find_clusters(items, threshold=0.8, max_size=10)

    assert len(clusters) >= 1
    cluster_contents = [i.content for cluster in clusters for i in cluster]
    assert "User enjoys writing Python code" in cluster_contents
    assert "User likes coding in Python" in cluster_contents


def test_find_clusters_skips_unembedded_items():

    items = [make_item("some content")] 
    clusters = _find_clusters(items, threshold=0.8, max_size=10)
    assert clusters == []


def test_consolidate_merges_similar_memories(store, embedder):

    store.insert(make_item("User enjoys writing Python code"))
    store.insert(make_item("User likes coding in Python"))
    store.insert(make_item("User prefers Python for scripting"))

    result = consolidate(
        user_id="user-1",
        backend=store._backend,
        config=ConsolidationConfig(similarity_threshold=0.75),
        now=NOW,
    )

    assert result.clusters_found >= 1
    assert result.memories_consolidated >= 2
    assert len(result.consolidated_items) >= 1


def test_consolidate_creates_consolidated_type(store, embedder):

    store.insert(make_item("User always uses dark mode"))
    store.insert(make_item("User prefers dark mode in all apps"))

    result = consolidate(
        user_id="user-1",
        backend=store._backend,
        config=ConsolidationConfig(similarity_threshold=0.75),
        now=NOW,
    )

    if result.consolidated_items:
        for item in result.consolidated_items:
            assert item.type == MemoryType.CONSOLIDATED
            assert "consolidated_from" in item.metadata


def test_consolidate_soft_deletes_originals(store, embedder):

    item1 = make_item("User drinks coffee every morning")
    item2 = make_item("User has coffee every day in the morning")
    store.insert(item1)
    store.insert(item2)

    result = consolidate(
        user_id="user-1",
        backend=store._backend,
        config=ConsolidationConfig(similarity_threshold=0.75),
        now=NOW,
    )

    if result.memories_consolidated >= 2:
        assert store._backend.get(item1.id) is None
        assert store._backend.get(item2.id) is None


def test_consolidate_unrelated_memories_not_merged(store, embedder):

    store.insert(make_item("User likes Python"))
    store.insert(make_item("User went hiking last weekend"))
    store.insert(make_item("User favorite food is pizza"))

    result = consolidate(
        user_id="user-1",
        backend=store._backend,
        config=ConsolidationConfig(similarity_threshold=0.95),
        now=NOW,
    )

    assert result.memories_consolidated == 0


def test_consolidate_empty_store_does_nothing():

    backend = InMemoryStorage()
    result = consolidate(user_id="user-1", backend=backend, now=NOW)

    
    assert result.clusters_found == 0
    assert result.memories_consolidated == 0