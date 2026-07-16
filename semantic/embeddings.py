from config import EMBEDDING_MODEL
from semantic.providers import MiniLMProvider, BGEProvider, GTEProvider

_PROVIDER = None
PROVIDER_VERSION = 0


def set_provider(model_name: str):
    """
    Sets the active embedding provider and increments the version
    so the semantic engine knows to rebuild the knowledge base.
    """
    global _PROVIDER, PROVIDER_VERSION
    name_lower = model_name.lower()
    
    if "bge" in name_lower:
        _PROVIDER = BGEProvider()
    elif "gte" in name_lower:
        _PROVIDER = GTEProvider()
    else:
        _PROVIDER = MiniLMProvider()
        
    PROVIDER_VERSION += 1


def load_provider():
    """
    Lazily loads and caches the embedding provider.
    """
    global _PROVIDER
    if _PROVIDER is None:
        set_provider(EMBEDDING_MODEL)
    return _PROVIDER


def get_embedding(text: str):
    """
    Returns an embedding vector for a single text.
    """
    if not text:
        return None
    provider = load_provider()
    return provider.get_embedding(text)


def get_embeddings(texts: list[str]):
    """
    Returns embeddings for multiple texts.
    """
    if not texts:
        return []
    provider = load_provider()
    return provider.get_embeddings(texts)


def model_name() -> str:
    """
    Returns the currently configured embedding model.
    """
    provider = load_provider()
    return provider.get_name()


def unload_model():
    """
    Frees the cached model.
    Useful for tests.
    """
    global _PROVIDER
    if _PROVIDER is not None:
        _PROVIDER.unload()
        _PROVIDER = None
