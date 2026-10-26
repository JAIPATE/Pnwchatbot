"""Dense vector embedding generator for text chunks and queries."""

from abc import ABC, abstractmethod
import hashlib
import math
from typing import List
import numpy as np


class BaseEmbedder(ABC):
    """Abstract base class for vector embedders."""

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text strings into vector representations."""
        pass

    def embed_query(self, query: str) -> List[float]:
        """Embed a single search query."""
        results = self.embed_texts([query])
        return results[0] if results else []

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the vector dimensionality."""
        pass


class FastEmbedder(BaseEmbedder):
    """Generates dense vector embeddings using FastEmbed (BAAI/bge-small-en-v1.5, 384 dims)."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        from fastembed import TextEmbedding
        self._model_name = model_name
        self._model = TextEmbedding(model_name=model_name)
        self._dim = 384

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = list(self._model.embed(texts))
        return [arr.tolist() if isinstance(arr, np.ndarray) else list(arr) for arr in embeddings]


class DeterministicEmbedder(BaseEmbedder):
    """Deterministic token-hash embedder for unit testing and offline fallback."""

    def __init__(self, dimension: int = 384):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        results: List[List[float]] = []
        for text in texts:
            vec = np.zeros(self._dim, dtype=np.float32)
            words = text.lower().split()
            if not words:
                words = ["empty"]
            for i, word in enumerate(words):
                h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
                idx = h % self._dim
                sign = 1.0 if ((h >> 8) & 1) else -1.0
                vec[idx] += sign * (1.0 / math.sqrt(i + 1))

            # Normalize to unit vector
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            results.append(vec.tolist())
        return results


def get_embedder(provider: str = "fastembed", model_name: str = "BAAI/bge-small-en-v1.5") -> BaseEmbedder:
    """Factory to retrieve the appropriate vector embedder."""
    if provider == "deterministic":
        return DeterministicEmbedder()

    try:
        return FastEmbedder(model_name=model_name)
    except Exception as exc:
        print(f"[WARN] Failed to initialize FastEmbedder ({exc}), falling back to DeterministicEmbedder")
        return DeterministicEmbedder()
