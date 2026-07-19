from fastapi import APIRouter, Depends, HTTPException, status

from memvault.api.dependencies import get_embedder, get_storage
from memvault.api.schemas import (
    ConsolidateRequest,
    ConsolidationResponse,
    CreateMemoryRequest,
    HealthResponse,
    MemoryResponse,
    SearchRequest,
    SearchResultResponse,
    UpdateMemoryRequest,
)
from memvault.core.consolidation import ConsolidationConfig, consolidate
from memvault.core.models import MemoryItem, MemoryQuery
from memvault.core.retrieval import retrieve
from memvault.observability.logging import get_logger
from memvault.observability.metrics import get_metrics
from memvault.storage.base import EmbeddingStorageWrapper

logger = get_logger(__name__)

VERSION = "0.1.0"

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Check that the API is running."""
    return HealthResponse(status="ok", version=VERSION)


@router.post(
    "/memories",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_memory(
    request: CreateMemoryRequest,
    store: EmbeddingStorageWrapper = Depends(get_storage),
):
    """
    Store a new memory.
    Embedding is generated automatically before saving.
    """

    item = MemoryItem(
        agent_id=request.agent_id,
        user_id=request.user_id,
        namespace=request.namespace,
        type=request.type,
        content=request.content,
        importance=request.importance,
        tags=request.tags,
        metadata=request.metadata,
        source=request.source,
    )

    stored = store.insert(item)
    logger.info("memory_created", memory_id=stored.id, user_id=request.user_id)
    return MemoryResponse.model_validate(stored)


@router.get("/memories/{memory_id}", response_model=MemoryResponse)
def get_memory(
    memory_id: str,
    store: EmbeddingStorageWrapper = Depends(get_storage),
):
    """Fetch a single memory by ID."""

    item = store.get(memory_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id!r} not found",
        )
    return MemoryResponse.model_validate(item)


@router.patch("/memories/{memory_id}", response_model=MemoryResponse)
def update_memory(
    memory_id: str,
    request: UpdateMemoryRequest,
    store: EmbeddingStorageWrapper = Depends(get_storage),
):
    """
    Partially update a memory.
    Only provided fields are updated — others stay as-is.
    Re-embeds automatically if content changed.
    """

    item = store.get(memory_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id!r} not found",
        )

    if request.content is not None:
        item.content = request.content
    if request.importance is not None:
        item.importance = request.importance
    if request.tags is not None:
        item.tags = request.tags
    if request.metadata is not None:
        item.metadata = request.metadata

    updated = store.update(item)
    return MemoryResponse.model_validate(updated)


@router.delete("/memories/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(
    memory_id: str,
    hard: bool = False,
    store: EmbeddingStorageWrapper = Depends(get_storage),
):
    """
    Delete a memory.
    Default is soft delete (recoverable). Pass ?hard=true for permanent deletion.
    """

    deleted = store.delete(memory_id, hard=hard)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id!r} not found",
        )


@router.post("/memories/search", response_model=list[SearchResultResponse])
def search_memories(
    request: SearchRequest,
    store: EmbeddingStorageWrapper = Depends(get_storage),
    embedder=Depends(get_embedder),
):
    """
    Semantic search over memories.
    Returns results ranked by hybrid similarity + relevance score.
    """

    query = MemoryQuery(
        text=request.text,
        user_id=request.user_id,
        agent_id=request.agent_id,
        namespace=request.namespace,
        types=request.types,
        top_k=request.top_k,
        recency_bias=request.recency_bias,
    )

    results = retrieve(
        query=query,
        backend=store._backend,
        embedder=embedder,
    )

    logger.info(
        "search_performed", query=request.text, user_id=request.user_id, results=len(results)
    )

    return [
        SearchResultResponse(
            memory=MemoryResponse.model_validate(r.item),
            similarity=r.similarity,
            relevance=r.relevance,
            final_score=r.final_score,
        )
        for r in results
    ]


@router.post("/memories/consolidate", response_model=ConsolidationResponse)
def consolidate_memories(
    request: ConsolidateRequest,
    store: EmbeddingStorageWrapper = Depends(get_storage),
):
    """
    Run consolidation for a user's memories.
    Detects near-duplicate memories, merges them, soft-deletes originals.
    """

    config = ConsolidationConfig(
        similarity_threshold=request.similarity_threshold,
    )

    result = consolidate(
        user_id=request.user_id,
        backend=store._backend,
        agent_id=request.agent_id,
        namespace=request.namespace,
        config=config,
    )

    return ConsolidationResponse(
        clusters_found=result.clusters_found,
        memories_consolidated=result.memories_consolidated,
        consolidated_ids=[item.id for item in result.consolidated_items],
    )


@router.get("/metrics")
def metrics_endpoint():
    """Return current system metrics"""

    return get_metrics().to_dict()
