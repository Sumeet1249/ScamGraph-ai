"""Canonical Training & Evaluation Record: ScamGraphRecordV2.

Unifies single SMS messages, conversations, multi-stage journey events, hard negatives,
and synthetic scenarios with complete language, quality, split, and provenance metadata.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id
from packages.schemas.provenance import (
    AnnotationRecord,
    AnnotationType,
    SourceProvenanceRecord,
    SourceProvenanceType,
)


class SplitType(str, Enum):
    """Dataset split assignments."""
    TRAIN = "TRAIN"
    VALIDATION = "VALIDATION"
    TEST = "TEST"
    GOLD = "GOLD"
    HOLDOUT = "HOLDOUT"
    UNASSIGNED = "UNASSIGNED"


class LanguageMetadata(BaseModel):
    """Structured linguistic and dialect metadata."""
    primary_language: str = Field(default="en", description="ISO code (e.g. en, hi, hinglish, bn, ta, te, mr, gu)")
    secondary_languages: List[str] = Field(default_factory=list)
    script: str = Field(default="Latin", description="Latin, Devanagari, Bengali, Tamil, etc.")
    code_mixed: bool = Field(default=False, description="True if text blends multiple languages (e.g. Hinglish)")
    transliterated: bool = Field(default=False, description="True if Hindi/regional text is written in English script")
    language_confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class QualityMetadata(BaseModel):
    """Audit and deduplication indicators for clean training and evaluation."""
    annotation_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reviewer_count: int = Field(default=1, ge=0)
    duplicate_group_id: Optional[str] = Field(default=None, description="Exact duplicate grouping ID")
    near_duplicate_group_id: Optional[str] = Field(default=None, description="Semantic or fuzzy duplicate grouping ID")
    template_group_id: Optional[str] = Field(default=None, description="Shared notification/SMS template cluster ID")
    campaign_group_id: Optional[str] = Field(default=None, description="Threat campaign cluster ID")
    journey_group_id: Optional[str] = Field(default=None, description="Scam journey progression sequence ID")
    gold_set: bool = Field(default=False, description="True if member of verified human gold standard")
    adversarial: bool = Field(default=False, description="True if designed as an adversarial evaluation sample")
    hard_negative: bool = Field(default=False, description="True if benign sample with high surface similarity to scam")
    quality_flags: List[str] = Field(default_factory=list)


class SplitMetadata(BaseModel):
    """Split partition controls to prevent data and template leakage."""
    split: SplitType = Field(default=SplitType.UNASSIGNED)
    split_strategy: str = Field(default="template_grouped", description="random, template_grouped, temporal, campaign_isolated")
    group_ids: List[str] = Field(default_factory=list, description="IDs used to enforce clean non-overlapping splits")
    time_bucket: Optional[str] = Field(default=None, description="Temporal partitioning indicator (e.g. 2026-Q1)")
    excluded_from_training: bool = Field(default=False)
    exclusion_reason: Optional[str] = Field(default=None)


class ScamGraphRecordV2(BaseModel):
    """Canonical V2 data foundation record for all ScamGraph ML datasets."""
    record_id: str = Field(default_factory=lambda: generate_id("rec"), description="Deterministic or unique record ID")
    schema_version: str = Field(default="2.0", description="Contract schema version")
    content: str = Field(..., description="Normalized text content or message payload")
    raw_content: Optional[str] = Field(default=None, description="Original unnormalized raw string")
    
    # Context & Correlation
    incident_id: Optional[str] = Field(default=None)
    conversation_id: Optional[str] = Field(default=None)
    campaign_id: Optional[str] = Field(default=None)
    artifact_id: Optional[str] = Field(default=None)
    event_context: Dict[str, Any] = Field(default_factory=dict, description="Channel, sender, or temporal context")
    
    # Metadata sub-objects
    language: LanguageMetadata = Field(default_factory=LanguageMetadata)
    provenance: SourceProvenanceRecord
    annotations: List[AnnotationRecord] = Field(default_factory=list)
    quality: QualityMetadata = Field(default_factory=QualityMetadata)
    split_metadata: SplitMetadata = Field(default_factory=SplitMetadata)
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted entity references")
    labels: Dict[str, Any] = Field(default_factory=dict, description="Convenience key-value labels (e.g. is_scam: 1)")

    @property
    def is_synthetic(self) -> bool:
        """Compatibility property for legacy code checking is_synthetic."""
        return self.provenance.source_type in (
            SourceProvenanceType.SYNTHETIC_LLM,
            SourceProvenanceType.SYNTHETIC_TEMPLATE,
            SourceProvenanceType.SYNTHETIC_OTHER,
        )

    def to_legacy(self) -> Dict[str, Any]:
        """Export backward-compatible representation for legacy MessageRecord consumers."""
        label_val = self.labels.get("is_scam", self.labels.get("label", 0))
        scam_type = self.labels.get("scam_type", "generic_scam" if label_val == 1 else "benign")
        return {
            "id": self.record_id,
            "text": self.content,
            "label": int(label_val),
            "scam_type": scam_type,
            "language": self.language.primary_language,
            "source_dataset": self.provenance.source_name,
            "is_synthetic": self.is_synthetic,
            "campaign_id": self.campaign_id or "unassigned",
            "split": self.split_metadata.split.value.lower(),
        }

    @classmethod
    def from_legacy(cls, legacy_record: Any) -> "ScamGraphRecordV2":
        """Convert a legacy MessageRecord or dictionary to ScamGraphRecordV2."""
        d = legacy_record.to_dict() if hasattr(legacy_record, "to_dict") else dict(legacy_record)
        is_syn = d.get("is_synthetic", False)
        source_name = d.get("source_dataset", "legacy_dataset")
        
        # Determine provenance type accurately
        if is_syn:
            prov_type = SourceProvenanceType.SYNTHETIC_LLM
        elif "scam-ham-india" in source_name or "scam_ham_india" in source_name:
            prov_type = SourceProvenanceType.PUBLIC_MIXED
        else:
            prov_type = SourceProvenanceType.PUBLIC_REAL

        text = d.get("text", "")
        label = int(d.get("label", 0))
        scam_type = d.get("scam_type", "benign" if label == 0 else "generic_scam")
        lang = d.get("language", "en")
        
        provenance = SourceProvenanceRecord(
            source_name=source_name,
            source_type=prov_type,
            record_id=d.get("id"),
        )
        
        # Explicit annotation records distinguishing ground truth vs rule-inferred
        annotations = [
            AnnotationRecord(
                label_name="is_scam",
                label_value=label,
                annotation_type=AnnotationType.SOURCE_PROVIDED,
                confidence=1.0,
            ),
            AnnotationRecord(
                label_name="scam_type",
                label_value=scam_type,
                annotation_type=AnnotationType.RULE_INFERRED if scam_type != "benign" else AnnotationType.SOURCE_PROVIDED,
                confidence=0.85 if scam_type != "benign" else 1.0,
                notes="Rule-inferred taxonomy from text heuristics" if scam_type != "benign" else None,
            )
        ]

        split_enum = SplitType.UNASSIGNED
        split_val = str(d.get("split", "train")).upper()
        if split_val in SplitType.__members__:
            split_enum = SplitType[split_val]

        return cls(
            record_id=d.get("id") or generate_id("rec"),
            content=text,
            provenance=provenance,
            annotations=annotations,
            labels={"is_scam": label, "scam_type": scam_type},
            language=LanguageMetadata(
                primary_language=lang,
                code_mixed=lang.lower() in ("hinglish", "bn_en", "hi_en"),
            ),
            split_metadata=SplitMetadata(split=split_enum),
            campaign_id=d.get("campaign_id"),
        )
