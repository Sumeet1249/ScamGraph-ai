#!/usr/bin/env python3
"""Phase 3: Specialist Model Benchmarking.

Benchmarks:
1. Multilingual Message Detector (Horizon-Labs/phishing-scam-detector-base)
2. URL Detection (URLBERT - optional, requires additional setup)
3. Hard Negatives Test (legitimate messages that resemble scams)
4. Language-Specific Evaluation (English, Hindi, Hinglish separately)

Compares against baseline (TF-IDF + Logistic Regression).

Usage:
    python ml/evaluation/phase_3_specialist_benchmark.py --models all
    python ml/evaluation/phase_3_specialist_benchmark.py --models multilingual
    python ml/evaluation/phase_3_specialist_benchmark.py --test-set hard-negatives
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from sklearn.model_selection import train_test_split

from ml.evaluation.benchmark_runner import BenchmarkRunner
from ml.evaluation.calibration import calibration_report
from ml.evaluation.leakage_checks import check_leakage
from ml.message.baseline import BaselineMessageModel
from ml.message.dataset_loader import load_all_datasets
from ml.message.preprocessor import MessagePreprocessor

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def load_trained_baseline(artifacts_dir: Optional[Path] = None) -> BaselineMessageModel:
    """Load previously trained baseline model."""
    print("Loading trained baseline model...")
    baseline_model = BaselineMessageModel.load(artifacts_dir)
    print("✓ Baseline model loaded\n")
    return baseline_model


def benchmark_multilingual_transformer(
    test_texts: List[str],
    test_labels: np.ndarray,
    benchmark_runner: BenchmarkRunner,
    sample_size: Optional[int] = None,
) -> None:
    """Benchmark Horizon-Labs multilingual phishing detector.
    
    Args:
        test_texts: List of message texts
        test_labels: Array of true labels
        benchmark_runner: BenchmarkRunner instance
        sample_size: Limit evaluation to N samples (for memory constraints)
    """
    print("=" * 80)
    print("BENCHMARKING: Multilingual Transformer (Horizon-Labs)")
    print("=" * 80 + "\n")

    try:
        from ml.message.transformer_adapter import load_recommended_model

        # Sample if needed (transformers can be memory-intensive)
        if sample_size:
            sample_indices = np.random.choice(len(test_texts), sample_size, replace=False)
            sample_texts = [test_texts[i] for i in sample_indices]
            sample_labels = test_labels[sample_indices]
            print(f"Evaluating on {sample_size} test samples (sampled from {len(test_texts)})")
        else:
            sample_texts = test_texts
            sample_labels = test_labels
            print(f"Evaluating on full {len(test_texts)} test samples")

        # Load model
        print("Loading Horizon-Labs/phishing-scam-detector-base...")
        transformer = load_recommended_model("phishing_scam_detector_base", device="auto")
        print("✓ Model loaded\n")

        # Inference
        print("Running inference...")
        transformer_probs = transformer.predict_proba(sample_texts)[:, 1]
        transformer_preds = transformer.predict(sample_texts)
        print(f"✓ Inference complete\n")

        # Record result
        benchmark_runner.record_result(
            model_name="Horizon-Labs/phishing-scam-detector-base",
            model_id="transformer_phishing_detector",
            test_set_name=f"In-Distribution ({len(sample_texts)} samples)",
            test_set_id="in_distribution_transformer",
            y_true=sample_labels,
            y_pred=transformer_preds,
            y_prob=transformer_probs,
            notes="Multilingual transformer (307M params). Detects phishing, scams, and spam.",
        )

        # Calibration analysis
        print("\nCalibration Analysis:")
        print(calibration_report(sample_labels, transformer_probs, "Multilingual Transformer"))

        # Cleanup
        transformer.unload()
        print("✓ Model unloaded from memory\n")

    except ImportError as e:
        print(f"⚠ Cannot load multilingual transformer: {e}")
        print("  Install with: pip install transformers torch\n")
    except Exception as e:
        logger.exception(f"Error benchmarking multilingual transformer: {e}")
        print(f"⚠ Error during transformer benchmark: {e}\n")


def benchmark_language_specific(
    records,
    benchmark_runner: BenchmarkRunner,
    baseline_model: BaselineMessageModel,
) -> None:
    """Evaluate baseline separately for each language.
    
    Args:
        records: All message records
        benchmark_runner: BenchmarkRunner instance
        baseline_model: Trained baseline model
    """
    print("=" * 80)
    print("LANGUAGE-SPECIFIC EVALUATION")
    print("=" * 80 + "\n")

    # Group by language
    language_records = {}
    for record in records:
        lang = record.language
        if lang not in language_records:
            language_records[lang] = []
        language_records[lang].append(record)

    # Evaluate each language
    for lang, lang_records in sorted(language_records.items(), key=lambda x: -len(x[1])):
        if len(lang_records) < 20:  # Skip languages with too few samples
            continue

        # Split language-specific data
        texts = [r.text for r in lang_records]
        labels = np.array([r.label for r in lang_records])

        # 80-20 split for this language
        train_texts, test_texts, train_labels, test_labels = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )

        # Evaluate
        predictions = baseline_model.predict(test_texts)
        probs = baseline_model.predict_proba(test_texts)[:, 1]

        # Record
        benchmark_runner.record_result(
            model_name="TF-IDF + Logistic Regression",
            model_id="baseline_tfidf_lr",
            test_set_name=f"Language: {lang} ({len(test_texts)} samples)",
            test_set_id=f"language_{lang}",
            y_true=test_labels,
            y_pred=predictions,
            y_prob=probs,
            notes=f"Baseline evaluated on {lang} language samples only.",
        )

        print(f"  {lang:<15} | Samples: {len(test_texts):<4} | F1: {benchmark_runner.results[-1].metrics.f1_score:.4f}")

    print()


def create_hard_negatives_recommendations() -> str:
    """Generate recommendations for hard negatives test set creation.
    
    Returns:
        Formatted recommendations text
    """
    recommendations = """
================================================================================
HARD NEGATIVES TEST SET RECOMMENDATIONS
================================================================================

Purpose: Test false positive rate on legitimate messages that resemble scams.

Recommended Categories (200-300 total):

1. LEGITIMATE BANK ALERTS (50 examples)
   ├─ "Your account has been accessed from a new device"
   ├─ "Confirm your recent transaction: ₹5,000 to XYZ"
   ├─ "Your credit limit has been increased to ₹50,000"
   └─ "Two-factor authentication enabled on your account"

2. DELIVERY & LOGISTICS (50 examples)
   ├─ "Your order is out for delivery today"
   ├─ "Package delivered. Signature required at address"
   ├─ "Your shipment has been delayed. Tracking: ABC123"
   └─ "Deliver by 6 PM: Click here for details"

3. GENUINE BILL REMINDERS (50 examples)
   ├─ "Your electricity bill (₹2,500) is due on 30th Dec"
   ├─ "Water bill payment received. Thank you"
   ├─ "Internet plan will expire on 15th Jan"
   └─ "Medical bill invoice ready: ₹10,000"

4. REAL JOB NOTIFICATIONS (30 examples)
   ├─ "Job offer from TCS: Software Engineer role"
   ├─ "Interview scheduled for 2 PM on Tuesday"
   ├─ "Your resume was viewed by 5 companies"
   └─ "Salary credited to your account"

5. ROUTINE SERVICE UPDATES (20 examples)
   ├─ "Your insurance renewal is due"
   ├─ "GST filing deadline extended to 31st March"
   ├─ "New terms of service available for review"
   └─ "System maintenance scheduled for tonight"

Collection Strategy:
├─ Source: Official bank/service provider templates
├─ Review: Have non-technical users verify authenticity
├─ Language: Include English, Hindi, Hinglish
├─ Label: All marked as "ham" (legitimate)
└─ Validation: Cross-check against official sources

Success Metric:
├─ False Positive Rate should remain < 5% on hard negatives
├─ If FPR > 10%: Model over-flags legitimate messages
└─ If FPR < 2%: Model may be under-cautious

================================================================================
"""
    return recommendations


def main():
    parser = argparse.ArgumentParser(
        description="Phase 3: Specialist Model Benchmarking"
    )
    parser.add_argument(
        "--models",
        choices=["all", "multilingual", "baseline"],
        default="all",
        help="Which models to benchmark",
    )
    parser.add_argument(
        "--test-set",
        choices=["standard", "hard-negatives", "language-specific"],
        default="standard",
        help="Which test set to use",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Sample size for transformer evaluation (default: full test set)",
    )
    args = parser.parse_args()

    try:
        # Initialize benchmark runner
        benchmark_runner = BenchmarkRunner(
            output_dir=ROOT_DIR / "ml" / "message" / "artifacts" / "benchmarks"
        )

        # Load baseline model
        baseline_model = load_trained_baseline()

        # Load test data
        print("Loading test data...")
        records = load_all_datasets()
        preprocessor = MessagePreprocessor(test_ratio=0.2, random_seed=42)
        partitioned, _ = preprocessor.partition_leakage_free(records)
        test_records = [r for r in partitioned if r.split == "test"]
        test_texts = [r.text for r in test_records]
        test_labels = np.array([r.label for r in test_records])
        print(f"✓ Loaded {len(test_texts)} test samples\n")

        # Baseline comparison
        print("Establishing baseline results for comparison...")
        baseline_preds = baseline_model.predict(test_texts)
        baseline_probs = baseline_model.predict_proba(test_texts)[:, 1]
        benchmark_runner.record_result(
            model_name="TF-IDF + Logistic Regression (Baseline)",
            model_id="baseline_tfidf_lr",
            test_set_name="In-Distribution Test (full)",
            test_set_id="in_distribution_full",
            y_true=test_labels,
            y_pred=baseline_preds,
            y_prob=baseline_probs,
            notes="Baseline for comparison",
        )
        print(f"✓ Baseline F1: {benchmark_runner.results[-1].metrics.f1_score:.4f}\n")

        # Run selected benchmarks
        if args.test_set == "standard":
            if args.models in ("all", "multilingual"):
                benchmark_multilingual_transformer(
                    test_texts,
                    test_labels,
                    benchmark_runner,
                    sample_size=args.sample_size or 100,
                )

        elif args.test_set == "language-specific":
            benchmark_language_specific(
                [r for r in partitioned if r.split == "test"],
                benchmark_runner,
                baseline_model,
            )

        elif args.test_set == "hard-negatives":
            print(create_hard_negatives_recommendations())

        # Save results
        if benchmark_runner.results:
            print("Saving benchmark results...")
            results_path = benchmark_runner.save_results("benchmark_results_phase3.json")
            report_path = benchmark_runner.save_report("benchmark_report_phase3.txt")
            print(f"✓ Results: {results_path}")
            print(f"✓ Report: {report_path}\n")

            # Print comparison
            print("\n" + benchmark_runner.generate_comparison_report())

        print("\n" + "=" * 80)
        print("PHASE 3 BENCHMARKING COMPLETE")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.exception(f"Phase 3 failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
