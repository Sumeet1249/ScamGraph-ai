"""Adaptive Intervention Engine (Step 14).

Implements context-aware, anti-alert-fatigue intervention decisions.
Its goal is NOT scam classification; its goal is to decide WHEN and HOW to interrupt the user.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from services.api.app.domain.enums import ConfidenceLevel, InterventionType, MatchLevel
from services.api.app.domain.models import PatternMatch
from services.pattern_engine.matcher.intervention_config import (
    FRICTION_SECONDS,
    INTERVENTION_THRESHOLDS,
    MAX_INTERVENTION_ON_COUNTER_EVIDENCE,
    MAX_INTERVENTION_ON_LOW_CONFIDENCE,
    MIN_JOURNEY_EVENTS_FOR_PRE_PAYMENT,
    PAYMENT_PROXIMITY_ESCALATION_THRESHOLD,
    PAYMENT_PROXIMITY_PRE_PAYMENT_THRESHOLD,
)

TIER_ORDER = [
    InterventionType.NONE,
    InterventionType.PASSIVE,
    InterventionType.CAUTION,
    InterventionType.STRONG_WARNING,
    InterventionType.PRE_PAYMENT_INTERVENTION,
]


class InterventionDecision(BaseModel):
    """Authoritative output of the Adaptive Intervention Engine."""
    action: InterventionType
    friction_delay_seconds: int = 0
    title: str = ""
    guidance: str = ""
    reasons: List[str] = Field(default_factory=list)
    dismissible: bool = True
    payment_blocked: bool = False


class AdaptiveInterventionEngine:
    """Decides calibrated user intervention to prevent alert fatigue."""

    def __init__(self, thresholds: Optional[Dict[str, int]] = None):
        self.thresholds = thresholds or INTERVENTION_THRESHOLDS

    def decide_intervention(
        self,
        risk_score: int,
        evidence_confidence: Union[ConfidenceLevel, str],
        journey_stage: str = "INITIAL_CONTACT",
        payment_proximity: bool = False,
        pattern_match: Optional[PatternMatch] = None,
        counter_evidence: Optional[List[str]] = None,
        num_events: int = 1,
    ) -> InterventionDecision:
        """Determines the appropriate intervention tier.
        
        Args:
            risk_score: Threat Risk Index (0 - 100 integer)
            evidence_confidence: LOW, MEDIUM, or HIGH
            journey_stage: Current stage in user journey
            payment_proximity: True if victim is on a payment page or near payment intent
            pattern_match: Evaluated PatternMatch if any
            counter_evidence: Verified safety/whitelist indicators
            num_events: Count of observed events in journey
        """
        reasons: List[str] = []
        conf_str = (
            evidence_confidence.value
            if isinstance(evidence_confidence, ConfidenceLevel)
            else str(evidence_confidence).upper()
        )
        counter_ev = counter_evidence or []

        # ── 1. Base Action Determination from Risk Score ──
        if risk_score >= self.thresholds["PRE_PAYMENT_INTERVENTION"]:
            base_action = InterventionType.PRE_PAYMENT_INTERVENTION
            reasons.append(f"Threat Risk Index {risk_score} exceeds pre-payment threshold (80)")
        elif risk_score >= self.thresholds["STRONG_WARNING"]:
            base_action = InterventionType.STRONG_WARNING
            reasons.append(f"Threat Risk Index {risk_score} exceeds strong warning threshold (65)")
        elif risk_score >= self.thresholds["CAUTION"]:
            base_action = InterventionType.CAUTION
            reasons.append(f"Threat Risk Index {risk_score} exceeds caution threshold (40)")
        elif risk_score >= self.thresholds["PASSIVE"]:
            base_action = InterventionType.PASSIVE
            reasons.append(f"Threat Risk Index {risk_score} warrants passive advisory (20)")
        else:
            base_action = InterventionType.NONE
            reasons.append(f"Threat Risk Index {risk_score} is below alert threshold (20)")

        current_idx = TIER_ORDER.index(base_action)

        # ── 2. Guard: Single Suspicious Message Protection ──
        # A single isolated event/message should NEVER trigger a disruptive pre-payment blocker
        if num_events < MIN_JOURNEY_EVENTS_FOR_PRE_PAYMENT:
            max_single_idx = TIER_ORDER.index(InterventionType.CAUTION)
            if current_idx > max_single_idx:
                current_idx = max_single_idx
                reasons.append("Alert-fatigue protection: Single event journey capped at CAUTION")

        # ── 3. Payment Proximity Escalation ──
        # If victim is directly facing a payment intent with high threat, escalate
        if payment_proximity or journey_stage in ("PAYMENT_REQUEST", "PAYMENT_INTENT"):
            if risk_score >= PAYMENT_PROXIMITY_PRE_PAYMENT_THRESHOLD and num_events >= MIN_JOURNEY_EVENTS_FOR_PRE_PAYMENT:
                target_idx = TIER_ORDER.index(InterventionType.PRE_PAYMENT_INTERVENTION)
                if current_idx < target_idx:
                    current_idx = target_idx
                    reasons.append("Payment proximity escalated alert to PRE_PAYMENT_INTERVENTION")
            elif risk_score >= PAYMENT_PROXIMITY_ESCALATION_THRESHOLD:
                target_idx = TIER_ORDER.index(InterventionType.STRONG_WARNING)
                if current_idx < target_idx:
                    current_idx = target_idx
                    reasons.append("Payment proximity escalated alert to STRONG_WARNING")

        # ── 4. Low Confidence De-escalation ──
        # Insufficient or uncorroborated evidence lowers disruption
        if conf_str == "LOW":
            max_low_conf_idx = TIER_ORDER.index(InterventionType(MAX_INTERVENTION_ON_LOW_CONFIDENCE))
            if current_idx > max_low_conf_idx:
                current_idx = max_low_conf_idx
                reasons.append("Low evidence confidence de-escalated alert from PRE_PAYMENT_INTERVENTION")
            elif current_idx == TIER_ORDER.index(InterventionType.STRONG_WARNING) and risk_score < 75:
                current_idx = TIER_ORDER.index(InterventionType.CAUTION)
                reasons.append("Low evidence confidence reduced alert to CAUTION")

        # ── 5. Counter-Evidence De-escalation ──
        # Verified safety indicators temper warnings.
        # Counter-evidence can REDUCE a higher tier, but must NEVER elevate NONE to PASSIVE.
        if counter_ev:
            max_counter_idx = TIER_ORDER.index(InterventionType(MAX_INTERVENTION_ON_COUNTER_EVIDENCE))
            if current_idx > max_counter_idx:
                current_idx = max_counter_idx
                reasons.append(f"Counter-evidence verified ({', '.join(counter_ev[:2])}): capped at CAUTION")
            elif risk_score < 50 and current_idx > TIER_ORDER.index(InterventionType.PASSIVE):
                # Only de-escalate if already above PASSIVE (i.e., CAUTION or higher)
                current_idx = TIER_ORDER.index(InterventionType.PASSIVE)
                reasons.append("Counter-evidence lowered alert to PASSIVE")

        final_action = TIER_ORDER[current_idx]
        friction_secs = FRICTION_SECONDS.get(final_action.value, 0)

        # ── 6. UI Guidance & Metadata Generation ──
        title, guidance, dismissible, blocked = self._format_guidance(
            final_action, pattern_match, journey_stage, friction_secs
        )

        return InterventionDecision(
            action=final_action,
            friction_delay_seconds=friction_secs,
            title=title,
            guidance=guidance,
            reasons=reasons,
            dismissible=dismissible,
            payment_blocked=blocked,
        )

    def _format_guidance(
        self,
        action: InterventionType,
        pattern_match: Optional[PatternMatch],
        journey_stage: str,
        friction_secs: int,
    ) -> tuple[str, str, bool, bool]:
        """Generates clear, human-understandable intervention copy."""
        pat_name = pattern_match.pattern_name if pattern_match else "Suspected Scam"

        if action == InterventionType.PRE_PAYMENT_INTERVENTION:
            return (
                f"🛑 Stop: High-Risk {pat_name} Detected",
                f"Payment step-up friction active ({friction_secs}s mandatory cooldown). "
                "Legitimate organizations will never demand immediate payment or OTP authorization over personal handles.",
                False,
                True,
            )
        elif action == InterventionType.STRONG_WARNING:
            return (
                f"⚠️ Warning: Critical Fraud Indicators Present",
                "High threat detected in this journey. Do not provide OTPs, passwords, or approve unsolicited transfer requests.",
                True,
                False,
            )
        elif action == InterventionType.CAUTION:
            return (
                "Notice: Suspicious Activity Detected",
                "Review this request carefully. Verify sender identity via official channels before proceeding.",
                True,
                False,
            )
        elif action == InterventionType.PASSIVE:
            return (
                "Advisory: Unverified Communication",
                "Sender is not in your verified contacts list. Exercise normal caution.",
                True,
                False,
            )
        else:
            return (
                "",
                "No intervention required.",
                True,
                False,
            )


# Global instance
intervention_engine = AdaptiveInterventionEngine()
