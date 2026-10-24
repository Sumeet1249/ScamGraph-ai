"""Comprehensive Data Quality, PII, Duplication, and Cross-Dataset Contamination Auditor."""

from collections import Counter, defaultdict
import hashlib
import re
from typing import Any, Dict, List, Set, Tuple

from ml.evaluation.splits import extract_template_signature
from packages.schemas.dataset import ScamGraphRecordV2


class DatasetQualityAuditor:
    """Audits dataset quality, language distributions, template diversity, and cross-dataset contamination."""

    @staticmethod
    def audit_single_dataset(records: List[ScamGraphRecordV2]) -> Dict[str, Any]:
        """Perform deep-dive quality check on a single normalized dataset."""
        if not records:
            return {"error": "Empty dataset"}

        total = len(records)
        languages = Counter([r.language.primary_language for r in records])
        scripts = Counter([r.language.script for r in records])
        labels = Counter([r.labels.get("is_scam", 0) for r in records])
        provenance_types = Counter([r.provenance.source_type.value for r in records])
        
        # PII Detection
        pii_phones_found = 0
        pii_vpa_found = 0
        pii_emails_found = 0
        
        # Deduplication & Templates
        content_hashes: Set[str] = set()
        exact_dupes = 0
        templates: Set[str] = set()

        for r in records:
            # Check text
            t = r.content
            if re.search(r"\b[6-9]\d{9}\b", t):
                pii_phones_found += 1
            if re.search(r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b", t):
                pii_vpa_found += 1
            if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", t):
                pii_emails_found += 1

            # Exact hash
            h = hashlib.sha256(t.strip().lower().encode()).hexdigest()
            if h in content_hashes:
                exact_dupes += 1
            else:
                content_hashes.add(h)

            # Template signature
            tmpl = extract_template_signature(t)
            templates.add(tmpl)

        unique_templates = len(templates)
        template_diversity_ratio = round(unique_templates / total, 4) if total else 0.0
        exact_dupe_rate = round(exact_dupes / total, 4) if total else 0.0

        return {
            "total_records": total,
            "unique_records": len(content_hashes),
            "exact_duplicate_rate": exact_dupe_rate,
            "unique_templates": unique_templates,
            "template_diversity_ratio": template_diversity_ratio,
            "class_distribution": dict(labels),
            "language_distribution": dict(languages),
            "script_distribution": dict(scripts),
            "provenance_distribution": dict(provenance_types),
            "pii_findings": {
                "unmasked_phones_detected": pii_phones_found,
                "potential_vpas_detected": pii_vpa_found,
                "potential_emails_detected": pii_emails_found,
            },
        }

    @staticmethod
    def audit_cross_dataset_contamination(
        records_a: List[ScamGraphRecordV2],
        dataset_name_a: str,
        records_b: List[ScamGraphRecordV2],
        dataset_name_b: str,
    ) -> Dict[str, Any]:
        """Detect duplicate records and shared templates across two distinct datasets."""
        hashes_a = {hashlib.sha256(r.content.strip().lower().encode()).hexdigest(): r.content for r in records_a}
        templates_a = {extract_template_signature(r.content) for r in records_a}

        exact_cross_dupes = 0
        template_cross_dupes = 0
        sample_cross_matches = []

        for r in records_b:
            h = hashlib.sha256(r.content.strip().lower().encode()).hexdigest()
            if h in hashes_a:
                exact_cross_dupes += 1
                if len(sample_cross_matches) < 5:
                    sample_cross_matches.append(r.content[:100])

            tmpl = extract_template_signature(r.content)
            if tmpl in templates_a:
                template_cross_dupes += 1

        return {
            "dataset_a": dataset_name_a,
            "count_a": len(records_a),
            "dataset_b": dataset_name_b,
            "count_b": len(records_b),
            "exact_cross_duplicates": exact_cross_dupes,
            "cross_template_overlaps": template_cross_dupes,
            "sample_cross_matches": sample_cross_matches,
            "contamination_risk": "HIGH" if exact_cross_dupes > 0 else ("MEDIUM" if template_cross_dupes > 0 else "LOW"),
        }
