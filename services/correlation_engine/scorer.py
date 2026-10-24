"""Correlation Scorer & Relationship Classifier (Phase 3B - Sections 37-43, 81-86).

Implements interpretable, rule-gated scoring:
1. Feature group weighting (Entity, Behavioral, Infrastructure, Temporal, Graph)
2. Group score capping to prevent double counting
3. Hard positive gates (Rare UPI + Strong DNA -> STRONGLY_RELATED)
4. Hard negative gates (Generic brands alone -> NOT_RELATED, CDNs alone -> NOT_RELATED)
5. Contradiction penalties and separate confidence evaluation
6. Zero criminal attribution boundary (Never outputs SAME_CRIMINAL)
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple
from packages.schemas.correlation import (
    CorrelationFeatures,
    EvidenceStrength,
    RelationshipEvidenceType,
    RelationshipStatus,
)
from services.correlation_engine.config import CorrelationConfig

logger = logging.getLogger("correlation_engine.scorer")


class CorrelationScorer:
    """Computes explainable correlation scores and relationship classifications."""

    def __init__(self, config: Optional[CorrelationConfig] = None):
        self.config = config or CorrelationConfig.load()

    def score_pair(
        self,
        features: CorrelationFeatures,
        positive_reasons: List[str],
        contradictions: List[str],
    ) -> Tuple[float, float, RelationshipStatus, EvidenceStrength, Dict[str, float], List[str]]:
        """Scores an incident pair and returns:

        (overall_score, confidence, relationship_status, evidence_strength, feature_breakdown, negative_reasons)
        """
        feature_breakdown: Dict[str, float] = {}
        negative_reasons: List[str] = []

        # ---------------------------------------------------------------------
        # Hard Negative Gate 1: Generic brand / platform super-node alone
        # ---------------------------------------------------------------------
        if features.shared_rare_entity_count == 0 and features.shared_common_entity_count > 0:
            if features.dna_similarity < 0.50 and features.journey_similarity < 0.50:
                negative_reasons.append("ONLY_GENERIC_SUPER_NODES_SHARED(SBI/TELEGRAM/WHATSAPP)")
                return (
                    0.0,
                    0.80,
                    RelationshipStatus.NOT_RELATED,
                    EvidenceStrength.WEAK,
                    {"super_node_suppression": 0.0},
                    negative_reasons,
                )

        # ---------------------------------------------------------------------
        # Hard Negative Gate 2: Shared common CDN / hosting alone
        # ---------------------------------------------------------------------
        if features.shared_rare_entity_count == 0 and features.infrastructure_similarity == 0.0 and features.dna_similarity < 0.40:
            negative_reasons.append("NO_SPECIFIC_ENTITY_OR_INFRASTRUCTURE_LINK")
            return (
                0.0,
                0.70,
                RelationshipStatus.NOT_RELATED,
                EvidenceStrength.WEAK,
                {"no_link_suppression": 0.0},
                negative_reasons,
            )

        # ---------------------------------------------------------------------
        # Group 1: Entity Evidence Group (Cap = 0.45, Weight = 0.35)
        # ---------------------------------------------------------------------
        raw_entity_score = (
            (0.50 * features.exact_payment_overlap)
            + (0.25 * features.exact_phone_overlap)
            + (0.15 * features.exact_domain_overlap)
            + (0.10 * features.exact_social_overlap)
        )
        if features.weighted_entity_overlap > 0:
            raw_entity_score = max(raw_entity_score, features.weighted_entity_overlap)
        capped_entity_score = min(self.config.group_score_caps["entity"], raw_entity_score * self.config.group_weights["entity_weight"] * (1.0 / 0.35))
        feature_breakdown["entity_contribution"] = round(capped_entity_score, 3)

        # ---------------------------------------------------------------------
        # Group 2: Behavioral Evidence Group (Cap = 0.35, Weight = 0.30)
        # Prevents double counting of Journey & Tactics inside ScamDNA
        # ---------------------------------------------------------------------
        raw_behavioral_score = max(
            features.dna_similarity,
            (0.60 * features.journey_similarity) + (0.40 * features.tactic_similarity),
        )
        capped_behavioral_score = min(self.config.group_score_caps["behavioral"], raw_behavioral_score * self.config.group_weights["behavioral_weight"] * (1.0 / 0.30))
        feature_breakdown["behavioral_contribution"] = round(capped_behavioral_score, 3)

        # ---------------------------------------------------------------------
        # Group 3: Infrastructure Evidence Group (Cap = 0.20, Weight = 0.15)
        # ---------------------------------------------------------------------
        raw_infra_score = features.infrastructure_similarity
        capped_infra_score = min(self.config.group_score_caps["infrastructure"], raw_infra_score * self.config.group_weights["infrastructure_weight"] * (1.0 / 0.15))
        feature_breakdown["infrastructure_contribution"] = round(capped_infra_score, 3)

        # ---------------------------------------------------------------------
        # Group 4: Temporal Evidence Group (Cap = 0.15, Weight = 0.10)
        # ---------------------------------------------------------------------
        raw_temporal_score = features.temporal_similarity
        capped_temporal_score = min(self.config.group_score_caps["temporal"], raw_temporal_score * self.config.group_weights["temporal_weight"] * (1.0 / 0.10))
        feature_breakdown["temporal_contribution"] = round(capped_temporal_score, 3)

        # ---------------------------------------------------------------------
        # Group 5: Graph Path Group (Cap = 0.15, Weight = 0.10)
        # ---------------------------------------------------------------------
        raw_graph_score = features.graph_path_score
        capped_graph_score = min(self.config.group_score_caps["graph"], raw_graph_score * self.config.group_weights["graph_weight"] * (1.0 / 0.10))
        feature_breakdown["graph_contribution"] = round(capped_graph_score, 3)

        # ---------------------------------------------------------------------
        # Composite Score Calculation
        # ---------------------------------------------------------------------
        composite_score = (
            capped_entity_score
            + capped_behavioral_score
            + capped_infra_score
            + capped_temporal_score
            + capped_graph_score
        )

        # Scale composite if strong multi-signal alignment occurs (Section 83)
        independent_signals = 0
        if capped_entity_score >= 0.20:
            independent_signals += 1
        if capped_behavioral_score >= 0.20:
            independent_signals += 1
        if capped_infra_score >= 0.10:
            independent_signals += 1
        if capped_temporal_score >= 0.08:
            independent_signals += 1

        if independent_signals >= 3:
            composite_score = min(1.0, composite_score * 1.15)

        # ---------------------------------------------------------------------
        # Contradiction Penalty Application (Section 42, 97)
        # ---------------------------------------------------------------------
        if contradictions:
            penalty = min(0.65, len(contradictions) * self.config.contradiction_penalty_factor)
            composite_score = max(0.0, composite_score * (1.0 - penalty))
            feature_breakdown["contradiction_penalty"] = -round(penalty, 3)
            negative_reasons.extend(contradictions)

        composite_score = round(min(1.0, max(0.0, composite_score)), 3)

        # ---------------------------------------------------------------------
        # Confidence & Evidence Strength
        # ---------------------------------------------------------------------
        # Confidence reflects independent evidence classes and absence of contradictions
        base_conf = 0.40 + (independent_signals * 0.15)
        if contradictions:
            base_conf = max(0.20, base_conf - 0.25)
        confidence = round(min(0.95, base_conf), 2)

        if composite_score >= 0.75 and independent_signals >= 2:
            strength = EvidenceStrength.VERY_STRONG
        elif composite_score >= 0.60:
            strength = EvidenceStrength.STRONG
        elif composite_score >= 0.40:
            strength = EvidenceStrength.MODERATE
        else:
            strength = EvidenceStrength.WEAK

        # ---------------------------------------------------------------------
        # Hard Positive & Relationship Status Classification
        # ---------------------------------------------------------------------
        # Condition A: Specific rare payment identifier + behavioral match -> STRONGLY_RELATED
        if features.exact_payment_overlap == 1.0 and (features.dna_similarity >= 0.60 or features.journey_similarity >= 0.60) and not contradictions:
            composite_score = max(composite_score, 0.85)
            confidence = max(confidence, 0.90)
            status = RelationshipStatus.STRONGLY_RELATED
            strength = EvidenceStrength.VERY_STRONG
        # Condition B: Identifier rotation (all IDs altered, strong DNA match) -> POSSIBLY_RELATED
        elif (
            features.shared_rare_entity_count == 0
            and features.dna_similarity >= 0.65
            and not contradictions
        ):
            composite_score = max(0.50, min(0.64, composite_score))
            confidence = 0.65  # Moderate confidence because no entity links exist
            status = RelationshipStatus.POSSIBLY_RELATED
            strength = EvidenceStrength.MODERATE
        # Condition C: Threshold-based classification
        elif composite_score >= self.config.strongly_related_threshold:
            status = RelationshipStatus.STRONGLY_RELATED
        elif composite_score >= self.config.likely_related_threshold:
            status = RelationshipStatus.LIKELY_RELATED_PATTERN
        elif composite_score >= self.config.possibly_related_threshold:
            status = RelationshipStatus.POSSIBLY_RELATED
        elif composite_score >= self.config.weak_signal_threshold:
            status = RelationshipStatus.WEAK_SIGNAL
        else:
            status = RelationshipStatus.NOT_RELATED

        return composite_score, confidence, status, strength, feature_breakdown, negative_reasons
