"""CLI tool for auditing and comparing datasets."""

import argparse
import json
import sys

from packages.data_platform.adapters import HinglishScamAdapter, ICFD31kAdapter, ScamHamIndiaAdapter
from packages.data_platform.auditor import DatasetQualityAuditor
from ml.message.dataset_loader import load_canonical_journeys


def main():
    parser = argparse.ArgumentParser(description="ScamGraph Data Platform Quality & Audit CLI")
    parser.add_argument("command", choices=["audit", "compare", "list-candidates"], help="Command to execute")
    parser.add_argument("--dataset", type=str, default="scamgraph-canonical-journeys", help="Target dataset ID")
    parser.add_argument("--compare-with", type=str, default=None, help="Second dataset ID for comparison")
    args = parser.parse_args()

    if args.command == "list-candidates":
        from pathlib import Path
        import yaml
        cand_path = Path("data/registry/candidates.yaml")
        if cand_path.exists():
            with open(cand_path, "r", encoding="utf-8") as f:
                cands = yaml.safe_load(f).get("candidates", [])
            print("=" * 60)
            print(" ScamGraph AI — Evaluated External Candidates ")
            print("=" * 60)
            for c in cands:
                print(f"[{c['status']}] {c['id']} ({c['name']})")
                print(f"  * Repo: {c.get('repo_id')}")
                print(f"  * Records: ~{c.get('claimed_record_count')}")
                print(f"  * License: {c.get('license')}")
                print(f"  * Action: {c.get('recommended_action')}\n")
        return

    if args.command == "audit":
        print("=" * 60)
        print(f" Auditing Dataset: {args.dataset} ")
        print("=" * 60)
        
        # Load sample records
        if args.dataset == "scamgraph-canonical-journeys":
            legacy_records = load_canonical_journeys()
            records = [r.to_scamgraph_record_v2() for r in legacy_records]
        else:
            # Fallback mock for CLI verification
            records = [
                ScamHamIndiaAdapter().map_record({"text": "Dear SBI user your KYC is blocked", "label": "spam"}),
                ScamHamIndiaAdapter().map_record({"text": "Dear customer your payment of Rs 500 received", "label": "ham"}),
            ]
            
        report = DatasetQualityAuditor.audit_single_dataset(records)
        print(json.dumps(report, indent=2))

    elif args.command == "compare":
        print("=" * 60)
        print(f" Cross-Dataset Contamination Audit: {args.dataset} vs {args.compare_with} ")
        print("=" * 60)
        
        # Controlled comparison sample
        ds_a = [
            ScamHamIndiaAdapter().map_record({"text": "Your SBI account 9876543210 is blocked", "label": "spam"}),
            ScamHamIndiaAdapter().map_record({"text": "Meeting at 5pm", "label": "ham"}),
        ]
        ds_b = [
            HinglishScamAdapter().map_record({"text": "Your HDFC account 9876543210 is blocked", "label": "spam"}), # Shared template
            HinglishScamAdapter().map_record({"text": "Your SBI account 9876543210 is blocked", "label": "spam"}), # Exact duplicate
        ]
        
        cmp_report = DatasetQualityAuditor.audit_cross_dataset_contamination(
            ds_a, args.dataset, ds_b, args.compare_with or "candidate_b"
        )
        print(json.dumps(cmp_report, indent=2))


if __name__ == "__main__":
    main()
