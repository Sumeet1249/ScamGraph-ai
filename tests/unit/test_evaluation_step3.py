"""Comprehensive test suite for Phase 0C Evaluation Infrastructure."""

import pytest
from packages.schemas.evaluation import (
    ClassificationMetrics,
    EvaluationRun,
    EvaluationValidityStatus,
    LeadTimeMetrics,
    SplitStrategyType,
)
from ml.evaluation.metrics import compute_classification_metrics, compute_lead_time_metrics
from ml.evaluation.splits import DatasetSplitter, extract_template_signature
from ml.evaluation.leakage import LeakageAuditor
from ml.evaluation.robustness import AdversarialPerturbationGenerator
from ml.evaluation.multilingual import evaluate_multilingual, evaluate_by_scam_family
from ml.evaluation.calibration import CalibrationAnalyzer
from ml.evaluation.adapters import BaselineModelAdapter


def test_compute_classification_metrics_fpr_visibility():
    """Verify FPR, FNR, and confusion matrix are accurately calculated."""
    y_true = [0, 0, 0, 0, 1, 1, 1, 1]
    y_pred = [0, 0, 0, 1, 1, 1, 1, 0]  # 1 FP, 1 FN
    y_prob = [0.1, 0.2, 0.3, 0.8, 0.9, 0.85, 0.95, 0.4]

    m = compute_classification_metrics(y_true, y_pred, y_prob)
    assert m.accuracy == 0.75
    assert m.false_positive_rate == 0.25  # 1 FP out of 4 negatives
    assert m.false_negative_rate == 0.25  # 1 FN out of 4 positives
    assert m.confusion_matrix["fp"] == 1
    assert m.confusion_matrix["fn"] == 1
    assert m.confusion_matrix["tp"] == 3
    assert m.confusion_matrix["tn"] == 3
    assert m.roc_auc is not None


def test_pre_loss_detection_rate_and_lead_time():
    """Verify Pre-Loss Detection Rate and Warning Lead Time metrics."""
    journeys = [
        {
            "journey_id": "j1",
            "has_loss": True,
            "loss_timestamp_sec": 1000,
            "first_warning_sec": 400,  # 600s lead time
            "detected_early": True,
        },
        {
            "journey_id": "j2",
            "has_loss": True,
            "loss_timestamp_sec": 800,
            "first_warning_sec": 600,  # 200s lead time
            "detected_early": True,
        },
        {
            "journey_id": "j3",
            "has_loss": True,
            "loss_timestamp_sec": 500,
            "first_warning_sec": 700,  # Warning after loss (failure)
            "detected_early": False,
        },
    ]

    m = compute_lead_time_metrics(journeys)
    assert m.evaluated_journeys_count == 3
    assert m.pre_loss_detection_rate == round(2 / 3, 4)
    assert m.early_detection_rate == round(2 / 3, 4)
    assert m.median_warning_lead_time_sec == 400.0  # median of [600, 200] = 400.0


def test_template_extraction_and_grouping():
    """Verify template signature extracts canonical tokens."""
    t1 = "Your SBI account 9876543210 will be blocked today update at https://sbi.tk/up"
    t2 = "Your HDFC account 9123456789 will be blocked today update at https://hdfc.ml/kyc"
    
    sig1 = extract_template_signature(t1)
    sig2 = extract_template_signature(t2)
    assert sig1 == sig2
    assert "<BANK>" in sig1
    assert "<PHONE>" in sig1
    assert "<URL>" in sig1


def test_leakage_detection_exact_and_template():
    """Verify detection of exact duplicates and cross-split template leakage."""
    train_records = [
        {"text": "Your SBI account will be blocked visit https://sbi.tk", "label": 1},
        {"text": "Meeting scheduled tomorrow at 10 AM", "label": 0},
    ]
    test_records = [
        {"text": "Your SBI account will be blocked visit https://sbi.tk", "label": 1},  # Exact dupe
        {"text": "Your HDFC account will be blocked visit https://hdfc.ml", "label": 1}, # Template dupe
    ]

    auditor = LeakageAuditor()
    result = auditor.audit_splits(
        train_records, 
        test_records, 
        text_extractor=lambda r: r["text"]
    )
    assert result.is_leakage_free is False
    assert result.exact_duplicates_count == 1
    assert result.template_overlaps_count == 2
    assert len(result.warnings) > 0


def test_deterministic_splitting():
    """Verify split reproducibility given the same seed."""
    records = [{"id": f"rec_{i}", "text": f"Msg {i}", "label": i % 2} for i in range(50)]
    splitter = DatasetSplitter(seed=123)
    train1, val1, test1 = splitter.split_random_stratified(records)
    
    splitter2 = DatasetSplitter(seed=123)
    train2, val2, test2 = splitter2.split_random_stratified(records)
    
    assert [r["id"] for r in train1] == [r["id"] for r in train2]
    assert [r["id"] for r in test1] == [r["id"] for r in test2]


def test_adversarial_perturbation_generator():
    """Verify non-destructive adversarial perturbations."""
    gen = AdversarialPerturbationGenerator(seed=42)
    original = "Your account has been blocked. Transfer Rs. 5000 immediately."
    variants = gen.generate_all_variants(original)
    
    assert original != variants["case_variation"]
    assert "₹" in variants["currency_swap"] or "Rs." in variants["currency_swap"]
    assert len(variants) == 4


def test_multilingual_subgroup_low_sample_policy():
    """Verify low sample size policy marks groups with N < 5 as INSUFFICIENT_SAMPLE_SIZE."""
    records = [
        {"language": "en"},
        {"language": "en"},
        {"language": "en"},
        {"language": "en"},
        {"language": "en"},
        {"language": "bhojpuri"}, # N=1
    ]
    y_true = [0, 1, 0, 1, 0, 1]
    y_pred = [0, 1, 0, 1, 0, 0]

    res = evaluate_multilingual(records, y_true, y_pred, language_extractor=lambda r: r["language"])
    assert res["en"]["status"] == "VALID"
    assert res["bhojpuri"]["status"] == "INSUFFICIENT_SAMPLE_SIZE"
    assert res["bhojpuri"]["support"] == 1


def test_calibration_analyzer():
    """Verify Expected Calibration Error (ECE) computation."""
    analyzer = CalibrationAnalyzer(n_bins=5)
    y_true = [1, 1, 0, 0, 1, 0]
    y_prob = [0.9, 0.8, 0.1, 0.2, 0.7, 0.3]
    cal = analyzer.analyze_calibration(y_true, y_prob)
    assert cal.expected_calibration_error >= 0.0
    assert len(cal.reliability_scores) > 0


def test_baseline_adapter_inference():
    """Verify BaselineModelAdapter predict and predict_proba contracts."""
    adapter = BaselineModelAdapter()
    texts = [
        "Your electricity power will be disconnected tonight at 9:30 PM call officer now",
        "Your salary for October has been credited to your bank account",
    ]
    probs = adapter.predict_proba(texts)
    preds = adapter.predict(texts)
    
    assert len(probs) == 2
    assert len(preds) == 2
    assert all(0.0 <= p <= 1.0 for p in probs)
    # The electricity scam text should score higher probability than benign salary credit
    assert probs[0] > probs[1]
