"""Canonical Provenance, Annotation, Model, and Dataset Lineage Schemas for ScamGraph AI V2."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class SourceProvenanceType(str, Enum):
    """Detailed provenance classification of data points."""
    REAL_VERIFIED = "REAL_VERIFIED"            # Verified real user incident / telecom capture
    REAL_ANONYMIZED = "REAL_ANONYMIZED"        # Real incident sanitized of PII
    PUBLIC_REAL = "PUBLIC_REAL"                # Sourced from public repository of real incidents
    PUBLIC_MIXED = "PUBLIC_MIXED"              # Public dataset containing unknown blend of real and synthetic
    HUMAN_CURATED = "HUMAN_CURATED"            # Hand-crafted scenarios designed by fraud analysts
    SYNTHETIC_LLM = "SYNTHETIC_LLM"            # Generated via Large Language Model prompting
    SYNTHETIC_TEMPLATE = "SYNTHETIC_TEMPLATE"  # Generated via rule/regex templates
    SYNTHETIC_OTHER = "SYNTHETIC_OTHER"        # Other programmatic generation
    WEAK_LABEL = "WEAK_LABEL"                  # Heuristically or regex-labelled data
    UNKNOWN = "UNKNOWN"


class AnnotationType(str, Enum):
    """How a ground-truth label or classification was produced."""
    HUMAN_VERIFIED = "HUMAN_VERIFIED"          # Multi-analyst consensus ground truth
    HUMAN_SINGLE_REVIEW = "HUMAN_SINGLE_REVIEW"# Single human review
    HUMAN_MULTI_REVIEW = "HUMAN_MULTI_REVIEW"  # Multiple reviewers agreed
    SOURCE_PROVIDED = "SOURCE_PROVIDED"        # Label was imported from third-party dataset card
    MODEL_INFERRED = "MODEL_INFERRED"          # Classified by ML/LLM model
    RULE_INFERRED = "RULE_INFERRED"            # Classified by regex or keyword heuristics
    SYNTHETIC_GROUND_TRUTH = "SYNTHETIC_GROUND_TRUTH" # Target label from synthetic prompt/generator
    UNKNOWN = "UNKNOWN"


class AnnotationRecord(BaseModel):
    """Explicit annotation provenance contract."""
    label_name: str = Field(..., description="Target dimension (e.g. is_scam, scam_type, urgency)")
    label_value: Any = Field(..., description="Assigned value (e.g. 1, 'fake_kyc', 'HIGH')")
    annotation_type: AnnotationType = Field(..., description="Method used to establish this label")
    annotator_id: Optional[str] = Field(default=None, description="Identifier of human reviewer if applicable")
    model_id: Optional[str] = Field(default=None, description="Identifier of model if MODEL_INFERRED")
    rule_id: Optional[str] = Field(default=None, description="Identifier of rule/regex if RULE_INFERRED")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this annotation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = Field(default=None, description="Reviewer notes or rationale")


class SourceProvenanceRecord(BaseModel):
    """Origin, lineage, and audit trail of a training or evaluation record."""
    source_name: str = Field(..., description="Origin name (e.g. scam-ham-india, user_report)")
    source_type: SourceProvenanceType = Field(default=SourceProvenanceType.UNKNOWN)
    source_uri: Optional[str] = Field(default=None, description="Hugging Face repo or external URI")
    dataset_id: Optional[str] = Field(default=None, description="Registry dataset ID if applicable")
    dataset_version: Optional[str] = Field(default=None, description="Dataset revision or git commit")
    record_id: Optional[str] = Field(default=None, description="Original record key in source dataset")
    collected_at: Optional[datetime] = Field(default=None)
    published_at: Optional[datetime] = Field(default=None)
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    license: Optional[str] = Field(default=None, description="Dataset license (e.g. Apache-2.0, MIT)")
    terms_notes: Optional[str] = Field(default=None)
    verification_method: Optional[str] = Field(default=None)
    annotator_type: Optional[str] = Field(default=None)
    generator_model: Optional[str] = Field(default=None, description="Model used if SYNTHETIC_LLM")
    generator_version: Optional[str] = Field(default=None)
    is_modified: bool = Field(default=False)
    parent_record_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ModelExecutionRecord(BaseModel):
    """Audit record capturing an inference invocation for lineage and explainability."""
    execution_id: str = Field(default_factory=lambda: generate_id("exe"))
    model_id: str = Field(..., description="Registered model ID (e.g. scamgraph-message-baseline)")
    model_revision: str = Field(..., description="Model version or artifact git hash")
    task: str = Field(..., description="Task performed (e.g. text_classification, url_scoring)")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = Field(..., ge=0.0, description="Inference execution duration in milliseconds")
    input_reference: str = Field(..., description="SHA-256 hash or pointer to input. Never store raw PII.")
    output_reference: Optional[str] = Field(default=None, description="Hash or pointer to prediction output")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    degraded: bool = Field(default=False, description="True if inference ran in degraded or fallback mode")
    fallback_used: bool = Field(default=False, description="True if a fallback model/heuristic was used")
    fallback_model_id: Optional[str] = Field(default=None)
    error_code: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DatasetLineageRecord(BaseModel):
    """Tracks transformations and splits applied to a data point."""
    record_id: str = Field(..., description="Target record ID")
    dataset_id: str = Field(..., description="Registry dataset ID")
    dataset_revision: str = Field(..., description="Version of the dataset")
    source_record_id: Optional[str] = Field(default=None)
    parent_record_ids: List[str] = Field(default_factory=list)
    transformations: List[str] = Field(default_factory=list, description="List of applied operations (e.g. lower, dedup, pii_mask)")
    normalization_version: str = Field(default="1.0")
    dedup_version: str = Field(default="1.0")
    annotation_version: str = Field(default="1.0")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
