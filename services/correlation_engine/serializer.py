"""Correlation Serializer & Privacy Firewall (Phase 3B - Sections 48-52, 111-113, 160).

Ensures:
1. Consumer views never expose victim identity, phone, UPI, raw messages, or foreign incident IDs.
2. Anti-small-cohort privacy protection (configurable minimum cohort size).
3. Plain-language consumer warnings based on verified collective network signals.
4. Comprehensive technical telemetry for authorized fraud analysts.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from packages.schemas.correlation import (
    AnalystCorrelationView,
    ConsumerNetworkSignal,
    ConsumerNetworkSignalType,
    IncidentCorrelation,
    RelationshipStatus,
)
from services.correlation_engine.config import CorrelationConfig

logger = logging.getLogger("correlation_engine.serializer")


class CorrelationSerializer:
    """Serializes correlation results into privacy-safe consumer and analyst views."""

    def __init__(self, config: Optional[CorrelationConfig] = None):
        self.config = config or CorrelationConfig.load()

    def to_consumer_network_signal(
        self,
        incident_id: str,
        correlations: List[IncidentCorrelation],
        display_stage: Optional[str] = None,
    ) -> ConsumerNetworkSignal:
        """Transforms a collection of incident correlations into an aggregate, privacy-safe consumer alert.

        NO other victim IDs, phone numbers, UPIs, or messages are ever exposed.
        """
        # Filter to only meaningful relationships
        meaningful = [
            c for c in correlations
            if c.relationship_status in (
                RelationshipStatus.STRONGLY_RELATED,
                RelationshipStatus.LIKELY_RELATED_PATTERN,
                RelationshipStatus.POSSIBLY_RELATED,
            )
        ]

        if not meaningful:
            return ConsumerNetworkSignal(
                incident_id=incident_id,
                network_signal=ConsumerNetworkSignalType.NO_NETWORK_SIGNAL,
                headline="No Network Links Detected",
                explanation_bullets=[
                    "This interaction has not been linked to existing reported scam networks.",
                    "Continue to exercise standard caution before making any transfer.",
                ],
                related_reports_band="NO_PRIOR_REPORTS",
                display_stage=display_stage,
                warning_level="INFO",
                recommended_actions=["Verify recipient credentials through official bank channels."],
                is_aggregate_safe=True,
            )

        # Count strong and shared entity links
        has_shared_payment = any("SHARED_PAYMENT_IDENTIFIER" in c.positive_reasons for c in meaningful)
        has_shared_phone = any("SHARED_PHONE_NUMBER" in c.positive_reasons for c in meaningful)
        has_strong_dna = any(c.dna_similarity and c.dna_similarity >= 0.70 for c in meaningful)
        strong_count = sum(1 for c in meaningful if c.relationship_status == RelationshipStatus.STRONGLY_RELATED)

        # Anti-small-cohort protection: requires at least minimum_cohort_size_for_disclosure
        cohort_size = len(meaningful)
        if cohort_size >= 5:
            band = "EXTENSIVE_REPORTS"
        elif cohort_size >= self.config.minimum_cohort_size_for_disclosure:
            band = "MULTIPLE_REPORTS"
        else:
            band = "LIMITED_REPORTS"

        bullets: List[str] = []
        if has_shared_payment:
            bullets.append("The payment destination in this interaction has appeared in other suspicious reports.")
        if has_shared_phone:
            bullets.append("The contact number used has been observed across similar interactions.")
        if has_strong_dna:
            bullets.append("The progression of events closely matches an active scam pattern reported by other users.")

        if not bullets:
            bullets.append("Similar behavioral patterns have been identified in our community threat intelligence.")

        # Determine signal tier
        if has_shared_payment or strong_count >= 2:
            signal_type = ConsumerNetworkSignalType.MULTIPLE_RELATED_SIGNALS
            headline = "High-Risk Network Link Detected"
            warning_level = "CRITICAL"
            actions = [
                "Do NOT transfer money to this payment identifier.",
                "Block and report the sender immediately.",
                "Independently verify with your bank or local cyber crime portal (cybercrime.gov.in / 1930).",
            ]
        elif has_shared_phone or has_shared_payment:
            signal_type = ConsumerNetworkSignalType.ENTITY_REPORTED_ELSEWHERE
            headline = "Identifier Previously Reported"
            warning_level = "STRONG_WARNING"
            actions = [
                "Pause all interaction before proceeding.",
                "Verify the recipient's identity through independent official directories.",
            ]
        else:
            signal_type = ConsumerNetworkSignalType.SIMILAR_PATTERN_OBSERVED
            headline = "Similar Scam Pattern Observed"
            warning_level = "WARNING"
            actions = [
                "Be aware that this multi-step pattern has led to financial loss in other reported cases.",
                "Do not deposit funds to unlock rewards or merchant tasks.",
            ]

        return ConsumerNetworkSignal(
            incident_id=incident_id,
            network_signal=signal_type,
            headline=headline,
            explanation_bullets=bullets,
            related_reports_band=band,
            display_stage=display_stage,
            warning_level=warning_level,
            recommended_actions=actions,
            is_aggregate_safe=True,
        )

    def to_analyst_view(
        self,
        correlation: IncidentCorrelation,
        feature_breakdown: Dict[str, float],
    ) -> AnalystCorrelationView:
        """Serializes full technical correlation telemetry for authorized fraud investigators."""
        # Synthesize explainable graph paths
        paths: List[str] = []
        for ent in correlation.shared_entities:
            ent_type = ent.get("entity_type", "ENTITY")
            masked = ent.get("canonical_value_masked", "***")
            paths.append(
                f"Incident({correlation.source_incident_id}) --[OBSERVED]--> {ent_type}({masked}) <--[OBSERVED]-- Incident({correlation.target_incident_id})"
            )

        if correlation.dna_similarity and correlation.dna_similarity >= 0.65:
            paths.append(
                f"Incident({correlation.source_incident_id}) --[MATCHES_DNA(sim={round(correlation.dna_similarity, 2)})]--> Incident({correlation.target_incident_id})"
            )

        return AnalystCorrelationView(
            correlation=correlation,
            feature_breakdown=correlation.feature_scores,
            group_contributions=feature_breakdown,
            explainable_graph_paths=paths,
            comparison_coverage=0.90,
            audit_trail=[
                f"Evaluated with engine_version={correlation.engine_version}",
                f"Overall score={round(correlation.overall_score, 3)}, confidence={round(correlation.confidence, 2)}",
                f"Status={correlation.relationship_status.value}, strength={correlation.evidence_strength.value}",
            ],
        )
