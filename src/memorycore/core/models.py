from enum import Enum
from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional, Any

from pydantic import BaseModel, Field

class MemoryType(str, Enum):
    """"The category a memory belongs to."""
    
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"
    CONSOLIDATED = "consolidated"

def utc_now() -> datetime:
    """Return the current UTC time. Centralized so it's easy to mock in the tests """
    return datetime.now(timezone.utc)

class MemoryItem(BaseModel):
    """A single memory unit of memory stored in the system"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    user_id: str
    namespace: str = "default"
    type: MemoryType
    content: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    last_accessed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    access_count: int = Field(default=0, ge=0)
    summary: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: Optional[str] = None
    embedding: Optional[list[float]] = None


class MemoryNamespace(BaseModel):
    """Identifies a logical, isolated pool of memories"""

    namespace: str = "default"
    user_id: str
    agent_id: Optional[str] = None
    project_id: Optional[str] = None


class MemoryQuery(BaseModel):
    """How a search query will look like"""

    text: str
    user_id: str
    agent_id: Optional[str] = None
    namespace: str = "default"
    types: Optional[list[MemoryType]] = None
    top_k: int = Field(default=5, ge=1, le=100)
    recency_bias: float = Field(default=0.0, ge=0.0, le=1.0)

    

