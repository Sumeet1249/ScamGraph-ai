"""Calibration Analysis for ScamGraph Models.

Ensures predicted probabilities match observed frequencies (calibration).
A well-calibrated model: when it predicts 70% scam, ~70% of those are actually scams.

Supports:
1. Calibration curves (expected vs observed)
2. Expected calibration error (ECE)
3. Maximum calibration error (MCE)
4. Reliability diagrams
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CalibrationMetrics:
    """Calibration analysis results."""

    expected_calibration_error: float
    maximum_calibration_error: float
    reliability_scores: List[Dict[str, float]]
    is_well_calibrated: bool
    interpretation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ece": round(self.expected_calibration_error, 4),
            "mce": round(self.maximum_calibration_error, 4),
            "is_well_calibrated": self.is_well_calibrated,
            "interpretation": self.interpretation,
            "reliability_scores": self.reliability_scores,
        }


class CalibrationAnalyzer:
    """Analyzes and visualizes model calibration."""

    def __init__(self, n_bins: int = 10):
        """
        Args:
            n_bins: Number of probability bins for calibration curve
        """
        self.n_bins = n_bins

    def analyze_calibration(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
    ) -> CalibrationMetrics:
        """Compute calibration metrics.
        
        Args:
            y_true: Binary true labels (0 or 1)
            y_prob: Predicted probabilities for positive class [0, 1]
            
        Returns:
            CalibrationMetrics object
        """
        y_true = np.array(y_true)
        y_prob = np.array(y_prob)

        # Compute expected calibration error (ECE)
        ece = self._expected_calibration_error(y_true, y_prob)

        # Compute maximum calibration error (MCE)
        mce = self._maximum_calibration_error(y_true, y_prob)

        # Generate reliability scores per bin
        reliability_scores = self._reliability_scores(y_true, y_prob)

        # Determine if well-calibrated
        is_calibrated = ece < 0.1  # ECE < 10% is generally considered good

        # Generate interpretation
        interp = self._interpret_calibration(ece, mce)

        return CalibrationMetrics(
            expected_calibration_error=ece,
            maximum_calibration_error=mce,
            reliability_scores=reliability_scores,
            is_well_calibrated=is_calibrated,
            interpretation=interp,
        )

    def _expected_calibration_error(
        self, y_true: np.ndarray, y_prob: np.ndarray
    ) -> float:
        """Expected Calibration Error (average difference per bin)."""
        bin_edges = np.linspace(0, 1, self.n_bins + 1)
        ece = 0
        total_samples = len(y_true)

        for i in range(self.n_bins):
            mask = (y_prob >= bin_edges[i]) & (y_prob < bin_edges[i + 1])
            if mask.sum() == 0:
                continue

            bin_probs = y_prob[mask]
            bin_true = y_true[mask]

            avg_confidence = bin_probs.mean()
            accuracy_in_bin = bin_true.mean()

            bin_weight = mask.sum() / total_samples
            ece += bin_weight * abs(avg_confidence - accuracy_in_bin)

        return float(ece)

    def _maximum_calibration_error(
        self, y_true: np.ndarray, y_prob: np.ndarray
    ) -> float:
        """Maximum Calibration Error (worst bin)."""
        bin_edges = np.linspace(0, 1, self.n_bins + 1)
        max_error = 0

        for i in range(self.n_bins):
            mask = (y_prob >= bin_edges[i]) & (y_prob < bin_edges[i + 1])
            if mask.sum() == 0:
                continue

            bin_probs = y_prob[mask]
            bin_true = y_true[mask]

            avg_confidence = bin_probs.mean()
            accuracy_in_bin = bin_true.mean()

            error = abs(avg_confidence - accuracy_in_bin)
            max_error = max(max_error, error)

        return float(max_error)

    def _reliability_scores(
        self, y_true: np.ndarray, y_prob: np.ndarray
    ) -> List[Dict[str, float]]:
        """Per-bin reliability scores."""
        bin_edges = np.linspace(0, 1, self.n_bins + 1)
        scores = []

        for i in range(self.n_bins):
            mask = (y_prob >= bin_edges[i]) & (y_prob < bin_edges[i + 1])
            if mask.sum() == 0:
                continue

            bin_probs = y_prob[mask]
            bin_true = y_true[mask]

            avg_confidence = bin_probs.mean()
            accuracy_in_bin = bin_true.mean()
            count = mask.sum()

            scores.append(
                {
                    "bin": f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}",
                    "predicted_prob": round(float(avg_confidence), 4),
                    "observed_accuracy": round(float(accuracy_in_bin), 4),
                    "samples": int(count),
                    "calibration_error": round(
                        abs(avg_confidence - accuracy_in_bin), 4
                    ),
                }
            )

        return scores

    def _interpret_calibration(self, ece: float, mce: float) -> str:
        """Generate human-readable interpretation."""
        if ece < 0.05:
            ece_desc = "Excellent calibration"
        elif ece < 0.1:
            ece_desc = "Good calibration"
        elif ece < 0.2:
            ece_desc = "Moderate calibration"
        else:
            ece_desc = "Poor calibration"

        if mce < 0.15:
            mce_desc = "consistent across bins"
        elif mce < 0.3:
            mce_desc = "some bins are poorly calibrated"
        else:
            mce_desc = "significant calibration issues in worst-case scenarios"

        return (
            f"{ece_desc} (ECE={ece:.4f}). "
            f"Model's worst-case bin is {mce_desc} (MCE={mce:.4f})."
        )


def calibration_report(
    y_true: List[int],
    y_prob: List[float],
    model_name: str = "Model",
) -> str:
    """Generate human-readable calibration report."""
    analyzer = CalibrationAnalyzer()
    metrics = analyzer.analyze_calibration(np.array(y_true), np.array(y_prob))

    lines = [
        "=" * 70,
        f"CALIBRATION ANALYSIS: {model_name}",
        "=" * 70,
        "",
        f"Expected Calibration Error (ECE): {metrics.expected_calibration_error:.4f}",
        f"Maximum Calibration Error (MCE): {metrics.maximum_calibration_error:.4f}",
        f"Well-Calibrated: {'YES' if metrics.is_well_calibrated else 'NO'}",
        "",
        f"Interpretation: {metrics.interpretation}",
        "",
        "Per-Bin Reliability:",
        "-" * 70,
        f"{'Probability Bin':<20} {'Predicted Prob':<15} {'Observed Acc':<15} {'Samples':<10}",
        "-" * 70,
    ]

    for score in metrics.reliability_scores:
        lines.append(
            f"{score['bin']:<20} "
            f"{score['predicted_prob']:<15.4f} "
            f"{score['observed_accuracy']:<15.4f} "
            f"{score['samples']:<10}"
        )

    lines.extend(
        [
            "=" * 70,
            "",
            "GUIDANCE:",
            "- If ECE < 0.05: Model is well calibrated, trust predicted probabilities",
            "- If 0.05 < ECE < 0.2: Consider calibration if precision threshold is critical",
            "- If ECE > 0.2: Model probabilities are unreliable, adjust decision threshold",
            "",
        ]
    )

    return "\n".join(lines)
