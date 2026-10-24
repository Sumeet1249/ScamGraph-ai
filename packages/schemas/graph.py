"""Cytoscape.js Graph Schemas for ScamGraph AI.

Provides standard serialization structures for rendering directed Scam Journey
Graphs and Infrastructure Networks directly in the Cytoscape.js canvas.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GraphNodeType(str, Enum):
    INCIDENT = "incident"
    JOURNEY_STEP = "journey_step"
    MESSAGE = "message"
    URL = "url"
    DOMAIN = "domain"
    IP = "ip"
    ASN = "asn"
    PHONE = "phone"
    UPI_HANDLE = "upi_handle"
    BANK_ACCOUNT = "bank_account"
    CAMPAIGN = "campaign"


class CytoscapeNodeData(BaseModel):
    id: str
    label: str
    node_type: GraphNodeType
    severity: Optional[str] = None
    subtext: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class CytoscapeEdgeData(BaseModel):
    id: str
    source: str
    target: str
    label: str
    relationship_type: str
    time_delta_seconds: Optional[int] = None
    confidence: Optional[float] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class CytoscapeNode(BaseModel):
    data: CytoscapeNodeData
    classes: Optional[str] = None


class CytoscapeEdge(BaseModel):
    data: CytoscapeEdgeData
    classes: Optional[str] = None


class CytoscapeGraph(BaseModel):
    """Complete graph container compatible with Cytoscape.js elements."""
    nodes: List[CytoscapeNode] = Field(default_factory=list)
    edges: List[CytoscapeEdge] = Field(default_factory=list)
