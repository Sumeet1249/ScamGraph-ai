"""Canonical Psychological Tactics & Call-to-Action Schemas for ScamGraph AI V2.

Encodes behavioral manipulation signals and requested actions for proactive user intervention.
"""

from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class TacticType(str, Enum):
    """Psychological manipulation tactics identified across Indian fraud journeys."""
    AUTHORITY = "AUTHORITY"                     # CBI, Police, Supreme Court, TRAI, Bank Manager
    URGENCY = "URGENCY"                         # 2 hours left, electricity disconnect at 9:30 PM
    FEAR = "FEAR"                               # Arrest warrant, legal action, account freeze
    GREED = "GREED"                             # Guaranteed 300% returns, lottery prize
    SCARCITY = "SCARCITY"                       # Only 2 job slots remaining, limited period
    SOCIAL_PROOF = "SOCIAL_PROOF"               # Fake Telegram group members showing withdrawal screenshots
    ROMANCE = "ROMANCE"                         # Matrimonial / emotional connection
    TRUST_BUILDING = "TRUST_BUILDING"           # Returning small profit (₹150 on ₹500 task)
    SECRECY = "SECRECY"                         # "Keep this confidential, do not tell family or bank"
    ISOLATION = "ISOLATION"                     # "Stay on Skype call, lock door, do not disconnect"
    RECIPROCITY = "RECIPROCITY"                 # "We helped you recover funds, now pay our legal fee"
    LOSS_AVERSION = "LOSS_AVERSION"             # "Pay ₹5,000 tax or lose your entire ₹50,000 balance"
    FAKE_REWARD = "FAKE_REWARD"                 # Free gift, cashback voucher, spin the wheel
    THREAT = "THREAT"                           # Defamation, leaking contacts, physical harm
    IMPERSONATION = "IMPERSONATION"             # Pretending to be courier, discom, bank officer
    PAYMENT_PRESSURE = "PAYMENT_PRESSURE"       # Demanding immediate UPI collect approval


class ActionRequestedType(str, Enum):
    """Explicit behavioral actions demanded by the scammer."""
    CLICK_LINK = "CLICK_LINK"
    CALL_NUMBER = "CALL_NUMBER"
    REPLY = "REPLY"
    INSTALL_APP = "INSTALL_APP"                 # AnyDesk, QuickSupport, malicious APK
    DOWNLOAD_FILE = "DOWNLOAD_FILE"
    SHARE_OTP = "SHARE_OTP"
    SHARE_CREDENTIAL = "SHARE_CREDENTIAL"       # Netbanking login, ATM PIN, CVV
    SHARE_SCREEN = "SHARE_SCREEN"
    MOVE_PLATFORM = "MOVE_PLATFORM"             # "Message me on Telegram / WhatsApp"
    ADD_CONTACT = "ADD_CONTACT"
    SEND_PAYMENT = "SEND_PAYMENT"               # Direct UPI transfer, IMPS, RTGS
    SCAN_QR = "SCAN_QR"                         # "Scan to receive payment" (scam trick)
    APPROVE_UPI_REQUEST = "APPROVE_UPI_REQUEST" # Collect request approval
    INVEST_MORE = "INVEST_MORE"
    PAY_FEE = "PAY_FEE"                         # Customs fee, tax, processing fee
    KEEP_SECRET = "KEEP_SECRET"
    DO_NOT_DISCONNECT = "DO_NOT_DISCONNECT"
    UNKNOWN = "UNKNOWN"


class ManipulationSignal(BaseModel):
    """Structured output representing psychological tactics and pressure points."""
    tactics_present: List[TacticType] = Field(default_factory=list)
    actions_requested: List[ActionRequestedType] = Field(default_factory=list)
    primary_tactic: TacticType = Field(default=TacticType.IMPERSONATION)
    manipulation_severity: str = Field(default="MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    explanation: str = Field(default="", description="Consumer-facing plain-language explanation of manipulation")
