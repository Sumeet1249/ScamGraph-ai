"""Consumer and Analyst Serialization for Tactic Intelligence in ScamGraph AI V2.

Provides plain-language, privacy-safe explanations for everyday consumers,
and rich, evidence-grounded forensic timelines for fraud analysts.
"""

from typing import Any, Dict, List, Set
from packages.schemas.tactics import (
    ConsumerTacticWarning,
    TacticSignal,
    TacticTimeline,
    TacticType,
)
from ml.tactics.ontology import CONSUMER_TACTIC_NAMES


class TacticSerializer:
    """Serializes tactic timelines for consumer and analyst consumption."""

    @staticmethod
    def serialize_consumer_warning(timeline: TacticTimeline) -> ConsumerTacticWarning:
        """Produces a clean, human-readable consumer warning without technical internals."""
        active_signals = [s for s in timeline.signals if not s.is_negated and not s.is_quoted]
        
        if not active_signals:
            return ConsumerTacticWarning(
                title="No Coercive Manipulation Detected",
                summary="This message does not appear to use high-pressure scam tactics.",
                detected_tactics=[],
                recommended_interventions=["Stay alert for unexpected payment or credential requests."],
            )

        # Unique consumer-friendly tactic names
        detected_names: List[str] = []
        seen_tactics: Set[TacticType] = set()
        for sig in active_signals:
            if sig.tactic not in seen_tactics:
                seen_tactics.add(sig.tactic)
                name = CONSUMER_TACTIC_NAMES.get(sig.tactic, sig.tactic.value.replace("_", " ").title())
                detected_names.append(name)

        # Human summary construction
        summary_clauses: List[str] = []
        if TacticType.AUTHORITY in seen_tactics or TacticType.IMPERSONATION in seen_tactics:
            summary_clauses.append("the sender claims official authority or impersonates a reputable organization")
        if TacticType.SECRECY in seen_tactics or TacticType.ISOLATION in seen_tactics:
            summary_clauses.append("asks you to keep the situation secret and not consult family or bank officials")
        if TacticType.URGENCY in seen_tactics or TacticType.FEAR in seen_tactics:
            summary_clauses.append("uses strict deadlines or threats of arrest and account blockage")
        if TacticType.PAYMENT_PRESSURE in seen_tactics:
            summary_clauses.append("pressures you to transfer money or approve payments immediately")
        if TacticType.CREDENTIAL_PRESSURE in seen_tactics:
            summary_clauses.append("demands confidential OTP or banking credentials")
        if TacticType.REMOTE_ACCESS_PRESSURE in seen_tactics:
            summary_clauses.append("urges you to install remote support apps or share your screen")
        if TacticType.PLATFORM_MIGRATION in seen_tactics:
            summary_clauses.append("attempts to move you to private messaging platforms like Telegram")

        if summary_clauses:
            joined = "; ".join(summary_clauses)
            summary = f"This communication uses high-pressure tactics commonly seen in scams: {joined}."
        else:
            summary = "This communication uses coercive patterns designed to pressure you into acting without thinking."

        # Actionable recommendations
        recommendations: List[str] = []
        if TacticType.CREDENTIAL_PRESSURE in seen_tactics:
            recommendations.append("DO NOT share OTP, PIN, or passwords with anyone.")
        if TacticType.PAYMENT_PRESSURE in seen_tactics:
            recommendations.append("PAUSE before making any payment or approving UPI collect requests.")
        if TacticType.REMOTE_ACCESS_PRESSURE in seen_tactics:
            recommendations.append("DO NOT install AnyDesk, QuickSupport, or share your screen.")
        if TacticType.ISOLATION in seen_tactics or TacticType.SECRECY in seen_tactics:
            recommendations.append("TALK to a trusted family member or visit your local bank branch directly.")
        if TacticType.AUTHORITY in seen_tactics or TacticType.IMPERSONATION in seen_tactics:
            recommendations.append("VERIFY INDEPENDENTLY using official contact numbers, never the caller's instructions.")

        if not recommendations:
            recommendations.append("Verify all sender claims independently before proceeding.")

        return ConsumerTacticWarning(
            title="High-Risk Manipulation Pattern Detected",
            summary=summary,
            detected_tactics=detected_names,
            recommended_interventions=recommendations,
        )

    @staticmethod
    def serialize_analyst_view(timeline: TacticTimeline) -> Dict[str, Any]:
        """Produces comprehensive forensic timeline for fraud analysts."""
        signals_data = []
        for s in timeline.signals:
            signals_data.append({
                "signal_id": s.signal_id,
                "tactic": s.tactic.value,
                "confidence": s.confidence,
                "severity": s.severity,
                "turn_index": s.turn_index,
                "detector_sources": s.detector_sources,
                "is_negated": s.is_negated,
                "is_quoted": s.is_quoted,
                "supporting_spans": [
                    {
                        "start": sp.start,
                        "end": sp.end,
                        "text": sp.text,
                        "text_hash": sp.text_hash,
                        "confidence": sp.confidence,
                    }
                    for sp in s.supporting_spans
                ],
                "requested_actions": [a.value for a in s.requested_actions],
                "related_entities": s.related_entities,
                "metadata": s.metadata,
            })

        return {
            "timeline_id": timeline.timeline_id,
            "conversation_id": timeline.conversation_id,
            "incident_id": timeline.incident_id,
            "signal_count": len(timeline.signals),
            "signals": signals_data,
            "tactic_vector": timeline.tactic_vector,
            "manipulation_density": timeline.manipulation_density,
            "escalation_signal": timeline.escalation_signal,
            "escalation_description": timeline.escalation_description,
            "intervention_candidates": timeline.intervention_candidates,
        }
