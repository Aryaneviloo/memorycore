from datetime import datetime, timedelta, timezone

from memorycore.core.models import MemoryItem, MemoryType
from memorycore.core.scoring import apply_decay, reinforce


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_item(**overrides) -> MemoryItem:
    defaults = dict(agent_id="a", user_id="u", type=MemoryType.EPISODIC, content="x")
    defaults.update(overrides)
    return MemoryItem(**defaults)


def test_decay_reduces_importance_over_time():
    item = make_item(importance=0.5, created_at=NOW - timedelta(days=30))
    original = item.importance

    apply_decay(item, now=NOW)

    assert item.importance < original


def test_decay_no_time_elapsed_does_nothing():
    item = make_item(importance=0.5, created_at=NOW)
    apply_decay(item, now=NOW)
    assert abs(item.importance - 0.5) < 1e-9


def test_decay_high_importance_decays_slower_than_low_importance():
    high = make_item(importance=0.9, created_at=NOW - timedelta(days=30))
    low = make_item(importance=0.9, created_at=NOW - timedelta(days=30))
    # give 'low' a much lower importance to compare relative shrinkage
    low.importance = 0.1

    apply_decay(high, now=NOW)
    apply_decay(low, now=NOW)

    high_retention = high.importance / 0.9
    low_retention = low.importance / 0.1

    assert high_retention > low_retention


def test_decay_never_goes_negative():
    item = make_item(importance=0.01, created_at=NOW - timedelta(days=10000))
    apply_decay(item, now=NOW, decay_rate_per_day=0.5)
    assert item.importance >= 0.0


def test_reinforce_increments_access_count():
    item = make_item(access_count=0)
    reinforce(item, now=NOW)
    assert item.access_count == 1

    reinforce(item, now=NOW)
    assert item.access_count == 2


def test_reinforce_updates_last_accessed_at():
    item = make_item(last_accessed_at=None)
    reinforce(item, now=NOW)
    assert item.last_accessed_at == NOW


def test_reinforce_increases_importance():
    item = make_item(importance=0.5)
    reinforce(item, now=NOW)
    assert item.importance > 0.5


def test_reinforce_has_diminishing_returns_near_max():
    near_max = make_item(importance=0.99)
    low = make_item(importance=0.1)

    near_max_before = near_max.importance
    low_before = low.importance

    reinforce(near_max, now=NOW, importance_boost=0.1)
    reinforce(low, now=NOW, importance_boost=0.1)

    near_max_gain = near_max.importance - near_max_before
    low_gain = low.importance - low_before

    assert low_gain > near_max_gain


def test_reinforce_never_exceeds_one():
    item = make_item(importance=0.999)
    for _ in range(100):
        reinforce(item, now=NOW, importance_boost=0.5)
    assert item.importance <= 1.0