"""Unified ScamGraph Risk Engine Schemas (Module D).

Defines multi-signal orchestration request and explainable risk synthesis response contracts
combining Smart Registry, Mule Intelligence, Graph Correlation, and Semantic Message NLP.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.mule import MuleEvaluationResponse, TransactionRecord
from packages.schemas.registry import ScreenResponse, TypedIdentifier


class UnifiedAction(str, Enum):
    ALLOW = "ALLOW"
    STEP_UP_VERIFICATION = "STEP_UP_VERIFICATION"
    FLAG_FOR_REVIEW = "FLAG_FOR_REVIEW"
    ESCALATE = "ESCALATE"


class UnifiedRiskBand(str, Enum):
    LOW = "LOW"            # 0.00 - 0.29
    MEDIUM = "MEDIUM"      # 0.30 - 0.59
    HIGH = "HIGH"          # 0.60 - 0.84
    CRITICAL = "CRITICAL"  # 0.85 - 1.00


class UnifiedRiskRequest(BaseModel):
    """Multi-signal investigation request payload."""
    entity_id: Optional[str] = None
    message_text: Optional[str] = Field(None, description="Raw message text (SMS, WhatsApp, email)")
    url: Optional[str] = Field(None, description="Suspicious URL or link")
    vpa: Optional[str] = Field(None, description="UPI VPA (e.g. user@oksbi)")
    phone: Optional[str] = Field(None, description="Sender phone number")
    bank_account: Optional[str] = Field(None, description="Bank account token or IFSC:ACC")
    device_id: Optional[str] = Field(None, description="Device fingerprint or IMEI")
    transactions: List[TransactionRecord] = Field(default_factory=list, description="Recent transaction sequence if evaluating account")
    account_age_days: Optional[int] = None
    historical_avg_daily_volume: Optional[float] = None
    caller_org: str = Field(default="SCAMGRAPH_CONSOLE")
    correlation_id: Optional[str] = None


class UnifiedRiskResponse(BaseModel):
    """Comprehensive, explainable fraud intelligence result."""
    entity_id: str
    overall_risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_band: UnifiedRiskBand
    recommended_action: UnifiedAction
    reason_codes: List[str]
    contributing_signals: Dict[str, Any]
    supporting_evidence: List[Dict[str, Any]]
    uncertainty_and_data_quality: Dict[str, Any]
    is_degraded: bool = False
    degraded_components: List[str] = Field(default_factory=list)
    model_versions: Dict[str, str]
    scored_at: datetime
    correlation_id: str
