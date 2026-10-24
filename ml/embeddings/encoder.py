"""Multilingual Semantic Vector Encoder (Step 20).

Provides the canonical SemanticEncoder interface and local Hugging Face SentenceTransformer
provider for ScamGraph AI.

Supported & Preferred Models:
- Primary / Advanced: BAAI/bge-m3 (1024 dims, 8192 max tokens)
- Lightweight Default: intfloat/multilingual-e5-small (384 dims, fast on CPU)

Configurable via SCAMGRAPH_EMBEDDING_MODEL environment variable.
Embeddings are NOT scam classifiers. They provide semantic similarity, paraphrase resistance,
and vector retrieval evidence.
"""

import hashlib
import logging
import os
from typing import Dict, List, Optional, Tuple, Union
import numpy as np

logger = logging.getLogger("scamgraph.ml.embeddings.encoder")

DEFAULT_MODEL = "intfloat/multilingual-e5-small"
MODEL_DIMENSIONS: Dict[str, int] = {
    "intfloat/multilingual-e5-small": 384,
    "BAAI/bge-m3": 1024,
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 384,
}


class EmbeddingCache:
    """In-memory LRU-like cache to prevent recomputing unchanged embeddings."""

    def __init__(self, max_size: int = 10000):
        self._cache: Dict[str, np.ndarray] = {}
        self._max_size = max_size

    @staticmethod
    def _key(model_name: str, text: str) -> str:
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"{model_name}:{text_hash}"

    def get(self, model_name: str, text: str) -> Optional[np.ndarray]:
        return self._cache.get(self._key(model_name, text))

    def set(self, model_name: str, text: str, vector: np.ndarray) -> None:
        if len(self._cache) >= self._max_size:
            # Evict first 1000 keys
            keys_to_remove = list(self._cache.keys())[:1000]
            for k in keys_to_remove:
                del self._cache[k]
        self._cache[self._key(model_name, text)] = vector.copy()

    def clear(self) -> None:
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)


class SemanticEncoder:
    """Configurable pretrained semantic encoder interface and local provider."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        use_cache: bool = True,
    ):
        env_model = os.getenv("SCAMGRAPH_EMBEDDING_MODEL")
        self.model_name = model_name or env_model or DEFAULT_MODEL
        self.model_version = "1.0.0"
        self.device = device or os.getenv("SCAMGRAPH_DEVICE", "cpu")
        self._dimension = MODEL_DIMENSIONS.get(self.model_name, 384)
        self._model = None
        self._cache = EmbeddingCache() if use_cache else None

    @property
    def dimension(self) -> int:
        return self._dimension

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Initializing SentenceTransformer: %s on %s", self.model_name, self.device)
                self._model = SentenceTransformer(self.model_name, device=self.device)
                # Inspect actual dimension if model is loaded
                if hasattr(self._model, "get_sentence_embedding_dimension"):
                    self._dimension = self._model.get_sentence_embedding_dimension()
            except Exception as e:
                logger.warning(
                    "Could not load local Hugging Face model '%s' (%s). Falling back to deterministic n-gram encoder.",
                    self.model_name,
                    e,
                )
                self._model = False
        return self._model

    def encode(
        self,
        text: Union[str, List[str]],
        is_query: bool = False,
    ) -> np.ndarray:
        """Encodes text or list of texts into L2-normalized float32 embedding vectors.
        
        For E5 family models, automatically prefixes queries with 'query: ' and passages
        with 'passage: ' unless already present, as recommended by model authors.
        """
        is_single = isinstance(text, str)
        texts = [text] if is_single else list(text)

        # Check cache for single text
        if is_single and self._cache is not None:
            cached = self._cache.get(self.model_name, texts[0])
            if cached is not None:
                return cached

        # Prepare text for E5 prefixing if applicable
        prepared_texts = []
        is_e5 = "e5" in self.model_name.lower()
        for t in texts:
            clean_t = t.strip()
            if is_e5:
                prefix = "query: " if is_query else "passage: "
                if not (clean_t.startswith("query: ") or clean_t.startswith("passage: ")):
                    clean_t = f"{prefix}{clean_t}"
            prepared_texts.append(clean_t)

        model = self._get_model()
        if model:
            try:
                embeddings = model.encode(prepared_texts, normalize_embeddings=True)
                res = np.array(embeddings, dtype=np.float32)
                if is_single and self._cache is not None:
                    self._cache.set(self.model_name, texts[0], res[0])
                return res[0] if is_single else res
            except Exception as e:
                logger.error("Encoding error with %s: %s. Using fallback.", self.model_name, e)

        # Deterministic lightweight n-gram fallback
        res = self._fallback_encode(prepared_texts)
        if is_single and self._cache is not None:
            self._cache.set(self.model_name, texts[0], res[0])
        return res[0] if is_single else res

    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        """Deterministic hashing projection ensuring test reproducibility."""
        dim = self._dimension
        vectors = []
        for t in texts:
            words = t.lower().split()
            vec = np.zeros(dim, dtype=np.float32)
            for w in words:
                idx = abs(hash(w)) % dim
                vec[idx] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            vectors.append(vec)
        return np.array(vectors, dtype=np.float32)

    @staticmethod
    def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Computes cosine similarity between two 1D or 2D normalized vectors."""
        a = np.asarray(vec_a, dtype=np.float32)
        b = np.asarray(vec_b, dtype=np.float32)
        if a.ndim > 1:
            a = a.flatten()
        if b.ndim > 1:
            b = b.flatten()
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))


# Global default instance
semantic_encoder = SemanticEncoder()
