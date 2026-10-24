"""CLI runner for model evaluation benchmarks."""

import argparse
import sys
from pathlib import Path

from ml.evaluation.adapters import BaselineModelAdapter
from ml.evaluation.runner import EvaluationOrchestrator
from ml.message.dataset_loader import load_canonical_journeys
from packages.schemas.evaluation import SplitStrategyType


def main():
    parser = argparse.ArgumentParser(description="ScamGraph Model Evaluation Runner")
    parser.add_argument("--model", type=str, default="scamgraph-message-baseline", help="Model ID")
    parser.add_argument("--dataset", type=str, default="canonical-journeys", help="Dataset ID")
    parser.add_argument(
        "--split-strategy",
        type=str,
        default="GROUP_BY_TEMPLATE",
        choices=["RANDOM_STRATIFIED", "GROUP_BY_TEMPLATE", "GROUP_BY_CAMPAIGN"],
        help="Split strategy",
    )
    args = parser.parse_args()

    print("=" * 60)
    print(f" ScamGraph AI — Evaluation Benchmark ")
    print(f" Model: {args.model}")
    print(f" Strategy: {args.split_strategy}")
    print("=" * 60)

    # Load local test records
    records = load_canonical_journeys()
    if not records:
        print("[ERROR] No local records found for evaluation.")
        sys.exit(1)

    adapter = BaselineModelAdapter()
    orchestrator = EvaluationOrchestrator()
    strategy = SplitStrategyType[args.split_strategy]

    run = orchestrator.run_evaluation(
        model_adapter=adapter,
        records=records,
        dataset_id=args.dataset,
        split_strategy=strategy,
    )

    m = run.overall_metrics
    print(f"\n[RESULTS] Evaluation ID: {run.evaluation_id}")
    print(f"  * Sample Count: {m.sample_count}")
    print(f"  * Accuracy:     {m.accuracy * 100:.2f}%")
    print(f"  * Precision:    {m.precision * 100:.2f}%")
    print(f"  * Recall:       {m.recall * 100:.2f}%")
    print(f"  * F1 Score:     {m.f1 * 100:.2f}%")
    print(f"  * False Positive Rate (FPR): {m.false_positive_rate * 100:.2f}% (CRITICAL)")
    print(f"  * False Negative Rate (FNR): {m.false_negative_rate * 100:.2f}%")
    print(f"  * Confusion Matrix: {m.confusion_matrix}")

    if run.latency_cost:
        print(f"\n[LATENCY & COMPUTE]")
        print(f"  * Mean Latency: {run.latency_cost.mean_latency_ms:.2f} ms")
        print(f"  * Throughput:   {run.latency_cost.throughput_items_per_sec:.1f} msgs/sec")

    print("\n" + "=" * 60)
    print(f" Report generated at: ml/artifacts/evaluations/")
    print("=" * 60)


if __name__ == "__main__":
    main()
