"""ScamDNA V3 Schemas for ScamGraph AI (Step 9).

Multi-Dimensional Behavioral Fingerprinting, Invariant Scam Signatures,
and Cross-Variant Alignment schemas across 8 decoupled dimensions.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class DNADimensionType(str, Enum):
    """The 8 decoupled behavioral dimensions of ScamDNA V3."""
    SEMANTIC = "SEMANTIC"
    JOURNEY = "JOURNEY"
    TACTIC = "TACTIC"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    PAYMENT = "PAYMENT"
    IDENTITY = "IDENTITY"
    TEMPORAL = "TEMPORAL"
    GRAPH = "GRAPH"


class DNAQuality(str, Enum):
    """Quality rating based on dimensional completeness and provenance."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class VariantStatus(str, Enum):
    """Calibrated behavioral relationship classification."""
    KNOWN_PATTERN = "KNOWN_PATTERN"
    LIKELY_VARIANT = "LIKELY_VARIANT"
    POSSIBLE_VARIANT = "POSSIBLE_VARIANT"
    NOVEL_PATTERN = "NOVEL_PATTERN"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class DNADimension(BaseModel):
    """Atomic representation of a single behavioral DNA dimension."""
    dimension: DNADimensionType
    available: bool = True
    quality: DNAQuality = DNAQuality.MEDIUM
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    features: Dict[str, Any] = Field(default_factory=dict, description="Privacy-safe invariant structural features")
    vector_reference: Optional[str] = Field(default=None, description="Vector ID in pgvector if persisted")
    vector_embedding: Optional[List[float]] = Field(default=None, description="Dense embedding vector if applicable")
    evidence_ids: List[str] = Field(default_factory=list, description="Associated evidence signal references")
    engine_version: str = Field(default="3.0.0")


class ScamDNA(BaseModel):
    """Canonical ScamDNA V3 Behavioral Fingerprint."""
    dna_id: str = Field(default_factory=lambda: f"dna_{uuid4().hex[:12]}")
    schema_version: str = Field(default="3.0")
    incident_id: str
    family_hypotheses: Dict[str, float] = Field(default_factory=dict, description="Probabilistic family distribution")
    dimensions: Dict[str, DNADimension] = Field(default_factory=dict, description="Keyed by DNADimensionType value")
    available_dimensions: List[str] = Field(default_factory=list)
    missing_dimensions: List[str] = Field(default_factory=list)
    quality: DNAQuality = DNAQuality.MEDIUM
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    canonical_signature: str = Field(default="", description="Explainable behavioral string representation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = Field(default="3.0.0")
    source_versions: Dict[str, str] = Field(default_factory=dict, description="Provenance versions of upstream engines")
    evidence_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_dimension(self, dim: DNADimensionType) -> Optional[DNADimension]:
        """Safely retrieves dimension if present and available."""
        d = self.dimensions.get(dim.value)
        return d if (d and d.available) else None


class ScamDNAMatch(BaseModel):
    """Detailed explainable breakdown of multi-dimensional DNA comparison."""
    match_id: str = Field(default_factory=lambda: f"dnam_{uuid4().hex[:12]}")
    source_dna_id: str
    target_dna_id: str
    overall_similarity: float = Field(..., ge=0.0, le=1.0)
    match_confidence: float = Field(..., ge=0.0, le=1.0)
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    available_comparison_dimensions: List[str] = Field(default_factory=list)
    missing_comparison_dimensions: List[str] = Field(default_factory=list)
    matched_features: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    variant_status: VariantStatus = VariantStatus.INSUFFICIENT_EVIDENCE
    reason_codes: List[str] = Field(default_factory=list)
    explanation: str = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = Field(default="3.0.0")


class ConsumerDNAView(BaseModel):
    """Privacy-safe plain-language summary for consumer interfaces."""
    incident_id: str
    summary_headline: str
    variant_verdict: str
    why_it_matches: List[str] = Field(default_factory=list)
    behavioral_traits: List[str] = Field(default_factory=list)
    recommended_action: str
    confidence_label: str
