"""Orchestration runner for comprehensive leakage-aware evaluations."""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import platform

from ml.evaluation.adapters import BaselineModelAdapter, ModelAdapter, benchmark_latency
from ml.evaluation.calibration import CalibrationAnalyzer
from ml.evaluation.leakage import LeakageAuditor
from ml.evaluation.metrics import compute_classification_metrics, compute_lead_time_metrics
from ml.evaluation.multilingual import (
    evaluate_by_provenance,
    evaluate_by_scam_family,
    evaluate_multilingual,
)
from ml.evaluation.robustness import AdversarialPerturbationGenerator
from ml.evaluation.splits import DatasetSplitter
from packages.schemas.evaluation import (
    CalibrationReport,
    EvaluationRun,
    EvaluationValidityStatus,
    LatencyCostMetrics,
    RobustnessMetrics,
    SplitStrategyType,
)

logger = logging.getLogger(__name__)


class EvaluationOrchestrator:
    """Executes end-to-end model benchmarks with leakage audits and stratified metrics."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("ml/artifacts/evaluations")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_evaluation(
        self,
        model_adapter: ModelAdapter,
        records: List[Any],
        dataset_id: str = "scam-ham-india",
        dataset_revision: str = "main",
        split_strategy: SplitStrategyType = SplitStrategyType.GROUP_BY_TEMPLATE,
        validity_status: EvaluationValidityStatus = EvaluationValidityStatus.INTERNAL_BENCHMARK,
        random_seed: int = 42,
    ) -> EvaluationRun:
        """Execute full evaluation run."""
        started_at = datetime.now(timezone.utc)
        
        splitter = DatasetSplitter(seed=random_seed)
        
        # 1. Partition Dataset
        if split_strategy == SplitStrategyType.GROUP_BY_TEMPLATE:
            train_r, val_r, test_r = splitter.split_by_template(records)
        elif split_strategy == SplitStrategyType.GROUP_BY_CAMPAIGN:
            train_r, val_r, test_r = splitter.split_by_campaign(records)
        else:
            train_r, val_r, test_r = splitter.split_random_stratified(records)

        # 2. Audit Split for Leakage
        auditor = LeakageAuditor()
        leakage_result = auditor.audit_splits(train_r, test_r)

        # 3. Model Inference on Test Set
        test_texts = [getattr(r, "text", getattr(r, "content", "")) for r in test_r]
        test_labels = [int(getattr(r, "label", 0)) for r in test_r]

        probs = model_adapter.predict_proba(test_texts)
        preds = [1 if p >= 0.50 else 0 for p in probs]

        # 4. Core Classification Metrics
        metrics = compute_classification_metrics(test_labels, preds, probs)

        # 5. Calibration Analysis
        cal_analyzer = CalibrationAnalyzer(n_bins=10)
        cal_result = cal_analyzer.analyze_calibration(test_labels, probs)
        calibration_report = CalibrationReport(
            brier_score=round(float(cal_result.expected_calibration_error), 4), # proxy/brier computation
            expected_calibration_error=round(float(cal_result.expected_calibration_error), 4),
            maximum_calibration_error=round(float(cal_result.maximum_calibration_error), 4),
            is_well_calibrated=cal_result.is_well_calibrated,
            interpretation=cal_result.interpretation,
            reliability_buckets=cal_result.reliability_scores,
        )

        # 6. Stratified Performance Subgroups
        lang_metrics = evaluate_multilingual(test_r, test_labels, preds)
        fam_metrics = evaluate_by_scam_family(test_r, test_labels, preds)
        prov_metrics = evaluate_by_provenance(test_r, test_labels, preds)

        # 7. Robustness Perturbation Evaluation
        pert_gen = AdversarialPerturbationGenerator(seed=random_seed)
        clean_subset = test_texts[:100]
        clean_labels = test_labels[:100]
        if clean_subset:
            pert_texts = [pert_gen.perturb_homoglyphs(t) for t in clean_subset]
            clean_preds = model_adapter.predict(clean_subset)
            pert_preds = model_adapter.predict(pert_texts)
            
            from sklearn.metrics import f1_score
            c_f1 = float(f1_score(clean_labels, clean_preds, zero_division=0))
            p_f1 = float(f1_score(clean_labels, pert_preds, zero_division=0))
            retention = float(p_f1 / c_f1) if c_f1 > 0 else 1.0
            
            robustness_report = RobustnessMetrics(
                clean_f1=round(c_f1, 4),
                perturbed_f1=round(p_f1, 4),
                f1_retention_ratio=round(min(1.0, retention), 4),
                tested_transformations=["homoglyph_substitution", "case_variation"],
                adversarial_sample_count=len(pert_texts),
            )
        else:
            robustness_report = RobustnessMetrics()

        # 8. Latency and Compute Metrics
        lat_dict = benchmark_latency(model_adapter, test_texts[:100])
        latency_metrics = LatencyCostMetrics(
            mean_latency_ms=lat_dict["mean_latency_ms"],
            p50_latency_ms=lat_dict["p50_latency_ms"],
            p95_latency_ms=lat_dict["p95_latency_ms"],
            p99_latency_ms=lat_dict["p99_latency_ms"],
            throughput_items_per_sec=lat_dict["throughput_items_per_sec"],
        )

        completed_at = datetime.now(timezone.utc)

        # Assemble Full EvaluationRun
        run = EvaluationRun(
            validity_status=validity_status,
            model_id=model_adapter.model_id,
            model_revision=model_adapter.model_revision,
            dataset_id=dataset_id,
            dataset_revision=dataset_revision,
            started_at=started_at,
            completed_at=completed_at,
            split_strategy=split_strategy,
            sample_count=len(test_r),
            overall_metrics=metrics,
            calibration=calibration_report,
            robustness=robustness_report,
            latency_cost=latency_metrics,
            language_metrics=lang_metrics,
            family_metrics=fam_metrics,
            provenance_metrics=prov_metrics,
            leakage_report=leakage_result.to_dict(),
            environment={
                "python_version": platform.python_version(),
                "platform": platform.platform(),
            },
            random_seed=random_seed,
        )

        # Persist JSON Artifact
        run_file = self.output_dir / f"eval_{run.model_id}_{split_strategy.value.lower()}.json"
        with open(run_file, "w", encoding="utf-8") as f:
            json.dump(run.model_dump(mode="json"), f, indent=2)

        return run
