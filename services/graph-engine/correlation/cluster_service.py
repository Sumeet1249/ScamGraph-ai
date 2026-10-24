"""Suspicious Cluster & Community Detection Service (Module C).

Detects connected components, shared infrastructure clusters, and money mule rings.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, List, Optional, Set
from uuid import uuid4

from packages.schemas.graph_correlation import (
    ClusterQueryRequest,
    ClusterQueryResponse,
    ClusterSummary,
    CorrelationEdgeType,
    CorrelationNodeType,
    GraphEdge,
    GraphNode,
)
from services.graph_engine.correlation.transaction_graph import (
    TransactionGraphEngine,
    get_transaction_graph_engine,
)


class GraphClusterService:
    """Detects suspicious communities and shared-infrastructure clusters."""

    def __init__(self, engine: Optional[TransactionGraphEngine] = None):
        self.engine = engine or get_transaction_graph_engine()

    def detect_clusters(self, req: ClusterQueryRequest) -> ClusterQueryResponse:
        """Find connected components and shared identifier rings."""
        visited: Set[str] = set()
        clusters: List[ClusterSummary] = []

        all_node_ids = list(self.engine._nodes.keys())

        for start_id in all_node_ids:
            if start_id in visited:
                continue

            # BFS to find connected component
            comp_node_ids: List[str] = []
            comp_edges: List[GraphEdge] = []
            queue = deque([start_id])
            visited.add(start_id)

            while queue:
                curr = queue.popleft()
                comp_node_ids.append(curr)

                neighbors = self.engine.get_neighbors(curr)
                all_adjacent = neighbors["outgoing"] + neighbors["incoming"]

                for edge in all_adjacent:
                    if edge not in comp_edges:
                        comp_edges.append(edge)

                    neighbor_id = edge.target_id if edge.source_id == curr else edge.source_id
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        queue.append(neighbor_id)

            if len(comp_node_ids) >= req.min_cluster_size:
                comp_nodes = [self.engine.get_node(nid) for nid in comp_node_ids if self.engine.get_node(nid)]

                # Check if cluster contains shared identifiers
                id_nodes = [n for n in comp_nodes if n.node_type in (CorrelationNodeType.PHONE, CorrelationNodeType.DEVICE, CorrelationNodeType.IP)]
                acc_nodes = [n for n in comp_nodes if n.node_type in (CorrelationNodeType.ACCOUNT, CorrelationNodeType.UPI_VPA)]
                reports = [n for n in comp_nodes if n.node_type == CorrelationNodeType.REPORT]

                if id_nodes and len(acc_nodes) >= 2:
                    cluster_type = "SHARED_IDENTIFIER_RING"
                    reason = f"{len(acc_nodes)} accounts share infrastructure ({len(id_nodes)} shared identifiers)."
                    score = min(0.95, 0.60 + 0.10 * len(id_nodes))
                elif reports:
                    cluster_type = "REGISTRY_LINKED_CLUSTER"
                    reason = f"Cluster linked to {len(reports)} active Smart Registry reports."
                    score = 0.90
                else:
                    cluster_type = "CONNECTED_COMPONENT"
                    reason = f"Topologically connected group of {len(comp_nodes)} entities with {len(comp_edges)} transactions."
                    score = 0.65

                clusters.append(
                    ClusterSummary(
                        cluster_id=f"cluster_{uuid4().hex[:8]}",
                        cluster_type=cluster_type,
                        node_count=len(comp_nodes),
                        edge_count=len(comp_edges),
                        nodes=comp_nodes,
                        edges=comp_edges,
                        suspicion_score=round(score, 2),
                        reason=reason,
                        related_report_ids=[r.id for r in reports],
                    )
                )

        clusters.sort(key=lambda c: c.suspicion_score, reverse=True)
        return ClusterQueryResponse(
            total_clusters=len(clusters),
            clusters=clusters[: req.limit],
        )


# Global instance
graph_cluster_service = GraphClusterService()


def get_graph_cluster_service() -> GraphClusterService:
    """Dependency provider."""
    return graph_cluster_service
