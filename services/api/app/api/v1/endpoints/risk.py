"""FastAPI Endpoints for Unified ScamGraph Risk & Decision Engine (Phase 4A).

Provides tripartite risk calibration (Risk + Confidence + Urgency),
action-ready dispositions (EDUCATE, WARN, STRONG_WARNING, DELAY_PAYMENT, BLOCK_PRE_LOSS),
and multi-engine signal attribution.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from packages.schemas.unified_decision import (
    ActionDecision,
    TripartiteDecision,
)
from packages.schemas.unified_risk import (
    UnifiedRiskRequest,
    UnifiedRiskResponse,
)
from services.decision_engine.service import (
    UnifiedDecisionService,
    unified_decision_service,
)
from services.risk_engine.unified_engine import (
    UnifiedScamGraphRiskEngine,
    get_unified_risk_engine,
)

router = APIRouter()


class DecisionEvaluateRequest(BaseModel):
    incident_id: Optional[str] = None
    message_text: Optional[str] = Field(None, description="Raw message text (SMS, WhatsApp, email)")
    url: Optional[str] = Field(None, description="Suspicious URL or link")
    vpa: Optional[str] = Field(None, description="UPI VPA (e.g. user@oksbi)")
    phone: Optional[str] = Field(None, description="Sender phone number")
    journey_stage: Optional[str] = Field(None, description="Current scam journey stage")
    tactics_observed: List[str] = Field(default_factory=list, description="Observed manipulation tactics")
    known_dna_similarity: Optional[float] = Field(None, ge=0.0, le=1.0)
    entity_trust_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    counter_evidence_signals: List[str] = Field(default_factory=list)


@router.post("/decision", response_model=TripartiteDecision)
async def evaluate_tripartite_decision(
    req: DecisionEvaluateRequest,
    service: UnifiedDecisionService = Depends(lambda: unified_decision_service),
):
    """Phase 4A: Unified Tripartite Risk + Confidence + Urgency evaluation and action layer."""
    try:
        return service.evaluate(
            incident_id=req.incident_id,
            message_text=req.message_text,
            url=req.url,
            vpa=req.vpa,
            phone=req.phone,
            journey_stage=req.journey_stage,
            tactics_observed=req.tactics_observed,
            known_dna_similarity=req.known_dna_similarity,
            entity_trust_score=req.entity_trust_score,
            counter_evidence_signals=req.counter_evidence_signals,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision evaluation failed: {str(e)}",
        )


@router.get("/decision/{incident_id}", response_model=TripartiteDecision)
async def get_incident_decision(
    incident_id: str,
    service: UnifiedDecisionService = Depends(lambda: unified_decision_service),
):
    """Retrieve or compute TripartiteDecision for a specific active incident session."""
    from services.api.app.api.v1.endpoints.incidents import _INCIDENT_EVENTS, _INCIDENTS_METADATA
    events = _INCIDENT_EVENTS.get(incident_id, [])
    metadata = _INCIDENTS_METADATA.get(incident_id, {})

    # Extract observed fields
    text = None
    url = None
    vpa = None
    phone = None
    for ev in events:
        p = ev.payload if isinstance(ev.payload, dict) else (ev.payload.model_dump() if hasattr(ev.payload, "model_dump") else {})
        if "text" in p:
            text = p["text"]
        if "raw_url" in p or "url" in p:
            url = p.get("raw_url") or p.get("url")
        if "vpa" in p:
            vpa = p["vpa"]
        if "sender_id" in p:
            phone = p["sender_id"]

    return service.evaluate(
        incident_id=incident_id,
        message_text=text or metadata.get("message_text"),
        url=url or metadata.get("url"),
        vpa=vpa or metadata.get("vpa"),
        phone=phone or metadata.get("phone"),
        journey_stage=metadata.get("journey_stage"),
        tactics_observed=metadata.get("tactics", []),
    )


# -----------------------------------------------------------------------------
# Legacy Module D Compatibility Endpoint
# -----------------------------------------------------------------------------
@router.post("/unified-assessment", response_model=UnifiedRiskResponse)
async def perform_unified_assessment(
    req: UnifiedRiskRequest,
    engine: UnifiedScamGraphRiskEngine = Depends(get_unified_risk_engine),
):
    """Legacy Module D: Perform multi-signal fraud risk synthesis."""
    try:
        return await engine.assess(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error performing unified assessment: {str(e)}",
        )
