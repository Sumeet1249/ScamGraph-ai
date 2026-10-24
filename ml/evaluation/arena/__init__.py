"""ScamGraph AI Model Benchmark Arena Package."""

from ml.evaluation.arena.taxonomy import ModelTask, ComputeCostClass
from ml.evaluation.arena.adapters import (
    ModelAdapter,
    ClassifierAdapter,
    EmbeddingAdapter,
    ClassifierOutput,
    BaselineModelAdapter,
    CharacterTfidfAdapter,
    WordCharEnsembleAdapter,
    TransformerClassifierAdapter,
    SentenceTransformerEmbeddingAdapter,
)
from ml.evaluation.arena.scorecard import (
    ClassifierScorecard,
    EmbeddingScorecard,
    VectorStorageCost,
    ScorecardCalculator,
)
from ml.evaluation.arena.promotion import (
    ModelLifecycleStatus,
    PromotionDecision,
    ModelPromotionPolicy,
)

__all__ = [
    "ModelTask",
    "ComputeCostClass",
    "ModelAdapter",
    "ClassifierAdapter",
    "EmbeddingAdapter",
    "ClassifierOutput",
    "BaselineModelAdapter",
    "CharacterTfidfAdapter",
    "WordCharEnsembleAdapter",
    "TransformerClassifierAdapter",
    "SentenceTransformerEmbeddingAdapter",
    "ClassifierScorecard",
    "EmbeddingScorecard",
    "VectorStorageCost",
    "ScorecardCalculator",
    "ModelLifecycleStatus",
    "PromotionDecision",
    "ModelPromotionPolicy",
    "BenchmarkArenaRunner",
]
