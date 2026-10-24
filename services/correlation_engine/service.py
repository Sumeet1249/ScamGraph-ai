"""Cross-Incident Correlation Engine Service (Phase 3B - Sections 120-121).

Coordinates candidate retrieval, feature extraction, scoring, privacy serialization,
and relationship materialization across incidents.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from packages.schemas.correlation import (
    AnalystCorrelationView,
    CandidateIncident,
    CandidateIncidentGroup,
    ConsumerNetworkSignal,
    IncidentCorrelation,
    RelationshipStatus,
)
from packages.schemas.dna import ScamDNA
from packages.schemas.journey import ScamJourney
from services.correlation_engine.config import CorrelationConfig
from services.correlation_engine.features import CorrelationFeatureExtractor
from services.correlation_engine.retriever import CandidateRetriever
from services.correlation_engine.scorer import CorrelationScorer
from services.correlation_engine.serializer import CorrelationSerializer
from services.dna_engine.service import ScamDNAService, scam_dna_service

logger = logging.getLogger("correlation_engine.service")


class CrossIncidentCorrelationService:
    """Core orchestration service for cross-victim network intelligence and relationship scoring."""

    def __init__(
        self,
        config: Optional[CorrelationConfig] = None,
        retriever: Optional[CandidateRetriever] = None,
        feature_extractor: Optional[CorrelationFeatureExtractor] = None,
        scorer: Optional[CorrelationScorer] = None,
        serializer: Optional[CorrelationSerializer] = None,
        dna_service: Optional[ScamDNAService] = None,
    ):
        self.config = config or CorrelationConfig.load()
        self.retriever = retriever or CandidateRetriever(config=self.config)
        self.feature_extractor = feature_extractor or CorrelationFeatureExtractor(config=self.config)
        self.scorer = scorer or CorrelationScorer(config=self.config)
        self.serializer = serializer or CorrelationSerializer(config=self.config)
        self.dna_service = dna_service or scam_dna_service

        # In-memory storage for material relationships: canonical_pair_id -> IncidentCorrelation
        self._materialized_correlations: Dict[str, IncidentCorrelation] = {}
        # Incident store: incident_id -> Dict[str, Any]
        self._incidents: Dict[str, Dict[str, Any]] = {}
        # Journey store: incident_id -> ScamJourney
        self._journeys: Dict[str, ScamJourney] = {}
        # Correlation history: canonical_pair_id -> List[IncidentCorrelation]
        self._correlation_history: Dict[str, List[IncidentCorrelation]] = {}

    @staticmethod
    def get_canonical_pair_id(id_a: str, id_b: str) -> str:
        """Enforces symmetric pair ordering: min(id_a, id_b)_max(id_a, id_b)."""
        first, second = sorted([id_a, id_b])
        return f"corr_{first}_{second}"

    def register_incident(
        self,
        incident_id: str,
        entities: Optional[List[Dict[str, Any]]] = None,
        scam_family: Optional[str] = None,
        dna: Optional[ScamDNA] = None,
        journey: Optional[ScamJourney] = None,
        text: Optional[str] = None,
        channels: Optional[List[str]] = None,
        is_verified_legitimate: bool = False,
        observed_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registers and indexes an incident in the correlation ecosystem."""
        ts = observed_at or datetime.now(timezone.utc)
        dna_id = dna.dna_id if dna else None

        self._incidents[incident_id] = {
            "incident_id": incident_id,
            "entities": entities or [],
            "scam_family": scam_family or (journey.scam_family if journey else "UNKNOWN"),
            "dna": dna,
            "dna_id": dna_id,
            "journey": journey,
            "text": text or "",
            "channels": channels or [],
            "is_verified_legitimate": is_verified_legitimate,
            "observed_at": ts,
            "metadata": metadata or {},
        }
        if journey:
            self._journeys[incident_id] = journey

        # Index incident in candidate retriever lookup
        self.retriever.index_incident(
            incident_id=incident_id,
            entities=entities,
            scam_family=scam_family or (journey.scam_family if journey else "UNKNOWN"),
            observed_at=ts,
            dna_id=dna_id,
            metadata=metadata,
        )

    def find_candidates(self, incident_id: str) -> List[CandidateIncident]:
        """Stage 1: Discovers candidate incidents using multi-source retrieval."""
        src = self._incidents.get(incident_id)
        if not src:
            return []

        return self.retriever.retrieve_candidates(
            source_incident_id=incident_id,
            source_entities=src.get("entities"),
            source_family=src.get("scam_family"),
            source_dna_id=src.get("dna_id"),
            observed_at=src.get("observed_at"),
        )

    def correlate_pair(
        self,
        source_incident_id: str,
        target_incident_id: str,
    ) -> IncidentCorrelation:
        """Stage 2: Detailed feature extraction and scoring between two incidents."""
        pair_id = self.get_canonical_pair_id(source_incident_id, target_incident_id)
        src = self._incidents.get(source_incident_id, {"incident_id": source_incident_id})
        tgt = self._incidents.get(target_incident_id, {"incident_id": target_incident_id})

        src_dna = src.get("dna")
        tgt_dna = tgt.get("dna")
        src_journey = src.get("journey") or self._journeys.get(source_incident_id)
        tgt_journey = tgt.get("journey") or self._journeys.get(target_incident_id)

        # 1. Feature extraction
        features, pos_reasons, contradictions, shared_ents = self.feature_extractor.extract_features(
            source_incident=src,
            target_incident=tgt,
            source_dna=src_dna,
            target_dna=tgt_dna,
            source_journey=src_journey,
            target_journey=tgt_journey,
        )

        # 2. Rule-gated scoring
        score, conf, status, strength, breakdown, neg_reasons = self.scorer.score_pair(
            features=features,
            positive_reasons=pos_reasons,
            contradictions=contradictions,
        )

        infra_list = src.get("channels", []) if features.infrastructure_similarity >= 0.70 else []

        correlation = IncidentCorrelation(
            correlation_id=pair_id,
            source_incident_id=source_incident_id,
            target_incident_id=target_incident_id,
            relationship_status=status,
            overall_score=score,
            confidence=conf,
            evidence_strength=strength,
            feature_scores=features.model_dump(),
            shared_entities=shared_ents,
            shared_infrastructure=infra_list,
            dna_similarity=features.dna_similarity,
            journey_similarity=features.journey_similarity,
            tactic_similarity=features.tactic_similarity,
            semantic_similarity=features.semantic_similarity,
            temporal_similarity=features.temporal_similarity,
            graph_similarity=features.graph_path_score,
            positive_reasons=pos_reasons,
            negative_reasons=neg_reasons,
            contradictions=contradictions,
            engine_version=self.config.engine_version,
            last_calculated_at=datetime.now(timezone.utc),
            metadata={"group_contributions": breakdown},
        )

        # Store in correlation history
        self._correlation_history.setdefault(pair_id, []).append(correlation)

        # Materialize if meaningful relationship threshold met
        if status in (
            RelationshipStatus.STRONGLY_RELATED,
            RelationshipStatus.LIKELY_RELATED_PATTERN,
            RelationshipStatus.POSSIBLY_RELATED,
        ):
            self._materialized_correlations[pair_id] = correlation
        elif pair_id in self._materialized_correlations and status == RelationshipStatus.NOT_RELATED:
            # Relationship downgraded/reversed
            del self._materialized_correlations[pair_id]

        return correlation

    def correlate_incident(
        self,
        incident_id: str,
        top_k: int = 10,
    ) -> List[IncidentCorrelation]:
        """Correlates an incident against the candidate index and returns top relationships."""
        candidates = self.find_candidates(incident_id)
        results: List[IncidentCorrelation] = []

        for cand in candidates:
            corr = self.correlate_pair(incident_id, cand.incident_id)
            if corr.relationship_status != RelationshipStatus.NOT_RELATED:
                results.append(corr)

        # Sort by overall score descending
        results.sort(key=lambda c: c.overall_score, reverse=True)
        return results[:top_k]

    def get_related_incidents(self, incident_id: str) -> List[IncidentCorrelation]:
        """Retrieves all materialized relationships involving this incident."""
        related: List[IncidentCorrelation] = []
        for pair_id, corr in self._materialized_correlations.items():
            if corr.source_incident_id == incident_id or corr.target_incident_id == incident_id:
                related.append(corr)
        return sorted(related, key=lambda c: c.overall_score, reverse=True)

    def get_network_signal(self, incident_id: str) -> ConsumerNetworkSignal:
        """Generates an aggregate, privacy-safe consumer alert for an incident."""
        related = self.get_related_incidents(incident_id)
        src = self._incidents.get(incident_id, {})
        journey = src.get("journey")
        display_stage = journey.current_stage.value if journey and hasattr(journey.current_stage, "value") else None

        return self.serializer.to_consumer_network_signal(
            incident_id=incident_id,
            correlations=related,
            display_stage=display_stage,
        )

    def get_analyst_view(
        self,
        source_id: str,
        target_id: str,
    ) -> AnalystCorrelationView:
        """Retrieves or computes full analyst telemetry for an incident pair."""
        pair_id = self.get_canonical_pair_id(source_id, target_id)
        corr = self._materialized_correlations.get(pair_id) or self.correlate_pair(source_id, target_id)
        breakdown = corr.metadata.get("group_contributions", {})
        return self.serializer.to_analyst_view(corr, breakdown)

    def recompute_pair(self, source_id: str, target_id: str) -> IncidentCorrelation:
        """Forces on-demand recomputation of an incident pair (e.g. after entity dispute/split)."""
        return self.correlate_pair(source_id, target_id)

    def recompute_for_entity(self, entity_val: str) -> List[IncidentCorrelation]:
        """Recomputes all correlations involving incidents that share a modified entity."""
        affected_incidents = self.retriever._entity_index.get(str(entity_val).strip().lower(), set())
        recomputed: List[IncidentCorrelation] = []
        inc_list = list(affected_incidents)
        for i in range(len(inc_list)):
            for j in range(i + 1, len(inc_list)):
                corr = self.correlate_pair(inc_list[i], inc_list[j])
                recomputed.append(corr)
        return recomputed

    def generate_campaign_candidate_group(
        self,
        incident_ids: List[str],
    ) -> CandidateIncidentGroup:
        """Emits a CampaignCandidateGroup across related incidents (Section 87, 145-146 for Prompt 12)."""
        valid_ids = [i for i in incident_ids if i in self._incidents]
        strong_edges = 0
        total_pairs = 0
        evidence_classes: Set[str] = set()
        first_seen = datetime.now(timezone.utc)
        last_seen = datetime.fromtimestamp(0, tz=timezone.utc)

        for i in range(len(valid_ids)):
            src_inc = self._incidents[valid_ids[i]]
            ts = src_inc.get("observed_at", first_seen)
            if ts < first_seen:
                first_seen = ts
            if ts > last_seen:
                last_seen = ts

            for j in range(i + 1, len(valid_ids)):
                total_pairs += 1
                corr = self.correlate_pair(valid_ids[i], valid_ids[j])
                if corr.relationship_status == RelationshipStatus.STRONGLY_RELATED:
                    strong_edges += 1
                for r in corr.positive_reasons:
                    evidence_classes.add(r.split("(")[0])

        density = (strong_edges / max(1, total_pairs)) if total_pairs > 0 else 0.0
        primary_family = self._incidents[valid_ids[0]].get("scam_family", "UNKNOWN") if valid_ids else "UNKNOWN"

        return CandidateIncidentGroup(
            group_id=f"cand_grp_{uuid4().hex[:10]}",
            member_incident_ids=valid_ids,
            relationship_density=round(density, 3),
            strong_edge_count=strong_edges,
            evidence_diversity=sorted(list(evidence_classes)),
            primary_family=primary_family,
            first_seen=first_seen,
            last_seen=last_seen,
            growth_velocity=round(len(valid_ids) / max(1.0, (last_seen - first_seen).total_seconds() / 86400.0), 2),
        )


# Default singleton instance
correlation_service = CrossIncidentCorrelationService()
