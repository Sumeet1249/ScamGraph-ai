"""Canonical Psychological Tactics & Call-to-Action Schemas for ScamGraph AI V2.

Encodes behavioral manipulation signals, requested actions, evidence spans,
multi-turn conversation timelines, and proactive consumer intervention candidates.
"""

from datetime import datetime, timezone
from enum import Enum
import hashlib
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class TacticType(str, Enum):
    """Psychological manipulation tactics identified across Indian fraud journeys."""
    AUTHORITY = "AUTHORITY"                     # CBI, Police, Supreme Court, TRAI, Bank Manager, Custom Dept
    URGENCY = "URGENCY"                         # 2 hours left, electricity disconnect at 9:30 PM, immediate action
    FEAR = "FEAR"                               # Arrest warrant, legal case, account freeze, parcel confiscation
    GREED = "GREED"                             # Guaranteed 300% returns, lottery prize, high daily wages
    SCARCITY = "SCARCITY"                       # Only 2 job slots remaining, limited period, final allocation
    SOCIAL_PROOF = "SOCIAL_PROOF"               # Fake Telegram group members showing withdrawal screenshots
    ROMANCE = "ROMANCE"                         # Matrimonial / emotional grooming
    TRUST_BUILDING = "TRUST_BUILDING"           # Returning small profit (₹150 on ₹500 task), polite onboarding
    SECRECY = "SECRECY"                         # "Keep this confidential, do not tell family or bank"
    ISOLATION = "ISOLATION"                     # "Stay on Skype call, lock door, do not disconnect or consult"
    RECIPROCITY = "RECIPROCITY"                 # "We helped you recover funds, now pay our legal fee / small deposit"
    LOSS_AVERSION = "LOSS_AVERSION"             # "Pay ₹5,000 tax or lose your entire ₹50,000 balance"
    FAKE_REWARD = "FAKE_REWARD"                 # Free gift, cashback voucher, spin the wheel, fake investment credit
    THREAT = "THREAT"                           # Defamation, leaking contacts, physical harm, police raid
    IMPERSONATION = "IMPERSONATION"             # Pretending to be courier, discom, bank officer, company CEO
    PAYMENT_PRESSURE = "PAYMENT_PRESSURE"       # Demanding immediate UPI collect approval, deposit, fee payment
    CREDENTIAL_PRESSURE = "CREDENTIAL_PRESSURE" # Demanding OTP, netbanking password, ATM PIN, CVV
    REMOTE_ACCESS_PRESSURE = "REMOTE_ACCESS_PRESSURE" # AnyDesk, TeamViewer, RustDesk, screen share, APK install
    PLATFORM_MIGRATION = "PLATFORM_MIGRATION"   # Moving victim from job portal/dating to WhatsApp/Telegram
    COMPLIANCE_PRESSURE = "COMPLIANCE_PRESSURE" # Rigid drill instructions ("Answer yes/no only", "Stay in camera frame")


class ActionRequestedType(str, Enum):
    """Explicit behavioral actions demanded by the scammer."""
    CLICK_LINK = "CLICK_LINK"
    CALL_NUMBER = "CALL_NUMBER"
    REPLY = "REPLY"
    INSTALL_APP = "INSTALL_APP"                 # AnyDesk, QuickSupport, malicious APK
    DOWNLOAD_FILE = "DOWNLOAD_FILE"
    SHARE_OTP = "SHARE_OTP"
    SHARE_CREDENTIAL = "SHARE_CREDENTIAL"       # Netbanking login, ATM PIN, CVV
    SHARE_SCREEN = "SHARE_SCREEN"
    MOVE_PLATFORM = "MOVE_PLATFORM"             # "Message me on Telegram / WhatsApp"
    ADD_CONTACT = "ADD_CONTACT"
    SEND_PAYMENT = "SEND_PAYMENT"               # Direct UPI transfer, IMPS, RTGS
    SCAN_QR = "SCAN_QR"                         # "Scan to receive payment" (scam trick)
    APPROVE_UPI_REQUEST = "APPROVE_UPI_REQUEST" # Collect request approval
    INVEST_MORE = "INVEST_MORE"
    PAY_FEE = "PAY_FEE"                         # Customs fee, tax, processing fee
    KEEP_SECRET = "KEEP_SECRET"
    DO_NOT_DISCONNECT = "DO_NOT_DISCONNECT"
    UNKNOWN = "UNKNOWN"


class EvidenceSpan(BaseModel):
    """Specific substring span supporting a detected tactic with privacy-aware hashing."""
    start: int = Field(..., ge=0, description="Start character offset")
    end: int = Field(..., ge=0, description="End character offset")
    text: str = Field(..., description="Exact substring matched")
    text_hash: str = Field(default="", description="SHA-256 hash of evidence text for audit")
    redacted_preview: str = Field(default="", description="PII-masked preview of span")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    def model_post_init(self, __context: Any) -> None:
        if not self.text_hash and self.text:
            self.text_hash = hashlib.sha256(self.text.strip().encode("utf-8")).hexdigest()
        if not self.redacted_preview and self.text:
            self.redacted_preview = self.text


class TacticSignal(BaseModel):
    """Granular, evidence-backed manipulation signal."""
    signal_id: str = Field(default_factory=lambda: generate_id("tact"), description="Unique tactic signal ID")
    schema_version: str = Field(default="2.0")
    tactic: TacticType = Field(..., description="Psychological manipulation tactic")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Signal confidence score")
    severity: str = Field(default="MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    artifact_id: Optional[str] = Field(default=None)
    event_id: Optional[str] = Field(default=None)
    incident_id: Optional[str] = Field(default=None)
    conversation_id: Optional[str] = Field(default=None)
    turn_index: Optional[int] = Field(default=None, description="Conversation turn index if multi-message")
    
    # Evidence & Action Links
    supporting_spans: List[EvidenceSpan] = Field(default_factory=list, description="Exact text spans supporting tactic")
    requested_actions: List[ActionRequestedType] = Field(default_factory=list, description="Immediate calls-to-action")
    related_entities: List[str] = Field(default_factory=list, description="Associated Entity IDs (e.g. ent_...)")
    detector_sources: List[str] = Field(default_factory=lambda: ["RULE"], description="RULE, CLASSIFIER, SEMANTIC, LLM, COMBINED")
    
    # Negation and Quoted Context flags
    is_negated: bool = Field(default=False, description="True if text uses tactic terms in protective/warning context")
    is_quoted: bool = Field(default=False, description="True if user is asking about or quoting scam text")
    
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TacticTimeline(BaseModel):
    """Chronological progression of psychological tactics across conversation turns or incident events."""
    timeline_id: str = Field(default_factory=lambda: generate_id("ttml"))
    conversation_id: Optional[str] = Field(default=None)
    incident_id: Optional[str] = Field(default=None)
    signals: List[TacticSignal] = Field(default_factory=list)
    
    # Aggregated Dimensions (ScamDNA foundation)
    tactic_vector: Dict[str, float] = Field(default_factory=dict, description="Normalized intensity [0.0 - 1.0] per TacticType")
    manipulation_density: float = Field(default=0.0, description="Density of manipulation signals across message turns")
    escalation_signal: bool = Field(default=False, description="True if coercive tactics escalate over time")
    escalation_description: Optional[str] = Field(default=None)
    
    # Derived Intervention Candidates
    intervention_candidates: List[str] = Field(
        default_factory=list,
        description="Candidate interventions: ANTI_ISOLATION_INTERVENTION_CANDIDATE, PAYMENT_INTERVENTION_CANDIDATE, CREDENTIAL_PROTECTION_CANDIDATE, REMOTE_ACCESS_WARNING_CANDIDATE, PAUSE_BEFORE_PAYMENT"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConsumerTacticWarning(BaseModel):
    """Privacy-safe, plain-language explanation for consumers (no raw probabilities or technical internals)."""
    title: str = Field(default="Manipulation Warning")
    summary: str = Field(..., description="Clear consumer-facing summary of why this communication is coercive")
    detected_tactics: List[str] = Field(default_factory=list, description="Human-readable names of tactics detected")
    recommended_interventions: List[str] = Field(default_factory=list, description="Safe next actions for user")


# Backwards compatibility wrapper for Phase 0 legacy code
class ManipulationSignal(BaseModel):
    """Structured output representing psychological tactics and pressure points (Legacy V1 compatibility)."""
    tactics_present: List[TacticType] = Field(default_factory=list)
    actions_requested: List[ActionRequestedType] = Field(default_factory=list)
    primary_tactic: TacticType = Field(default=TacticType.IMPERSONATION)
    manipulation_severity: str = Field(default="MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    explanation: str = Field(default="", description="Consumer-facing plain-language explanation of manipulation")
