"""Unit tests for canonical ScamGraph AI schemas."""

import unittest
from datetime import datetime, timezone
from packages.schemas import (
    Event,
    EventType,
    ChannelType,
    MessagePayload,
    UrlPayload,
    PaymentPayload,
    EvidenceSignal,
    SignalDimension,
    SignalSeverity,
    ProvenanceRecord,
    ScamJourney,
    JourneyStep,
    JourneyStage,
    AssessmentResult,
    RiskLevel,
    EvidenceConfidence,
    InterventionAction,
    AdaptiveIntervention,
    ExplainabilityReport,
    ScamFingerprint,
    CytoscapeGraph,
    CytoscapeNode,
    CytoscapeNodeData,
    CytoscapeEdge,
    CytoscapeEdgeData,
    GraphNodeType,
)


class TestScamGraphSchemas(unittest.TestCase):
    def test_event_creation(self):
        msg = MessagePayload(
            sender_id="+919876543210",
            recipient_id_hash="user_hash_123",
            text="Dear user, your electricity power will be disconnected at 9:30 PM. Call officer immediately.",
            channel=ChannelType.SMS,
        )
        event = Event(
            incident_id="inc_001",
            sequence_number=1,
            event_type=EventType.MESSAGE_RECEIVED,
            payload=msg,
        )
        self.assertEqual(event.incident_id, "inc_001")
        self.assertEqual(event.sequence_number, 1)
        self.assertEqual(event.event_type, EventType.MESSAGE_RECEIVED)
        self.assertIn("electricity", event.payload.text)

    def test_evidence_signal_and_provenance(self):
        prov = ProvenanceRecord(
            source_service="services/investigation",
            detector_name="TinyFish API",
            target_artifact="http://mahavitaran-billupdate.info",
            raw_evidence={"domain_age_days": 1, "has_otp_field": True},
        )
        sig = EvidenceSignal(
            incident_id="inc_001",
            dimension=SignalDimension.URL,
            signal_type="NEW_DOMAIN_BRAND_IMPERSONATION",
            severity=SignalSeverity.HIGH,
            confidence=0.95,
            weight=1.5,
            description="Domain registered 1 day ago imitating electricity board",
            provenance=prov,
        )
        self.assertEqual(sig.severity, SignalSeverity.HIGH)
        self.assertEqual(sig.provenance.raw_evidence["domain_age_days"], 1)
        self.assertFalse(sig.is_counter_evidence)

    def test_assessment_dual_axis_and_insufficient_evidence(self):
        intervention = AdaptiveIntervention(
            action=InterventionAction.PRE_PAYMENT_INTERVENTION,
            friction_delay_seconds=10,
            banner_title="High Risk Payment Attempt",
            banner_message="The recipient handle does not match the utility entity you were contacted about.",
        )
        explain = ExplainabilityReport(
            what_happened="SMS received -> fraudulent site clicked -> UPI collect request triggered.",
            why_suspicious="Impersonating electricity utility with newly registered domain and personal UPI handle.",
            when_risk_increased="Inflection point: user clicked shortened link to newly created domain.",
            which_evidence_supports=["URGENCY_PRESSURE", "TYPOSQUATTING_DOMAIN", "VPA_MISMATCH"],
            which_sources_produced=["NLP Message Model", "TinyFish API", "Payment Handle Engine"],
            what_counter_evidence_exists=[],
            how_confident="HIGH: Corroborated across 3 independent dimensions (SEMANTIC, URL, PAYMENT).",
            what_to_do_next="Decline the collect request. Pay bills solely through official utility portal.",
        )
        assessment = AssessmentResult(
            incident_id="inc_001",
            risk_level=RiskLevel.HIGH,
            evidence_confidence=EvidenceConfidence.HIGH,
            risk_score=0.92,
            confidence_score=0.88,
            is_insufficient_evidence=False,
            intervention=intervention,
            explainability=explain,
        )
        self.assertEqual(assessment.risk_level, RiskLevel.HIGH)
        self.assertEqual(assessment.evidence_confidence, EvidenceConfidence.HIGH)
        self.assertEqual(assessment.intervention.friction_delay_seconds, 10)

    def test_cytoscape_serialization(self):
        node = CytoscapeNode(
            data=CytoscapeNodeData(
                id="step_1",
                label="Unknown SMS Contact",
                node_type=GraphNodeType.JOURNEY_STEP,
                severity="HIGH",
            )
        )
        edge = CytoscapeEdge(
            data=CytoscapeEdgeData(
                id="e1",
                source="step_1",
                target="step_2",
                label="FOLLOWED_BY",
                relationship_type="FOLLOWED_BY",
                time_delta_seconds=120,
            )
        )
        graph = CytoscapeGraph(nodes=[node], edges=[edge])
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(graph.nodes[0].data.id, "step_1")
        self.assertEqual(graph.edges[0].data.time_delta_seconds, 120)


if __name__ == "__main__":
    unittest.main()
