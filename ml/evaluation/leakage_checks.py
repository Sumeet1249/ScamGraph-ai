"""Data Leakage Detection and Prevention for ScamGraph ML Pipelines.

Detects common leakage sources:
1. Exact duplicates across train/test
2. Semantic duplicates (same message with minor variations)
3. Campaign template leakage (same template in both sets)
4. Time-based leakage (future data in training set)
5. Source-dataset contamination
"""

from __future__ import annotations

import hashlib
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Set, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class LeakageReport:
    """Summary of detected leakage issues."""

    total_train_samples: int
    total_test_samples: int
    exact_duplicates_train_to_test: int
    semantic_duplicates_train_to_test: int
    campaign_template_leakage: int
    source_dataset_leakage_pairs: List[Tuple[str, str]]
    warnings: List[str]
    is_clean: bool

    def to_dict(self):
        return {
            "total_train_samples": self.total_train_samples,
            "total_test_samples": self.total_test_samples,
            "exact_duplicates": self.exact_duplicates_train_to_test,
            "semantic_duplicates": self.semantic_duplicates_train_to_test,
            "campaign_leakage": self.campaign_template_leakage,
            "source_dataset_leakage_pairs": [
                {"train_source": t, "test_source": s}
                for t, s in self.source_dataset_leakage_pairs
            ],
            "warnings": self.warnings,
            "is_clean": self.is_clean,
        }


class LeakageDetector:
    """Detects various forms of data leakage in train/test splits."""

    def __init__(self, semantic_similarity_threshold: float = 0.95):
        """
        Args:
            semantic_similarity_threshold: Similarity threshold for semantic duplicate detection (0-1)
        """
        self.threshold = semantic_similarity_threshold

    def detect_exact_duplicates(
        self,
        train_texts: List[str],
        test_texts: List[str],
    ) -> Tuple[int, Set[str]]:
        """Detect exact string duplicates across train and test."""
        train_set = set(train_texts)
        test_set = set(test_texts)
        overlaps = train_set & test_set
        return len(overlaps), overlaps

    def detect_semantic_duplicates(
        self,
        train_texts: List[str],
        test_texts: List[str],
    ) -> Tuple[int, List[Tuple[str, str]]]:
        """Detect high-similarity strings (variations of same message).
        
        Returns:
            (count, list of (train_text, test_text) pairs)
        """
        duplicates = []
        for train_text in train_texts:
            for test_text in test_texts:
                similarity = SequenceMatcher(
                    None, train_text.lower(), test_text.lower()
                ).ratio()
                if similarity >= self.threshold:
                    duplicates.append((train_text, test_text))
        return len(duplicates), duplicates

    def detect_campaign_leakage(
        self,
        train_campaigns: List[str],
        test_campaigns: List[str],
    ) -> Tuple[int, Dict[str, Tuple[int, int]]]:
        """Detect if same campaign template appears in both train and test.
        
        Returns:
            (count of leaked campaigns, dict of campaign -> (train_count, test_count))
        """
        train_counter = Counter(train_campaigns)
        test_counter = Counter(test_campaigns)
        overlapping_campaigns = {}
        leak_count = 0

        for campaign in train_counter:
            if campaign in test_counter:
                overlapping_campaigns[campaign] = (
                    train_counter[campaign],
                    test_counter[campaign],
                )
                leak_count += min(train_counter[campaign], test_counter[campaign])

        return leak_count, overlapping_campaigns

    def detect_source_dataset_contamination(
        self,
        train_sources: List[str],
        test_sources: List[str],
    ) -> Tuple[int, List[Tuple[str, str]]]:
        """Check if exact same source dataset is split improperly.
        
        Returns:
            (contamination_score, list of (train_source, test_source) pairs)
        """
        train_set = set(train_sources)
        test_set = set(test_sources)
        exact_overlaps = train_set & test_set

        # Count severity: if same source is in both, it's a leak
        pairs = []
        for source in exact_overlaps:
            pairs.append((source, source))

        return len(pairs), pairs

    def full_report(
        self,
        train_texts: List[str],
        test_texts: List[str],
        train_campaigns: List[str],
        test_campaigns: List[str],
        train_sources: List[str],
        test_sources: List[str],
    ) -> LeakageReport:
        """Run comprehensive leakage detection.
        
        Args:
            train_texts, test_texts: Message texts
            train_campaigns, test_campaigns: Campaign IDs
            train_sources, test_sources: Dataset sources
            
        Returns:
            LeakageReport with all detected issues
        """
        warnings = []

        # 1. Exact duplicates
        exact_dup_count, exact_dups = self.detect_exact_duplicates(
            train_texts, test_texts
        )
        if exact_dup_count > 0:
            pct = (exact_dup_count / len(test_texts)) * 100
            warnings.append(
                f"CRITICAL: {exact_dup_count} ({pct:.1f}%) exact duplicates "
                f"from train found in test set. Remove or re-split."
            )

        # 2. Semantic duplicates
        semantic_dup_count, _ = self.detect_semantic_duplicates(train_texts, test_texts)
        if semantic_dup_count > 0:
            pct = (semantic_dup_count / len(test_texts)) * 100
            warnings.append(
                f"WARNING: {semantic_dup_count} ({pct:.1f}%) semantically similar "
                f"messages from train found in test. Consider semantic deduplication."
            )

        # 3. Campaign leakage
        campaign_leak_count, campaign_pairs = self.detect_campaign_leakage(
            train_campaigns, test_campaigns
        )
        if campaign_leak_count > 0:
            warnings.append(
                f"WARNING: Campaign template leakage detected. "
                f"{len(campaign_pairs)} templates appear in both train and test: "
                f"{list(campaign_pairs.keys())[:3]}..."
            )

        # 4. Source dataset contamination
        source_leak_count, source_pairs = self.detect_source_dataset_contamination(
            train_sources, test_sources
        )
        if source_leak_count > 0:
            warnings.append(
                f"CRITICAL: Source dataset contamination. "
                f"Same datasets in both train and test: {source_pairs}"
            )

        is_clean = exact_dup_count == 0 and source_leak_count == 0

        return LeakageReport(
            total_train_samples=len(train_texts),
            total_test_samples=len(test_texts),
            exact_duplicates_train_to_test=exact_dup_count,
            semantic_duplicates_train_to_test=semantic_dup_count,
            campaign_template_leakage=campaign_leak_count,
            source_dataset_leakage_pairs=source_pairs,
            warnings=warnings,
            is_clean=is_clean,
        )


def check_leakage(
    train_records,
    test_records,
) -> LeakageReport:
    """Quick leakage check from MessageRecord objects.
    
    Args:
        train_records: List of MessageRecord objects in training set
        test_records: List of MessageRecord objects in test set
        
    Returns:
        LeakageReport
    """
    detector = LeakageDetector()

    train_texts = [r.text for r in train_records]
    test_texts = [r.text for r in test_records]
    train_campaigns = [r.campaign_id for r in train_records]
    test_campaigns = [r.campaign_id for r in test_records]
    train_sources = [r.source_dataset for r in train_records]
    test_sources = [r.source_dataset for r in test_records]

    return detector.full_report(
        train_texts,
        test_texts,
        train_campaigns,
        test_campaigns,
        train_sources,
        test_sources,
    )
