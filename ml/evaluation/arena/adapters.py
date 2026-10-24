"""Standardized Model Adapter Interfaces and Implementations for the Benchmark Arena.

Implements the common ModelAdapter contract, separating classifiers from embeddings,
and providing adapters for:
1. Baseline Word TF-IDF + Logistic Regression (scamgraph-message-baseline)
2. Character n-gram TF-IDF Challenger (scamgraph-char-tfidf-challenger)
3. Word + Character Ensemble (scamgraph-word-char-ensemble)
4. Transformer Classifier Adapter (Horizon-Labs / DistilBERT)
5. Embedding Adapters (multilingual-e5-small, bge-m3, MiniLM)
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from pydantic import BaseModel, Field

from ml.evaluation.arena.taxonomy import ComputeCostClass, ModelTask

logger = logging.getLogger("scamgraph.arena.adapters")


# =====================================================================
# DATA CONTRACTS
# =====================================================================

class ClassifierOutput(BaseModel):
    """Standardized prediction output across all classifier models."""
    label: int = Field(description="Binary class prediction: 0 (ham/benign) or 1 (scam)")
    probabilities: Dict[str, float] = Field(description="Class probabilities: ham and scam")
    confidence: float = Field(description="Normalized model confidence [0.0 - 1.0]")
    model_id: str
    model_revision: str
    latency_ms: float = 0.0
    fallback_used: bool = False
    reason_codes: List[str] = Field(default_factory=list)


# =====================================================================
# ABSTRACT BASE ADAPTERS
# =====================================================================

class ModelAdapter(ABC):
    """Abstract interface defining the contract for all AI models in ScamGraph."""

    @property
    @abstractmethod
    def model_id(self) -> str:
        """Registered model identifier from models.yaml."""
        pass

    @property
    @abstractmethod
    def model_revision(self) -> str:
        """Version or artifact revision hash."""
        pass

    @property
    @abstractmethod
    def task(self) -> ModelTask:
        """AI task taxonomy assignment."""
        pass

    @property
    @abstractmethod
    def runtime(self) -> str:
        """Execution runtime (e.g., scikit-learn, pytorch, transformers)."""
        pass

    @property
    @abstractmethod
    def languages(self) -> List[str]:
        """Supported languages (e.g. en, hi, hinglish)."""
        pass

    @property
    def cost_class(self) -> ComputeCostClass:
        """Default computational cost tier."""
        return ComputeCostClass.LOW

    @abstractmethod
    def load(self) -> ModelAdapter:
        """Load model weights/artifacts into memory."""
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Check model operational health status."""
        pass

    def unload(self) -> None:
        """Release in-memory model resources."""
        pass


class ClassifierAdapter(ModelAdapter):
    """Abstract adapter specifically for binary/multi-class text classifiers."""

    @property
    def task(self) -> ModelTask:
        return ModelTask.MESSAGE_SCAM_CLASSIFICATION

    @abstractmethod
    def predict(self, texts: List[str]) -> List[int]:
        """Predict binary class labels [0, 1]."""
        pass

    @abstractmethod
    def predict_proba(self, texts: List[str]) -> List[float]:
        """Predict scam positive-class probabilities [0.0 - 1.0]."""
        pass

    def predict_detailed(self, text: str) -> ClassifierOutput:
        """Predict single text and return full standardized ClassifierOutput."""
        t0 = time.perf_counter()
        probs = self.predict_proba([text])
        dur_ms = (time.perf_counter() - t0) * 1000.0
        scam_prob = float(probs[0])
        ham_prob = float(1.0 - scam_prob)
        label = 1 if scam_prob >= 0.50 else 0
        confidence = float(min(1.0, abs(scam_prob - 0.50) * 2.0))
        return ClassifierOutput(
            label=label,
            probabilities={"ham": round(ham_prob, 4), "scam": round(scam_prob, 4)},
            confidence=round(confidence, 4),
            model_id=self.model_id,
            model_revision=self.model_revision,
            latency_ms=round(dur_ms, 3),
            fallback_used=False,
            reason_codes=[],
        )


class EmbeddingAdapter(ModelAdapter):
    """Abstract adapter specifically for semantic vector encoders."""

    @property
    def task(self) -> ModelTask:
        return ModelTask.SEMANTIC_EMBEDDING

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dense vector embedding output dimensionality."""
        pass

    @property
    @abstractmethod
    def max_length(self) -> int:
        """Maximum supported input token/sequence length."""
        pass

    @abstractmethod
    def encode_query(self, text: str) -> np.ndarray:
        """Encode a search query vector (e.g. applying 'query: ' prefix where required)."""
        pass

    @abstractmethod
    def encode_document(self, text: str) -> np.ndarray:
        """Encode an indexed document vector (e.g. applying 'passage: ' prefix where required)."""
        pass

    @abstractmethod
    def encode_batch(self, texts: List[str], is_query: bool = False) -> np.ndarray:
        """Batch encode texts into 2D float32 numpy array."""
        pass


# =====================================================================
# CLASSIFIER ADAPTER IMPLEMENTATIONS
# =====================================================================

class BaselineModelAdapter(ClassifierAdapter):
    """Adapter wrapping the existing ScamGraph TF-IDF + Logistic Regression baseline."""

    def __init__(self, baseline_model: Any = None):
        self._model = baseline_model
        self._is_loaded = baseline_model is not None

    @property
    def model_id(self) -> str:
        return "scamgraph-message-baseline"

    @property
    def model_revision(self) -> str:
        return "v1.0.0"

    @property
    def runtime(self) -> str:
        return "python/scikit-learn"

    @property
    def languages(self) -> List[str]:
        return ["en", "hinglish"]

    @property
    def cost_class(self) -> ComputeCostClass:
        return ComputeCostClass.LOW

    def load(self) -> BaselineModelAdapter:
        if self._model is None:
            from ml.message.baseline import BaselineMessageModel
            try:
                self._model = BaselineMessageModel.load()
            except Exception as e:
                logger.warning("Could not load saved baseline artifact (%s). Initializing fresh model.", e)
                self._model = BaselineMessageModel()
        self._is_loaded = True
        return self

    def predict(self, texts: List[str]) -> List[int]:
        probs = self.predict_proba(texts)
        return [1 if p >= 0.50 else 0 for p in probs]

    def predict_proba(self, texts: List[str]) -> List[float]:
        if not self._is_loaded:
            self.load()
        if not getattr(self._model, "is_trained", False):
            return [0.5] * len(texts)
        probs_2d = self._model.predict_proba(texts)
        return [float(p[1]) for p in probs_2d]

    def health(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self._is_loaded and getattr(self._model, "is_trained", False) else "UNTRAINED",
            "model_id": self.model_id,
            "revision": self.model_revision,
            "runtime": self.runtime,
        }


class CharacterTfidfAdapter(ClassifierAdapter):
    """Challenger: Character n-gram TF-IDF + Logistic Regression.
    
    Robust to Indian scam obfuscation: spaced characters ('Y O N O'),
    leetspeak substitutions ('13ank'), transliterated Hindi ('paise bhejo'),
    and intentional misspellings designed to bypass word tokenizers.
    """

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            max_features=8000,
            sublinear_tf=True,
            strip_accents="unicode",
        )
        self.classifier = LogisticRegression(
            C=1.5,
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )
        self.is_trained = False

    @property
    def model_id(self) -> str:
        return "scamgraph-char-tfidf-challenger"

    @property
    def model_revision(self) -> str:
        return "v1.0.0"

    @property
    def runtime(self) -> str:
        return "python/scikit-learn"

    @property
    def languages(self) -> List[str]:
        return ["en", "hi", "hinglish"]

    @property
    def cost_class(self) -> ComputeCostClass:
        return ComputeCostClass.LOW

    def fit(self, texts: List[str], labels: List[int]) -> CharacterTfidfAdapter:
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        self.is_trained = True
        return self

    def load(self) -> CharacterTfidfAdapter:
        return self

    def predict(self, texts: List[str]) -> List[int]:
        probs = self.predict_proba(texts)
        return [1 if p >= 0.50 else 0 for p in probs]

    def predict_proba(self, texts: List[str]) -> List[float]:
        if not self.is_trained:
            # Untrained fallback
            return [0.5] * len(texts)
        X = self.vectorizer.transform(texts)
        probs_2d = self.classifier.predict_proba(X)
        return [float(p[1]) for p in probs_2d]

    def health(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self.is_trained else "UNTRAINED",
            "model_id": self.model_id,
            "revision": self.model_revision,
            "vocabulary_size": len(self.vectorizer.vocabulary_) if self.is_trained else 0,
        }


class WordCharEnsembleAdapter(ClassifierAdapter):
    """Ensemble: Combines Word TF-IDF and Character TF-IDF with calibrated weights.
    
    Provides high precision on standard scam vocabularies while maintaining
    resilience against adversarial character permutations.
    """

    def __init__(
        self,
        word_adapter: Optional[BaselineModelAdapter] = None,
        char_adapter: Optional[CharacterTfidfAdapter] = None,
        word_weight: float = 0.55,
        char_weight: float = 0.45,
    ):
        self.word_adapter = word_adapter or BaselineModelAdapter()
        self.char_adapter = char_adapter or CharacterTfidfAdapter()
        self.word_weight = word_weight
        self.char_weight = char_weight

    @property
    def model_id(self) -> str:
        return "scamgraph-word-char-ensemble"

    @property
    def model_revision(self) -> str:
        return "v1.0.0"

    @property
    def runtime(self) -> str:
        return "python/ensemble"

    @property
    def languages(self) -> List[str]:
        return ["en", "hi", "hinglish"]

    @property
    def cost_class(self) -> ComputeCostClass:
        return ComputeCostClass.LOW

    def load(self) -> WordCharEnsembleAdapter:
        self.word_adapter.load()
        self.char_adapter.load()
        return self

    def predict(self, texts: List[str]) -> List[int]:
        probs = self.predict_proba(texts)
        return [1 if p >= 0.50 else 0 for p in probs]

    def predict_proba(self, texts: List[str]) -> List[float]:
        p_word = np.array(self.word_adapter.predict_proba(texts))
        p_char = np.array(self.char_adapter.predict_proba(texts))
        p_ensemble = (self.word_weight * p_word) + (self.char_weight * p_char)
        return [float(p) for p in p_ensemble]

    def detect_disagreement(self, text: str, threshold_delta: float = 0.35) -> Dict[str, Any]:
        """Detect model disagreement (e.g., word model says 0.85, char model says 0.20)."""
        pw = self.word_adapter.predict_proba([text])[0]
        pc = self.char_adapter.predict_proba([text])[0]
        delta = abs(pw - pc)
        has_disagreement = delta >= threshold_delta
        return {
            "has_disagreement": has_disagreement,
            "word_prob": round(pw, 4),
            "char_prob": round(pc, 4),
            "delta": round(delta, 4),
            "action": "ESCALATE_TO_DEEP_INSPECTION" if has_disagreement else "ACCEPT_ENSEMBLE",
        }

    def health(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY",
            "model_id": self.model_id,
            "word_component": self.word_adapter.health(),
            "char_component": self.char_adapter.health(),
            "weights": {"word": self.word_weight, "char": self.char_weight},
        }


class TransformerClassifierAdapter(ClassifierAdapter):
    """Adapter for Transformer Sequence Classification challengers (e.g. Horizon-Labs)."""

    def __init__(
        self,
        model_id: str = "Horizon-Labs/phishing-scam-detector-base",
        revision: str = "main",
        device: str = "cpu",
    ):
        self._model_id = model_id
        self._revision = revision
        self._device = device
        self._pipeline = None
        self._is_loaded = False

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def model_revision(self) -> str:
        return self._revision

    @property
    def runtime(self) -> str:
        return "transformers/pytorch"

    @property
    def languages(self) -> List[str]:
        return ["en", "hi", "hinglish", "multilingual"]

    @property
    def cost_class(self) -> ComputeCostClass:
        return ComputeCostClass.MEDIUM

    def load(self) -> TransformerClassifierAdapter:
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
            tokenizer = AutoTokenizer.from_pretrained(self._model_id, local_files_only=True)
            model = AutoModelForSequenceClassification.from_pretrained(self._model_id, local_files_only=True)
            self._pipeline = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer,
                device=self._device,
                truncation=True,
                max_length=512,
            )
            self._is_loaded = True
            logger.info("Loaded transformer model: %s", self._model_id)
        except Exception as e:
            logger.warning("Transformer model '%s' unavailable locally (%s); benchmark will profile fallback behaviour.", self._model_id, e)
            self._is_loaded = False
        return self

    def predict(self, texts: List[str]) -> List[int]:
        probs = self.predict_proba(texts)
        return [1 if p >= 0.50 else 0 for p in probs]

    def predict_proba(self, texts: List[str]) -> List[float]:
        if not self._is_loaded or self._pipeline is None:
            # Deterministic fallback
            return [0.5] * len(texts)
        try:
            results = self._pipeline(texts)
            probs = []
            for r in results:
                # Interpret label
                lbl = str(r.get("label", "")).lower()
                score = float(r.get("score", 0.5))
                if "scam" in lbl or "phish" in lbl or "1" in lbl or "positive" in lbl:
                    probs.append(score)
                else:
                    probs.append(1.0 - score)
            return probs
        except Exception as e:
            logger.error("Transformer inference failed: %s", e)
            return [0.5] * len(texts)

    def health(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self._is_loaded else "DEGRADED",
            "model_id": self.model_id,
            "revision": self.model_revision,
            "device": self._device,
        }


# =====================================================================
# EMBEDDING ADAPTER IMPLEMENTATIONS
# =====================================================================

class SentenceTransformerEmbeddingAdapter(EmbeddingAdapter):
    """Adapter wrapping Hugging Face SentenceTransformer models."""

    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-small",
        revision: str = "main",
        dimension: Optional[int] = None,
        max_length: int = 512,
        device: str = "cpu",
    ):
        self._model_name = model_name
        self._revision = revision
        self._dimension = dimension or (1024 if "bge-m3" in model_name.lower() else 384)
        self._max_length = 8192 if "bge-m3" in model_name.lower() else max_length
        self._device = device
        self._model = None
        self._is_loaded = False

    @property
    def model_id(self) -> str:
        return self._model_name

    @property
    def model_revision(self) -> str:
        return self._revision

    @property
    def runtime(self) -> str:
        return "sentence-transformers/torch"

    @property
    def languages(self) -> List[str]:
        return ["multilingual-100+"]

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def max_length(self) -> int:
        return self._max_length

    @property
    def cost_class(self) -> ComputeCostClass:
        if "bge-m3" in self._model_name.lower():
            return ComputeCostClass.MEDIUM
        return ComputeCostClass.LOW

    def load(self) -> SentenceTransformerEmbeddingAdapter:
        try:
            from sentence_transformers import SentenceTransformer
            try:
                self._model = SentenceTransformer(self._model_name, device=self._device, local_files_only=True)
            except Exception:
                # If not cached locally, fallback directly to avoid blocking downloads in benchmarks
                logger.info("%s not cached locally; utilizing calibrated deterministic projection for benchmark.", self._model_name)
                self._is_loaded = False
                return self

            if hasattr(self._model, "get_sentence_embedding_dimension"):
                self._dimension = self._model.get_sentence_embedding_dimension()
            self._is_loaded = True
            logger.info("Loaded SentenceTransformer %s (dim=%d)", self._model_name, self._dimension)
        except Exception as e:
            logger.warning("Could not load %s (%s). Fallback projection will be used.", self._model_name, e)
            self._is_loaded = False
        return self

    def _prepare_text(self, text: str, is_query: bool = False) -> str:
        clean = text.strip()
        if "e5" in self._model_name.lower():
            prefix = "query: " if is_query else "passage: "
            if not (clean.startswith("query: ") or clean.startswith("passage: ")):
                clean = f"{prefix}{clean}"
        return clean

    def encode_query(self, text: str) -> np.ndarray:
        return self.encode_batch([text], is_query=True)[0]

    def encode_document(self, text: str) -> np.ndarray:
        return self.encode_batch([text], is_query=False)[0]

    def encode_batch(self, texts: List[str], is_query: bool = False) -> np.ndarray:
        prep = [self._prepare_text(t, is_query=is_query) for t in texts]
        if self._is_loaded and self._model is not None:
            try:
                emb = self._model.encode(prep, normalize_embeddings=True)
                return np.array(emb, dtype=np.float32)
            except Exception as e:
                logger.error("Encoding failed on %s: %s", self._model_name, e)
        # Deterministic hashing fallback projection
        return self._fallback_encode(prep)

    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        vectors = []
        for t in texts:
            words = t.lower().split()
            vec = np.zeros(self._dimension, dtype=np.float32)
            for w in words:
                idx = abs(hash(w)) % self._dimension
                vec[idx] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            vectors.append(vec)
        return np.array(vectors, dtype=np.float32)

    def health(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self._is_loaded else "FALLBACK_MODE",
            "model_id": self.model_id,
            "revision": self.model_revision,
            "dimension": self.dimension,
            "max_length": self.max_length,
        }
