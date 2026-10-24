"""Scam Fingerprint V2 Similarity Engine (Step 25).

Combines 5 core correlation dimensions:
1. Semantic meaning & psychological tactics
2. Temporal journey progression & sequence alignment
3. Infrastructure overlap (Domain, IP, ASN, NS, Cert)
4. Payment context (VPA, bank account, channel)
5. Pattern matching overlap

Strict Rule:
Overall similarity is NOT an opaque average. It uses configurable weights
defined in config/scam_fingerprint.yaml with explainable dimensional breakdowns.
"""

from __future__ import annotations

import difflib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import yaml

from packages.schemas.fingerprint import (
    FingerprintSimilarityResult,
    ScamFingerprintV2,
)

logger = logging.getLogger("pattern_engine.similarity_engine")

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "config" / "scam_fingerprint.yaml"

DEFAULT_WEIGHTS = {
    "semantic_weight": 0.30,
    "journey_weight": 0.30,
    "pattern_weight": 0.15,
    "infrastructure_weight": 0.15,
    "payment_weight": 0.10,
}


def load_fingerprint_config() -> Dict[str, Any]:
    """Load weights and thresholds from config/scam_fingerprint.yaml."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data or {}
        except Exception as e:
            logger.warning(f"Failed to parse {CONFIG_PATH}: {e}. Using default weights.")
    return {"weights": DEFAULT_WEIGHTS}


class ScamFingerprintSimilarityEngine:
    """Computes multi-dimensional similarity and sequence alignment between two ScamFingerprintV2 instances."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or load_fingerprint_config()
        self.weights = self.config.get("weights", DEFAULT_WEIGHTS)
        self.thresholds = self.config.get("thresholds", {})
        self.seq_cfg = self.config.get("sequence_alignment", {})

    # -------------------------------------------------------------------------
    # Dimension 1: Semantic Similarity
    # -------------------------------------------------------------------------

    def compute_semantic_similarity(
        self,
        fp1: ScamFingerprintV2,
        fp2: ScamFingerprintV2,
    ) -> float:
        """Compute semantic vector cosine similarity + tactic & action overlap."""
        # 1. Vector cosine similarity
        vector_sim = 0.0
        has_vector = False
        if fp1.semantic_embedding and fp2.semantic_embedding:
            vec1 = np.array(fp1.semantic_embedding, dtype=np.float32)
            vec2 = np.array(fp2.semantic_embedding, dtype=np.float32)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 > 0 and norm2 > 0:
                raw_cos = float(np.dot(vec1, vec2) / (norm1 * norm2))
                vector_sim = max(0.0, min(1.0, raw_cos))
                has_vector = True

        # 2. Tactic overlap (Jaccard)
        tactics1 = set(t.upper() for t in fp1.social_engineering_tactics)
        tactics2 = set(t.upper() for t in fp2.social_engineering_tactics)
        if tactics1 and tactics2:
            tactic_sim = len(tactics1.intersection(tactics2)) / len(tactics1.union(tactics2))
        else:
            tactic_sim = 1.0 if not tactics1 and not tactics2 else 0.0

        # 3. Requested action overlap
        act1 = set(a.upper() for a in fp1.requested_actions)
        act2 = set(a.upper() for a in fp2.requested_actions)
        if act1 and act2:
            action_sim = len(act1.intersection(act2)) / len(act1.union(act2))
        else:
            action_sim = 1.0 if not act1 and not act2 else 0.0

        if has_vector:
            return round(0.60 * vector_sim + 0.20 * tactic_sim + 0.20 * action_sim, 4)
        return round(0.50 * tactic_sim + 0.50 * action_sim, 4)

    # -------------------------------------------------------------------------
    # Dimension 2: Temporal Journey Sequence Similarity
    # -------------------------------------------------------------------------

    def compute_journey_similarity(
        self,
        seq1: List[str],
        seq2: List[str],
    ) -> Tuple[float, Dict[str, Any]]:
        """Compute deterministic sequence similarity tolerant of small insertions and reorderings.

        Uses Gestalt pattern matching (LCS alignment) with reordering window tolerance.
        """
        if not seq1 and not seq2:
            return 1.0, {"alignment_score": 1.0, "matches": 0, "status": "both_empty"}
        if not seq1 or not seq2:
            return 0.0, {"alignment_score": 0.0, "matches": 0, "status": "one_empty"}

        s1 = [e.upper().strip() for e in seq1]
        s2 = [e.upper().strip() for e in seq2]

        # Use SequenceMatcher to find contiguous matching blocks
        matcher = difflib.SequenceMatcher(None, s1, s2)
        ratio = matcher.ratio()

        # Check set overlap of stages
        set1 = set(s1)
        set2 = set(s2)
        jaccard_stages = len(set1.intersection(set2)) / len(set1.union(set2))

        # Reordering tolerance: if the same stages exist in slightly permuted order,
        # blend the sequence ratio with the stage set overlap
        combined_score = 0.65 * ratio + 0.35 * jaccard_stages

        # Alignment diagnostics
        matching_blocks = [
            {"seq1_idx": b.a, "seq2_idx": b.b, "length": b.size}
            for b in matcher.get_matching_blocks()
            if b.size > 0
        ]

        alignment_info = {
            "sequence_matcher_ratio": round(ratio, 4),
            "stage_set_jaccard": round(jaccard_stages, 4),
            "matching_blocks": matching_blocks,
            "seq1_length": len(s1),
            "seq2_length": len(s2),
        }

        return round(combined_score, 4), alignment_info

    # -------------------------------------------------------------------------
    # Dimension 3: Infrastructure Similarity
    # -------------------------------------------------------------------------

    def compute_infrastructure_similarity(
        self,
        inf1: Dict[str, Any],
        inf2: Dict[str, Any],
    ) -> Tuple[float, List[str]]:
        """Compute Jaccard similarity across domain, IP, ASN, nameserver, certificate."""
        keys = ["domain", "ip", "asn", "nameserver", "certificate"]
        shared: List[str] = []
        total_features = 0

        for k in keys:
            val1 = str(inf1.get(k) or "").strip().lower()
            val2 = str(inf2.get(k) or "").strip().lower()
            if val1 or val2:
                total_features += 1
                if val1 and val2 and val1 == val2:
                    shared.append(f"{k}:{val1}")

        if total_features == 0:
            return 0.0, []

        sim = len(shared) / total_features
        return round(sim, 4), shared

    # -------------------------------------------------------------------------
    # Dimension 4: Payment Similarity
    # -------------------------------------------------------------------------

    def compute_payment_similarity(
        self,
        pay1: Dict[str, Any],
        pay2: Dict[str, Any],
    ) -> Tuple[float, List[str]]:
        """Compute payment recipient similarity (VPA handle, bank account, payment channel)."""
        vpa1 = str(pay1.get("vpa") or pay1.get("payment_id") or "").strip().lower()
        vpa2 = str(pay2.get("vpa") or pay2.get("payment_id") or "").strip().lower()

        acc1 = str(pay1.get("account_number") or "").strip()
        acc2 = str(pay2.get("account_number") or "").strip()

        shared = []
        if vpa1 and vpa2 and vpa1 == vpa2:
            shared.append(f"vpa:{vpa1}")
            return 1.0, shared

        if acc1 and acc2 and acc1 == acc2:
            shared.append(f"account:{acc1}")
            return 1.0, shared

        # Same PSP / payment provider (e.g. both @oksbi) gives partial context
        if "@" in vpa1 and "@" in vpa2:
            handle1 = vpa1.split("@")[1]
            handle2 = vpa2.split("@")[1]
            if handle1 == handle2:
                return 0.25, [f"shared_psp:@{handle1}"]

        return 0.0, []

    # -------------------------------------------------------------------------
    # Dimension 5: Pattern Similarity
    # -------------------------------------------------------------------------

    def compute_pattern_similarity(
        self,
        pats1: List[str],
        pats2: List[str],
    ) -> Tuple[float, List[str]]:
        """Compute Jaccard similarity of recognized pattern classifications."""
        set1 = set(p.upper() for p in pats1)
        set2 = set(p.upper() for p in pats2)

        if not set1 and not set2:
            return 0.0, []
        if not set1 or not set2:
            return 0.0, []

        intersection = set1.intersection(set2)
        union = set1.union(set2)
        sim = len(intersection) / len(union)
        return round(sim, 4), sorted(intersection)

    # -------------------------------------------------------------------------
    # Identifier Overlap (Exact match of phone, domain, VPA)
    # -------------------------------------------------------------------------

    def compute_identifier_overlap(
        self,
        fp1: ScamFingerprintV2,
        fp2: ScamFingerprintV2,
    ) -> Tuple[float, List[str]]:
        """Direct exact match of primary identifiers. In a mutated scam, this is 0.0."""
        shared_ids: List[str] = []
        total_ids = 0

        # Phone
        phone1 = str(fp1.infrastructure_entities.get("phone") or "").strip()
        phone2 = str(fp2.infrastructure_entities.get("phone") or "").strip()
        if phone1 or phone2:
            total_ids += 1
            if phone1 and phone2 and phone1 == phone2:
                shared_ids.append(f"phone:{phone1}")

        # Domain
        dom1 = str(fp1.infrastructure_entities.get("domain") or "").strip().lower()
        dom2 = str(fp2.infrastructure_entities.get("domain") or "").strip().lower()
        if dom1 or dom2:
            total_ids += 1
            if dom1 and dom2 and dom1 == dom2:
                shared_ids.append(f"domain:{dom1}")

        # Payment VPA
        vpa1 = str(fp1.payment_entities.get("vpa") or "").strip().lower()
        vpa2 = str(fp2.payment_entities.get("vpa") or "").strip().lower()
        if vpa1 or vpa2:
            total_ids += 1
            if vpa1 and vpa2 and vpa1 == vpa2:
                shared_ids.append(f"vpa:{vpa1}")

        if total_ids == 0:
            return 0.0, []

        overlap = len(shared_ids) / total_ids
        return round(overlap, 4), shared_ids

    # -------------------------------------------------------------------------
    # Master Similarity Engine
    # -------------------------------------------------------------------------

    @classmethod
    def compare_fingerprints(
        cls,
        fp1: ScamFingerprintV2,
        fp2: ScamFingerprintV2,
    ) -> FingerprintSimilarityResult:
        """Convenience class method to compare two fingerprints using default config."""
        return cls().compare(fp1, fp2)

    def compare(
        self,
        fp1: ScamFingerprintV2,
        fp2: ScamFingerprintV2,
    ) -> FingerprintSimilarityResult:
        """Compare two ScamFingerprintV2 instances across all 5 dimensions."""
        # 1. Semantic
        sem_sim = self.compute_semantic_similarity(fp1, fp2)

        # 2. Temporal Journey
        jrn_sim, alignment_info = self.compute_journey_similarity(
            fp1.ordered_event_sequence, fp2.ordered_event_sequence
        )

        # 3. Infrastructure
        inf_sim, shared_inf = self.compute_infrastructure_similarity(
            fp1.infrastructure_entities, fp2.infrastructure_entities
        )

        # 4. Payment
        pay_sim, shared_pay = self.compute_payment_similarity(
            fp1.payment_entities, fp2.payment_entities
        )

        # 5. Pattern
        pat_sim, shared_pats = self.compute_pattern_similarity(
            fp1.pattern_matches, fp2.pattern_matches
        )

        # Identifier Overlap
        id_overlap, shared_ids = self.compute_identifier_overlap(fp1, fp2)

        # Overall weighted similarity index
        w = self.weights
        overall_index = (
            w.get("semantic_weight", 0.30) * sem_sim
            + w.get("journey_weight", 0.30) * jrn_sim
            + w.get("pattern_weight", 0.15) * pat_sim
            + w.get("infrastructure_weight", 0.15) * inf_sim
            + w.get("payment_weight", 0.10) * pay_sim
        )
        overall_index = round(max(0.0, min(1.0, overall_index)), 4)

        # Dimension classifications
        dimension_scores = {
            "SEMANTIC": sem_sim,
            "JOURNEY": jrn_sim,
            "PATTERN": pat_sim,
            "INFRASTRUCTURE": inf_sim,
            "PAYMENT": pay_sim,
        }
        matched_dims = [dim for dim, score in dimension_scores.items() if score >= 0.70]
        diff_dims = [dim for dim, score in dimension_scores.items() if score < 0.40]

        all_shared_entities = list(set(shared_ids + shared_inf + shared_pay))

        # Construct clear explainability summary
        if id_overlap == 0.0 and sem_sim >= 0.70 and jrn_sim >= 0.70:
            explanation = (
                f"MUTATED VARIANT DETECTED: Identifiers completely differ (overlap: 0.0), "
                f"yet behavioral semantics ({sem_sim}) and journey progression ({jrn_sim}) "
                f"exhibit near-identical grooming structure."
            )
        elif overall_index >= 0.70:
            explanation = (
                f"HIGH SIMILARITY ({overall_index}): Incidents share strong behavioral "
                f"and technical patterns across {len(matched_dims)} dimensions."
            )
        elif overall_index >= 0.40:
            explanation = (
                f"MODERATE SIMILARITY ({overall_index}): Partial overlap observed in "
                f"{', '.join(matched_dims) if matched_dims else 'workflow'}."
            )
        else:
            explanation = (
                f"LOW SIMILARITY ({overall_index}): Workflows and technical indicators diverge significantly."
            )

        return FingerprintSimilarityResult(
            semantic_similarity=sem_sim,
            journey_similarity=jrn_sim,
            infrastructure_similarity=inf_sim,
            payment_similarity=pay_sim,
            pattern_similarity=pat_sim,
            identifier_overlap=id_overlap,
            overall_similarity_index=overall_index,
            matched_dimensions=matched_dims,
            different_dimensions=diff_dims,
            shared_entities=all_shared_entities,
            shared_patterns=shared_pats,
            sequence_alignment=alignment_info,
            explanation=explanation,
        )


# Default singleton instance
fingerprint_similarity_engine = ScamFingerprintSimilarityEngine()
