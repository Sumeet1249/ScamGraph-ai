"""ScamGraph AI Evaluation Package Exports."""

from ml.evaluation.adapters import BaselineModelAdapter, ModelAdapter, benchmark_latency
from ml.evaluation.calibration import CalibrationAnalyzer, CalibrationMetrics
from ml.evaluation.leakage import LeakageAuditResult, LeakageAuditor
from ml.evaluation.metrics import compute_classification_metrics, compute_lead_time_metrics
from ml.evaluation.multilingual import (
    evaluate_by_provenance,
    evaluate_by_scam_family,
    evaluate_multilingual,
)
from ml.evaluation.robustness import AdversarialPerturbationGenerator
from ml.evaluation.runner import EvaluationOrchestrator
from ml.evaluation.splits import DatasetSplitter, extract_template_signature
from packages.schemas.evaluation import (
    CalibrationReport,
    ClassificationMetrics,
    EvaluationRun,
    EvaluationValidityStatus,
    LatencyCostMetrics,
    LeadTimeMetrics,
    RobustnessMetrics,
    SplitStrategyType,
)

__all__ = [
    "EvaluationOrchestrator",
    "ModelAdapter",
    "BaselineModelAdapter",
    "benchmark_latency",
    "DatasetSplitter",
    "extract_template_signature",
    "LeakageAuditor",
    "LeakageAuditResult",
    "CalibrationAnalyzer",
    "CalibrationMetrics",
    "AdversarialPerturbationGenerator",
    "compute_classification_metrics",
    "compute_lead_time_metrics",
    "evaluate_multilingual",
    "evaluate_by_scam_family",
    "evaluate_by_provenance",
    "EvaluationRun",
    "EvaluationValidityStatus",
    "SplitStrategyType",
    "ClassificationMetrics",
    "CalibrationReport",
    "LeadTimeMetrics",
    "RobustnessMetrics",
    "LatencyCostMetrics",
]
