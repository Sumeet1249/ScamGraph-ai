"""Canonical Review Queue & User Feedback Schemas.

Rules:
1. Low-confidence, new patterns, or disputed records route to Review Queue.
2. User feedback is treated as evidence, NEVER as automatic ground truth for autonomous retraining.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class ReviewReason(str, Enum):
    """Why an item was flagged for human analyst review."""
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    MODEL_DISAGREEMENT = "MODEL_DISAGREEMENT"
    NEW_PATTERN = "NEW_PATTERN"
    POSSIBLE_CAMPAIGN = "POSSIBLE_CAMPAIGN"
    HIGH_IMPACT_ENTITY = "HIGH_IMPACT_ENTITY"
    USER_DISPUTE = "USER_DISPUTE"
    GOLD_SET_CANDIDATE = "GOLD_SET_CANDIDATE"


class ReviewStatus(str, Enum):
    """State machine for review queue items."""
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED_SCAM = "VERIFIED_SCAM"
    VERIFIED_BENIGN = "VERIFIED_BENIGN"
    INCONCLUSIVE = "INCONCLUSIVE"
    DISCARDED = "DISCARDED"


class UserFeedbackType(str, Enum):
    """Structured consumer feedback on ScamGraph checks."""
    THIS_HELPED = "THIS_HELPED"
    FALSE_ALARM = "FALSE_ALARM"
    I_WAS_SCAMMED = "I_WAS_SCAMMED"
    I_PAID = "I_PAID"
    ENTITY_WAS_LEGITIMATE = "ENTITY_WAS_LEGITIMATE"
    ENTITY_WAS_SUSPICIOUS = "ENTITY_WAS_SUSPICIOUS"
    NOT_SURE = "NOT_SURE"


class ReviewItem(BaseModel):
    """An item queued for expert human evaluation."""
    review_id: str = Field(default_factory=lambda: generate_id("rev"))
    target_id: str = Field(..., description="Target record_id, incident_id, or entity_id")
    target_type: str = Field(default="INCIDENT", description="INCIDENT, RECORD, ENTITY, CAMPAIGN")
    reason: ReviewReason
    status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    reviewer_id: Optional[str] = Field(default=None)
    reviewer_notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserFeedbackRecord(BaseModel):
    """Recorded consumer interaction feedback."""
    feedback_id: str = Field(default_factory=lambda: generate_id("fbk"))
    incident_id: str = Field(..., description="Associated incident ID")
    feedback_type: UserFeedbackType
    user_comment: Optional[str] = Field(default=None)
    reported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_incorporated_into_training: bool = Field(default=False, description="Must remain False until human vetted")
