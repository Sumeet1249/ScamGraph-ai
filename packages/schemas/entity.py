"""Canonical Entity Schema for ScamGraph AI V2.

Represents an atomic, resolved, or observed real-world or digital identifier:
phones, domains, UPI VPAs, bank accounts, handles, and brands.
"""

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
    SOCIAL_ACCOUNT = "SOCIAL_ACCOUNT"
    TELEGRAM_HANDLE = "TELEGRAM_HANDLE"
    WHATSAPP_NUMBER = "WHATSAPP_NUMBER"
    BRAND = "BRAND"
    ORGANIZATION = "ORGANIZATION"
    IP_ADDRESS = "IP_ADDRESS"
    CRYPTO_ADDRESS = "CRYPTO_ADDRESS"
    DEVICE_TOKEN = "DEVICE_TOKEN"
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


class Entity(BaseModel):
    """Canonical Entity contract supporting privacy-preserving correlation."""
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
    incident_count: int = Field(default=1, ge=0, description="Number of correlated incidents linked to this entity")
    campaign_count: int = Field(default=0, ge=0, description="Number of campaigns this entity belongs to")
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
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Contextual tags, telecom circles, registrar info")
