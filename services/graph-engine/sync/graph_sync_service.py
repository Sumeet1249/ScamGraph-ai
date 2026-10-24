"""Graph Synchronization Service for ScamGraph AI (Step 23).

Transforms incidents, extracted entities, evidence signals, and pattern matches
into normalized Neo4j graph nodes and provenance-backed relationships.

Safety Rule:
Graph synchronization failure must NEVER crash incident assessment or ingestion.
If Neo4j is unavailable, returns GraphSyncResult with status="UNAVAILABLE".
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from services.graph_engine.models.graph_models import (
    GraphEntityNode,
    GraphNodeType,
    GraphSyncResult,
    IncidentNode,
    RelationshipProvenance,
)
from services.graph_engine.neo4j.repository import GraphRepository, graph_repository
from services.graph_engine.normalization.entity_normalizer import (
    EntityNormalizer,
    entity_normalizer,
)

logger = logging.getLogger("graph_engine.sync")


class GraphSyncService:
    """Synchronizes multi-source incident telemetry into the Neo4j Evidence Graph."""

    def __init__(
        self,
        repository: Optional[GraphRepository] = None,
        normalizer: Optional[EntityNormalizer] = None,
    ):
        self.repo = repository or graph_repository
        self.normalizer = normalizer or entity_normalizer

    async def sync_incident(
        self,
        incident: Any,
        entities: Optional[List[Dict[str, Any]]] = None,
        evidence: Optional[List[Any]] = None,
        pattern_matches: Optional[List[Any]] = None,
        scam_fingerprint: Optional[Any] = None,
    ) -> GraphSyncResult:
        """Synchronize incident, infrastructure entities, payment identifiers, and patterns.

        Guaranteed non-throwing: returns status="UNAVAILABLE" on Neo4j/system failure.
        """
        # Extract incident ID
        if isinstance(incident, dict):
            incident_id = str(incident.get("id") or incident.get("incident_id") or "")
            channel = str(incident.get("channel", "UNKNOWN"))
            status = str(incident.get("status", "ACTIVE"))
            risk_score = incident.get("risk_score")
        else:
            incident_id = str(getattr(incident, "id", getattr(incident, "incident_id", "")))
            channel = str(getattr(incident, "channel", "UNKNOWN"))
            status = str(getattr(incident, "status", "ACTIVE"))
            risk_score = getattr(incident, "risk_score", None)

        if not incident_id:
            return GraphSyncResult(
                status="UNAVAILABLE",
                incident_id="unknown",
                error="Missing incident identifier.",
            )

        nodes_synced = 0
        rels_synced = 0

        try:
            # 1. Upsert Incident node
            inc_node = IncidentNode(
                id=incident_id,
                channel=channel,
                status=status,
                risk_score=float(risk_score) if risk_score is not None else None,
            )
            await self.repo.upsert_incident(inc_node)
            nodes_synced += 1

            # Build evidence ID lookup and default provenance
            evidence_ids: List[str] = []
            if evidence:
                for ev in evidence:
                    if isinstance(ev, dict):
                        eid = ev.get("signal_id") or ev.get("id")
                    else:
                        eid = getattr(ev, "signal_id", getattr(ev, "id", None))
                    if eid:
                        evidence_ids.append(str(eid))

            base_provenance = RelationshipProvenance(
                evidence_ids=evidence_ids,
                confidence=0.95,
                source="investigation_pipeline",
            )

            # 2. Process extracted entities
            normalized_urls: List[str] = []
            normalized_domains: List[str] = []
            normalized_ips: List[str] = []

            for ent in (entities or []):
                ent_type = str(ent.get("type") or ent.get("entity_type") or "").upper()
                raw_val = str(ent.get("value") or ent.get("display_value") or "").strip()
                if not raw_val:
                    continue

                if ent_type in ("PHONE", "TELEPHONE", "MOBILE"):
                    norm, disp = self.normalizer.normalize_phone(raw_val)
                    if norm:
                        node = GraphEntityNode(
                            node_type=GraphNodeType.PHONE,
                            normalized_value=norm,
                            display_value=disp,
                        )
                        await self.repo.upsert_entity(node)
                        nodes_synced += 1
                        await self.repo.connect_incident_entity(
                            incident_id, GraphNodeType.PHONE.value, norm, base_provenance
                        )
                        rels_synced += 1

                elif ent_type in ("URL", "LINK"):
                    norm, disp = self.normalizer.normalize_url(raw_val)
                    if norm:
                        normalized_urls.append(norm)
                        node = GraphEntityNode(
                            node_type=GraphNodeType.URL,
                            normalized_value=norm,
                            display_value=disp,
                        )
                        await self.repo.upsert_entity(node)
                        nodes_synced += 1
                        await self.repo.connect_incident_entity(
                            incident_id, GraphNodeType.URL.value, norm, base_provenance
                        )
                        rels_synced += 1

                        # Automatically derive domain from URL if not explicitly supplied
                        dom_norm, dom_disp = self.normalizer.normalize_domain(norm)
                        if dom_norm:
                            dom_node = GraphEntityNode(
                                node_type=GraphNodeType.DOMAIN,
                                normalized_value=dom_norm,
                                display_value=dom_disp,
                            )
                            await self.repo.upsert_entity(dom_node)
                            nodes_synced += 1
                            await self.repo.connect_url_domain(norm, dom_norm, base_provenance)
                            rels_synced += 1
                            normalized_domains.append(dom_norm)

                elif ent_type == "DOMAIN":
                    norm, disp = self.normalizer.normalize_domain(raw_val)
                    if norm:
                        normalized_domains.append(norm)
                        node = GraphEntityNode(
                            node_type=GraphNodeType.DOMAIN,
                            normalized_value=norm,
                            display_value=disp,
                        )
                        await self.repo.upsert_entity(node)
                        nodes_synced += 1
                        await self.repo.connect_incident_entity(
                            incident_id, GraphNodeType.DOMAIN.value, norm, base_provenance
                        )
                        rels_synced += 1

                elif ent_type in ("IP", "IP_ADDRESS"):
                    norm, disp = self.normalizer.normalize_ip(raw_val)
                    if norm:
                        normalized_ips.append(norm)
                        node = GraphEntityNode(
                            node_type=GraphNodeType.IP,
                            normalized_value=norm,
                            display_value=disp,
                        )
                        await self.repo.upsert_entity(node)
                        nodes_synced += 1
                        # Connect domain to IP if domain was observed
                        for d_norm in normalized_domains:
                            await self.repo.connect_domain_ip(d_norm, norm, base_provenance)
                            rels_synced += 1

                elif ent_type in ("PAYMENT", "UPI", "VPA", "BANK_ACCOUNT"):
                    ptype = "UPI" if ("@" in raw_val or ent_type == "UPI") else "BANK_ACCOUNT"
                    norm, disp = self.normalizer.normalize_payment_entity(raw_val, ptype)
                    if norm:
                        node = GraphEntityNode(
                            node_type=GraphNodeType.PAYMENT_ENTITY,
                            normalized_value=norm,
                            display_value=disp,
                            properties={"payment_type": ptype},
                        )
                        await self.repo.upsert_entity(node)
                        nodes_synced += 1
                        await self.repo.connect_payment_entity(incident_id, norm, base_provenance)
                        rels_synced += 1

                elif ent_type == "ASN":
                    norm, disp = self.normalizer.normalize_asn(raw_val)
                    if norm:
                        node = GraphEntityNode(
                            node_type=GraphNodeType.ASN,
                            normalized_value=norm,
                            display_value=disp,
                        )
                        await self.repo.upsert_entity(node)
                        nodes_synced += 1
                        for ip_norm in normalized_ips:
                            await self.repo.connect_ip_asn(ip_norm, norm, base_provenance)
                            rels_synced += 1

                elif ent_type in ("CERTIFICATE", "SSL"):
                    norm, disp = self.normalizer.normalize_certificate(raw_val)
                    if norm:
                        node = GraphEntityNode(
                            node_type=GraphNodeType.CERTIFICATE,
                            normalized_value=norm,
                            display_value=disp,
                        )
                        await self.repo.upsert_entity(node)
                        nodes_synced += 1
                        for d_norm in normalized_domains:
                            await self.repo.connect_domain_certificate(d_norm, norm, base_provenance)
                            rels_synced += 1

                elif ent_type in ("NAMESERVER", "NS"):
                    norm, disp = self.normalizer.normalize_nameserver(raw_val)
                    if norm:
                        node = GraphEntityNode(
                            node_type=GraphNodeType.NAMESERVER,
                            normalized_value=norm,
                            display_value=disp,
                        )
                        await self.repo.upsert_entity(node)
                        nodes_synced += 1
                        for d_norm in normalized_domains:
                            await self.repo.connect_domain_nameserver(d_norm, norm, base_provenance)
                            rels_synced += 1

                elif ent_type == "BRAND":
                    norm, disp = self.normalizer.normalize_brand(raw_val)
                    if norm:
                        node = GraphEntityNode(
                            node_type=GraphNodeType.BRAND,
                            normalized_value=norm,
                            display_value=disp,
                        )
                        await self.repo.upsert_entity(node)
                        nodes_synced += 1
                        for u_norm in normalized_urls:
                            await self.repo.connect_url_brand(u_norm, norm, base_provenance)
                            rels_synced += 1

            # 3. Process pattern matches
            if pattern_matches:
                for pat in pattern_matches:
                    pat_id = (
                        pat.get("pattern_id") or pat.get("id") or pat.get("pattern_code")
                        if isinstance(pat, dict)
                        else getattr(pat, "pattern_id", getattr(pat, "id", None))
                    )
                    if pat_id:
                        pat_node = GraphEntityNode(
                            node_type=GraphNodeType.PATTERN,
                            normalized_value=str(pat_id),
                            display_value=str(pat_id),
                        )
                        await self.repo.upsert_entity(pat_node)
                        nodes_synced += 1
                        await self.repo.connect_pattern(incident_id, str(pat_id), base_provenance)
                        rels_synced += 1

            # 4. Query shared entities and related incidents
            shared_entities = await self.repo.find_shared_entities(incident_id)
            related_incidents = await self.repo.find_related_incidents(incident_id)

            return GraphSyncResult(
                status="SUCCESS",
                incident_id=incident_id,
                nodes_synced=nodes_synced,
                relationships_synced=rels_synced,
                shared_entities=shared_entities,
                related_incidents=related_incidents,
            )

        except Exception as e:
            logger.warning(
                f"Graph synchronization degraded/unavailable for incident {incident_id}: {e}"
            )
            return GraphSyncResult(
                status="UNAVAILABLE",
                incident_id=incident_id,
                nodes_synced=nodes_synced,
                relationships_synced=rels_synced,
                error=str(e),
            )


# Default singleton instance
graph_sync_service = GraphSyncService()
