"""Enterprise API & SDK Platform V2 schemas (Prompt 20 / Phase 6B)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class EnvironmentType(str, Enum):
    """Execution environment for API credentials and requests."""
    LIVE = "LIVE"
    SANDBOX = "SANDBOX"


class DataContributionPolicy(str, Enum):
    """Customer-controlled policy governing global network intelligence sharing."""
    PRIVATE_ONLY = "PRIVATE_ONLY"
    AGGREGATE_ALLOWED = "AGGREGATE_ALLOWED"
    NETWORK_INTELLIGENCE_ALLOWED = "NETWORK_INTELLIGENCE_ALLOWED"
    TRAINING_OPT_IN = "TRAINING_OPT_IN"


class GuardActionType(str, Enum):
    """Canonical Pre-Payment Guard actions for banking and fintech integrators."""
    ALLOW_NORMAL_FLOW = "ALLOW_NORMAL_FLOW"
    SHOW_CAUTION = "SHOW_CAUTION"
    VERIFY_INDEPENDENTLY = "VERIFY_INDEPENDENTLY"
    PAUSE_BEFORE_PAYMENT = "PAUSE_BEFORE_PAYMENT"
    STRONG_WARNING = "STRONG_WARNING"
    ESCALATE_REVIEW = "ESCALATE_REVIEW"


class AnalysisJobStatus(str, Enum):
    """Lifecycle status of an asynchronous multimodal analysis job."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WebhookEventType(str, Enum):
    """Standardized event triggers emitted to partner webhook endpoints."""
    ANALYSIS_COMPLETED = "analysis.completed"
    ANALYSIS_FAILED = "analysis.failed"
    HIGH_RISK_DETECTED = "high_risk.detected"
    CAMPAIGN_EMERGING = "campaign.emerging"
    CAMPAIGN_OUTBREAK = "campaign.outbreak"
    CAMPAIGN_RESURGING = "campaign.resurging"
    ENTITY_NETWORK_SIGNAL_CHANGED = "entity.network_signal_changed"


# -----------------------------------------------------------------------------
# Organization & Credentials
# -----------------------------------------------------------------------------

class EnterpriseOrganization(BaseModel):
    """Multi-tenant organization boundary for enterprise partners."""
    org_id: str = Field(default_factory=lambda: generate_id("org"))
    name: str
    status: str = Field(default="ACTIVE", description="ACTIVE, SUSPENDED, PENDING")
    data_contribution_policy: DataContributionPolicy = Field(default=DataContributionPolicy.NETWORK_INTELLIGENCE_ALLOWED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApiKeyRecord(BaseModel):
    """Stored representation of an API credential (never stores raw secret)."""
    key_id: str = Field(default_factory=lambda: generate_id("key"))
    prefix: str
    hashed_secret: str
    org_id: str
    environment: EnvironmentType = Field(default=EnvironmentType.LIVE)
    scopes: List[str] = Field(default_factory=lambda: ["check:write", "guard:write", "entity:read", "campaign:read"])
    status: str = Field(default="ACTIVE", description="ACTIVE, REVOKED, EXPIRED")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: Optional[datetime] = None


class ApiKeyCreateResponse(BaseModel):
    """Returned once upon key creation; raw secret is never displayed again."""
    key_id: str
    api_key: str
    prefix: str
    environment: EnvironmentType
    scopes: List[str]
    created_at: datetime


# -----------------------------------------------------------------------------
# Scam Check API Contracts
# -----------------------------------------------------------------------------

class EnterpriseCheckRequest(BaseModel):
    """Input payload for the multi-signal Scam Check API."""
    message_text: Optional[str] = None
    url: Optional[str] = None
    phone: Optional[str] = None
    vpa: Optional[str] = None
    email: Optional[str] = None
    social_handle: Optional[str] = None
    artifact_id: Optional[str] = None
    external_reference: Optional[str] = Field(default=None, description="Partner's safe internal reference ID")
    context: Dict[str, Any] = Field(default_factory=dict)
    environment: EnvironmentType = Field(default=EnvironmentType.LIVE)


class EnterpriseCheckResponse(BaseModel):
    """Standardized customer-safe assessment response."""
    check_id: str
    request_id: str
    risk_level: str = Field(description="LOW, MEDIUM, HIGH, CRITICAL, INSUFFICIENT_EVIDENCE")
    risk_score: int = Field(ge=0, le=100)
    confidence: str = Field(description="LOW, MEDIUM, HIGH")
    urgency: str = Field(description="LOW, MEDIUM, HIGH, CRITICAL")
    recommended_action: str
    reason_codes: List[str] = Field(default_factory=list)
    journey_summary: Optional[Dict[str, Any]] = None
    network_signal: str = Field(default="NO_NETWORK_SIGNAL")
    campaign_signal: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)
    processing_ms: int = 0
    environment: EnvironmentType = EnvironmentType.LIVE


# -----------------------------------------------------------------------------
# Pre-Payment Guard API Contracts
# -----------------------------------------------------------------------------

class EnterpriseGuardRequest(BaseModel):
    """Input payload for payment-sensitive pre-transaction check."""
    vpa: str
    amount: Optional[float] = Field(default=None, ge=0.0)
    currency: str = Field(default="INR")
    qr_payload: Optional[str] = None
    message_text: Optional[str] = None
    external_reference: Optional[str] = None
    user_id_hash: Optional[str] = None
    fast_path: bool = Field(default=True, description="Strict latency mode avoiding deep models")
    environment: EnvironmentType = Field(default=EnvironmentType.LIVE)


class EnterpriseGuardResponse(BaseModel):
    """Decision response for payment and fintech checkout flows."""
    guard_id: str
    request_id: str
    action: GuardActionType
    friction_level: int = Field(ge=0, le=6, description="0=allow, 1-3=warning, 4=pause, 5-6=block/escalate")
    risk_score: int = Field(ge=0, le=100)
    confidence: str
    payment_proximity: str
    reason_codes: List[str]
    intervention_title: str
    intervention_message: str
    safe_guidance: List[str]
    network_signal: str
    latency_tier: str = Field(default="FAST_PATH")
    processing_ms: int = 0
    environment: EnvironmentType = EnvironmentType.LIVE


# -----------------------------------------------------------------------------
# Entity & Network Intelligence Contracts
# -----------------------------------------------------------------------------

class EnterpriseEntityCheckRequest(BaseModel):
    """Lookup request for fraud entity reputation."""
    entity_type: str = Field(description="PHONE, EMAIL, UPI, DOMAIN, URL, SOCIAL_ACCOUNT")
    value: str


class EnterpriseEntityCheckResponse(BaseModel):
    """Privacy-safe entity intelligence disclosure."""
    entity_type: str
    normalized_value: str
    verification_state: str = Field(description="VERIFIED_LEGITIMATE, SUSPICIOUS, UNVERIFIED, UNKNOWN")
    network_reputation: str = Field(description="CLEAN, REPORTED_SUSPICIOUS, CAMPAIGN_LINKED, HIGH_RISK_MULE")
    incident_count_bracket: str = Field(description="Bracketed count e.g. 1-5, 6-20, 20+ to protect small cohorts")
    campaign_associations: List[str] = Field(default_factory=list)
    confidence: float = 0.80
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class EnterpriseNetworkCheckRequest(BaseModel):
    """Correlation check request across shared syndicate infrastructure."""
    entity_value: Optional[str] = None
    incident_id: Optional[str] = None


class EnterpriseNetworkCheckResponse(BaseModel):
    """Privacy-safe network correlation signal."""
    network_signal: str = Field(description="NO_NETWORK_SIGNAL, SIMILAR_PATTERN_OBSERVED, ENTITY_REPORTED_ELSEWHERE, MULTIPLE_RELATED_SIGNALS, EMERGING_PATTERN")
    confidence: float
    corroborating_sources_count: int
    summary: str
    warnings: List[str] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Async Analysis & Jobs
# -----------------------------------------------------------------------------

class AnalysisJobRecord(BaseModel):
    """Asynchronous job state for long-running media / batch workloads."""
    job_id: str = Field(default_factory=lambda: generate_id("job"))
    org_id: str
    status: AnalysisJobStatus = Field(default=AnalysisJobStatus.PENDING)
    progress_stage: str = Field(default="QUEUED", description="QUEUED, OCR_PROCESSING, SPEECH_TRANSCRIBING, RECONSTRUCTING_JOURNEY, COMPLETED")
    artifact_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


# -----------------------------------------------------------------------------
# Webhook Architecture
# -----------------------------------------------------------------------------

class WebhookEndpointRecord(BaseModel):
    """Registered partner destination for threat event webhooks."""
    endpoint_id: str = Field(default_factory=lambda: generate_id("whk"))
    org_id: str
    url: str
    secret_hash: str
    event_types: List[WebhookEventType]
    status: str = Field(default="ACTIVE", description="ACTIVE, DISABLED, FAILING")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WebhookEventPayload(BaseModel):
    """Standardized webhook notification payload sent to partner servers."""
    event_id: str = Field(default_factory=lambda: generate_id("evt"))
    event_type: WebhookEventType
    api_version: str = "v1"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any]


class WebhookDeliveryRecord(BaseModel):
    """Persistent audit record of an individual webhook dispatch attempt."""
    delivery_id: str = Field(default_factory=lambda: generate_id("del"))
    endpoint_id: str
    event_id: str
    status: str = Field(default="DELIVERED", description="DELIVERED, RETRYING, FAILED")
    attempts: int = 1
    last_response_code: Optional[int] = 200
    delivered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# -----------------------------------------------------------------------------
# Idempotency & Error Handling
# -----------------------------------------------------------------------------

class IdempotencyRecord(BaseModel):
    """Ensures repeated API calls with identical keys do not execute duplicate mutations."""
    idempotency_key: str
    org_id: str
    endpoint: str
    request_hash: str
    response_payload: Dict[str, Any]
    status_code: int = 200
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime


class EnterpriseErrorResponse(BaseModel):
    """Customer-safe standardized error schema (no raw internal stack traces)."""
    code: str
    message: str
    request_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    retryable: bool = False
    docs_url: str = "https://docs.scamgraph.ai/errors"
