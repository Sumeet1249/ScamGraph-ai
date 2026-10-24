"""Declarative Cypher Query Builder for ScamGraph AI.

Constructs parameterized queries for:
- Scam Journey path construction (:JourneyStep -[:FOLLOWED_BY]-> :JourneyStep)
- Entity resolution (linking Senders, URLs, Domains, UPI Handles)
- Incident fusion (detecting shared infrastructure across distinct incidents)
- Cytoscape.js subgraph extraction
"""

from typing import Any, Dict, List, Optional
from packages.schemas import CytoscapeGraph, CytoscapeNode, CytoscapeNodeData, CytoscapeEdge, CytoscapeEdgeData, GraphNodeType


class CypherQueryBuilder:
    """Builds parameterized Cypher queries for the dual graph model."""

    @staticmethod
    def merge_incident(incident_id: str, status: str = "ACTIVE") -> Dict[str, Any]:
        query = """
        MERGE (i:Incident {id: $incident_id})
        ON CREATE SET i.status = $status, i.createdAt = datetime()
        ON MATCH SET i.updatedAt = datetime()
        RETURN i.id as id
        """
        return {"query": query, "params": {"incident_id": incident_id, "status": status}}

    @staticmethod
    def add_journey_step(
        incident_id: str,
        step_id: str,
        sequence: int,
        stage: str,
        title: str,
        prev_step_id: Optional[str] = None,
        time_delta_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Creates a JourneyStep and links it to Incident and preceding step."""
        query = """
        MATCH (i:Incident {id: $incident_id})
        MERGE (s:JourneyStep {stepId: $step_id})
        ON CREATE SET 
            s.sequence = $sequence,
            s.stage = $stage,
            s.title = $title,
            s.createdAt = datetime()
        MERGE (i)-[:CONTAINS_STEP]->(s)
        WITH s
        """
        if prev_step_id:
            query += """
            MATCH (prev:JourneyStep {stepId: $prev_step_id})
            MERGE (prev)-[r:FOLLOWED_BY]->(s)
            ON CREATE SET r.timeDeltaSeconds = $time_delta_seconds
            """

        query += " RETURN s.stepId as stepId"
        return {
            "query": query,
            "params": {
                "incident_id": incident_id,
                "step_id": step_id,
                "sequence": sequence,
                "stage": stage,
                "title": title,
                "prev_step_id": prev_step_id,
                "time_delta_seconds": time_delta_seconds or 0,
            },
        }

    @staticmethod
    def link_sender(step_id: str, phone: str, channel: str = "SMS") -> Dict[str, Any]:
        query = """
        MATCH (s:JourneyStep {stepId: $step_id})
        MERGE (snd:Sender {identifier: $phone})
        ON CREATE SET snd.channel = $channel, snd.firstSeen = datetime()
        MERGE (s)-[:ORIGINATED_FROM]->(snd)
        RETURN snd.identifier as identifier
        """
        return {"query": query, "params": {"step_id": step_id, "phone": phone, "channel": channel}}

    @staticmethod
    def link_upi_handle(step_id: str, vpa: str, claimed_name: Optional[str] = None) -> Dict[str, Any]:
        query = """
        MATCH (s:JourneyStep {stepId: $step_id})
        MERGE (v:UPIHandle {vpa: $vpa})
        ON CREATE SET v.claimedName = $claimed_name, v.firstSeen = datetime()
        MERGE (s)-[:TARGETS_PAYMENT]->(v)
        RETURN v.vpa as vpa
        """
        return {"query": query, "params": {"step_id": step_id, "vpa": vpa, "claimed_name": claimed_name}}

    @staticmethod
    def find_cross_incident_correlations(incident_id: str) -> Dict[str, Any]:
        """Finds other incidents sharing the same sender phone or target UPI handle."""
        query = """
        MATCH (curr:Incident {id: $incident_id})-[:CONTAINS_STEP]->(s:JourneyStep)
        OPTIONAL MATCH (s)-[:ORIGINATED_FROM]->(snd:Sender)<-[:ORIGINATED_FROM]-(otherStep:JourneyStep)<-[:CONTAINS_STEP]-(otherInc:Incident)
        WHERE otherInc.id <> $incident_id
        OPTIONAL MATCH (s)-[:TARGETS_PAYMENT]->(v:UPIHandle)<-[:TARGETS_PAYMENT]-(otherPayStep:JourneyStep)<-[:CONTAINS_STEP]-(otherPayInc:Incident)
        WHERE otherPayInc.id <> $incident_id
        RETURN 
            collect(DISTINCT {other_incident_id: otherInc.id, shared_entity: snd.identifier, type: 'PHONE'}) as phone_shares,
            collect(DISTINCT {other_incident_id: otherPayInc.id, shared_entity: v.vpa, type: 'VPA'}) as vpa_shares
        """
        return {"query": query, "params": {"incident_id": incident_id}}

    @staticmethod
    def parse_to_cytoscape(records: List[Dict[str, Any]]) -> CytoscapeGraph:
        """Parses graph query records into a clean CytoscapeGraph."""
        nodes: Dict[str, CytoscapeNode] = {}
        edges: List[CytoscapeEdge] = []

        for row in records:
            # Handle row formatting from Neo4j paths or node collections
            if "node" in row:
                n = row["node"]
                n_id = str(n.get("id") or n.get("stepId") or n.get("identifier") or n.get("vpa"))
                if n_id and n_id not in nodes:
                    label = str(n.get("title") or n.get("label") or n_id)
                    nodes[n_id] = CytoscapeNode(
                        data=CytoscapeNodeData(
                            id=n_id,
                            label=label,
                            node_type=GraphNodeType.JOURNEY_STEP,
                        )
                    )

        return CytoscapeGraph(nodes=list(nodes.values()), edges=edges)
