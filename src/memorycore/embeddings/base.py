from abc import abstractmethod, ABC

class BaseEmbedder (ABC):
    """
    Abstract interface for all embedding providers
    
    Any embedder - local BGE, OpenAI, Cohere,, etc. must implement these two methods
    """

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Embed a single piece of text into a vector """

        raise NotImplementedError
    
    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """
        Embed a search query
        
        Separates from embed() because some models use a different prefix for queries vs store content
        """

        raise NotImplementedError
    
    @property
    @abstractmethod

    def dimentions(self)-> int:
        """
        Number of dimensions in the output vector
        """
        raise NotImplementedError
    



