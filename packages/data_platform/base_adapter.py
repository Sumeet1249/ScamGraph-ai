"""Abstract Base Dataset Adapter Interface.

Every external dataset must map cleanly into ScamGraphRecordV2 without scattering
ad-hoc dataset-specific column names throughout model code.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path

from packages.schemas.dataset import ScamGraphRecordV2


class DatasetAdapter(ABC):
    """Abstract adapter transforming raw external records into ScamGraphRecordV2."""

    @property
    @abstractmethod
    def dataset_id(self) -> str:
        """Registered dataset ID."""
        pass

    @property
    @abstractmethod
    def declared_license(self) -> str:
        """Dataset license (e.g. Apache-2.0, MIT, CC-BY-NC-4.0)."""
        pass

    @abstractmethod
    def load_raw(self, source_path_or_df: Any) -> List[Any]:
        """Load raw source records."""
        pass

    @abstractmethod
    def map_record(self, raw_item: Any) -> ScamGraphRecordV2:
        """Convert a single raw item into a canonical ScamGraphRecordV2."""
        pass

    def convert_dataset(self, source_items: List[Any]) -> List[ScamGraphRecordV2]:
        """Convert an entire collection of raw records with validation."""
        converted: List[ScamGraphRecordV2] = []
        for item in source_items:
            try:
                rec = self.map_record(item)
                if rec and rec.content.strip():
                    converted.append(rec)
            except Exception:
                continue
        return converted
