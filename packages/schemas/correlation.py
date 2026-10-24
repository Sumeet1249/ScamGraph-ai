"""Canonical Pydantic Schemas for Cross-Victim & Cross-Incident Correlation Engine (Phase 3B).

Provides typed contracts for multi-signal relationship scoring, privacy-safe consumer network alerts,
analyst correlation views, and candidate campaign groupings.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RelationshipStatus(str, Enum):
    """Categorical classification of cross-incident relationship."""
    NOT_RELATED = "NOT_RELATED"
    WEAK_SIGNAL = "WEAK_SIGNAL"
    POSSIBLY_RELATED = "POSSIBLY_RELATED"
    LIKELY_RELATED_PATTERN = "LIKELY_RELATED_PATTERN"
    STRONGLY_RELATED = "STRONGLY_RELATED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class EvidenceStrength(str, Enum):
    """Qualitative strength of supporting correlation evidence."""
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


class RelationshipEvidenceType(str, Enum):
    """Independent evidence classes for correlation."""
    ENTITY = "ENTITY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    BEHAVIORAL = "BEHAVIORAL"
    TEMPORAL = "TEMPORAL"
    GRAPH = "GRAPH"
    SEMANTIC = "SEMANTIC"
    PAYMENT = "PAYMENT"


class ConsumerNetworkSignalType(str, Enum):
    """Consumer-safe network warning tier (zero victim disclosure)."""
    NO_NETWORK_SIGNAL = "NO_NETWORK_SIGNAL"
    SIMILAR_PATTERN_OBSERVED = "SIMILAR_PATTERN_OBSERVED"
    ENTITY_REPORTED_ELSEWHERE = "ENTITY_REPORTED_ELSEWHERE"
    MULTIPLE_RELATED_SIGNALS = "MULTIPLE_RELATED_SIGNALS"
    EMERGING_PATTERN = "EMERGING_PATTERN"


class CorrelationFeatures(BaseModel):
    """Normalized multi-dimensional correlation feature vector."""
    exact_payment_overlap: float = 0.0
    exact_phone_overlap: float = 0.0
    exact_domain_overlap: float = 0.0
    exact_social_overlap: float = 0.0
    weighted_entity_overlap: float = 0.0
    infrastructure_similarity: float = 0.0
    dna_similarity: float = 0.0
    dna_coverage: float = 0.0
    journey_similarity: float = 0.0
    tactic_similarity: float = 0.0
    semantic_similarity: float = 0.0
    temporal_similarity: float = 0.0
    graph_path_score: float = 0.0
    shared_rare_entity_count: int = 0
    shared_common_entity_count: int = 0
    contradiction_score: float = 0.0
    evidence_quality: float = 0.80


class IncidentCorrelation(BaseModel):
    """Canonical cross-incident correlation record between two incidents."""
    correlation_id: str
    source_incident_id: str
    target_incident_id: str
    relationship_status: RelationshipStatus = RelationshipStatus.INSUFFICIENT_EVIDENCE
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_strength: EvidenceStrength = EvidenceStrength.WEAK
    feature_scores: Dict[str, float] = Field(default_factory=dict)
    shared_entities: List[Dict[str, Any]] = Field(default_factory=list)
    shared_infrastructure: List[str] = Field(default_factory=list)
    dna_similarity: Optional[float] = None
    journey_similarity: Optional[float] = None
    tactic_similarity: Optional[float] = None
    semantic_similarity: Optional[float] = None
    temporal_similarity: Optional[float] = None
    graph_similarity: Optional[float] = None
    positive_reasons: List[str] = Field(default_factory=list)
    negative_reasons: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    first_calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = "3.2.0"
    feature_version: str = "2.0.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CandidateIncident(BaseModel):
    """Candidate incident discovered during Stage 1 retrieval."""
    incident_id: str
    source_reasons: List[str] = Field(default_factory=list)
    retrieval_score: float = 0.0
    shared_identifiers: List[str] = Field(default_factory=list)
    dna_id: Optional[str] = None
    scam_family: Optional[str] = None
    observed_at: Optional[datetime] = None


class ConsumerNetworkSignal(BaseModel):
    """Privacy-safe aggregate network alert for end consumers (No victim PII)."""
    incident_id: str
    network_signal: ConsumerNetworkSignalType
    headline: str
    explanation_bullets: List[str] = Field(default_factory=list)
    related_reports_band: str  # e.g. "MULTIPLE_REPORTS", "SEVERAL_REPORTS", "NO_PRIOR_REPORTS"
    display_stage: Optional[str] = None
    warning_level: str = "CAUTION"
    recommended_actions: List[str] = Field(default_factory=list)
    is_aggregate_safe: bool = True


class AnalystCorrelationView(BaseModel):
    """Comprehensive technical correlation view for authorized fraud analysts."""
    correlation: IncidentCorrelation
    feature_breakdown: Dict[str, float]
    group_contributions: Dict[str, float]
    explainable_graph_paths: List[str] = Field(default_factory=list)
    comparison_coverage: float = 1.0
    audit_trail: List[str] = Field(default_factory=list)


class CandidateIncidentGroup(BaseModel):
    """Group of correlated incidents forming a campaign candidate (Prompt 12 input)."""
    group_id: str
    member_incident_ids: List[str] = Field(default_factory=list)
    relationship_density: float = 0.0
    strong_edge_count: int = 0
    evidence_diversity: List[str] = Field(default_factory=list)
    primary_family: str = "UNKNOWN"
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    growth_velocity: float = 0.0
