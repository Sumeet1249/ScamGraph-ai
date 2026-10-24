"""Entity Correlation Service (Step 16).

Computes explainable graph correlation features:
- shared_phone_count
- shared_domain_count
- shared_ip_count
- shared_payment_entity_count
- shared_nameserver_count
- shared_certificate_count

Produces explainable graph paths and canonical EvidenceSignal objects.
"""

from typing import Any, Dict, List, Optional
from packages.schemas import EvidenceSignal, SignalDimension, SignalSeverity, ProvenanceRecord
from services.graph_engine.neo4j.repository import GraphRepository, graph_repository


class EntityCorrelationReport:
    def __init__(
        self,
        incident_id: str,
        shared_phone_count: int = 0,
        shared_domain_count: int = 0,
        shared_ip_count: int = 0,
        shared_payment_entity_count: int = 0,
        shared_nameserver_count: int = 0,
        shared_certificate_count: int = 0,
        explanation_paths: Optional[List[str]] = None,
        signals: Optional[List[EvidenceSignal]] = None,
    ):
        self.incident_id = incident_id
        self.shared_phone_count = shared_phone_count
        self.shared_domain_count = shared_domain_count
        self.shared_ip_count = shared_ip_count
        self.shared_payment_entity_count = shared_payment_entity_count
        self.shared_nameserver_count = shared_nameserver_count
        self.shared_certificate_count = shared_certificate_count
        self.explanation_paths = explanation_paths or []
        self.signals = signals or []

    @property
    def total_shared_entities(self) -> int:
        return (
            self.shared_phone_count
            + self.shared_domain_count
            + self.shared_ip_count
            + self.shared_payment_entity_count
            + self.shared_nameserver_count
            + self.shared_certificate_count
        )


class EntityCorrelationService:
    """Evaluates graph-based entity sharing and resolution across incidents."""

    def __init__(self, repo: Optional[GraphRepository] = None):
        self.repo = repo or graph_repository

    async def correlate_incident(self, incident_id: str) -> EntityCorrelationReport:
        """Finds shared entities and returns an explainable correlation report with canonical signals."""
        shared = await self.repo.find_shared_entities(incident_id)

        phone_items = shared.get("Phone", [])
        domain_items = shared.get("Domain", [])
        ip_items = shared.get("IP", [])
        payment_items = shared.get("PaymentEntity", [])
        ns_items = shared.get("Nameserver", [])
        cert_items = shared.get("Certificate", [])

        explanation_paths: List[str] = []
        signals: List[EvidenceSignal] = []

        # 1. Shared Payment Entities (VPA / Bank accounts) -> CRITICAL severity
        for item in payment_items:
            vpa = item["entity_id"]
            others = item["shared_with_incidents"]
            path_str = f"Incident ({incident_id}) -> PaymentEntity ({vpa}) <- Incident(s) ({', '.join(others)})"
            explanation_paths.append(path_str)
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.PAYMENT,
                    signal_type="SHARED_PAYMENT_ENTITY_ACROSS_INCIDENTS",
                    severity=SignalSeverity.CRITICAL,
                    confidence=0.98,
                    weight=2.0,
                    description=f"Target UPI/payment handle '{vpa}' is shared with {len(others)} other incident(s): {', '.join(others[:3])}",
                    provenance=ProvenanceRecord(
                        source_service="services/graph-engine",
                        detector_name="EntityCorrelationService",
                        target_artifact=vpa,
                        raw_evidence={"shared_with_incidents": others, "graph_path": path_str},
                    ),
                )
            )

        # 2. Shared Phone Numbers -> HIGH severity
        for item in phone_items:
            phone = item["entity_id"]
            others = item["shared_with_incidents"]
            path_str = f"Incident ({incident_id}) -> Phone ({phone}) <- Incident(s) ({', '.join(others)})"
            explanation_paths.append(path_str)
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.INFRASTRUCTURE,
                    signal_type="SHARED_PHONE_NUMBER_ACROSS_INCIDENTS",
                    severity=SignalSeverity.HIGH,
                    confidence=0.92,
                    weight=1.7,
                    description=f"Sender phone number '{phone}' was also observed in {len(others)} other incident(s)",
                    provenance=ProvenanceRecord(
                        source_service="services/graph-engine",
                        detector_name="EntityCorrelationService",
                        target_artifact=phone,
                        raw_evidence={"shared_with_incidents": others, "graph_path": path_str},
                    ),
                )
            )

        # 3. Shared Domains -> HIGH severity
        for item in domain_items:
            dom = item["entity_id"]
            others = item["shared_with_incidents"]
            path_str = f"Incident ({incident_id}) -> Domain ({dom}) <- Incident(s) ({', '.join(others)})"
            explanation_paths.append(path_str)
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.INFRASTRUCTURE,
                    signal_type="SHARED_DOMAIN_ACROSS_INCIDENTS",
                    severity=SignalSeverity.HIGH,
                    confidence=0.90,
                    weight=1.6,
                    description=f"Phishing domain '{dom}' is actively reused across {len(others)} incident(s)",
                    provenance=ProvenanceRecord(
                        source_service="services/graph-engine",
                        detector_name="EntityCorrelationService",
                        target_artifact=dom,
                        raw_evidence={"shared_with_incidents": others, "graph_path": path_str},
                    ),
                )
            )

        # 4. Shared IP, NS, Certs -> MEDIUM severity
        for item in ip_items:
            ip = item["entity_id"]
            others = item["shared_with_incidents"]
            explanation_paths.append(f"Incident ({incident_id}) -> IP ({ip}) <- Incident(s) ({', '.join(others)})")

        return EntityCorrelationReport(
            incident_id=incident_id,
            shared_phone_count=len(phone_items),
            shared_domain_count=len(domain_items),
            shared_ip_count=len(ip_items),
            shared_payment_entity_count=len(payment_items),
            shared_nameserver_count=len(ns_items),
            shared_certificate_count=len(cert_items),
            explanation_paths=explanation_paths,
            signals=signals,
        )


# Global instance
entity_correlation_service = EntityCorrelationService()
