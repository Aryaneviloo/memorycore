from sentence_transformers import SentenceTransformer
from memorycore.embeddings.base import BaseEmbedder



#this prefix yiels better results with the bge model
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "



class LocalEmbedder(BaseEmbedder):
    """
    Local embedding provider using BGE-small via sentence transformers
    
    Downloads the model on first use, cached locally 
    RUNS ON CPU by default
    
    Install the optional dependency 
    pip install memorycore[local]
    
    """

    MODEL_NAME = "BAAI/bge-small-en-v1.5"

    def __init__(self, device: str = "cpu") -> None:
        self._model = SentenceTransformer(self.MODEL_NAME, device=device)

    
    def embed(self, text: str) -> list[float]:
        """Embed content text for storage"""
        vector = self._model.encode(text, normalize_embeddings = True)
        return vector.tolist()
    
    def embed_query(self, query: str) -> list[float]:
        """Embed the query with BGE prefix for better retrieval"""
        vector = self._model.encode(
            BGE_QUERY_PREFIX + query, normalize_embeddings=True,)
        
        return vector.tolist()
    

    @property
    def dimensions(self) -> int:
        return 384