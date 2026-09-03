import pytest
import config
from semantic.embeddings import set_provider, load_provider, get_embedding, unload_model
import numpy as np

def test_default_model_is_bge():
    assert config.EMBEDDING_MODEL == "BAAI/bge-base-en-v1.5", "Default model must remain BGE"
    
def test_multilingual_model_selection():
    try:
        set_provider("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        provider = load_provider()
        assert provider.get_name() == "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    finally:
        unload_model()
        # Restore default
        set_provider(config.EMBEDDING_MODEL)

def test_numpy_contract():
    try:
        set_provider("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        emb = get_embedding("Hello world")
        assert isinstance(emb, np.ndarray), "Embedding must be a numpy array"
        assert emb.dtype == np.float32, "Embedding dtype must be float32"
    finally:
        unload_model()
        set_provider(config.EMBEDDING_MODEL)
