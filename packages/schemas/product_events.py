"""Canonical Privacy-Conscious Product Telemetry Events for ScamGraph AI.

Rule: Product telemetry measures protection effectiveness without logging raw message contents or PII.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class ProductEventType(str, Enum):
    """Privacy-preserving lifecycle events measured in the consumer application."""
    CHECK_STARTED = "CHECK_STARTED"
    CHECK_COMPLETED = "CHECK_COMPLETED"
    WARNING_SHOWN = "WARNING_SHOWN"
    VERIFY_ACTION_CLICKED = "VERIFY_ACTION_CLICKED"
    PAYMENT_DELAY_RECOMMENDED = "PAYMENT_DELAY_RECOMMENDED"
    PAYMENT_BLOCKED_BY_USER = "PAYMENT_BLOCKED_BY_USER"
    RESCUE_STARTED = "RESCUE_STARTED"
    REPORT_GUIDANCE_OPENED = "REPORT_GUIDANCE_OPENED"
    EVIDENCE_PACK_CREATED = "EVIDENCE_PACK_CREATED"
    USER_FEEDBACK_SUBMITTED = "USER_FEEDBACK_SUBMITTED"


class ProductEvent(BaseModel):
    """Telemetry event record tracking consumer protection metrics."""
    event_id: str = Field(default_factory=lambda: generate_id("pevt"))
    event_type: ProductEventType
    session_id_hash: str = Field(..., description="Anonymized session hash")
    incident_id: Optional[str] = Field(default=None)
    
    # High-level context (NO raw text or unmasked identifiers)
    scam_family_inferred: Optional[str] = Field(default=None)
    risk_tier: Optional[str] = Field(default=None)
    primary_tactic: Optional[str] = Field(default=None)
    lead_time_seconds: Optional[float] = Field(default=None)
    
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
