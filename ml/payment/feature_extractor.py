from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional, Set
import yaml
import math

CONFIG_PATH = Path("config/payment_ml.yaml")
if not CONFIG_PATH.exists():
    CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "payment_ml.yaml"

class PaymentFeatureExtractor:
    """Extracts a numeric feature vector from payment related payloads.

    Features include characteristics of VPA handles, amount patterns,
    transaction type flags and simple heuristics for suspicious keywords.
    The extractor mirrors the style of the URL feature extractor for
    consistency across the ML pipeline.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config()
        self.suspicious_keywords: Set[str] = set(
            kw.lower() for kw in self.config.get("suspicious_keywords", ["verify", "otp", "login", "update", "claim", "bank", "upi"])
        )
        self.high_value_threshold: float = self.config.get("high_value_threshold", 10000.0)
        self.medium_value_threshold: float = self.config.get("medium_value_threshold", 1000.0)

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                pass
        return {}

    @staticmethod
    def _normalize_vpa(vpa: str) -> str:
        """Return a lower‑cased, stripped VPA without surrounding whitespaces.
        If the input is empty or None, returns an empty string.
        """
        return (vpa or "").strip().lower()

    @staticmethod
    def _extract_amount_features(amount: Any) -> Dict[str, float]:
        """Create simple bucketed amount features.
        The amount may be a string or numeric type; non‑numeric values are treated as 0.
        """
        try:
            amt = float(amount)
        except Exception:
            amt = 0.0
        log_amt = 0.0 if amt <= 0 else (math.log2(amt) / 10.0)  # scaled log
        return {
            "amount": amt,
            "amount_log": log_amt,
            "high_value": 1.0 if amt >= 10000 else 0.0,
            "medium_value": 1.0 if 1000 <= amt < 10000 else 0.0,
            "low_value": 1.0 if amt < 1000 else 0.0,
        }

    def _keyword_score(self, text: str) -> float:
        lowered = (text or "").lower()
        count = sum(1 for kw in self.suspicious_keywords if kw in lowered)
        return float(count)

    def extract(self, payload: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from a payment payload dict.

        Expected keys (based on ``PaymentPayload`` schema):
        - ``vpa`` (or ``payment_id``) – the virtual payment address string.
        - ``claimed_payee_name`` – free‑form name of the payee.
        - ``amount`` – numeric or string amount.
        - ``transaction_type`` – e.g. ``collect``, ``direct_pay``, ``qr``, ``intent``.
        - ``reference_note`` – optional note field.
        """
        vpa_raw = payload.get("vpa") or payload.get("payment_id") or ""
        vpa = self._normalize_vpa(vpa_raw)

        # VPA structural features
        vpa_len = len(vpa)
        digit_count = sum(1 for c in vpa if c.isdigit())
        hyphen_count = vpa.count("-")
        at_parts = vpa.split("@")
        local_part = at_parts[0] if at_parts else ""
        domain_part = at_parts[1] if len(at_parts) > 1 else ""
        domain_len = len(domain_part)
        local_len = len(local_part)
        # Simple regex flags for common patterns
        has_upi = 1.0 if re.search(r"@?upi", vpa) else 0.0
        has_bank = 1.0 if re.search(r"bank", vpa) else 0.0

        # Amount feature set
        amount_features = self._extract_amount_features(payload.get("amount"))

        # Transaction type one‑hot (up to four known types)
        txn_type = (payload.get("transaction_type") or "").lower()
        txn_collect = 1.0 if "collect" in txn_type else 0.0
        txn_direct = 1.0 if "direct" in txn_type else 0.0
        txn_qr = 1.0 if "qr" in txn_type else 0.0
        txn_intent = 1.0 if "intent" in txn_type else 0.0

        # Keyword counts from free‑form fields
        payee_name = payload.get("claimed_payee_name", "")
        reference_note = payload.get("reference_note", "")
        kw_score = self._keyword_score(" ".join([payee_name, reference_note, vpa]))

        return {
            # VPA structural features (canonical names)
            "vpa_local_len": float(local_len),
            "vpa_domain_len": float(domain_len),
            "vpa_has_digits": float(digit_count) / max(1, vpa_len),
            "vpa_has_hyphens": float(hyphen_count),
            # optional UPI/bank flags are kept for possible future use but not weighted
            "vpa_has_upi": has_upi,
            "vpa_has_bank": has_bank,
            # Amount features
            "amount_log": float(amount_features["amount_log"]),
            "amount_category_low": amount_features["low_value"],
            "amount_category_medium": amount_features["medium_value"],
            "amount_category_high": amount_features["high_value"],
            # Transaction type one‑hot (canonical keys)
            "transaction_type_collect": txn_collect,
            "transaction_type_direct_pay": txn_direct,
            "transaction_type_qr": txn_qr,
            "transaction_type_intent": txn_intent,
            # Keyword / suspicion score
            "vpa_suspicious_keyword": kw_score,
        }
