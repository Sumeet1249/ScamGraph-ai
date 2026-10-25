"""FastAPI Endpoints for Graph Correlation Engine (Module C).

Exposes multi-hop path tracing, circular flow detection, cluster identification,
and transparent risk propagation with distance decay.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from packages.schemas.graph_correlation import (
    ClusterQueryRequest,
    ClusterQueryResponse,
    CorrelationEdgeType,
    CorrelationNodeType,
    GraphEdge,
    GraphNode,
    PathQueryRequest,
    PathQueryResponse,
    RiskPropagationRequest,
    RiskPropagationResponse,
)
from services.graph_engine.algorithms.risk_propagation import (
    GraphRiskPropagator,
    get_graph_risk_propagator,
)
from services.graph_engine.correlation.cluster_service import (
    GraphClusterService,
    get_graph_cluster_service,
)
from services.graph_engine.correlation.transaction_graph import (
    TransactionGraphEngine,
    get_transaction_graph_engine,
)

router = APIRouter()


class BuildGraphPayload(BaseModel):
    """Payload to build or ingest nodes and edges into the correlation graph."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]


@router.post("/build", status_code=status.HTTP_201_CREATED)
async def build_or_update_graph(
    payload: BuildGraphPayload,
    engine: TransactionGraphEngine = Depends(get_transaction_graph_engine),
):
    """Ingest nodes and edges into the correlation graph."""
    for n in payload.nodes:
        engine.add_node(n)
    for e in payload.edges:
        engine.add_edge(e)
    return {
        "status": "GRAPH_UPDATED",
        "nodes_added": len(payload.nodes),
        "edges_added": len(payload.edges),
        "total_nodes": len(engine._nodes),
        "total_edges": len(engine._edges),
    }


@router.get("/topology")
async def get_graph_topology(
    engine: TransactionGraphEngine = Depends(get_transaction_graph_engine),
):
    """Retrieve full nodes, edges, and topology summary of the correlation graph."""
    nodes = list(engine._nodes.values())
    edges = list(engine._edges.values())
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "accounts_count": sum(1 for n in nodes if n.node_type == CorrelationNodeType.ACCOUNT),
            "shared_phones_count": sum(1 for n in nodes if n.node_type == CorrelationNodeType.PHONE),
            "shared_devices_count": sum(1 for n in nodes if n.node_type == CorrelationNodeType.DEVICE),
            "shared_ips_count": sum(1 for n in nodes if n.node_type == CorrelationNodeType.IP),
        },
    }


@router.get("/entities/{entity_id}", response_model=GraphNode)
async def get_graph_entity(
    entity_id: str,
    engine: TransactionGraphEngine = Depends(get_transaction_graph_engine),
):
    """Retrieve graph entity by ID."""
    node = engine.get_node(entity_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity '{entity_id}' not found in correlation graph.",
        )
    return node


@router.get("/entities/{entity_id}/neighbors")
async def get_entity_neighbors(
    entity_id: str,
    engine: TransactionGraphEngine = Depends(get_transaction_graph_engine),
):
    """Retrieve 1-hop incoming and outgoing connections for an entity."""
    node = engine.get_node(entity_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity '{entity_id}' not found in correlation graph.",
        )
    neighbors = engine.get_neighbors(entity_id)
    return {
        "entity_id": entity_id,
        "node": node,
        "outgoing_edges": neighbors["outgoing"],
        "incoming_edges": neighbors["incoming"],
        "in_degree": len(neighbors["incoming"]),
        "out_degree": len(neighbors["outgoing"]),
    }


@router.post("/paths", response_model=PathQueryResponse)
async def trace_transaction_paths(
    req: PathQueryRequest,
    engine: TransactionGraphEngine = Depends(get_transaction_graph_engine),
):
    """Trace multi-hop fund flows, rapid pass-throughs, and circular flows up to max_depth."""
    try:
        return engine.trace_paths(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error tracing graph paths: {str(e)}",
        )


@router.post("/clusters", response_model=ClusterQueryResponse)
async def detect_suspicious_clusters(
    req: ClusterQueryRequest,
    service: GraphClusterService = Depends(get_graph_cluster_service),
):
    """Detect connected components, shared-identifier rings, and campaign communities."""
    try:
        return service.detect_clusters(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error detecting clusters: {str(e)}",
        )


@router.post("/risk-propagation", response_model=RiskPropagationResponse)
async def propagate_graph_risk(
    req: RiskPropagationRequest,
    propagator: GraphRiskPropagator = Depends(get_graph_risk_propagator),
):
    """Calculate transparent risk propagation with distance decay (lambda) from verified seed reports."""
    try:
        return propagator.propagate_risk(req)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error propagating graph risk: {str(e)}",
        )


@router.get("/cases/{case_id}")
async def get_case_subgraph(
    case_id: str,
    engine: TransactionGraphEngine = Depends(get_transaction_graph_engine),
):
    """Retrieve full subgraph and timeline associated with an investigation case."""
    # Find all nodes linked to this case or incident
    subgraph_nodes = []
    subgraph_edges = []

    for nid, node in engine._nodes.items():
        if node.metadata.get("case_id") == case_id or nid == case_id:
            subgraph_nodes.append(node)
            neighbors = engine.get_neighbors(nid)
            for e in neighbors["outgoing"] + neighbors["incoming"]:
                if e not in subgraph_edges:
                    subgraph_edges.append(e)

    return {
        "case_id": case_id,
        "nodes": subgraph_nodes,
        "edges": subgraph_edges,
        "summary": f"Case graph containing {len(subgraph_nodes)} nodes and {len(subgraph_edges)} relationships.",
    }
