"""Correlation Feature Extractor (Phase 3B - Sections 35-36, 81-86).

Extracts normalized, versioned feature vectors across:
1. Entity overlap (rare UPI, phone, domain, social, informativeness weighting)
2. Infrastructure behavior (channel sequences, CDN downweighting)
3. Behavioral alignment (ScamDNA, Journey sequence, Tactic profiles)
4. Temporal alignment (inter-incident days, burst proximity)
5. Graph structure (meaningful path scoring, supernode filtering)
6. Contradictions (verified legitimate entity, incompatible journeys)
"""

from __future__ import annotations

import difflib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from packages.schemas.correlation import CorrelationFeatures
from packages.schemas.dna import ScamDNA, DNADimensionType
from packages.schemas.journey import ScamJourney
from services.correlation_engine.config import CorrelationConfig
from services.dna_engine.similarity import ScamDNASimilarityEngine

logger = logging.getLogger("correlation_engine.features")


class CorrelationFeatureExtractor:
    """Extracts transparent, auditable feature vectors for cross-incident scoring."""

    def __init__(
        self,
        config: Optional[CorrelationConfig] = None,
        dna_similarity_engine: Optional[ScamDNASimilarityEngine] = None,
    ):
        self.config = config or CorrelationConfig.load()
        self.dna_sim_engine = dna_similarity_engine or ScamDNASimilarityEngine()

    def extract_features(
        self,
        source_incident: Dict[str, Any],
        target_incident: Dict[str, Any],
        source_dna: Optional[ScamDNA] = None,
        target_dna: Optional[ScamDNA] = None,
        source_journey: Optional[ScamJourney] = None,
        target_journey: Optional[ScamJourney] = None,
    ) -> Tuple[CorrelationFeatures, List[str], List[str], List[Dict[str, Any]]]:
        """Extracts complete feature vector, positive reasons, contradictions, and shared entities."""
        positive_reasons: List[str] = []
        contradictions: List[str] = []
        shared_entities_list: List[Dict[str, Any]] = []

        src_ents = source_incident.get("entities", [])
        tgt_ents = target_incident.get("entities", [])

        # ---------------------------------------------------------------------
        # 1. Entity Overlap Features & Informativeness
        # ---------------------------------------------------------------------
        src_ent_map: Dict[str, Dict[str, Any]] = {}
        for e in src_ents:
            val = e.get("canonical_value") or e.get("value") or e.get("entity_id")
            if val:
                src_ent_map[str(val).strip().lower()] = e

        tgt_ent_map: Dict[str, Dict[str, Any]] = {}
        for e in tgt_ents:
            val = e.get("canonical_value") or e.get("value") or e.get("entity_id")
            if val:
                tgt_ent_map[str(val).strip().lower()] = e

        shared_keys = set(src_ent_map.keys()).intersection(tgt_ent_map.keys())

        exact_payment = 0.0
        exact_phone = 0.0
        exact_domain = 0.0
        exact_social = 0.0
        shared_rare_count = 0
        shared_common_count = 0
        shared_info_sum = 0.0

        for key in shared_keys:
            e_src = src_ent_map[key]
            ent_type = e_src.get("entity_type", "UNKNOWN")
            raw_val = str(e_src.get("canonical_value") or key).strip()
            val_upper = raw_val.upper()
            val_lower = raw_val.lower()

            # Super-node check: generic brand or common CDN
            is_generic_brand = val_upper in self.config.generic_brands or ent_type == "BRAND"
            is_common_cdn = val_lower in self.config.common_infrastructure_domains

            if is_generic_brand:
                shared_common_count += 1
                continue  # Generic brands produce 0 entity correlation weight

            if is_common_cdn:
                shared_common_count += 1
                continue  # Shared CDNs produce 0 entity correlation weight

            # Specific rare entity match
            shared_rare_count += 1
            info_weight = self.config.entity_type_informativeness.get(ent_type, 0.70)
            shared_info_sum += info_weight

            shared_entities_list.append({
                "entity_type": ent_type,
                "canonical_value_masked": raw_val[:3] + "***" + raw_val[-2:] if len(raw_val) > 5 else "***",
                "informativeness": info_weight,
            })

            if ent_type in ("PAYMENT_IDENTIFIER", "UPI_VPA", "BANK_ACCOUNT"):
                exact_payment = 1.0
                positive_reasons.append("SHARED_PAYMENT_IDENTIFIER")
            elif ent_type in ("PHONE_NUMBER", "PHONE"):
                exact_phone = 1.0
                positive_reasons.append("SHARED_PHONE_NUMBER")
            elif ent_type in ("DOMAIN", "URL"):
                exact_domain = 1.0
                positive_reasons.append(f"SHARED_DEDICATED_DOMAIN({raw_val})")
            elif ent_type in ("TELEGRAM_HANDLE", "SOCIAL_ACCOUNT"):
                exact_social = 1.0
                positive_reasons.append("SHARED_SOCIAL_HANDLE")

        # Weighted entity overlap ratio
        all_unique_keys = set(src_ent_map.keys()).union(tgt_ent_map.keys())
        total_info_union = sum(
            self.config.entity_type_informativeness.get(
                src_ent_map.get(k, tgt_ent_map.get(k, {})).get("entity_type", "UNKNOWN"), 0.5
            )
            for k in all_unique_keys
            if k.upper() not in self.config.generic_brands and k.lower() not in self.config.common_infrastructure_domains
        )
        weighted_entity_overlap = min(1.0, shared_info_sum / max(1.0, total_info_union)) if total_info_union > 0 else 0.0

        # ---------------------------------------------------------------------
        # 2. Infrastructure Similarity
        # ---------------------------------------------------------------------
        src_channels = source_incident.get("channels", []) or (source_journey.channels if source_journey else [])
        tgt_channels = target_incident.get("channels", []) or (target_journey.channels if target_journey else [])
        infra_sim = 0.0
        if src_channels and tgt_channels:
            matcher = difflib.SequenceMatcher(None, src_channels, tgt_channels)
            infra_sim = round(matcher.ratio(), 3)
            if infra_sim >= 0.75:
                positive_reasons.append(f"SHARED_CHANNEL_PROGRESSION({' > '.join(src_channels)})")

        # ---------------------------------------------------------------------
        # 3. Behavioral Similarity (ScamDNA, Journey, Tactics)
        # ---------------------------------------------------------------------
        dna_sim = 0.0
        dna_cov = 0.0
        tactic_sim = 0.0
        journey_sim = 0.0

        if source_dna and target_dna:
            dna_match = self.dna_sim_engine.compare(source_dna, target_dna)
            dna_sim = dna_match.overall_similarity
            dna_cov = len(dna_match.available_comparison_dimensions) / 8.0
            if dna_sim >= 0.70:
                positive_reasons.append(f"STRONG_SCAM_DNA_ALIGNMENT(sim={round(dna_sim, 2)})")

            # Extract journey & tactic dimension scores if available
            journey_sim = dna_match.dimension_scores.get(DNADimensionType.JOURNEY.value, 0.0)
            tactic_sim = dna_match.dimension_scores.get(DNADimensionType.TACTIC.value, 0.0)

            # Check for DNA contradictions
            if dna_match.contradictions:
                contradictions.extend(dna_match.contradictions)
        elif source_journey and target_journey:
            # Fallback to direct journey comparison
            s1 = [s.value if hasattr(s, "value") else str(s) for s in source_journey.stage_history]
            s2 = [s.value if hasattr(s, "value") else str(s) for s in target_journey.stage_history]
            if s1 and s2:
                journey_sim = difflib.SequenceMatcher(None, s1, s2).ratio()
                if journey_sim >= 0.70:
                    positive_reasons.append(f"SIMILAR_JOURNEY_STAGES(ratio={round(journey_sim, 2)})")

        # ---------------------------------------------------------------------
        # 4. Semantic Similarity
        # ---------------------------------------------------------------------
        txt1 = source_incident.get("text", "") or source_incident.get("summary", "")
        txt2 = target_incident.get("text", "") or target_incident.get("summary", "")
        semantic_sim = 0.0
        if txt1 and txt2:
            semantic_sim = round(difflib.SequenceMatcher(None, txt1.lower(), txt2.lower()).ratio(), 3)
            if semantic_sim >= 0.75:
                positive_reasons.append("HIGH_TEXT_SIMILARITY")

        # ---------------------------------------------------------------------
        # 5. Temporal Similarity
        # ---------------------------------------------------------------------
        ts1 = source_incident.get("observed_at") or datetime.now(timezone.utc)
        ts2 = target_incident.get("observed_at") or datetime.now(timezone.utc)
        if hasattr(ts1, "timestamp") and hasattr(ts2, "timestamp"):
            days_diff = abs((ts1 - ts2).total_seconds()) / 86400.0
            temporal_sim = max(0.0, 1.0 - (days_diff / float(self.config.time_window_days)))
            if days_diff <= 7.0:
                positive_reasons.append(f"CONCURRENT_TEMPORAL_BURST({round(days_diff, 1)}d)")
        else:
            temporal_sim = 0.50

        # ---------------------------------------------------------------------
        # 6. Graph Path Score
        # ---------------------------------------------------------------------
        # Direct shared rare entity = 1.0, 2-hop shared infrastructure = 0.6, shared supernode alone = 0.0
        if shared_rare_count >= 1:
            graph_path_score = 1.0
            positive_reasons.append("DIRECT_SHARED_ENTITY_GRAPH_HOP")
        elif infra_sim >= 0.75:
            graph_path_score = 0.60
        else:
            graph_path_score = 0.0

        # ---------------------------------------------------------------------
        # 7. Contradiction Detection
        # ---------------------------------------------------------------------
        # Check if one is confirmed legitimate while the other is malicious
        src_legit = source_incident.get("is_verified_legitimate", False)
        tgt_legit = target_incident.get("is_verified_legitimate", False)
        if src_legit != tgt_legit:
            contradictions.append("CONTRADICTORY_LEGITIMATE_ENTITY_STATUS")

        # Check family incompatibility (e.g. digital arrest extortion vs job task scam)
        fam1 = source_incident.get("scam_family") or (source_journey.scam_family if source_journey else "UNKNOWN")
        fam2 = target_incident.get("scam_family") or (target_journey.scam_family if target_journey else "UNKNOWN")
        if fam1 != "UNKNOWN" and fam2 != "UNKNOWN" and fam1 != fam2:
            contradictions.append(f"INCOMPATIBLE_SCAM_FAMILY({fam1}_VS_{fam2})")

        # Rare identifier shared but completely incompatible journey
        if exact_payment > 0 and journey_sim > 0 and journey_sim < 0.25:
            contradictions.append("SHARED_PAYMENT_WITH_DIVERGENT_JOURNEY")

        contradiction_score = min(1.0, len(contradictions) * 0.40)

        features = CorrelationFeatures(
            exact_payment_overlap=exact_payment,
            exact_phone_overlap=exact_phone,
            exact_domain_overlap=exact_domain,
            exact_social_overlap=exact_social,
            weighted_entity_overlap=round(weighted_entity_overlap, 3),
            infrastructure_similarity=round(infra_sim, 3),
            dna_similarity=round(dna_sim, 3),
            dna_coverage=round(dna_cov, 3),
            journey_similarity=round(journey_sim, 3),
            tactic_similarity=round(tactic_sim, 3),
            semantic_similarity=round(semantic_sim, 3),
            temporal_similarity=round(temporal_sim, 3),
            graph_path_score=round(graph_path_score, 3),
            shared_rare_entity_count=shared_rare_count,
            shared_common_entity_count=shared_common_count,
            contradiction_score=round(contradiction_score, 3),
            evidence_quality=0.85,
        )

        return features, positive_reasons, contradictions, shared_entities_list
