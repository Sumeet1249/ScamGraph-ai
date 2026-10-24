"""Canonical Full-Journey Schema for Multi-Stage Longitudinal Fraud Tracks.

Encodes the complete temporal and cross-channel scam lifecycle from initial lure to exit/loss.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id
from packages.schemas.events import Event


class JourneyOutcome(str, Enum):
    """The terminal or current outcome of a scam journey."""
    ONGOING_GROOMING = "ONGOING_GROOMING"
    PREVENTED_BEFORE_LOSS = "PREVENTED_BEFORE_LOSS"
    INTERRUPTED_MID_JOURNEY = "INTERRUPTED_MID_JOURNEY"
    INITIAL_LOSS_OCCURRED = "INITIAL_LOSS_OCCURRED"
    MAJOR_LOSS_OCCURRED = "MAJOR_LOSS_OCCURRED"
    RESCUE_RECOVERY_STARTED = "RESCUE_RECOVERY_STARTED"
    ABANDONED_BY_SCAMMER = "ABANDONED_BY_SCAMMER"
    FALSE_ALARM_BENIGN = "FALSE_ALARM_BENIGN"


class ScamJourneyRecord(BaseModel):
    """Complete end-to-end representation of a scam encounter across multiple touchpoints."""
    journey_id: str = Field(default_factory=lambda: generate_id("jrn"), description="Canonical journey ID")
    incident_id: str = Field(..., description="Correlated incident ID")
    schema_version: str = Field(default="2.0")
    
    scam_family: str = Field(..., description="fake_kyc, electricity, investment_trading, job_task, digital_arrest")
    channels_involved: List[str] = Field(default_factory=list, description="SMS, WHATSAPP, TELEGRAM, UPI, WEB, CALL")
    
    # Chronological progression
    ordered_events: List[Event] = Field(default_factory=list, description="Sequence of all cross-channel events")
    first_contact_event_id: Optional[str] = Field(default=None)
    credential_harvest_event_id: Optional[str] = Field(default=None)
    initial_payment_event_id: Optional[str] = Field(default=None)
    major_loss_event_id: Optional[str] = Field(default=None)
    
    # Financial impact
    total_loss_inr: float = Field(default=0.0, ge=0.0)
    loss_prevented_inr: float = Field(default=0.0, ge=0.0)
    outcome: JourneyOutcome = Field(default=JourneyOutcome.ONGOING_GROOMING)
    
    # Entities and intelligence links
    associated_entities: List[str] = Field(default_factory=list, description="Entity IDs observed across journey")
    associated_campaign_ids: List[str] = Field(default_factory=list)
    tactics_observed: List[str] = Field(default_factory=list)
    
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
