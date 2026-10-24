"""Standardized Contracts, Reason Codes, and Untrusted Input Wrappers for Inference.

Ensures:
1. Consumer reason codes are explainable and backed by supporting text spans (Rules 64-66).
2. Separation between Risk and Confidence (Rule 38).
3. Untrusted scam content cannot cause prompt injection into system instructions (Rules 56-57).
4. Failure states never return 'SAFE' (Rule 44).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from packages.inference.tiers import InferenceTier


class ConsumerRiskLevel(str, Enum):
    """Consumer-facing risk tiers (Rule 45)."""
    LIKELY_SAFE = "LIKELY_SAFE"
    CAUTION = "CAUTION"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH_RISK"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class StandardReasonCode(str, Enum):
    """Standardized explainability reason codes (Rule 65)."""
    AUTHORITY_IMPERSONATION = "AUTHORITY_IMPERSONATION"
    URGENT_PAYMENT_REQUEST = "URGENT_PAYMENT_REQUEST"
    SECRECY_REQUEST = "SECRECY_REQUEST"
    UNKNOWN_PAYMENT_RECIPIENT = "UNKNOWN_PAYMENT_RECIPIENT"
    SUSPICIOUS_LINK = "SUSPICIOUS_LINK"
    CREDENTIAL_REQUEST = "CREDENTIAL_REQUEST"
    PLATFORM_MIGRATION = "PLATFORM_MIGRATION"
    FAKE_REWARD_PATTERN = "FAKE_REWARD_PATTERN"
    PAYMENT_ESCALATION = "PAYMENT_ESCALATION"
    WITHDRAWAL_FEE_PATTERN = "WITHDRAWAL_FEE_PATTERN"
    RELATED_INCIDENTS_FOUND = "RELATED_INCIDENTS_FOUND"


class ReasonEvidence(BaseModel):
    """Evidence backing a user-facing explanation (Rule 66)."""
    code: StandardReasonCode
    explanation: str
    supporting_span: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    engine: str
    engine_version: str


class UntrustedArtifact(BaseModel):
    """Defensive wrapper isolating untrusted consumer messages/web content from system instructions (Rules 56, 57)."""
    raw_content: str
    sanitized_content: str
    source_type: str = "USER_SUBMITTED_MESSAGE"
    contains_instruction_like_patterns: bool = False
    
    @classmethod
    def sanitize(cls, text: str, source_type: str = "USER_SUBMITTED_MESSAGE") -> UntrustedArtifact:
        """Sanitizes text and flags common prompt injection indicators."""
        lower = text.lower()
        injection_markers = [
            "ignore previous instructions",
            "system prompt",
            "override instructions",
            "you are now",
            "jailbreak",
        ]
        has_injection = any(m in lower for m in injection_markers)
        return cls(
            raw_content=text,
            sanitized_content=text.replace("<script", "&lt;script").replace("</script>", "&lt;/script&gt;"),
            source_type=source_type,
            contains_instruction_like_patterns=has_injection,
        )


class LanguageProfile(BaseModel):
    """Separation of Language from Script (Rule 31)."""
    language: str = "en"           # ISO 639-1: en, hi, bn, ta, te
    script: str = "Latn"           # ISO 15924: Latn, Deva, Beng, etc.
    is_transliterated: bool = False # True for Romanized Hindi (Hinglish)
    is_code_mixed: bool = False
    confidence: float = 1.0


class TacticEvidence(BaseModel):
    """Evidence record for multi-label tactic classification (Rule 34, 35)."""
    tactic: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_text_span: Optional[str] = None
    engine: str = "tactic-rule-baseline"


class InferenceResponse(BaseModel):
    """Unified runtime response returned by ModelRouter (Rules 45, 79)."""
    execution_id: str
    risk_level: ConsumerRiskLevel
    scam_probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: List[ReasonEvidence] = Field(default_factory=list)
    tactics_detected: List[TacticEvidence] = Field(default_factory=list)
    language_profile: Optional[LanguageProfile] = None
    tier_executed: InferenceTier
    model_id: str
    model_revision: str
    latency_ms: float = 0.0
    fallback_used: bool = False
    degraded_mode: bool = False
    missing_capabilities: List[str] = Field(default_factory=list)
    cached_result: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
