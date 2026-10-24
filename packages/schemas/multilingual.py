"""Canonical Schemas for India Multilingual Intelligence V2 (Prompt 17 / Phase 5C).

Models Language, Script, Locale, Indic Normalization, Transliteration,
Protective Negation, Code-Mixing, and Language-Invariant Behavioral Features.
"""

from datetime import datetime, timezone
from enum import Enum
import hashlib
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id
from packages.schemas.tactics import ActionRequestedType, TacticType


class ScriptType(str, Enum):
    """Writing systems observed in Indian digital communications."""
    LATIN = "LATIN"
    DEVANAGARI = "DEVANAGARI"
    BENGALI = "BENGALI"
    MIXED = "MIXED"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class LanguageSupportTier(str, Enum):
    """Maturity and benchmark-validated status of language intelligence."""
    PRODUCTION_VALIDATED = "PRODUCTION_VALIDATED"  # English, Hindi (Devanagari), Hinglish (Roman Hindi)
    BETA = "BETA"                                  # Bengali (Bengali script & Roman Bengali)
    EXPERIMENTAL = "EXPERIMENTAL"                  # Tamil, Telugu, Marathi, Gujarati
    NORMALIZATION_ONLY = "NORMALIZATION_ONLY"      # Basic Unicode cleaning, no deep semantic modeling
    UNSUPPORTED = "UNSUPPORTED"                    # Language detected but unsupported; degraded analysis


class LanguageSegment(BaseModel):
    """Sub-span segment within code-mixed or multi-script communication."""
    start: int = Field(..., ge=0, description="Start character offset")
    end: int = Field(..., ge=0, description="End character offset")
    text: str = Field(..., description="Segment text")
    language: str = Field(..., description="ISO 639-3 or code (e.g. eng, hin, ben, hinglish)")
    script: ScriptType = Field(default=ScriptType.UNKNOWN)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class LanguageProfile(BaseModel):
    """Centralized language and script identification profile."""
    profile_id: str = Field(default_factory=lambda: generate_id("langprof"))
    primary_language: str = Field(default="eng", description="Primary detected language (eng, hin, hinglish, ben, und)")
    secondary_languages: List[str] = Field(default_factory=list)
    language_probabilities: Dict[str, float] = Field(default_factory=dict)
    scripts: List[ScriptType] = Field(default_factory=list)
    code_mixed: bool = Field(default=False, description="True if text blends multiple languages (e.g. Hinglish)")
    code_mix_score: float = Field(default=0.0, ge=0.0, le=1.0, description="0.0 = pure monolingual, 1.0 = heavy mixing")
    romanized_indic: bool = Field(default=False, description="True if Indic language written in Latin script (e.g. Roman Hindi)")
    language_segments: List[LanguageSegment] = Field(default_factory=list)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    support_tier: LanguageSupportTier = Field(default=LanguageSupportTier.PRODUCTION_VALIDATED)
    detection_method: str = Field(default="HYBRID_RULE_LEXICON_V2")
    model_version: str = Field(default="LangIntel-v2.0")
    normalization_version: str = Field(default="IndicNorm-v2.0")


class MultilingualTextRepresentation(BaseModel):
    """Multi-tiered derived representations of an immutable raw text artifact."""
    representation_id: str = Field(default_factory=lambda: generate_id("mlrep"))
    original_text: str = Field(..., description="Immutable original raw text as received from source")
    original_hash: str = Field(default="")
    language_profile: LanguageProfile
    normalized_text: str = Field(..., description="Cleaned text preserving security tokens and entity boundaries")
    normalized_segments: List[str] = Field(default_factory=list)
    transliterated_text: Optional[str] = Field(default=None, description="Derived phonetic transliteration if applicable")
    translated_text: Optional[str] = Field(default=None, description="Supporting English translation if applicable")
    translation_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    semantic_input_text: str = Field(..., description="Final text representation fed into multilingual semantic models")
    normalization_steps: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    version: str = Field(default="2.0.0")

    def model_post_init(self, __context: Any) -> None:
        if not self.original_hash and self.original_text:
            self.original_hash = hashlib.sha256(self.original_text.encode("utf-8")).hexdigest()


class UserLanguagePreference(BaseModel):
    """User-controlled localization preferences (decoupled from input detection)."""
    ui_language: str = Field(default="en", description="UI chrome language: en, hi, hinglish, bn")
    explanation_language: str = Field(default="en", description="Explanation and guidance language")
    input_language_auto_detect: bool = Field(default=True)
    fallback_language: str = Field(default="en")


class NegationSignal(BaseModel):
    """Explicit detection of protective safety negation versus fraudulent demands."""
    has_negation: bool = Field(default=False)
    is_protective_advisory: bool = Field(default=False, description="True if text is advising NOT to perform an action")
    negated_action: Optional[ActionRequestedType] = None
    negation_tokens: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    explanation: str = Field(default="")


class BehavioralFeatureSet(BaseModel):
    """Language-independent canonical behavioral representation between text and network intelligence."""
    feature_id: str = Field(default_factory=lambda: generate_id("bfeat"))
    tactics: List[TacticType] = Field(default_factory=list)
    requested_actions: List[ActionRequestedType] = Field(default_factory=list)
    journey_stage_candidate: Optional[str] = None
    payment_escalation_detected: bool = Field(default=False)
    platform_migration_detected: bool = Field(default=False)
    authority_impersonation_detected: bool = Field(default=False)
    secrecy_detected: bool = Field(default=False)
    isolation_detected: bool = Field(default=False)
    reward_progression_detected: bool = Field(default=False)
    withdrawal_blocking_detected: bool = Field(default=False)
    credential_request_detected: bool = Field(default=False)
    remote_access_request_detected: bool = Field(default=False)
    protective_negation_present: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)
