"""Advanced leakage-safe data splitting strategies for ScamGraph AI."""

from collections import defaultdict
import hashlib
import random
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from packages.schemas.evaluation import SplitStrategyType


def extract_template_signature(text: str) -> str:
    """Normalize text into an abstracted structural template signature.
    
    Replaces entities (phones, URLs, OTPs, amounts, banks) with canonical tokens.
    """
    import re
    clean = text.lower()
    # Replace URLs
    clean = re.sub(r"https?://\S+|www\.\S+", "<URL>", clean)
    # Replace Indian phone numbers (10 digits)
    clean = re.sub(r"(?:\+91|0)?[6-9]\d{9}", "<PHONE>", clean)
    # Replace Amounts (e.g. Rs 5000, INR 500, ₹1000)
    clean = re.sub(r"(?:rs\.?|inr|₹)\s*\d+(?:,\d+)*(?:\.\d+)?", "<AMOUNT>", clean)
    # Replace OTP / PIN
    clean = re.sub(r"\b\d{4,6}\b", "<CODE>", clean)
    # Replace standard banks
    clean = re.sub(r"\b(sbi|hdfc|icici|pnb|axis|bob|kotak|canara)\b", "<BANK>", clean)
    # Strip whitespace & non-alphanumeric
    clean = re.sub(r"[^\w\s<>]", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


class DatasetSplitter:
    """Partitions records into Train / Validation / Test sets using leakage-safe strategies."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def split_random_stratified(
        self,
        records: List[Any],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        label_extractor: Callable[[Any], int] = lambda r: getattr(r, "label", 0),
    ) -> Tuple[List[Any], List[Any], List[Any]]:
        """Stratified random partition (development only, susceptible to template leakage)."""
        rng = random.Random(self.seed)
        class_buckets: Dict[int, List[Any]] = defaultdict(list)
        for r in records:
            class_buckets[label_extractor(r)].append(r)

        train, val, test = [], [], []
        for _, items in class_buckets.items():
            rng.shuffle(items)
            n = len(items)
            n_train = int(n * train_ratio)
            n_val = int(n * val_ratio)
            train.extend(items[:n_train])
            val.extend(items[n_train:n_train + n_val])
            test.extend(items[n_train + n_val:])
        return train, val, test

    def split_grouped(
        self,
        records: List[Any],
        group_key_func: Callable[[Any], str],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ) -> Tuple[List[Any], List[Any], List[Any]]:
        """Group-isolated partition: all items sharing the same group key stay in the same split."""
        rng = random.Random(self.seed)
        groups: Dict[str, List[Any]] = defaultdict(list)
        for r in records:
            k = group_key_func(r)
            groups[k].append(r)

        group_keys = list(groups.keys())
        rng.shuffle(group_keys)

        total_items = len(records)
        target_train = int(total_items * train_ratio)
        target_val = int(total_items * val_ratio)

        train, val, test = [], [], []
        curr_train, curr_val = 0, 0

        for gk in group_keys:
            items = groups[gk]
            if curr_train + len(items) <= target_train or not train:
                train.extend(items)
                curr_train += len(items)
            elif curr_val + len(items) <= target_val or not val:
                val.extend(items)
                curr_val += len(items)
            else:
                test.extend(items)

        return train, val, test

    def split_by_template(
        self,
        records: List[Any],
        text_extractor: Callable[[Any], str] = lambda r: getattr(r, "text", getattr(r, "content", "")),
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ) -> Tuple[List[Any], List[Any], List[Any]]:
        """Template-isolated split: messages with identical structural templates never cross splits."""
        return self.split_grouped(
            records=records,
            group_key_func=lambda r: extract_template_signature(text_extractor(r)),
            train_ratio=train_ratio,
            val_ratio=val_ratio,
            test_ratio=test_ratio,
        )

    def split_by_campaign(
        self,
        records: List[Any],
        campaign_extractor: Callable[[Any], str] = lambda r: getattr(r, "campaign_id", "unassigned"),
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ) -> Tuple[List[Any], List[Any], List[Any]]:
        """Campaign-isolated split: tests whether model generalizes to completely unseen campaigns."""
        return self.split_grouped(
            records=records,
            group_key_func=campaign_extractor,
            train_ratio=train_ratio,
            val_ratio=val_ratio,
            test_ratio=test_ratio,
        )

    def split_source_holdout(
        self,
        records: List[Any],
        holdout_source: str,
        source_extractor: Callable[[Any], str] = lambda r: getattr(r, "source_dataset", ""),
    ) -> Tuple[List[Any], List[Any]]:
        """Source holdout split: train on all other sources, evaluate on the target holdout source."""
        train = [r for r in records if source_extractor(r) != holdout_source]
        test = [r for r in records if source_extractor(r) == holdout_source]
        return train, test
