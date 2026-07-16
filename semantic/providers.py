from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
import torch
from config import FORCE_CPU, NORMALIZE_EMBEDDINGS

class EmbeddingProvider(ABC):
    
    @abstractmethod
    def get_embedding(self, text: str):
        pass
        
    @abstractmethod
    def get_embeddings(self, texts: list[str]):
        pass
        
    @abstractmethod
    def get_name(self) -> str:
        pass
        
    @abstractmethod
    def unload(self):
        pass


class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        self._model_name = model_name
        self._model = None
        
    def _get_device(self) -> str:
        if FORCE_CPU:
            return "cpu"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"
        
    def _load(self):
        if self._model is None:
            self._model = SentenceTransformer(
                self._model_name,
                device=self._get_device()
            )
            
    def get_embedding(self, text: str):
        if not text:
            return None
        self._load()
        return self._model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=NORMALIZE_EMBEDDINGS
        )
        
    def get_embeddings(self, texts: list[str]):
        if not texts:
            return []
        self._load()
        return self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=NORMALIZE_EMBEDDINGS
        )
        
    def get_name(self) -> str:
        return self._model_name
        
    def unload(self):
        self._model = None


class MiniLMProvider(SentenceTransformerProvider):
    def __init__(self):
        super().__init__("sentence-transformers/all-MiniLM-L6-v2")


class BGEProvider(SentenceTransformerProvider):
    def __init__(self):
        super().__init__("BAAI/bge-base-en-v1.5")


class GTEProvider(SentenceTransformerProvider):
    def __init__(self):
        super().__init__("thenlper/gte-large")
