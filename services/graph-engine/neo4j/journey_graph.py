"""Scam Journey Graph Service (Step 12).

Constructs the topological Neo4j property graph:
- (:Incident)-[:HAS_EVENT]->(:Event)
- (:Event)-[:FOLLOWED_BY]->(:Event)
- (:Message)-[:CONTAINS]->(:URL)
- (:URL)-[:HOSTED_ON]->(:Domain)
- (:Domain)-[:RESOLVES_TO]->(:IP)
- (:URL)-[:IMPERSONATES]->(:Brand)
- (:PaymentRequest)-[:TO]->(:PaymentEntity)
"""

from typing import Any, Dict, List, Optional
from packages.schemas import (
    CytoscapeGraph,
    CytoscapeNode,
    CytoscapeNodeData,
    CytoscapeEdge,
    CytoscapeEdgeData,
    GraphNodeType,
)


class JourneyGraphBuilder:
    """Constructs and queries the Step 12 canonical Scam Journey Graph."""

    @staticmethod
    def query_merge_incident_and_event(
        incident_id: str,
        event_id: str,
        event_type: str,
        sequence: int,
        prev_event_id: Optional[str] = None,
        time_delta_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Links (:Incident)-[:HAS_EVENT]->(:Event) and (:Event)-[:FOLLOWED_BY]->(:Event)."""
        query = """
        MERGE (i:Incident {id: $incident_id})
        ON CREATE SET i.status = 'ACTIVE', i.createdAt = datetime()
        MERGE (e:Event {id: $event_id})
        ON CREATE SET 
            e.eventType = $event_type,
            e.sequence = $sequence,
            e.createdAt = datetime()
        MERGE (i)-[:HAS_EVENT]->(e)
        WITH e
        """
        if prev_event_id:
            query += """
            MATCH (prev:Event {id: $prev_event_id})
            MERGE (prev)-[r:FOLLOWED_BY]->(e)
            ON CREATE SET r.timeDeltaSeconds = $time_delta_seconds
            """

        query += " RETURN e.id as event_id"
        return {
            "query": query,
            "params": {
                "incident_id": incident_id,
                "event_id": event_id,
                "event_type": event_type,
                "sequence": sequence,
                "prev_event_id": prev_event_id,
                "time_delta_seconds": time_delta_seconds or 0,
            },
        }

    @staticmethod
    def query_link_message_and_url(
        event_id: str,
        message_id: str,
        text_snippet: str,
        raw_url: str,
    ) -> Dict[str, Any]:
        """Links (:Event)-[:OBSERVED]->(:Message)-[:CONTAINS]->(:URL)."""
        query = """
        MATCH (e:Event {id: $event_id})
        MERGE (m:Message {id: $message_id})
        ON CREATE SET m.snippet = $text_snippet
        MERGE (e)-[:OBSERVED]->(m)
        MERGE (u:URL {rawUrl: $raw_url})
        MERGE (m)-[:CONTAINS]->(u)
        RETURN m.id as message_id, u.rawUrl as url
        """
        return {
            "query": query,
            "params": {
                "event_id": event_id,
                "message_id": message_id,
                "text_snippet": text_snippet[:120],
                "raw_url": raw_url,
            },
        }

    @staticmethod
    def query_link_url_infrastructure(
        raw_url: str,
        domain_name: str,
        ip_address: Optional[str] = None,
        impersonated_brand: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Links:

        (:URL)-[:HOSTED_ON]->(:Domain)
        (:Domain)-[:RESOLVES_TO]->(:IP)
        (:URL)-[:IMPERSONATES]->(:Brand)
        """
        query = """
        MATCH (u:URL {rawUrl: $raw_url})
        MERGE (d:Domain {name: $domain_name})
        MERGE (u)-[:HOSTED_ON]->(d)
        WITH u, d
        """
        if ip_address:
            query += """
            MERGE (ip:IP {address: $ip_address})
            MERGE (d)-[:RESOLVES_TO]->(ip)
            WITH u, d
            """

        if impersonated_brand:
            query += """
            MERGE (b:Brand {name: $impersonated_brand})
            MERGE (u)-[:IMPERSONATES]->(b)
            WITH u, d
            """

        query += " RETURN d.name as domain"
        return {
            "query": query,
            "params": {
                "raw_url": raw_url,
                "domain_name": domain_name,
                "ip_address": ip_address,
                "impersonated_brand": impersonated_brand,
            },
        }

    @staticmethod
    def query_link_payment_request(
        event_id: str,
        payment_request_id: str,
        vpa: str,
        claimed_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Links:

        (:Event)-[:OBSERVED]->(:PaymentRequest)-[:TO]->(:PaymentEntity)
        """
        query = """
        MATCH (e:Event {id: $event_id})
        MERGE (pr:PaymentRequest {id: $payment_request_id})
        MERGE (e)-[:OBSERVED]->(pr)
        MERGE (pe:PaymentEntity {vpa: $vpa})
        ON CREATE SET pe.claimedName = $claimed_name
        MERGE (pr)-[:TO]->(pe)
        RETURN pr.id as payment_request_id, pe.vpa as vpa
        """
        return {
            "query": query,
            "params": {
                "event_id": event_id,
                "payment_request_id": payment_request_id,
                "vpa": vpa,
                "claimed_name": claimed_name,
            },
        }

    @staticmethod
    def query_full_journey_subgraph(incident_id: str) -> Dict[str, Any]:
        """Retrieves the complete graph of events, messages, URLs, domains, and payment entities."""
        query = """
        MATCH (i:Incident {id: $incident_id})-[:HAS_EVENT]->(e:Event)
        OPTIONAL MATCH (e)-[f:FOLLOWED_BY]->(nextE:Event)
        OPTIONAL MATCH (e)-[:OBSERVED]->(m:Message)-[:CONTAINS]->(u:URL)
        OPTIONAL MATCH (u)-[:HOSTED_ON]->(d:Domain)
        OPTIONAL MATCH (d)-[:RESOLVES_TO]->(ip:IP)
        OPTIONAL MATCH (u)-[:IMPERSONATES]->(b:Brand)
        OPTIONAL MATCH (e)-[:OBSERVED]->(pr:PaymentRequest)-[:TO]->(pe:PaymentEntity)
        RETURN 
            i, e, f, nextE, m, u, d, ip, b, pr, pe
        """
        return {"query": query, "params": {"incident_id": incident_id}}
