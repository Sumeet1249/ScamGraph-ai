"""Canonical Artifact Schema for ScamGraph AI V2.

Represents an individual submitted, observed, or ingested digital artifact across any communication channel.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import PrivacyClassification, generate_id


class ArtifactType(str, Enum):
    """Supported digital artifact modalities."""
    MESSAGE = "MESSAGE"
    URL = "URL"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    QR = "QR"
    PAYMENT_REQUEST = "PAYMENT_REQUEST"
    SOCIAL_PROFILE = "SOCIAL_PROFILE"
    SCREENSHOT = "SCREENSHOT"
    VOICE_TRANSCRIPT = "VOICE_TRANSCRIPT"
    DOCUMENT = "DOCUMENT"
    WEB_PAGE = "WEB_PAGE"
    OTHER = "OTHER"


class Artifact(BaseModel):
    """Canonical Artifact contract representing raw observed evidence."""
    artifact_id: str = Field(default_factory=lambda: generate_id("art"), description="Stable opaque artifact identifier")
    schema_version: str = Field(default="2.0", description="Contract schema version")
    artifact_type: ArtifactType = Field(..., description="Modality of the artifact")
    channel: str = Field(default="UNKNOWN", description="Channel observed on (SMS, WHATSAPP, TELEGRAM, CALL, WEB, UPI)")
    content_reference: Optional[str] = Field(
        default=None, 
        description="Object storage URI or file hash pointer for binary assets (e.g. screenshots/documents)"
    )
    normalized_content: Optional[str] = Field(
        default=None, 
        description="Text or canonical string representation for safe analysis"
    )
    language: Optional[str] = Field(default=None, description="ISO language code or dialect (e.g. en, hi, hinglish)")
    script: Optional[str] = Field(default=None, description="Script encoding (e.g. Latin, Devanagari)")
    code_mixed: bool = Field(default=False, description="True if text mixes multiple languages or scripts")
    transliterated: bool = Field(default=False, description="True if text is phonetic transliteration")
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of observation")
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of system ingestion")
    source: str = Field(default="USER_SUBMISSION", description="Origin of artifact (USER_SUBMISSION, PARTNER_API, CRAWLER)")
    privacy_classification: PrivacyClassification = Field(
        default=PrivacyClassification.INTERNAL,
        description="PII sensitivity classification for access control"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary non-PII contextual metadata")
