"""Campaigns endpoint for cross-incident clustering and campaign graph visualization."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from packages.schemas import (
    CytoscapeGraph,
    CytoscapeNode,
    CytoscapeNodeData,
    CytoscapeEdge,
    CytoscapeEdgeData,
    GraphNodeType,
)
from datetime import datetime, timezone

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


# Demo Campaign data representing realistic clusters discovered across incidents
DEMO_CAMPAIGNS: Dict[str, Dict[str, Any]] = {
    "camp_kyc_syndicate": {
        "id": "camp_kyc_syndicate",
        "name": "State Bank Impersonation & OTP Harvest Syndicate",
        "pattern_type": "KYC_IMPERSONATION",
        "severity": "CRITICAL",
        "incidents_count": 14,
        "shared_infrastructure_count": 6,
        "first_seen": datetime(2026, 10, 15, 8, 30, tzinfo=timezone.utc),
        "last_seen": datetime(2026, 10, 20, 17, 45, tzinfo=timezone.utc),
        "tactics": ["ACCOUNT_SUSPENSION_FEAR", "OFFICIAL_IMPERSONATION", "TYPOSQUAT_URL", "OTP_HARVEST", "MICRO_COLLECT"],
        "sample_domain": "sbi-kyc-verify-portal.online",
        "sample_vpa": "scammer.ops@oksbi",
        "nodes": [
            {"id": "camp_root", "label": "Campaign: SBI Syndicate", "type": GraphNodeType.CAMPAIGN, "severity": "CRITICAL"},
            {"id": "dom_1", "label": "sbi-kyc-verify-portal.online", "type": GraphNodeType.DOMAIN, "severity": "HIGH"},
            {"id": "ip_1", "label": "194.168.10.45", "type": GraphNodeType.IP, "severity": "MEDIUM"},
            {"id": "vpa_1", "label": "scammer.ops@oksbi", "type": GraphNodeType.UPI_HANDLE, "severity": "HIGH"},
            {"id": "phone_1", "label": "+919111111111", "type": GraphNodeType.PHONE, "severity": "HIGH"},
            {"id": "inc_1", "label": "Incident #1041 (Mumbai)", "type": GraphNodeType.INCIDENT, "severity": "CRITICAL"},
            {"id": "inc_2", "label": "Incident #1048 (Delhi)", "type": GraphNodeType.INCIDENT, "severity": "CRITICAL"},
            {"id": "inc_3", "label": "Incident #1059 (Bengaluru)", "type": GraphNodeType.INCIDENT, "severity": "HIGH"},
        ],
        "edges": [
            {"source": "camp_root", "target": "dom_1", "label": "CONTROLS"},
            {"source": "camp_root", "target": "vpa_1", "label": "COLLECTS_VIA"},
            {"source": "camp_root", "target": "phone_1", "label": "OUTREACH_FROM"},
            {"source": "dom_1", "target": "ip_1", "label": "RESOLVES_TO"},
            {"source": "inc_1", "target": "dom_1", "label": "VISITED_URL"},
            {"source": "inc_1", "target": "vpa_1", "label": "PAID_TO"},
            {"source": "inc_2", "target": "phone_1", "label": "CONTACTED_BY"},
            {"source": "inc_2", "target": "dom_1", "label": "VISITED_URL"},
            {"source": "inc_3", "target": "vpa_1", "label": "TARGETED_BY"},
        ]
    },
    "camp_task_part_time": {
        "id": "camp_task_part_time",
        "name": "E-Commerce Rating & Telegram Task Fraud",
        "pattern_type": "PART_TIME_JOB_FRAUD",
        "severity": "HIGH",
        "incidents_count": 8,
        "shared_infrastructure_count": 4,
        "first_seen": datetime(2026, 10, 18, 11, 0, tzinfo=timezone.utc),
        "last_seen": datetime(2026, 10, 20, 20, 15, tzinfo=timezone.utc),
        "tactics": ["TELEGRAM_ONBOARDING", "DAILY_GUARANTEED_RETURNS", "VIP_TASK_DEPOSIT"],
        "sample_domain": "task-earning-hub.xyz",
        "sample_vpa": "vip.task@paytm",
        "nodes": [
            {"id": "camp_root", "label": "Campaign: Task Fraud Network", "type": GraphNodeType.CAMPAIGN, "severity": "HIGH"},
            {"id": "dom_2", "label": "task-earning-hub.xyz", "type": GraphNodeType.DOMAIN, "severity": "HIGH"},
            {"id": "vpa_2", "label": "vip.task@paytm", "type": GraphNodeType.UPI_HANDLE, "severity": "HIGH"},
            {"id": "inc_4", "label": "Incident #1062", "type": GraphNodeType.INCIDENT, "severity": "HIGH"},
            {"id": "inc_5", "label": "Incident #1071", "type": GraphNodeType.INCIDENT, "severity": "HIGH"},
        ],
        "edges": [
            {"source": "camp_root", "target": "dom_2", "label": "CONTROLS"},
            {"source": "camp_root", "target": "vpa_2", "label": "COLLECTS_VIA"},
            {"source": "inc_4", "target": "dom_2", "label": "VISITED_URL"},
            {"source": "inc_5", "target": "vpa_2", "label": "PAID_TO"},
        ]
    }
}


@router.get("", response_model=List[CampaignSummary])
async def list_campaigns():
    """Retrieve aggregated campaigns discovered across incidents."""
    summaries = []
    for c in DEMO_CAMPAIGNS.values():
        summaries.append(
            CampaignSummary(
                id=c["id"],
                name=c["name"],
                pattern_type=c["pattern_type"],
                severity=c["severity"],
                incidents_count=c["incidents_count"],
                shared_infrastructure_count=c["shared_infrastructure_count"],
                first_seen=c["first_seen"],
                last_seen=c["last_seen"],
                tactics=c["tactics"],
                sample_domain=c.get("sample_domain"),
                sample_vpa=c.get("sample_vpa"),
            )
        )
    return summaries


@router.get("/{campaign_id}/graph", response_model=CytoscapeGraph)
async def get_campaign_graph(campaign_id: str):
    """Retrieve the multi-incident campaign correlation graph for Cytoscape.js canvas."""
    camp = DEMO_CAMPAIGNS.get(campaign_id)
    if not camp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Campaign '{campaign_id}' not found.")

    nodes: List[CytoscapeNode] = []
    for n in camp["nodes"]:
        nodes.append(
            CytoscapeNode(
                data=CytoscapeNodeData(
                    id=n["id"],
                    label=n["label"],
                    node_type=n["type"],
                    severity=n.get("severity", "INFO"),
                )
            )
        )

    edges: List[CytoscapeEdge] = []
    for idx, e in enumerate(camp["edges"]):
        edges.append(
            CytoscapeEdge(
                data=CytoscapeEdgeData(
                    id=f"e_{campaign_id}_{idx}",
                    source=e["source"],
                    target=e["target"],
                    label=e["label"],
                    relationship_type=e["label"],
                )
            )
        )

    return CytoscapeGraph(nodes=nodes, edges=edges)
