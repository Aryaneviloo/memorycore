from functools import lru_cache


from memorycore.embeddings.local import LocalEmbedder
from memorycore.storage.sqlite import SQLiteStorage
from memorycore.storage.base import EmbeddingStorageWrapper



@lru_cache(maxsize=1)
def get_embedder() -> LocalEmbedder:
    """
    Load the embedding model once and cache it.
    lru_cache ensures this is only called once per process —
    loading the model is expensive, we don't want to do it per request.
    """
    return LocalEmbedder()



@lru_cache(maxsize=1)
def get_storage() -> EmbeddingStorageWrapper:
    """
    Create the storage backend once and cache it.
    Uses SQLite by default
    Path configurable later via env vars.
    """
    backend = SQLiteStorage("memories.db")
    embedder = get_embedder()
    return EmbeddingStorageWrapper(backend=backend, embedder=embedder)