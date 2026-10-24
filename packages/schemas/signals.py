"""Canonical Evidence Signal Schemas for ScamGraph AI.

Represents typed evidence produced by detectors, ML models, or external lookups.
Strict Rule: No single signal declares fraud.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class SignalDimension(str, Enum):
    """The seven correlation dimensions of ScamGraph AI."""
    SEMANTIC = "SEMANTIC"
    URL = "URL"
    PAYMENT = "PAYMENT"
    TEMPORAL = "TEMPORAL"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    HISTORICAL = "HISTORICAL"
    CAMPAIGN = "CAMPAIGN"


class SignalSeverity(str, Enum):
    """Graded severity for individual signals."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProvenanceRecord(BaseModel):
    """Tracks complete origin and audit trail for every finding."""
    source_service: str = Field(..., description="Service producing the signal (e.g. services/investigation)")
    detector_name: str = Field(..., description="Model, rule, or provider name (e.g. TinyFish API, NLP Urgency)")
    target_artifact: str = Field(..., description="Entity or payload snippet evaluated")
    raw_evidence: Dict[str, Any] = Field(default_factory=dict, description="Detailed extractor telemetry or outputs")
    
    # V2 Lineage & Governance extensions (all optional to preserve legacy callers)
    source_category: Optional[str] = Field(default=None, description="Category (e.g. ML_MODEL, HEURISTIC, OSINT, REPUTATION)")
    provider: Optional[str] = Field(default=None, description="Model provider or service name")
    model_id: Optional[str] = Field(default=None, description="Registered model ID in model registry")
    model_version: Optional[str] = Field(default=None, description="Version or checkpoint revision")
    collection_timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence_timestamp: Optional[datetime] = Field(default=None)
    reliability_score: float = Field(default=1.0, ge=0.0, le=1.0)
    content_hash: Optional[str] = Field(default=None, description="SHA-256 hash of evaluated target")
    reference_uri: Optional[str] = Field(default=None)
    redaction_status: str = Field(default="NONE", description="NONE, MASKED, PSEUDONYMIZED, HASHED")


class EvidenceSignal(BaseModel):
    """Canonical Evidence Signal representing an atomic finding."""
    signal_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique signal ID")
    incident_id: str = Field(..., description="Associated incident ID")
    event_id: Optional[str] = Field(default=None, description="Event from which the signal was extracted, if any")
    dimension: SignalDimension
    signal_type: str = Field(..., description="Descriptive code (e.g. URGENCY_PRESSURE, TYPOSQUATTING_DOMAIN)")
    severity: SignalSeverity = Field(default=SignalSeverity.MEDIUM)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Local model/extractor confidence (0.0 to 1.0)")
    weight: float = Field(default=1.0, ge=0.1, description="Relative impact weight in fusion formula")
    is_counter_evidence: bool = Field(default=False, description="True if this signal indicates safety/legitimacy")
    description: str = Field(..., description="Human-readable explanation of why this signal was flagged")
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provenance: ProvenanceRecord

    @property
    def context(self) -> Dict[str, Any]:
        """Convenience property accessing provenance.raw_evidence."""
        return self.provenance.raw_evidence
