"""Canonical Evidence Records supporting both corroboration and contradiction.

Rules:
1. Evidence can SUPPORT, CONTRADICT, or be NEUTRAL toward a claim.
2. System must not exhibit confirmation bias (only gathering evidence for fraud).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class EvidencePolarity(str, Enum):
    """How the evidence affects a hypothesis or claim."""
    SUPPORTS = "SUPPORTS"           # Strengthens fraud hypothesis
    CONTRADICTS = "CONTRADICTS"     # Proves legitimacy (e.g. valid official bank domain, verified sender ID)
    NEUTRAL = "NEUTRAL"             # Contextual info without clear polarity


class ClaimEvidenceRecord(BaseModel):
    """Structured evidence finding with explicit polarity and provenance."""
    evidence_id: str = Field(default_factory=lambda: generate_id("evi"))
    claim: str = Field(..., description="Hypothesis evaluated (e.g. SENDER_IS_SBI, DOMAIN_IS_PHISHING)")
    polarity: EvidencePolarity = Field(default=EvidencePolarity.SUPPORTS)
    
    # Provenance
    source_service: str = Field(..., description="Detector or service generating evidence")
    source_type: str = Field(default="ML_MODEL", description="ML_MODEL, HEURISTIC, OSINT, REGISTRY, REPUTATION")
    provider: Optional[str] = Field(default=None)
    model_or_rule_id: Optional[str] = Field(default=None)
    
    # Credibility & Timing
    reliability_score: float = Field(default=1.0, ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(default=None)
    
    # Supporting assets
    target_artifact_hash: Optional[str] = Field(default=None)
    details: Dict[str, Any] = Field(default_factory=dict)
    rationale: str = Field(default="", description="Plain-language human readable explanation")
