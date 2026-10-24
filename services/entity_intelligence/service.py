"""Unified Entity Intelligence Service for ScamGraph AI V2 (Prompt 6).

Coordinates:
- Entity extraction from raw artifacts
- Deterministic canonical normalization
- Privacy masking and hashing
- Lineage-preserving entity resolution
- Contextual observation tracking
- Evidence-backed relationship mapping
- Authoritative directory verification
- Multi-dimensional reputation and trust assessment
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from packages.schemas.entity import (
    Entity,
    EntityClaim,
    EntityMergeRecord,
    EntityObservation,
    EntityObservationRole,
    EntityRelationship,
    EntityRelationshipType,
    EntitySplitRecord,
    EntityType,
    EntityVerificationState,
    TrustAssessment,
)
from services.entity_intelligence.extractor import EntityExtractor, ExtractedEntityCandidate
from services.entity_intelligence.normalizer import EntityNormalizer, NormalizedEntityResult
from services.entity_intelligence.privacy import AntiEnumerationGuard, PrivacySerializer
from services.entity_intelligence.relationships import EntityRelationshipManager
from services.entity_intelligence.reputation import EntityReputationEngine
from services.entity_intelligence.resolver import EntityResolutionEngine, ResolutionMatchType, ResolutionResult
from services.entity_intelligence.verification import AuthoritativeDirectoryVerificationProvider, VerificationResult

logger = logging.getLogger("scamgraph.entity_intelligence.service")


class EntityIntelligenceService:
    """Core service managing entities, observations, relationships, and trust intelligence."""

    def __init__(
        self,
        resolver: Optional[EntityResolutionEngine] = None,
        relationship_manager: Optional[EntityRelationshipManager] = None,
        reputation_engine: Optional[EntityReputationEngine] = None,
        verification_provider: Optional[AuthoritativeDirectoryVerificationProvider] = None,
    ):
        # Repositories / In-memory indexes
        self._entities: Dict[str, Entity] = {}
        self._observations: Dict[str, EntityObservation] = {}
        self._entity_observations_index: Dict[str, List[str]] = {}  # entity_id -> [obs_id, ...]
        self._incident_entities_index: Dict[str, List[str]] = {}     # incident_id -> [entity_id, ...]

        self.resolver = resolver or EntityResolutionEngine(self._entities)
        self.relationships = relationship_manager or EntityRelationshipManager()
        self.reputation = reputation_engine or EntityReputationEngine()
        self.verification = verification_provider or AuthoritativeDirectoryVerificationProvider()
        self.anti_enumeration = AntiEnumerationGuard()

    # -------------------------------------------------------------------------
    # 1. ENTITY INGESTION & RESOLUTION
    # -------------------------------------------------------------------------
    def resolve_and_upsert_entity(
        self,
        entity_type: EntityType,
        raw_value: str,
        incident_id: str,
        role: EntityObservationRole = EntityObservationRole.UNKNOWN,
        channel: str = "SMS",
        artifact_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        confidence: float = 1.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Entity, EntityObservation]:
        """Normalizes, resolves, indexes, and records an entity observation."""
        # 1. Normalize based on type
        norm_result = self._normalize_by_type(entity_type, raw_value)

        # 2. Resolve against existing canonical entities
        res = self.resolver.resolve(norm_result)

        now = datetime.now(timezone.utc)
        if res.match_type in (ResolutionMatchType.EXACT_MATCH, ResolutionMatchType.STRONG_MATCH):
            # Existing canonical entity
            entity_id = res.matched_entity_id
            entity = self._entities[entity_id]
            entity.observation_count += 1
            entity.last_seen = now
            if incident_id not in self._incident_entities_index.get(incident_id, []):
                entity.incident_count += 1
        else:
            # Create new canonical entity
            # Verify against authoritative directory if domain/url
            ver_res = self.verification.verify(entity_type, norm_result.normalized_value)

            entity = Entity(
                entity_type=entity_type,
                canonical_value=norm_result.normalized_value,
                display_value=norm_result.display_value,
                masked_value=norm_result.display_value,
                canonical_hash=norm_result.canonical_hash,
                first_seen=now,
                last_seen=now,
                observation_count=1,
                incident_count=1,
                verification_state=ver_res.verification_state if ver_res.is_verified else EntityVerificationState.OBSERVED,
                metadata={
                    "validation_status": norm_result.validation_status.value,
                    "normalization_confidence": norm_result.confidence,
                    **norm_result.extra_metadata,
                },
            )
            self._entities[entity.entity_id] = entity
            self.resolver.index_entity(entity)
            entity_id = entity.entity_id

        # 3. Create observation record
        observation = EntityObservation(
            entity_id=entity_id,
            incident_id=incident_id,
            artifact_id=artifact_id,
            channel=channel,
            role=role,
            evidence_id=evidence_id,
            confidence=confidence,
            context=context or {},
        )
        self._observations[observation.observation_id] = observation
        self._entity_observations_index.setdefault(entity_id, []).append(observation.observation_id)
        self._incident_entities_index.setdefault(incident_id, []).append(entity_id)

        return entity, observation

    def _normalize_by_type(self, entity_type: EntityType, raw_value: str) -> NormalizedEntityResult:
        """Dispatches to appropriate normalizer."""
        if entity_type == EntityType.PHONE:
            return EntityNormalizer.normalize_phone(raw_value)
        elif entity_type == EntityType.EMAIL:
            return EntityNormalizer.normalize_email(raw_value)
        elif entity_type == EntityType.DOMAIN:
            return EntityNormalizer.normalize_domain(raw_value)
        elif entity_type == EntityType.URL:
            return EntityNormalizer.normalize_url(raw_value)
        elif entity_type == EntityType.UPI_VPA:
            return EntityNormalizer.normalize_upi_vpa(raw_value)
        elif entity_type == EntityType.TELEGRAM_HANDLE:
            return EntityNormalizer.normalize_telegram_handle(raw_value)
        elif entity_type == EntityType.BRAND:
            return EntityNormalizer.normalize_brand(raw_value)
        else:
            from packages.utils.privacy import canonical_hash
            raw_clean = str(raw_value or "").strip()
            return NormalizedEntityResult(
                entity_type=entity_type,
                raw_value=raw_clean,
                normalized_value=raw_clean.lower(),
                display_value=raw_clean,
                canonical_hash=canonical_hash(raw_clean.lower()),
                validation_status=EntityNormalizer.normalize_domain(raw_clean).validation_status,
                confidence=0.8,
            )

    # -------------------------------------------------------------------------
    # 2. INCIDENT EXTRACTION & RELATIONSHIP LINKING
    # -------------------------------------------------------------------------
    def process_incident_text(
        self,
        incident_id: str,
        text: str,
        channel: str = "SMS",
        artifact_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
    ) -> List[Tuple[Entity, EntityObservation]]:
        """Extracts all entities from text and creates co-occurrence relationships."""
        candidates = EntityExtractor.extract_all(text)
        results: List[Tuple[Entity, EntityObservation]] = []
        entity_ids_in_message: List[str] = []

        for cand in candidates:
            ent, obs = self.resolve_and_upsert_entity(
                entity_type=cand.entity_type,
                raw_value=cand.raw_value,
                incident_id=incident_id,
                role=cand.suggested_role,
                channel=channel,
                artifact_id=artifact_id,
                evidence_id=evidence_id,
                confidence=cand.extraction_confidence,
                context={"span_start": cand.span_start, "span_end": cand.span_end},
            )
            results.append((ent, obs))
            if ent.entity_id not in entity_ids_in_message:
                entity_ids_in_message.append(ent.entity_id)

        # Create APPEARED_WITH relationships between co-occurring entities in the incident
        for i in range(len(entity_ids_in_message)):
            for j in range(i + 1, len(entity_ids_in_message)):
                e1 = entity_ids_in_message[i]
                e2 = entity_ids_in_message[j]
                self.relationships.link_entities(
                    source_entity_id=e1,
                    target_entity_id=e2,
                    relationship_type=EntityRelationshipType.APPEARED_WITH,
                    evidence_id=evidence_id,
                    confidence=0.90,
                    created_by="RULE_INCIDENT_CO_OCCURRENCE",
                )

        return results

    # -------------------------------------------------------------------------
    # 3. RETRIEVAL & TRUST ASSESSMENT
    # -------------------------------------------------------------------------
    def get_entity(self, entity_id: str, access_tier: str = "CONSUMER") -> Optional[Dict[str, Any]]:
        """Retrieves an entity with privacy serialization applied."""
        entity = self._entities.get(entity_id)
        if not entity:
            return None
        if access_tier == "ANALYST":
            return PrivacySerializer.serialize_for_analyst(entity)
        return PrivacySerializer.serialize_for_consumer(entity)

    def get_entity_observations(self, entity_id: str) -> List[EntityObservation]:
        """Retrieves all historical observations of an entity."""
        obs_ids = self._entity_observations_index.get(entity_id, [])
        return [self._observations[oid] for oid in obs_ids if oid in self._observations]

    def get_entity_relationships(self, entity_id: str) -> List[EntityRelationship]:
        """Retrieves all active relationships connected to an entity."""
        return self.relationships.get_relationships_for_entity(entity_id)

    def assess_entity_trust(self, entity_id: str) -> TrustAssessment:
        """Assesses evidence-aware reputation, corroboration, and decay for an entity."""
        entity = self._entities.get(entity_id)
        if not entity:
            raise ValueError(f"Entity {entity_id} not found")
        obs = self.get_entity_observations(entity_id)
        return self.reputation.assess_trust(entity, observations=obs)

    def find_related_incidents(self, entity_id: str) -> List[str]:
        """Finds all unique incident IDs connected to this entity or its direct 1-hop neighbors."""
        obs = self.get_entity_observations(entity_id)
        incidents: Set[str] = set(o.incident_id for o in obs)

        # Expand to connected 1-hop infrastructure entities (e.g. shared UPI or Domain)
        connected = self.relationships.find_connected_entities(entity_id, max_depth=1)
        for neighbor_id in connected.keys():
            neighbor_obs = self.get_entity_observations(neighbor_id)
            for nobs in neighbor_obs:
                incidents.add(nobs.incident_id)

        return sorted(list(incidents))

    def record_evidence_signal(
        self,
        entity_id: str,
        is_supporting_scam: bool = True,
    ) -> None:
        """Updates supporting or counter-evidence counters for an entity."""
        entity = self._entities.get(entity_id)
        if not entity:
            return
        if is_supporting_scam:
            entity.supporting_evidence_count += 1
        else:
            entity.contradicting_evidence_count += 1


# Global instance
entity_intelligence_service = EntityIntelligenceService()
