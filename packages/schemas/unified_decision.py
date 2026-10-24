"""Unified Decision & Tripartite Risk Schemas (Phase 4A).

Defines the decision layer integrating Risk, Confidence, and Urgency
with action-ready dispositions (EDUCATE, WARN, STRONG_WARNING, DELAY_PAYMENT, BLOCK_PRE_LOSS)
and multi-signal component contributions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TripartiteRiskBand(str, Enum):
    """Categorical severity and financial/data loss risk band."""
    BENIGN = "BENIGN"          # 0.00 - 0.19
    LOW = "LOW"                # 0.20 - 0.39
    MEDIUM = "MEDIUM"          # 0.40 - 0.64
    HIGH = "HIGH"              # 0.65 - 0.84
    CRITICAL = "CRITICAL"      # 0.85 - 1.00


class TripartiteConfidenceBand(str, Enum):
    """Evidence depth, quality, and independent corroboration tier."""
    VERY_LOW = "VERY_LOW"      # 0.00 - 0.29 (single weak heuristic)
    LOW = "LOW"                # 0.30 - 0.49
    MEDIUM = "MEDIUM"          # 0.50 - 0.69 (multiple consistent signals)
    HIGH = "HIGH"              # 0.70 - 0.84 (corroborated by entity/DNA)
    VERY_HIGH = "VERY_HIGH"    # 0.85 - 1.00 (cross-incident graph/campaign confirmed)


class TripartiteUrgencyBand(str, Enum):
    """Immediacy of financial loss or credential compromise requiring action."""
    LOW = "LOW"                               # Informational / early contact
    ELEVATED = "ELEVATED"                     # Social engineering in progress
    URGENT = "URGENT"                         # Payment request or credential harvest pending
    IMMEDIATE_INTERVENTION = "IMMEDIATE_INTERVENTION" # Pre-loss transfer imminent or active outbreak


class ActionDecision(str, Enum):
    """Calibrated, safe intervention action returned to consumers and partner platforms."""
    ALLOW = "ALLOW"
    EDUCATE = "EDUCATE"
    VERIFY_INDEPENDENTLY = "VERIFY_INDEPENDENTLY"
    WARN = "WARN"
    STRONG_WARNING = "STRONG_WARNING"
    DELAY_PAYMENT = "DELAY_PAYMENT"
    BLOCK_PRE_LOSS = "BLOCK_PRE_LOSS"


class DecisionDimension(str, Enum):
    """Component dimension contributing to the unified decision."""
    MESSAGE_NLP = "MESSAGE_NLP"
    URL_SAFETY = "URL_SAFETY"
    ENTITY_TRUST = "ENTITY_TRUST"
    TACTIC_MANIPULATION = "TACTIC_MANIPULATION"
    JOURNEY_STAGE = "JOURNEY_STAGE"
    SCAM_DNA = "SCAM_DNA"
    CAMPAIGN_OUTBREAK = "CAMPAIGN_OUTBREAK"
    GRAPH_CORRELATION = "GRAPH_CORRELATION"
    MULE_INTELLIGENCE = "MULE_INTELLIGENCE"
    COUNTER_EVIDENCE = "COUNTER_EVIDENCE"


class SignalContribution(BaseModel):
    """Detailed attribution of an individual intelligence engine to the decision."""
    dimension: DecisionDimension
    engine_name: str
    raw_score: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    weighted_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(default=0.80, ge=0.0, le=1.0)
    evidence_summary: str
    is_counter_evidence: bool = False


class TripartiteDecision(BaseModel):
    """Canonical Tripartite Risk + Confidence + Urgency assessment and intervention plan."""
    decision_id: str
    incident_id: Optional[str] = None
    entity_id: Optional[str] = None

    # Tripartite Core
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_band: TripartiteRiskBand
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_band: TripartiteConfidenceBand
    urgency_score: float = Field(..., ge=0.0, le=1.0)
    urgency_band: TripartiteUrgencyBand

    # Action Layer
    primary_action: ActionDecision
    secondary_actions: List[ActionDecision] = Field(default_factory=list)

    # Consumer-Safe Explanation Layer (No internal IDs or raw ML leakage)
    consumer_headline: str
    consumer_message: str
    recommended_steps: List[str] = Field(default_factory=list)

    # Signal Attribution & Calibrated Adjustments
    signal_contributions: List[SignalContribution] = Field(default_factory=list)
    contradictory_discount: float = 0.0
    uncertainty_penalty: float = 0.0

    # Campaign & Network Context
    matched_campaign_id: Optional[str] = None
    campaign_title: Optional[str] = None
    outbreak_status: Optional[str] = None
    pre_loss_intervention: bool = False

    # Auditing & Provenance
    scored_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = "4.1.0"
    is_degraded: bool = False
    degraded_components: List[str] = Field(default_factory=list)
