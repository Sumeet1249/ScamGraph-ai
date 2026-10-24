"""Canonical Scam Journey Engine V1 Schemas for ScamGraph AI V2.

Encodes multi-stage psychological grooming, temporal reasoning, stage observations,
monetization status, progress metrics, and pre-loss early warning candidates.
"""

from datetime import datetime, timezone
from enum import Enum
import hashlib
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id
from packages.schemas.signals import EvidenceSignal


class JourneyStage(str, Enum):
    """Universal Journey Stage Ontology (15 canonical stages + legacy backwards-compatible aliases)."""
    # 15 Canonical Stages
    DISCOVERY = "DISCOVERY"                                 # Initial advertisement, job post, social lure
    CONTACT = "CONTACT"                                     # Inbound outreach, SMS, WhatsApp cold message, phone call
    TRUST_BUILDING = "TRUST_BUILDING"                       # Small task reward, friendly onboarding, ISO certificate
    IMPERSONATION = "IMPERSONATION"                         # Law enforcement, courier, discom, bank officer disguise
    PLATFORM_MIGRATION = "PLATFORM_MIGRATION"               # Moving victim from marketplace/ad to Telegram/WhatsApp
    URGENCY = "URGENCY"                                     # Artificial deadline ("within 2 hours", "account blocking")
    CREDENTIAL_REQUEST = "CREDENTIAL_REQUEST"               # Demanding OTP, ATM PIN, netbanking password
    INITIAL_PAYMENT = "INITIAL_PAYMENT"                     # Small deposit, registration fee, verification transfer
    REWARD_OR_FAKE_PROFIT = "REWARD_OR_FAKE_PROFIT"         # Fake wallet balance credit, screenshot of profit
    PAYMENT_ESCALATION = "PAYMENT_ESCALATION"               # Demanding larger deposit (₹5k -> ₹25k -> ₹1L)
    WITHDRAWAL_BLOCK = "WITHDRAWAL_BLOCK"                   # "System error: 30% tax required before withdrawal"
    RECOVERY_FEE = "RECOVERY_FEE"                           # Fee demanded to unfreeze or release previous money
    THREAT_OR_PRESSURE = "THREAT_OR_PRESSURE"               # Blackmail, CBI raid threat, legal defamation
    EXIT = "EXIT"                                           # Victim cut off, channels blocked, money extracted
    UNKNOWN = "UNKNOWN"

    # Legacy Backwards-Compatible Aliases
    INITIAL_CONTACT = "CONTACT"
    URGENCY_PRESSURE = "URGENCY"
    SUSPICIOUS_LINK = "DISCOVERY"
    CREDENTIAL_OTP_HARVEST = "CREDENTIAL_REQUEST"
    PAYMENT_REQUEST = "INITIAL_PAYMENT"
    PAYMENT_INTENT = "INITIAL_PAYMENT"


class StageCategory(str, Enum):
    """Coarse-grained lifecycle phase groupings."""
    PRE_MONETIZATION = "PRE_MONETIZATION"       # DISCOVERY, CONTACT, TRUST_BUILDING, IMPERSONATION, PLATFORM_MIGRATION, URGENCY, CREDENTIAL_REQUEST
    MONETIZATION = "MONETIZATION"               # INITIAL_PAYMENT, PAYMENT_ESCALATION, RECOVERY_FEE
    REINFORCEMENT = "REINFORCEMENT"             # REWARD_OR_FAKE_PROFIT
    CONTROL_RETENTION = "CONTROL_RETENTION"     # WITHDRAWAL_BLOCK, THREAT_OR_PRESSURE
    TERMINATION = "TERMINATION"                 # EXIT
    UNKNOWN = "UNKNOWN"


def get_stage_category(stage: JourneyStage) -> StageCategory:
    """Classifies a journey stage into its coarse-grained lifecycle grouping."""
    pre_monetization = {
        JourneyStage.DISCOVERY,
        JourneyStage.CONTACT,
        JourneyStage.TRUST_BUILDING,
        JourneyStage.IMPERSONATION,
        JourneyStage.PLATFORM_MIGRATION,
        JourneyStage.URGENCY,
        JourneyStage.CREDENTIAL_REQUEST,
    }
    monetization = {
        JourneyStage.INITIAL_PAYMENT,
        JourneyStage.PAYMENT_ESCALATION,
        JourneyStage.RECOVERY_FEE,
    }
    reinforcement = {
        JourneyStage.REWARD_OR_FAKE_PROFIT,
    }
    control_retention = {
        JourneyStage.WITHDRAWAL_BLOCK,
        JourneyStage.THREAT_OR_PRESSURE,
    }
    termination = {
        JourneyStage.EXIT,
    }

    if stage in pre_monetization:
        return StageCategory.PRE_MONETIZATION
    elif stage in monetization:
        return StageCategory.MONETIZATION
    elif stage in reinforcement:
        return StageCategory.REINFORCEMENT
    elif stage in control_retention:
        return StageCategory.CONTROL_RETENTION
    elif stage in termination:
        return StageCategory.TERMINATION
    return StageCategory.UNKNOWN


class MonetizationStatus(str, Enum):
    """Explicit payment lifecycle status within a journey."""
    NO_PAYMENT_SIGNAL = "NO_PAYMENT_SIGNAL"
    PAYMENT_HINT = "PAYMENT_HINT"
    PAYMENT_REQUESTED = "PAYMENT_REQUESTED"
    PAYMENT_INITIATED = "PAYMENT_INITIATED"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    MULTIPLE_PAYMENTS = "MULTIPLE_PAYMENTS"
    ADDITIONAL_PAYMENT_REQUESTED = "ADDITIONAL_PAYMENT_REQUESTED"
    UNKNOWN = "UNKNOWN"


class LossStatus(str, Enum):
    """Categorization of financial damage incurred by the victim."""
    NO_KNOWN_LOSS = "NO_KNOWN_LOSS"
    AT_RISK = "AT_RISK"
    POSSIBLE_LOSS = "POSSIBLE_LOSS"
    CONFIRMED_USER_REPORTED_LOSS = "CONFIRMED_USER_REPORTED_LOSS"
    UNKNOWN = "UNKNOWN"


class JourneyEvent(BaseModel):
    """An individual ordered event contributing evidence to the scam journey."""
    event_id: str = Field(default_factory=lambda: generate_id("jrev"))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sequence_number: int = Field(default=0, ge=0)
    event_type: str = Field(..., description="MESSAGE_RECEIVED, PAYMENT_REQUESTED, LINK_CLICKED, APP_INSTALLED")
    artifact_ids: List[str] = Field(default_factory=list)
    channel: str = Field(default="UNKNOWN", description="WHATSAPP, TELEGRAM, SMS, UPI, CALL, WEB")
    speaker_role: str = Field(default="UNKNOWN", description="SCAMMER, VICTIM, AUTHORITY")
    entities: List[str] = Field(default_factory=list, description="Associated Entity IDs")
    tactics: List[str] = Field(default_factory=list, description="Tactic names detected in event")
    requested_actions: List[str] = Field(default_factory=list)
    payment_context: Dict[str, Any] = Field(default_factory=dict)
    stage_candidates: List[JourneyStage] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    timestamp_confidence: str = Field(default="EXACT", description="EXACT, APPROXIMATE, ORDER_ONLY, UNKNOWN")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StageObservation(BaseModel):
    """Evidence-grounded observation of a specific journey stage."""
    observation_id: str = Field(default_factory=lambda: generate_id("stgob"))
    stage: JourneyStage
    category: StageCategory = Field(default=StageCategory.UNKNOWN)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    event_ids: List[str] = Field(default_factory=list)
    supporting_signals: List[str] = Field(default_factory=list)
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    detector_sources: List[str] = Field(default_factory=lambda: ["RULE"])
    reason_codes: List[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if self.category == StageCategory.UNKNOWN:
            self.category = get_stage_category(self.stage)


class EarlyWarningCandidate(BaseModel):
    """Proactive early warning generated before major financial loss occurs."""
    warning_id: str = Field(default_factory=lambda: generate_id("warn"))
    warning_type: str = Field(
        ...,
        description="MANIPULATION_ESCALATION, PAYMENT_RISK, CREDENTIAL_RISK, REMOTE_ACCESS_RISK, AUTHORITY_IMPERSONATION_RISK, RECOVERY_FEE_RISK, MULTI_STAGE_SCAM_PATTERN"
    )
    trigger_event_id: Optional[str] = Field(default=None)
    current_stage: JourneyStage = Field(default=JourneyStage.UNKNOWN)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)
    recommended_intervention_class: str = Field(
        default="WARNING",
        description="INFORMATION, CAUTION, WARNING, STRONG_WARNING, IMMEDIATE_PAUSE"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JourneyProgress(BaseModel):
    """Multi-dimensional progress intelligence for consumer and analyst tracking."""
    current_phase: StageCategory = Field(default=StageCategory.PRE_MONETIZATION)
    monetization_proximity: float = Field(default=0.0, ge=0.0, le=1.0, description="0.0=pre-lure, 1.0=payment demanded")
    loss_proximity: float = Field(default=0.0, ge=0.0, le=1.0, description="0.0=safe, 1.0=irreversible loss imminent")
    escalation_level: str = Field(default="LOW", description="LOW, MEDIUM, HIGH, CRITICAL")
    evidence_completeness: float = Field(default=0.5, ge=0.0, le=1.0)
    display_stage: str = Field(default="Initial Contact")
    completed_steps: List[str] = Field(default_factory=list)
    current_step: str = Field(default="Contact")
    possible_future_steps: List[str] = Field(default_factory=list)


class JourneyFeatureVector(BaseModel):
    """Privacy-safe structural feature vector for future ScamDNA and cross-incident correlation."""
    stage_sequence: List[str] = Field(default_factory=list)
    tactic_vector: Dict[str, float] = Field(default_factory=dict)
    channel_sequence: List[str] = Field(default_factory=list)
    requested_action_sequence: List[str] = Field(default_factory=list)
    monetization_velocity: float = Field(default=0.0)
    family_distribution: Dict[str, float] = Field(default_factory=dict)
    event_count: int = Field(default=0)
    total_duration_seconds: float = Field(default=0.0)


class ConsumerJourneyView(BaseModel):
    """Consumer-friendly plain-language explanation of scam journey progression."""
    likely_family: str
    progress_label: str
    what_happened: List[str]
    why_this_matters: str
    recommended_action: str
    warning_level: str
    progress_meter: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Canonical ScamJourney & Legacy Compatibility
# ---------------------------------------------------------------------------

class JourneyStep(BaseModel):
    """Legacy V1 Step representation for backwards compatibility."""
    step_id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str = Field(default="")
    sequence: int = Field(default=1, ge=1)
    stage: JourneyStage = Field(default=JourneyStage.CONTACT)
    title: str = Field(default="")
    description: str = Field(default="")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    time_delta_seconds: Optional[int] = Field(default=None)
    associated_signals: List[EvidenceSignal] = Field(default_factory=list)


class NextStepPrediction(BaseModel):
    """Legacy V1 Prediction representation for backwards compatibility."""
    current_stage: JourneyStage = Field(default=JourneyStage.CONTACT)
    predicted_next_stage: JourneyStage = Field(default=JourneyStage.UNKNOWN)
    rationale: str = Field(default="")
    recommended_preventive_action: str = Field(default="")


class ScamJourney(BaseModel):
    """Canonical reconstructed scam journey in ScamGraph AI V2."""
    journey_id: str = Field(default_factory=lambda: generate_id("jrn"))
    schema_version: str = Field(default="2.0")
    incident_id: str
    session_id: Optional[str] = Field(default=None)
    
    # Classification & Hypotheses
    scam_family: str = Field(default="UNKNOWN", description="JOB_TASK, INVESTMENT, DIGITAL_ARREST, KYC_BANK, FAKE_SUPPORT_REFUND, UNKNOWN")
    family_hypotheses: Dict[str, float] = Field(default_factory=dict, description="Probabilities across scam families")
    
    # Chronological Events & Stage Observations
    events: List[JourneyEvent] = Field(default_factory=list)
    stage_observations: List[StageObservation] = Field(default_factory=list)
    current_stage: JourneyStage = Field(default=JourneyStage.CONTACT)
    current_stage_confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    stage_history: List[JourneyStage] = Field(default_factory=list)
    
    # Financial Monetization & Loss Intelligence
    monetization_status: MonetizationStatus = Field(default=MonetizationStatus.NO_PAYMENT_SIGNAL)
    loss_status: LossStatus = Field(default=LossStatus.NO_KNOWN_LOSS)
    monetization_boundary_event_id: Optional[str] = Field(default=None)
    first_actionable_warning_event_id: Optional[str] = Field(default=None)
    first_actionable_warning_timestamp: Optional[datetime] = Field(default=None)
    major_loss_event_id: Optional[str] = Field(default=None)
    major_loss_timestamp: Optional[datetime] = Field(default=None)
    warning_lead_time_seconds: Optional[float] = Field(default=None, description="T_loss - T_warning lead time")
    pre_loss_warning_issued: bool = Field(default=False)
    
    # Multi-dimensional Progress
    progress: Optional[JourneyProgress] = Field(default=None)
    
    # Context Aggregations
    tactics: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    channels: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    early_warnings: List[EarlyWarningCandidate] = Field(default_factory=list)
    
    # Temporal Bounds
    first_observed_at: Optional[datetime] = Field(default=None)
    last_observed_at: Optional[datetime] = Field(default=None)
    
    # Legacy V1 Compatibility fields
    steps: List[JourneyStep] = Field(default_factory=list)
    total_pace_seconds: int = Field(default=0)
    prediction: Optional[NextStepPrediction] = Field(default=None)
    
    engine_version: str = Field(default="2.0.0")
    degraded: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)
