"""Intelligence Console V2 schemas (Prompt 19 / Phase 6A)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class AlertType(str, Enum):
    """Operational alert types emitted by campaign and outbreak engines."""
    OUTBREAK = "OUTBREAK"
    RAPID_GROWTH = "RAPID_GROWTH"
    RESURGENCE = "RESURGENCE"
    EMERGING_CAMPAIGN = "EMERGING_CAMPAIGN"
    NEW_VARIANT = "NEW_VARIANT"
    HIGH_RISK_PAYMENT_NETWORK = "HIGH_RISK_PAYMENT_NETWORK"


class AlertStatus(str, Enum):
    """Workflow state of an operational threat alert."""
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ReviewType(str, Enum):
    """Categories of items in the human-in-the-loop analyst review queue."""
    ENTITY_MERGE = "ENTITY_MERGE"
    ENTITY_SPLIT = "ENTITY_SPLIT"
    CORRELATION = "CORRELATION"
    CAMPAIGN_MEMBERSHIP = "CAMPAIGN_MEMBERSHIP"
    CAMPAIGN_MERGE = "CAMPAIGN_MERGE"
    CAMPAIGN_SPLIT = "CAMPAIGN_SPLIT"
    NOVEL_VARIANT = "NOVEL_VARIANT"
    LOW_CONFIDENCE_EXTRACTION = "LOW_CONFIDENCE_EXTRACTION"
    OUTBREAK_CANDIDATE = "OUTBREAK_CANDIDATE"


class ReviewDecisionType(str, Enum):
    """Decision outcomes made by authorized fraud analysts."""
    CONFIRM = "CONFIRM"
    REJECT = "REJECT"
    UNCERTAIN = "UNCERTAIN"
    DEFER = "DEFER"


class CaseStatus(str, Enum):
    """Status of an operational investigation case."""
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    WAITING = "WAITING"
    RESOLVED = "RESOLVED"
    ARCHIVED = "ARCHIVED"


# -----------------------------------------------------------------------------
# DTOs
# -----------------------------------------------------------------------------

class IntelligenceAlert(BaseModel):
    """Actionable operational alert for analyst triage."""
    alert_id: str = Field(default_factory=lambda: generate_id("alt"))
    alert_type: AlertType
    severity: str = Field(default="HIGH", description="CRITICAL, HIGH, MEDIUM, LOW")
    title: str
    description: str
    campaign_id: Optional[str] = None
    campaign_name: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    status: AlertStatus = Field(default=AlertStatus.NEW)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReviewQueueItem(BaseModel):
    """Item requiring human-in-the-loop analyst judgment."""
    review_id: str = Field(default_factory=lambda: generate_id("rev"))
    review_type: ReviewType
    priority_score: float = Field(ge=0.0, le=1.0, default=0.75)
    title: str
    summary: str
    evidence_context: Dict[str, Any] = Field(default_factory=dict)
    candidate_entities: List[str] = Field(default_factory=list)
    candidate_campaign_ids: List[str] = Field(default_factory=list)
    status: str = Field(default="PENDING", description="PENDING, REVIEWED")
    decision: Optional[ReviewDecisionType] = None
    reviewer_notes: Optional[str] = None
    reviewer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decided_at: Optional[datetime] = None


class InvestigationCase(BaseModel):
    """Lightweight case management entity grouping multi-incident intelligence."""
    case_id: str = Field(default_factory=lambda: generate_id("case"))
    title: str
    status: CaseStatus = Field(default=CaseStatus.OPEN)
    priority: str = Field(default="HIGH", description="CRITICAL, HIGH, MEDIUM, LOW")
    assigned_analyst: Optional[str] = None
    linked_incident_ids: List[str] = Field(default_factory=list)
    linked_campaign_ids: List[str] = Field(default_factory=list)
    linked_entities: List[str] = Field(default_factory=list)
    notes: List[Dict[str, Any]] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SystemIntelligenceHealth(BaseModel):
    """Lightweight operational health state of intelligence subsystems."""
    knowledge_graph: str = "HEALTHY"
    campaign_discovery_engine: str = "HEALTHY"
    outbreak_radar: str = "HEALTHY"
    multimodal_processor: str = "HEALTHY"
    language_intelligence: str = "HEALTHY"
    degraded_components: List[str] = Field(default_factory=list)


class CommandCenterSummary(BaseModel):
    """Aggregated operational dashboard summary payload."""
    time_window: str = "24h"
    active_alerts_count: int = 0
    surging_campaigns_count: int = 0
    emerging_campaigns_count: int = 0
    pending_reviews_count: int = 0
    open_cases_count: int = 0
    alerts: List[IntelligenceAlert] = Field(default_factory=list)
    surging_campaigns: List[Dict[str, Any]] = Field(default_factory=list)
    emerging_campaigns: List[Dict[str, Any]] = Field(default_factory=list)
    review_queue: List[ReviewQueueItem] = Field(default_factory=list)
    health: SystemIntelligenceHealth = Field(default_factory=SystemIntelligenceHealth)
    recent_network_activity: List[Dict[str, Any]] = Field(default_factory=list)
