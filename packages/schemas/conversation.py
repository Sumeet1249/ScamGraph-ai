"""Canonical Conversation & Dialogue Schemas for ScamGraph AI V2.

Represents ordered, multi-turn scam communications across WhatsApp, Telegram, SMS dialogues,
and streaming voice/call transcripts (supports datasets like ICFD-31k).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class SpeakerRole(str, Enum):
    """Role of the participant in a conversation turn."""
    SCAMMER = "SCAMMER"
    VICTIM = "VICTIM"
    UNKNOWN_ACTOR = "UNKNOWN_ACTOR"
    IMPERSONATED_AUTHORITY = "IMPERSONATED_AUTHORITY"
    SYSTEM_NOTIFICATION = "SYSTEM_NOTIFICATION"
    FAMILY_FRIEND = "FAMILY_FRIEND"


class ConversationMessage(BaseModel):
    """An individual message or speech chunk within an ordered conversation."""
    message_id: str = Field(default_factory=lambda: generate_id("msg"), description="Unique turn identifier")
    turn_index: int = Field(..., ge=0, description="Chronological sequence counter (0-indexed)")
    speaker_role: SpeakerRole = Field(default=SpeakerRole.UNKNOWN_ACTOR)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    text: str = Field(..., description="Message text or voice chunk transcript")
    
    # Enrichment metadata
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted entities in this turn")
    tactics: List[str] = Field(default_factory=list, description="Tactics detected in this turn")
    requested_actions: List[str] = Field(default_factory=list, description="Immediate calls-to-action in this turn")
    journey_stage_hint: Optional[str] = Field(default=None, description="Stage hint (e.g. TRUST_BUILDING, MONETIZATION)")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Conversation(BaseModel):
    """Full-turn conversation thread between victim and scam actor."""
    conversation_id: str = Field(default_factory=lambda: generate_id("conv"), description="Unique conversation thread ID")
    schema_version: str = Field(default="2.0")
    channel: str = Field(default="WHATSAPP", description="WHATSAPP, TELEGRAM, PHONE_CALL, SMS, SOCIAL_MEDIA")
    participants: List[str] = Field(default_factory=list, description="Pseudonymized or hashed participant IDs")
    
    # Ordered turns
    messages: List[ConversationMessage] = Field(default_factory=list, description="Chronological message sequence")
    
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    
    # Linguistic & Classification Context
    primary_language: str = Field(default="en")
    is_code_mixed: bool = Field(default=False)
    scam_family: Optional[str] = Field(default=None, description="Inferred scam typology (e.g. task_job, digital_arrest)")
    is_scam: bool = Field(default=True)
    outcome: Optional[str] = Field(default=None, description="COMPLETED_LOSS, INTERRUPTED, ABANDONED, REPORTED")
    
    # Provenance
    source_dataset: str = Field(default="internal")
    provenance_type: str = Field(default="SYNTHETIC_LLM")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_message(self, message: ConversationMessage) -> None:
        """Append an ordered message turn."""
        self.messages.append(message)
        # Ensure chronological ordering
        self.messages.sort(key=lambda m: m.turn_index)
