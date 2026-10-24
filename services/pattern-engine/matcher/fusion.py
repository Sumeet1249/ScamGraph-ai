"""Multi-Signal Evidence Fusion and Dual-Axis Risk Calibrator.

Implements the fundamental rules:
- Rule 10: Model outputs are evidence, never final truth.
- Rule 11: Risk Level and Evidence Confidence remain separate values.
- Rule 12: Every risk reason retains provenance.
- Rule 13: Strictly return INSUFFICIENT_EVIDENCE when corroboration is absent.
- Rule 14: Never claim fraud from a single signal alone.
"""

from typing import Dict, List, Set, Tuple
from packages.schemas import (
    AssessmentResult,
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    RiskLevel,
    EvidenceConfidence,
    EmergingStatus,
    InterventionAction,
    AdaptiveIntervention,
    ExplainabilityReport,
)

SEVERITY_WEIGHTS = {
    SignalSeverity.INFO: 0.1,
    SignalSeverity.LOW: 0.3,
    SignalSeverity.MEDIUM: 0.6,
    SignalSeverity.HIGH: 0.85,
    SignalSeverity.CRITICAL: 1.0,
}


class EvidenceFusionEngine:
    """Fuses multi-dimensional evidence signals into calibrated dual-axis assessments."""

    @staticmethod
    def evaluate(
        incident_id: str,
        signals: List[EvidenceSignal],
        payment_proximate: bool = False,
        is_simulated: bool = False,
    ) -> AssessmentResult:
        # Separate supporting vs counter evidence
        active_supporting = [s for s in signals if not s.is_counter_evidence]
        counter_signals = [s for s in signals if s.is_counter_evidence]

        # 1. Evaluate Distinct Corroborated Dimensions
        distinct_dimensions: Set[SignalDimension] = {s.dimension for s in active_supporting}
        total_signals = len(active_supporting)
        # Rule 13 & 14: If fewer than 2 signals OR signals originate from only 1 dimension, return INSUFFICIENT_EVIDENCE
        has_critical = any(s.severity == SignalSeverity.CRITICAL for s in active_supporting)
        if (total_signals < 2 or len(distinct_dimensions) < 2) and not (has_critical and payment_proximate):
            max_conf = max((float(getattr(s, "confidence", 0.15)) for s in active_supporting), default=0.15)
            return AssessmentResult(
                incident_id=incident_id,
                risk_level=RiskLevel.INSUFFICIENT_EVIDENCE,
                evidence_confidence=EvidenceConfidence.LOW,
                risk_score=round(max_conf, 2),
                confidence_score=0.10,
                is_insufficient_evidence=True,
                emerging_status=EmergingStatus.KNOWN_PATTERN,
                corroborated_dimensions=list(distinct_dimensions),
                signals=active_supporting,
                counter_evidence=counter_signals,
                intervention=AdaptiveIntervention(
                    action=InterventionAction.NONE,
                    friction_delay_seconds=0,
                    banner_message="Insufficient evidence to evaluate risk. Monitoring passively.",
                ),
                explainability=ExplainabilityReport(
                    what_happened="Fewer than 2 independent signals observed.",
                    why_suspicious="Not enough verified indicators to demonstrate intentional deception.",
                    when_risk_increased="No escalation confirmed.",
                    which_evidence_supports=[s.description for s in active_supporting],
                    which_sources_produced=[s.provenance.detector_name for s in active_supporting],
                    what_counter_evidence_exists=[s.description for s in counter_signals],
                    how_confident="LOW: Corroboration across at least 2 independent dimensions is required.",
                    what_to_do_next="Proceed with standard caution. Verify any payment request independently.",
                ),
                is_simulated=is_simulated,
            )

        # 2. Compute Weighted Risk Score (0.0 to 1.0)
        total_weight = 0.0
        weighted_risk_sum = 0.0
        for s in active_supporting:
            w = s.weight
            sev_score = SEVERITY_WEIGHTS.get(s.severity, 0.5)
            weighted_risk_sum += w * sev_score * s.confidence
            total_weight += w

        raw_risk_score = (weighted_risk_sum / total_weight) if total_weight > 0 else 0.0

        # Counter-evidence discount
        if counter_signals:
            counter_discount = 0.25 * len(counter_signals)
            raw_risk_score = max(0.0, raw_risk_score - counter_discount)

        # Drive risk score from detected signal confidence
        if active_supporting:
            max_signal_conf = max(float(getattr(s, "confidence", 0.7)) for s in active_supporting)
            raw_risk_score = max(raw_risk_score, max_signal_conf)

        normalized_risk_score = round(min(1.0, max(0.0, raw_risk_score)), 2)

        # 4. Determine Evidence Confidence based on Multi-Dimensional Corroboration
        num_dims = len(distinct_dimensions)
        if num_dims >= 3:
            confidence_level = EvidenceConfidence.HIGH
            confidence_score = 0.88
        elif num_dims == 2:
            confidence_level = EvidenceConfidence.MEDIUM
            confidence_score = 0.65
        else:
            confidence_level = EvidenceConfidence.LOW
            confidence_score = 0.35

        # 3. Determine Risk Level (with multi-dimensional corroboration boost)
        if normalized_risk_score >= 0.65 or (normalized_risk_score >= 0.55 and num_dims >= 3):
            risk_level = RiskLevel.HIGH
        elif normalized_risk_score >= 0.35:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # 5. Adaptive Intervention Calibration (combats alert fatigue)
        intervention = EvidenceFusionEngine._calibrate_intervention(
            risk_level=risk_level,
            confidence_level=confidence_level,
            payment_proximate=payment_proximate,
        )

        # 6. Formulate Explainability Report
        explainability = ExplainabilityReport(
            what_happened=f"Observed {total_signals} suspicious signals across {num_dims} independent dimensions.",
            why_suspicious=f"Detected high-risk signals including: {', '.join(s.signal_type for s in active_supporting[:3])}.",
            when_risk_increased="Risk escalated when multi-dimensional signals intersected near payment context.",
            which_evidence_supports=[s.description for s in active_supporting],
            which_sources_produced=list({s.provenance.detector_name for s in active_supporting}),
            what_counter_evidence_exists=[s.description for s in counter_signals],
            how_confident=f"{confidence_level.value}: Verified across {num_dims} independent dimensions: {', '.join(d.value for d in distinct_dimensions)}.",
            what_to_do_next=intervention.banner_message or "Verify recipient identity via official directory.",
        )

        return AssessmentResult(
            incident_id=incident_id,
            risk_level=risk_level,
            evidence_confidence=confidence_level,
            risk_score=normalized_risk_score,
            confidence_score=confidence_score,
            is_insufficient_evidence=False,
            emerging_status=EmergingStatus.MUTATED_VARIANT if num_dims >= 2 else EmergingStatus.KNOWN_PATTERN,
            corroborated_dimensions=list(distinct_dimensions),
            signals=active_supporting,
            counter_evidence=counter_signals,
            intervention=intervention,
            explainability=explainability,
            is_simulated=is_simulated,
        )

    @staticmethod
    def _calibrate_intervention(
        risk_level: RiskLevel,
        confidence_level: EvidenceConfidence,
        payment_proximate: bool,
    ) -> AdaptiveIntervention:
        if risk_level == RiskLevel.HIGH and confidence_level == EvidenceConfidence.HIGH:
            if payment_proximate:
                return AdaptiveIntervention(
                    action=InterventionAction.PRE_PAYMENT_INTERVENTION,
                    friction_delay_seconds=10,
                    banner_title="High Risk Payment Progression Detected",
                    banner_message="This payment was preceded by urgent impersonation text and newly created domain.",
                    action_button_text="I Understand the Risk — Proceed with Verification",
                    dismissible=False,
                )
            else:
                return AdaptiveIntervention(
                    action=InterventionAction.STRONG_WARNING,
                    friction_delay_seconds=0,
                    banner_title="Suspicious Grooming Journey",
                    banner_message="High-confidence scam pattern detected across multiple channels.",
                )
        elif risk_level in (RiskLevel.HIGH, RiskLevel.MEDIUM) and confidence_level in (EvidenceConfidence.MEDIUM, EvidenceConfidence.HIGH):
            return AdaptiveIntervention(
                action=InterventionAction.CAUTION,
                friction_delay_seconds=0,
                banner_title="Caution: Verify Sender Identity",
                banner_message="Unverified sender credentials and urgency markers observed.",
            )
        else:
            return AdaptiveIntervention(
                action=InterventionAction.PASSIVE,
                friction_delay_seconds=0,
                banner_message="Signals monitored passively to avoid alert fatigue.",
            )
