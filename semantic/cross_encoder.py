from sentence_transformers import CrossEncoder
import torch
import numpy as np
from config import CROSS_ENCODER_MODEL, FORCE_CPU

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


def load_model() -> CrossEncoder:
    """
    Lazily loads and caches the cross encoder model.
    """
    global _MODEL

    if _MODEL is None:
        device = _get_device()
        _MODEL = CrossEncoder(
            CROSS_ENCODER_MODEL,
            device=device
        )

    return _MODEL


def predict_scores(prompt: str, candidates: list[str]) -> list[float]:
    """
    Returns sigmoid scores for a prompt against a list of candidates.
    """
    if not prompt or not candidates:
        return []

    model = load_model()
    pairs = [[prompt, candidate] for candidate in candidates]
    
    # Model returns raw logits. We apply sigmoid to map to [0, 1]
    logits = model.predict(pairs)
    
    # Handle single candidate vs multiple candidates
    if isinstance(logits, float) or logits.ndim == 0:
        logits = np.array([logits])
        
    scores = 1 / (1 + np.exp(-logits))
    return scores.tolist()


def unload_model():
    """
    Frees the cached model.
    """
    global _MODEL
    _MODEL = None
