"""Risk Engine Configuration and Heuristic Weights (Step 13).

Centralized configuration of transparent heuristic points for the Threat Risk Index
and Evidence Confidence calibration.
"""

from typing import Dict

# ─────────────────────────────────────────────────────────────────────────────
# 1. Threat Risk Index Base Points (Max contribution capped at 100)
# ─────────────────────────────────────────────────────────────────────────────
THREAT_CATEGORY_POINTS: Dict[str, int] = {
    "IMPERSONATION": 25,
    "URGENCY": 20,
    "CREDENTIAL_REQUEST": 30,
    "OTP_REQUEST": 35,
    "PAYMENT_REQUEST": 25,
    "SUSPICIOUS_URL": 25,
    "KNOWN_RELATIONSHIP": 10,
}

# Amplification from deterministic pattern match
PATTERN_MATCH_AMPLIFICATION: Dict[str, int] = {
    "STRONG": 18,
    "MODERATE": 10,
    "WEAK": 4,
    "NONE": 0,
}

# Discount points deducted for verified counter-evidence
COUNTER_EVIDENCE_DISCOUNT_POINTS: int = 25

# Minimum independent evidence sources required to claim HIGH confidence
MIN_SOURCES_FOR_HIGH_CONFIDENCE: int = 3
MIN_SOURCES_FOR_MEDIUM_CONFIDENCE: int = 2

# Risk Level Classification Thresholds (Threat Risk Index 0 - 100)
RISK_LEVEL_THRESHOLDS = {
    "HIGH": 65,
    "MEDIUM": 35,
    "LOW": 0,
}
