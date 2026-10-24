"""FastAPI Endpoints for Unified ScamGraph Risk Engine (Module D).

Provides multi-signal orchestration, correlation-aware fusion, and explainable recommendations.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from packages.schemas.unified_risk import (
    UnifiedRiskRequest,
    UnifiedRiskResponse,
)
from services.risk_engine.unified_engine import (
    UnifiedScamGraphRiskEngine,
    get_unified_risk_engine,
)

router = APIRouter()


@router.post("/unified-assessment", response_model=UnifiedRiskResponse)
async def perform_unified_assessment(
    req: UnifiedRiskRequest,
    engine: UnifiedScamGraphRiskEngine = Depends(get_unified_risk_engine),
):
    """Perform multi-signal fraud risk synthesis across Smart Registry, Mule Intelligence, Graph Correlation, and Semantic NLP."""
    try:
        return await engine.assess(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error performing unified assessment: {str(e)}",
        )
