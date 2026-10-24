"""Scam Journey Graph Schemas for ScamGraph AI.

Represents the multi-stage psychological grooming and payment progression.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from packages.schemas.signals import EvidenceSignal


class JourneyStage(str, Enum):
    """Recognized stages in the digital finance scam progression."""
    INITIAL_CONTACT = "INITIAL_CONTACT"
    IMPERSONATION = "IMPERSONATION"
    URGENCY_PRESSURE = "URGENCY_PRESSURE"
    SUSPICIOUS_LINK = "SUSPICIOUS_LINK"
    CREDENTIAL_OTP_HARVEST = "CREDENTIAL_OTP_HARVEST"
    PAYMENT_REQUEST = "PAYMENT_REQUEST"
    PAYMENT_INTENT = "PAYMENT_INTENT"
    UNKNOWN = "UNKNOWN"


class JourneyStep(BaseModel):
    """An individual step along the scam progression timeline."""
    step_id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str
    sequence: int = Field(..., ge=1, description="Order within this journey")
    stage: JourneyStage
    title: str = Field(..., description="Short summary of this step")
    description: str = Field(..., description="Detailed narrative of user/attacker action")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    time_delta_seconds: Optional[int] = Field(default=None, description="Seconds elapsed since preceding step")
    associated_signals: List[EvidenceSignal] = Field(default_factory=list)


class NextStepPrediction(BaseModel):
    """Anticipates the attacker's likely next move on the grooming ladder."""
    current_stage: JourneyStage
    predicted_next_stage: JourneyStage
    rationale: str
    recommended_preventive_action: str


class ScamJourney(BaseModel):
    """Complete reconstructed scam journey."""
    journey_id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str
    session_id: str
    current_stage: JourneyStage = Field(default=JourneyStage.INITIAL_CONTACT)
    steps: List[JourneyStep] = Field(default_factory=list)
    total_pace_seconds: int = Field(default=0, description="Total elapsed seconds from first to last step")
    prediction: Optional[NextStepPrediction] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
