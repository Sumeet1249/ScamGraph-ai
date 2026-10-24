"""Transaction Path Analysis & Flow Engine (Module C).

Implements multi-hop money flow tracing, circular flow cycle detection,
rapid pass-through layering identification, and fan-in/fan-out graph analytics.
"""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple
from uuid import uuid4

from packages.schemas.graph_correlation import (
    CorrelationEdgeType,
    CorrelationNodeType,
    GraphEdge,
    GraphNode,
    PathQueryRequest,
    PathQueryResponse,
    TransactionHop,
    TransactionPath,
)


class TransactionGraphEngine:
    """In-memory multi-hop graph engine for financial transaction paths."""

    def __init__(self):
        self._nodes: Dict[str, GraphNode] = {}
        # Outgoing edges: node_id -> List[GraphEdge]
        self._adj_out: Dict[str, List[GraphEdge]] = defaultdict(list)
        # Incoming edges: node_id -> List[GraphEdge]
        self._adj_in: Dict[str, List[GraphEdge]] = defaultdict(list)
        self._edges: Dict[str, GraphEdge] = {}

    def add_node(self, node: GraphNode) -> None:
        """Register a node in the graph."""
        self._nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        """Add a directed edge in the graph."""
        self._edges[edge.id] = edge
        self._adj_out[edge.source_id].append(edge)
        self._adj_in[edge.target_id].append(edge)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Fetch node by ID."""
        return self._nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> Dict[str, List[GraphEdge]]:
        """Return incoming and outgoing edges for an entity."""
        return {
            "outgoing": self._adj_out.get(node_id, []),
            "incoming": self._adj_in.get(node_id, []),
        }

    def trace_paths(self, req: PathQueryRequest) -> PathQueryResponse:
        """Trace transaction paths up to max_depth using bounded depth-first exploration."""
        discovered_paths: List[TransactionPath] = []
        has_circular = False

        # DFS stack: (current_node, visited_nodes, accumulated_hops)
        stack: deque[Tuple[str, List[str], List[TransactionHop]]] = deque()
        stack.append((req.source_id, [req.source_id], []))

        while stack and len(discovered_paths) < req.limit:
            curr_node, visited, hops = stack.pop()

            if len(hops) >= req.max_depth:
                continue

            for edge in self._adj_out.get(curr_node, []):
                if edge.relationship_type != CorrelationEdgeType.SENT_TO:
                    continue

                if req.min_amount is not None and edge.amount is not None and edge.amount < req.min_amount:
                    continue

                next_node = edge.target_id

                # Calculate dwell time from previous hop if timestamp available
                dwell_time: Optional[float] = None
                if hops and hops[-1].timestamp and edge.timestamp:
                    dwell = (edge.timestamp - hops[-1].timestamp).total_seconds()
                    if dwell >= 0:
                        dwell_time = dwell

                hop = TransactionHop(
                    from_account=curr_node,
                    to_account=next_node,
                    amount=edge.amount or 0.0,
                    timestamp=edge.timestamp,
                    txn_id=edge.transaction_id,
                    dwell_time_seconds=dwell_time,
                )

                new_hops = hops + [hop]
                new_visited = visited + [next_node]

                # Check for cycle / circular flow
                is_cycle = next_node in visited
                if is_cycle:
                    has_circular = True
                    total_amt = sum(h.amount for h in new_hops)
                    dwells = [h.dwell_time_seconds for h in new_hops if h.dwell_time_seconds is not None]
                    min_dwell = min(dwells) if dwells else None

                    discovered_paths.append(
                        TransactionPath(
                            path_id=f"path_{uuid4().hex[:8]}",
                            hop_count=len(new_hops),
                            total_amount=round(total_amt, 2),
                            is_circular=True,
                            nodes=new_visited,
                            hops=new_hops,
                            min_dwell_time_seconds=min_dwell,
                            explanation=f"Circular fund flow detected: {len(new_hops)} hops returning to earlier ring entity '{next_node}'.",
                        )
                    )
                    continue

                # If target_id was specified and matched
                if req.target_id and next_node == req.target_id:
                    total_amt = sum(h.amount for h in new_hops)
                    dwells = [h.dwell_time_seconds for h in new_hops if h.dwell_time_seconds is not None]
                    min_dwell = min(dwells) if dwells else None

                    discovered_paths.append(
                        TransactionPath(
                            path_id=f"path_{uuid4().hex[:8]}",
                            hop_count=len(new_hops),
                            total_amount=round(total_amt, 2),
                            is_circular=False,
                            nodes=new_visited,
                            hops=new_hops,
                            min_dwell_time_seconds=min_dwell,
                            explanation=f"Direct multi-hop flow connecting '{req.source_id}' to '{req.target_id}' across {len(new_hops)} hops.",
                        )
                    )
                    continue

                # Otherwise, if no specific target or intermediate node
                if not req.target_id and len(new_hops) >= 2:
                    total_amt = sum(h.amount for h in new_hops)
                    dwells = [h.dwell_time_seconds for h in new_hops if h.dwell_time_seconds is not None]
                    min_dwell = min(dwells) if dwells else None

                    discovered_paths.append(
                        TransactionPath(
                            path_id=f"path_{uuid4().hex[:8]}",
                            hop_count=len(new_hops),
                            total_amount=round(total_amt, 2),
                            is_circular=False,
                            nodes=new_visited,
                            hops=new_hops,
                            min_dwell_time_seconds=min_dwell,
                            explanation=f"Multi-hop fund flow from '{req.source_id}' traversing {len(new_hops)} intermediate accounts.",
                        )
                    )

                stack.append((next_node, new_visited, new_hops))

        return PathQueryResponse(
            source_id=req.source_id,
            paths_found=len(discovered_paths),
            circular_flows_detected=has_circular,
            paths=discovered_paths,
        )

    def detect_fan_in_fan_out_hubs(self, in_degree_thresh: int = 3, out_degree_thresh: int = 3) -> Dict[str, Any]:
        """Detect accounts exhibiting dramatic fan-in (aggregation) or fan-out (layering) degree."""
        fan_in_nodes = []
        fan_out_nodes = []

        for node_id, node in self._nodes.items():
            in_edges = [e for e in self._adj_in.get(node_id, []) if e.relationship_type == CorrelationEdgeType.SENT_TO]
            out_edges = [e for e in self._adj_out.get(node_id, []) if e.relationship_type == CorrelationEdgeType.SENT_TO]

            unique_senders = set(e.source_id for e in in_edges)
            unique_recipients = set(e.target_id for e in out_edges)

            if len(unique_senders) >= in_degree_thresh:
                total_in = sum(e.amount or 0.0 for e in in_edges)
                fan_in_nodes.append({
                    "node_id": node_id,
                    "label": node.label,
                    "unique_senders_count": len(unique_senders),
                    "total_inflow": round(total_in, 2),
                    "pattern": "FAN_IN_AGGREGATOR",
                })

            if len(unique_recipients) >= out_degree_thresh:
                total_out = sum(e.amount or 0.0 for e in out_edges)
                fan_out_nodes.append({
                    "node_id": node_id,
                    "label": node.label,
                    "unique_recipients_count": len(unique_recipients),
                    "total_outflow": round(total_out, 2),
                    "pattern": "FAN_OUT_DISPERSER",
                })

        return {
            "fan_in_hubs": fan_in_nodes,
            "fan_out_hubs": fan_out_nodes,
        }


# Global instance
transaction_graph_engine = TransactionGraphEngine()


def get_transaction_graph_engine() -> TransactionGraphEngine:
    """Dependency provider."""
    return transaction_graph_engine
