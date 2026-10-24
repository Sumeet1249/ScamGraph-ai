"""Canonical Evaluation Run and Metric Result Schemas for ScamGraph AI V2."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.schemas.common import generate_id


class EvaluationValidityStatus(str, Enum):
    """Integrity and validity rating of an evaluation run."""
    DEVELOPMENT_ONLY = "DEVELOPMENT_ONLY"       # Quick local iteration, random split or small debug set
    INTERNAL_BENCHMARK = "INTERNAL_BENCHMARK"   # Leakage-controlled offline benchmark on registered datasets
    GOLD_BENCHMARK = "GOLD_BENCHMARK"           # Verified independent evaluation on held-out India Gold Set
    PRODUCTION_MONITORING = "PRODUCTION_MONITORING" # Continuous live production shadow/monitoring run


class SplitStrategyType(str, Enum):
    """Supported data partition strategies."""
    RANDOM_STRATIFIED = "RANDOM_STRATIFIED"
    GROUP_BY_DUPLICATE = "GROUP_BY_DUPLICATE"
    GROUP_BY_TEMPLATE = "GROUP_BY_TEMPLATE"
    GROUP_BY_CAMPAIGN = "GROUP_BY_CAMPAIGN"
    GROUP_BY_JOURNEY = "GROUP_BY_JOURNEY"
    GROUP_BY_GENERATOR = "GROUP_BY_GENERATOR"
    TEMPORAL = "TEMPORAL"
    SOURCE_HOLDOUT = "SOURCE_HOLDOUT"
    LANGUAGE_HOLDOUT = "LANGUAGE_HOLDOUT"
    SCAM_FAMILY_HOLDOUT = "SCAM_FAMILY_HOLDOUT"
    COMBINED_GROUP_TEMPORAL = "COMBINED_GROUP_TEMPORAL"


class ClassificationMetrics(BaseModel):
    """First-class binary classification performance metrics."""
    accuracy: float = Field(..., ge=0.0, le=1.0)
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1: float = Field(..., ge=0.0, le=1.0)
    macro_f1: float = Field(..., ge=0.0, le=1.0)
    weighted_f1: float = Field(..., ge=0.0, le=1.0)
    false_positive_rate: float = Field(..., ge=0.0, le=1.0, description="CRITICAL: Legitimate messages falsely labeled as scam")
    false_negative_rate: float = Field(..., ge=0.0, le=1.0, description="Scam messages missed by model")
    specificity: float = Field(..., ge=0.0, le=1.0)
    balanced_accuracy: float = Field(..., ge=0.0, le=1.0)
    roc_auc: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    pr_auc: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confusion_matrix: Dict[str, int] = Field(default_factory=dict)
    sample_count: int = Field(..., ge=0)
    positive_count: int = Field(..., ge=0)
    negative_count: int = Field(..., ge=0)


class CalibrationReport(BaseModel):
    """Probability calibration diagnostics."""
    brier_score: float = Field(..., ge=0.0, le=1.0)
    expected_calibration_error: float = Field(..., ge=0.0, le=1.0)
    maximum_calibration_error: float = Field(..., ge=0.0, le=1.0)
    is_well_calibrated: bool = Field(default=False)
    interpretation: str = Field(default="")
    reliability_buckets: List[Dict[str, Any]] = Field(default_factory=list)


class LeadTimeMetrics(BaseModel):
    """Pre-Loss Detection Rate and Warning Lead Time benchmarks."""
    pre_loss_detection_rate: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Fraction of scam journeys where actionable warning fired before designated loss event"
    )
    early_detection_rate: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=1.0, 
        description="Fraction of journeys detected before initial financial or credential step"
    )
    median_warning_lead_time_sec: Optional[float] = Field(
        default=None,
        description="Median duration (seconds) between first warning and victim loss event"
    )
    mean_warning_lead_time_sec: Optional[float] = Field(default=None)
    p25_lead_time_sec: Optional[float] = Field(default=None)
    p75_lead_time_sec: Optional[float] = Field(default=None)
    p90_lead_time_sec: Optional[float] = Field(default=None)
    evaluated_journeys_count: int = Field(default=0, ge=0)


class RobustnessMetrics(BaseModel):
    """Adversarial and perturbation robustness results."""
    clean_f1: float = Field(default=0.0)
    perturbed_f1: float = Field(default=0.0)
    f1_retention_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    tested_transformations: List[str] = Field(default_factory=list)
    adversarial_sample_count: int = Field(default=0)


class LatencyCostMetrics(BaseModel):
    """Execution latency, throughput, and compute resource footprint."""
    mean_latency_ms: float = Field(..., ge=0.0)
    p50_latency_ms: float = Field(..., ge=0.0)
    p95_latency_ms: float = Field(..., ge=0.0)
    p99_latency_ms: float = Field(..., ge=0.0)
    throughput_items_per_sec: float = Field(..., ge=0.0)
    memory_peak_mb: Optional[float] = Field(default=None)
    model_size_mb: Optional[float] = Field(default=None)


class EvaluationRun(BaseModel):
    """Canonical, reproducible evaluation run artifact."""
    evaluation_id: str = Field(default_factory=lambda: generate_id("eval"))
    schema_version: str = Field(default="2.0")
    validity_status: EvaluationValidityStatus = Field(default=EvaluationValidityStatus.INTERNAL_BENCHMARK)
    
    # Model & Dataset Lineage
    model_id: str = Field(..., description="Registered model ID from models.yaml")
    model_revision: str = Field(..., description="Git hash or version string")
    dataset_id: str = Field(..., description="Registered dataset ID from datasets.yaml")
    dataset_revision: str = Field(default="main")
    
    # Timestamps
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Split
    split_strategy: SplitStrategyType
    sample_count: int = Field(..., ge=0)
    
    # Primary Metrics
    overall_metrics: ClassificationMetrics
    calibration: Optional[CalibrationReport] = None
    lead_time: Optional[LeadTimeMetrics] = None
    robustness: Optional[RobustnessMetrics] = None
    latency_cost: Optional[LatencyCostMetrics] = None
    
    # Stratified Subgroup Performance
    language_metrics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    family_metrics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    provenance_metrics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Integrity & Audit
    leakage_report: Dict[str, Any] = Field(default_factory=dict)
    environment: Dict[str, Any] = Field(default_factory=dict)
    git_commit: Optional[str] = Field(default=None)
    random_seed: int = Field(default=42)
    notes: Optional[str] = Field(default=None)
