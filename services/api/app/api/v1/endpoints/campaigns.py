"""Campaigns endpoint for Campaign Intelligence V2 and Outbreak Radar (Phase 3C)."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from packages.schemas import (
    CytoscapeEdge,
    CytoscapeEdgeData,
    CytoscapeGraph,
    CytoscapeNode,
    CytoscapeNodeData,
    GraphNodeType,
    ScamCampaign,
)
from services.campaign_engine.service import campaign_service

router = APIRouter()


class CampaignSummary(BaseModel):
    id: str
    name: str
    pattern_type: str
    severity: str
    incidents_count: int
    shared_infrastructure_count: int
    first_seen: datetime
    last_seen: datetime
    tactics: List[str]
    sample_domain: Optional[str] = None
    sample_vpa: Optional[str] = None
    lifecycle_state: Optional[str] = None
    current_velocity: Optional[float] = None
    confidence: Optional[float] = None


class MergeSplitRequest(BaseModel):
    action: str  # "MERGE" or "SPLIT"
    target_campaign_id: Optional[str] = None
    reason: str
    evidence: List[str] = Field(default_factory=list)


@router.get("", response_model=List[Dict[str, Any]])
async def list_campaigns(
    lifecycle_state: Optional[str] = None,
    family: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    demo_mode: bool = False,
):
    """Retrieve aggregated campaigns discovered across incidents."""
    # Ensure demo data is seeded if empty and requested
    if demo_mode or not campaign_service._campaigns:
        campaign_service.seed_demo_data()

    campaigns = campaign_service.list_campaigns(
        lifecycle_state=lifecycle_state,
        family=family,
        limit=limit,
        offset=offset,
    )

    results = []
    for c in campaigns:
        cdict = c.model_dump()
        # Add backward-compatible fields for legacy UI components
        cdict["id"] = c.campaign_id
        cdict["name"] = c.title
        cdict["pattern_type"] = c.scam_family
        cdict["severity"] = "CRITICAL" if c.lifecycle_state.value == "OUTBREAK" else ("HIGH" if c.lifecycle_state.value == "SURGING" else "MEDIUM")
        cdict["incidents_count"] = c.incident_count
        cdict["shared_infrastructure_count"] = c.unique_entity_count
        cdict["tactics"] = c.tactic_profile
        cdict["sample_domain"] = c.infrastructure_profile[0] if c.infrastructure_profile else None
        cdict["sample_vpa"] = c.payment_profile[0] if c.payment_profile else None
        results.append(cdict)

    return results


@router.get("/{campaign_id}", response_model=Dict[str, Any])
async def get_campaign(campaign_id: str):
    """Retrieve complete multi-dimensional ScamCampaign V2 record."""
    if not campaign_service._campaigns:
        campaign_service.seed_demo_data()

    camp = campaign_service.get_campaign(campaign_id)
    if not camp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{campaign_id}' not found.",
        )
    res = camp.model_dump()
    res["id"] = camp.campaign_id
    res["name"] = camp.title
    res["pattern_type"] = camp.scam_family
    return res


@router.get("/{campaign_id}/velocity", response_model=Dict[str, Any])
async def get_campaign_velocity(campaign_id: str):
    """Retrieve normalized velocity, acceleration, baseline, and outbreak tier."""
    if not campaign_service._campaigns:
        campaign_service.seed_demo_data()

    camp = campaign_service.get_campaign(campaign_id)
    if not camp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{campaign_id}' not found.",
        )

    return {
        "campaign_id": camp.campaign_id,
        "velocity_state": camp.velocity_state.value,
        "current_velocity_per_day": camp.current_velocity,
        "baseline_velocity_per_day": camp.baseline_velocity,
        "growth_multiplier": camp.growth_multiplier,
        "acceleration": camp.acceleration,
        "is_outbreak": (camp.velocity_state.value == "OUTBREAK"),
        "last_updated": camp.updated_at.isoformat(),
    }


@router.get("/{campaign_id}/timeline", response_model=List[Dict[str, Any]])
async def get_campaign_timeline(campaign_id: str):
    """Retrieve chronological mutations, drift, and lifecycle events for this campaign."""
    camp = campaign_service.get_campaign(campaign_id)
    if not camp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{campaign_id}' not found.",
        )

    timeline = [
        {
            "event_type": "FIRST_SEEN",
            "timestamp": camp.first_seen.isoformat(),
            "description": f"Campaign established with {camp.scam_family} pattern.",
        }
    ]

    for mut in camp.active_mutations:
        timeline.append({
            "event_type": "MUTATION_DETECTED",
            "timestamp": camp.updated_at.isoformat(),
            "description": mut,
        })

    timeline.append({
        "event_type": "LIFECYCLE_STATE",
        "timestamp": camp.updated_at.isoformat(),
        "description": f"Current status: {camp.lifecycle_state.value} ({camp.current_velocity} reports/day).",
    })

    return timeline


@router.post("/{campaign_id}/merge-split", response_model=Dict[str, Any])
async def propose_merge_split(campaign_id: str, req: MergeSplitRequest):
    """Submit an auditable proposal to merge or split campaigns."""
    if req.action.upper() == "MERGE":
        if not req.target_campaign_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="target_campaign_id required for MERGE action.",
            )
        prop = campaign_service.propose_merge(
            campaign_id,
            req.target_campaign_id,
            req.reason,
            req.evidence,
        )
        if not prop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both campaigns not found for merge.",
            )
        return prop.model_dump()

    elif req.action.upper() == "SPLIT":
        prop = campaign_service.propose_split(
            campaign_id,
            req.reason,
            req.evidence,
        )
        if not prop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign '{campaign_id}' not found for split.",
            )
        return prop.model_dump()

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown action '{req.action}'. Expected MERGE or SPLIT.",
        )


@router.get("/{campaign_id}/graph", response_model=CytoscapeGraph)
async def get_campaign_graph(campaign_id: str):
    """Retrieve the multi-incident campaign correlation graph for Cytoscape.js canvas."""
    if not campaign_service._campaigns:
        campaign_service.seed_demo_data()

    camp = campaign_service.get_campaign(campaign_id)
    if not camp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign '{campaign_id}' not found.",
        )

    nodes: List[CytoscapeNode] = [
        CytoscapeNode(
            data=CytoscapeNodeData(
                id=camp.campaign_id,
                label=camp.title,
                node_type=GraphNodeType.CAMPAIGN,
                severity="CRITICAL" if camp.lifecycle_state.value == "OUTBREAK" else "HIGH",
            )
        )
    ]
    edges: List[CytoscapeEdge] = []

    # Map infrastructure
    for idx, infra in enumerate(camp.infrastructure_profile[:6]):
        nid = f"infra_{camp.campaign_id}_{idx}"
        nodes.append(
            CytoscapeNode(
                data=CytoscapeNodeData(
                    id=nid,
                    label=infra,
                    node_type=GraphNodeType.DOMAIN if "." in infra else GraphNodeType.PHONE,
                    severity="HIGH",
                )
            )
        )
        edges.append(
            CytoscapeEdge(
                data=CytoscapeEdgeData(
                    id=f"e_infra_{idx}",
                    source=camp.campaign_id,
                    target=nid,
                    label="USES_INFRASTRUCTURE",
                    relationship_type="USES_INFRASTRUCTURE",
                )
            )
        )

    # Map payment accounts
    for idx, pay in enumerate(camp.payment_profile[:4]):
        nid = f"pay_{camp.campaign_id}_{idx}"
        nodes.append(
            CytoscapeNode(
                data=CytoscapeNodeData(
                    id=nid,
                    label=pay,
                    node_type=GraphNodeType.UPI_HANDLE,
                    severity="CRITICAL",
                )
            )
        )
        edges.append(
            CytoscapeEdge(
                data=CytoscapeEdgeData(
                    id=f"e_pay_{idx}",
                    source=camp.campaign_id,
                    target=nid,
                    label="COLLECTS_VIA",
                    relationship_type="COLLECTS_VIA",
                )
            )
        )

    return CytoscapeGraph(nodes=nodes, edges=edges)
