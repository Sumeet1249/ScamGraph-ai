"""Mule Intelligence Engine Schemas (Module B).

Inspired by the publicly documented capabilities of RBIH MuleHunter.ai.
Defines transaction validation contracts, 19 behavioral feature schemas,
rules engine outputs, supervised ML model metadata, and account evaluation results.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class TransactionDirection(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class TransactionChannel(str, Enum):
    UPI = "UPI"
    IMPS = "IMPS"
    NEFT = "NEFT"
    RTGS = "RTGS"
    CARD = "CARD"
    WALLET = "WALLET"
    ATM = "ATM"


class TransactionOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


class MuleRiskBand(str, Enum):
    LOW = "LOW"            # 0.00 - 0.29
    MEDIUM = "MEDIUM"      # 0.30 - 0.59
    HIGH = "HIGH"          # 0.60 - 0.84
    CRITICAL = "CRITICAL"  # 0.85 - 1.00


class MuleAction(str, Enum):
    ALLOW = "ALLOW"
    MONITOR = "MONITOR"
    STEP_UP_KYC = "STEP_UP_KYC"
    FREEZE_SUSPEND = "FREEZE_SUSPEND"


# -----------------------------------------------------------------------------
# Transaction Schema & Ingestion
# -----------------------------------------------------------------------------

class TransactionRecord(BaseModel):
    """Canonical transaction model for mule account behavioral analysis."""
    txn_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(..., description="Timezone-aware transaction timestamp")
    amount: float = Field(..., gt=0.0, description="Transaction amount in specified currency (must be positive)")
    currency: str = Field(default="INR", min_length=3, max_length=3)
    direction: TransactionDirection
    source_account: Optional[str] = Field(None, description="Originating account/VPA token")
    destination_account: Optional[str] = Field(None, description="Receiving account/VPA token")
    counterparty_account: Optional[str] = Field(None, description="Primary counterparty account/VPA token")
    channel: TransactionChannel = TransactionChannel.UPI
    outcome: TransactionOutcome = TransactionOutcome.SUCCESS
    balance_after: Optional[float] = Field(None, ge=0.0, description="Account balance immediately post-transaction")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("amount")
    @classmethod
    def check_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Transaction amount must be strictly greater than 0.")
        if v > 100_000_000:  # 10 Crore cap for sanity
            raise ValueError("Amount exceeds valid transaction thresholds.")
        return round(v, 2)


# -----------------------------------------------------------------------------
# 19 Behavioral Features Schema
# -----------------------------------------------------------------------------

class MuleFeatureVector(BaseModel):
    """The 19 core behavioral feature representations for mule detection."""
    account_id: str
    evaluated_at: datetime

    # 1. Temporal & Velocity Features
    f01_velocity_1h_count: int = Field(default=0, description="Number of transactions in the peak 1-hour window")
    f02_velocity_24h_count: int = Field(default=0, description="Total transactions in the last 24 hours")
    f03_volume_turnover_ratio: float = Field(default=0.0, description="Ratio of total debited volume to total credited volume")
    f04_dwell_time_seconds_avg: float = Field(default=0.0, description="Average dwell time between credit and subsequent debit")
    f05_rapid_churn_ratio: float = Field(default=0.0, description="Fraction of credits drained within 5 minutes")

    # 2. Counterparty & Flow Topology
    f06_counterparty_diversity: float = Field(default=0.0, description="Unique counterparties divided by total transactions")
    f07_fan_in_count: int = Field(default=0, description="Number of distinct unique senders crediting this account")
    f08_fan_out_count: int = Field(default=0, description="Number of distinct unique recipients debited from this account")
    f09_fan_in_to_out_ratio: float = Field(default=0.0, description="Ratio of unique senders to unique recipients")

    # 3. Lifecycle & Account Profile
    f10_account_age_days: Optional[int] = Field(None, description="Age of account in days since onboarding")
    f11_dormancy_burst_score: float = Field(default=0.0, description="Burst factor comparing current throughput to historical daily average")
    f12_odd_hours_ratio: float = Field(default=0.0, description="Ratio of transactions executed between 12:00 AM and 05:00 AM")

    # 4. Cash Flow & Structuring Patterns
    f13_round_chunking_detected: bool = Field(default=False, description="Presence of recurring threshold-skimming amounts (e.g. ₹9,999, ₹49,999)")
    f14_balance_extraction_ratio: float = Field(default=0.0, description="Proportion of credit drained leaving balance < 1% of credit")
    f15_micro_test_followed_by_spike: bool = Field(default=False, description="Micro credit (e.g. ₹1-₹10) immediately followed by large inflow")
    f16_identical_amount_repetition_count: int = Field(default=0, description="Number of times exact same transfer amount was repeated")

    # 5. Channel & Registry Indicators
    f17_upi_handle_count: int = Field(default=1, description="Number of unique UPI VPAs linked to account")
    f18_channel_risk_concentration: float = Field(default=0.0, description="Proportion of volume over high-risk channels (UPI collect / peer)")
    f19_registry_match_indicator: bool = Field(default=False, description="Whether account identifier has a confirmed Smart Registry hit")

    # Data Quality Indicator
    is_partial_features: bool = Field(default=False, description="True if some historical features could not be calculated due to sparse data")


# -----------------------------------------------------------------------------
# Rules & Model Decision Schemas
# -----------------------------------------------------------------------------

class MuleRuleHit(BaseModel):
    """An individual behavioral rule triggered by account activity."""
    rule_id: str
    name: str
    description: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    weight: float
    trigger_value: Any


class MuleEvaluationRequest(BaseModel):
    """Request payload to evaluate an account for mule risk."""
    account_id: str = Field(..., min_length=2)
    transactions: List[TransactionRecord] = Field(..., min_length=1)
    account_age_days: Optional[int] = Field(None, ge=0)
    historical_avg_daily_volume: Optional[float] = Field(None, ge=0.0)
    current_balance: Optional[float] = Field(None, ge=0.0)
    linked_vpa_count: int = Field(default=1, ge=1)
    has_registry_match: bool = Field(default=False)


class MuleEvaluationResponse(BaseModel):
    """Structured risk response from Mule Intelligence Engine."""
    account_id: str
    evaluated_at: datetime
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_band: MuleRiskBand
    recommended_action: MuleAction
    rules_engine_score: float
    ml_model_score: Optional[float] = None
    is_calibrated: bool = False
    top_contributing_rules: List[MuleRuleHit]
    extracted_features: MuleFeatureVector
    model_metadata: Dict[str, Any]
    data_quality_warnings: List[str] = Field(default_factory=list)


class BatchMuleEvaluationRequest(BaseModel):
    """Batch evaluation for multiple accounts."""
    accounts: List[MuleEvaluationRequest] = Field(..., min_length=1, max_length=50)


class BatchMuleEvaluationResponse(BaseModel):
    """Batch evaluation response."""
    evaluated_at: datetime
    total_accounts: int
    high_risk_count: int
    evaluations: List[MuleEvaluationResponse]
