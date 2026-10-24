"""Entity Resolution Engine for ScamGraph AI V2 (Prompt 6).

Responsibilities:
1. Exact normalized match via canonical hash
2. Strong deterministic alias resolution
3. Fuzzy candidate generation with review flag (NO AUTOMATIC MERGE of fuzzy candidates)
4. Lineage-preserving merge & reversible split
"""

from __future__ import annotations

import difflib
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from packages.schemas.entity import (
    Entity,
    EntityMergeRecord,
    EntitySplitRecord,
    EntityType,
    EntityVerificationState,
)
from services.entity_intelligence.normalizer import NormalizedEntityResult


class ResolutionMatchType(str, Enum):
    """Categorized resolution outcome."""
    EXACT_MATCH = "EXACT_MATCH"
    STRONG_MATCH = "STRONG_MATCH"
    POSSIBLE_MATCH = "POSSIBLE_MATCH"
    NO_MATCH = "NO_MATCH"
    CONFLICT = "CONFLICT"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class ResolutionResult(BaseModel):
    """Decision output from EntityResolutionEngine."""
    match_type: ResolutionMatchType
    matched_entity_id: Optional[str] = None
    candidate_entity_ids: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    explanation: str = ""
    requires_human_review: bool = False


class EntityResolutionEngine:
    """In-memory and repository-compatible entity resolution engine."""

    def __init__(self, entities_index: Optional[Dict[str, Entity]] = None):
        # Index keyed by entity_id
        self._entities: Dict[str, Entity] = entities_index or {}
        # Index keyed by canonical_hash -> entity_id
        self._hash_index: Dict[str, str] = {}
        # Index keyed by alias -> canonical entity_id
        self._alias_index: Dict[str, str] = {}

        # Rebuild indexes
        for eid, ent in self._entities.items():
            self._hash_index[ent.canonical_hash] = eid
            for alias in ent.aliases:
                self._alias_index[alias.lower()] = eid

    def index_entity(self, entity: Entity) -> None:
        """Adds or updates an entity in the resolution indexes."""
        self._entities[entity.entity_id] = entity
        self._hash_index[entity.canonical_hash] = entity.entity_id
        if entity.canonical_value:
            self._alias_index[entity.canonical_value.lower()] = entity.entity_id
        for alias in entity.aliases:
            self._alias_index[alias.lower()] = entity.entity_id

    def resolve(self, norm_result: NormalizedEntityResult) -> ResolutionResult:
        """Resolves a normalized entity against known canonical entities.
        
        Rule: Exact hash match = EXACT_MATCH.
        Known alias match = STRONG_MATCH.
        Fuzzy match = POSSIBLE_MATCH (never auto-merged!).
        """
        # 1. Exact canonical hash match
        if norm_result.canonical_hash in self._hash_index:
            eid = self._hash_index[norm_result.canonical_hash]
            return ResolutionResult(
                match_type=ResolutionMatchType.EXACT_MATCH,
                matched_entity_id=eid,
                candidate_entity_ids=[eid],
                confidence=1.0,
                explanation="Exact match on canonical cryptographic hash.",
                requires_human_review=False,
            )

        # 2. Strong alias match
        norm_val = (norm_result.normalized_value or "").lower()
        if norm_val in self._alias_index:
            eid = self._alias_index[norm_val]
            return ResolutionResult(
                match_type=ResolutionMatchType.STRONG_MATCH,
                matched_entity_id=eid,
                candidate_entity_ids=[eid],
                confidence=0.95,
                explanation="Resolved via verified canonical alias index.",
                requires_human_review=False,
            )

        # 3. Fuzzy candidate generation (for domains, usernames, VPAs)
        # CRITICAL RULE: DO NOT automatically merge fuzzy candidates!
        fuzzy_candidates: List[Tuple[str, float]] = []
        for eid, ent in self._entities.items():
            if ent.entity_type != norm_result.entity_type:
                continue
            if not ent.canonical_value or not norm_val:
                continue

            # Compute character sequence similarity ratio
            sim = difflib.SequenceMatcher(None, norm_val, ent.canonical_value.lower()).ratio()
            if sim >= 0.88 and sim < 1.0:
                fuzzy_candidates.append((eid, sim))

        if fuzzy_candidates:
            # Sort by similarity descending
            fuzzy_candidates.sort(key=lambda x: x[1], reverse=True)
            candidate_ids = [c[0] for c in fuzzy_candidates[:3]]
            top_sim = fuzzy_candidates[0][1]

            return ResolutionResult(
                match_type=ResolutionMatchType.POSSIBLE_MATCH,
                matched_entity_id=None,  # No auto-merge!
                candidate_entity_ids=candidate_ids,
                confidence=round(top_sim, 3),
                explanation=f"High lexical similarity ({top_sim:.1%}) with existing entities; requires human review before merge.",
                requires_human_review=True,
            )

        # 4. No Match
        return ResolutionResult(
            match_type=ResolutionMatchType.NO_MATCH,
            matched_entity_id=None,
            candidate_entity_ids=[],
            confidence=1.0,
            explanation="New unique entity identifier.",
            requires_human_review=False,
        )

    def merge_entities(
        self,
        canonical_entity_id: str,
        target_entity_ids: List[str],
        reason: str,
        evidence_ids: Optional[List[str]] = None,
    ) -> EntityMergeRecord:
        """Consolidates target entities into canonical entity while strictly preserving lineage (Prompt 6)."""
        canonical = self._entities.get(canonical_entity_id)
        if not canonical:
            raise ValueError(f"Canonical entity {canonical_entity_id} not found")

        merged_ids: List[str] = []
        for tid in target_entity_ids:
            if tid == canonical_entity_id:
                continue
            target = self._entities.get(tid)
            if not target:
                continue

            # Consolidate observation and incident counts
            canonical.observation_count += target.observation_count
            canonical.incident_count += target.incident_count
            canonical.supporting_evidence_count += target.supporting_evidence_count
            canonical.contradicting_evidence_count += target.contradicting_evidence_count

            # Add target aliases and canonical value
            if target.canonical_value and target.canonical_value not in canonical.aliases:
                canonical.aliases.append(target.canonical_value)
            canonical.aliases.append(tid)  # link previous entity ID
            for a in target.aliases:
                if a not in canonical.aliases:
                    canonical.aliases.append(a)

            # Update alias index to point target to canonical
            if target.canonical_value:
                self._alias_index[target.canonical_value.lower()] = canonical_entity_id
            self._hash_index[target.canonical_hash] = canonical_entity_id
            merged_ids.append(tid)

        record = EntityMergeRecord(
            canonical_entity_id=canonical_entity_id,
            merged_entity_ids=merged_ids,
            reason=reason,
            evidence_ids=evidence_ids or [],
            can_split=True,
        )
        return record

    def split_entity(
        self,
        merge_record: EntityMergeRecord,
        reason: str,
    ) -> EntitySplitRecord:
        """Reverses an entity consolidation, restoring independent entity lineages."""
        canonical = self._entities.get(merge_record.canonical_entity_id)
        if not canonical:
            raise ValueError(f"Canonical entity {merge_record.canonical_entity_id} not found")

        # Remove aliases pointing to the merged entities
        for mid in merge_record.merged_entity_ids:
            if mid in canonical.aliases:
                canonical.aliases.remove(mid)

        return EntitySplitRecord(
            original_entity_id=merge_record.canonical_entity_id,
            resulting_entity_ids=merge_record.merged_entity_ids,
            reason=reason,
        )
