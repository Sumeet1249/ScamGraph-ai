"""Evaluate DistilBERT transformer baseline vs TF-IDF baseline on Indian scam messages.

Compares:
1. TF-IDF + Logistic Regression
2. anmolshrivastav/distilbert-scam-detector-india
on the identical evaluation test split.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from ml.message.baseline import BaselineMessageModel
from ml.message.dataset_loader import load_all_datasets
from ml.message.preprocessor import MessagePreprocessor

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
TRANSFORMER_MODEL_ID = "anmolshrivastav/distilbert-scam-detector-india"


class DistilBertScamEvaluator:
    """Wrapper for DistilBERT scam detector inference and evaluation."""

    def __init__(self, model_id: str = TRANSFORMER_MODEL_ID):
        self.model_id = model_id
        logger.info(f"Loading transformer model {model_id}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id)
        self.model.eval()

    def predict_batch(self, texts: List[str], batch_size: int = 32) -> List[int]:
        """Run batch inference returning predicted labels (0=ham, 1=scam)."""
        all_preds: List[int] = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            inputs = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=256,
                return_token_type_ids=False,
                return_tensors="pt",
            )
            with torch.no_grad():
                logits = self.model(**inputs).logits
                preds = torch.argmax(logits, dim=-1).cpu().tolist()
                all_preds.extend(preds)

        return all_preds

    def predict_single(self, text: str) -> Dict[str, Any]:
        """Classify a single message returning probabilities."""
        inputs = self.tokenizer(
            text,
            truncation=True,
            max_length=256,
            return_token_type_ids=False,
            return_tensors="pt",
        )
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]

        # id2label in distilbert config: {0: 'ham', 1: 'spam'}
        scam_prob = float(probs[1])
        ham_prob = float(probs[0])
        pred_label = 1 if scam_prob >= 0.5 else 0

        return {
            "label": "scam" if pred_label == 1 else "ham",
            "is_scam": bool(pred_label == 1),
            "scam_probability": round(scam_prob, 4),
            "ham_probability": round(ham_prob, 4),
            "confidence": round(float(abs(scam_prob - 0.5) * 2.0), 4),
        }

    def evaluate(self, test_texts: List[str], test_labels: List[int]) -> Dict[str, Any]:
        """Evaluate model on test set."""
        y_true = np.array(test_labels)
        y_pred = np.array(self.predict_batch(test_texts))

        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

        return {
            "model_name": self.model_id,
            "architecture": "DistilBertForSequenceClassification",
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


def compare_models(
    sample_limit: Optional[int] = 200,
    random_seed: int = 42,
    test_ratio: float = 0.20,
) -> Dict[str, Any]:
    """Compare TF-IDF baseline and DistilBERT on the test partition.

    Args:
        sample_limit: Optional limit on test set size for rapid evaluation on CPU.
    """
    records = load_all_datasets()
    preprocessor = MessagePreprocessor(test_ratio=test_ratio, random_seed=random_seed)
    partitioned, _ = preprocessor.partition_leakage_free(records)

    test_data = [r for r in partitioned if r.split == "test"]
    if sample_limit and len(test_data) > sample_limit:
        test_data = test_data[:sample_limit]

    test_texts = [r.text for r in test_data]
    test_labels = [r.label for r in test_data]

    # Evaluate TF-IDF baseline
    tfidf_model = BaselineMessageModel.load()
    tfidf_metrics = tfidf_model.evaluate(test_texts, test_labels)
    tfidf_metrics["model_name"] = "TF-IDF + Logistic Regression"
    tfidf_metrics["architecture"] = "TfidfVectorizer + LogisticRegression"

    # Evaluate DistilBERT
    distilbert_evaluator = DistilBertScamEvaluator()
    distilbert_metrics = distilbert_evaluator.evaluate(test_texts, test_labels)

    comparison = {
        "evaluation_sample_count": len(test_texts),
        "models": {
            "tfidf_logistic_regression": tfidf_metrics,
            "distilbert_transformer": distilbert_metrics,
        },
        "summary": {
            "higher_f1": "distilbert" if distilbert_metrics["f1_score"] > tfidf_metrics["f1_score"] else "tfidf",
            "lower_fpr": "distilbert" if distilbert_metrics["false_positive_rate"] < tfidf_metrics["false_positive_rate"] else "tfidf",
        },
    }

    # Save to artifacts
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ARTIFACTS_DIR / "model_comparison.json", "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)

    return comparison


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = compare_models(sample_limit=200)
    print("Model Comparison Result:\n", json.dumps(res, indent=2))
