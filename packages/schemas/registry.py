"""Smart Registry Schemas for ScamGraph AI (Module A).

Inspired by the publicly documented capabilities of RBIH Digital Payments Intelligence Platform (DPIP).
Provides typed identifiers, canonical fingerprinting contracts, core entity models, report lifecycle states,
screening models, dispute resolution, revocation workflows, and immutable audit logs.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class IdentifierType(str, Enum):
    """Supported canonical identifier types in Smart Registry."""
    PHONE = "PHONE"
    PHONE_NUMBER = "PHONE_NUMBER"  # Alias
    UPI_VPA = "UPI_VPA"
    UPI_ID = "UPI_ID"              # Alias
    BANK_ACCOUNT = "BANK_ACCOUNT"
    DEVICE_ID = "DEVICE_ID"
    IP_ADDRESS = "IP_ADDRESS"
    URL_DOMAIN = "URL_DOMAIN"
    URL = "URL"                    # Alias
    DOMAIN = "DOMAIN"              # Alias
    EMAIL = "EMAIL"
    TRANSACTION_REF = "TRANSACTION_REF"


class ReportStatus(str, Enum):
    """Explicit state machine for registry fraud reports."""
    REPORTED = "REPORTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    DISPUTED = "DISPUTED"
    REVOKED = "REVOKED"


class MatchType(str, Enum):
    """Categorization of match confidence."""
    EXACT_FINGERPRINT = "EXACT_FINGERPRINT"
    APPROXIMATE_SIMILARITY = "APPROXIMATE_SIMILARITY"
    GRAPH_ASSOCIATION = "GRAPH_ASSOCIATION"
    INFERRED_RISK = "INFERRED_RISK"


class AuditAction(str, Enum):
    """Audit action types for immutable registry ledger."""
    REPORT_CREATED = "REPORT_CREATED"
    REPORT_REVIEWED = "REPORT_REVIEWED"
    STATUS_CHANGED = "STATUS_CHANGED"
    DISPUTE_FILED = "DISPUTE_FILED"
    DISPUTE_RESOLVED = "DISPUTE_RESOLVED"
    REVOCATION_REQUESTED = "REVOCATION_REQUESTED"
    REVOCATION_APPROVED = "REVOCATION_APPROVED"
    SCREENING_PERFORMED = "SCREENING_PERFORMED"
    FEEDBACK_LOGGED = "FEEDBACK_LOGGED"


# -----------------------------------------------------------------------------
# Identifier & Fingerprint Schemas
# -----------------------------------------------------------------------------

class TypedIdentifier(BaseModel):
    """Raw typed identifier input."""
    identifier_type: IdentifierType
    raw_value: str = Field(..., min_length=1, description="Raw input value before canonicalization")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CanonicalFingerprint(BaseModel):
    """Keyed HMAC-SHA-256 canonical fingerprint for privacy-preserving exact match."""
    identifier_type: IdentifierType
    fingerprint: str = Field(..., description="HMAC-SHA-256 hex digest prefixed with key version")
    key_version: str = Field(default="v1", description="HMAC key version used to generate digest")
    normalized_preview: Optional[str] = Field(
        None,
        description="Masked or partial preview for administrative identification"
    )


# -----------------------------------------------------------------------------
# Core Registry Entity Model (Phase 3)
# -----------------------------------------------------------------------------

class RegistryEntity(BaseModel):
    """Canonical registry entity tracking a protected suspect identifier."""
    entity_id: str = Field(..., description="Internal entity ID (e.g. ent_abc123)")
    entity_type: IdentifierType
    fingerprint: str = Field(..., description="HMAC-SHA-256 fingerprint")
    normalization_version: str = Field(default="v1", description="Version of normalization algorithm")
    protection_key_version: str = Field(default="v1", description="Version of HMAC key used")
    status: ReportStatus = Field(default=ReportStatus.REPORTED, description="Current aggregated registry status")
    category: str = Field(default="SUSPECT_ACTIVITY", description="Primary fraud category")
    report_count: int = Field(default=1, description="Number of linked reports")
    associated_report_ids: List[str] = Field(default_factory=list, description="IDs of linked fraud reports")
    highest_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    masked_preview: Optional[str] = Field(None, description="Safe masked preview")
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# Report Ingestion & Lifecycle Schemas
# -----------------------------------------------------------------------------

class CreateReportRequest(BaseModel):
    """Payload to submit a suspect entity/identifier report into Smart Registry."""
    reporting_org: str = Field(..., min_length=2, description="Identifier of reporting institution (e.g. BANK_HDFC_01)")
    entity_name: Optional[str] = Field(None, description="Optional entity or suspect trade name")
    category: str = Field(..., description="Fraud category (e.g. MULE_ACCOUNT, KYC_IMPERSONATION, UTILITY_PHISHING)")
    reason: str = Field(..., min_length=5, description="Factual justification for report")
    identifiers: List[TypedIdentifier] = Field(..., min_length=1, description="List of identifiers associated with report")
    evidence_references: List[str] = Field(default_factory=list, description="External reference IDs, I4C complaints, incident IDs")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Reporting institution confidence level")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReviewReportRequest(BaseModel):
    """Payload to review and change status of a registry report."""
    new_status: ReportStatus = Field(..., description="Target status: CONFIRMED, REJECTED, or UNDER_REVIEW")
    reviewer: str = Field(..., min_length=2, description="Identity or badge ID of the compliance officer")
    notes: str = Field(..., min_length=5, description="Justification and review commentary")


class RegistryReport(BaseModel):
    """Full Smart Registry report record."""
    report_id: str
    reporting_org: str
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    category: str
    reason: str
    status: ReportStatus = ReportStatus.REPORTED
    confidence: float = 0.9
    created_at: datetime
    updated_at: datetime
    fingerprints: List[CanonicalFingerprint]
    evidence_references: List[str] = Field(default_factory=list)
    review_history: List[Dict[str, Any]] = Field(default_factory=list)
    active_dispute_id: Optional[str] = None
    revocation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# Screening Schemas
# -----------------------------------------------------------------------------

class ScreenRequest(BaseModel):
    """Payload to screen one or more typed identifiers."""
    caller_org: str = Field(..., min_length=2, description="Identifier of querying institution")
    identifiers: List[TypedIdentifier] = Field(..., min_length=1, max_length=50)
    correlation_id: Optional[str] = None


class ScreeningMatch(BaseModel):
    """Individual match hit returned by screening."""
    identifier_type: IdentifierType
    match_type: MatchType
    matched_fingerprint: str
    entity_id: Optional[str] = None
    report_id: str
    report_status: ReportStatus
    category: str
    reporting_source: str
    reported_at: datetime
    is_disputed: bool
    is_revoked: bool
    risk_score: float
    reason_code: str
    confidence: float
    warnings: List[str] = Field(default_factory=list)
    data_freshness: str = "REALTIME"


class ScreenResponse(BaseModel):
    """Response returned by screening service."""
    screening_id: str
    screened_at: datetime
    caller_org: str
    total_queried: int
    total_hits: int
    has_confirmed_hit: bool
    has_disputed_hit: bool
    has_revoked_hit: bool
    highest_risk_score: float
    matches: List[ScreeningMatch]
    correlation_id: str
    warnings: List[str] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# Disputes, Revocations & Feedback Schemas
# -----------------------------------------------------------------------------

class SubmitDisputeRequest(BaseModel):
    """Payload to contest a report in Smart Registry."""
    report_id: str = Field(..., min_length=3)
    disputing_org: str = Field(..., min_length=2)
    reason: str = Field(..., min_length=10, description="Justification and grounds for disputing report")
    evidence_documents: List[str] = Field(default_factory=list, description="Document or verification references")


class DisputeDecisionRequest(BaseModel):
    """Payload to decide / resolve an open dispute."""
    decision: str = Field(..., description="'UPHELD' (reaffirm report) or 'DISMISSED' (accept dispute, dismiss report)")
    notes: str = Field(..., min_length=5, description="Administrative justification")
    reviewer: str = Field(..., min_length=2, description="Compliance reviewer username")


class ResolveDisputeRequest(BaseModel):
    """Payload to resolve an open dispute (Legacy / Backward Compatibility)."""
    dispute_id: str
    resolution: str = Field(..., description="'UPHELD' (report reaffirmed) or 'DISMISSED' (dispute accepted, report rejected/revoked)")
    resolution_notes: str = Field(..., min_length=5)
    reviewed_by: str = Field(..., min_length=2)


class DisputeRecord(BaseModel):
    """Dispute entity in Smart Registry."""
    dispute_id: str
    report_id: str
    entity_id: Optional[str] = None
    disputing_org: str
    reason: str
    status: str = "OPEN"  # OPEN, UNDER_REVIEW, RESOLVED_UPHELD, RESOLVED_DISMISSED
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    evidence_documents: List[str] = Field(default_factory=list)


class SubmitRevocationRequest(BaseModel):
    """Payload to revoke a previously confirmed report."""
    report_id: str = Field(..., min_length=3)
    authorizing_org: str = Field(..., min_length=2)
    revocation_reason: str = Field(..., min_length=10)
    authorized_by: str = Field(..., min_length=2)


class RevocationDecisionRequest(BaseModel):
    """Payload to approve or reject a revocation request."""
    decision: str = Field(..., description="'APPROVED' or 'REJECTED'")
    notes: str = Field(..., min_length=5)
    reviewer: str = Field(..., min_length=2)


class RevocationRecord(BaseModel):
    """Revocation entity in Smart Registry."""
    revocation_id: str
    report_id: str
    entity_id: Optional[str] = None
    authorizing_org: str
    revocation_reason: str
    authorized_by: str
    revoked_at: datetime
    status: str = "APPROVED"


class RegistryFeedbackRequest(BaseModel):
    """Feedback on screening effectiveness / true vs false positive."""
    screening_id: str
    report_id: str
    outcome: str = Field(..., description="'TRUE_POSITIVE_FRAUD_PREVENTED', 'FALSE_POSITIVE_CLEARED', 'UNDER_INVESTIGATION'")
    feedback_notes: Optional[str] = None
    reporting_org: str


class AuditEvent(BaseModel):
    """Immutable audit event logging all state changes."""
    audit_id: str
    timestamp: datetime
    entity_type: str
    entity_id: str
    action: AuditAction
    actor_org: str
    actor_user: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    reason: Optional[str] = None
    integrity_hash: str


# -----------------------------------------------------------------------------
# System Statistics & Detailed Entity Response
# -----------------------------------------------------------------------------

class RegistryStatistics(BaseModel):
    """Aggregate statistics for Smart Registry."""
    total_entities: int
    total_reports: int
    confirmed_count: int
    under_review_count: int
    disputed_count: int
    revoked_count: int
    screening_count: int
    audit_event_count: int
    active_key_version: str
    supported_identifier_types: List[str]
    system_status: str = "HEALTHY"


class RegistryEntityDetail(BaseModel):
    """Detailed view of a RegistryEntity with linked reports and audit trail."""
    entity: RegistryEntity
    reports: List[RegistryReport]
    audit_trail: List[AuditEvent]
