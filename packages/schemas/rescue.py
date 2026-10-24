"""Canonical Schema for ScamGraph Rescue (Prompt 16 / Phase 5B).

Covers Post-Loss Emergency Triage, Incident Reconstruction, Loss Timeline,
Exposure Assessment, Official Reporting Resources, Evidence Preservation,
Recovery-Scam Protection, Case Package, and Missed-Prevention Review.
"""

from datetime import datetime, timezone
from enum import Enum
import hashlib
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class LossType(str, Enum):
    """Categorization of reported scam loss or disclosure."""
    MONEY_TRANSFER = "MONEY_TRANSFER"
    UPI_PAYMENT = "UPI_PAYMENT"
    BANK_TRANSFER = "BANK_TRANSFER"
    CARD_PAYMENT = "CARD_PAYMENT"
    WALLET_PAYMENT = "WALLET_PAYMENT"
    CRYPTO_TRANSFER = "CRYPTO_TRANSFER"
    CREDENTIAL_DISCLOSURE = "CREDENTIAL_DISCLOSURE"
    OTP_DISCLOSURE = "OTP_DISCLOSURE"
    REMOTE_ACCESS = "REMOTE_ACCESS"
    IDENTITY_DOCUMENT_DISCLOSURE = "IDENTITY_DOCUMENT_DISCLOSURE"
    ACCOUNT_TAKEOVER = "ACCOUNT_TAKEOVER"
    MULTIPLE = "MULTIPLE"
    UNKNOWN = "UNKNOWN"


class LossStatus(str, Enum):
    """Operational status of the reported loss."""
    NO_CONFIRMED_LOSS = "NO_CONFIRMED_LOSS"
    PAYMENT_INITIATED = "PAYMENT_INITIATED"
    PAYMENT_COMPLETED = "PAYMENT_COMPLETED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    CREDENTIALS_EXPOSED = "CREDENTIALS_EXPOSED"
    ACCOUNT_COMPROMISE_SUSPECTED = "ACCOUNT_COMPROMISE_SUSPECTED"
    ACCOUNT_COMPROMISE_CONFIRMED = "ACCOUNT_COMPROMISE_CONFIRMED"
    UNKNOWN = "UNKNOWN"


class ExposureCategory(str, Enum):
    """Assets or accounts exposed to the adversary."""
    PAYMENT = "PAYMENT"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    EMAIL_ACCOUNT = "EMAIL_ACCOUNT"
    SOCIAL_ACCOUNT = "SOCIAL_ACCOUNT"
    MESSAGING_ACCOUNT = "MESSAGING_ACCOUNT"
    DEVICE = "DEVICE"
    IDENTITY = "IDENTITY"
    OTHER = "OTHER"


class ExposureSeverity(str, Enum):
    """Urgency / severity of an exposure."""
    CRITICAL = "CRITICAL"      # Active remote access, netbanking password disclosed, active OTP session
    HIGH = "HIGH"              # Bank account details, email password, social login
    MEDIUM = "MEDIUM"          # ID document (Aadhaar/PAN), phone number, email address
    LOW = "LOW"                # Public social handle, name
    INFO = "INFO"


class TimeGranularity(str, Enum):
    """Precision level of a victim-reported timestamp."""
    EXACT = "EXACT"
    APPROXIMATE = "APPROXIMATE"
    DATE_ONLY = "DATE_ONLY"
    ORDER_ONLY = "ORDER_ONLY"
    UNKNOWN = "UNKNOWN"


class ActionCategory(str, Enum):
    """Action priority categorization in the Emergency Action Plan."""
    DO_NOW = "DO_NOW"          # First 1-15 minutes (kill remote access, 1930 / bank 24/7 fraud line)
    DO_NEXT = "DO_NEXT"        # First 1-2 hours (reset passwords, revoke app permissions, alert family)
    PRESERVE = "PRESERVE"      # Capture UTR, transaction IDs, original unedited chat screenshots
    REPORT = "REPORT"          # File formal NCRP (cybercrime.gov.in) complaint with structured evidence
    MONITOR = "MONITOR"        # Watch out for recovery scams ("pay release fee") and account activity


class ActionStatus(str, Enum):
    """State of an action step for the user."""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ReportingResourceType(str, Enum):
    """Official resource category for India cyber fraud response."""
    NATIONAL_CYBER_FRAUD_HELP = "NATIONAL_CYBER_FRAUD_HELP"  # 1930 Helpline
    CYBERCRIME_REPORTING = "CYBERCRIME_REPORTING"            # cybercrime.gov.in (NCRP)
    BANK_OR_PAYMENT_PROVIDER = "BANK_OR_PAYMENT_PROVIDER"    # SBI, HDFC, ICICI, etc.
    UPI_PROVIDER = "UPI_PROVIDER"                            # NPCI, PhonePe, Google Pay, Paytm
    CARD_ISSUER = "CARD_ISSUER"                              # Visa, Mastercard, RuPay
    LOCAL_LAW_ENFORCEMENT = "LOCAL_LAW_ENFORCEMENT"          # State cyber police station
    ACCOUNT_PROVIDER = "ACCOUNT_PROVIDER"                    # Google, Meta, Apple, Telegram


class OfficialReportingResource(BaseModel):
    """Verified official authority or banking contact registry."""
    resource_id: str = Field(default_factory=lambda: generate_id("res"))
    resource_type: ReportingResourceType
    jurisdiction: str = Field(default="IN", description="ISO country code (e.g. IN for India)")
    organization: str
    display_name: str
    official_url: Optional[str] = None
    official_phone: Optional[str] = None
    verification_state: str = Field(default="VERIFIED", description="VERIFIED, PROVISIONAL, PENDING")
    source: str = Field(default="MHA_I4C_OFFICIAL", description="Data authority source")
    last_verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    instructions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LossEvent(BaseModel):
    """Detailed record of an individual financial loss or money transfer event."""
    loss_event_id: str = Field(default_factory=lambda: generate_id("loss"))
    incident_id: str
    payment_method: str = Field(default="UPI", description="UPI, IMPS, NEFT, RTGS, CARD, CRYPTO, WALLET")
    amount: float = Field(ge=0.0)
    currency: str = Field(default="INR")
    amount_confidence: str = Field(default="USER_REPORTED", description="USER_REPORTED, EVIDENCE_VERIFIED, ESTIMATED")
    recipient_entity_id: Optional[str] = None
    recipient_identifier: Optional[str] = Field(default=None, description="e.g. UPI VPA or masked account")
    transaction_reference_tokenized: Optional[str] = Field(default=None, description="Masked/tokenized UTR or txn ref")
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    time_granularity: TimeGranularity = Field(default=TimeGranularity.EXACT)
    status: LossStatus = Field(default=LossStatus.PAYMENT_COMPLETED)
    evidence_ids: List[str] = Field(default_factory=list)
    user_reported: bool = Field(default=True)
    verification_state: str = Field(default="UNVERIFIED", description="UNVERIFIED, PENDING_STATEMENT, BANK_VERIFIED")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def deduplication_key(self) -> str:
        """Computes deterministic hash key to prevent double-counting payments."""
        ref = (self.transaction_reference_tokenized or "").strip().lower()
        recip = (self.recipient_identifier or "").strip().lower()
        amt = f"{self.amount:.2f}"
        raw = f"{self.incident_id}|{amt}|{self.currency}|{ref}|{recip}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class ExposureAssessment(BaseModel):
    """Evaluates compromised credentials, devices, or identity documents."""
    exposure_id: str = Field(default_factory=lambda: generate_id("exp"))
    incident_id: str
    category: ExposureCategory
    severity: ExposureSeverity
    target_identifier: Optional[str] = Field(default=None, description="e.g. masked phone, bank name, app name")
    details: str = Field(default="", description="Descriptive statement of what was shared")
    remote_tool_name: Optional[str] = Field(default=None, description="AnyDesk, TeamViewer, RustDesk if remote access")
    id_document_type: Optional[str] = Field(default=None, description="AADHAAR, PAN, PASSPORT, DRIVING_LICENSE")
    has_secret_exposed: bool = Field(default=False, description="True if password, PIN, or OTP disclosed")
    active_now: bool = Field(default=False, description="True if adversary may currently have access")
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RescueActionItem(BaseModel):
    """An individual actionable step for victim assistance."""
    action_id: str = Field(default_factory=lambda: generate_id("act"))
    category: ActionCategory
    priority_order: int = Field(default=1)
    title: str
    description: str
    official_resource: Optional[OfficialReportingResource] = None
    action_type: str = Field(default="DIRECT_CALL", description="DIRECT_CALL, BROWSER_LINK, COPY_TEXT, DEVICE_SETTING")
    link_or_dial: Optional[str] = None
    status: ActionStatus = Field(default=ActionStatus.TODO)
    user_confirmed_at: Optional[datetime] = None
    is_immediate_lifeline: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EmergencyActionPlan(BaseModel):
    """Tailored, context-aware action plan prioritizing immediate safety over paperwork."""
    plan_id: str = Field(default_factory=lambda: generate_id("eap"))
    incident_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    do_now: List[RescueActionItem] = Field(default_factory=list)
    do_next: List[RescueActionItem] = Field(default_factory=list)
    preserve: List[RescueActionItem] = Field(default_factory=list)
    report: List[RescueActionItem] = Field(default_factory=list)
    monitor: List[RescueActionItem] = Field(default_factory=list)
    total_actions: int = Field(default=0)
    completed_actions: int = Field(default=0)


class RescueTimelineEventType(str, Enum):
    """Events recorded on the post-loss and response timeline."""
    SCAM_CONTACT = "SCAM_CONTACT"
    PLATFORM_MOVE = "PLATFORM_MOVE"
    PAYMENT_REQUEST = "PAYMENT_REQUEST"
    PAYMENT_SENT = "PAYMENT_SENT"
    CREDENTIAL_SHARED = "CREDENTIAL_SHARED"
    REMOTE_ACCESS_GRANTED = "REMOTE_ACCESS_GRANTED"
    LOSS_DISCOVERED = "LOSS_DISCOVERED"
    BANK_CONTACTED = "BANK_CONTACTED"
    HELPLINE_CONTACTED = "HELPLINE_CONTACTED"
    COMPLAINT_SUBMITTED = "COMPLAINT_SUBMITTED"
    ACCOUNT_SECURED = "ACCOUNT_SECURED"
    ADDITIONAL_SCAM_CONTACT = "ADDITIONAL_SCAM_CONTACT"
    RECOVERY_SCAM_CONTACT = "RECOVERY_SCAM_CONTACT"


class RescueTimelineEvent(BaseModel):
    """Chronological event in the victim's encounter and response journey."""
    timeline_event_id: str = Field(default_factory=lambda: generate_id("rtm"))
    event_type: RescueTimelineEventType
    title: str
    description: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    time_granularity: TimeGranularity = Field(default=TimeGranularity.EXACT)
    loss_event_id: Optional[str] = None
    exposure_id: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    source: str = Field(default="USER_REPORTED", description="USER_REPORTED, SYSTEM_INFERRED, OFFICIAL_LOG")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidencePreservationItem(BaseModel):
    """Item of evidence identified and preserved for official reporting."""
    preservation_id: str = Field(default_factory=lambda: generate_id("prv"))
    evidence_id: str
    evidence_type: str = Field(..., description="SCREENSHOT, CHAT_EXPORT, UPI_SLIP, CALL_RECORD, SMS, URL")
    display_title: str
    description: str
    sha256_hash: str
    is_original: bool = Field(default=True)
    derived_from_id: Optional[str] = None
    redaction_state: str = Field(default="MASKED_SECRETS", description="RAW, MASKED_SECRETS, ANONYMIZED")
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    storage_path: Optional[str] = None
    mime_type: str = Field(default="application/octet-stream")


class EvidencePreservationPlan(BaseModel):
    """Checklist and manifest of critical evidence required for bank/NCRP filing."""
    plan_id: str = Field(default_factory=lambda: generate_id("epp"))
    incident_id: str
    items: List[EvidencePreservationItem] = Field(default_factory=list)
    recommended_items_missing: List[str] = Field(default_factory=list)
    guidance_notes: List[str] = Field(default_factory=list)


class RecoveryScamProtection(BaseModel):
    """Protection signals and warnings against secondary advance-fee recovery fraud."""
    protection_id: str = Field(default_factory=lambda: generate_id("rsp"))
    incident_id: str
    risk_level: str = Field(default="HIGH", description="CRITICAL, HIGH, MEDIUM, LOW")
    secondary_contact_detected: bool = Field(default=False)
    recovery_fee_requested: bool = Field(default=False)
    threat_patterns_detected: List[str] = Field(default_factory=list)
    warning_text: str = Field(
        default="NEVER pay anyone claiming they can 'recover', 'hack back', or 'unfreeze' your funds for a fee. "
                "Official law enforcement and banks never charge advance fees to investigate fraud."
    )
    rules_triggered: List[str] = Field(default_factory=list)


class RescueTriage(BaseModel):
    """Core post-loss assessment summary determining severity and immediate steps."""
    triage_id: str = Field(default_factory=lambda: generate_id("trg"))
    incident_id: str
    loss_types: List[LossType] = Field(default_factory=list)
    loss_status: LossStatus = Field(default=LossStatus.UNKNOWN)
    financial_exposure: bool = Field(default=False)
    credential_exposure: bool = Field(default=False)
    account_exposure: bool = Field(default=False)
    device_exposure: bool = Field(default=False)
    identity_exposure: bool = Field(default=False)
    total_reported_loss: float = Field(default=0.0)
    currency: str = Field(default="INR")
    ongoing_contact: bool = Field(default=False)
    remote_access_active_or_possible: bool = Field(default=False)
    additional_payment_risk: bool = Field(default=False)
    recovery_scam_risk: bool = Field(default=False)
    priority: str = Field(default="URGENT", description="EMERGENCY_CRITICAL, URGENT, ELEVATED, STANDARD")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    policy_version: str = Field(default="2026.10-v1")
    engine_version: str = Field(default="RescueTriageEngine-v1.0")


class MissedPreventionReview(BaseModel):
    """Post-incident analysis evaluating whether earlier detection was possible without future leakage."""
    review_id: str = Field(default_factory=lambda: generate_id("mpr"))
    incident_id: str
    loss_boundary: datetime = Field(description="Timestamp of the very first monetary loss or critical disclosure")
    pre_loss_signals_count: int = Field(default=0)
    post_loss_signals_count: int = Field(default=0)
    earliest_possible_warning_stage: Optional[str] = None
    actual_warning_stage: Optional[str] = None
    failure_category: str = Field(
        default="NO_PRELOSS_CHECK",
        description="NO_PRELOSS_CHECK, INSUFFICIENT_EVIDENCE, MODEL_MISS, JOURNEY_MISS, ENTITY_MISS, NETWORK_MISS, CAMPAIGN_MISS, POLICY_MISS, USER_CONTINUED_AFTER_WARNING, SYSTEM_UNAVAILABLE"
    )
    pre_loss_evidence_ids: List[str] = Field(default_factory=list)
    post_loss_evidence_ids: List[str] = Field(default_factory=list)
    notes: str = Field(default="")


class RescueCasePackage(BaseModel):
    """Structured, privacy-safe exportable incident package for reporting to 1930/NCRP/Banks."""
    package_id: str = Field(default_factory=lambda: generate_id("rcp"))
    incident_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    package_version: str = Field(default="1.0.0")
    assessment_version: str = Field(default="UnifiedAssessment-v2.0")
    
    # 1. User-Reported Facts (Cleanly Separated)
    user_reported_facts: Dict[str, Any] = Field(default_factory=dict)
    
    # 2. Financial Loss Summary
    reported_total_loss: float = Field(default=0.0)
    confirmed_verified_loss: Optional[float] = None
    currency: str = Field(default="INR")
    payment_events_count: int = Field(default=0)
    payment_events: List[LossEvent] = Field(default_factory=list)
    
    # 3. Timeline
    timeline_events: List[RescueTimelineEvent] = Field(default_factory=list)
    
    # 4. Suspect Entities (Masked / Safe)
    contact_entities: List[Dict[str, Any]] = Field(default_factory=list)
    urls_and_domains: List[str] = Field(default_factory=list)
    social_handles: List[str] = Field(default_factory=list)
    claimed_organizations: List[str] = Field(default_factory=list)
    
    # 5. ScamGraph Inferred Intelligence
    inferred_scam_family: Optional[str] = None
    scam_journey_summary: str = Field(default="")
    manipulation_tactics: List[str] = Field(default_factory=list)
    network_campaign_id: Optional[str] = None
    
    # 6. Evidence Manifest
    evidence_manifest: List[EvidencePreservationItem] = Field(default_factory=list)
    
    # 7. Actions Taken & Next Steps
    actions_already_taken: List[str] = Field(default_factory=list)
    recommended_official_actions: List[str] = Field(default_factory=list)
    official_reporting_resources: List[OfficialReportingResource] = Field(default_factory=list)
    
    # 8. Copyable Text Summary for 1930 / Bank Portals
    copyable_incident_summary: str = Field(default="")
    
    # 9. Legal Disclaimers
    legal_disclaimer: str = Field(
        default="This document is a technical Incident Information Package prepared based on user-provided "
                "statements and ScamGraph AI automated analysis. It does NOT constitute an official Police "
                "FIR, Government Cybercrime Registration, or guarantee of fund recovery. It is designed to assist "
                "victims in filing accurate, structured reports with verified authorities and banking institutions."
    )
