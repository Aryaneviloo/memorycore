import pytest

from memorycore.core.models import MemoryType, MemoryQuery, MemoryItem
from memorycore.storage.memory import InMemoryStorage
from memorycore.storage.sqlite import SQLiteStorage


@pytest.fixture(params=["memory", "sqlite"])
def store(request):
    """RUN every test on both the bakends"""

    if request.param == "memory":
        return InMemoryStorage()
    return SQLiteStorage(":memory:")

@pytest.fixture
def sample_item():
    return MemoryItem(
        agent_id="agent-1",
        user_id="user-1",
        type=MemoryType.EPISODIC,
        content = "User likes to code",
        tags=["preference", "language"],
        metadata={"source": "chat"},

    )

def test_insert_and_get(store, sample_item):
    store.insert(sample_item)
    fetched = store.get(sample_item.id)
    assert fetched is not None
    assert fetched.id == sample_item.id
    assert fetched.content == "User likes to code"
    assert fetched.tags == ["preference", "language"]
    assert fetched.metadata == {"source": "chat"}
    assert fetched.type == MemoryType.EPISODIC

def test_get_nonexistent_returns_none(store):
    assert store.get("does-not-exist") is None


def test_update_changes_content_and_timestamp(store, sample_item):
    store.insert(sample_item)
    original_updated_at = sample_item.updated_at
    sample_item.content = "User hates to code"
    updated = store.update(sample_item)

    assert updated.content == "User hates to code"
    assert updated.updated_at > original_updated_at

    refetched = store.get(sample_item.id)
    assert refetched.content == "User hates to code"


def test_soft_delete_hides_item_from_get(store, sample_item):
    store.insert(sample_item)
    deleted = store.delete(sample_item.id)

    assert deleted is True
    assert store.get(sample_item.id) is None



def test_delete_nonexistent_returns_false(store):
    assert store.delete("does-not-exist") is False


def test_search_matches_content_substring(store, sample_item):
    store.insert(sample_item)
    results = store.search(MemoryQuery(text = "code", user_id="user-1"))
    assert len(results) == 1
    assert results[0].id == sample_item.id


def test_search_respects_user_isolation(store, sample_item):
    store.insert(sample_item)
    results = store.search(MemoryQuery(text="code", user_id="someone_else"))
    assert results == []

def test_search_excludes_soft_deleted(store, sample_item):
    store.insert(sample_item)
    store.delete(sample_item.id)

    results = store.search(MemoryQuery(text="code", user_id="user-1"))
    assert results == []


def test_search_filters_by_type(store, sample_item):
    store.insert(sample_item)
    other = MemoryItem(
        agent_id="agent-1", user_id="user-1", type=MemoryType.SEMANTIC, content="User likes Python too"
    )
    store.insert(other)

    results = store.search(
        MemoryQuery(text="python", user_id="user-1", types=[MemoryType.SEMANTIC])
    )
    assert len(results) == 1
    assert results[0].id == other.id


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

def test_search_filters_by_agent_id(store):
    store.insert(
        MemoryItem(agent_id="agent-A", user_id="u", type=MemoryType.EPISODIC, content="shared topic")
    )
    store.insert(
        MemoryItem(agent_id="agent-B", user_id="u", type=MemoryType.EPISODIC, content="shared topic")
    )

    results = store.search(MemoryQuery(text="shared", user_id="u", agent_id="agent-A"))
    assert len(results) == 1
    assert results[0].agent_id == "agent-A"


def test_list_recent_filters_by_agent_id(store):
    store.insert(MemoryItem(agent_id="agent-A", user_id="u", type=MemoryType.EPISODIC, content="x"))
    store.insert(MemoryItem(agent_id="agent-B", user_id="u", type=MemoryType.EPISODIC, content="y"))

    results = store.list_recent(user_id="u", agent_id="agent-A")
    assert len(results) == 1
    assert results[0].agent_id == "agent-A"


def test_hard_delete_permanently_removes_item(store, sample_item):
    store.insert(sample_item)
    deleted = store.delete(sample_item.id, hard=True)

    assert deleted is True
    assert store.get(sample_item.id) is None