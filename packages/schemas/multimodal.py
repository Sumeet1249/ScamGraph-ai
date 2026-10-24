"""Canonical Pydantic Schemas for Multimodal Intelligence V2 (Prompt 18 / Phase 5D).

Provides contracts for:
- Screenshot OCR & Structural Region Analysis
- QR Decoding & Safe UPI Payload Parsing
- Payment Screenshot Extraction & Status Verification
- Document Claim Extraction
- Voice / Audio Speech-to-Text & Transcript Artifacts
- Derived Observations with strict Evidence Lineage
- Evidence Fusion Engine (independent source groups, double-counting prevention)
- Synthetic Media Signals & Tampering Analysis
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id
from packages.schemas.tactics import ActionRequestedType, TacticType


class MultimodalModality(str, Enum):
    """Supported input modalities."""
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    SCREENSHOT = "SCREENSHOT"
    QR_IMAGE = "QR_IMAGE"
    PAYMENT_SCREENSHOT = "PAYMENT_SCREENSHOT"
    SOCIAL_SCREENSHOT = "SOCIAL_SCREENSHOT"
    EMAIL_SCREENSHOT = "EMAIL_SCREENSHOT"
    WEBSITE_SCREENSHOT = "WEBSITE_SCREENSHOT"
    DOCUMENT_IMAGE = "DOCUMENT_IMAGE"
    AUDIO = "AUDIO"
    VOICE_NOTE = "VOICE_NOTE"
    CALL_RECORDING = "CALL_RECORDING"
    TRANSCRIPT = "TRANSCRIPT"
    UNKNOWN = "UNKNOWN"


class ScreenshotCategory(str, Enum):
    """Categorization of screenshot visual layout."""
    CHAT = "CHAT"
    SMS = "SMS"
    EMAIL = "EMAIL"
    PAYMENT = "PAYMENT"
    SOCIAL_PROFILE = "SOCIAL_PROFILE"
    WEBSITE = "WEBSITE"
    BROWSER_WARNING = "BROWSER_WARNING"
    DOCUMENT = "DOCUMENT"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class QRPayloadType(str, Enum):
    """Classification of decoded QR content."""
    UPI_PAYMENT = "UPI_PAYMENT"
    URL = "URL"
    TEXT = "TEXT"
    CONTACT = "CONTACT"
    APP_LINK = "APP_LINK"
    UNKNOWN = "UNKNOWN"


class ObservationType(str, Enum):
    """Types of derived atomic evidence observations."""
    TEXT_SPAN = "TEXT_SPAN"
    UPI_VPA = "UPI_VPA"
    PAYMENT_AMOUNT = "PAYMENT_AMOUNT"
    PHONE_NUMBER = "PHONE_NUMBER"
    URL = "URL"
    DOMAIN = "DOMAIN"
    BRAND_MENTION = "BRAND_MENTION"
    CLAIMED_IDENTITY = "CLAIMED_IDENTITY"
    TRANSACTION_REFERENCE = "TRANSACTION_REFERENCE"
    TACTIC_EVIDENCE = "TACTIC_EVIDENCE"
    REQUESTED_ACTION = "REQUESTED_ACTION"
    JOURNEY_STAGE = "JOURNEY_STAGE"
    MEDIA_TAMPERING = "MEDIA_TAMPERING"


class OCRBoundingBox(BaseModel):
    """Relative or pixel coordinates bounding box."""
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0


class OCRTextBlock(BaseModel):
    """Individual recognized text block within an image."""
    text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bounding_box: Optional[OCRBoundingBox] = None
    language_hint: Optional[str] = None


class OCRResult(BaseModel):
    """Structured OCR extraction output."""
    full_text: str
    blocks: List[OCRTextBlock] = Field(default_factory=list)
    overall_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    detected_script: str = "LATIN"
    provider: str = "LocalOCR"
    model_version: str = "2.0.0"
    raw_rotation_degrees: float = 0.0


class UPIQRPayload(BaseModel):
    """Structured fields safely extracted from a upi://pay URI."""
    vpa: str
    name_claim: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "INR"
    transaction_note: Optional[str] = None
    merchant_code: Optional[str] = None
    transaction_ref: Optional[str] = None
    raw_uri: str


class QRDecodeResult(BaseModel):
    """Decoded QR payload and metadata."""
    payload: str
    payload_type: QRPayloadType = QRPayloadType.UNKNOWN
    upi_details: Optional[UPIQRPayload] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bounding_box: Optional[OCRBoundingBox] = None
    decoder_name: str = "StandardQRDecoder"


class PaymentScreenshotExtraction(BaseModel):
    """Extracted financial indicators from payment receipts and wallet screenshots."""
    amount: Optional[float] = None
    currency: str = "INR"
    recipient_claim: Optional[str] = None
    vpa: Optional[str] = None
    reference_id: Optional[str] = None
    payment_status_claim: str = "UNKNOWN"  # SUCCESSFUL, PENDING, FAILED, UNKNOWN
    date_time_claim: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    raw_text: str = ""


class AudioTranscriptSegment(BaseModel):
    """Timestamped segment in a speech transcription."""
    start_ms: int = 0
    end_ms: int = 0
    speaker_tag: str = "SPEAKER_UNKNOWN"
    text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    language: str = "eng"


class TranscriptArtifact(BaseModel):
    """Full derived transcription of an audio recording."""
    full_transcript: str
    segments: List[AudioTranscriptSegment] = Field(default_factory=list)
    duration_seconds: float = 0.0
    primary_language: str = "eng"
    is_code_mixed: bool = False
    provider: str = "SpeechToTextAdapter"
    model_version: str = "2.0.0"
    overall_confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class SyntheticMediaSignal(BaseModel):
    """Carefully bounded signal regarding media authenticity or voice cloning."""
    state: str = "NOT_ANALYZED"  # NOT_ANALYZED, NO_STRONG_SIGNAL, POSSIBLE_SYNTHETIC, LIKELY_SYNTHETIC, INCONCLUSIVE
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    rationale: str = "Audio analyzed for behavioral manipulation patterns; authenticity unverified."
    safe_action_guidance: str = "Verify caller identity via a trusted independent channel."


class DerivedObservation(BaseModel):
    """Atomic derived piece of intelligence linked immutably to a source artifact."""
    observation_id: str = Field(default_factory=lambda: generate_id("obs"))
    source_artifact_id: str
    incident_id: str
    modality: MultimodalModality
    observation_type: ObservationType
    raw_value: str
    normalized_value: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bounding_box: Optional[OCRBoundingBox] = None
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None
    extractor_name: str
    extractor_version: str = "2.0.0"
    evidence_ids: List[str] = Field(default_factory=list)
    lineage_parent_ids: List[str] = Field(default_factory=list, description="IDs of upstream derived observations to prevent double-counting")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceFusionResult(BaseModel):
    """Fused multimodal intelligence avoiding double-counting of derived artifacts."""
    incident_id: str
    observations: List[DerivedObservation] = Field(default_factory=list)
    independent_source_groups: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Maps independent source roots to their derived child observation IDs"
    )
    corroborating_claims: List[str] = Field(default_factory=list)
    contradicting_claims: List[str] = Field(default_factory=list)
    coverage_score: float = Field(default=0.5, ge=0.0, le=1.0)
    fusion_confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    double_counting_prevented_count: int = 0
    fusion_version: str = "2.0.0"
