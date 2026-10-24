"""Baseline TF-IDF + Logistic Regression model for ScamGraph Message Intelligence.

Provides:
1. Vectorizer and model training on leakage-free partitioned data
2. Comprehensive evaluation (precision, recall, F1, FPR, confusion matrix)
3. Artifact serialization to ml/message/artifacts/
4. Fast inference helper for runtime message scoring
"""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from ml.message.dataset_loader import MessageRecord, load_all_datasets
from ml.message.preprocessor import MessagePreprocessor, PreprocessingStats

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"


class BaselineMessageModel:
    """TF-IDF + Logistic Regression Scam Detection Baseline."""

    def __init__(
        self,
        vectorizer: Optional[TfidfVectorizer] = None,
        classifier: Optional[LogisticRegression] = None,
    ):
        self.vectorizer = vectorizer or TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            strip_accents="unicode",
        )
        self.classifier = classifier or LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )
        self.is_trained = classifier is not None and vectorizer is not None

    def fit(self, train_texts: List[str], train_labels: List[int]) -> BaselineMessageModel:
        """Fit vectorizer and classifier on training data."""
        logger.info(f"Training TF-IDF on {len(train_texts)} samples...")
        X_train = self.vectorizer.fit_transform(train_texts)
        logger.info(f"Fitting LogisticRegression classifier...")
        self.classifier.fit(X_train, train_labels)
        self.is_trained = True
        return self

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """Return scam probability for texts."""
        if not self.is_trained:
            raise RuntimeError("Model is not trained or loaded.")
        X = self.vectorizer.transform(texts)
        return self.classifier.predict_proba(X)

    def predict(self, texts: List[str], threshold: float = 0.5) -> List[int]:
        """Predict 0 (ham) or 1 (scam) with configurable decision threshold."""
        probs = self.predict_proba(texts)[:, 1]
        return [1 if p >= threshold else 0 for p in probs]

    def predict_single(self, text: str) -> Dict[str, Any]:
        """Classify single message returning label, probability, and risk level."""
        probs = self.predict_proba([text])[0]
        scam_prob = float(probs[1])
        ham_prob = float(probs[0])
        predicted_label = 1 if scam_prob >= 0.5 else 0

        # Confidence is distance from decision boundary (0.5) scaled to 0..1
        confidence = float(min(1.0, abs(scam_prob - 0.5) * 2.0))

        return {
            "label": "scam" if predicted_label == 1 else "ham",
            "is_scam": bool(predicted_label == 1),
            "scam_probability": round(scam_prob, 4),
            "ham_probability": round(ham_prob, 4),
            "confidence": round(confidence, 4),
        }

    def evaluate(self, test_texts: List[str], test_labels: List[int]) -> Dict[str, Any]:
        """Comprehensive evaluation on test data."""
        y_true = np.array(test_labels)
        y_pred = np.array(self.predict(test_texts))
        y_prob = self.predict_proba(test_texts)[:, 1]

        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

        metrics = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "false_positive_rate": round(fpr, 4),
            "confusion_matrix": {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
            },
            "test_sample_count": len(test_texts),
        }
        return metrics

    def save(self, directory: Optional[Path] = None) -> Path:
        """Serialize model, vectorizer, and metadata to disk."""
        target_dir = Path(directory) if directory else ARTIFACTS_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.classifier, target_dir / "model.joblib")
        joblib.dump(self.vectorizer, target_dir / "vectorizer.joblib")
        logger.info(f"Saved model artifacts to {target_dir}")
        return target_dir

    @classmethod
    def load(cls, directory: Optional[Path] = None) -> BaselineMessageModel:
        """Load serialized model and vectorizer."""
        target_dir = Path(directory) if directory else ARTIFACTS_DIR
        model_path = target_dir / "model.joblib"
        vec_path = target_dir / "vectorizer.joblib"

        if not model_path.exists() or not vec_path.exists():
            raise FileNotFoundError(f"Model artifacts not found in {target_dir}")

        classifier = joblib.load(model_path)
        if not hasattr(classifier, "multi_class"):
            classifier.multi_class = "auto"
        vectorizer = joblib.load(vec_path)
        return cls(vectorizer=vectorizer, classifier=classifier)


def train_and_evaluate_baseline(
    test_ratio: float = 0.20,
    random_seed: int = 42,
    artifacts_dir: Optional[Path] = None,
) -> Tuple[BaselineMessageModel, Dict[str, Any], PreprocessingStats]:
    """Orchestrate end-to-end dataset loading, preprocessing, training, evaluation, and persistence."""
    out_dir = Path(artifacts_dir) if artifacts_dir else ARTIFACTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load datasets (exclude_unreviewed=True ensures only audited records are used)
    records = load_all_datasets()

    # 2. Preprocess & Partition
    preprocessor = MessagePreprocessor(test_ratio=test_ratio, random_seed=random_seed)
    partitioned, stats = preprocessor.partition_leakage_free(records)

    train_data = [r for r in partitioned if r.split == "train"]
    test_data = [r for r in partitioned if r.split == "test"]

    train_texts = [r.text for r in train_data]
    train_labels = [r.label for r in train_data]

    test_texts = [r.text for r in test_data]
    test_labels = [r.label for r in test_data]

    # 3. Train Baseline
    model = BaselineMessageModel()
    model.fit(train_texts, train_labels)

    # 4. Evaluate
    metrics = model.evaluate(test_texts, test_labels)

    # 5. Save Artifacts
    model.save(out_dir)

    # Save metrics.json
    with open(out_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # Save dataset_manifest.json
    manifest = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "random_seed": random_seed,
        "test_ratio": test_ratio,
        "preprocessing_stats": stats.to_dict(),
        "evaluation_metrics": metrics,
    }
    with open(out_dir / "dataset_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Save model_metadata.json
    model_metadata = {
        "model_architecture": "TfidfVectorizer + LogisticRegression",
        "vectorizer_config": {
            "ngram_range": [1, 2],
            "max_features": 5000,
            "sublinear_tf": True,
        },
        "classifier_config": {
            "class_weight": "balanced",
            "C": 1.0,
            "max_iter": 1000,
        },
        "intended_scope": "Baseline Indian message scam signal detection (SMS / WhatsApp).",
        "output_type": "EvidenceSignal classification input, not final autonomous fraud verdict.",
    }
    with open(out_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(model_metadata, f, indent=2)

    logger.info("Successfully trained baseline and saved all artifacts.")
    return model, metrics, stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    model, metrics, stats = train_and_evaluate_baseline()
    print("Metrics:", json.dumps(metrics, indent=2))
