"""Explainable RiskEngine for ScamGraph AI (Step 18).

Consumes canonical Evidence, PatternMatch, and GraphCorrelation objects.
Produces:
- risk_score: An INDEX (0 to 100), NOT a probability.
- risk_level: LOW | MEDIUM | HIGH | INSUFFICIENT_EVIDENCE
- evidence_confidence: LOW | MEDIUM | HIGH
- reason_codes: Detailed findings linked to Evidence IDs.
- counter_evidence: Indicators of safety.
- recommended_intervention: Calibrated friction.
"""

from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from packages.schemas import (
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    RiskLevel,
    EvidenceConfidence,
    InterventionAction,
    AdaptiveIntervention,
)
from services.pattern_engine.patterns.scam_patterns import PatternMatch
from services.graph_engine.correlation.entity_service import EntityCorrelationReport

SEVERITY_POINTS = {
    SignalSeverity.INFO: 5,
    SignalSeverity.LOW: 15,
    SignalSeverity.MEDIUM: 35,
    SignalSeverity.HIGH: 65,
    SignalSeverity.CRITICAL: 90,
}


class RiskAssessment(BaseModel):
    incident_id: str
    risk_score: int = Field(..., ge=0, le=100, description="Risk Index from 0 to 100 (NOT a probability)")
    risk_level: RiskLevel
    evidence_confidence: EvidenceConfidence
    reason_codes: List[str]
    counter_evidence: List[EvidenceSignal] = Field(default_factory=list)
    recommended_intervention: AdaptiveIntervention
    pattern_name: Optional[str] = None
    is_insufficient_evidence: bool = False


class RiskEngine:
    """Computes explainable, non-probabilistic risk index and evidence confidence."""

    @staticmethod
    def evaluate(
        incident_id: str,
        signals: List[EvidenceSignal],
        pattern_match: Optional[PatternMatch] = None,
        graph_correlation: Optional[EntityCorrelationReport] = None,
        payment_proximate: bool = False,
    ) -> RiskAssessment:
        # Separate supporting vs counter evidence
        supporting = [s for s in signals if not s.is_counter_evidence]
        counter = [s for s in signals if s.is_counter_evidence]

        # Combine signals from graph correlation if provided
        if graph_correlation and graph_correlation.signals:
            for g_sig in graph_correlation.signals:
                if not any(s.signal_id == g_sig.signal_id for s in supporting):
                    supporting.append(g_sig)

        # Deduplicate correlated signals: keep highest confidence signal per (dimension, signal_type)
        deduped_map: Dict[tuple, EvidenceSignal] = {}
        for s in supporting:
            key = (s.dimension, s.signal_type)
            if key not in deduped_map or s.confidence > deduped_map[key].confidence:
                deduped_map[key] = s
        deduped_supporting = list(deduped_map.values())

        distinct_dims: Set[SignalDimension] = {s.dimension for s in deduped_supporting}
        num_dims = len(distinct_dims)
        total_unique_signals = len(deduped_supporting)
        has_critical = any(s.severity == SignalSeverity.CRITICAL for s in deduped_supporting)

        # ─────────────────────────────────────────────────────────────
        # Rule 13 & 14: Enforce INSUFFICIENT_EVIDENCE
        # ─────────────────────────────────────────────────────────────
        if (total_unique_signals < 2 or num_dims < 2) and not (has_critical and payment_proximate):
            reason_codes = [
                f"[RC_INSUFFICIENT_DATA] Evidence ID: {s.signal_id} -> {s.description}"
                for s in deduped_supporting
            ]
            if not reason_codes:
                reason_codes = ["[RC_NO_SIGNALS] No suspicious indicators observed."]

            if deduped_supporting:
                max_conf = max(float(s.confidence) for s in deduped_supporting)
                computed_score = int(round(max_conf * 100)) if max_conf <= 1.0 else int(round(max_conf))
            else:
                computed_score = 15

            return RiskAssessment(
                incident_id=incident_id,
                risk_score=computed_score,
                risk_level=RiskLevel.INSUFFICIENT_EVIDENCE if computed_score < 40 else (RiskLevel.HIGH if computed_score >= 70 else RiskLevel.MEDIUM),
                evidence_confidence=EvidenceConfidence.LOW,
                reason_codes=reason_codes,
                counter_evidence=counter,
                recommended_intervention=AdaptiveIntervention(
                    action=InterventionAction.NONE,
                    friction_delay_seconds=0,
                    banner_message="Insufficient evidence to assess risk. Monitored passively.",
                ),
                is_insufficient_evidence=computed_score < 40,
            )

        # ─────────────────────────────────────────────────────────────
        # Compute Risk Index (0 - 100)
        # ─────────────────────────────────────────────────────────────
        accumulated_points = 0.0
        total_weights = 0.0
        reason_codes = []

        for s in deduped_supporting:
            pts = SEVERITY_POINTS.get(s.severity, 25)
            w = s.weight
            accumulated_points += pts * w * s.confidence
            total_weights += w
            reason_codes.append(
                f"[RC_{s.signal_type}] Evidence ID: {s.signal_id} ({s.dimension.value}) -> {s.description}"
            )

        raw_index = accumulated_points / total_weights if total_weights > 0 else 0.0

        # Pattern match boost (explainable structural amplification)
        if pattern_match and pattern_match.is_strong_match:
            raw_index += 12.0
            reason_codes.append(
                f"[RC_PATTERN_MATCH] Matched known scam workflow: {pattern_match.pattern_name} (Score: {pattern_match.match_score})"
            )

        # Multi-dimension corroboration amplification
        if num_dims >= 3:
            raw_index += 8.0

        # Counter-evidence discount (deducts 20 points per confirmed legitimate marker)
        if counter:
            discount = 20.0 * len(counter)
            raw_index = max(5.0, raw_index - discount)
            for c in counter:
                reason_codes.append(
                    f"[RC_COUNTER_EVIDENCE] Evidence ID: {c.signal_id} -> {c.description}"
                )

        if deduped_supporting:
            max_conf = max(float(s.confidence) for s in deduped_supporting)
            base_score_from_conf = int(round(max_conf * 100)) if max_conf <= 1.0 else int(round(max_conf))
            final_risk_score = max(base_score_from_conf, int(round(min(100.0, max(0.0, raw_index)))))
        else:
            final_risk_score = int(round(min(100.0, max(0.0, raw_index))))

        # ─────────────────────────────────────────────────────────────
        # Determine Risk Level & Evidence Confidence
        # ─────────────────────────────────────────────────────────────
        if final_risk_score >= 65:
            risk_level = RiskLevel.HIGH
        elif final_risk_score >= 35:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        if num_dims >= 3:
            evidence_confidence = EvidenceConfidence.HIGH
        elif num_dims == 2:
            evidence_confidence = EvidenceConfidence.MEDIUM
        else:
            evidence_confidence = EvidenceConfidence.LOW

        # ─────────────────────────────────────────────────────────────
        # Adaptive Intervention Selection
        # ─────────────────────────────────────────────────────────────
        if risk_level == RiskLevel.HIGH and evidence_confidence == EvidenceConfidence.HIGH:
            if payment_proximate:
                intervention = AdaptiveIntervention(
                    action=InterventionAction.PRE_PAYMENT_INTERVENTION,
                    friction_delay_seconds=10,
                    banner_title="High Risk Payment Progression",
                    banner_message="Multi-source verified threat detected directly before payment intent.",
                    action_button_text="I Understand the Risk — Verify Details",
                    dismissible=False,
                )
            else:
                intervention = AdaptiveIntervention(
                    action=InterventionAction.STRONG_WARNING,
                    friction_delay_seconds=0,
                    banner_title="High Risk Scam Progression",
                    banner_message="Corroborated grooming pattern observed across multiple indicators.",
                )
        elif risk_level in (RiskLevel.HIGH, RiskLevel.MEDIUM) and evidence_confidence in (EvidenceConfidence.MEDIUM, EvidenceConfidence.HIGH):
            intervention = AdaptiveIntervention(
                action=InterventionAction.CAUTION,
                friction_delay_seconds=0,
                banner_title="Caution: Unverified Beneficiary",
                banner_message="Unusual urgency markers or unverified domain detected.",
            )
        else:
            intervention = AdaptiveIntervention(
                action=InterventionAction.PASSIVE,
                friction_delay_seconds=0,
                banner_message="Monitored passively without alert friction.",
            )

        return RiskAssessment(
            incident_id=incident_id,
            risk_score=final_risk_score,
            risk_level=risk_level,
            evidence_confidence=evidence_confidence,
            reason_codes=reason_codes,
            counter_evidence=counter,
            recommended_intervention=intervention,
            pattern_name=pattern_match.pattern_name if pattern_match else None,
            is_insufficient_evidence=False,
        )


# Global instance
risk_engine = RiskEngine()
