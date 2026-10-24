"""Correlation Engine Configuration Loader (Phase 3B).

Parses and validates config/correlation.yaml with production defaults.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Set
import yaml

logger = logging.getLogger("correlation_engine.config")

DEFAULT_CONFIG_PATH = Path("config/correlation.yaml")


class CorrelationConfig:
    """Thread-safe configuration container for Cross-Incident Correlation Engine."""

    def __init__(self, config_dict: Dict[str, Any]):
        self.schema_version = config_dict.get("schema_version", "2.0.0")
        self.engine_version = config_dict.get("engine_version", "3.2.0")

        # Thresholds
        thresh = config_dict.get("thresholds", {})
        self.strongly_related_threshold = float(thresh.get("strongly_related_threshold", 0.78))
        self.likely_related_threshold = float(thresh.get("likely_related_threshold", 0.62))
        self.possibly_related_threshold = float(thresh.get("possibly_related_threshold", 0.45))
        self.weak_signal_threshold = float(thresh.get("weak_signal_threshold", 0.28))
        self.minimum_confidence_for_materialization = float(thresh.get("minimum_confidence_for_materialization", 0.40))
        self.review_threshold = float(thresh.get("review_threshold", 0.55))
        self.contradiction_penalty_factor = float(thresh.get("contradiction_penalty_factor", 0.40))
        self.minimum_cohort_size_for_disclosure = int(thresh.get("minimum_cohort_size_for_disclosure", 2))

        # Weights & Caps
        self.group_weights = config_dict.get("feature_group_weights", {
            "entity_weight": 0.35,
            "behavioral_weight": 0.30,
            "infrastructure_weight": 0.15,
            "temporal_weight": 0.10,
            "graph_weight": 0.10,
        })
        self.group_score_caps = config_dict.get("group_score_caps", {
            "entity": 0.45,
            "behavioral": 0.35,
            "infrastructure": 0.20,
            "temporal": 0.15,
            "graph": 0.15,
        })

        # Retrieval budget
        ret = config_dict.get("retrieval", {})
        self.max_candidates_per_source = int(ret.get("max_candidates_per_source", 25))
        self.max_total_candidates = int(ret.get("max_total_candidates", 60))
        self.time_window_days = int(ret.get("time_window_days", 90))
        self.min_retrieval_similarity = float(ret.get("min_retrieval_similarity", 0.35))

        # Super-nodes & Downweighted entities
        sn = config_dict.get("super_nodes", {})
        self.generic_brands: Set[str] = {b.upper() for b in sn.get("generic_brands", [])}
        self.common_infrastructure_domains: Set[str] = {d.lower() for d in sn.get("common_infrastructure_domains", [])}

        # Entity type informativeness
        self.entity_type_informativeness = config_dict.get("entity_type_informativeness", {
            "PAYMENT_IDENTIFIER": 1.00,
            "PHONE_NUMBER": 0.85,
            "DOMAIN": 0.80,
            "TELEGRAM_HANDLE": 0.75,
            "EMAIL": 0.70,
            "URL_PATH": 0.65,
            "BRAND": 0.05,
            "PLATFORM": 0.00,
        })

    @classmethod
    def load(cls, config_path: Path = DEFAULT_CONFIG_PATH) -> CorrelationConfig:
        """Loads configuration from YAML file or falls back to defaults."""
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                return cls(data)
            except Exception as e:
                logger.warning(f"Failed to parse {config_path}: {e}. Using fallback defaults.")
        return cls({})
