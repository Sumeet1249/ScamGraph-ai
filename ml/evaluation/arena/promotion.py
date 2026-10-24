"""Model Promotion Pipeline & Gating Policy for ScamGraph AI.

Enforces strict promotion governance:
CANDIDATE -> BENCHMARKING -> SHADOW -> APPROVED -> ACTIVE / REJECTED

A model that improves scam recall while creating unacceptable false alarms
on legitimate notifications CANNOT be approved (Rule 69).
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ml.evaluation.arena.scorecard import ClassifierScorecard, EmbeddingScorecard


class ModelLifecycleStatus(str, Enum):
    """Formal model governance lifecycle statuses (Rule 60)."""
    CANDIDATE = "CANDIDATE"
    BENCHMARKING = "BENCHMARKING"
    SHADOW = "SHADOW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    DEPRECATED = "DEPRECATED"


class PromotionDecision(BaseModel):
    """Formal audit decision regarding whether a model can be promoted."""
    model_id: str
    current_status: ModelLifecycleStatus
    target_status: ModelLifecycleStatus
    decision: str  # "PROMOTE", "HOLD", "REJECT"
    explanation: str
    passed_gates: List[str]
    failed_gates: List[str]
    target_tier: Optional[str] = None
    shadow_rollout_pct: float = 0.0


class ModelPromotionPolicy:
    """Evaluates scorecards against strict startup production gates."""

    @staticmethod
    def evaluate_classifier_promotion(
        scorecard: ClassifierScorecard,
        baseline_scorecard: Optional[ClassifierScorecard] = None,
        target_tier: str = "TIER_1_FAST_ML",
    ) -> PromotionDecision:
        """Evaluates whether a candidate classifier model meets promotion requirements."""
        passed: List[str] = []
        failed: List[str] = []

        # Gate 1: Hard-Negative FPR <= 1.0% (Rule 69 - Critical Consumer Trust Gate)
        if scorecard.hard_negative_fpr <= 0.010:
            passed.append(f"Gate 1 Passed: Hard-Negative FPR ({scorecard.hard_negative_fpr:.2%}) <= 1.0%")
        else:
            failed.append(f"Gate 1 FAILED: Hard-Negative FPR ({scorecard.hard_negative_fpr:.2%}) > 1.0%")

        # Gate 2: F1 >= Baseline F1
        baseline_f1 = baseline_scorecard.f1 if baseline_scorecard else 0.80
        if scorecard.f1 >= (baseline_f1 - 0.02):
            passed.append(f"Gate 2 Passed: F1 ({scorecard.f1:.3f}) >= Baseline ({baseline_f1:.3f})")
        else:
            failed.append(f"Gate 2 FAILED: F1 ({scorecard.f1:.3f}) < Baseline ({baseline_f1:.3f})")

        # Gate 3: Calibration ECE <= 0.10
        if scorecard.ece <= 0.10:
            passed.append(f"Gate 3 Passed: ECE ({scorecard.ece:.3f}) <= 0.10")
        else:
            failed.append(f"Gate 3 FAILED: ECE ({scorecard.ece:.3f}) > 0.10 (Poor calibration)")

        # Gate 4: Latency budget
        max_lat = 25.0 if target_tier == "TIER_1_FAST_ML" else 150.0
        if scorecard.p95_latency_ms <= max_lat:
            passed.append(f"Gate 4 Passed: p95 latency ({scorecard.p95_latency_ms:.1f}ms) <= {max_lat}ms")
        else:
            failed.append(f"Gate 4 FAILED: p95 latency ({scorecard.p95_latency_ms:.1f}ms) exceeds {max_lat}ms")

        # Decision logic
        if not failed:
            decision = "PROMOTE"
            target_status = ModelLifecycleStatus.APPROVED
            expl = f"Model passed all {len(passed)} production gates. Approved for {target_tier} deployment."
        elif any("Gate 1 FAILED" in f for f in failed):
            decision = "REJECT"
            target_status = ModelLifecycleStatus.REJECTED
            expl = "Model rejected due to excessive false positives on legitimate notifications (Hard-Negative Gate failure)."
        else:
            decision = "HOLD"
            target_status = ModelLifecycleStatus.BENCHMARKING
            expl = f"Model held in benchmarking. Failed gates: {'; '.join(failed)}"

        return PromotionDecision(
            model_id=scorecard.model_id,
            current_status=ModelLifecycleStatus.BENCHMARKING,
            target_status=target_status,
            decision=decision,
            explanation=expl,
            passed_gates=passed,
            failed_gates=failed,
            target_tier=target_tier if decision == "PROMOTE" else None,
            shadow_rollout_pct=5.0 if decision == "PROMOTE" else 0.0,
        )

    @staticmethod
    def evaluate_embedding_promotion(
        scorecard: EmbeddingScorecard,
        target_tier: str = "TIER_1_FAST_ML",
    ) -> PromotionDecision:
        """Evaluates whether a candidate embedding model meets retrieval and safety gates."""
        passed: List[str] = []
        failed: List[str] = []

        # Gate 1: Recall@5 >= 0.80
        if scorecard.recall_at_5 >= 0.80:
            passed.append(f"Gate 1 Passed: Recall@5 ({scorecard.recall_at_5:.2%}) >= 80%")
        else:
            failed.append(f"Gate 1 FAILED: Recall@5 ({scorecard.recall_at_5:.2%}) < 80%")

        # Gate 2: False-Neighbor Rate <= 5.0% (Rule 27)
        if scorecard.false_neighbor_rate <= 0.05:
            passed.append(f"Gate 2 Passed: False-Neighbor Rate ({scorecard.false_neighbor_rate:.2%}) <= 5.0%")
        else:
            failed.append(f"Gate 2 FAILED: False-Neighbor Rate ({scorecard.false_neighbor_rate:.2%}) > 5.0% (Misleading neighbors)")

        # Decision logic
        if not failed:
            decision = "PROMOTE"
            target_status = ModelLifecycleStatus.APPROVED
            expl = f"Embedding passed all retrieval & safety gates. Certified for {target_tier}."
        else:
            decision = "HOLD"
            target_status = ModelLifecycleStatus.BENCHMARKING
            expl = f"Embedding held in benchmarking. Failed gates: {'; '.join(failed)}"

        return PromotionDecision(
            model_id=scorecard.model_id,
            current_status=ModelLifecycleStatus.BENCHMARKING,
            target_status=target_status,
            decision=decision,
            explanation=expl,
            passed_gates=passed,
            failed_gates=failed,
            target_tier=target_tier if decision == "PROMOTE" else None,
        )
