"""ScamDNA Service Orchestrator.

Manages ScamDNA creation, caching, candidate indexing, and multi-dimensional comparison.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from packages.schemas.dna import (
    ConsumerDNAView,
    ScamDNA,
    ScamDNAMatch,
)
from packages.schemas.journey import ScamJourney
from services.dna_engine.builder import ScamDNABuilder
from services.dna_engine.retrieval import DNACandidateIndex
from services.dna_engine.serializer import DNASerializer
from services.dna_engine.similarity import ScamDNASimilarityEngine

logger = logging.getLogger("dna_engine.service")


class ScamDNAService:
    """Core service managing lifecycle and matching of ScamDNA behavioral signatures."""

    def __init__(
        self,
        similarity_engine: Optional[ScamDNASimilarityEngine] = None,
        candidate_index: Optional[DNACandidateIndex] = None,
    ):
        self.similarity_engine = similarity_engine or ScamDNASimilarityEngine()
        self.candidate_index = candidate_index or DNACandidateIndex(self.similarity_engine)
        self.dna_store: Dict[str, ScamDNA] = {}
        self.incident_dna_map: Dict[str, str] = {}

    def create_or_update_dna(
        self,
        incident_id: str,
        journey: Optional[ScamJourney] = None,
        tactics: Optional[List[str]] = None,
        entities: Optional[List[Dict[str, Any]]] = None,
        payment_context: Optional[Dict[str, Any]] = None,
        infrastructure: Optional[Dict[str, Any]] = None,
        temporal_context: Optional[Dict[str, Any]] = None,
        graph_context: Optional[Dict[str, Any]] = None,
        message_text: Optional[str] = None,
        message_summary: Optional[str] = None,
        requested_actions: Optional[List[str]] = None,
        family_hypotheses: Optional[Dict[str, float]] = None,
        evidence_ids: Optional[List[str]] = None,
    ) -> ScamDNA:
        """Builds and indexes a ScamDNA instance for an incident."""
        dna = ScamDNABuilder.build(
            incident_id=incident_id,
            journey=journey,
            tactics=tactics,
            entities=entities,
            payment_context=payment_context,
            infrastructure=infrastructure,
            temporal_context=temporal_context,
            graph_context=graph_context,
            message_text=message_text,
            message_summary=message_summary,
            requested_actions=requested_actions,
            family_hypotheses=family_hypotheses,
            evidence_ids=evidence_ids,
        )

        self.dna_store[dna.dna_id] = dna
        self.incident_dna_map[incident_id] = dna.dna_id
        self.candidate_index.index_dna(dna)

        return dna

    def get_dna_by_incident(self, incident_id: str) -> Optional[ScamDNA]:
        """Retrieves the latest ScamDNA for an incident."""
        dna_id = self.incident_dna_map.get(incident_id)
        return self.dna_store.get(dna_id) if dna_id else None

    def get_dna(self, dna_id: str) -> Optional[ScamDNA]:
        """Retrieves ScamDNA by DNA ID."""
        return self.dna_store.get(dna_id)

    def compare_incidents(self, incident_id_1: str, incident_id_2: str) -> Optional[ScamDNAMatch]:
        """Compares two incidents using their ScamDNA signatures."""
        dna1 = self.get_dna_by_incident(incident_id_1)
        dna2 = self.get_dna_by_incident(incident_id_2)
        if not dna1 or not dna2:
            return None
        return self.similarity_engine.compare(dna1, dna2)

    def find_similar_patterns(self, incident_id: str, top_k: int = 5) -> List[ScamDNAMatch]:
        """Retrieves most similar known patterns or variant incidents for an incident."""
        dna = self.get_dna_by_incident(incident_id)
        if not dna:
            return []
        return self.candidate_index.find_similar(dna, top_k=top_k)

    def serialize_consumer_view(self, incident_id: str, target_incident_id: Optional[str] = None) -> Optional[ConsumerDNAView]:
        """Returns consumer-friendly explanation."""
        dna = self.get_dna_by_incident(incident_id)
        if not dna:
            return None
        
        match = None
        if target_incident_id:
            match = self.compare_incidents(incident_id, target_incident_id)
        else:
            similar = self.find_similar_patterns(incident_id, top_k=1)
            match = similar[0] if similar else None

        if not match:
            # Generate self-descriptive match
            match = self.similarity_engine.compare(dna, dna)

        return DNASerializer.serialize_consumer_view(dna, match)

    def serialize_analyst_view(self, incident_id: str, target_incident_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Returns full forensic analyst telemetry."""
        dna = self.get_dna_by_incident(incident_id)
        if not dna:
            return None
        
        match = None
        if target_incident_id:
            match = self.compare_incidents(incident_id, target_incident_id)
        return DNASerializer.serialize_analyst_view(dna, match)
