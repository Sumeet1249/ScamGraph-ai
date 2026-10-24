"""Dual-Axis Assessment and Adaptive Intervention Schemas.

Strict Rule: Risk Level and Evidence Confidence remain separate values.
The system explicitly supports INSUFFICIENT_EVIDENCE.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from packages.schemas.signals import EvidenceSignal, SignalDimension


class RiskLevel(str, Enum):
    """Calibrated severity of harm."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class EvidenceConfidence(str, Enum):
    """Degree of multi-signal corroboration across independent dimensions."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EmergingStatus(str, Enum):
    """Mutation and campaign classification."""
    KNOWN_PATTERN = "KNOWN_PATTERN"
    MUTATED_VARIANT = "MUTATED_VARIANT"
    POSSIBLE_EMERGING_CAMPAIGN = "POSSIBLE_EMERGING_CAMPAIGN"
    NO_SIGNIFICANT_MATCH = "NO_SIGNIFICANT_MATCH"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class InterventionAction(str, Enum):
    """Graded intervention friction to combat alert fatigue."""
    NONE = "NONE"
    PASSIVE = "PASSIVE"
    CAUTION = "CAUTION"
    STRONG_WARNING = "STRONG_WARNING"
    PRE_PAYMENT_INTERVENTION = "PRE_PAYMENT_INTERVENTION"


class AdaptiveIntervention(BaseModel):
    """Contextual friction recommendation."""
    action: InterventionAction
    friction_delay_seconds: int = Field(default=0, ge=0, description="Mandatory step-up countdown friction (e.g. 10s)")
    banner_title: Optional[str] = None
    banner_message: Optional[str] = None
    action_button_text: Optional[str] = None
    dismissible: bool = True


class ExplainabilityReport(BaseModel):
    """Enforces the 7 essential answers for auditability and transparency."""
    what_happened: str = Field(..., description="Summary of the observed user journey")
    why_suspicious: str = Field(..., description="Concrete contradictions or anomalies observed")
    when_risk_increased: str = Field(..., description="The turning point in the chronological timeline")
    which_evidence_supports: List[str] = Field(default_factory=list, description="Summary of supporting signals")
    which_sources_produced: List[str] = Field(default_factory=list, description="Detector or provider provenance")
    what_counter_evidence_exists: List[str] = Field(default_factory=list, description="Indicators pointing to safety/legitimacy")
    how_confident: str = Field(..., description="Explanation of confidence level / corroboration breadth")
    what_to_do_next: str = Field(..., description="Clear, actionable safe guidance for the user")


class AssessmentResult(BaseModel):
    """The authoritative evaluated outcome for an incident."""
    assessment_id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str
    risk_level: RiskLevel
    evidence_confidence: EvidenceConfidence
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Normalized risk score (0.0 - 1.0)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Multi-source corroboration score (0.0 - 1.0)")
    is_insufficient_evidence: bool = Field(default=False)
    emerging_status: EmergingStatus = Field(default=EmergingStatus.KNOWN_PATTERN)
    detected_pattern_name: Optional[str] = Field(default=None)
    campaign_id: Optional[str] = Field(default=None)
    corroborated_dimensions: List[SignalDimension] = Field(default_factory=list)
    signals: List[EvidenceSignal] = Field(default_factory=list)
    counter_evidence: List[EvidenceSignal] = Field(default_factory=list)
    intervention: AdaptiveIntervention
    explainability: ExplainabilityReport
    is_simulated: bool = Field(default=False, description="Watermark flag for synthetic/demonstration scenarios")
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
