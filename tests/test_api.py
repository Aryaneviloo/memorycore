import pytest
from fastapi.testclient import TestClient

from memvault.api.app import create_app
from memvault.api.dependencies import get_storage
from memvault.embeddings.local import LocalEmbedder
from memvault.storage.base import EmbeddingStorageWrapper
from memvault.storage.memory import InMemoryStorage


@pytest.fixture(scope="module")
def client():
    """
    Test client using in-memory storage — no real DB, no real files.
    Overrides the get_storage dependency so tests are isolated.
    """
    embedder = LocalEmbedder()
    backend = InMemoryStorage()
    test_store = EmbeddingStorageWrapper(backend=backend, embedder=embedder)

    app = create_app()
    app.dependency_overrides[get_storage] = lambda: test_store

    return TestClient(app)


@pytest.fixture
def created_memory(client):
    """Create a memory and return the response JSON."""
    response = client.post(
        "/memories",
        json={
            "agent_id": "agent-1",
            "user_id": "user-1",
            "content": "User prefers Python over JavaScript",
            "type": "semantic",
            "importance": 0.8,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_memory_returns_201(client):
    response = client.post(
        "/memories",
        json={
            "agent_id": "agent-1",
            "user_id": "user-1",
            "content": "User likes clean code",
            "type": "episodic",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["content"] == "User likes clean code"
    assert data["importance"] == 0.5


def test_create_memory_validates_importance(client):
    response = client.post(
        "/memories",
        json={
            "agent_id": "a",
            "user_id": "u",
            "content": "test",
            "importance": 5.0,  # out of range
        },
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_get_memory_returns_correct_item(client, created_memory):
    memory_id = created_memory["id"]
    response = client.get(f"/memories/{memory_id}")
    assert response.status_code == 200
    assert response.json()["id"] == memory_id


def test_get_memory_returns_404_for_unknown(client):
    response = client.get("/memories/does-not-exist")
    assert response.status_code == 404


def test_update_memory_changes_content(client, created_memory):
    memory_id = created_memory["id"]
    response = client.patch(
        f"/memories/{memory_id}",
        json={
            "content": "User prefers Python AND Rust",
        },
    )
    assert response.status_code == 200
    assert response.json()["content"] == "User prefers Python AND Rust"


def test_update_memory_partial_only_changes_given_fields(client, created_memory):
    memory_id = created_memory["id"]
    original_importance = created_memory["importance"]

    response = client.patch(
        f"/memories/{memory_id}",
        json={
            "tags": ["language", "preference"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tags"] == ["language", "preference"]
    assert data["importance"] == original_importance


def test_delete_memory_returns_204(client, created_memory):
    memory_id = created_memory["id"]
    response = client.delete(f"/memories/{memory_id}")
    assert response.status_code == 204


def test_delete_memory_makes_it_unfetchable(client, created_memory):
    memory_id = created_memory["id"]
    client.delete(f"/memories/{memory_id}")
    response = client.get(f"/memories/{memory_id}")
    assert response.status_code == 404


def test_delete_nonexistent_returns_404(client):
    response = client.delete("/memories/does-not-exist")
    assert response.status_code == 404


def test_search_returns_semantic_results(client):
    client.post(
        "/memories",
        json={
            "agent_id": "agent-1",
            "user_id": "user-search",
            "content": "User enjoys writing Python code",
        },
    )

    response = client.post(
        "/memories/search",
        json={
            "text": "programming language preferences",
            "user_id": "user-search",
        },
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert "similarity" in results[0]
    assert "final_score" in results[0]
    assert "memory" in results[0]


def test_search_respects_user_isolation(client):
    client.post(
        "/memories",
        json={
            "agent_id": "agent-1",
            "user_id": "user-isolated",
            "content": "Private memory for isolated user",
        },
    )

    response = client.post(
        "/memories/search",
        json={
            "text": "private memory",
            "user_id": "different-user",
        },
    )
    assert response.status_code == 200
    assert response.json() == []


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
