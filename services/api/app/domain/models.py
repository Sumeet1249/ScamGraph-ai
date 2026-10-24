"""Canonical Domain Models for ScamGraph AI (Step 10).

Provides unified data contracts shared across TinyFish, ML, Neo4j, URL Intelligence,
and Semantic Signal Processing.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from services.api.app.domain.enums import (
    ConfidenceLevel,
    EntityType,
    EventType,
    EvidenceSource,
    IncidentStatus,
    InterventionType,
    MatchLevel,
    RiskLevel,
)


def validate_tz_aware(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensure timestamp is explicitly timezone-aware."""
    if dt is not None and (dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None):
        raise ValueError("Timestamp must be timezone-aware.")
    return dt


def validate_uuid_str(val: str) -> str:
    """Ensure ID is non-empty and UUID or valid identifier format."""
    if not val or not val.strip():
        raise ValueError("ID cannot be empty.")
    # Attempt parsing as UUID or valid prefixed identifier
    clean = val.strip()
    try:
        UUID(clean)
    except ValueError:
        # Allow canonical prefixed IDs like 'inc_...', 'ev_...', 'sig_...'
        if len(clean) < 3:
            raise ValueError(f"ID '{val}' is too short to be a valid identifier.")
    return clean


# ─────────────────────────────────────────────────────────────────────────────
# 1. INCIDENT
# ─────────────────────────────────────────────────────────────────────────────
class Incident(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime
    updated_at: datetime
    status: IncidentStatus = IncidentStatus.OPEN
    title: str = Field(..., min_length=1)
    source: str = Field(default="USER_REPORT")
    owner_id: Optional[str] = Field(default=None, description="Consumer owner user ID")
    org_id: Optional[str] = Field(default=None, description="Enterprise tenant organization ID")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def check_id(cls, v: str) -> str:
        return validate_uuid_str(v)

    @field_validator("created_at", "updated_at")
    @classmethod
    def check_tz(cls, v: datetime) -> datetime:
        return validate_tz_aware(v)  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# 2. EVENT
# ─────────────────────────────────────────────────────────────────────────────
class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str
    timestamp: datetime
    event_type: EventType
    source: EvidenceSource = EvidenceSource.USER_INPUT
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    payload: Dict[str, Any] = Field(default_factory=dict)
    evidence_ids: List[str] = Field(default_factory=list)

    @field_validator("id", "incident_id")
    @classmethod
    def check_ids(cls, v: str) -> str:
        return validate_uuid_str(v)

    @field_validator("timestamp")
    @classmethod
    def check_tz(cls, v: datetime) -> datetime:
        return validate_tz_aware(v)  # type: ignore

    @field_validator("evidence_ids")
    @classmethod
    def check_evidence_ids(cls, v: List[str]) -> List[str]:
        return [validate_uuid_str(e_id) for e_id in v]

    def __lt__(self, other: "Event") -> bool:
        """Support explicit temporal ordering of events."""
        if not isinstance(other, Event):
            return NotImplemented
        return self.timestamp < other.timestamp


# ─────────────────────────────────────────────────────────────────────────────
# 3. ENTITY
# ─────────────────────────────────────────────────────────────────────────────
class Entity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    entity_type: EntityType
    normalized_value: str = Field(..., min_length=1)
    display_value: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def check_id(cls, v: str) -> str:
        return validate_uuid_str(v)

    @field_validator("metadata")
    @classmethod
    def reject_credentials(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Strict Rule: Do not store secrets, passwords, or PINs in entity metadata."""
        prohibited = {"password", "pin", "otp", "cvv", "secret_key"}
        for k in v.keys():
            if k.lower() in prohibited:
                raise ValueError(f"Prohibited sensitive credential field in entity metadata: '{k}'")
        return v


# ─────────────────────────────────────────────────────────────────────────────
# 4. EVIDENCE
# ─────────────────────────────────────────────────────────────────────────────
class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str
    source: EvidenceSource
    signal: str = Field(..., min_length=1)
    observation: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime
    entity_ids: List[str] = Field(default_factory=list)
    event_ids: List[str] = Field(default_factory=list)
    source_reference: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "incident_id")
    @classmethod
    def check_ids(cls, v: str) -> str:
        return validate_uuid_str(v)

    @field_validator("timestamp")
    @classmethod
    def check_tz(cls, v: datetime) -> datetime:
        return validate_tz_aware(v)  # type: ignore

    @field_validator("entity_ids", "event_ids")
    @classmethod
    def check_uuid_lists(cls, v: List[str]) -> List[str]:
        return [validate_uuid_str(x) for x in v]

    @field_validator("observation", "signal")
    @classmethod
    def reject_final_verdicts(cls, v: str) -> str:
        """Rule: Evidence represents an observation and MUST NOT contain a final scam verdict."""
        lower_v = v.lower()
        if "final verdict: scam" in lower_v or "conclusive scam verdict" in lower_v:
            raise ValueError("Evidence must represent objective observations, not final verdicts.")
        return v


# ─────────────────────────────────────────────────────────────────────────────
# 5. RELATIONSHIP
# ─────────────────────────────────────────────────────────────────────────────
class Relationship(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_entity_id: str
    target_entity_id: str
    relationship_type: str = Field(..., min_length=1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_ids: List[str] = Field(default_factory=list)
    first_seen: datetime
    last_seen: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "source_entity_id", "target_entity_id")
    @classmethod
    def check_ids(cls, v: str) -> str:
        return validate_uuid_str(v)

    @field_validator("first_seen", "last_seen")
    @classmethod
    def check_tz(cls, v: datetime) -> datetime:
        return validate_tz_aware(v)  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# 6. OBSERVATION
# ─────────────────────────────────────────────────────────────────────────────
class Observation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source: EvidenceSource
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def check_id(cls, v: str) -> str:
        return validate_uuid_str(v)

    @field_validator("observed_at")
    @classmethod
    def check_tz(cls, v: datetime) -> datetime:
        return validate_tz_aware(v)  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# 7. SCAM PATTERN
# ─────────────────────────────────────────────────────────────────────────────
class ScamPattern(BaseModel):
    id: str
    pattern_name: str = Field(..., min_length=1)
    required_events: List[EventType]
    supporting_events: List[EventType] = Field(default_factory=list)
    sequence: List[EventType] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# 8. PATTERN MATCH
# ─────────────────────────────────────────────────────────────────────────────
class PatternMatch(BaseModel):
    pattern_id: str
    pattern_name: str = Field(..., min_length=1)
    matched_events: List[str] = Field(default_factory=list)
    missing_events: List[str] = Field(default_factory=list)
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    match_level: MatchLevel = MatchLevel.NONE
    current_stage: str = Field(default="UNKNOWN")
    common_next_stage: str = Field(default="UNKNOWN")
    confidence: float = Field(..., ge=0.0, le=1.0)


# ─────────────────────────────────────────────────────────────────────────────
# 9. GRAPH CORRELATION
# ─────────────────────────────────────────────────────────────────────────────
class GraphCorrelation(BaseModel):
    related_incident_id: str
    shared_entities: List[str] = Field(default_factory=list)
    shared_infrastructure: List[str] = Field(default_factory=list)
    relationship_paths: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_ids: List[str] = Field(default_factory=list)

    @field_validator("related_incident_id")
    @classmethod
    def check_id(cls, v: str) -> str:
        return validate_uuid_str(v)


# ─────────────────────────────────────────────────────────────────────────────
# 10. CAMPAIGN
# ─────────────────────────────────────────────────────────────────────────────
class Campaign(BaseModel):
    id: str
    name: str = Field(..., min_length=1)
    pattern_type: str
    first_seen: datetime
    last_seen: datetime
    incident_ids: List[str] = Field(default_factory=list)
    entity_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("first_seen", "last_seen")
    @classmethod
    def check_tz(cls, v: datetime) -> datetime:
        return validate_tz_aware(v)  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# 11. RISK ASSESSMENT
# ─────────────────────────────────────────────────────────────────────────────
class RiskAssessment(BaseModel):
    incident_id: str
    risk_score: int = Field(..., ge=0, le=100, description="Risk score is an INDEX (0-100), NOT a probability.")
    risk_level: RiskLevel
    evidence_confidence: ConfidenceLevel
    confidence_level: ConfidenceLevel
    reason_codes: List[str] = Field(default_factory=list)
    counter_evidence: List[str] = Field(default_factory=list)
    pattern_matches: List[PatternMatch] = Field(default_factory=list)
    graph_correlations: List[GraphCorrelation] = Field(default_factory=list)
    insufficient_evidence: bool = False
    assessed_at: datetime

    @field_validator("incident_id")
    @classmethod
    def check_id(cls, v: str) -> str:
        return validate_uuid_str(v)

    @field_validator("assessed_at")
    @classmethod
    def check_tz(cls, v: datetime) -> datetime:
        return validate_tz_aware(v)  # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# 12. INTERVENTION DECISION
# ─────────────────────────────────────────────────────────────────────────────
class InterventionDecision(BaseModel):
    incident_id: str
    intervention_type: InterventionType
    reason: str = Field(..., min_length=1, description="InterventionDecision must contain a non-empty reason.")
    triggering_evidence_ids: List[str] = Field(default_factory=list)
    journey_stage: str
    payment_proximity: bool = False
    created_at: datetime

    @field_validator("incident_id")
    @classmethod
    def check_id(cls, v: str) -> str:
        return validate_uuid_str(v)

    @field_validator("created_at")
    @classmethod
    def check_tz(cls, v: datetime) -> datetime:
        return validate_tz_aware(v)  # type: ignore

    @field_validator("reason")
    @classmethod
    def check_reason(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("An InterventionDecision must contain a non-empty reason.")
        return v.strip()
