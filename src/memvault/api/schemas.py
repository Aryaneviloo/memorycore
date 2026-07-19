from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from memvault.core.models import MemoryType


class CreateMemoryRequest(BaseModel):
    """What the API caller sends when creating a memory."""

    agent_id: str
    user_id: str
    namespace: str = "default"
    type: MemoryType = MemoryType.EPISODIC
    content: str
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: str | None = None


class UpdateMemoryRequest(BaseModel):
    """What the API caller sends when updating a memory."""

    content: str | None = None
    importance: float | None = Field(default=None, ge=0.0, le=1.0)
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class SearchRequest(BaseModel):
    """What the API caller sends when searching memories."""

    text: str
    user_id: str
    agent_id: str | None = None
    namespace: str = "default"
    types: list[MemoryType] | None = None
    top_k: int = Field(default=5, ge=1, le=100)
    recency_bias: float = Field(default=0.0, ge=0.0, le=1.0)


class MemoryResponse(BaseModel):
    """What the API returns when showing a memory."""

    id: str
    agent_id: str
    user_id: str
    namespace: str
    type: MemoryType
    content: str
    summary: str | None
    tags: list[str]
    metadata: dict[str, Any]
    source: str | None
    importance: float
    confidence: float
    access_count: int
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime | None
    expires_at: datetime | None

    model_config = {"from_attributes": True}


class SearchResultResponse(BaseModel):
    """A memory with its retrieval scores attached."""

    memory: MemoryResponse
    similarity: float
    relevance: float
    final_score: float


class ConsolidateRequest(BaseModel):
    """Request to run consolidation for a user's memories."""

    user_id: str
    agent_id: str | None = None
    namespace: str = "default"
    similarity_threshold: float = Field(default=0.85, ge=0.0, le=1.0)


class ConsolidationResponse(BaseModel):
    """Result of a consolidation run."""

    clusters_found: int
    memories_consolidated: int
    consolidated_ids: list[str]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
