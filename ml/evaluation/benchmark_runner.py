"""Benchmark Runner for ScamGraph Model Evaluation.

Comprehensive evaluation framework for:
1. Baseline (TF-IDF + Logistic Regression)
2. Multilingual Message Detector (Horizon-Labs/phishing-scam-detector-base)
3. URL Detection (CrabInHoney/urlbert-tiny-v6)

Supports multiple test sets:
- in-distribution: familiar patterns with deduplication
- unseen-campaign: new templates not in training
- language-specific: English, Hindi, Hinglish
- hard-negatives: legitimate notifications that resemble scams
- calibration: probability calibration analysis
"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "message" / "artifacts"


@dataclass
class ModelMetrics:
    """Canonical metric set for model evaluation."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    false_negative_rate: float
    roc_auc: float
    confusion_matrix: Dict[str, int]
    test_sample_count: int
    positive_class_count: int
    negative_class_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_predictions(
        cls,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None,
    ) -> ModelMetrics:
        """Compute metrics from true labels and predictions."""
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)

        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

        # ROC-AUC (requires probabilities)
        try:
            roc_auc = float(roc_auc_score(y_true, y_prob)) if y_prob is not None else 0.0
        except Exception:
            roc_auc = 0.0

        return cls(
            accuracy=round(acc, 4),
            precision=round(prec, 4),
            recall=round(rec, 4),
            f1_score=round(f1, 4),
            false_positive_rate=round(fpr, 4),
            false_negative_rate=round(fnr, 4),
            roc_auc=round(roc_auc, 4),
            confusion_matrix={
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
            },
            test_sample_count=len(y_true),
            positive_class_count=int((y_true == 1).sum()),
            negative_class_count=int((y_true == 0).sum()),
        )


@dataclass
class BenchmarkResult:
    """Single model evaluation result."""

    model_name: str
    model_id: str
    test_set_name: str
    test_set_id: str
    metrics: ModelMetrics
    timestamp: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_id": self.model_id,
            "test_set_name": self.test_set_name,
            "test_set_id": self.test_set_id,
            "metrics": self.metrics.to_dict(),
            "timestamp": self.timestamp,
            "notes": self.notes,
        }


class BenchmarkRunner:
    """Orchestrates benchmarking across models and test sets."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir) if output_dir else ARTIFACTS_DIR / "benchmarks"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[BenchmarkResult] = []

    def record_result(
        self,
        model_name: str,
        model_id: str,
        test_set_name: str,
        test_set_id: str,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: Optional[np.ndarray] = None,
        notes: Optional[str] = None,
    ) -> BenchmarkResult:
        """Record a single benchmark evaluation."""
        metrics = ModelMetrics.from_predictions(y_true, y_pred, y_prob)
        result = BenchmarkResult(
            model_name=model_name,
            model_id=model_id,
            test_set_name=test_set_name,
            test_set_id=test_set_id,
            metrics=metrics,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            notes=notes,
        )
        self.results.append(result)
        logger.info(
            f"Recorded: {model_name} on {test_set_name} | F1={metrics.f1_score:.4f} FPR={metrics.false_positive_rate:.4f}"
        )
        return result

    def save_results(self, filename: str = "benchmark_results.json") -> Path:
        """Save all recorded results to JSON."""
        output_path = self.output_dir / filename
        data = {
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_results": len(self.results),
            "results": [r.to_dict() for r in self.results],
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(self.results)} results to {output_path}")
        return output_path

    def generate_comparison_report(self) -> str:
        """Generate human-readable comparison report."""
        if not self.results:
            return "No results to compare."

        # Group by model
        by_model = {}
        for result in self.results:
            if result.model_id not in by_model:
                by_model[result.model_id] = []
            by_model[result.model_id].append(result)

        report_lines = [
            "=" * 80,
            "SCAMGRAPH MODEL BENCHMARK REPORT",
            f"Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
            "=" * 80,
            "",
        ]

        for model_id, model_results in by_model.items():
            report_lines.append(f"\nModel: {model_results[0].model_name} ({model_id})")
            report_lines.append("-" * 80)
            report_lines.append(
                f"{'Test Set':<25} {'F1':<8} {'Prec':<8} {'Rec':<8} {'FPR':<8} {'ROC-AUC':<8} {'Samples'}"
            )
            report_lines.append("-" * 80)

            for result in model_results:
                m = result.metrics
                report_lines.append(
                    f"{result.test_set_id:<25} {m.f1_score:<8.4f} "
                    f"{m.precision:<8.4f} {m.recall:<8.4f} {m.false_positive_rate:<8.4f} "
                    f"{m.roc_auc:<8.4f} {m.test_sample_count}"
                )

        report_lines.append("\n" + "=" * 80)
        report_lines.append("INTERPRETATION GUIDE")
        report_lines.append("=" * 80)
        report_lines.append("F1:        Harmonic mean of precision and recall")
        report_lines.append("Precision: Proportion of positive predictions that were correct")
        report_lines.append("Recall:    Proportion of actual positives that were detected")
        report_lines.append("FPR:       False positive rate (legitimate marked as scam)")
        report_lines.append("ROC-AUC:   Area under receiver operating characteristic curve")
        report_lines.append("")
        report_lines.append("Higher is better for: F1, Precision, Recall, ROC-AUC")
        report_lines.append("Lower is better for: FPR, False Negative Rate")

        return "\n".join(report_lines)

    def save_report(self, filename: str = "benchmark_report.txt") -> Path:
        """Save comparison report to file."""
        output_path = self.output_dir / filename
        report = self.generate_comparison_report()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info(f"Saved benchmark report to {output_path}")
        return output_path
