"""Campaign Intelligence V2 Schemas (Phase 3C - Sections 6-10, 63-70).

Provides typed contracts for multi-signal scam campaigns, lifecycle transitions,
membership records, mutation tracking, and merge/split proposals.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CampaignLifecycleState(str, Enum):
    """Lifecycle state of a scam campaign."""
    CANDIDATE = "CANDIDATE"
    EMERGING = "EMERGING"
    ACTIVE = "ACTIVE"
    SURGING = "SURGING"
    OUTBREAK = "OUTBREAK"
    DECLINING = "DECLINING"
    DORMANT = "DORMANT"
    RESURGING = "RESURGING"
    CLOSED = "CLOSED"
    DISPUTED = "DISPUTED"


class CampaignVelocityState(str, Enum):
    """Activity and report acceleration tier relative to baseline."""
    NORMAL = "NORMAL"
    RISING = "RISING"
    SURGING = "SURGING"
    OUTBREAK = "OUTBREAK"


class CampaignReviewState(str, Enum):
    """Analyst review and acknowledgement state (never criminal accusation)."""
    UNREVIEWED = "UNREVIEWED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    CONFIRMED_PATTERN = "CONFIRMED_PATTERN"
    DISMISSED = "DISMISSED"
    MONITORING = "MONITORING"


class CampaignMembership(BaseModel):
    """Membership record linking an incident to a campaign."""
    incident_id: str
    campaign_id: str
    membership_score: float = Field(default=0.85, ge=0.0, le=1.0)
    confidence: float = Field(default=0.80, ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)
    first_assigned: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_evaluated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = "3.3.0"


class ScamCampaign(BaseModel):
    """Canonical multi-dimensional scam campaign object."""
    campaign_id: str
    schema_version: str = "2.0.0"
    title: str
    scam_family: str
    family_confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    lifecycle_state: CampaignLifecycleState = CampaignLifecycleState.CANDIDATE
    velocity_state: CampaignVelocityState = CampaignVelocityState.NORMAL
    review_state: CampaignReviewState = CampaignReviewState.UNREVIEWED

    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    incident_count: int = 0
    strongly_related_incident_count: int = 0

    unique_entity_count: int = 0
    unique_payment_identifier_count: int = 0
    unique_domain_count: int = 0
    unique_phone_count: int = 0
    unique_social_account_count: int = 0

    languages: List[str] = Field(default_factory=lambda: ["English", "Hinglish"])
    channels: List[str] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)

    # Multi-dimensional profiles
    journey_profile: List[str] = Field(default_factory=list)
    dna_profile_id: Optional[str] = None
    tactic_profile: List[str] = Field(default_factory=list)
    infrastructure_profile: List[str] = Field(default_factory=list)
    payment_profile: List[str] = Field(default_factory=list)

    # Core scores
    risk_score: float = Field(default=0.75, ge=0.0, le=1.0)
    confidence: float = Field(default=0.80, ge=0.0, le=1.0)
    urgency_level: str = "HIGH"

    # Velocity metrics
    current_velocity: float = 0.0      # Reports per day
    baseline_velocity: float = 0.0     # Historical rolling baseline
    growth_multiplier: float = 1.0     # current / baseline
    acceleration: float = 0.0          # Rate of velocity change

    # Lineage & mutation tracking
    parent_campaign_id: Optional[str] = None
    merged_from: List[str] = Field(default_factory=list)
    split_from: Optional[str] = None
    superseded_by: Optional[str] = None
    mutation_count: int = 0
    active_mutations: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = "3.3.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CampaignMergeSplitProposal(BaseModel):
    """Proposal for merging strongly connected or splitting bifurcated campaigns."""
    proposal_id: str
    proposal_type: str  # "MERGE" or "SPLIT"
    source_campaign_ids: List[str]
    target_campaign_id: Optional[str] = None
    reason: str
    supporting_evidence: List[str] = Field(default_factory=list)
    status: str = "PENDING_REVIEW"  # PENDING_REVIEW, APPROVED, REJECTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
