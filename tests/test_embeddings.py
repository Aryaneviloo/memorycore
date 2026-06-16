import pytest
from memorycore.embeddings.base import BaseEmbedder
from memorycore.embeddings.local import LocalEmbedder
from memorycore.embeddings.provider import get_embedder


@pytest.fixture(scope="module")
def embedder():
    """
    Module scoped: model loads once for all the tests saving time
    
    """

    return LocalEmbedder()


def dot(a: list[float], b: list[float]) -> float:
    return sum(x*y for x, y in zip(a,b))


def test_embed_returns_correct_d(embedder):
    vector = embedder.embed("Hello World")

    assert len(vector) == 384
    assert len(vector) == embedder.dimensions


def test_embed_returns_list_of_floats(embedder):
    vector = embedder.embed("hello world")

    assert isinstance (vector, list)
    assert all(isinstance(v, float) for v in vector)


def test_embed_is_normalized(embedder):
    vector = embedder.embed("hello world")
    magnitude = sum( v ** 2 for v in vector) ** 0.5

    assert abs(magnitude - 1.0) < 1e-5


def test_similar_texts_have_high_similarity(embedder):
    v1 = embedder.embed("user loves to code in python")
    v2 = embedder.embed("programming language preference")

    assert dot(v1, v2) > 0.7


def unrelated_texts_have_lower_similarity(embedder):
    v1 = embedder.embed("User likes python")
    v2 = embedder.embed("he likes burmese python")

    assert dot(v1, v2) < 0.7


def test_query_and_content_embed_differently(embedder):
    text = "User hates snakes"

    assert embedder.embed(text) != embedder.embed_query(text)


def test_get_embedder_factory_retuns_local():
    a = get_embedder("local")

    assert isinstance(a, LocalEmbedder)
    assert isinstance(a, BaseEmbedder)


def test_get_embedder_factory_raises_on_unknown():
    with pytest.raises(ValueError, match = "Unknown embedding provider"):
        get_embedder("unknown")

