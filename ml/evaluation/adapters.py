"""Standard model challenger interface and adapters for ScamGraph AI."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import time
import numpy as np


class ModelAdapter(ABC):
    """Abstract interface wrapping models for evaluation benchmarking."""

    @property
    @abstractmethod
    def model_id(self) -> str:
        """Registered model ID from models.yaml."""
        pass

    @property
    @abstractmethod
    def model_revision(self) -> str:
        """Version or artifact revision hash."""
        pass

    @abstractmethod
    def predict(self, texts: List[str]) -> List[int]:
        """Predict binary class (0: benign/ham, 1: scam)."""
        pass

    @abstractmethod
    def predict_proba(self, texts: List[str]) -> List[float]:
        """Predict scam probability (0.0 - 1.0)."""
        pass


class BaselineModelAdapter(ModelAdapter):
    """Adapter for the baseline TF-IDF + Logistic Regression message classifier."""

    def __init__(self, baseline_model: Any = None):
        if baseline_model is None:
            from ml.message.baseline import BaselineMessageModel
            self._model = BaselineMessageModel.load()
        else:
            self._model = baseline_model

    @property
    def model_id(self) -> str:
        return "scamgraph-message-baseline"

    @property
    def model_revision(self) -> str:
        return "v1.0.0"

    def predict(self, texts: List[str]) -> List[int]:
        probs = self.predict_proba(texts)
        return [1 if p >= 0.50 else 0 for p in probs]

    def predict_proba(self, texts: List[str]) -> List[float]:
        if not self._model.is_trained:
            return [0.5] * len(texts)
        probs_2d = self._model.predict_proba(texts)
        # return positive class (scam) probabilities
        return [float(p[1]) for p in probs_2d]


def benchmark_latency(
    adapter: ModelAdapter,
    sample_texts: List[str],
    warmup_runs: int = 5,
) -> Dict[str, float]:
    """Measure single-item and batch execution latency."""
    # Warmup
    for _ in range(warmup_runs):
        if sample_texts:
            adapter.predict_proba([sample_texts[0]])

    latencies_ms: List[float] = []
    for t in sample_texts:
        t0 = time.perf_counter()
        adapter.predict_proba([t])
        t1 = time.perf_counter()
        latencies_ms.append((t1 - t0) * 1000.0)

    arr = np.array(latencies_ms) if latencies_ms else np.array([0.0])
    
    # Batch throughput test
    t_batch_0 = time.perf_counter()
    adapter.predict_proba(sample_texts)
    t_batch_1 = time.perf_counter()
    batch_dur_sec = max(t_batch_1 - t_batch_0, 1e-6)
    throughput = len(sample_texts) / batch_dur_sec

    return {
        "mean_latency_ms": round(float(np.mean(arr)), 3),
        "p50_latency_ms": round(float(np.percentile(arr, 50)), 3),
        "p95_latency_ms": round(float(np.percentile(arr, 95)), 3),
        "p99_latency_ms": round(float(np.percentile(arr, 99)), 3),
        "throughput_items_per_sec": round(float(throughput), 1),
    }
