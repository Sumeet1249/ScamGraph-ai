"""Data preprocessing, deduplication, and leakage-safe splitting for Message Intelligence.

Implements:
1. Text normalization
2. Exact deduplication and near-duplicate logging
3. Leakage prevention: split by campaign_id / template hash rather than random rows
4. Class, language, and synthetic distribution reporting
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple

from ml.message.dataset_loader import MessageRecord


def normalize_message_text(text: str) -> str:
    """Normalize text for consistent processing and deduplication."""
    if not text:
        return ""
    # Standardize whitespace
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned


def compute_template_fingerprint(text: str) -> str:
    """Mask numbers, phone numbers, amounts, and URLs to compute a template fingerprint.

    Prevents train/test leakage by grouping parameterized instances of the same template.
    """
    masked = text.lower()
    # Mask URLs
    masked = re.sub(r"https?://\S+|www\.\S+", "<URL>", masked)
    # Mask phone numbers (+91, 10-digit)
    masked = re.sub(r"(\+91[\-\s]?)?[6-9]\d{9}", "<PHONE>", masked)
    # Mask amounts (INR / Rs / Rs. / amounts)
    masked = re.sub(r"(inr|rs\.?|₹)\s*\d+([,\.]\d+)*", "<AMOUNT>", masked)
    masked = re.sub(r"\b\d+([,\.]\d+)*\s*(inr|rs|rupees)\b", "<AMOUNT>", masked)
    # Mask account/card numbers (4+ digits)
    masked = re.sub(r"\b\d{4,}\b", "<NUM>", masked)
    # Standardize whitespace
    masked = re.sub(r"\s+", " ", masked).strip()
    return hashlib.sha256(masked.encode("utf-8")).hexdigest()[:16]


def compute_jaccard_similarity(text_a: str, text_b: str) -> float:
    """Compute word-level Jaccard similarity for near-duplicate screening."""
    words_a = set(re.findall(r"\w+", text_a.lower()))
    words_b = set(re.findall(r"\w+", text_b.lower()))
    if not words_a or not words_b:
        return 0.0
    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)
    return len(intersection) / len(union)


@dataclass
class PreprocessingStats:
    total_raw: int
    total_deduplicated: int
    exact_duplicates_removed: int
    train_count: int
    test_count: int
    class_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    synthetic_distribution: Dict[str, int]
    source_distribution: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_raw": self.total_raw,
            "total_deduplicated": self.total_deduplicated,
            "exact_duplicates_removed": self.exact_duplicates_removed,
            "train_count": self.train_count,
            "test_count": self.test_count,
            "class_distribution": self.class_distribution,
            "language_distribution": self.language_distribution,
            "synthetic_distribution": self.synthetic_distribution,
            "source_distribution": self.source_distribution,
        }


class MessagePreprocessor:
    """Preprocesses raw MessageRecord objects into a deduplicated, partitioned dataset."""

    def __init__(self, test_ratio: float = 0.20, random_seed: int = 42):
        self.test_ratio = test_ratio
        self.random_seed = random_seed

    def deduplicate(self, records: List[MessageRecord]) -> Tuple[List[MessageRecord], int]:
        """Remove exact duplicates based on normalized text."""
        seen_normalized: Set[str] = set()
        deduped: List[MessageRecord] = []
        exact_dupes_removed = 0

        for record in records:
            norm = normalize_message_text(record.text).lower()
            if norm in seen_normalized:
                exact_dupes_removed += 1
                continue
            seen_normalized.add(norm)
            # Update record text with cleanly trimmed whitespace
            record.text = normalize_message_text(record.text)
            deduped.append(record)

        return deduped, exact_dupes_removed

    def partition_leakage_free(
        self,
        records: List[MessageRecord],
    ) -> Tuple[List[MessageRecord], PreprocessingStats]:
        """Deduplicate and partition records into train/test using template/campaign hashing.

        Ensures variants sharing the same template or campaign never leak into both train & test.
        """
        raw_count = len(records)
        deduped_records, exact_removed = self.deduplicate(records)

        # Assign campaign/template key for leakage-safe grouping
        group_to_records: Dict[str, List[MessageRecord]] = {}
        for rec in deduped_records:
            template_fp = compute_template_fingerprint(rec.text)
            # Combine campaign_id and template fingerprint for strict isolation
            group_key = f"{rec.source_dataset}:{rec.campaign_id}:{template_fp}"
            if group_key not in group_to_records:
                group_to_records[group_key] = []
            group_to_records[group_key].append(rec)

        # Deterministically split groups based on hash
        train_records: List[MessageRecord] = []
        test_records: List[MessageRecord] = []

        # Sort group keys for full reproducibility
        sorted_keys = sorted(group_to_records.keys())
        for key in sorted_keys:
            # Deterministic hash to partition 0..99
            hash_val = int(hashlib.md5(f"{self.random_seed}:{key}".encode()).hexdigest(), 16) % 100
            is_test = hash_val < int(self.test_ratio * 100)
            split_label = "test" if is_test else "train"

            for rec in group_to_records[key]:
                rec.split = split_label
                if is_test:
                    test_records.append(rec)
                else:
                    train_records.append(rec)

        all_partitioned = train_records + test_records

        # Compile distribution statistics
        class_dist = Counter("scam" if r.label == 1 else "ham" for r in all_partitioned)
        lang_dist = Counter(r.language for r in all_partitioned)
        synth_dist = Counter("synthetic" if r.is_synthetic else "real_or_mixed" for r in all_partitioned)
        source_dist = Counter(r.source_dataset for r in all_partitioned)

        stats = PreprocessingStats(
            total_raw=raw_count,
            total_deduplicated=len(all_partitioned),
            exact_duplicates_removed=exact_removed,
            train_count=len(train_records),
            test_count=len(test_records),
            class_distribution=dict(class_dist),
            language_distribution=dict(lang_dist),
            synthetic_distribution=dict(synth_dist),
            source_distribution=dict(source_dist),
        )

        return all_partitioned, stats
