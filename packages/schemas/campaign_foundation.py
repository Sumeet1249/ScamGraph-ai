"""Canonical Campaign Foundation Schema for Threat Intelligence and Cluster Discovery."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class CampaignVelocity(str, Enum):
    """Growth rate and propagation velocity of a scam campaign."""
    EMERGING = "EMERGING"       # Newly observed (1-5 incidents)
    SURGING = "SURGING"         # Rapidly accelerating outbreak (>5 incidents/hour)
    STABLE = "STABLE"           # Persistent low-velocity operation
    SUBSIDING = "SUBSIDING"     # Takedown or campaign exhaustion in progress
    DORMANT = "DORMANT"         # No new activity for >14 days


class CampaignRecord(BaseModel):
    """A cluster of coordinated incidents sharing underlying infrastructure, templates, or tactics."""
    campaign_id: str = Field(default_factory=lambda: generate_id("cmp"))
    name: str = Field(..., description="Human-friendly threat label (e.g. 'Oct-2026 SBI KYC Smishing Ring')")
    scam_family: str = Field(..., description="Primary typology (e.g. job_task, digital_arrest, fake_kyc)")
    
    # Active State
    velocity: CampaignVelocity = Field(default=CampaignVelocity.EMERGING)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    incident_count: int = Field(default=1, ge=1)
    
    # Shared Infrastructure & Breadcrumbs
    shared_entities: List[str] = Field(default_factory=list, description="Entity IDs shared across incidents")
    shared_templates: List[str] = Field(default_factory=list, description="Template cluster signatures")
    shared_domains: List[str] = Field(default_factory=list)
    shared_vpas: List[str] = Field(default_factory=list)
    
    # Geographic & Linguistic Distribution
    languages: List[str] = Field(default_factory=list)
    channels: List[str] = Field(default_factory=list)
    target_regions: List[str] = Field(default_factory=list, description="States/circles (e.g. Delhi-NCR, Maharashtra)")
    
    # Timeline
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Plain Language Threat Advisory
    consumer_advisory: str = Field(default="", description="Who is targeted, how it begins, what to avoid")
    metadata: Dict[str, Any] = Field(default_factory=dict)
