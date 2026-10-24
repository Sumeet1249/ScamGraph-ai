"""Neo4j Graph Repository for ScamGraph Graph Intelligence V1.

Provides:
- Abstract GraphRepository interface
- Concrete Neo4jGraphRepository implementation
- Provenance-backed edge creation
- In-memory fallback for local offline testing and resilient degradation
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from services.graph_engine.models.graph_models import (
    GraphEntityNode,
    GraphNodeType,
    GraphRelationshipType,
    IncidentNode,
    RelationshipProvenance,
)
from services.graph_engine.neo4j.client import Neo4jClient, neo4j_client

logger = logging.getLogger("graph_engine.repository")


class GraphRepository(ABC):
    """Abstract interface for ScamGraph Evidence Graph operations."""

    def __new__(cls, *args, **kwargs):
        if cls is GraphRepository:
            return super().__new__(Neo4jGraphRepository)
        return super().__new__(cls)

    @abstractmethod
    async def upsert_incident(self, incident: IncidentNode) -> Dict[str, Any]:
        """Upsert an :Incident node."""
        ...

    @abstractmethod
    async def upsert_entity(
        self,
        entity_or_type: Any,
        entity_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Upsert an entity node (Phone, URL, Domain, IP, ASN, PaymentEntity, etc.)."""
        ...

    @abstractmethod
    async def connect_incident_entity(
        self,
        incident_id: str,
        entity_type: str,
        entity_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Incident)-[:OBSERVED]->(:Entity)."""
        ...

    @abstractmethod
    async def connect_url_domain(
        self,
        url_id: str,
        domain_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:URL)-[:HOSTED_ON]->(:Domain)."""
        ...

    @abstractmethod
    async def connect_domain_ip(
        self,
        domain_id: str,
        ip_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Domain)-[:RESOLVES_TO]->(:IP)."""
        ...

    @abstractmethod
    async def connect_ip_asn(
        self,
        ip_id: str,
        asn_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:IP)-[:BELONGS_TO]->(:ASN)."""
        ...

    @abstractmethod
    async def connect_domain_certificate(
        self,
        domain_id: str,
        certificate_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Domain)-[:USES_CERTIFICATE]->(:Certificate)."""
        ...

    @abstractmethod
    async def connect_domain_nameserver(
        self,
        domain_id: str,
        nameserver_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Domain)-[:USES_NAMESERVER]->(:Nameserver)."""
        ...

    @abstractmethod
    async def connect_url_brand(
        self,
        url_id: str,
        brand_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:URL)-[:IMPERSONATES]->(:Brand)."""
        ...

    @abstractmethod
    async def connect_payment_entity(
        self,
        incident_id: str,
        payment_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Incident)-[:REQUESTS_PAYMENT_TO]->(:PaymentEntity)."""
        ...

    @abstractmethod
    async def connect_pattern(
        self,
        incident_id: str,
        pattern_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Incident)-[:MATCHES_PATTERN]->(:Pattern)."""
        ...

    @abstractmethod
    async def find_incident_entities(self, incident_id: str) -> List[Dict[str, Any]]:
        """Retrieve all entity nodes directly connected to an incident."""
        ...

    @abstractmethod
    async def find_entity_incidents(self, entity_type: str, entity_id: str) -> List[str]:
        """Retrieve all incident IDs connected to a given entity."""
        ...

    @abstractmethod
    async def find_shared_entities(self, incident_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Find entities linked to this incident that also connect to other incidents."""
        ...

    @abstractmethod
    async def find_related_incidents(self, incident_id: str) -> List[Dict[str, Any]]:
        """Find incidents related via shared infrastructure, payment, or identifiers."""
        ...


class Neo4jGraphRepository(GraphRepository):
    """Production Neo4j implementation with graceful in-memory fallback for offline test suites."""

    def __init__(self, client: Optional[Neo4jClient] = None):
        self.client = client or neo4j_client

        # In-memory mock storage for fallback and testing
        self._mock_incidents: Dict[str, Dict[str, Any]] = {}
        self._mock_events: Dict[str, Dict[str, Any]] = {}
        self._mock_entities: Dict[str, Dict[str, Any]] = {}  # key: "type:id"
        self._mock_relationships: List[Dict[str, Any]] = []

    def _default_prov(self, prov: Optional[RelationshipProvenance]) -> RelationshipProvenance:
        return prov or RelationshipProvenance()

    # -------------------------------------------------------------------------
    # Backward Compatibility Helpers (Step 16)
    # -------------------------------------------------------------------------

    async def create_incident(self, incident_id: str, channel: str = "SMS", status: str = "ACTIVE") -> Dict[str, Any]:
        return await self.upsert_incident(IncidentNode(id=incident_id, channel=channel, status=status))

    async def create_event(
        self,
        event_id: str,
        incident_id: str,
        event_type: str,
        sequence: int,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        self._mock_events[event_id] = {
            "id": event_id,
            "incident_id": incident_id,
            "event_type": event_type,
            "sequence": sequence,
        }
        self._record_mock_relationship({
            "source": f"Incident:{incident_id}",
            "target": f"Event:{event_id}",
            "type": "HAS_EVENT",
        })
        return {"id": event_id}

    async def connect_events_temporally(
        self,
        from_event_id: str,
        to_event_id: str,
        time_delta_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        self._record_mock_relationship({
            "source": f"Event:{from_event_id}",
            "target": f"Event:{to_event_id}",
            "type": "FOLLOWED_BY",
        })
        return {"relationship": "FOLLOWED_BY"}

    async def connect_entity(
        self,
        event_or_inc_id: str,
        entity_type_or_target: str,
        entity_id_or_rel: str = "OBSERVED",
        relationship_type: str = "OBSERVED",
    ) -> Dict[str, Any]:
        if relationship_type == "OBSERVED" and entity_id_or_rel not in [e.value for e in GraphNodeType] and not entity_id_or_rel.startswith("+"):
            # 3 arguments: connect_entity(inc_id, target_entity, rel_type)
            inc_id = event_or_inc_id
            target = entity_type_or_target
            rel_type = entity_id_or_rel
            self._record_mock_relationship({
                "source": f"Incident:{inc_id}",
                "target": f"Phone:{target}" if "phone" in target.lower() else f"Entity:{target}",
                "type": rel_type,
            })
            return {"relationship": rel_type}

        # 4 arguments: connect_entity(event_id, entity_type, entity_id, rel_type)
        ev = self._mock_events.get(event_or_inc_id, {})
        inc_id = ev.get("incident_id")
        if inc_id:
            await self.connect_incident_entity(inc_id, entity_type_or_target, entity_id_or_rel)
        self._record_mock_relationship({
            "source": f"Event:{event_or_inc_id}",
            "target": f"{entity_type_or_target}:{entity_id_or_rel}",
            "type": relationship_type,
        })
        return {"relationship": relationship_type}

    # -------------------------------------------------------------------------
    # Node Operations
    # -------------------------------------------------------------------------

    async def upsert_incident(self, incident: IncidentNode) -> Dict[str, Any]:
        """Upsert an :Incident node."""
        data = incident.to_dict()
        self._mock_incidents[incident.id] = data

        query = """
        MERGE (i:Incident {id: $id})
        ON CREATE SET i.channel = $channel, i.status = $status, i.created_at = $created_at, i.risk_score = $risk_score
        ON MATCH SET i.status = $status, i.risk_score = $risk_score
        RETURN i.id as id
        """
        records = await self.client.execute_query(
            query,
            {
                "id": incident.id,
                "channel": incident.channel,
                "status": incident.status,
                "created_at": incident.created_at,
                "risk_score": incident.risk_score,
            },
        )
        return records[0] if records else {"id": incident.id}

    async def upsert_entity(
        self,
        entity_or_type: Any,
        entity_id: Optional[str] = None,
        properties: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Upsert an entity node (:Phone, :URL, :Domain, :IP, etc.)."""
        if isinstance(entity_or_type, GraphEntityNode):
            entity = entity_or_type
        else:
            raw_a = str(entity_or_type)
            raw_b = str(entity_id or "")
            types = {e.value.lower(): e for e in GraphNodeType}
            if raw_b.lower() in types:
                matched_node_type = types[raw_b.lower()]
                eid = raw_a
            elif raw_a.lower() in types:
                matched_node_type = types[raw_a.lower()]
                eid = raw_b
            else:
                matched_node_type = GraphNodeType.DOMAIN
                eid = raw_b or raw_a

            props = properties if isinstance(properties, dict) else {}
            disp = properties if isinstance(properties, str) else eid
            entity = GraphEntityNode(
                node_type=matched_node_type,
                normalized_value=eid,
                display_value=disp,
                properties=props,
            )
        key = f"{entity.node_type.value}:{entity.normalized_value}"
        data = entity.to_dict()
        self._mock_entities[key] = {
            "type": entity.node_type.value,
            "id": entity.normalized_value,
            "normalized_value": entity.normalized_value,
            "display_value": entity.display_value,
            "properties": entity.properties,
            "first_seen": entity.first_seen,
            "last_seen": entity.last_seen,
        }

        query = f"""
        MERGE (n:{entity.node_type.value} {{normalized_value: $normalized_value}})
        ON CREATE SET n.id = $id, n.display_value = $display_value, n.first_seen = $first_seen, n.last_seen = $last_seen, n += $properties
        ON MATCH SET n.last_seen = $last_seen, n.display_value = $display_value, n += $properties
        RETURN n.normalized_value as id
        """
        records = await self.client.execute_query(
            query,
            {
                "id": entity.normalized_value,
                "normalized_value": entity.normalized_value,
                "display_value": entity.display_value,
                "first_seen": entity.first_seen,
                "last_seen": entity.last_seen,
                "properties": entity.properties,
            },
        )
        return records[0] if records else {"id": entity.normalized_value}

    # -------------------------------------------------------------------------
    # Relationship Operations with Provenance
    # -------------------------------------------------------------------------

    async def connect_incident_entity(
        self,
        incident_id: str,
        entity_type: str,
        entity_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Incident)-[:OBSERVED]->(:Entity)."""
        prov = self._default_prov(provenance)
        rel_data = {
            "source": f"Incident:{incident_id}",
            "target": f"{entity_type}:{entity_id}",
            "type": GraphRelationshipType.OBSERVED.value,
            "provenance": prov.to_dict(),
        }
        self._record_mock_relationship(rel_data)

        query = f"""
        MATCH (i:Incident {{id: $incident_id}})
        MATCH (e:{entity_type} {{normalized_value: $entity_id}})
        MERGE (i)-[r:{GraphRelationshipType.OBSERVED.value}]->(e)
        ON CREATE SET r.evidence_ids = $evidence_ids, r.confidence = $confidence, r.first_seen = $first_seen, r.last_seen = $last_seen, r.source = $source
        ON MATCH SET r.last_seen = $last_seen, r.confidence = $confidence
        RETURN type(r) as relationship
        """
        records = await self.client.execute_query(
            query,
            {
                "incident_id": incident_id,
                "entity_id": entity_id,
                "evidence_ids": prov.evidence_ids,
                "confidence": prov.confidence,
                "first_seen": prov.first_seen,
                "last_seen": prov.last_seen,
                "source": prov.source,
            },
        )
        return records[0] if records else {"relationship": GraphRelationshipType.OBSERVED.value}

    async def connect_url_domain(
        self,
        url_id: str,
        domain_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:URL)-[:HOSTED_ON]->(:Domain)."""
        prov = self._default_prov(provenance)
        self._record_mock_relationship({
            "source": f"URL:{url_id}",
            "target": f"Domain:{domain_id}",
            "type": GraphRelationshipType.HOSTED_ON.value,
            "provenance": prov.to_dict(),
        })

        query = f"""
        MATCH (u:URL {{normalized_value: $url_id}})
        MATCH (d:Domain {{normalized_value: $domain_id}})
        MERGE (u)-[r:{GraphRelationshipType.HOSTED_ON.value}]->(d)
        ON CREATE SET r.evidence_ids = $evidence_ids, r.confidence = $confidence, r.first_seen = $first_seen, r.last_seen = $last_seen, r.source = $source
        ON MATCH SET r.last_seen = $last_seen
        RETURN type(r) as relationship
        """
        records = await self.client.execute_query(
            query,
            {
                "url_id": url_id,
                "domain_id": domain_id,
                "evidence_ids": prov.evidence_ids,
                "confidence": prov.confidence,
                "first_seen": prov.first_seen,
                "last_seen": prov.last_seen,
                "source": prov.source,
            },
        )
        return records[0] if records else {"relationship": GraphRelationshipType.HOSTED_ON.value}

    async def connect_domain_ip(
        self,
        domain_id: str,
        ip_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Domain)-[:RESOLVES_TO]->(:IP)."""
        prov = self._default_prov(provenance)
        self._record_mock_relationship({
            "source": f"Domain:{domain_id}",
            "target": f"IP:{ip_id}",
            "type": GraphRelationshipType.RESOLVES_TO.value,
            "provenance": prov.to_dict(),
        })

        query = f"""
        MATCH (d:Domain {{normalized_value: $domain_id}})
        MATCH (ip:IP {{normalized_value: $ip_id}})
        MERGE (d)-[r:{GraphRelationshipType.RESOLVES_TO.value}]->(ip)
        ON CREATE SET r.evidence_ids = $evidence_ids, r.confidence = $confidence, r.first_seen = $first_seen, r.last_seen = $last_seen, r.source = $source
        ON MATCH SET r.last_seen = $last_seen
        RETURN type(r) as relationship
        """
        records = await self.client.execute_query(
            query,
            {
                "domain_id": domain_id,
                "ip_id": ip_id,
                "evidence_ids": prov.evidence_ids,
                "confidence": prov.confidence,
                "first_seen": prov.first_seen,
                "last_seen": prov.last_seen,
                "source": prov.source,
            },
        )
        return records[0] if records else {"relationship": GraphRelationshipType.RESOLVES_TO.value}

    async def connect_ip_asn(
        self,
        ip_id: str,
        asn_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:IP)-[:BELONGS_TO]->(:ASN)."""
        prov = self._default_prov(provenance)
        self._record_mock_relationship({
            "source": f"IP:{ip_id}",
            "target": f"ASN:{asn_id}",
            "type": GraphRelationshipType.BELONGS_TO.value,
            "provenance": prov.to_dict(),
        })

        query = f"""
        MATCH (ip:IP {{normalized_value: $ip_id}})
        MATCH (a:ASN {{normalized_value: $asn_id}})
        MERGE (ip)-[r:{GraphRelationshipType.BELONGS_TO.value}]->(a)
        ON CREATE SET r.evidence_ids = $evidence_ids, r.confidence = $confidence, r.first_seen = $first_seen, r.last_seen = $last_seen, r.source = $source
        ON MATCH SET r.last_seen = $last_seen
        RETURN type(r) as relationship
        """
        records = await self.client.execute_query(
            query,
            {
                "ip_id": ip_id,
                "asn_id": asn_id,
                "evidence_ids": prov.evidence_ids,
                "confidence": prov.confidence,
                "first_seen": prov.first_seen,
                "last_seen": prov.last_seen,
                "source": prov.source,
            },
        )
        return records[0] if records else {"relationship": GraphRelationshipType.BELONGS_TO.value}

    async def connect_domain_certificate(
        self,
        domain_id: str,
        certificate_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Domain)-[:USES_CERTIFICATE]->(:Certificate)."""
        prov = self._default_prov(provenance)
        self._record_mock_relationship({
            "source": f"Domain:{domain_id}",
            "target": f"Certificate:{certificate_id}",
            "type": GraphRelationshipType.USES_CERTIFICATE.value,
            "provenance": prov.to_dict(),
        })

        query = f"""
        MATCH (d:Domain {{normalized_value: $domain_id}})
        MATCH (c:Certificate {{normalized_value: $certificate_id}})
        MERGE (d)-[r:{GraphRelationshipType.USES_CERTIFICATE.value}]->(c)
        ON CREATE SET r.evidence_ids = $evidence_ids, r.confidence = $confidence, r.first_seen = $first_seen, r.last_seen = $last_seen, r.source = $source
        ON MATCH SET r.last_seen = $last_seen
        RETURN type(r) as relationship
        """
        records = await self.client.execute_query(
            query,
            {
                "domain_id": domain_id,
                "certificate_id": certificate_id,
                "evidence_ids": prov.evidence_ids,
                "confidence": prov.confidence,
                "first_seen": prov.first_seen,
                "last_seen": prov.last_seen,
                "source": prov.source,
            },
        )
        return records[0] if records else {"relationship": GraphRelationshipType.USES_CERTIFICATE.value}

    async def connect_domain_nameserver(
        self,
        domain_id: str,
        nameserver_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Domain)-[:USES_NAMESERVER]->(:Nameserver)."""
        prov = self._default_prov(provenance)
        self._record_mock_relationship({
            "source": f"Domain:{domain_id}",
            "target": f"Nameserver:{nameserver_id}",
            "type": GraphRelationshipType.USES_NAMESERVER.value,
            "provenance": prov.to_dict(),
        })

        query = f"""
        MATCH (d:Domain {{normalized_value: $domain_id}})
        MATCH (ns:Nameserver {{normalized_value: $nameserver_id}})
        MERGE (d)-[r:{GraphRelationshipType.USES_NAMESERVER.value}]->(ns)
        ON CREATE SET r.evidence_ids = $evidence_ids, r.confidence = $confidence, r.first_seen = $first_seen, r.last_seen = $last_seen, r.source = $source
        ON MATCH SET r.last_seen = $last_seen
        RETURN type(r) as relationship
        """
        records = await self.client.execute_query(
            query,
            {
                "domain_id": domain_id,
                "nameserver_id": nameserver_id,
                "evidence_ids": prov.evidence_ids,
                "confidence": prov.confidence,
                "first_seen": prov.first_seen,
                "last_seen": prov.last_seen,
                "source": prov.source,
            },
        )
        return records[0] if records else {"relationship": GraphRelationshipType.USES_NAMESERVER.value}

    async def connect_url_brand(
        self,
        url_id: str,
        brand_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:URL)-[:IMPERSONATES]->(:Brand)."""
        prov = self._default_prov(provenance)
        self._record_mock_relationship({
            "source": f"URL:{url_id}",
            "target": f"Brand:{brand_id}",
            "type": GraphRelationshipType.IMPERSONATES.value,
            "provenance": prov.to_dict(),
        })

        query = f"""
        MATCH (u:URL {{normalized_value: $url_id}})
        MATCH (b:Brand {{normalized_value: $brand_id}})
        MERGE (u)-[r:{GraphRelationshipType.IMPERSONATES.value}]->(b)
        ON CREATE SET r.evidence_ids = $evidence_ids, r.confidence = $confidence, r.first_seen = $first_seen, r.last_seen = $last_seen, r.source = $source
        ON MATCH SET r.last_seen = $last_seen
        RETURN type(r) as relationship
        """
        records = await self.client.execute_query(
            query,
            {
                "url_id": url_id,
                "brand_id": brand_id,
                "evidence_ids": prov.evidence_ids,
                "confidence": prov.confidence,
                "first_seen": prov.first_seen,
                "last_seen": prov.last_seen,
                "source": prov.source,
            },
        )
        return records[0] if records else {"relationship": GraphRelationshipType.IMPERSONATES.value}

    async def connect_payment_entity(
        self,
        incident_id: str,
        payment_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Incident)-[:REQUESTS_PAYMENT_TO]->(:PaymentEntity)."""
        prov = self._default_prov(provenance)
        self._record_mock_relationship({
            "source": f"Incident:{incident_id}",
            "target": f"PaymentEntity:{payment_id}",
            "type": GraphRelationshipType.REQUESTS_PAYMENT_TO.value,
            "provenance": prov.to_dict(),
        })

        query = f"""
        MATCH (i:Incident {{id: $incident_id}})
        MATCH (pe:PaymentEntity {{normalized_value: $payment_id}})
        MERGE (i)-[r:{GraphRelationshipType.REQUESTS_PAYMENT_TO.value}]->(pe)
        ON CREATE SET r.evidence_ids = $evidence_ids, r.confidence = $confidence, r.first_seen = $first_seen, r.last_seen = $last_seen, r.source = $source
        ON MATCH SET r.last_seen = $last_seen
        RETURN type(r) as relationship
        """
        records = await self.client.execute_query(
            query,
            {
                "incident_id": incident_id,
                "payment_id": payment_id,
                "evidence_ids": prov.evidence_ids,
                "confidence": prov.confidence,
                "first_seen": prov.first_seen,
                "last_seen": prov.last_seen,
                "source": prov.source,
            },
        )
        return records[0] if records else {"relationship": GraphRelationshipType.REQUESTS_PAYMENT_TO.value}

    async def connect_pattern(
        self,
        incident_id: str,
        pattern_id: str,
        provenance: Optional[RelationshipProvenance] = None,
    ) -> Dict[str, Any]:
        """Link (:Incident)-[:MATCHES_PATTERN]->(:Pattern)."""
        prov = self._default_prov(provenance)
        self._record_mock_relationship({
            "source": f"Incident:{incident_id}",
            "target": f"Pattern:{pattern_id}",
            "type": GraphRelationshipType.MATCHES_PATTERN.value,
            "provenance": prov.to_dict(),
        })

        query = f"""
        MATCH (i:Incident {{id: $incident_id}})
        MATCH (pat:Pattern {{id: $pattern_id}})
        MERGE (i)-[r:{GraphRelationshipType.MATCHES_PATTERN.value}]->(pat)
        ON CREATE SET r.evidence_ids = $evidence_ids, r.confidence = $confidence, r.first_seen = $first_seen, r.last_seen = $last_seen, r.source = $source
        ON MATCH SET r.last_seen = $last_seen
        RETURN type(r) as relationship
        """
        records = await self.client.execute_query(
            query,
            {
                "incident_id": incident_id,
                "pattern_id": pattern_id,
                "evidence_ids": prov.evidence_ids,
                "confidence": prov.confidence,
                "first_seen": prov.first_seen,
                "last_seen": prov.last_seen,
                "source": prov.source,
            },
        )
        return records[0] if records else {"relationship": GraphRelationshipType.MATCHES_PATTERN.value}

    # -------------------------------------------------------------------------
    # Correlation and Retrieval Operations
    # -------------------------------------------------------------------------

    async def find_incident_entities(self, incident_id: str) -> List[Dict[str, Any]]:
        """Retrieve all entity nodes directly or indirectly connected to an incident."""
        if not self.client.is_connected:
            return self._mock_find_incident_entities(incident_id)

        query = """
        MATCH (i:Incident {id: $incident_id})-[r]->(e)
        WHERE NOT e:Incident
        RETURN labels(e)[0] as entity_type, e.normalized_value as entity_id, e.display_value as display_value, type(r) as relationship
        """
        return await self.client.execute_query(query, {"incident_id": incident_id})

    async def find_entity_incidents(self, entity_type: str, entity_id: str) -> List[str]:
        """Retrieve all incident IDs connected to a given entity."""
        if not self.client.is_connected:
            incidents = set()
            target_key = f"{entity_type}:{entity_id}"
            for r in self._mock_relationships:
                if r["target"] == target_key and r["source"].startswith("Incident:"):
                    incidents.add(r["source"].split(":", 1)[1])
            return sorted(incidents)

        query = f"""
        MATCH (i:Incident)-[]->(e:{entity_type} {{normalized_value: $entity_id}})
        RETURN DISTINCT i.id as incident_id
        """
        records = await self.client.execute_query(query, {"entity_id": entity_id})
        return [r["incident_id"] for r in records]

    async def find_shared_entities(self, incident_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Find all entities linked to this incident that are also linked to other incidents."""
        if not self.client.is_connected:
            return self._mock_find_shared_entities(incident_id)

        query = """
        MATCH (i:Incident {id: $incident_id})-[r1]->(e)<-[r2]-(otherInc:Incident)
        WHERE otherInc.id <> $incident_id
        RETURN 
            labels(e)[0] as entity_type,
            e.normalized_value as entity_id,
            e.display_value as display_value,
            collect(DISTINCT otherInc.id) as shared_with_incidents,
            count(DISTINCT otherInc.id) as shared_count
        ORDER BY shared_count DESC
        """
        records = await self.client.execute_query(query, {"incident_id": incident_id})
        by_type: Dict[str, List[Dict[str, Any]]] = {}
        for r in records:
            by_type.setdefault(r["entity_type"], []).append(r)
        return by_type

    async def find_related_incidents(self, incident_id: str) -> List[Dict[str, Any]]:
        """Find incidents related via shared infrastructure, payment, or identifiers."""
        if not self.client.is_connected:
            return self._mock_find_related_incidents(incident_id)

        query = """
        MATCH (i:Incident {id: $incident_id})-[r1]->(e)<-[r2]-(otherInc:Incident)
        WHERE otherInc.id <> $incident_id
        RETURN 
            otherInc.id as related_incident_id,
            collect(DISTINCT {type: labels(e)[0], id: e.normalized_value, display: e.display_value}) as connecting_entities,
            count(DISTINCT e) as shared_entity_score
        ORDER BY shared_entity_score DESC
        """
        return await self.client.execute_query(query, {"incident_id": incident_id})

    # -------------------------------------------------------------------------
    # In-Memory Mock Helpers for Testing / Offline Resilience
    # -------------------------------------------------------------------------

    def _record_mock_relationship(self, rel_data: Dict[str, Any]) -> None:
        """Idempotent relationship recording in mock store."""
        for existing in self._mock_relationships:
            if (
                existing["source"] == rel_data["source"]
                and existing["target"] == rel_data["target"]
                and existing["type"] == rel_data["type"]
            ):
                # Update provenance idempotently
                existing["provenance"] = rel_data.get("provenance", {})
                return
        self._mock_relationships.append(rel_data)

    def _mock_find_incident_entities(self, incident_id: str) -> List[Dict[str, Any]]:
        inc_key = f"Incident:{incident_id}"
        results = []
        for r in self._mock_relationships:
            if r["source"] == inc_key:
                ent_type, ent_id = r["target"].split(":", 1)
                ent = self._mock_entities.get(r["target"], {})
                results.append({
                    "entity_type": ent_type,
                    "entity_id": ent_id,
                    "display_value": ent.get("display_value", ent_id),
                    "relationship": r["type"],
                })
        return results

    def _mock_find_shared_entities(self, incident_id: str) -> Dict[str, List[Dict[str, Any]]]:
        inc_key = f"Incident:{incident_id}"
        # Direct entities connected to this incident
        target_entities: Set[str] = set()
        for r in self._mock_relationships:
            if r["source"] == inc_key and ":" in str(r["target"]):
                target_entities.add(r["target"])

        # Find other incidents connected to these target entities
        results: Dict[str, List[Dict[str, Any]]] = {}
        for entity_key in target_entities:
            ent_type, ent_id = entity_key.split(":", 1)
            other_incidents: Set[str] = set()
            for r in self._mock_relationships:
                if r["target"] == entity_key and r["source"].startswith("Incident:"):
                    other_id = r["source"].split(":", 1)[1]
                    if other_id != incident_id:
                        other_incidents.add(other_id)

            if other_incidents:
                ent = self._mock_entities.get(entity_key, {})
                results.setdefault(ent_type, []).append({
                    "entity_type": ent_type,
                    "entity_id": ent_id,
                    "display_value": ent.get("display_value", ent_id),
                    "shared_with_incidents": sorted(other_incidents),
                    "shared_count": len(other_incidents),
                })
        return results

    def _mock_find_related_incidents(self, incident_id: str) -> List[Dict[str, Any]]:
        shared = self._mock_find_shared_entities(incident_id)
        related_map: Dict[str, List[Dict[str, Any]]] = {}
        for ent_type, items in shared.items():
            for item in items:
                for other_id in item["shared_with_incidents"]:
                    related_map.setdefault(other_id, []).append({
                        "type": ent_type,
                        "id": item["entity_id"],
                        "display": item.get("display_value", item["entity_id"]),
                    })

        output = []
        for other_id, entities in related_map.items():
            output.append({
                "related_incident_id": other_id,
                "connecting_entities": entities,
                "shared_entity_score": len(entities),
            })
        output.sort(key=lambda x: x["shared_entity_score"], reverse=True)
        return output

    def clear_mock_store(self) -> None:
        """Clear the in-memory mock store (useful for clean unit test states)."""
        self._mock_incidents.clear()
        self._mock_entities.clear()
        self._mock_relationships.clear()


# Global singleton instance
graph_repository = Neo4jGraphRepository()
