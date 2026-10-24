"""Canonical Event Schemas for ScamGraph AI.

Represents atomic multi-channel user interaction events:
SMS, WhatsApp, Telegram, calls, URLs clicked, and payment requests.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Union
from uuid import uuid4
from pydantic import BaseModel, Field


class ChannelType(str, Enum):
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    TELEGRAM = "TELEGRAM"
    CALL = "CALL"
    WEB = "WEB"
    UPI = "UPI"
    BANK_APP = "BANK_APP"


class EventType(str, Enum):
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED"
    LINK_CLICKED = "LINK_CLICKED"
    CALL_LOGGED = "CALL_LOGGED"
    APP_INSTALLED = "APP_INSTALLED"
    OTP_REQUESTED = "OTP_REQUESTED"
    COLLECT_REQUEST_RECEIVED = "COLLECT_REQUEST_RECEIVED"
    PAYMENT_INTENT_INITIATED = "PAYMENT_INTENT_INITIATED"


class MessagePayload(BaseModel):
    """Payload for incoming communication messages."""
    sender_id: str = Field(..., description="Sender phone number, shortcode, or handle")
    recipient_id_hash: str = Field(..., description="Pseudonymized recipient hash")
    text: str = Field(..., description="Raw text of the communication message")
    channel: ChannelType = Field(default=ChannelType.SMS)
    language_hint: Optional[str] = Field(default=None, description="Optional detected language code (e.g. en, hi)")


class UrlPayload(BaseModel):
    """Payload for web links and clicked URLs."""
    raw_url: str = Field(..., description="Raw URL as observed in the communication")
    normalized_url: Optional[str] = Field(default=None, description="Cleaned/canonical URL without tracking params")
    referrer_event_id: Optional[str] = Field(default=None, description="ID of preceding event delivering the URL")


class PaymentPayload(BaseModel):
    """Payload for UPI collect or payment requests."""
    vpa: str = Field(..., description="Virtual Payment Address (e.g. user@bank)")
    claimed_payee_name: Optional[str] = Field(default=None, description="Name purported by the sender or page")
    amount: Optional[float] = Field(default=None, ge=0.0, description="Amount requested in INR")
    transaction_type: str = Field(default="COLLECT", description="COLLECT, DIRECT_PAY, QR, INTENT")
    reference_note: Optional[str] = Field(default=None, description="Transaction note or remark")


class ActorRole(str, Enum):
    """Actor initiating or responding in the event."""
    USER = "USER"
    UNKNOWN_ACTOR = "UNKNOWN_ACTOR"
    PLATFORM = "PLATFORM"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class Event(BaseModel):
    """Universal canonical event envelope with V2 extension compatibility."""
    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event identifier")
    schema_version: str = Field(default="2.0", description="Contract schema version")
    incident_id: str = Field(..., description="Identifier linking events within a single journey session")
    sequence_number: int = Field(..., ge=1, description="Chronological sequence counter (1-indexed)")
    event_type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Union[MessagePayload, UrlPayload, PaymentPayload, Dict[str, Any]]
    actor_role: ActorRole = Field(default=ActorRole.UNKNOWN, description="Role of the actor triggering this event")
    artifact_ids: list[str] = Field(default_factory=list, description="Associated raw artifact IDs")
    entities: list[Dict[str, Any]] = Field(default_factory=list, description="Resolved entity references")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Device, network, or contextual flags")
