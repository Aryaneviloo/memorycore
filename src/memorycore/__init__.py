"""MemoryCore - open source infrastructure for AI agents

Quick starts:
    from memorycore import Memorycore

    mc = MemoryCore()
    mc.remember("User likes C++", user_id="aryan")
    results = mc.recall("programming preferences", user_id="aryan")
    
    """


from memorycore.memorycore import MemoryCore
from memorycore.core.models import MemoryItem, MemoryQuery, MemoryType
from memorycore.core.retrieval import RetrievalConfig, RetrievalResult
from memorycore.core.scoring import ScoringWeights


__version__ = "0.1.0"
__all__ = [
    "MemoryCore",
    "MemoryItem",
    "MemoryQuery",
    "MemoryType",
    "RetrievalConfig",
    "RetrievalResult",
    "ScoringWeights",
]
