"""Incident Fusion and Cross-Incident Correlation Engine.

Implements entity resolution and community detection principles (harvested
from demo-fraud-detection-with-p2p) to find shared infrastructure across victims.
"""

from typing import Any, Dict, List
from packages.schemas import EvidenceSignal, SignalDimension, SignalSeverity, ProvenanceRecord


class IncidentFusionEngine:
    """Detects cross-incident linkages such as shared VPAs, phone numbers, and domains."""

    @staticmethod
    def evaluate_correlations(incident_id: str, correlation_records: List[Dict[str, Any]]) -> List[EvidenceSignal]:
        """Transforms graph correlation query records into canonical Evidence Signals."""
        signals: List[EvidenceSignal] = []

        for record in correlation_records:
            phone_shares = record.get("phone_shares", [])
            for share in phone_shares:
                other_inc = share.get("other_incident_id")
                shared_phone = share.get("shared_entity")
                if other_inc and shared_phone:
                    signals.append(
                        EvidenceSignal(
                            incident_id=incident_id,
                            dimension=SignalDimension.HISTORICAL,
                            signal_type="REUSED_SENDER_PHONE_ACROSS_VICTIMS",
                            severity=SignalSeverity.HIGH,
                            confidence=0.90,
                            weight=1.6,
                            description=f"Sender number {shared_phone} was previously observed targeting incident {other_inc}",
                            provenance=ProvenanceRecord(
                                source_service="services/graph-engine",
                                detector_name="Neo4j Entity Resolution",
                                target_artifact=shared_phone,
                                raw_evidence={"matched_incident_id": other_inc},
                            ),
                        )
                    )

            vpa_shares = record.get("vpa_shares", [])
            for share in vpa_shares:
                other_inc = share.get("other_incident_id")
                shared_vpa = share.get("shared_entity")
                if other_inc and shared_vpa:
                    signals.append(
                        EvidenceSignal(
                            incident_id=incident_id,
                            dimension=SignalDimension.PAYMENT,
                            signal_type="CROSS_INCIDENT_UPI_VPA_REUSE",
                            severity=SignalSeverity.CRITICAL,
                            confidence=0.98,
                            weight=2.0,
                            description=f"Target UPI VPA '{shared_vpa}' was previously flagged in incident {other_inc}",
                            provenance=ProvenanceRecord(
                                source_service="services/graph-engine",
                                detector_name="Neo4j Entity Resolution",
                                target_artifact=shared_vpa,
                                raw_evidence={"matched_incident_id": other_inc},
                            ),
                        )
                    )

        return signals
