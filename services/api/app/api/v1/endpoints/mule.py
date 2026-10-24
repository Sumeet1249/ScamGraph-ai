"""FastAPI Endpoints for Mule Intelligence Engine (Module B).

Exposes single-account evaluation, batch scoring, rules directory, and model metrics.
"""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from packages.schemas.mule import (
    BatchMuleEvaluationRequest,
    BatchMuleEvaluationResponse,
    MuleEvaluationRequest,
    MuleEvaluationResponse,
)
from services.mule_engine.service import (
    MuleIntelligenceService,
    get_mule_intelligence_service,
)

router = APIRouter()


@router.post("/evaluate", response_model=MuleEvaluationResponse)
async def evaluate_account_mule_risk(
    req: MuleEvaluationRequest,
    service: MuleIntelligenceService = Depends(get_mule_intelligence_service),
):
    """Evaluate an account's recent transaction stream across 19 behavioral patterns for mule risk."""
    try:
        return await service.evaluate_account(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to evaluate account: {str(e)}",
        )


@router.post("/batch-evaluate", response_model=BatchMuleEvaluationResponse)
async def batch_evaluate_accounts(
    req: BatchMuleEvaluationRequest,
    service: MuleIntelligenceService = Depends(get_mule_intelligence_service),
):
    """Batch evaluate multiple accounts for mule indicators."""
    try:
        return await service.evaluate_batch(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed batch evaluation: {str(e)}",
        )


@router.get("/metrics")
async def get_model_evaluation_metrics(
    service: MuleIntelligenceService = Depends(get_mule_intelligence_service),
):
    """Retrieve model performance metrics, confusion matrix, PR-AUC, and feature importances."""
    return service.get_evaluation_metrics()


@router.get("/rules")
async def list_mule_behavioral_rules():
    """List the 19 behavioral patterns and active heuristic rules."""
    return {
        "total_rules": 10,
        "total_features": 19,
        "rules": [
            {"rule_id": "RULE_VELOCITY_BURST_1H", "name": "1-Hour Velocity Burst", "threshold": ">= 5 txns/hr"},
            {"rule_id": "RULE_FULL_VOLUME_TURNOVER", "name": "Complete Turnover Churn", "threshold": "0.85 <= debit/credit <= 1.15"},
            {"rule_id": "RULE_RAPID_PASS_THROUGH", "name": "Rapid Pass-Through Dwell Time", "threshold": "dwell_time <= 300s or churn >= 50%"},
            {"rule_id": "RULE_FAN_IN_CONVERGENCE", "name": "Multi-Source Fan-In", "threshold": "unique senders >= 3"},
            {"rule_id": "RULE_FAN_OUT_DISPERSAL", "name": "Layering Fan-Out Dispersal", "threshold": "unique recipients >= 3"},
            {"rule_id": "RULE_NEW_ACCOUNT_BURST", "name": "New Account Burst", "threshold": "age <= 30 days and burst >= 5x"},
            {"rule_id": "RULE_ZERO_BALANCE_EXTRACTION", "name": "Immediate Balance Depletion", "threshold": "balance exit ratio >= 70%"},
            {"rule_id": "RULE_STRUCTURING_CHUNKING", "name": "Threshold Skimming / Round Chunking", "threshold": "₹9,999 / ₹49,999 / 10k multiples"},
            {"rule_id": "RULE_MICRO_TEST_SPIKE", "name": "Micro-Test Inflow Spike", "threshold": "Micro credit (<=10) + immediate large credit"},
            {"rule_id": "RULE_REGISTRY_CONFIRMED_HIT", "name": "Smart Registry Confirmed Hit", "threshold": "Confirmed report in central registry"},
        ],
    }
