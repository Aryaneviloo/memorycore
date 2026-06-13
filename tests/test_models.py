import pytest
from pydantic import ValidationError

from memorycore.core.models import MemoryItem, MemoryNamespace, MemoryQuery, MemoryType


def test_memory_item_minimal_creation():
    """A MemoryItem can be created with only the required fields."""
    m = MemoryItem(
        agent_id="agent-1",
        user_id="user-1",
        type=MemoryType.EPISODIC,
        content="User prefers concise answers",
    )
    assert m.namespace == "default"
    assert m.importance == 0.5
    assert m.access_count == 0
    assert m.tags == []
    assert m.id  


def test_memory_item_unique_ids():
    """Each MemoryItem gets its own unique id."""
    m1 = MemoryItem(agent_id="a", user_id="u", type=MemoryType.EPISODIC, content="x")
    m2 = MemoryItem(agent_id="a", user_id="u", type=MemoryType.EPISODIC, content="y")
    assert m1.id != m2.id


def test_memory_item_rejects_invalid_type():
    """An invalid memory type should raise a validation error."""
    with pytest.raises(ValidationError):
        MemoryItem(agent_id="a", user_id="u", type="not_a_real_type", content="x")


def test_memory_item_rejects_out_of_range_importance():
    """Importance must be between 0 and 1."""
    with pytest.raises(ValidationError):
        MemoryItem(agent_id="a", user_id="u", type=MemoryType.EPISODIC, content="x", importance=1.5)


def test_memory_item_tags_are_independent():
    """Mutable defaults must not be shared between instances."""
    m1 = MemoryItem(agent_id="a", user_id="u", type=MemoryType.EPISODIC, content="x")
    m2 = MemoryItem(agent_id="a", user_id="u", type=MemoryType.EPISODIC, content="y")
    m1.tags.append("important")
    assert m2.tags == []


def test_memory_namespace_defaults():
    ns = MemoryNamespace(user_id="user-1")
    assert ns.namespace == "default"
    assert ns.agent_id is None


def test_memory_query_defaults():
    q = MemoryQuery(text="what does the user like?", user_id="user-1")
    assert q.top_k == 5
    assert q.types is None
    assert q.recency_bias == 0.0


def test_memory_query_top_k_bounds():
    with pytest.raises(ValidationError):
        MemoryQuery(text="x", user_id="u", top_k=0)
    with pytest.raises(ValidationError):
        MemoryQuery(text="x", user_id="u", top_k=101)