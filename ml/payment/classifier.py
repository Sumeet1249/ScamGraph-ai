import yaml
import math
from typing import Dict, Any

CONFIG_PATH = "config/payment_ml.yaml"

def load_config() -> Dict[str, Any]:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

class PaymentMLPrediction:
    def __init__(self, malicious_probability: float, risk_tier: str, confidence: float, top_risk_factors: list,
                 model_name: str = "Configured Logistic Payment-Risk Scorer",
                 model_version: str = "v1.0",
                 feature_values: Dict[str, float] = None,
                 limitations: list = None):
        self.malicious_probability = malicious_probability
        self.risk_tier = risk_tier
        self.confidence = confidence
        self.top_risk_factors = top_risk_factors
        self.is_malicious = malicious_probability >= 0.85
        self.model_name = model_name
        self.model_version = model_version
        self.feature_values = feature_values or {}
        self.limitations = limitations or []

    def model_dump(self) -> Dict[str, Any]:
        return {
            "malicious_probability": self.malicious_probability,
            "risk_tier": self.risk_tier,
            "confidence": self.confidence,
            "top_risk_factors": self.top_risk_factors,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "feature_values": self.feature_values,
            "limitations": self.limitations,
        }

class PaymentRiskClassifier:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or load_config()
        self.weights = self.config.get("weights", {})
        self.thresholds = self.config.get("thresholds", {"benign": 0.35, "suspicious": 0.65, "high_risk": 0.85})
        self.bias = self.weights.get("bias", -1.0)

    def _logistic(self, z: float) -> float:
        return 1 / (1 + math.exp(-z))

    def predict(self, features: Dict[str, float]) -> PaymentMLPrediction:
        # Linear combination
        z = self.bias
        for name, weight in self.weights.items():
            if name == "bias":
                continue
            z += weight * features.get(name, 0.0)
        prob = self._logistic(z)
        # Determine tier
        if prob < self.thresholds.get("benign", 0.35):
            tier = "BENIGN"
        elif prob < self.thresholds.get("suspicious", 0.65):
            tier = "SUSPICIOUS"
        elif prob < self.thresholds.get("high_risk", 0.85):
            tier = "HIGH_RISK"
        else:
            tier = "MALICIOUS"
        # Simple top risk factor extraction (largest weight contributions)
        contributions = {k: self.weights.get(k, 0) * features.get(k, 0) for k in features.keys()}
        top_factors = sorted(contributions, key=contributions.get, reverse=True)[:3]
        return PaymentMLPrediction(
            malicious_probability=prob,
            risk_tier=tier,
            confidence=prob,
            top_risk_factors=top_factors,
            feature_values=features,
            limitations=["Weights are hand‑crafted prototype; no training data used."]
        )
