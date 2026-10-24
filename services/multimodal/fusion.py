"""Multimodal Evidence Fusion Engine (Prompt 18 / Phase 5D).

Rules:
1. Prevent double-counting: Derived observations sharing an ancestor lineage must not be counted as independent corroboration.
2. Independent corroboration: Genuinely separate artifacts (e.g. chat screenshot + separate QR code) sharing an entity or tactic strengthen confidence.
3. Track contradicting claims alongside corroborating claims.
4. Calculate coverage score and overall fusion confidence.
"""

from collections import defaultdict
import logging
from typing import Dict, List, Optional, Set, Tuple

from packages.schemas.multimodal import DerivedObservation, EvidenceFusionResult

logger = logging.getLogger("scamgraph.multimodal.fusion")


class EvidenceFusionEngine:
    """Fuses multi-source multimodal observations while strictly preventing double-counting."""

    FUSION_VERSION = "2.0.0"

    def fuse(
        self,
        incident_id: str,
        observations: List[DerivedObservation],
    ) -> EvidenceFusionResult:
        """Evaluates observations for independent root provenance, corroboration, and contradictions."""
        if not observations:
            return EvidenceFusionResult(
                incident_id=incident_id,
                observations=[],
                independent_source_groups={},
                corroborating_claims=[],
                contradicting_claims=[],
                coverage_score=0.0,
                fusion_confidence=0.5,
                double_counting_prevented_count=0,
                fusion_version=self.FUSION_VERSION,
            )

        # 1. Group observations by their root source_artifact_id
        source_groups: Dict[str, List[str]] = defaultdict(list)
        entity_to_sources: Dict[str, Set[str]] = defaultdict(set)
        tactics_to_sources: Dict[str, Set[str]] = defaultdict(set)

        double_count_prevented = 0

        for obs in observations:
            root_src = obs.source_artifact_id
            source_groups[root_src].append(obs.observation_id)

            # Check if this observation is derived from an upstream observation from the same root
            if obs.lineage_parent_ids:
                # Derived from prior observation in same artifact chain
                double_count_prevented += len(obs.lineage_parent_ids)

            # Map normalized entities and tactics to independent root sources
            if obs.observation_type.value in ("UPI_VPA", "PHONE_NUMBER", "URL", "DOMAIN", "PAYMENT_AMOUNT"):
                entity_to_sources[f"{obs.observation_type.value}:{obs.normalized_value}"].add(root_src)

            if obs.observation_type.value == "TACTIC_EVIDENCE":
                tactics_to_sources[obs.normalized_value].add(root_src)

        # 2. Identify Independent Corroborating Claims
        corroborating_claims: List[str] = []
        for entity_key, sources in entity_to_sources.items():
            if len(sources) >= 2:
                corroborating_claims.append(
                    f"INDEPENDENT_ENTITY_CORROBORATION({entity_key} confirmed across {len(sources)} distinct artifacts)"
                )

        for tactic_key, sources in tactics_to_sources.items():
            if len(sources) >= 2:
                corroborating_claims.append(
                    f"INDEPENDENT_TACTIC_CORROBORATION({tactic_key} observed across {len(sources)} distinct artifacts)"
                )

        # 3. Contradictions (e.g. legitimate bank domain claimed vs personal UPI VPA requested)
        contradicting_claims: List[str] = []
        has_official_claim = any(
            obs.observation_type.value == "BRAND_MENTION" and ("sbi" in obs.raw_value.lower() or "rbi" in obs.raw_value.lower())
            for obs in observations
        )
        has_personal_vpa = any(
            obs.observation_type.value == "UPI_VPA" and any(p in obs.normalized_value.lower() for p in ("@oksbi", "@paytm", "@ybl", "@apl"))
            for obs in observations
        )
        if has_official_claim and has_personal_vpa:
            contradicting_claims.append(
                "CONTRADICTION(Official institutional authority claimed, but payment destination is an individual personal VPA)"
            )

        # 4. Coverage & Confidence Score
        distinct_sources_count = len(source_groups)
        obs_types_count = len(set(obs.observation_type.value for obs in observations))
        coverage_score = min(1.0, round((distinct_sources_count * 0.25) + (obs_types_count * 0.15), 2))

        # Overall fusion confidence: higher when multiple independent sources corroborate
        fusion_conf = 0.85
        if corroborating_claims:
            fusion_conf = min(0.98, fusion_conf + (len(corroborating_claims) * 0.04))
        if contradicting_claims:
            # Contradictions are evidence of fraudulent impersonation!
            fusion_conf = min(0.99, fusion_conf + 0.05)

        return EvidenceFusionResult(
            incident_id=incident_id,
            observations=observations,
            independent_source_groups=dict(source_groups),
            corroborating_claims=corroborating_claims,
            contradicting_claims=contradicting_claims,
            coverage_score=coverage_score,
            fusion_confidence=round(fusion_conf, 2),
            double_counting_prevented_count=double_count_prevented,
            fusion_version=self.FUSION_VERSION,
        )


evidence_fusion_engine = EvidenceFusionEngine()
