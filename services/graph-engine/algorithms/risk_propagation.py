"""Explainable Graph Risk Propagation with Geometric Decay (Module C).

Propagates fraud risk from verified registry reports or incident seeds across
the graph with transparent distance decay (lambda), relationship weighting,
and dispute/revocation responsiveness.
"""

from __future__ import annotations

import math
from collections import deque
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

from packages.schemas.graph_correlation import (
    CorrelationEdgeType,
    CorrelationNodeType,
    GraphNode,
    PropagatedNodeRisk,
    RiskPropagationRequest,
    RiskPropagationResponse,
)
from services.graph_engine.correlation.transaction_graph import (
    TransactionGraphEngine,
    get_transaction_graph_engine,
)

RELATIONSHIP_WEIGHTS: Dict[CorrelationEdgeType, float] = {
    CorrelationEdgeType.LINKED_TO_REPORT: 1.0,
    CorrelationEdgeType.INVOLVED_IN_INCIDENT: 0.95,
    CorrelationEdgeType.SENT_TO: 0.90,
    CorrelationEdgeType.USES_IDENTIFIER: 0.85,
    CorrelationEdgeType.USED_DEVICE: 0.75,
    CorrelationEdgeType.ACCESSED_FROM: 0.60,
    CorrelationEdgeType.ASSOCIATED_WITH: 0.50,
}


class GraphRiskPropagator:
    """Calculates explainable risk propagation over graph topology."""

    def __init__(self, engine: Optional[TransactionGraphEngine] = None):
        self.engine = engine or get_transaction_graph_engine()

    def propagate_risk(self, req: RiskPropagationRequest) -> RiskPropagationResponse:
        """Propagate risk from seed nodes with geometric distance decay."""
        now = datetime.now(timezone.utc)
        results: Dict[str, PropagatedNodeRisk] = {}

        queue: deque[Tuple[str, int, float, List[str]]] = deque()
        visited_depth: Dict[str, int] = {}

        for seed_id in req.seed_node_ids:
            seed_node = self.engine.get_node(seed_id)
            if not seed_node:
                continue

            seed_risk = seed_node.direct_risk if seed_node.direct_risk > 0 else seed_node.risk_score
            if seed_risk <= 0:
                seed_risk = 0.90

            if seed_node.is_revoked:
                continue

            if seed_node.is_disputed:
                seed_risk = round(seed_risk * 0.5, 3)

            queue.append((seed_id, 0, seed_risk, [f"Seed: {seed_node.label} ({seed_id})"]))
            visited_depth[seed_id] = 0

            results[seed_id] = PropagatedNodeRisk(
                node_id=seed_id,
                node_type=seed_node.node_type,
                hops_from_seed=0,
                direct_risk=seed_node.direct_risk or seed_risk,
                propagated_risk=0.0,
                total_risk=seed_risk,
                contributing_seed_ids=[seed_id],
                path_explanation=[f"Direct verified seed indicator: {seed_node.label}"],
            )

        while queue:
            curr_id, hops, strength, path = queue.popleft()

            if hops >= req.max_hops:
                continue

            neighbors = self.engine.get_neighbors(curr_id)
            all_edges = neighbors["outgoing"] + neighbors["incoming"]

            for edge in all_edges:
                if not edge.is_valid:
                    continue

                neighbor_id = edge.target_id if edge.source_id == curr_id else edge.source_id
                next_hops = hops + 1

                w_edge = RELATIONSHIP_WEIGHTS.get(edge.relationship_type, 0.7)
                next_strength = round(strength * req.decay_factor * w_edge, 3)

                if next_strength < 0.05:
                    continue

                edge_desc = f"{curr_id} -[{edge.relationship_type.value}]-> {neighbor_id}"
                next_path = path + [edge_desc]

                neighbor_node = self.engine.get_node(neighbor_id)
                n_type = neighbor_node.node_type if neighbor_node else CorrelationNodeType.ACCOUNT

                if neighbor_id not in results:
                    direct_r = neighbor_node.direct_risk if neighbor_node else 0.0
                    results[neighbor_id] = PropagatedNodeRisk(
                        node_id=neighbor_id,
                        node_type=n_type,
                        hops_from_seed=next_hops,
                        direct_risk=direct_r,
                        propagated_risk=next_strength,
                        total_risk=round(min(1.0, direct_r + next_strength), 3),
                        contributing_seed_ids=[path[0].split("(")[-1].rstrip(")")],
                        path_explanation=next_path,
                    )
                    queue.append((neighbor_id, next_hops, next_strength, next_path))
                    visited_depth[neighbor_id] = next_hops
                else:
                    existing = results[neighbor_id]
                    if next_strength > existing.propagated_risk:
                        existing.propagated_risk = next_strength
                        existing.total_risk = round(min(1.0, existing.direct_risk + next_strength), 3)
                        existing.hops_from_seed = min(existing.hops_from_seed, next_hops)
                        existing.path_explanation = next_path

        return RiskPropagationResponse(
            evaluated_at=now,
            decay_factor_used=req.decay_factor,
            seeds_processed=len(req.seed_node_ids),
            affected_nodes_count=len(results),
            nodes=list(results.values()),
        )


# Global instance
graph_risk_propagator = GraphRiskPropagator()


def get_graph_risk_propagator() -> GraphRiskPropagator:
    """Dependency provider."""
    return graph_risk_propagator
