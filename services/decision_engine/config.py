"""Unified Decision Engine Configuration Loader (Phase 4A)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict
import yaml

logger = logging.getLogger("decision_engine.config")

DEFAULT_CONFIG_PATH = Path("config/decision.yaml")


class DecisionConfig:
    """Thread-safe configuration for Tripartite Decision Engine."""

    def __init__(self, config_dict: Dict[str, Any]):
        self.schema_version = config_dict.get("schema_version", "2.0.0")
        self.engine_version = config_dict.get("engine_version", "4.1.0")

        # Dimension weights
        weights = config_dict.get("dimension_weights", {})
        self.weight_message_nlp = float(weights.get("message_nlp", 0.15))
        self.weight_url_safety = float(weights.get("url_safety", 0.15))
        self.weight_entity_trust = float(weights.get("entity_trust", 0.15))
        self.weight_tactic_manipulation = float(weights.get("tactic_manipulation", 0.15))
        self.weight_journey_stage = float(weights.get("journey_stage", 0.15))
        self.weight_scam_dna = float(weights.get("scam_dna", 0.10))
        self.weight_campaign_outbreak = float(weights.get("campaign_outbreak", 0.15))

        # Journey urgency multipliers
        self.journey_urgency = config_dict.get("journey_urgency_multipliers", {
            "INITIAL_CONTACT": 0.25,
            "ENGAGEMENT_GROOMING": 0.40,
            "PLATFORM_MIGRATION": 0.55,
            "CREDENTIAL_OTP_HARVEST": 0.85,
            "PAYMENT_REQUEST": 0.90,
            "PAYMENT_INTENT": 1.00,
            "EXTORTION_PRESSURE": 0.95,
            "WITHDRAWAL_BLOCK": 0.70,
        })

        # Thresholds
        thresh = config_dict.get("action_thresholds", {})
        self.block_min_risk = float(thresh.get("block_pre_loss", {}).get("min_risk", 0.85))
        self.block_min_conf = float(thresh.get("block_pre_loss", {}).get("min_confidence", 0.75))
        self.block_min_urg = float(thresh.get("block_pre_loss", {}).get("min_urgency", 0.70))

        self.delay_min_risk = float(thresh.get("delay_payment", {}).get("min_risk", 0.65))
        self.delay_min_urg = float(thresh.get("delay_payment", {}).get("min_urgency", 0.60))

        self.strong_warn_min_risk = float(thresh.get("strong_warning", {}).get("min_risk", 0.65))
        self.strong_warn_min_conf = float(thresh.get("strong_warning", {}).get("min_confidence", 0.60))

        self.warn_min_risk = float(thresh.get("warn", {}).get("min_risk", 0.40))
        self.verify_min_risk = float(thresh.get("verify_independently", {}).get("min_risk", 0.25))
        self.verify_max_conf = float(thresh.get("verify_independently", {}).get("max_confidence", 0.55))
        self.educate_min_risk = float(thresh.get("educate", {}).get("min_risk", 0.20))

        # Adjustments
        self.counter_discount_factor = float(config_dict.get("counter_evidence_discount_factor", 0.40))
        self.uncertainty_penalty = float(config_dict.get("missing_dimension_uncertainty_penalty", 0.08))


def load_decision_config(path: Path = DEFAULT_CONFIG_PATH) -> DecisionConfig:
    if not path.exists():
        logger.warning(f"Config path {path} not found. Using defaults.")
        return DecisionConfig({})
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return DecisionConfig(raw)
    except Exception as e:
        logger.error(f"Failed to load {path}: {e}")
        return DecisionConfig({})


decision_config = load_decision_config()
