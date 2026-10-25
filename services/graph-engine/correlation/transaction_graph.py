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

    def __init__(self, seed_defaults: bool = False):
        self._nodes: Dict[str, GraphNode] = {}
        # Outgoing edges: node_id -> List[GraphEdge]
        self._adj_out: Dict[str, List[GraphEdge]] = defaultdict(list)
        # Incoming edges: node_id -> List[GraphEdge]
        self._adj_in: Dict[str, List[GraphEdge]] = defaultdict(list)
        self._edges: Dict[str, GraphEdge] = {}
        if seed_defaults:
            self._seed_default_topology()

    def _seed_default_topology(self) -> None:
        """Seed realistic national syndicate and laundering ring fraud topologies."""
        from datetime import timedelta
        now = datetime.now(timezone.utc)

        # --- PRESET 1: 3-Hop Layering Chain (Victim -> Mule 1 -> Mule 2 -> Exit Gateway) ---
        t0 = now - timedelta(hours=2)
        p1_nodes = [
            GraphNode(id="ACC_VICTIM_001", node_type=CorrelationNodeType.ACCOUNT, label="Victim (SBI - R. Sharma)", direct_risk=0.05, risk_score=0.05, metadata={"bank": "State Bank of India", "tier": "Victim Source"}),
            GraphNode(id="ACC_MULE_1", node_type=CorrelationNodeType.ACCOUNT, label="Tier-1 Mule (ICICI - Rohit Ent.)", direct_risk=0.82, risk_score=0.82, metadata={"bank": "ICICI Bank", "tier": "Layer 1"}),
            GraphNode(id="ACC_MULE_2", node_type=CorrelationNodeType.ACCOUNT, label="Tier-2 Mule (HDFC - Apex Log.)", direct_risk=0.91, risk_score=0.91, metadata={"bank": "HDFC Bank", "tier": "Layer 2"}),
            GraphNode(id="ACC_EXIT_GATEWAY", node_type=CorrelationNodeType.ACCOUNT, label="Exit Gateway (P2P Crypto Desk)", direct_risk=0.98, risk_score=0.98, metadata={"bank": "Crypto P2P OTC Desk", "tier": "Cashout Exit"}),
        ]
        for n in p1_nodes:
            self.add_node(n)

        self.add_edge(GraphEdge(
            id="edge_p1_1", source_id="ACC_VICTIM_001", target_id="ACC_MULE_1",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=95000.0, timestamp=t0,
            transaction_id="TXN_UPI_9801A", confidence=1.0,
        ))
        self.add_edge(GraphEdge(
            id="edge_p1_2", source_id="ACC_MULE_1", target_id="ACC_MULE_2",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=93500.0, timestamp=t0 + timedelta(seconds=120),
            transaction_id="TXN_IMPS_4412B", confidence=0.98,
        ))
        self.add_edge(GraphEdge(
            id="edge_p1_3", source_id="ACC_MULE_2", target_id="ACC_EXIT_GATEWAY",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=92000.0, timestamp=t0 + timedelta(seconds=300),
            transaction_id="TXN_RTGS_8821C", confidence=0.99,
        ))

        # --- PRESET 2: Circular Wash Cycle (ACC_NODE_A -> ACC_NODE_B -> ACC_NODE_C -> ACC_NODE_A) ---
        t_ring = now - timedelta(hours=5)
        p2_nodes = [
            GraphNode(id="ACC_NODE_A", node_type=CorrelationNodeType.ACCOUNT, label="Wash Ring Node A (Kavya Traders)", direct_risk=0.89, risk_score=0.89, metadata={"entity_type": "Mule Ring Hub"}),
            GraphNode(id="ACC_NODE_B", node_type=CorrelationNodeType.ACCOUNT, label="Wash Ring Node B (Zenith Global)", direct_risk=0.85, risk_score=0.85, metadata={"entity_type": "Intermediary Shell"}),
            GraphNode(id="ACC_NODE_C", node_type=CorrelationNodeType.ACCOUNT, label="Wash Ring Node C (Sunrise Metal)", direct_risk=0.87, risk_score=0.87, metadata={"entity_type": "Layering Node"}),
        ]
        for n in p2_nodes:
            self.add_node(n)

        self.add_edge(GraphEdge(
            id="edge_p2_1", source_id="ACC_NODE_A", target_id="ACC_NODE_B",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=50000.0, timestamp=t_ring,
            transaction_id="TXN_WASH_01", confidence=0.99,
        ))
        self.add_edge(GraphEdge(
            id="edge_p2_2", source_id="ACC_NODE_B", target_id="ACC_NODE_C",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=48500.0, timestamp=t_ring + timedelta(minutes=4),
            transaction_id="TXN_WASH_02", confidence=0.99,
        ))
        self.add_edge(GraphEdge(
            id="edge_p2_3", source_id="ACC_NODE_C", target_id="ACC_NODE_A",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=47000.0, timestamp=t_ring + timedelta(minutes=9),
            transaction_id="TXN_WASH_03", confidence=0.99,
        ))

        # --- PRESET 3: Aggregator Fan-Out Hub (ACC_HUB_AGGREGATOR) ---
        t_hub = now - timedelta(hours=8)
        hub_node = GraphNode(id="ACC_HUB_AGGREGATOR", node_type=CorrelationNodeType.ACCOUNT, label="Central Syndicate Hub (Jaipur)", direct_risk=0.97, risk_score=0.97, metadata={"cluster": "Aggregator Hub"})
        self.add_node(hub_node)

        for i, (name, amt) in enumerate([("Victim Delhi", 45000), ("Victim Mumbai", 70000), ("Victim Jaipur", 85000), ("Victim Bengaluru", 60000)], 1):
            vid = f"ACC_INFLOW_{i}"
            self.add_node(GraphNode(id=vid, node_type=CorrelationNodeType.ACCOUNT, label=name, direct_risk=0.08, risk_score=0.08))
            self.add_edge(GraphEdge(
                id=f"edge_in_{i}", source_id=vid, target_id="ACC_HUB_AGGREGATOR",
                relationship_type=CorrelationEdgeType.SENT_TO, amount=float(amt), timestamp=t_hub + timedelta(minutes=i*10),
                transaction_id=f"TXN_IN_{i}",
            ))

        for j, (name, amt) in enumerate([("Cashout Mule 1 (ATM)", 55000), ("Cashout Mule 2 (Gold VPA)", 60000), ("Cashout Mule 3 (P2P)", 45000), ("Cashout Mule 4 (Forex)", 50000), ("Cashout Mule 5 (Card)", 50000)], 1):
            mid = f"ACC_CASHOUT_{j}"
            self.add_node(GraphNode(id=mid, node_type=CorrelationNodeType.ACCOUNT, label=name, direct_risk=0.88, risk_score=0.88))
            self.add_edge(GraphEdge(
                id=f"edge_out_{j}", source_id="ACC_HUB_AGGREGATOR", target_id=mid,
                relationship_type=CorrelationEdgeType.SENT_TO, amount=float(amt), timestamp=t_hub + timedelta(minutes=45 + j*5),
                transaction_id=f"TXN_OUT_{j}",
            ))

        # --- SHARED INFRASTRUCTURE / CLUSTERS (Phones, Devices, VPAs) ---
        phone_node = GraphNode(id="PHONE_SHARED_9844", node_type=CorrelationNodeType.PHONE, label="+91 98441 23091", risk_score=0.95, direct_risk=0.95)
        dev_node = GraphNode(id="DEV_IMEI_8849", node_type=CorrelationNodeType.DEVICE, label="IMEI-86490218991 (Xiaomi Pad)", risk_score=0.92, direct_risk=0.92)
        ip_node = GraphNode(id="IP_PROXY_103", node_type=CorrelationNodeType.IP, label="103.21.99.14 (Jaipur VPN)", risk_score=0.85, direct_risk=0.85)
        self.add_node(phone_node)
        self.add_node(dev_node)
        self.add_node(ip_node)

        for mule in ["ACC_MULE_1", "ACC_MULE_2", "ACC_NODE_A"]:
            self.add_edge(GraphEdge(id=f"rel_ph_{mule}", source_id=mule, target_id="PHONE_SHARED_9844", relationship_type=CorrelationEdgeType.USES_IDENTIFIER))
            self.add_edge(GraphEdge(id=f"rel_dev_{mule}", source_id=mule, target_id="DEV_IMEI_8849", relationship_type=CorrelationEdgeType.USED_DEVICE))
            self.add_edge(GraphEdge(id=f"rel_ip_{mule}", source_id=mule, target_id="IP_PROXY_103", relationship_type=CorrelationEdgeType.ACCESSED_FROM))

        # --- RISK PROPAGATION SEEDS ---
        seed_fraud = GraphNode(id="ACC_CONFIRMED_FRAUD_881", node_type=CorrelationNodeType.ACCOUNT, label="Confirmed Syndicate Master (CFCFRMS)", direct_risk=1.0, risk_score=1.0)
        layer1_mule = GraphNode(id="ACC_LAYER1_MULE", node_type=CorrelationNodeType.ACCOUNT, label="Primary Mule (Layer 1)", direct_risk=0.2, risk_score=0.2)
        layer2_mule = GraphNode(id="ACC_LAYER2_MULE", node_type=CorrelationNodeType.ACCOUNT, label="Secondary Mule (Layer 2)", direct_risk=0.1, risk_score=0.1)
        layer3_mule = GraphNode(id="ACC_LAYER3_CASHOUT", node_type=CorrelationNodeType.ACCOUNT, label="Tertiary Exit (Layer 3)", direct_risk=0.05, risk_score=0.05)
        self.add_node(seed_fraud)
        self.add_node(layer1_mule)
        self.add_node(layer2_mule)
        self.add_node(layer3_mule)

        self.add_edge(GraphEdge(id="edge_prop_1", source_id="ACC_CONFIRMED_FRAUD_881", target_id="ACC_LAYER1_MULE", relationship_type=CorrelationEdgeType.SENT_TO, amount=85000.0, timestamp=now - timedelta(hours=1)))
        self.add_edge(GraphEdge(id="edge_prop_2", source_id="ACC_LAYER1_MULE", target_id="ACC_LAYER2_MULE", relationship_type=CorrelationEdgeType.SENT_TO, amount=80000.0, timestamp=now - timedelta(minutes=45)))
        self.add_edge(GraphEdge(id="edge_prop_3", source_id="ACC_LAYER2_MULE", target_id="ACC_LAYER3_CASHOUT", relationship_type=CorrelationEdgeType.SENT_TO, amount=75000.0, timestamp=now - timedelta(minutes=20)))

        # Multi-seed Ring (ACC_SUSPECT_401, ACC_SUSPECT_402)
        s401 = GraphNode(id="ACC_SUSPECT_401", node_type=CorrelationNodeType.ACCOUNT, label="Suspect Operator Alpha", direct_risk=0.88, risk_score=0.88)
        s402 = GraphNode(id="ACC_SUSPECT_402", node_type=CorrelationNodeType.ACCOUNT, label="Suspect Operator Beta", direct_risk=0.84, risk_score=0.84)
        intermediary = GraphNode(id="ACC_JOINT_INTERMEDIARY", node_type=CorrelationNodeType.ACCOUNT, label="Joint Convergence Acc", direct_risk=0.15, risk_score=0.15)
        self.add_node(s401)
        self.add_node(s402)
        self.add_node(intermediary)
        self.add_edge(GraphEdge(id="edge_s1", source_id="ACC_SUSPECT_401", target_id="ACC_JOINT_INTERMEDIARY", relationship_type=CorrelationEdgeType.SENT_TO, amount=60000.0, timestamp=now - timedelta(hours=3)))
        self.add_edge(GraphEdge(id="edge_s2", source_id="ACC_SUSPECT_402", target_id="ACC_JOINT_INTERMEDIARY", relationship_type=CorrelationEdgeType.SENT_TO, amount=65000.0, timestamp=now - timedelta(hours=3)))

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
transaction_graph_engine = TransactionGraphEngine(seed_defaults=True)


def get_transaction_graph_engine() -> TransactionGraphEngine:
    """Dependency provider."""
    return transaction_graph_engine
