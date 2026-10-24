"""Graph Correlation Engine Schemas (Module C).

Defines typed nodes, typed edges, path exploration contracts, cluster summaries,
and explainable risk propagation models.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CorrelationNodeType(str, Enum):
    ACCOUNT = "ACCOUNT"
    UPI_VPA = "UPI_VPA"
    PHONE = "PHONE"
    DEVICE = "DEVICE"
    IP = "IP"
    URL_DOMAIN = "URL_DOMAIN"
    TRANSACTION = "TRANSACTION"
    REPORT = "REPORT"
    INCIDENT = "INCIDENT"
    CASE = "CASE"


class CorrelationEdgeType(str, Enum):
    SENT_TO = "SENT_TO"
    RECEIVED_FROM = "RECEIVED_FROM"
    USES_IDENTIFIER = "USES_IDENTIFIER"
    USED_DEVICE = "USED_DEVICE"
    ACCESSED_FROM = "ACCESSED_FROM"
    LINKED_TO_REPORT = "LINKED_TO_REPORT"
    INVOLVED_IN_INCIDENT = "INVOLVED_IN_INCIDENT"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"


class GraphNode(BaseModel):
    """A node in the correlation graph."""
    id: str
    node_type: CorrelationNodeType
    label: str
    risk_score: float = 0.0
    direct_risk: float = 0.0
    propagated_risk: float = 0.0
    is_disputed: bool = False
    is_revoked: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """A directed edge in the correlation graph preserving provenance and temporal data."""
    id: str
    source_id: str
    target_id: str
    relationship_type: CorrelationEdgeType
    amount: Optional[float] = None
    timestamp: Optional[datetime] = None
    confidence: float = 1.0
    is_inferred: bool = False
    is_valid: bool = True
    transaction_id: Optional[str] = None
    report_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# Path Analysis Schemas
# -----------------------------------------------------------------------------

class PathQueryRequest(BaseModel):
    """Request to trace money flows and multi-hop paths."""
    source_id: str
    target_id: Optional[str] = None
    max_depth: int = Field(default=4, ge=1, le=5)
    min_amount: Optional[float] = Field(None, ge=0.0)
    time_window_hours: Optional[int] = Field(default=72, ge=1, le=720)
    limit: int = Field(default=20, ge=1, le=50)


class TransactionHop(BaseModel):
    """Individual transfer step along a transaction path."""
    from_account: str
    to_account: str
    amount: float
    timestamp: Optional[datetime] = None
    txn_id: Optional[str] = None
    dwell_time_seconds: Optional[float] = None


class TransactionPath(BaseModel):
    """A reconstructed flow path across accounts."""
    path_id: str
    hop_count: int
    total_amount: float
    is_circular: bool = False
    nodes: List[str]
    hops: List[TransactionHop]
    min_dwell_time_seconds: Optional[float] = None
    explanation: str


class PathQueryResponse(BaseModel):
    """Response containing discovered transaction paths."""
    source_id: str
    paths_found: int
    circular_flows_detected: bool
    paths: List[TransactionPath]


# -----------------------------------------------------------------------------
# Cluster Detection Schemas
# -----------------------------------------------------------------------------

class ClusterSummary(BaseModel):
    """A suspicious cluster or connected component."""
    cluster_id: str
    cluster_type: str  # CONNECTED_COMPONENT, SHARED_IDENTIFIER_RING, LAYER_DISPERSAL
    node_count: int
    edge_count: int
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    suspicion_score: float
    reason: str
    time_window: Optional[str] = None
    related_report_ids: List[str] = Field(default_factory=list)


class ClusterQueryRequest(BaseModel):
    """Request to detect suspicious graph clusters."""
    min_cluster_size: int = Field(default=2, ge=2, le=50)
    include_dormant: bool = False
    limit: int = Field(default=20, ge=1, le=50)


class ClusterQueryResponse(BaseModel):
    """Response containing suspicious clusters."""
    total_clusters: int
    clusters: List[ClusterSummary]


# -----------------------------------------------------------------------------
# Risk Propagation Schemas
# -----------------------------------------------------------------------------

class RiskPropagationRequest(BaseModel):
    """Request to propagate risk from seed entities with distance decay."""
    seed_node_ids: List[str] = Field(..., min_length=1)
    decay_factor: float = Field(default=0.5, ge=0.1, le=0.9, description="Geometric decay factor per hop (lambda)")
    max_hops: int = Field(default=3, ge=1, le=4)
    temporal_half_life_days: float = Field(default=30.0, ge=1.0)


class PropagatedNodeRisk(BaseModel):
    """Risk calculation details for an affected node."""
    node_id: str
    node_type: CorrelationNodeType
    hops_from_seed: int
    direct_risk: float
    propagated_risk: float
    total_risk: float
    contributing_seed_ids: List[str]
    path_explanation: List[str]


class RiskPropagationResponse(BaseModel):
    """Results of transparent risk propagation."""
    evaluated_at: datetime
    decay_factor_used: float
    seeds_processed: int
    affected_nodes_count: int
    nodes: List[PropagatedNodeRisk]
