"""Semantic Similarity Service (Step 20).

Provides high-level retrieval over vector storage:
- find_similar_messages()
- find_similar_incidents()
- find_similar_patterns()

Crucial Invariant:
"Similarity is evidence. It is NOT fraud probability."
Matches returned provide probabilistic historical correlation, never automated verdicts.
"""

import logging
from typing import Any, Dict, List, Optional, Union
import numpy as np

from ml.embeddings.encoder import SemanticEncoder, semantic_encoder
from ml.embeddings.representation import SemanticRepresentation, SemanticRepresentationBuilder
from packages.schemas import EvidenceSignal, SignalDimension, SignalSeverity, ProvenanceRecord
from services.storage.vector.base import VectorStore
from services.storage.vector.in_memory import InMemoryVectorStore
from services.storage.vector.models import VectorObjectType, VectorRecord, VectorSearchResult

logger = logging.getLogger("scamgraph.services.vector.similarity")


class SemanticSimilarityService:
    """Orchestrates embedding generation, vector indexing, and nearest-neighbor search."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        encoder: Optional[SemanticEncoder] = None,
    ):
        self.vector_store = vector_store or InMemoryVectorStore()
        self.encoder = encoder or semantic_encoder

    async def store_message(
        self,
        message_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Embeds and indexes a user communication message."""
        vec = self.encoder.encode(text, is_query=False)
        record = VectorRecord(
            object_type=VectorObjectType.MESSAGE,
            object_id=message_id,
            model_name=self.encoder.model_name,
            model_version=self.encoder.model_version,
            embedding=vec.tolist(),
            metadata=dict(metadata or {}, text_snippet=text[:300]),
        )
        return await self.vector_store.store_embedding(record)

    async def store_incident_summary(
        self,
        incident_id: str,
        representation: Union[str, SemanticRepresentation],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Embeds and indexes a normalized incident summary representation."""
        text = representation.to_normalized_text() if isinstance(representation, SemanticRepresentation) else representation
        vec = self.encoder.encode(text, is_query=False)
        record = VectorRecord(
            object_type=VectorObjectType.INCIDENT_SUMMARY,
            object_id=incident_id,
            model_name=self.encoder.model_name,
            model_version=self.encoder.model_version,
            embedding=vec.tolist(),
            metadata=dict(metadata or {}, representation=text),
        )
        return await self.vector_store.store_embedding(record)

    async def store_pattern(
        self,
        pattern_id: str,
        representation: Union[str, SemanticRepresentation],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Embeds and indexes a known scam pattern representation."""
        text = representation.to_normalized_text() if isinstance(representation, SemanticRepresentation) else representation
        vec = self.encoder.encode(text, is_query=False)
        record = VectorRecord(
            object_type=VectorObjectType.PATTERN,
            object_id=pattern_id,
            model_name=self.encoder.model_name,
            model_version=self.encoder.model_version,
            embedding=vec.tolist(),
            metadata=dict(metadata or {}, representation=text),
        )
        return await self.vector_store.store_embedding(record)

    async def store_campaign(
        self,
        campaign_id: str,
        representation: Union[str, SemanticRepresentation],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Embeds and indexes a syndicated attack campaign representation."""
        text = representation.to_normalized_text() if isinstance(representation, SemanticRepresentation) else representation
        vec = self.encoder.encode(text, is_query=False)
        record = VectorRecord(
            object_type=VectorObjectType.CAMPAIGN,
            object_id=campaign_id,
            model_name=self.encoder.model_name,
            model_version=self.encoder.model_version,
            embedding=vec.tolist(),
            metadata=dict(metadata or {}, representation=text),
        )
        return await self.vector_store.store_embedding(record)

    async def find_similar_messages(
        self,
        message_text: str,
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        """Finds historical messages semantically similar to input message."""
        query_vec = self.encoder.encode(message_text, is_query=True)
        return await self.vector_store.find_similar(
            query_vector=query_vec.tolist(),
            object_type=VectorObjectType.MESSAGE,
            top_k=top_k,
            threshold=threshold,
        )

    async def find_similar_incidents(
        self,
        incident_representation: Union[str, SemanticRepresentation],
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        """Finds historical incidents with similar semantic lures and tactics."""
        text = (
            incident_representation.to_normalized_text()
            if isinstance(incident_representation, SemanticRepresentation)
            else incident_representation
        )
        query_vec = self.encoder.encode(text, is_query=True)
        return await self.vector_store.find_similar(
            query_vector=query_vec.tolist(),
            object_type=VectorObjectType.INCIDENT_SUMMARY,
            top_k=top_k,
            threshold=threshold,
        )

    async def find_similar_patterns(
        self,
        pattern_representation: Union[str, SemanticRepresentation],
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> List[VectorSearchResult]:
        """Matches observed interaction against catalog of known scam patterns."""
        text = (
            pattern_representation.to_normalized_text()
            if isinstance(pattern_representation, SemanticRepresentation)
            else pattern_representation
        )
        query_vec = self.encoder.encode(text, is_query=True)
        return await self.vector_store.find_similar(
            query_vector=query_vec.tolist(),
            object_type=VectorObjectType.PATTERN,
            top_k=top_k,
            threshold=threshold,
        )

    def to_evidence_signal(
        self,
        incident_id: str,
        match: VectorSearchResult,
    ) -> EvidenceSignal:
        """Converts a vector search result into a canonical EvidenceSignal.
        
        Explicitly reinforces: Similarity is evidence, NOT fraud probability.
        """
        sim_pct = round(match.similarity * 100, 1)
        severity = SignalSeverity.HIGH if match.similarity >= 0.85 else SignalSeverity.MEDIUM

        return EvidenceSignal(
            incident_id=incident_id,
            dimension=SignalDimension.SEMANTIC,
            signal_type=f"SEMANTIC_SIMILARITY_TO_{match.object_type.value}",
            severity=severity,
            confidence=round(match.similarity, 2),
            weight=1.5,
            description=(
                f"Exhibits {sim_pct}% semantic similarity to {match.object_type.value} '{match.object_id}'. "
                "Note: Similarity is historical retrieval evidence, not fraud certainty."
            ),
            provenance=ProvenanceRecord(
                source_service="services/storage/vector",
                detector_name="SemanticSimilarityService",
                target_artifact=match.object_id,
                raw_evidence={
                    "object_id": match.object_id,
                    "object_type": match.object_type.value,
                    "similarity": match.similarity,
                    "model_name": match.model_name,
                    "model_version": match.model_version,
                    "metadata": match.metadata,
                },
            ),
        )


# Global singleton instance
similarity_service_v2 = SemanticSimilarityService()
