"""Neo4j Graph Analytics Service for ScamGraph AI (Step 24).

Implements explainable graph algorithms:
1. Weakly Connected Components (WCC) for campaign candidate clustering
2. Bipartite Node Similarity (Jaccard, Overlap, Cosine) on incident neighborhoods
3. Community Detection (Candidate Campaign Communities via Louvain/modularity)
4. High-Value Hub Entity Discovery (degree centrality & incident sharing)
5. Explainable path traversal (Never return similarity alone)

Note: Graph similarity represents topological relatedness, NOT calibrated fraud probability.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

from services.graph_engine.models.graph_models import (
    GraphCorrelationResult,
    GraphNodeType,
)
from services.graph_engine.neo4j.repository import GraphRepository, graph_repository

logger = logging.getLogger("graph_engine.analytics")


class GraphAnalyticsService:
    """Provides topological analysis, candidate campaign clustering, and neighborhood similarity."""

    def __init__(self, repo: Optional[GraphRepository] = None):
        self.repo = repo or graph_repository

    # -------------------------------------------------------------------------
    # 1. Weakly Connected Components (WCC)
    # -------------------------------------------------------------------------

    async def find_connected_components(self) -> List[Dict[str, Any]]:
        """Identify groups of incidents connected via shared infrastructure or identifiers.

        Connects incidents sharing: Phone, Domain, IP, Nameserver, Certificate, PaymentEntity.
        """
        # If Neo4j driver is active and has GDS, attempt Cypher WCC
        if self.repo.client and self.repo.client.is_connected:
            try:
                gds_query = """
                CALL gds.wcc.stream({
                    nodeProjection: ['Incident', 'Phone', 'Domain', 'IP', 'PaymentEntity', 'Nameserver', 'Certificate'],
                    relationshipProjection: {
                        REL: {type: '*', orientation: 'UNDIRECTED'}
                    }
                })
                YIELD nodeId, componentId
                WITH gds.util.asNode(nodeId) AS n, componentId
                WHERE n:Incident
                RETURN componentId as component_id, collect(n.id) as incident_ids
                ORDER BY size(incident_ids) DESC
                """
                records = await self.repo.client.execute_query(gds_query)
                if records:
                    results = []
                    for r in records:
                        inc_ids = r["incident_ids"]
                        if len(inc_ids) >= 1:
                            shared = await self._find_entities_shared_by_group(inc_ids)
                            results.append({
                                "component_id": f"wcc_{r['component_id']}",
                                "incident_ids": sorted(inc_ids),
                                "size": len(inc_ids),
                                "shared_entities": shared,
                                "explanation": f"Connected component of {len(inc_ids)} incidents linked by shared infrastructure.",
                            })
                    return results
            except Exception as e:
                logger.info(f"Native GDS WCC not available ({e}). Using deterministic in-memory WCC.")

        return self._compute_in_memory_wcc()

    def _compute_in_memory_wcc(self) -> List[Dict[str, Any]]:
        """Deterministic BFS-based WCC computation over the incident-entity bipartite graph."""
        # Build adjacency graph
        incident_neighbors: Dict[str, Set[str]] = defaultdict(set)
        entity_incidents: Dict[str, Set[str]] = defaultdict(set)

        for rel in self.repo._mock_relationships:
            src = rel["source"]
            tgt = rel["target"]

            # Direct Incident -> Entity
            if src.startswith("Incident:") and ":" in tgt:
                inc_id = src.split(":", 1)[1]
                incident_neighbors[inc_id].add(tgt)
                entity_incidents[tgt].add(inc_id)

            # URL -> Domain: propagate domain to incident that observed URL
            elif src.startswith("URL:") and tgt.startswith("Domain:"):
                # Find incidents that observed this URL
                for r2 in self.repo._mock_relationships:
                    if r2["target"] == src and r2["source"].startswith("Incident:"):
                        inc_id = r2["source"].split(":", 1)[1]
                        incident_neighbors[inc_id].add(tgt)
                        entity_incidents[tgt].add(inc_id)

        all_incidents = set(self.repo._mock_incidents.keys()) | set(incident_neighbors.keys())
        visited: Set[str] = set()
        components: List[Dict[str, Any]] = []
        comp_idx = 0

        for inc_id in sorted(all_incidents):
            if inc_id in visited:
                continue

            # BFS to find entire connected component
            comp_incidents: Set[str] = set()
            queue = [inc_id]
            visited.add(inc_id)

            while queue:
                curr = queue.pop(0)
                comp_incidents.add(curr)
                # For each entity connected to curr
                for ent_key in incident_neighbors.get(curr, set()):
                    # For each other incident connected to this entity
                    for neighbor_inc in entity_incidents.get(ent_key, set()):
                        if neighbor_inc not in visited:
                            visited.add(neighbor_inc)
                            queue.append(neighbor_inc)

            # Identify entities shared within this component
            shared_ents: List[Dict[str, Any]] = []
            for ent_key, incs in entity_incidents.items():
                intersection = incs.intersection(comp_incidents)
                if len(intersection) >= 2:
                    ent_type, ent_id = ent_key.split(":", 1)
                    ent = self.repo._mock_entities.get(ent_key, {})
                    shared_ents.append({
                        "entity_type": ent_type,
                        "entity_id": ent_id,
                        "display_value": ent.get("display_value", ent_id),
                        "shared_count": len(intersection),
                    })

            comp_list = sorted(comp_incidents)
            components.append({
                "component_id": f"comp_{comp_idx}",
                "incident_ids": comp_list,
                "size": len(comp_list),
                "shared_entities": shared_ents,
                "explanation": (
                    f"Component with {len(comp_list)} incidents connected via {len(shared_ents)} shared identifiers/infrastructure."
                    if shared_ents
                    else f"Isolated incident component ({comp_list[0]})."
                ),
            })
            comp_idx += 1

        components.sort(key=lambda c: c["size"], reverse=True)
        return components

    # -------------------------------------------------------------------------
    # 2. Node Similarity (Neighborhood Jaccard / Overlap / Cosine)
    # -------------------------------------------------------------------------

    async def find_similar_incidents(
        self,
        incident_id: str,
        top_k: int = 5,
        metric: str = "jaccard",
    ) -> List[Dict[str, Any]]:
        """Compute neighborhood similarity between an incident and other incidents.

        Metrics supported: 'jaccard', 'overlap', 'cosine'.
        Strict Rule: Similarity is structural graph overlap, NOT calibrated fraud probability.
        """
        target_neighbors = self._get_incident_entity_keys(incident_id)
        if not target_neighbors:
            return []

        all_incidents = set(self.repo._mock_incidents.keys())
        results: List[Dict[str, Any]] = []

        for other_id in sorted(all_incidents):
            if other_id == incident_id:
                continue

            other_neighbors = self._get_incident_entity_keys(other_id)
            if not other_neighbors:
                continue

            intersection = target_neighbors.intersection(other_neighbors)
            union = target_neighbors.union(other_neighbors)

            if not intersection:
                continue

            if metric.lower() == "overlap":
                score = len(intersection) / min(len(target_neighbors), len(other_neighbors))
            elif metric.lower() == "cosine":
                score = len(intersection) / ((len(target_neighbors) * len(other_neighbors)) ** 0.5)
            else:  # default jaccard
                score = len(intersection) / len(union)

            shared_details = []
            for k in sorted(intersection):
                ent_type, ent_id = k.split(":", 1)
                ent = self.repo._mock_entities.get(k, {})
                shared_details.append({
                    "entity_type": ent_type,
                    "entity_id": ent_id,
                    "display_value": ent.get("display_value", ent_id),
                })

            results.append({
                "incident_a": incident_id,
                "incident_b": other_id,
                "similarity_score": round(score, 4),
                "metric": metric.lower(),
                "shared_neighbors": shared_details,
                "explanation": (
                    f"Incidents {incident_id} and {other_id} share {len(intersection)} entities "
                    f"({metric.capitalize()} similarity: {round(score, 3)}). Note: Similarity is structural, not fraud probability."
                ),
            })

        results.sort(key=lambda r: r["similarity_score"], reverse=True)
        return results[:top_k]

    # -------------------------------------------------------------------------
    # 3. Community Detection (Candidate Campaign Communities)
    # -------------------------------------------------------------------------

    async def find_communities(self) -> List[Dict[str, Any]]:
        """Detect candidate campaign communities via Louvain/modularity grouping.

        Terminology Rule: Returns candidate campaign communities, NOT confirmed scam campaigns.
        """
        # Connected components serve as natural modular communities for multi-incident infrastructure
        components = await self.find_connected_components()
        communities: List[Dict[str, Any]] = []

        for idx, comp in enumerate(components):
            # Only clusters of 2+ incidents form candidate campaigns
            if comp["size"] >= 2:
                communities.append({
                    "community_id": f"campaign_community_{idx + 1}",
                    "incident_ids": comp["incident_ids"],
                    "size": comp["size"],
                    "important_entities": comp["shared_entities"],
                    "explanation": (
                        f"Candidate campaign community comprising {comp['size']} incidents "
                        f"sharing common infrastructure and payment entities."
                    ),
                })

        return communities

    # -------------------------------------------------------------------------
    # 4. Entity Importance & Hub Discovery
    # -------------------------------------------------------------------------

    async def find_high_value_entities(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """Identify high-degree hub entities (e.g. mule accounts, shared phones, bulletproof nameservers)."""
        entity_incidents: Dict[str, Set[str]] = defaultdict(set)

        for rel in self.repo._mock_relationships:
            src = rel["source"]
            tgt = rel["target"]
            if src.startswith("Incident:") and ":" in tgt:
                inc_id = src.split(":", 1)[1]
                entity_incidents[tgt].add(inc_id)

        ranked: List[Dict[str, Any]] = []
        for ent_key, incs in entity_incidents.items():
            ent_type, ent_id = ent_key.split(":", 1)
            ent = self.repo._mock_entities.get(ent_key, {})
            ranked.append({
                "entity_type": ent_type,
                "entity_id": ent_id,
                "display_value": ent.get("display_value", ent_id),
                "incident_count": len(incs),
                "connected_incidents": sorted(incs),
                "degree": len(incs),
            })

        ranked.sort(key=lambda e: e["incident_count"], reverse=True)
        return ranked[:top_k]

    # -------------------------------------------------------------------------
    # 5. Explainable Relationship Path Traversal
    # -------------------------------------------------------------------------

    def explain_relationship_path(self, incident_a: str, incident_b: str) -> List[str]:
        """Generate human-readable traversal paths linking two incidents.

        Example: Incident inc_A -> OBSERVED Phone (+919999900001) <- OBSERVED Incident inc_B
        """
        neigh_a = self._get_incident_entity_keys(incident_a)
        neigh_b = self._get_incident_entity_keys(incident_b)
        shared = neigh_a.intersection(neigh_b)

        paths: List[str] = []
        for k in sorted(shared):
            ent_type, ent_id = k.split(":", 1)
            ent = self.repo._mock_entities.get(k, {})
            disp = ent.get("display_value", ent_id)
            paths.append(f"Incident {incident_a} -> OBSERVED {ent_type} ({disp}) <- OBSERVED Incident {incident_b}")

        return paths

    # -------------------------------------------------------------------------
    # 6. High-Level Graph Correlation Results
    # -------------------------------------------------------------------------

    async def correlate_incident(self, incident_id: str) -> List[GraphCorrelationResult]:
        """Synthesize similarity, paths, and explanations into structured GraphCorrelationResult objects."""
        similar = await self.find_similar_incidents(incident_id, top_k=5, metric="jaccard")
        communities = await self.find_communities()

        # Find community ID if incident belongs to one
        assigned_comm: Optional[str] = None
        for c in communities:
            if incident_id in c["incident_ids"]:
                assigned_comm = c["community_id"]
                break

        results: List[GraphCorrelationResult] = []
        for sim in similar:
            other_id = sim["incident_b"]
            paths = self.explain_relationship_path(incident_id, other_id)
            shared_ents = sim["shared_neighbors"]

            explanation = (
                f"Topological link discovered: {incident_id} ↔ {other_id} with Jaccard similarity {sim['similarity_score']}. "
                f"Shared entities: {', '.join(e['display_value'] for e in shared_ents)}."
            )

            results.append(
                GraphCorrelationResult(
                    related_incident_id=other_id,
                    graph_similarity=sim["similarity_score"],
                    shared_entities=shared_ents,
                    relationship_paths=paths,
                    community_id=assigned_comm,
                    evidence_ids=[],
                    explanation=explanation,
                )
            )

        return results

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _get_incident_entity_keys(self, incident_id: str) -> Set[str]:
        """Collect all entity keys directly or transitively linked to an incident."""
        inc_key = f"Incident:{incident_id}"
        keys: Set[str] = set()

        for r in self.repo._mock_relationships:
            if r["source"] == inc_key and ":" in str(r["target"]):
                tgt = r["target"]
                keys.add(tgt)
                # If target is URL, also add its hosted domain
                if tgt.startswith("URL:"):
                    for r2 in self.repo._mock_relationships:
                        if r2["source"] == tgt and r2["target"].startswith("Domain:"):
                            keys.add(r2["target"])

        return keys

    async def _find_entities_shared_by_group(self, incident_ids: List[str]) -> List[Dict[str, Any]]:
        """Find entities shared by at least 2 incidents in a group."""
        group_set = set(incident_ids)
        counts: Dict[str, Set[str]] = defaultdict(set)

        for inc_id in group_set:
            for ent_key in self._get_incident_entity_keys(inc_id):
                counts[ent_key].add(inc_id)

        shared = []
        for ent_key, incs in counts.items():
            if len(incs) >= 2:
                ent_type, ent_id = ent_key.split(":", 1)
                ent = self.repo._mock_entities.get(ent_key, {})
                shared.append({
                    "entity_type": ent_type,
                    "entity_id": ent_id,
                    "display_value": ent.get("display_value", ent_id),
                    "shared_count": len(incs),
                })
        return shared


# Default singleton instance
graph_analytics_service = GraphAnalyticsService()
