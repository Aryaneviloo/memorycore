from memvault.embeddings.base import BaseEmbedder
from memvault.embeddings.local import LocalEmbedder


def get_embedder(provider: str = "local", **kwargs) -> BaseEmbedder:
    """

    Factory- return the right embedder for the given provider name

    Currenlty supported: "local" - BGE small running locally via sentence transformer

    More providers (OPENAI, Cohera, etc) can be added
    """

    if provider == "local":
        return LocalEmbedder(**kwargs)

    raise ValueError(f"Unknown embedding provider, {provider!r} Available: 'local'")
