"""Configuration for Adaptive Intervention Engine (Step 14).

Centralized configuration of configurable prototype thresholds and friction rules
to prevent alert fatigue while safeguarding users before financial harm.
"""

from typing import Dict, Any

# ─────────────────────────────────────────────────────────────────────────────
# 1. Base Threat Risk Score Brackets (Threat Risk Index: 0 to 100)
# ─────────────────────────────────────────────────────────────────────────────
INTERVENTION_THRESHOLDS: Dict[str, int] = {
    "PRE_PAYMENT_INTERVENTION": 80,
    "STRONG_WARNING": 65,
    "CAUTION": 40,
    "PASSIVE": 20,
    "NONE": 0,
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. Friction Delay Timing (Seconds)
# ─────────────────────────────────────────────────────────────────────────────
FRICTION_SECONDS: Dict[str, int] = {
    "PRE_PAYMENT_INTERVENTION": 10,
    "STRONG_WARNING": 5,
    "CAUTION": 2,
    "PASSIVE": 0,
    "NONE": 0,
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. Escalation / De-escalation Policy Configuration
# ─────────────────────────────────────────────────────────────────────────────
# Minimum events/stages before pre-payment disruptive intervention can ever be issued
MIN_JOURNEY_EVENTS_FOR_PRE_PAYMENT: int = 2

# Risk threshold where payment proximity automatically escalates CAUTION -> STRONG_WARNING
PAYMENT_PROXIMITY_ESCALATION_THRESHOLD: int = 45

# Risk threshold where payment proximity escalates STRONG_WARNING -> PRE_PAYMENT_INTERVENTION
PAYMENT_PROXIMITY_PRE_PAYMENT_THRESHOLD: int = 65

# Maximum intervention tier allowed when evidence confidence is LOW
MAX_INTERVENTION_ON_LOW_CONFIDENCE: str = "STRONG_WARNING"

# Maximum intervention tier allowed when verified counter-evidence exists
MAX_INTERVENTION_ON_COUNTER_EVIDENCE: str = "CAUTION"
