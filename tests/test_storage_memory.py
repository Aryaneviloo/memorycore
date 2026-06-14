import pytest

from memorycore.core.models import MemoryItem, MemoryQuery, MemoryType
from memorycore.storage.memory import InMemoryStorage


@pytest.fixture
def store():
    """Fresh, empty store for each test."""
    return InMemoryStorage()


@pytest.fixture
def sample_item():
    return MemoryItem(
        agent_id="agent-1",
        user_id="user-1",
        type=MemoryType.EPISODIC,
        content="User likes Python",
    )


def test_insert_and_get(store, sample_item):
    store.insert(sample_item)
    fetched = store.get(sample_item.id)
    assert fetched is not None
    assert fetched.id == sample_item.id
    assert fetched.content == "User likes Python"


def test_get_nonexistent_returns_none(store):
    assert store.get("does-not-exist") is None


def test_update_changes_content_and_timestamp(store, sample_item):
    store.insert(sample_item)
    original_updated_at = sample_item.updated_at

    sample_item.content = "User REALLY likes Python"
    updated = store.update(sample_item)

    assert updated.content == "User REALLY likes Python"
    assert updated.updated_at > original_updated_at


def test_soft_delete_hides_item_from_get(store, sample_item):
    store.insert(sample_item)
    deleted = store.delete(sample_item.id)

    assert deleted is True
    assert store.get(sample_item.id) is None


def test_hard_delete_removes_item_completely(store, sample_item):
    store.insert(sample_item)
    store.delete(sample_item.id, hard=True)
    assert sample_item.id not in store._items


def test_delete_nonexistent_returns_false(store):
    assert store.delete("does-not-exist") is False


def test_search_matches_content_substring(store, sample_item):
    store.insert(sample_item)

    results = store.search(MemoryQuery(text="python", user_id="user-1"))
    assert len(results) == 1
    assert results[0].id == sample_item.id


def test_search_respects_user_isolation(store, sample_item):
    store.insert(sample_item)
    results = store.search(MemoryQuery(text="python", user_id="someone-else"))
    assert results == []


def test_search_excludes_soft_deleted(store, sample_item):
    store.insert(sample_item)
    store.delete(sample_item.id)

    results = store.search(MemoryQuery(text="python", user_id="user-1"))
    assert results == []


def test_list_recent_orders_by_creation_time(store):
    older = MemoryItem(agent_id="a", user_id="u", type=MemoryType.EPISODIC, content="first")
    newer = MemoryItem(agent_id="a", user_id="u", type=MemoryType.EPISODIC, content="second")

    store.insert(older)
    store.insert(newer)

    results = store.list_recent(user_id="u")
    assert results[0].id == newer.id
    assert results[1].id == older.id


def test_list_recent_respects_limit(store):
    for i in range(5):
        store.insert(
            MemoryItem(agent_id="a", user_id="u", type=MemoryType.EPISODIC, content=f"memory {i}")
        )

    results = store.list_recent(user_id="u", limit=3)
    assert len(results) == 3