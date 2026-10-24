"""Entity Relationship & Edge Graph Manager for ScamGraph AI V2 (Prompt 6).

Responsibilities:
1. Idempotent creation and updating of EntityRelationship records
2. Multi-hop traversal across shared infrastructure
3. Correlating incidents sharing phone, domain, UPI, or Telegram accounts
4. Strictly disallowing unsupported criminal attribution edges (NEVER SAME_CRIMINAL)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from packages.schemas.entity import (
    EntityRelationship,
    EntityRelationshipType,
    EntityVerificationState,
)


class EntityRelationshipManager:
    """Manages directed evidence-backed relationships between canonical entities."""

    def __init__(self):
        # Keyed by relationship_id
        self._relationships: Dict[str, EntityRelationship] = {}
        # Keyed by (source_id, target_id, rel_type) -> relationship_id (for idempotency)
        self._edge_index: Dict[Tuple[str, str, EntityRelationshipType], str] = {}
        # Adjacency lists for fast bidirectional traversal
        self._out_edges: Dict[str, Set[str]] = {}  # entity_id -> set of relationship_ids
        self._in_edges: Dict[str, Set[str]] = {}

    def link_entities(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: EntityRelationshipType,
        evidence_id: Optional[str] = None,
        confidence: float = 1.0,
        created_by: str = "RULE",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EntityRelationship:
        """Idempotently links two entities with evidence and confidence."""
        if source_entity_id == target_entity_id:
            # Self-loops disallowed
            raise ValueError("Cannot create self-referencing relationship edge")

        key = (source_entity_id, target_entity_id, relationship_type)
        now = datetime.now(timezone.utc)

        if key in self._edge_index:
            rel_id = self._edge_index[key]
            rel = self._relationships[rel_id]
            rel.observation_count += 1
            rel.last_seen = now
            if evidence_id and evidence_id not in rel.evidence_ids:
                rel.evidence_ids.append(evidence_id)
            if metadata:
                rel.metadata.update(metadata)
            return rel

        # Create new relationship
        evidence_list = [evidence_id] if evidence_id else []
        rel = EntityRelationship(
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            first_seen=now,
            last_seen=now,
            observation_count=1,
            evidence_ids=evidence_list,
            confidence=confidence,
            verification_state=EntityVerificationState.OBSERVED,
            created_by=created_by,
            metadata=metadata or {},
        )

        self._relationships[rel.relationship_id] = rel
        self._edge_index[key] = rel.relationship_id

        self._out_edges.setdefault(source_entity_id, set()).add(rel.relationship_id)
        self._in_edges.setdefault(target_entity_id, set()).add(rel.relationship_id)

        return rel

    def get_relationships_for_entity(
        self,
        entity_id: str,
        direction: str = "BOTH",  # "OUT", "IN", "BOTH"
    ) -> List[EntityRelationship]:
        """Retrieves active relationships connected to an entity."""
        rel_ids: Set[str] = set()
        if direction in ("OUT", "BOTH"):
            rel_ids.update(self._out_edges.get(entity_id, set()))
        if direction in ("IN", "BOTH"):
            rel_ids.update(self._in_edges.get(entity_id, set()))

        return [self._relationships[rid] for rid in rel_ids if rid in self._relationships]

    def find_connected_entities(
        self,
        start_entity_id: str,
        max_depth: int = 2,
    ) -> Dict[str, int]:
        """Multi-hop breadth-first traversal finding connected entities and distance."""
        visited: Dict[str, int] = {start_entity_id: 0}
        queue = [(start_entity_id, 0)]

        while queue:
            curr_id, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            rels = self.get_relationships_for_entity(curr_id, direction="BOTH")
            for r in rels:
                neighbor = r.target_entity_id if r.source_entity_id == curr_id else r.source_entity_id
                if neighbor not in visited:
                    visited[neighbor] = depth + 1
                    queue.append((neighbor, depth + 1))

        # Remove start entity from results
        visited.pop(start_entity_id, None)
        return visited

    def __len__(self) -> int:
        return len(self._relationships)
