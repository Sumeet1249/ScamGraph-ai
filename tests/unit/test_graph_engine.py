import unittest
import importlib

cypher_builder_mod = importlib.import_module("services.graph-engine.neo4j.cypher_builder")
CypherQueryBuilder = cypher_builder_mod.CypherQueryBuilder

fusion_mod = importlib.import_module("services.graph-engine.correlation.fusion")
IncidentFusionEngine = fusion_mod.IncidentFusionEngine
from packages.schemas import SignalDimension, SignalSeverity


class TestGraphEngine(unittest.TestCase):
    def test_merge_incident_query(self):
        built = CypherQueryBuilder.merge_incident("inc_test_101")
        self.assertIn("MERGE (i:Incident {id: $incident_id})", built["query"])
        self.assertEqual(built["params"]["incident_id"], "inc_test_101")

    def test_add_journey_step_query(self):
        built = CypherQueryBuilder.add_journey_step(
            incident_id="inc_test_101",
            step_id="step_01",
            sequence=1,
            stage="INITIAL_CONTACT",
            title="SMS Received",
            prev_step_id=None,
        )
        self.assertIn("MERGE (s:JourneyStep {stepId: $step_id})", built["query"])
        self.assertEqual(built["params"]["step_id"], "step_01")

    def test_linked_step_query(self):
        built = CypherQueryBuilder.add_journey_step(
            incident_id="inc_test_101",
            step_id="step_02",
            sequence=2,
            stage="PAYMENT_REQUEST",
            title="UPI Collect",
            prev_step_id="step_01",
            time_delta_seconds=45,
        )
        self.assertIn("MERGE (prev)-[r:FOLLOWED_BY]->(s)", built["query"])
        self.assertEqual(built["params"]["time_delta_seconds"], 45)

    def test_incident_fusion_signals(self):
        mock_records = [
            {
                "phone_shares": [
                    {"other_incident_id": "inc_victim_99", "shared_entity": "+919876543210", "type": "PHONE"}
                ],
                "vpa_shares": [
                    {"other_incident_id": "inc_victim_99", "shared_entity": "mule@paytm", "type": "VPA"}
                ],
            }
        ]
        signals = IncidentFusionEngine.evaluate_correlations("inc_victim_100", mock_records)
        self.assertEqual(len(signals), 2)

        phone_sig = signals[0]
        self.assertEqual(phone_sig.dimension, SignalDimension.HISTORICAL)
        self.assertEqual(phone_sig.severity, SignalSeverity.HIGH)
        self.assertEqual(phone_sig.provenance.target_artifact, "+919876543210")

        vpa_sig = signals[1]
        self.assertEqual(vpa_sig.dimension, SignalDimension.PAYMENT)
        self.assertEqual(vpa_sig.severity, SignalSeverity.CRITICAL)
        self.assertEqual(vpa_sig.provenance.target_artifact, "mule@paytm")


if __name__ == "__main__":
    unittest.main()
