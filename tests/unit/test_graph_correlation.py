"""Unit Tests for Graph Correlation Engine (Module C).

Tests multi-hop path tracing, circular fund flow cycles, fan-in/fan-out hub analysis,
suspicious cluster detection, and explainable risk propagation with distance decay.
"""

import pytest
from datetime import datetime, timezone, timedelta

from packages.schemas.graph_correlation import (
    ClusterQueryRequest,
    CorrelationEdgeType,
    CorrelationNodeType,
    GraphEdge,
    GraphNode,
    PathQueryRequest,
    RiskPropagationRequest,
)
from services.graph_engine.algorithms.risk_propagation import GraphRiskPropagator
from services.graph_engine.correlation.cluster_service import GraphClusterService
from services.graph_engine.correlation.transaction_graph import TransactionGraphEngine


class TestTransactionGraphEngine:
    """Tests multi-hop flow paths and circular cycle detection."""

    def test_multi_hop_path_tracing(self):
        engine = TransactionGraphEngine()
        t0 = datetime(2026, 10, 22, 10, 0, 0, tzinfo=timezone.utc)

        # Build 3-hop chain: Victim -> Mule 1 -> Mule 2 -> Cashout
        for acc in ["ACC_VICTIM", "ACC_MULE_1", "ACC_MULE_2", "ACC_CASHOUT"]:
            engine.add_node(GraphNode(id=acc, node_type=CorrelationNodeType.ACCOUNT, label=acc))

        engine.add_edge(GraphEdge(
            id="e1", source_id="ACC_VICTIM", target_id="ACC_MULE_1",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=95000.0, timestamp=t0,
        ))
        engine.add_edge(GraphEdge(
            id="e2", source_id="ACC_MULE_1", target_id="ACC_MULE_2",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=94000.0, timestamp=t0 + timedelta(minutes=2),
        ))
        engine.add_edge(GraphEdge(
            id="e3", source_id="ACC_MULE_2", target_id="ACC_CASHOUT",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=93500.0, timestamp=t0 + timedelta(minutes=5),
        ))

        res = engine.trace_paths(PathQueryRequest(source_id="ACC_VICTIM", target_id="ACC_CASHOUT", max_depth=4))
        assert res.paths_found >= 1
        path = res.paths[0]
        assert path.hop_count == 3
        assert path.nodes == ["ACC_VICTIM", "ACC_MULE_1", "ACC_MULE_2", "ACC_CASHOUT"]
        assert path.min_dwell_time_seconds == 120.0  # 2 minutes between hop 1 and hop 2
        assert path.is_circular is False

    def test_circular_fund_flow_cycle_detection(self):
        engine = TransactionGraphEngine()
        t0 = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)

        # Ring: A -> B -> C -> A
        for node_id in ["ACC_A", "ACC_B", "ACC_C"]:
            engine.add_node(GraphNode(id=node_id, node_type=CorrelationNodeType.ACCOUNT, label=node_id))

        engine.add_edge(GraphEdge(
            id="e_ab", source_id="ACC_A", target_id="ACC_B",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=50000.0, timestamp=t0,
        ))
        engine.add_edge(GraphEdge(
            id="e_bc", source_id="ACC_B", target_id="ACC_C",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=48000.0, timestamp=t0 + timedelta(minutes=5),
        ))
        engine.add_edge(GraphEdge(
            id="e_ca", source_id="ACC_C", target_id="ACC_A",
            relationship_type=CorrelationEdgeType.SENT_TO, amount=45000.0, timestamp=t0 + timedelta(minutes=10),
        ))

        res = engine.trace_paths(PathQueryRequest(source_id="ACC_A", max_depth=4))
        assert res.circular_flows_detected is True
        circular_paths = [p for p in res.paths if p.is_circular]
        assert len(circular_paths) >= 1
        assert "Circular fund flow detected" in circular_paths[0].explanation

    def test_fan_in_and_fan_out_hub_detection(self):
        engine = TransactionGraphEngine()

        engine.add_node(GraphNode(id="ACC_HUB_IN", node_type=CorrelationNodeType.ACCOUNT, label="Hub In"))
        engine.add_node(GraphNode(id="ACC_HUB_OUT", node_type=CorrelationNodeType.ACCOUNT, label="Hub Out"))

        # Fan-in: 4 senders -> ACC_HUB_IN
        for i in range(4):
            src = f"SENDER_{i}"
            engine.add_node(GraphNode(id=src, node_type=CorrelationNodeType.ACCOUNT, label=src))
            engine.add_edge(GraphEdge(
                id=f"e_in_{i}", source_id=src, target_id="ACC_HUB_IN",
                relationship_type=CorrelationEdgeType.SENT_TO, amount=10000.0,
            ))

        # Fan-out: ACC_HUB_OUT -> 4 recipients
        for i in range(4):
            dst = f"RECIPIENT_{i}"
            engine.add_node(GraphNode(id=dst, node_type=CorrelationNodeType.ACCOUNT, label=dst))
            engine.add_edge(GraphEdge(
                id=f"e_out_{i}", source_id="ACC_HUB_OUT", target_id=dst,
                relationship_type=CorrelationEdgeType.SENT_TO, amount=5000.0,
            ))

        hubs = engine.detect_fan_in_fan_out_hubs(in_degree_thresh=3, out_degree_thresh=3)
        assert len(hubs["fan_in_hubs"]) == 1
        assert hubs["fan_in_hubs"][0]["node_id"] == "ACC_HUB_IN"
        assert hubs["fan_in_hubs"][0]["unique_senders_count"] == 4

        assert len(hubs["fan_out_hubs"]) == 1
        assert hubs["fan_out_hubs"][0]["node_id"] == "ACC_HUB_OUT"
        assert hubs["fan_out_hubs"][0]["unique_recipients_count"] == 4


class TestGraphRiskPropagation:
    """Tests transparent risk propagation with distance decay."""

    def test_distance_decay_formula(self):
        engine = TransactionGraphEngine()

        # Seed -> Hop 1 -> Hop 2 -> Hop 3
        engine.add_node(GraphNode(
            id="SEED_REPORT", node_type=CorrelationNodeType.REPORT,
            label="Confirmed Phishing Report", direct_risk=0.90, risk_score=0.90,
        ))
        engine.add_node(GraphNode(id="ACC_HOP1", node_type=CorrelationNodeType.ACCOUNT, label="Hop 1 Mule"))
        engine.add_node(GraphNode(id="ACC_HOP2", node_type=CorrelationNodeType.ACCOUNT, label="Hop 2 Layer"))
        engine.add_node(GraphNode(id="ACC_HOP3", node_type=CorrelationNodeType.ACCOUNT, label="Hop 3 Beneficiary"))

        engine.add_edge(GraphEdge(
            id="e1", source_id="SEED_REPORT", target_id="ACC_HOP1",
            relationship_type=CorrelationEdgeType.LINKED_TO_REPORT,
        ))
        engine.add_edge(GraphEdge(
            id="e2", source_id="ACC_HOP1", target_id="ACC_HOP2",
            relationship_type=CorrelationEdgeType.SENT_TO,
        ))
        engine.add_edge(GraphEdge(
            id="e3", source_id="ACC_HOP2", target_id="ACC_HOP3",
            relationship_type=CorrelationEdgeType.SENT_TO,
        ))

        propagator = GraphRiskPropagator(engine=engine)
        res = propagator.propagate_risk(
            RiskPropagationRequest(seed_node_ids=["SEED_REPORT"], decay_factor=0.5, max_hops=3)
        )

        node_map = {n.node_id: n for n in res.nodes}
        assert "SEED_REPORT" in node_map
        assert node_map["SEED_REPORT"].hops_from_seed == 0
        assert node_map["SEED_REPORT"].direct_risk == 0.90

        # Hop 1: 0.90 * 0.5 * 1.0 (LINKED_TO_REPORT) = 0.45
        assert "ACC_HOP1" in node_map
        assert node_map["ACC_HOP1"].hops_from_seed == 1
        assert node_map["ACC_HOP1"].propagated_risk == pytest.approx(0.45, 0.05)

        # Hop 2: 0.45 * 0.5 * 0.9 (SENT_TO) ~ 0.20
        assert "ACC_HOP2" in node_map
        assert node_map["ACC_HOP2"].hops_from_seed == 2
        assert node_map["ACC_HOP2"].propagated_risk < node_map["ACC_HOP1"].propagated_risk

    def test_revoked_seed_propagates_zero_risk(self):
        engine = TransactionGraphEngine()
        engine.add_node(GraphNode(
            id="REVOKED_REPORT", node_type=CorrelationNodeType.REPORT,
            label="Revoked Report", direct_risk=0.90, risk_score=0.90, is_revoked=True,
        ))
        engine.add_node(GraphNode(id="ACC_TARGET", node_type=CorrelationNodeType.ACCOUNT, label="Target Account"))
        engine.add_edge(GraphEdge(
            id="e1", source_id="REVOKED_REPORT", target_id="ACC_TARGET",
            relationship_type=CorrelationEdgeType.LINKED_TO_REPORT,
        ))

        propagator = GraphRiskPropagator(engine=engine)
        res = propagator.propagate_risk(
            RiskPropagationRequest(seed_node_ids=["REVOKED_REPORT"], decay_factor=0.5)
        )
        # Target must not receive risk from revoked report
        node_map = {n.node_id: n for n in res.nodes}
        assert "ACC_TARGET" not in node_map


class TestGraphClusterService:
    """Tests suspicious cluster detection."""

    def test_detect_shared_identifier_ring(self):
        engine = TransactionGraphEngine()

        # Shared phone indicator used by 3 separate accounts
        engine.add_node(GraphNode(id="PHONE_SUSPECT", node_type=CorrelationNodeType.PHONE, label="+919876543210"))
        for i in range(3):
            acc_id = f"ACC_MULE_{i}"
            engine.add_node(GraphNode(id=acc_id, node_type=CorrelationNodeType.ACCOUNT, label=acc_id))
            engine.add_edge(GraphEdge(
                id=f"rel_{i}", source_id=acc_id, target_id="PHONE_SUSPECT",
                relationship_type=CorrelationEdgeType.USES_IDENTIFIER,
            ))

        service = GraphClusterService(engine=engine)
        res = service.detect_clusters(ClusterQueryRequest(min_cluster_size=2))

        assert res.total_clusters >= 1
        ring_cluster = res.clusters[0]
        assert ring_cluster.cluster_type == "SHARED_IDENTIFIER_RING"
        assert ring_cluster.node_count == 4
        assert ring_cluster.suspicion_score >= 0.70
