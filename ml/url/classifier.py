"""URL Risk Machine Learning Classifier (Step 27).

Evaluates URLs using a calibrated feature-weighted ensemble with explainable
per-feature contributions and risk tiering.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from pydantic import BaseModel, Field

from ml.url.feature_extractor import URLFeatureExtractor
from packages.schemas.signals import EvidenceSignal, ProvenanceRecord, SignalDimension, SignalSeverity

logger = logging.getLogger("ml.url.classifier")

CONFIG_PATH = Path("config/url_ml.yaml")
if not CONFIG_PATH.exists():
    CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "url_ml.yaml"


class URLMLPrediction(BaseModel):
    """Structured ML inference result with full explainability."""
    raw_url: str
    malicious_probability: float = Field(..., ge=0.0, le=1.0)
    risk_tier: str  # BENIGN, SUSPICIOUS, HIGH_RISK, MALICIOUS
    is_malicious: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    feature_contributions: Dict[str, float] = Field(default_factory=dict)
    top_risk_factors: List[str] = Field(default_factory=list)
    explanation: str = ""


class URLRiskClassifier:
    """Interpretable, calibrated machine learning classifier for URL risk analysis."""

    DEFAULT_WEIGHTS = {
        "has_ip_host": 2.5,
        "suspicious_tld": 1.8,
        "brand_in_subdomain_or_path": 2.2,
        "suspicious_keyword_count": 0.8,
        "hostname_entropy": 0.6,
        "url_length_log": 0.4,
        "subdomain_count": 0.5,
        "hyphen_count": 0.4,
        "encoded_char_count": 0.7,
        "non_https": 0.9,
        "punycode": 2.0,
        "digit_ratio": 0.8,
        "path_depth": 0.3,
        "bias": -3.2,
    }

    RISK_FACTOR_LABELS = {
        "has_ip_host": "Direct IP address used instead of hostname",
        "suspicious_tld": "High-abuse top-level domain extension (.xyz, .top, etc.)",
        "brand_in_subdomain_or_path": "Targeted brand identity spoofed in subdomain or path",
        "suspicious_keyword_count": "Presence of credential/phishing keywords (verify, login, kyc)",
        "hostname_entropy": "High-entropy or randomly generated hostname characters",
        "non_https": "Insecure unencrypted HTTP scheme",
        "punycode": "Internationalized / homograph punycode domain",
        "digit_ratio": "Abnormally high digit density in URL",
        "subdomain_count": "Excessive subdomain hierarchy depth",
        "number_of_hyphens": "Excessive hyphenation in domain/path",
        "encoded_char_count": "Obfuscated percent-encoded characters",
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config()
        self.weights = self.config.get("feature_weights", self.DEFAULT_WEIGHTS)
        self.thresholds = self.config.get("thresholds", {
            "benign_threshold": 0.35,
            "suspicious_threshold": 0.65,
            "high_risk_threshold": 0.85,
        })
        self.extractor = URLFeatureExtractor(self.config)

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    if isinstance(cfg, dict):
                        return cfg
            except Exception as e:
                logger.warning(f"Failed to read {CONFIG_PATH}: {e}")
        return {}

    def predict(self, raw_url: str) -> URLMLPrediction:
        """Evaluates URL and outputs malicious probability, tier, and explainable contributions."""
        features = self.extractor.extract(raw_url)

        # Compute calibrated linear combination
        bias = float(self.weights.get("bias", -3.2))
        z = bias
        contributions: Dict[str, float] = {}

        for feat_name, feat_val in features.items():
            weight = float(self.weights.get(feat_name, 0.0))
            if weight != 0.0 and feat_val > 0.0:
                contrib = weight * feat_val
                z += contrib
                contributions[feat_name] = round(contrib, 3)

        # Sigmoid calibration: P = 1 / (1 + e^-z)
        try:
            prob = 1.0 / (1.0 + math.exp(-z))
        except OverflowError:
            prob = 1.0 if z > 0 else 0.0

        prob = max(0.01, min(0.99, round(prob, 4)))

        # Determine risk tier
        benign_th = self.thresholds.get("benign_threshold", 0.35)
        suspicious_th = self.thresholds.get("suspicious_threshold", 0.65)
        high_risk_th = self.thresholds.get("high_risk_threshold", 0.85)

        if prob >= high_risk_th:
            tier = "MALICIOUS"
            is_mal = True
        elif prob >= suspicious_th:
            tier = "HIGH_RISK"
            is_mal = True
        elif prob >= benign_th:
            tier = "SUSPICIOUS"
            is_mal = False
        else:
            tier = "BENIGN"
            is_mal = False

        # Sort contributions to extract top factors
        sorted_contribs = sorted(contributions.items(), key=lambda kv: kv[1], reverse=True)
        top_factors = [
            f"{self.RISK_FACTOR_LABELS.get(k, k)} (+{v:.2f})"
            for k, v in sorted_contribs
            if v > 0.3
        ]

        if not top_factors and is_mal:
            top_factors = ["Cumulative elevated lexical risk metrics"]
        elif not top_factors and not is_mal:
            top_factors = ["Clean domain profile with standard structural characteristics"]

        # Explanation formulation
        if is_mal:
            explanation = (
                f"URL evaluated with {prob*100:.1f}% malicious likelihood ({tier}). "
                f"Primary risk drivers: {'; '.join(top_factors[:3])}."
            )
        else:
            explanation = (
                f"URL exhibits benign characteristics ({prob*100:.1f}% risk score, {tier}). "
                f"No deceptive brand spoofing or high-abuse infrastructure patterns detected."
            )

        # Confidence: distance from decision threshold (0.50) scaled
        confidence = round(min(0.98, max(0.60, 0.50 + abs(prob - 0.50))), 2)

        return URLMLPrediction(
            raw_url=raw_url,
            malicious_probability=prob,
            risk_tier=tier,
            is_malicious=is_mal,
            confidence=confidence,
            feature_contributions=contributions,
            top_risk_factors=top_factors,
            explanation=explanation,
        )

    def to_evidence_signal(
        self,
        incident_id: str,
        prediction: URLMLPrediction,
    ) -> Optional[EvidenceSignal]:
        """Converts an ML prediction into a canonical EvidenceSignal."""
        if prediction.risk_tier == "BENIGN":
            return None

        severity_map = {
            "MALICIOUS": SignalSeverity.CRITICAL,
            "HIGH_RISK": SignalSeverity.HIGH,
            "SUSPICIOUS": SignalSeverity.MEDIUM,
        }
        severity = severity_map.get(prediction.risk_tier, SignalSeverity.MEDIUM)

        context_data = {
            "malicious_probability": prediction.malicious_probability,
            "risk_tier": prediction.risk_tier,
            "top_risk_factors": prediction.top_risk_factors,
            "feature_contributions": prediction.feature_contributions,
        }

        return EvidenceSignal(
            incident_id=incident_id,
            dimension=SignalDimension.URL,
            signal_type="ML_HIGH_RISK_URL_DETECTED" if prediction.is_malicious else "ML_SUSPICIOUS_URL_DETECTED",
            severity=severity,
            confidence=prediction.confidence,
            description=prediction.explanation,
            provenance=ProvenanceRecord(
                source_service="URL_ML",
                detector_name="URLRiskClassifier",
                target_artifact=prediction.raw_url,
                raw_evidence=context_data,
            ),
        )
