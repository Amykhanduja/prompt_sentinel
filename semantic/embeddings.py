from sentence_transformers import SentenceTransformer
import torch
from config import EMBEDDING_MODEL,FORCE_CPU, NORMALIZE_EMBEDDINGS

_MODEL = None




def _get_device() -> str:
    """
    Returns the best available device.
    """
    if FORCE_CPU:
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def load_model() -> SentenceTransformer:
    """
    Lazily loads and caches the embedding model.
    """

    global _MODEL

    if _MODEL is None:

        device = _get_device()

        _MODEL = SentenceTransformer(
            EMBEDDING_MODEL,
            device=device
        )

    return _MODEL


def get_embedding(text: str):
    """
    Returns an embedding vector for a single text.
    """

    if not text:
        return None

    model = load_model()

    return model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=NORMALIZE_EMBEDDINGS
    )


def get_embeddings(texts: list[str]):
    """
    Returns embeddings for multiple texts.
    """

    if not texts:
        return []

    model = load_model()

    return model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=NORMALIZE_EMBEDDINGS
    )


def model_name() -> str:
    """
    Returns the currently configured embedding model.
    """

    return MODEL_NAME


def unload_model():
    """
    Frees the cached model.
    Useful for tests.
    """

    global _MODEL

    _MODEL = None
