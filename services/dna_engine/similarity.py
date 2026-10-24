"""ScamDNA V3 Similarity Engine.

Computes explainable multi-dimensional similarity between two ScamDNA instances.
Implements dimension-specific similarity algorithms, missing-dimension re-normalization,
family-specific weight overrides, contradiction penalization, and variant classification.
"""

from __future__ import annotations

import difflib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

import numpy as np
import yaml

from packages.schemas.dna import (
    DNADimension,
    DNADimensionType,
    ScamDNA,
    ScamDNAMatch,
    VariantStatus,
)

logger = logging.getLogger("dna_engine.similarity")

CONFIG_PATH = Path("config/scam_dna.yaml")


def load_dna_config() -> Dict[str, Any]:
    """Loads weights and thresholds from config/scam_dna.yaml."""
    paths_to_try = [
        CONFIG_PATH,
        Path(__file__).resolve().parent.parent.parent / "config" / "scam_dna.yaml",
    ]
    for p in paths_to_try:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        return data
            except Exception as e:
                logger.warning(f"Error loading {p}: {e}")

    # Sensible fallbacks
    return {
        "weights": {
            "journey_weight": 0.25,
            "tactic_weight": 0.20,
            "semantic_weight": 0.15,
            "payment_weight": 0.15,
            "identity_weight": 0.10,
            "infrastructure_weight": 0.05,
            "temporal_weight": 0.05,
            "graph_weight": 0.05,
        },
        "thresholds": {
            "known_pattern_threshold": 0.80,
            "likely_variant_threshold": 0.65,
            "possible_variant_threshold": 0.50,
            "novel_pattern_threshold": 0.38,
            "early_match_threshold": 0.55,
            "minimum_dimensions_for_confident_match": 3,
            "contradiction_penalty_factor": 0.30,
        },
        "tactic_informativeness": {
            "AUTHORITY": 1.4,
            "ISOLATION": 1.8,
            "SECRECY": 1.6,
            "THREAT": 1.5,
            "FAKE_REWARD": 1.5,
            "WITHDRAWAL_BLOCK": 1.6,
            "PAYMENT_PRESSURE": 1.3,
            "URGENCY": 0.8,
        },
    }


class ScamDNASimilarityEngine:
    """Computes multi-dimensional behavioral alignment and variant classification."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or load_dna_config()
        self.weights = self.config.get("weights", {})
        self.family_weights = self.config.get("family_weights", {})
        self.thresholds = self.config.get("thresholds", {})
        self.tactic_info = self.config.get("tactic_informativeness", {})

    # -------------------------------------------------------------------------
    # Dimension 1: Semantic Similarity
    # -------------------------------------------------------------------------
    def compare_semantic(self, d1: DNADimension, d2: DNADimension) -> Tuple[float, List[str]]:
        reasons = []
        scores = []

        # Vector cosine
        v1 = d1.vector_embedding
        v2 = d2.vector_embedding
        if v1 and v2:
            arr1 = np.array(v1, dtype=np.float32)
            arr2 = np.array(v2, dtype=np.float32)
            n1 = np.linalg.norm(arr1)
            n2 = np.linalg.norm(arr2)
            if n1 > 0 and n2 > 0:
                cos = float(np.dot(arr1, arr2) / (n1 * n2))
                cos_sim = max(0.0, min(1.0, cos))
                scores.append(cos_sim)
                if cos_sim >= 0.70:
                    reasons.append("HIGH_SEMANTIC_EMBEDDING_ALIGNMENT")

        # Requested actions overlap
        act1 = set(d1.features.get("requested_actions", []))
        act2 = set(d2.features.get("requested_actions", []))
        if act1 or act2:
            act_sim = len(act1.intersection(act2)) / len(act1.union(act2)) if (act1 and act2) else 0.0
            scores.append(act_sim)
            if act_sim >= 0.60:
                reasons.append(f"SHARED_REQUESTED_ACTIONS({', '.join(act1.intersection(act2))})")

        if not scores:
            return 0.5, ["INSUFFICIENT_SEMANTIC_DATA"]

        return round(float(np.mean(scores)), 3), reasons

    # -------------------------------------------------------------------------
    # Dimension 2: Journey Progression Similarity (Sequence Alignment)
    # -------------------------------------------------------------------------
    def compare_journey(self, d1: DNADimension, d2: DNADimension) -> Tuple[float, List[str]]:
        reasons = []
        seq1 = d1.features.get("stage_sequence", [])
        seq2 = d2.features.get("stage_sequence", [])

        if not seq1 or not seq2:
            return 0.0, ["EMPTY_JOURNEY_STAGES"]

        # Ordered subsequence alignment ratio via difflib SequenceMatcher
        matcher = difflib.SequenceMatcher(None, seq1, seq2)
        seq_ratio = matcher.ratio()

        # Check prefix relationship (Section 88: Partial Journey Prefix)
        is_prefix = False
        if len(seq1) >= 2 and len(seq2) >= 2:
            shorter, longer = (seq1, seq2) if len(seq1) <= len(seq2) else (seq2, seq1)
            if longer[:len(shorter)] == shorter:
                is_prefix = True

        # Monetization boundary alignment
        b1 = d1.features.get("monetization_boundary_crossed", False)
        b2 = d2.features.get("monetization_boundary_crossed", False)
        if b1 == b2:
            boundary_match = 1.0
        elif is_prefix:
            boundary_match = 0.8
        else:
            boundary_match = 0.0

        # Current stage proximity
        curr1 = d1.features.get("current_stage")
        curr2 = d2.features.get("current_stage")
        if curr1 == curr2:
            curr_match = 1.0 if (b1 == b2 or is_prefix) else 0.3
        elif is_prefix:
            curr_match = 0.8
        else:
            curr_match = 0.0 if (b1 != b2) else 0.4

        composite = (0.60 * seq_ratio) + (0.25 * boundary_match) + (0.15 * curr_match)
        if is_prefix:
            reasons.append("EARLY_JOURNEY_PREFIX_ALIGNED")
        if seq_ratio >= 0.70:
            reasons.append(f"SIMILAR_JOURNEY_SEQUENCE(ratio={round(seq_ratio, 2)})")
        if curr1 and curr1 == curr2:
            reasons.append(f"IDENTICAL_CURRENT_STAGE({curr1})")

        return round(min(1.0, composite), 3), reasons

    # -------------------------------------------------------------------------
    # Dimension 3: Tactic Intelligence Similarity (Informativeness-Weighted)
    # -------------------------------------------------------------------------
    def compare_tactic(self, d1: DNADimension, d2: DNADimension) -> Tuple[float, List[str]]:
        reasons = []
        t1 = set(d1.features.get("tactics", []))
        t2 = set(d2.features.get("tactics", []))

        if not t1 or not t2:
            return 0.0, ["EMPTY_TACTICS"]

        shared = t1.intersection(t2)
        all_t = t1.union(t2)

        # Weighted Jaccard using informativeness weights
        shared_weight = sum(self.tactic_info.get(tac, 1.0) for tac in shared)
        union_weight = sum(self.tactic_info.get(tac, 1.0) for tac in all_t)

        weighted_sim = shared_weight / max(0.01, union_weight)
        if shared:
            reasons.append(f"SHARED_TACTICS({', '.join(sorted(shared))})")
        if "ISOLATION" in shared or "AUTHORITY" in shared:
            reasons.append("HIGH_IMPACT_COERCION_TACTICS_ALIGNED")

        return round(min(1.0, weighted_sim), 3), reasons

    # -------------------------------------------------------------------------
    # Dimension 4: Infrastructure DNA Similarity
    # -------------------------------------------------------------------------
    def compare_infrastructure(self, d1: DNADimension, d2: DNADimension) -> Tuple[float, List[str]]:
        reasons = []
        c1 = d1.features.get("channels", [])
        c2 = d2.features.get("channels", [])

        if not c1 or not c2:
            return 0.5, ["DEFAULT_INFRA_MATCH"]

        # Sequence matcher over channel paths (e.g. INSTA > WA > TG > UPI)
        matcher = difflib.SequenceMatcher(None, c1, c2)
        channel_sim = matcher.ratio()

        if channel_sim >= 0.60:
            reasons.append(f"SHARED_CHANNEL_MIGRATION_PATTERN({d1.features.get('channel_progression')})")

        p_mig1 = d1.features.get("has_platform_migration", False)
        p_mig2 = d2.features.get("has_platform_migration", False)
        bonus = 0.20 if (p_mig1 and p_mig2) else 0.0

        return round(min(1.0, (0.80 * channel_sim) + bonus), 3), reasons

    # -------------------------------------------------------------------------
    # Dimension 5: Payment Behavior Similarity
    # -------------------------------------------------------------------------
    def compare_payment(self, d1: DNADimension, d2: DNADimension) -> Tuple[float, List[str]]:
        reasons = []
        p1 = d1.features.get("payment_progression", [])
        p2 = d2.features.get("payment_progression", [])

        if not p1 or not p2:
            return 0.5, ["NO_COMPARATIVE_PAYMENT_PROG"]

        # Exact progression comparison
        matcher = difflib.SequenceMatcher(None, p1, p2)
        prog_sim = matcher.ratio()

        # Fee after block match
        fab1 = d1.features.get("fee_after_block", False)
        fab2 = d2.features.get("fee_after_block", False)
        fab_match = 1.0 if fab1 == fab2 else 0.5

        composite = (0.75 * prog_sim) + (0.25 * fab_match)
        if prog_sim >= 0.70:
            reasons.append(f"SIMILAR_PAYMENT_ESCALATION({d1.features.get('progression_signature')})")
        if fab1 and fab2:
            reasons.append("IDENTICAL_WITHDRAWAL_BLOCK_EXTORTION")

        return round(min(1.0, composite), 3), reasons

    # -------------------------------------------------------------------------
    # Dimension 6: Identity DNA Similarity
    # -------------------------------------------------------------------------
    def compare_identity(self, d1: DNADimension, d2: DNADimension) -> Tuple[float, List[str]]:
        reasons = []
        cat1 = d1.features.get("impersonated_category", "NONE")
        cat2 = d2.features.get("impersonated_category", "NONE")

        if cat1 == "NONE" and cat2 == "NONE":
            return 0.5, ["NO_PURPORTED_IDENTITY"]

        if cat1 == cat2 and cat1 != "NONE":
            reasons.append(f"SHARED_IMPERSONATION_CATEGORY({cat1})")
            return 0.90, reasons
        else:
            return 0.20, ["DIVERGENT_IMPERSONATED_ENTITY_CLASS"]

    # -------------------------------------------------------------------------
    # Dimension 7: Temporal DNA Similarity
    # -------------------------------------------------------------------------
    def compare_temporal(self, d1: DNADimension, d2: DNADimension) -> Tuple[float, List[str]]:
        reasons = []
        pace1 = d1.features.get("temporal_pace", "UNKNOWN")
        pace2 = d2.features.get("temporal_pace", "UNKNOWN")

        pace_score = 1.0 if pace1 == pace2 else 0.4
        if pace1 == pace2:
            reasons.append(f"ALIGNED_TEMPORAL_PACE({pace1})")

        acc1 = d1.features.get("accelerating_pressure", False)
        acc2 = d2.features.get("accelerating_pressure", False)
        acc_score = 1.0 if acc1 == acc2 else 0.5

        return round((0.60 * pace_score) + (0.40 * acc_score), 3), reasons

    # -------------------------------------------------------------------------
    # Dimension 8: Graph DNA Similarity
    # -------------------------------------------------------------------------
    def compare_graph(self, d1: DNADimension, d2: DNADimension) -> Tuple[float, List[str]]:
        reasons = []
        tier1 = d1.features.get("degree_centrality_tier", "LOW")
        tier2 = d2.features.get("degree_centrality_tier", "LOW")

        sim = 1.0 if tier1 == tier2 else 0.5
        if tier1 == tier2:
            reasons.append(f"SIMILAR_GRAPH_TOPOLOGY({tier1})")

        return round(sim, 3), reasons

    # -------------------------------------------------------------------------
    # Master Multi-Dimensional DNA Comparison
    # -------------------------------------------------------------------------
    def compare(self, dna1: ScamDNA, dna2: ScamDNA) -> ScamDNAMatch:
        """Compares two ScamDNA instances across all available dimensions with re-normalization."""
        dimension_scores: Dict[str, float] = {}
        all_reasons: List[str] = []
        matched_features: List[str] = []
        contradictions: List[str] = []

        # Find mutually available dimensions
        available_in_both = [
            dim for dim in DNADimensionType
            if dna1.get_dimension(dim) and dna2.get_dimension(dim)
        ]
        missing_in_either = [
            dim.value for dim in DNADimensionType
            if not (dna1.get_dimension(dim) and dna2.get_dimension(dim))
        ]

        if not available_in_both:
            return ScamDNAMatch(
                source_dna_id=dna1.dna_id,
                target_dna_id=dna2.dna_id,
                overall_similarity=0.0,
                match_confidence=0.0,
                variant_status=VariantStatus.INSUFFICIENT_EVIDENCE,
                explanation="No mutually available behavioral dimensions to compare.",
            )

        # Select weights: check if both share a primary family hypothesis
        top_fam1 = max(dna1.family_hypotheses.items(), key=lambda kv: kv[1])[0] if dna1.family_hypotheses else "UNKNOWN"
        top_fam2 = max(dna2.family_hypotheses.items(), key=lambda kv: kv[1])[0] if dna2.family_hypotheses else "UNKNOWN"
        
        active_weights_config = self.weights
        if top_fam1 == top_fam2 and top_fam1 in self.family_weights:
            active_weights_config = self.family_weights[top_fam1]

        # Calculate raw dimensional scores
        for dim in available_in_both:
            d1 = dna1.dimensions[dim.value]
            d2 = dna2.dimensions[dim.value]
            score, reasons = 0.0, []

            if dim == DNADimensionType.SEMANTIC:
                score, reasons = self.compare_semantic(d1, d2)
            elif dim == DNADimensionType.JOURNEY:
                score, reasons = self.compare_journey(d1, d2)
            elif dim == DNADimensionType.TACTIC:
                score, reasons = self.compare_tactic(d1, d2)
            elif dim == DNADimensionType.INFRASTRUCTURE:
                score, reasons = self.compare_infrastructure(d1, d2)
            elif dim == DNADimensionType.PAYMENT:
                score, reasons = self.compare_payment(d1, d2)
            elif dim == DNADimensionType.IDENTITY:
                score, reasons = self.compare_identity(d1, d2)
            elif dim == DNADimensionType.TEMPORAL:
                score, reasons = self.compare_temporal(d1, d2)
            elif dim == DNADimensionType.GRAPH:
                score, reasons = self.compare_graph(d1, d2)

            dimension_scores[dim.value] = score
            all_reasons.extend(reasons)
            if score >= 0.65:
                matched_features.append(f"{dim.value}({round(score, 2)})")

        # Contradiction Detection (Section 37, 97, 126)
        # Check if one is a partial pre-monetization prefix of the other (Section 88)
        j1_dim = dna1.dimensions.get(DNADimensionType.JOURNEY.value)
        j2_dim = dna2.dimensions.get(DNADimensionType.JOURNEY.value)
        j1_stages = j1_dim.features.get("stage_sequence", []) if (j1_dim and j1_dim.available) else []
        j2_stages = j2_dim.features.get("stage_sequence", []) if (j2_dim and j2_dim.available) else []
        is_partial_prefix = False
        if len(j1_stages) >= 2 and len(j2_stages) >= 2:
            shorter, longer = (j1_stages, j2_stages) if len(j1_stages) <= len(j2_stages) else (j2_stages, j1_stages)
            if longer[:len(shorter)] == shorter:
                is_partial_prefix = True

        # 1. Coercion tactics asymmetry (e.g. coercive threats/urgency vs benign advisory)
        t1_dim = dna1.dimensions.get(DNADimensionType.TACTIC.value)
        t2_dim = dna2.dimensions.get(DNADimensionType.TACTIC.value)
        t1_list = set(t1_dim.features.get("tactics", [])) if (t1_dim and t1_dim.available) else set()
        t2_list = set(t2_dim.features.get("tactics", [])) if (t2_dim and t2_dim.available) else set()
        coercion_tactics = {"AUTHORITY", "THREAT", "ISOLATION", "SECRECY", "FEAR", "CREDENTIAL_PRESSURE", "PAYMENT_PRESSURE"}
        t1_coercive = bool(t1_list.intersection(coercion_tactics))
        t2_coercive = bool(t2_list.intersection(coercion_tactics))
        if not is_partial_prefix and (t1_coercive != t2_coercive):
            contradictions.append("COERCION_TACTICS_ASYMMETRY")

        # 2. Identity class divergence or contradiction
        id_score = dimension_scores.get(DNADimensionType.IDENTITY.value)
        if id_score is not None and id_score <= 0.20:
            contradictions.append("DIVERGENT_IMPERSONATED_ENTITY_CLASS")

        # 3. Monetization / extraction boundary asymmetry
        b1 = j1_dim.features.get("monetization_boundary_crossed", False) if (j1_dim and j1_dim.available) else False
        b2 = j2_dim.features.get("monetization_boundary_crossed", False) if (j2_dim and j2_dim.available) else False
        if not is_partial_prefix and (b1 != b2):
            contradictions.append("MONETIZATION_BOUNDARY_ASYMMETRY")

        # 4. Sensitive action extraction asymmetry (e.g. demanding OTP/passwords vs benign)
        s1_dim = dna1.dimensions.get(DNADimensionType.SEMANTIC.value)
        s2_dim = dna2.dimensions.get(DNADimensionType.SEMANTIC.value)
        act1 = set(s1_dim.features.get("requested_actions", [])) if (s1_dim and s1_dim.available) else set()
        act2 = set(s2_dim.features.get("requested_actions", [])) if (s2_dim and s2_dim.available) else set()
        sensitive_actions = {"SUBMIT_OTP", "ENTER_NETBANKING_PASSWORD", "RECHARGE_ACCOUNT", "SEND_PAYMENT", "DEPOSIT_FUNDS", "TRANSFER_FUNDS"}
        if bool(act1.intersection(sensitive_actions)) != bool(act2.intersection(sensitive_actions)):
            contradictions.append("CREDENTIAL_PAYMENT_EXTRACTION_ASYMMETRY")

        # Re-normalize weights across ONLY the mutually available dimensions (Section 23)
        weight_key_map = {
            DNADimensionType.JOURNEY: "journey_weight",
            DNADimensionType.TACTIC: "tactic_weight",
            DNADimensionType.SEMANTIC: "semantic_weight",
            DNADimensionType.PAYMENT: "payment_weight",
            DNADimensionType.IDENTITY: "identity_weight",
            DNADimensionType.INFRASTRUCTURE: "infrastructure_weight",
            DNADimensionType.TEMPORAL: "temporal_weight",
            DNADimensionType.GRAPH: "graph_weight",
        }

        total_active_weight = sum(
            active_weights_config.get(weight_key_map[dim], 0.10)
            for dim in available_in_both
        )

        composite_similarity = 0.0
        if total_active_weight > 0:
            for dim in available_in_both:
                w = active_weights_config.get(weight_key_map[dim], 0.10) / total_active_weight
                composite_similarity += w * dimension_scores[dim.value]

        # Apply contradiction penalty if detected (Section 97)
        base_penalty = self.thresholds.get("contradiction_penalty_factor", 0.30)
        if contradictions:
            total_penalty = min(0.65, len(contradictions) * base_penalty)
            composite_similarity = max(0.0, composite_similarity * (1.0 - total_penalty))

        composite_similarity = round(composite_similarity, 3)

        # Match confidence is scaled by comparison coverage (dimensions available / 8)
        coverage_ratio = len(available_in_both) / 8.0
        avg_dim_confidence = float(np.mean([
            min(dna1.dimensions[dim.value].confidence, dna2.dimensions[dim.value].confidence)
            for dim in available_in_both
        ]))
        match_confidence = round(0.50 * coverage_ratio + 0.50 * avg_dim_confidence, 2)

        # Variant classification
        min_dims = self.thresholds.get("minimum_dimensions_for_confident_match", 3)
        if len(available_in_both) < min_dims:
            variant_status = VariantStatus.INSUFFICIENT_EVIDENCE
        elif composite_similarity >= self.thresholds.get("known_pattern_threshold", 0.80) and match_confidence >= 0.60:
            variant_status = VariantStatus.KNOWN_PATTERN
        elif composite_similarity >= self.thresholds.get("likely_variant_threshold", 0.65):
            variant_status = VariantStatus.LIKELY_VARIANT
        elif composite_similarity >= self.thresholds.get("possible_variant_threshold", 0.50):
            variant_status = VariantStatus.POSSIBLE_VARIANT
        else:
            variant_status = VariantStatus.NOVEL_PATTERN

        # Synthesize plain-language explanation
        explanation_lines = [
            f"Overall DNA similarity: {round(composite_similarity * 100, 1)}% ({variant_status.value}).",
            f"Compared across {len(available_in_both)}/8 dimensions: {', '.join([d.value for d in available_in_both])}.",
        ]
        if matched_features:
            explanation_lines.append(f"Strong alignment in: {', '.join(matched_features)}.")
        if contradictions:
            explanation_lines.append(f"Contradictions observed: {', '.join(contradictions)}.")

        return ScamDNAMatch(
            match_id=f"dnam_{uuid4().hex[:12]}",
            source_dna_id=dna1.dna_id,
            target_dna_id=dna2.dna_id,
            overall_similarity=composite_similarity,
            match_confidence=match_confidence,
            dimension_scores=dimension_scores,
            available_comparison_dimensions=[d.value for d in available_in_both],
            missing_comparison_dimensions=missing_in_either,
            matched_features=matched_features,
            contradictions=contradictions,
            variant_status=variant_status,
            reason_codes=list(set(all_reasons)),
            explanation=" ".join(explanation_lines),
            engine_version="3.0.0",
        )
