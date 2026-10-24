"""Comprehensive leakage audit engine for cross-split duplicates and template overlap."""

from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
import hashlib
from typing import Any, Callable, Dict, List, Set, Tuple

from ml.evaluation.splits import extract_template_signature


@dataclass
class LeakageAuditResult:
    """Findings from split leakage verification."""
    exact_duplicates_count: int
    template_overlaps_count: int
    near_duplicates_count: int
    campaign_overlaps_count: int
    train_count: int
    test_count: int
    is_leakage_free: bool
    warnings: List[str]
    sample_leakages: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exact_duplicates": self.exact_duplicates_count,
            "template_overlaps": self.template_overlaps_count,
            "near_duplicates": self.near_duplicates_count,
            "campaign_overlaps": self.campaign_overlaps_count,
            "train_samples": self.train_count,
            "test_samples": self.test_count,
            "is_leakage_free": self.is_leakage_free,
            "warnings": self.warnings,
            "sample_leakages": self.sample_leakages[:10],
        }


class LeakageAuditor:
    """Audits train and test splits for data leakage."""

    def __init__(self, near_duplicate_threshold: float = 0.90):
        self.threshold = near_duplicate_threshold

    @staticmethod
    def _normalize_text(text: str) -> str:
        import re
        return re.sub(r"\s+", " ", text.strip().lower())

    def audit_splits(
        self,
        train_records: List[Any],
        test_records: List[Any],
        text_extractor: Callable[[Any], str] = lambda r: getattr(r, "text", getattr(r, "content", "")),
        campaign_extractor: Callable[[Any], str] = lambda r: getattr(r, "campaign_id", "unassigned"),
    ) -> LeakageAuditResult:
        """Run complete leakage scan across train and test partitions."""
        warnings: List[str] = []
        sample_leakages: List[Dict[str, Any]] = []

        # 1. Exact Duplicates
        train_hashes: Dict[str, str] = {}
        for r in train_records:
            t = self._normalize_text(text_extractor(r))
            h = hashlib.sha256(t.encode("utf-8")).hexdigest()
            train_hashes[h] = t

        exact_dupes = 0
        for r in test_records:
            t = self._normalize_text(text_extractor(r))
            h = hashlib.sha256(t.encode("utf-8")).hexdigest()
            if h in train_hashes:
                exact_dupes += 1
                sample_leakages.append({
                    "type": "EXACT_DUPLICATE",
                    "text": t[:100],
                    "matched_train": train_hashes[h][:100],
                })

        if exact_dupes > 0:
            warnings.append(f"CRITICAL: Found {exact_dupes} exact duplicate messages between train and test splits.")

        # 2. Template Overlaps
        train_templates: Set[str] = {
            extract_template_signature(text_extractor(r)) for r in train_records
        }
        template_overlaps = 0
        for r in test_records:
            tmpl = extract_template_signature(text_extractor(r))
            if tmpl in train_templates:
                template_overlaps += 1

        if template_overlaps > 0:
            warnings.append(f"WARNING: {template_overlaps} test samples share identical notification templates with train set.")

        # 3. Campaign Overlaps
        train_campaigns = {
            campaign_extractor(r) for r in train_records if campaign_extractor(r) not in ("unassigned", "none", "", None)
        }
        campaign_overlaps = 0
        for r in test_records:
            c = campaign_extractor(r)
            if c and c in train_campaigns:
                campaign_overlaps += 1

        if campaign_overlaps > 0:
            warnings.append(f"WARNING: {campaign_overlaps} test samples share campaign IDs with train set.")

        # 4. Near-Duplicate Sampling (sample-based check for efficiency on larger sets)
        near_dupes = 0
        sample_size = min(200, len(test_records))
        for test_r in test_records[:sample_size]:
            test_t = self._normalize_text(text_extractor(test_r))
            for train_r in train_records[:sample_size]:
                train_t = self._normalize_text(text_extractor(train_r))
                if test_t != train_t:
                    sim = SequenceMatcher(None, test_t, train_t).ratio()
                    if sim >= self.threshold:
                        near_dupes += 1
                        break

        is_clean = (exact_dupes == 0)

        return LeakageAuditResult(
            exact_duplicates_count=exact_dupes,
            template_overlaps_count=template_overlaps,
            near_duplicates_count=near_dupes,
            campaign_overlaps_count=campaign_overlaps,
            train_count=len(train_records),
            test_count=len(test_records),
            is_leakage_free=is_clean,
            warnings=warnings,
            sample_leakages=sample_leakages,
        )
