"""Canonical Incident Schema for ScamGraph AI V2.

Represents an ongoing or completed investigation session linking events, artifacts, entities,
evidence signals, and risk assessments.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import ConfidenceLevelV2, RiskLevelV2, UrgencyLevelV2, generate_id


class IncidentStatus(str, Enum):
    """Lifecycle state machine for scam incidents."""
    OPEN = "OPEN"
    ANALYZING = "ANALYZING"
    ASSESSMENT_READY = "ASSESSMENT_READY"
    MONITORING = "MONITORING"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class Incident(BaseModel):
    """Canonical Incident contract representing an end-to-end scam journey encounter."""
    incident_id: str = Field(default_factory=lambda: generate_id("inc"), description="Stable opaque incident ID")
    schema_version: str = Field(default="2.0", description="Contract schema version")
    status: IncidentStatus = Field(default=IncidentStatus.OPEN, description="Current lifecycle state")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    first_observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Decoupled entity / event references (scalable persistence)
    event_ids: List[str] = Field(default_factory=list, description="IDs of chronological interaction events")
    artifact_ids: List[str] = Field(default_factory=list, description="IDs of ingested raw artifacts")
    entity_ids: List[str] = Field(default_factory=list, description="IDs of resolved entities in this incident")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of extracted EvidenceSignals")
    
    # Multi-dimensional risk and manipulation metrics
    current_risk: RiskLevelV2 = Field(default=RiskLevelV2.UNKNOWN)
    current_confidence: ConfidenceLevelV2 = Field(default=ConfidenceLevelV2.UNKNOWN)
    current_urgency: UrgencyLevelV2 = Field(default=UrgencyLevelV2.NONE)
    
    # Intelligence links
    likely_scam_family: Optional[str] = Field(default=None, description="Inferred scam typology (e.g. fake_kyc, digital_arrest)")
    journey_id: Optional[str] = Field(default=None, description="Linked Journey ID if active in Journey Engine")
    campaign_ids: List[str] = Field(default_factory=list, description="Clustered campaign IDs if correlated")
    
    # Context
    user_context: Dict[str, Any] = Field(default_factory=dict, description="Pseudonymized victim or session context")
    source_context: Dict[str, Any] = Field(default_factory=dict, description="Reporting channel or integration origin")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary extensible metadata")
