"""Mule Intelligence Service Orchestrator (Module B).

Coordinates 19-dimensional behavioral feature extraction, baseline rules evaluation,
supervised ML model inference, calibrated score synthesis, and escalation recommendations.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from packages.schemas.mule import (
    BatchMuleEvaluationRequest,
    BatchMuleEvaluationResponse,
    MuleAction,
    MuleEvaluationRequest,
    MuleEvaluationResponse,
    MuleRiskBand,
)
from services.mule_engine.feature_extractor import MuleFeatureExtractor
from services.mule_engine.model import METRICS_PATH, MuleMLClassifier, get_mule_classifier
from services.mule_engine.rules_engine import MuleRulesEngine


class MuleIntelligenceService:
    """Core evaluation engine for money-mule account detection."""

    def __init__(self, classifier: Optional[MuleMLClassifier] = None):
        self.classifier = classifier or get_mule_classifier()

    @staticmethod
    def map_risk_band_and_action(score: float) -> tuple[MuleRiskBand, MuleAction]:
        """Map numeric score to risk band and recommended disposition."""
        if score >= 0.85:
            return MuleRiskBand.CRITICAL, MuleAction.FREEZE_SUSPEND
        elif score >= 0.60:
            return MuleRiskBand.HIGH, MuleAction.STEP_UP_KYC
        elif score >= 0.30:
            return MuleRiskBand.MEDIUM, MuleAction.MONITOR
        return MuleRiskBand.LOW, MuleAction.ALLOW

    async def evaluate_account(self, req: MuleEvaluationRequest) -> MuleEvaluationResponse:
        """Evaluate an account's mule risk based on transaction stream and account profile."""
        now = datetime.now(timezone.utc)
        warnings: List[str] = []

        if len(req.transactions) < 3:
            warnings.append("Sparse transaction sequence (< 3 transactions); behavioral signals have higher uncertainty.")

        if req.account_age_days is None:
            warnings.append("Account tenure is unknown; dormancy-burst and age-decay features estimated.")

        if req.historical_avg_daily_volume is None:
            warnings.append("Historical baseline daily volume missing; using cohort default.")

        # 1. Extract 19 behavioral features
        features = MuleFeatureExtractor.extract_features(
            account_id=req.account_id,
            transactions=req.transactions,
            account_age_days=req.account_age_days,
            historical_avg_daily_volume=req.historical_avg_daily_volume,
            current_balance=req.current_balance,
            linked_vpa_count=req.linked_vpa_count,
            has_registry_match=req.has_registry_match,
        )

        # 2. Evaluate transparent baseline rules
        rules_score, rule_hits = MuleRulesEngine.evaluate(features)

        # 3. Predict via supervised ML model if trained artifact exists
        ml_score = self.classifier.predict_score(features)
        is_calibrated = False

        if ml_score is not None:
            # Corroborate ML probability with rules engine, ensuring confirmed rule violations are not diluted
            hybrid_score = round(0.55 * ml_score + 0.45 * rules_score, 3)
            final_score = max(rules_score, hybrid_score) if rules_score >= 0.60 else hybrid_score
            is_calibrated = True
            model_mode = "ensemble_hybrid"
        else:
            final_score = rules_score
            model_mode = "baseline_rules_only"

        risk_band, recommended_action = self.map_risk_band_and_action(final_score)


        return MuleEvaluationResponse(
            account_id=req.account_id,
            evaluated_at=now,
            risk_score=final_score,
            risk_band=risk_band,
            recommended_action=recommended_action,
            rules_engine_score=rules_score,
            ml_model_score=ml_score,
            is_calibrated=is_calibrated,
            top_contributing_rules=rule_hits[:5],
            extracted_features=features,
            model_metadata={
                "model_version": self.classifier.version,
                "model_mode": model_mode,
                "feature_pipeline_version": "mule_features_v1.0.0",
                "features_extracted_count": 19,
            },
            data_quality_warnings=warnings,
        )

    async def evaluate_batch(self, req: BatchMuleEvaluationRequest) -> BatchMuleEvaluationResponse:
        """Batch evaluate accounts."""
        now = datetime.now(timezone.utc)
        evaluations: List[MuleEvaluationResponse] = []
        high_risk_count = 0

        for acc_req in req.accounts:
            res = await self.evaluate_account(acc_req)
            if res.risk_band in (MuleRiskBand.HIGH, MuleRiskBand.CRITICAL):
                high_risk_count += 1
            evaluations.append(res)

        return BatchMuleEvaluationResponse(
            evaluated_at=now,
            total_accounts=len(evaluations),
            high_risk_count=high_risk_count,
            evaluations=evaluations,
        )

    @staticmethod
    def get_evaluation_metrics() -> Dict[str, Any]:
        """Fetch latest offline model evaluation report."""
        if METRICS_PATH.exists():
            try:
                with open(METRICS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "status": "baseline_operational",
            "message": "Model evaluation report available after running synthetic benchmark training.",
            "supported_features": 19,
        }


# Global instance
mule_intelligence_service = MuleIntelligenceService()


def get_mule_intelligence_service() -> MuleIntelligenceService:
    """Dependency provider."""
    return mule_intelligence_service
