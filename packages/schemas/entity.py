"""Canonical Entity, Observation, Relationship, and Trust Schemas for ScamGraph AI V2.

Represents atomic, resolved, or observed real-world or digital identifiers:
phones, domains, UPI VPAs, bank account tokens, handles, brands, organizations.
Distinguishes observation, claim, evidence, and trust assessment (Rule 10, Prompt 6).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class EntityType(str, Enum):
    """Supported canonical entity types."""
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    URL = "URL"
    DOMAIN = "DOMAIN"
    UPI_VPA = "UPI_VPA"
    BANK_ACCOUNT_TOKEN = "BANK_ACCOUNT_TOKEN"
    IFSC = "IFSC"
    SOCIAL_ACCOUNT = "SOCIAL_ACCOUNT"
    TELEGRAM_HANDLE = "TELEGRAM_HANDLE"
    WHATSAPP_NUMBER = "WHATSAPP_NUMBER"
    BRAND = "BRAND"
    ORGANIZATION = "ORGANIZATION"
    IP_ADDRESS = "IP_ADDRESS"
    CRYPTO_ADDRESS = "CRYPTO_ADDRESS"
    APP_PACKAGE = "APP_PACKAGE"
    DEVICE_TOKEN = "DEVICE_TOKEN"
    QR_PAYLOAD = "QR_PAYLOAD"
    OTHER = "OTHER"


class EntityVerificationState(str, Enum):
    """Corroboration and verification state of an entity.
    
    Rule: VERIFIED_MALICIOUS requires verified multi-incident corroboration or official reporting.
    Similarity or single unvetted user reports must NOT trigger VERIFIED_MALICIOUS.
    """
    UNKNOWN = "UNKNOWN"
    UNVERIFIED = "UNVERIFIED"
    OBSERVED = "OBSERVED"
    CORROBORATED = "CORROBORATED"
    DISPUTED = "DISPUTED"
    VERIFIED_LEGITIMATE = "VERIFIED_LEGITIMATE"
    VERIFIED_MALICIOUS = "VERIFIED_MALICIOUS"


class EntityObservationRole(str, Enum):
    """Contextual role played by the entity in a specific interaction or artifact."""
    SENDER = "SENDER"
    RECIPIENT = "RECIPIENT"
    PAYMENT_RECIPIENT = "PAYMENT_RECIPIENT"
    PAYMENT_SENDER = "PAYMENT_SENDER"
    CLAIMED_AUTHORITY = "CLAIMED_AUTHORITY"
    CONTACT_POINT = "CONTACT_POINT"
    REDIRECT_TARGET = "REDIRECT_TARGET"
    HOST = "HOST"
    BRAND_REFERENCE = "BRAND_REFERENCE"
    SOCIAL_PROFILE = "SOCIAL_PROFILE"
    SUPPORT_CONTACT = "SUPPORT_CONTACT"
    UNKNOWN = "UNKNOWN"


class EntityRelationshipType(str, Enum):
    """Directed, evidence-backed relationship between two canonical entities.
    
    Rule: NEVER infer SAME_CRIMINAL without authorized judicial evidence.
    Use SHARES_INFRASTRUCTURE, APPEARED_WITH, or RELATED_TO.
    """
    APPEARED_WITH = "APPEARED_WITH"
    CONTACTED = "CONTACTED"
    REDIRECTS_TO = "REDIRECTS_TO"
    HOSTED_ON = "HOSTED_ON"
    REQUESTED_PAYMENT_TO = "REQUESTED_PAYMENT_TO"
    USES_PHONE = "USES_PHONE"
    USES_EMAIL = "USES_EMAIL"
    USES_DOMAIN = "USES_DOMAIN"
    USES_SOCIAL_ACCOUNT = "USES_SOCIAL_ACCOUNT"
    CLAIMS_TO_REPRESENT = "CLAIMS_TO_REPRESENT"
    IMPERSONATES = "IMPERSONATES"
    SHARES_INFRASTRUCTURE = "SHARES_INFRASTRUCTURE"
    OBSERVED_IN = "OBSERVED_IN"
    RELATED_TO = "RELATED_TO"


class TrustLevel(str, Enum):
    """Multi-dimensional evidence-aware trust outcomes (Rule: Avoid binary malicious/safe)."""
    KNOWN_LEGITIMATE = "KNOWN_LEGITIMATE"
    LIKELY_LEGITIMATE = "LIKELY_LEGITIMATE"
    UNKNOWN = "UNKNOWN"
    CAUTION = "CAUTION"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH_RISK"
    DISPUTED = "DISPUTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class EntityObservation(BaseModel):
    """Contextual sighting of an entity within an artifact, event, or incident."""
    observation_id: str = Field(default_factory=lambda: generate_id("obs"), description="Unique observation ID")
    entity_id: str = Field(..., description="Canonical entity ID")
    incident_id: str = Field(..., description="Associated incident ID")
    artifact_id: Optional[str] = Field(default=None, description="Source artifact ID")
    event_id: Optional[str] = Field(default=None, description="Interaction event ID")
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    channel: str = Field(default="SMS", description="Channel: SMS, WHATSAPP, TELEGRAM, EMAIL, WEB, UPI, etc.")
    source: str = Field(default="USER_REPORT", description="Observation origin: USER_REPORT, HONEYPOT, ANALYST, etc.")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual snippet, claimed purpose, surrounding text")
    role: EntityObservationRole = Field(default=EntityObservationRole.UNKNOWN, description="Entity role in sighting")
    evidence_id: Optional[str] = Field(default=None, description="Linked EvidenceSignal ID")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Observation extraction confidence")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EntityRelationship(BaseModel):
    """Directed edge linking two entities supported by explicit evidence."""
    relationship_id: str = Field(default_factory=lambda: generate_id("rel"), description="Unique relationship ID")
    source_entity_id: str = Field(..., description="Source entity ID")
    target_entity_id: str = Field(..., description="Target entity ID")
    relationship_type: EntityRelationshipType = Field(..., description="Semantic relationship type")
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    observation_count: int = Field(default=1, ge=1, description="Number of times this co-occurrence was observed")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of corroborating evidence signals")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    verification_state: EntityVerificationState = Field(default=EntityVerificationState.OBSERVED)
    created_by: str = Field(default="RULE", description="RULE, MODEL, HUMAN, EXTERNAL_SOURCE")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TrustAssessment(BaseModel):
    """Evidence-aware reputation and trust evaluation of an entity."""
    entity_id: str
    assessment: TrustLevel
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence_count: int = 0
    contradicting_evidence_count: int = 0
    reputation_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Normalized risk score [0.0 - 1.0]")
    decay_applied: bool = False
    freshness_status: str = "FRESH"
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = "v2.0.0"
    summary_reason: str = ""


class EntityClaim(BaseModel):
    """An asserted claim regarding an entity, backed by supporting/contradicting evidence."""
    claim_id: str = Field(default_factory=lambda: generate_id("clm"))
    entity_id: str
    statement: str
    polarity: str = Field(default="SUPPORTS", description="SUPPORTS or CONTRADICTS")
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    asserted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EntityMergeRecord(BaseModel):
    """Audit log tracking canonical entity consolidation (preserves lineage)."""
    merge_id: str = Field(default_factory=lambda: generate_id("mrg"))
    canonical_entity_id: str
    merged_entity_ids: List[str]
    reason: str
    evidence_ids: List[str] = Field(default_factory=list)
    merged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    can_split: bool = True


class EntitySplitRecord(BaseModel):
    """Audit log reversing an erroneous entity merge."""
    split_id: str = Field(default_factory=lambda: generate_id("splt"))
    original_entity_id: str
    resulting_entity_ids: List[str]
    reason: str
    split_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Entity(BaseModel):
    """Canonical Entity contract supporting privacy-preserving correlation across incidents."""
    entity_id: str = Field(default_factory=lambda: generate_id("ent"), description="Stable opaque entity ID")
    schema_version: str = Field(default="2.0", description="Contract schema version")
    entity_type: EntityType = Field(..., description="Classification of the entity")
    canonical_value: Optional[str] = Field(
        default=None, 
        description="Internal normalized value for system processing. Never expose unmasked PII publicly."
    )
    display_value: Optional[str] = Field(
        default=None, 
        description="Formatted value safe for UI presentation"
    )
    masked_value: str = Field(..., description="Securely masked representation (e.g. ******3210, n***@oksbi)")
    canonical_hash: str = Field(..., description="Deterministic cryptographic SHA-256 or HMAC hash of normalized value")
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    observation_count: int = Field(default=1, ge=0, description="Total number of times observed across all sources")
    incident_count: int = Field(default=1, ge=0, description="Number of unique correlated incidents linked to this entity")
    campaign_count: int = Field(default=0, ge=0, description="Number of campaigns this entity belongs to")
    supporting_evidence_count: int = Field(default=0, ge=0, description="Number of corroborating scam evidence signals")
    contradicting_evidence_count: int = Field(default=0, ge=0, description="Number of counter-evidence / legitimate signals")
    verification_state: EntityVerificationState = Field(
        default=EntityVerificationState.OBSERVED,
        description="Verification and trust lifecycle state"
    )
    risk_summary: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Aggregated risk scores and confidence across all sightings"
    )
    confidence_summary: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Confidence metrics and observation weights"
    )
    reputation_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Evidence-weighted reputation scores and decay factors"
    )
    aliases: List[str] = Field(default_factory=list, description="Resolved alias values or legacy entity IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Contextual tags, telecom circles, registrar info")
