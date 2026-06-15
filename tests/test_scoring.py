from datetime import datetime, timedelta, timezone

from memorycore.core.models import MemoryItem, MemoryType
from memorycore.core.scoring import (ScoringWeights, frequency_score, importance_score, recency_score, relevance_score, )



NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def make_item(**overrides) -> MemoryItem:
    defaults = dict(agent_id="a", user_id="u", type = MemoryType.EPISODIC, content ="x")
    defaults.update(overrides)
    return MemoryItem(**defaults)


#--------RECENCY SCORE----------
def test_recency_score_fresh_memory_is_near_one():
    item = make_item(created_at = NOW)
    assert recency_score(item, now=NOW) == 1.0


def test_recency_score_at_half_life_is_half():
    item = make_item(created_at=NOW - timedelta(days=7))
    score = recency_score(item, half_life_days=7.0, now=NOW)
    assert abs(score - 0.5) < 0.001

def test_recency_score_decreases_with_age():
    fresh = make_item(created_at = NOW)
    old = make_item(created_at=NOW - timedelta(days=30))
    assert recency_score(fresh, now=NOW) > recency_score(old, now=NOW)

def test_recency_score_uses_last_accessed():
    item = make_item(created_at=NOW - timedelta(days=30), last_accessed_at=NOW,)
    assert recency_score(item, now=NOW) == 1.0
    #was created long ago but was accessed recently so score should be fresh


#-------IMPORTANCE SCORE-------------
def test_importance_score_weighted_by_confidence():
    confident = make_item(importance=0.9, confidence=1.0)
    unsure = make_item(importance = 0.9, confidence=0.3)

    assert importance_score(confident) == 0.9
    assert abs(importance_score(unsure) - 0.27) < 0.001
    assert importance_score(confident) > importance_score(unsure)


def test_frequency_score_accesses_is_zero():
    item = make_item(access_count=0)
    assert frequency_score(item) == 0.0

def test_frequency_score_increases_with_access():
    rarely = make_item(access_count = 1)
    often = make_item(access_count = 10)

    assert frequency_score(often) > frequency_score(rarely)
    assert frequency_score(often) < 1.0


#------------RELEVANCE--------------

def test_relevance_score_combines_signals():
    fresh_important = make_item(created_at=NOW, importance=0.9, confidence=1.0, access_count=20)
    old_unimportant = make_item(
        created_at=NOW - timedelta(days=60), importance=0.1, confidence=0.5, access_count=0
    )

    assert relevance_score(fresh_important, now=NOW) > relevance_score(old_unimportant, now=NOW)
                      

def test_relevance_score_custom_weights():
    item = make_item(created_at=NOW - timedelta(days=100), importance=1.0, confidence=1.0, access_count=0)

    # heavily weight importance -> old but important memory should score high
    importance_heavy = ScoringWeights(recency=0.0, importance=1.0, frequency=0.0)
    score = relevance_score(item, weights=importance_heavy, now=NOW)

    assert abs(score - 1.0) < 0.001