"""Canonical Payment Context Schema for Pre-Payment Intervention (ScamGraph Guard).

Captures the psychological, relational, and transactional context preceding a UPI/payment transfer
to evaluate whether the payment intent originates from manipulation.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class ClaimedPaymentReason(str, Enum):
    """The reason purported by the sender or believed by the victim for making payment."""
    JOB_REGISTRATION = "JOB_REGISTRATION"
    TASK_DEPOSIT = "TASK_DEPOSIT"               # Prepaid recharge tasks, YouTube likes
    INVESTMENT = "INVESTMENT"                   # Crypto, forex, share trading
    TAX = "TAX"                                 # "TDS fee before withdrawal"
    SECURITY_DEPOSIT = "SECURITY_DEPOSIT"       # Courier customs, apartment deposit
    REFUND_PROCESSING = "REFUND_PROCESSING"     # "Pay ₹1 to receive ₹5,000 refund"
    LOAN_FEE = "LOAN_FEE"                       # Insurance or processing fee for instant loan
    COURIER_FEE = "COURIER_FEE"
    CUSTOMS_FEE = "CUSTOMS_FEE"
    KYC_FEE = "KYC_FEE"
    POLICE_FINE = "POLICE_FINE"                 # Digital arrest settlement fine
    GOVERNMENT_PAYMENT = "GOVERNMENT_PAYMENT"
    FRIEND_FAMILY = "FRIEND_FAMILY"             # Impersonated friend in emergency
    SELLER_PAYMENT = "SELLER_PAYMENT"           # OLX fake army officer advance
    CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"       # Fake toll-free helpline
    PRIZE_FEE = "PRIZE_FEE"                     # Registration fee to release lottery
    WITHDRAWAL_FEE = "WITHDRAWAL_FEE"
    UNKNOWN = "UNKNOWN"


class PaymentContextRecord(BaseModel):
    """Contextual intelligence preceding a payment execution."""
    payment_context_id: str = Field(default_factory=lambda: generate_id("payctx"))
    incident_id: str = Field(..., description="Associated incident ID")
    journey_stage: str = Field(default="PAYMENT", description="CONTACT, GROOMING, TRIAL_PAYMENT, ESCALATION, LOSS")
    
    # Financial parameters
    payment_method: str = Field(default="UPI", description="UPI, QR, IMPS, RTGS, WALLET, CRYPTO")
    amount_inr: Optional[float] = Field(default=None, ge=0.0)
    amount_bucket: str = Field(default="MICRO", description="MICRO (<500), LOW (500-2k), MID (2k-10k), HIGH (>10k)")
    recipient_vpa: Optional[str] = Field(default=None, description="Normalized destination VPA")
    recipient_name_claimed: Optional[str] = Field(default=None)
    
    # Contextual flags
    claimed_reason: ClaimedPaymentReason = Field(default=ClaimedPaymentReason.UNKNOWN)
    inferred_reason: ClaimedPaymentReason = Field(default=ClaimedPaymentReason.UNKNOWN)
    is_first_payment_to_recipient: bool = Field(default=True)
    payment_sequence_in_journey: int = Field(default=1, ge=1)
    prior_small_reward_received: bool = Field(default=False, description="True if victim previously received bait profit")
    
    # Active Pressure Signals
    pressure_present: bool = Field(default=False)
    urgency_present: bool = Field(default=False)
    authority_present: bool = Field(default=False)
    withdrawal_block_present: bool = Field(default=False)
    
    # Final Guard Assessment
    risk_tier: str = Field(default="HIGH", description="SAFE, CAUTION, SUSPICIOUS, HIGH_RISK, CRITICAL")
    recommended_delay_minutes: int = Field(default=0, ge=0, description="Defensive cooling-off period")
    consumer_warning: str = Field(default="")
    evidence_signals: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
