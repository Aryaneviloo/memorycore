"""
Engram - the main entry point for using this library

This facade class wires together storage, embeddings, retriveal, socirng, 
and consolidation into a single clean interface
Advanced users can still import and use diff layers directly

"""

from __future__ import annotations
from datetime import datetime 
from typing import Optional

from memorycore.core.consolidation import ConsolidationConfig, ConsolidationResult, consolidate
from memorycore.core.models import MemoryItem, MemoryQuery, MemoryType
from memorycore.core.retrieval import RetrievalConfig, RetrievalResult, relevance_score, retrieve
from memorycore.core.scoring import ScoringWeights, apply_decay, reinforce
from memorycore.embeddings.base import BaseEmbedder
from memorycore.storage.base import EmbeddingStorageWrapper, StorageBackend


class Engram:
    """
    The main interface for Engram 
    
    Wires together storage, embeddings, retrieval, scoring and consolidation into a single API
    
    Basic usage: 
    emem = Engram()
    emem.remember("user likes Python, user_id="alice)
    results = emem.recall("programming preferences", use_id="alice")
    
    Custom Backends:
    from engram.storage.postgres import PostgresStorage
    from engram.embeddings.local import LocalEmbedder
    
    emem = Engram(
        storage = PostgresStorage("postgresql://..."),
        embedder=LocalEmbedder(),
    )
"""

    def __init__(
            self,
            storage: Optional[StorageBackend] = None,
            embedder: Optional[BaseEmbedder] = None,
            db_path: str = "memories.db",
    ) -> None:
        """
        Initialize Engram.


        Args:
            storage: Any StorageBackend. Defaults to SQLiteStorage(db_path)
            embedder: Any BaseEmbedder, Defaults to LocalEmbedder()
            db_path: Path for SQLite database (used only if storage not provided)
        
        """

        if embedder is None:
            from memorycore.embeddings.local import LocalEmbedder
            embedder = LocalEmbedder()

        if storage is None:
            from memorycore.storage.sqlite import SQLiteStorage
            storage = SQLiteStorage(db_path)

        self._embedder = embedder
        self._backend = storage
        self._store = EmbeddingStorageWrapper(
            backend=self._backend,
            embedder=self._embedder,
        )

    def remember (
            self, 
            content: str,
            *,
            user_id: str,
            agent_id: str,
            namespace: str -
    )