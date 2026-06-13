from abc import ABC, abstractmethod
from typing import Optional

from memorycore.core.models import MemoryItem, MemoryQuery


class StorageBackend(ABC):
    """
    Abstract interface that every storage backend must implement.

    This defines *what* operations are possible on memory storage,
    without saying *how* they're implemented (SQLite, Postgres, etc.).
    """

    @abstractmethod
    def insert(self, item: MemoryItem) -> MemoryItem:
        """Store a new memory item and return it."""
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: str) -> Optional[MemoryItem]:
        """Fetch a memory item by its ID. Return None if not found."""
        raise NotImplementedError

    @abstractmethod
    def update(self, item: MemoryItem) -> MemoryItem:
        """Persist changes to an existing memory item and return it."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, item_id: str, hard: bool = False) -> bool:
        """
        Delete a memory item.

        If hard=False (default), perform a soft delete (set deleted_at).
        If hard=True, permanently remove the record.
        Return True if something was deleted, False if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def search(self, query: MemoryQuery) -> list[MemoryItem]:
        """Return memory items matching the given query, ranked by relevance."""
        raise NotImplementedError

    @abstractmethod
    def list_recent(
        self,
        user_id: str,
        agent_id: Optional[str] = None,
        namespace: str = "default",
        limit: int = 20,
    ) -> list[MemoryItem]:
        """Return the most recently created/updated memories for a scope."""
        raise NotImplementedError