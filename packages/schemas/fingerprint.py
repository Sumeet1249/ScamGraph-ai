"""Scam Fingerprint Schemas for ScamGraph AI (Step 25).

Represents invariant multi-attribute behavioral signatures used to recognize
scam variants even when phone numbers, domains, or payment handles mutate.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class ScamFingerprint(BaseModel):
    """Invariant behavioral fingerprint of a scam incident or campaign cluster (V1)."""

    fingerprint_id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str
    semantic_embedding: Optional[List[float]] = Field(default=None, description="Dense vector embedding (e.g. 384 dims)")
    claimed_identity: Optional[str] = Field(default=None, description="Purported institution (e.g. SBI, Electricity Board)")
    social_engineering_tactics: List[str] = Field(default_factory=list, description="Extracted psychological tactics")
    requested_action: Optional[str] = Field(default=None, description="What the attacker demands the victim perform")
    stage_sequence: List[str] = Field(default_factory=list, description="Ordered stages observed")
    temporal_pace_seconds: int = Field(default=0, description="Elapsed seconds across the stage progression")
    url_lexical_markers: List[str] = Field(default_factory=list, description="Lexical traits of associated URLs")
    web_behavior: Dict[str, Any] = Field(default_factory=dict, description="Forms, OTP traps, or APK payloads")
    infrastructure_hash: Dict[str, Any] = Field(default_factory=dict, description="ASN, registrar, nameserver traits")
    payment_profile: Dict[str, Any] = Field(default_factory=dict, description="VPA PSP, merchant vs personal type")
    campaign_match_id: Optional[str] = Field(default=None, description="Matched historical campaign cluster")
    similarity_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScamFingerprintV2(BaseModel):
    """Enhanced Multi-Dimensional Behavioral Fingerprint (V2).

    Unifies Semantic, Temporal Journey, Infrastructure, Graph, and Payment intelligence.
    """

    fingerprint_id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str
    semantic_vector_reference: Optional[str] = Field(default=None, description="Vector ID or reference in pgvector")
    semantic_embedding: Optional[List[float]] = Field(default=None, description="384/1024-dim dense representation vector")
    semantic_features: Dict[str, Any] = Field(default_factory=dict, description="Linguistic markers, urgency keywords, intent")
    ordered_event_sequence: List[str] = Field(default_factory=list, description="Ordered sequence of canonical event types")
    event_time_gaps: List[int] = Field(default_factory=list, description="Time deltas between consecutive events in seconds")
    social_engineering_tactics: List[str] = Field(default_factory=list, description="Psychological levers: URGENCY, AUTHORITY, FEAR, LURE")
    claimed_identity: Optional[str] = Field(default=None, description="Impersonated entity: SBI, HDFC, Discom, Police, etc.")
    requested_actions: List[str] = Field(default_factory=list, description="Actions demanded of victim: UPDATE_KYC, SUBMIT_OTP, PAY")
    pattern_matches: List[str] = Field(default_factory=list, description="Matched fraud patterns: KYC_IMPERSONATION, etc.")
    URL_features: Dict[str, Any] = Field(default_factory=dict, description="Lexical, domain age, typosquatting, redirect count")
    TinyFish_observations: Dict[str, Any] = Field(default_factory=dict, description="Live DOM observations: has_otp_form, credential_input")
    infrastructure_entities: Dict[str, Any] = Field(default_factory=dict, description="Domain, IP, ASN, nameserver, certificate")
    payment_entities: Dict[str, Any] = Field(default_factory=dict, description="Target VPA, bank account, payment channel")
    graph_community: Optional[str] = Field(default=None, description="Neo4j candidate campaign community cluster ID")
    graph_features: Dict[str, Any] = Field(default_factory=dict, description="Degree centrality, shared entity counts, hub status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FingerprintSimilarityResult(BaseModel):
    """Detailed explainable breakdown of multi-dimensional fingerprint similarity."""

    semantic_similarity: float = Field(..., ge=0.0, le=1.0)
    journey_similarity: float = Field(..., ge=0.0, le=1.0)
    infrastructure_similarity: float = Field(..., ge=0.0, le=1.0)
    payment_similarity: float = Field(..., ge=0.0, le=1.0)
    pattern_similarity: float = Field(..., ge=0.0, le=1.0)
    identifier_overlap: float = Field(..., ge=0.0, le=1.0)
    overall_similarity_index: float = Field(..., ge=0.0, le=1.0)
    matched_dimensions: List[str] = Field(default_factory=list)
    different_dimensions: List[str] = Field(default_factory=list)
    shared_entities: List[str] = Field(default_factory=list)
    shared_patterns: List[str] = Field(default_factory=list)
    sequence_alignment: Dict[str, Any] = Field(default_factory=dict)
    explanation: str = ""

    @property
    def overall_similarity(self) -> float:
        return self.overall_similarity_index

    @property
    def sequence_similarity(self) -> float:
        return self.journey_similarity
