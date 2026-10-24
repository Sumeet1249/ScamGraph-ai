"""Contextual Intervention & Pre-Payment Guard REST Endpoints (Phase 4B / Prompt 14)."""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from packages.schemas.contextual_intervention import (
    InterventionDecision,
    InterventionFeedback,
    PaymentProximity,
    PaymentReason,
    PrePaymentContext,
    UserResponseAction,
)
from services.intervention_engine.service import (
    GuardEvaluationResult,
    contextual_intervention_service,
    pre_payment_guard_service,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class EvaluateInterventionRequest(BaseModel):
    incident_id: str = Field(..., description="Target incident ID")
    message_text: Optional[str] = Field(None, description="Raw message or SMS body")
    url: Optional[str] = Field(None, description="Suspect URL")
    vpa: Optional[str] = Field(None, description="Destination VPA")
    phone: Optional[str] = Field(None, description="Sender phone number")
    journey_stage: str = Field(default="INITIAL_CONTACT")
    payment_proximity: PaymentProximity = Field(default=PaymentProximity.NONE)
    payment_reason: PaymentReason = Field(default=PaymentReason.UNKNOWN)
    tactics_observed: List[str] = Field(default_factory=list)
    claimed_org: Optional[str] = Field(None)
    already_paid: bool = Field(default=False)
    lang: str = Field(default="en")


class FeedbackSubmissionRequest(BaseModel):
    user_response: UserResponseAction
    dispute_reason: Optional[str] = None


@router.post("/evaluate", response_model=InterventionDecision)
async def evaluate_intervention(req: EvaluateInterventionRequest) -> InterventionDecision:
    """Evaluates contextual intervention decision for an interaction."""
    try:
        return contextual_intervention_service.evaluate_from_signals(
            incident_id=req.incident_id,
            message_text=req.message_text,
            url=req.url,
            vpa=req.vpa,
            phone=req.phone,
            journey_stage=req.journey_stage,
            payment_proximity=req.payment_proximity,
            payment_reason=req.payment_reason,
            tactics_observed=req.tactics_observed,
            claimed_org=req.claimed_org,
            already_paid=req.already_paid,
            lang=req.lang,
        )
    except Exception as e:
        logger.exception("Failed evaluating contextual intervention: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{incident_id}", response_model=InterventionDecision)
async def get_incident_intervention(
    incident_id: str,
    lang: str = Query("en", description="Target language: en, hi, hinglish"),
) -> InterventionDecision:
    """Retrieves or re-evaluates intervention for an existing incident."""
    try:
        # Default fallback evaluation for the incident ID
        return contextual_intervention_service.evaluate_from_signals(
            incident_id=incident_id,
            lang=lang,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{incident_id}/feedback")
async def submit_intervention_feedback(
    incident_id: str,
    feedback_req: FeedbackSubmissionRequest,
) -> Dict[str, Any]:
    """Records user action (verify, trust, pause, already paid) on an intervention."""
    try:
        fb = InterventionFeedback(
            incident_id=incident_id,
            intervention_id=f"intv_{incident_id}",
            user_response=feedback_req.user_response,
            dispute_reason=feedback_req.dispute_reason,
        )
        return contextual_intervention_service.record_feedback(incident_id, fb)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Payment Guard Router ──
payment_guard_router = APIRouter()


@payment_guard_router.post("/check", response_model=GuardEvaluationResult)
async def check_pre_payment(
    req: PrePaymentContext,
    lang: str = Query("en", description="Target language: en, hi, hinglish"),
) -> GuardEvaluationResult:
    """ScamGraph Guard: evaluates pre-payment context to protect user before authorizing transfer."""
    try:
        return pre_payment_guard_service.check_payment(req, lang=lang)
    except Exception as e:
        logger.exception("Failed pre-payment guard check: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
