"""Contextual Intervention and Pre-Payment Guard Schemas (Phase 4B / Prompt 14).

Defines authoritative types for anti-manipulation intervention, progressive friction,
pre-payment guard context, independent verification plans, and fatigue management.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class InterventionType(str, Enum):
    """Categorical intervention actions decided by ScamGraph."""
    NO_ACTION = "NO_ACTION"
    EDUCATE = "EDUCATE"
    VERIFY_INDEPENDENTLY = "VERIFY_INDEPENDENTLY"
    CAUTION = "CAUTION"
    WARN = "WARN"
    STRONG_WARNING = "STRONG_WARNING"
    PAUSE_AND_VERIFY = "PAUSE_AND_VERIFY"
    DELAY_PAYMENT = "DELAY_PAYMENT"
    DO_NOT_SHARE_CREDENTIALS = "DO_NOT_SHARE_CREDENTIALS"
    DO_NOT_SHARE_OTP = "DO_NOT_SHARE_OTP"
    DO_NOT_INSTALL_REMOTE_ACCESS = "DO_NOT_INSTALL_REMOTE_ACCESS"
    TALK_TO_TRUSTED_PERSON = "TALK_TO_TRUSTED_PERSON"
    BREAK_CONTACT_AND_VERIFY = "BREAK_CONTACT_AND_VERIFY"
    EMERGENCY_RESPONSE = "EMERGENCY_RESPONSE"


class FrictionLevel(str, Enum):
    """Progressive friction tiers (0: None, 6: Emergency)."""
    NONE = "NONE"                     # Level 0
    PASSIVE = "PASSIVE"               # Level 1: In-line banner
    LIGHT = "LIGHT"                   # Level 2: Dismissible advisory
    MODERATE = "MODERATE"             # Level 3: Modal warning
    STRONG = "STRONG"                 # Level 4: Interactive pause & acknowledge
    DELAY_PAYMENT = "DELAY_PAYMENT"   # Level 5: Mandatory cooling-off countdown
    EMERGENCY = "EMERGENCY"           # Level 6: Post-loss emergency handoff


class PaymentReason(str, Enum):
    """Purported or stated reason for transferring funds."""
    PURCHASE = "PURCHASE"
    FAMILY_OR_FRIEND = "FAMILY_OR_FRIEND"
    RENT = "RENT"
    BILL = "BILL"
    INVESTMENT = "INVESTMENT"
    JOB_OR_TASK = "JOB_OR_TASK"
    LOAN_OR_FEE = "LOAN_OR_FEE"
    GOVERNMENT_OR_FINE = "GOVERNMENT_OR_FINE"
    COURIER_OR_CUSTOMS = "COURIER_OR_CUSTOMS"
    REFUND_OR_SUPPORT = "REFUND_OR_SUPPORT"
    VERIFICATION_OR_KYC = "VERIFICATION_OR_KYC"
    UNKNOWN = "UNKNOWN"


class PaymentProximity(str, Enum):
    """Victim temporal proximity to financial execution."""
    NONE = "NONE"
    DISTANT = "DISTANT"
    APPROACHING = "APPROACHING"
    IMMINENT = "IMMINENT"
    REQUESTED = "REQUESTED"
    PAYMENT_OBSERVED = "PAYMENT_OBSERVED"
    POST_PAYMENT = "POST_PAYMENT"


class InterventionTiming(str, Enum):
    """When the intervention must be displayed."""
    NOW = "NOW"
    BEFORE_NEXT_ACTION = "BEFORE_NEXT_ACTION"
    BEFORE_PAYMENT = "BEFORE_PAYMENT"
    BEFORE_CREDENTIAL_SHARE = "BEFORE_CREDENTIAL_SHARE"
    POST_PAYMENT = "POST_PAYMENT"
    BACKGROUND_EDUCATION = "BACKGROUND_EDUCATION"


class UserResponseAction(str, Enum):
    """User response to an intervention."""
    VERIFY = "VERIFY"
    I_TRUST_THIS = "I_TRUST_THIS"
    NOT_SURE = "NOT_SURE"
    STOPPED_PAYMENT = "STOPPED_PAYMENT"
    ALREADY_PAID = "ALREADY_PAID"
    TALKED_TO_SOMEONE = "TALKED_TO_SOMEONE"
    CONTINUED = "CONTINUED"


class VerificationPlan(BaseModel):
    """Structured guidance on how to verify legitimacy without suspect-supplied channels."""
    plan_id: str = Field(default_factory=lambda: generate_id("verplan"))
    verification_type: str = Field(..., description="BANK_DIRECT, EMPLOYER_HR, OFFICIAL_PORTAL, COURIER_DIRECT, POLICE_STATION")
    target_type: str = Field(..., description="FINANCIAL_INSTITUTION, GOVERNMENT_AGENCY, EMPLOYER, MARKETPLACE")
    trusted_source_required: str = Field(..., description="E.g. Bank passbook phone, official .gov.in portal")
    steps: List[str] = Field(default_factory=list, description="Step-by-step verification instructions")
    reason: str = Field(..., description="Why this verification method protects the user")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PrePaymentContext(BaseModel):
    """Input payload for ScamGraph Guard evaluating pre-payment risk context."""
    incident_id: str = Field(..., description="Associated incident ID")
    payment_intent: bool = Field(default=True, description="True if victim intends to pay")
    payment_reason: PaymentReason = Field(default=PaymentReason.UNKNOWN)
    amount_inr: Optional[float] = Field(default=None, ge=0.0)
    amount_band: Optional[str] = Field(default=None, description="MICRO (<500), LOW (500-2k), MID (2k-10k), HIGH (>10k)")
    recipient_entity_id: Optional[str] = Field(default=None)
    recipient_vpa: Optional[str] = Field(default=None)
    recipient_verification_state: Optional[str] = Field(default="UNVERIFIED", description="VERIFIED_MERCHANT, UNVERIFIED, SUSPICIOUS, MULE_FLAGGED")
    journey_stage: str = Field(default="PAYMENT_REQUEST")
    payment_proximity: PaymentProximity = Field(default=PaymentProximity.REQUESTED)
    requested_action: Optional[str] = Field(default="UPI_TRANSFER")
    tactics_present: List[str] = Field(default_factory=list)
    scam_dna_family: Optional[str] = Field(default=None)
    campaign_id: Optional[str] = Field(default=None)
    is_campaign_outbreak: bool = Field(default=False)
    already_paid: bool = Field(default=False)
    user_context_flags: Dict[str, Any] = Field(default_factory=dict)
    assessment_id: Optional[str] = Field(default=None)


class InterventionDecision(BaseModel):
    """Canonical decision object emitted by the Contextual Intervention Engine."""
    intervention_id: str = Field(default_factory=lambda: generate_id("intv"))
    schema_version: str = Field(default="2.0.0")
    subject_type: str = Field(default="INCIDENT", description="INCIDENT, TRANSACTION, SESSION")
    subject_id: str = Field(..., description="ID of the incident or session")
    assessment_id: Optional[str] = Field(default=None)

    # Core Intervention Directive
    intervention_type: InterventionType = Field(..., description="Primary protective action")
    secondary_interventions: List[InterventionType] = Field(default_factory=list, description="Supplemental protective actions")
    priority: str = Field(default="HIGH", description="LOW, MEDIUM, HIGH, CRITICAL, EMERGENCY")
    severity: str = Field(default="HIGH", description="LOW, MEDIUM, HIGH, CRITICAL")
    trigger_reason_codes: List[str] = Field(default_factory=list)

    # Tripartite Anchors
    risk: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    urgency: float = Field(..., ge=0.0, le=1.0)

    # Contextual State
    journey_stage: str = Field(default="INITIAL_CONTACT")
    payment_proximity: PaymentProximity = Field(default=PaymentProximity.NONE)
    requested_action: Optional[str] = Field(default=None)
    campaign_context: Optional[Dict[str, Any]] = Field(default=None)
    network_context: Optional[Dict[str, Any]] = Field(default=None)

    # Consumer Presentation & Message Catalog
    message_key: str = Field(..., description="Catalog key for multilingual localization")
    consumer_headline: str = Field(...)
    consumer_message: str = Field(...)
    recommended_steps: List[str] = Field(default_factory=list)
    verification_plan: Optional[VerificationPlan] = Field(default=None)

    # Progressive Friction & Timing
    friction_level: FrictionLevel = Field(default=FrictionLevel.MODERATE)
    timing: InterventionTiming = Field(default=InterventionTiming.NOW)
    suggested_cooling_off_minutes: int = Field(default=0, ge=0)

    # Governance & Metadata
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    policy_version: str = Field(default="4.2.0")
    engine_version: str = Field(default="contextual_intervention_v2")
    degraded: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InterventionFeedback(BaseModel):
    """User feedback or response to an intervention."""
    incident_id: str
    intervention_id: str
    user_response: UserResponseAction
    dispute_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
