"""Dedicated Analysis Endpoints (Step 16).

Provides POST /api/v1/analyze/url for deep infrastructure and safety intelligence.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from services.api.app.repository import get_incident_repository
from services.investigation.url_analysis.service import url_investigation_service

router = APIRouter()


class AnalyzeURLRequest(BaseModel):
    incident_id: str = Field(..., description="Target Incident ID to attach resulting evidence")
    url: str = Field(..., description="Web URL to investigate")


class AnalyzeURLResponse(BaseModel):
    investigation_id: str
    status: str
    normalized_url: Optional[str] = None
    features: Optional[Dict[str, Any]] = None
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


@router.post("/url", response_model=AnalyzeURLResponse)
async def analyze_url(req: AnalyzeURLRequest):
    """Safely normalizes and inspects a URL, extracting DNS, RDAP, TLS, and lexical features.
    
    Enforces strict SSRF protection: targets resolving to loopback, private RFC1918,
    or cloud metadata endpoints are rejected before network transmission.
    """
    from services.api.app.api.v1.endpoints.incidents import _INCIDENTS_METADATA, _INCIDENT_SIGNALS
    from services.api.app.domain.models import Incident
    from datetime import datetime, timezone

    repo = get_incident_repository()
    incident = await repo.get_incident(req.incident_id)
    if not incident and req.incident_id in _INCIDENTS_METADATA:
        meta = _INCIDENTS_METADATA[req.incident_id]
        now = datetime.now(timezone.utc)
        incident = Incident(
            id=req.incident_id,
            created_at=meta.get("created_at", now),
            updated_at=meta.get("created_at", now),
            title=meta.get("metadata", {}).get("title", f"Incident {req.incident_id}"),
            metadata=meta,
        )
        await repo.create_incident(incident)

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{req.incident_id}' not found.",
        )

    try:
        inv_result = await url_investigation_service.investigate_url(
            incident_id=req.incident_id,
            raw_url=req.url,
        )

        # Attach resulting evidence to Incident in repository and session metadata
        for ev in inv_result.evidence:
            await repo.add_evidence(req.incident_id, ev)
            if req.incident_id in _INCIDENTS_METADATA:
                _INCIDENTS_METADATA[req.incident_id].setdefault("evidence", []).append(ev.model_dump())

        return AnalyzeURLResponse(
            investigation_id=inv_result.investigation_id,
            status=inv_result.status,
            normalized_url=inv_result.normalized_url.normalized_url if inv_result.normalized_url else None,
            features=inv_result.features.model_dump() if inv_result.features else None,
            entities=[e.model_dump() for e in inv_result.entities],
            evidence=[e.model_dump() for e in inv_result.evidence],
            errors=inv_result.errors,
        )
    except Exception as e:
        # Never expose raw exception stack traces to external callers
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"URL investigation could not be completed: {str(e)}",
        )
