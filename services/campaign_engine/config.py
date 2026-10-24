"""Campaign Engine Configuration Loader (Phase 3C).

Parses and validates config/campaign.yaml with production defaults.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict
import yaml

logger = logging.getLogger("campaign_engine.config")

DEFAULT_CONFIG_PATH = Path("config/campaign.yaml")


class CampaignConfig:
    """Thread-safe configuration container for Campaign Intelligence V2 & Outbreak Radar."""

    def __init__(self, config_dict: Dict[str, Any]):
        self.schema_version = config_dict.get("schema_version", "2.0.0")
        self.engine_version = config_dict.get("engine_version", "3.3.0")

        # Lifecycle Thresholds
        lc = config_dict.get("lifecycle_thresholds", {})
        self.candidate_min_incidents = int(lc.get("candidate_min_incidents", 3))
        self.active_min_incidents = int(lc.get("active_min_incidents", 5))
        self.relationship_density_threshold = float(lc.get("relationship_density_threshold", 0.60))
        self.strong_edge_min_ratio = float(lc.get("strong_edge_min_ratio", 0.50))
        self.dna_consistency_min = float(lc.get("dna_consistency_min", 0.65))
        self.dormant_inactivity_days = int(lc.get("dormant_inactivity_days", 30))
        self.resurgence_window_days = int(lc.get("resurgence_window_days", 90))

        # Velocity & Outbreak Thresholds
        vel = config_dict.get("velocity_thresholds", {})
        self.baseline_window_days = int(vel.get("baseline_window_days", 14))
        self.rising_growth_multiplier = float(vel.get("rising_growth_multiplier", 1.50))
        self.surging_growth_multiplier = float(vel.get("surging_growth_multiplier", 2.20))
        self.outbreak_growth_multiplier = float(vel.get("outbreak_growth_multiplier", 3.50))
        self.outbreak_min_volume_24h = int(vel.get("outbreak_min_volume_24h", 8))
        self.emerging_min_volume_24h = int(vel.get("emerging_min_volume_24h", 4))
        self.max_duplicate_ratio = float(vel.get("max_duplicate_ratio", 0.35))

        # Radar Visual Settings
        r = config_dict.get("radar", {})
        rings = r.get("rings", {})
        self.critical_radius = int(rings.get("critical_radius", 120))
        self.surging_radius = int(rings.get("surging_radius", 220))
        self.emerging_radius = int(rings.get("emerging_radius", 320))
        self.canvas_size = int(r.get("canvas_size", 700))
        self.sweep_duration_seconds = float(r.get("sweep_duration_seconds", 4.0))


def load_campaign_config(config_path: Path = DEFAULT_CONFIG_PATH) -> CampaignConfig:
    """Loads configuration from YAML file or falls back to production defaults."""
    if not config_path.exists():
        logger.warning(f"Config path {config_path} not found. Using defaults.")
        return CampaignConfig({})

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw_dict = yaml.safe_load(f) or {}
        return CampaignConfig(raw_dict)
    except Exception as e:
        logger.error(f"Failed to parse {config_path}: {e}. Falling back to defaults.")
        return CampaignConfig({})


# Global singleton configuration
campaign_config = load_campaign_config()
