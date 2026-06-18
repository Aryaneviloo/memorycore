from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from memorycore.core.models import MemoryItem, MemoryType
from memorycore.core.retrieval import cosine_similarity
from memorycore.storage.base import StorageBackend


@dataclass
class ConsolidationConfig:
    """
    Tunable metrics/param for the consolidation pipeline
    (detects duplicate mmeory and removes the softer one)
    """

    similarity_threshold: float = 0.85
    min_cluster_size: int = 2
    max_cluster_size: int = 10


@dataclass
class ConsolidationResult:
    """Result of a consolidation run"""

    clusters_found: int 
    memories_consolidated: int
    consolidated_item: list[MemoryItem] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)

def find_clusters(items: list[MemoryItem],
                              threshold: float,
                              max_size: int,
                              ) -> list[list[MemoryItem]]:
    
    """
    Group memories into clusters of similar items
    
    Uses a greedy appraoch:
    1) Iterate through items
    2) Assign each to an existing cluster if similar enough to its first member
    3) Otherwise start a new cluster
    
    Returns only clusters with 2+ memners(singletons are not consolidated)
    """

    if not items:
        return []
    
    clusters: list[list[MemoryItem]] = []
    assigned = set()

    for i, item in enumerate(items):
        if i in assigned or item.embedding is None:
            continue

        cluster = [item]
        assigned.add(i)


        for j, other in enumerate(items):
            if j in assigned or other.embedding is None:
                continue
            if len(cluster) >= max_size:
                break

            sim = cosine_similarity(item.embedding,  other.embedding)
            if sim>= threshold:
                cluster.append(other)
                assigned.add(j)


        clusters.append(cluster)


    return [c for c in clusters if len(c) >= 2]



def _make_summary(items: list[MemoryItem]) -> str:
    """
    
    Generate a simple summary from a cluster of similar memories.
    In version 1 this is deterministic text merge later we will add LLM
    
    """

    contents = [item.content for item in items]
    unique = list(dict.fromkeys(contents))


    if len(unique) == 1:
        return unique[0]
    
    joined = " | ".join(unique)
    return f" [Consolidated] {joined}"


def consolidate(
        user_id: str,
        backend: StorageBackend,
        *,
        agent_id: str | None = None,
        namespace: str = "default",
        config: ConsolidationConfig | None = None,
        now: datetime | None = None,

) -> ConsolidationResult:
    

    """
    Find clusters of similar memories, merg eeach clusters into a single CONSOLIDATED memory, and soft-delete the originals
    
    Args:
        user_id: Scope consolidated to this user
        backend: Storage backend to read from and write to
        agent_id: Optional agent scope
        namespace: Memory namespace to consolidate
        config: Tunable threshold
        now: reference time(uses UTC now if None)
        
    """

    if config is None:
        config = ConsolidationConfig()
    if now is None:
        npw = datetime.now(timezone.utc)



    candidates = backend.list_recent(
        user_id=user_id,
        agent_id=agent_id,
        namespace=namespace,
        limit=500,
    )

    embeddable = [c for c in candidates if c.embedding is not None]

    clusters = find_clusters(
        embeddable,
        threshold=config.similarity_threshold,
        max_size=config.max_cluster_size,
    )

    result = ConsolidationResult(clusters_found=len(clusters))

    for cluster in clusters:
        summary = _make_summary(cluster)

        max_importance = max(item.importance for item in cluster)

        consolidated = MemoryItem(
            agent_id=cluster[0].agent_id,
            user_id=user_id,
            namespace=namespace,
            type=MemoryType.CONSOLIDATED,
            content=summary,
            summary=summary,
            importance=min(max_importance * 1.1, 1.0),  # slight boost
            confidence=min(
                sum(i.confidence for i in cluster) / len(cluster), 1.0
            ), 
            tags=list({tag for item in cluster for tag in item.tags}),
            metadata={
                "consolidated_from": [item.id for item in cluster],
                "consolidated_at": now.isoformat(),
                "cluster_size": len(cluster),
            },
            created_at=now,
            updated_at=now,
        )


        backend.insert(consolidated)

        for item in cluster:
            backend.delete(item.id)

        result.consolidated_items.append(consolidated)
        result.source_ids.extend(item.id for item in cluster)
        result.memories_consolidated += len(cluster)





                                        
                                
                                        
                                    