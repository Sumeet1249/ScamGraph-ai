"""Graph domain models, node types, relationship types, and provenance for Neo4j Evidence Graph.

Conforms to ScamGraph Graph Intelligence V1 specifications.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class GraphNodeType(str, Enum):
    """Canonical node labels in the Neo4j Evidence Graph."""

    INCIDENT = "Incident"
    PHONE = "Phone"
    URL = "URL"
    DOMAIN = "Domain"
    IP = "IP"
    ASN = "ASN"
    BRAND = "Brand"
    PAYMENT_ENTITY = "PaymentEntity"
    CERTIFICATE = "Certificate"
    NAMESERVER = "Nameserver"
    PATTERN = "Pattern"
    CAMPAIGN = "Campaign"


class GraphRelationshipType(str, Enum):
    """Canonical relationship types connecting nodes."""

    OBSERVED = "OBSERVED"
    HOSTED_ON = "HOSTED_ON"
    RESOLVES_TO = "RESOLVES_TO"
    BELONGS_TO = "BELONGS_TO"
    USES_CERTIFICATE = "USES_CERTIFICATE"
    USES_NAMESERVER = "USES_NAMESERVER"
    IMPERSONATES = "IMPERSONATES"
    REQUESTS_PAYMENT_TO = "REQUESTS_PAYMENT_TO"
    MATCHES_PATTERN = "MATCHES_PATTERN"
    PART_OF = "PART_OF"


@dataclass
class RelationshipProvenance:
    """Provenance tracking for every graph relationship.

    Strict Rule: Never create unexplained graph relationships.
    """

    evidence_ids: List[str] = field(default_factory=list)
    confidence: float = 1.0
    first_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "investigation_pipeline"
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Flatten properties into top-level for Neo4j edge properties
        props = d.pop("properties", {})
        d.update(props)
        return d


@dataclass
class IncidentNode:
    """Represents an :Incident node."""

    id: str
    channel: str = "UNKNOWN"
    status: str = "ACTIVE"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    risk_score: Optional[float] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GraphEntityNode:
    """Represents an atomic entity node with normalized value and display value."""

    node_type: GraphNodeType
    normalized_value: str
    display_value: str
    properties: Dict[str, Any] = field(default_factory=dict)
    first_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def id(self) -> str:
        """Normalized value serves as primary key."""
        return self.normalized_value

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": self.normalized_value,
            "normalized_value": self.normalized_value,
            "display_value": self.display_value,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
        }
        if isinstance(self.properties, dict):
            d.update(self.properties)
        elif self.properties:
            d["value"] = str(self.properties)
        return d


@dataclass
class GraphSyncResult:
    """Result of synchronizing an incident and its evidence to the graph."""

    status: str  # "SUCCESS", "DEGRADED", "UNAVAILABLE"
    incident_id: str
    nodes_synced: int = 0
    relationships_synced: int = 0
    shared_entities: Dict[str, Any] = field(default_factory=dict)
    related_incidents: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GraphCorrelationResult:
    """Rich correlation result with structural similarity, paths, and explanations."""

    related_incident_id: str
    graph_similarity: float
    shared_entities: List[Dict[str, Any]] = field(default_factory=list)
    relationship_paths: List[str] = field(default_factory=list)
    community_id: Optional[str] = None
    evidence_ids: List[str] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
