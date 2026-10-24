"""Unit tests for Step 12: Scam Journey Graph Neo4j relationships."""

import unittest
import importlib

journey_mod = importlib.import_module("services.graph-engine.neo4j.journey_graph")
JourneyGraphBuilder = journey_mod.JourneyGraphBuilder


class TestJourneyGraphStep12(unittest.TestCase):
    def test_incident_has_event_and_followed_by(self):
        built = JourneyGraphBuilder.query_merge_incident_and_event(
            incident_id="inc_step12_01",
            event_id="ev_01",
            event_type="MESSAGE_RECEIVED",
            sequence=1,
            prev_event_id=None,
        )
        self.assertIn("MERGE (i)-[:HAS_EVENT]->(e)", built["query"])
        self.assertNotIn("FOLLOWED_BY", built["query"])

        built_next = JourneyGraphBuilder.query_merge_incident_and_event(
            incident_id="inc_step12_01",
            event_id="ev_02",
            event_type="LINK_CLICKED",
            sequence=2,
            prev_event_id="ev_01",
            time_delta_seconds=30,
        )
        self.assertIn("MERGE (prev)-[r:FOLLOWED_BY]->(e)", built_next["query"])
        self.assertEqual(built_next["params"]["time_delta_seconds"], 30)

    def test_message_contains_url(self):
        built = JourneyGraphBuilder.query_link_message_and_url(
            event_id="ev_01",
            message_id="msg_01",
            text_snippet="Update KYC bill immediately",
            raw_url="http://sbi-update.info",
        )
        self.assertIn("MERGE (m:Message {id: $message_id})", built["query"])
        self.assertIn("MERGE (u:URL {rawUrl: $raw_url})", built["query"])
        self.assertIn("MERGE (m)-[:CONTAINS]->(u)", built["query"])

    def test_url_infrastructure_and_brand_impersonation(self):
        built = JourneyGraphBuilder.query_link_url_infrastructure(
            raw_url="http://sbi-update.info",
            domain_name="sbi-update.info",
            ip_address="104.21.45.67",
            impersonated_brand="State Bank of India",
        )
        self.assertIn("MERGE (u)-[:HOSTED_ON]->(d)", built["query"])
        self.assertIn("MERGE (d)-[:RESOLVES_TO]->(ip)", built["query"])
        self.assertIn("MERGE (u)-[:IMPERSONATES]->(b)", built["query"])
        self.assertEqual(built["params"]["impersonated_brand"], "State Bank of India")

    def test_payment_request_to_payment_entity(self):
        built = JourneyGraphBuilder.query_link_payment_request(
            event_id="ev_03",
            payment_request_id="pay_req_01",
            vpa="scammer@oksbi",
            claimed_name="Electricity Officer",
        )
        self.assertIn("MERGE (pr:PaymentRequest {id: $payment_request_id})", built["query"])
        self.assertIn("MERGE (pe:PaymentEntity {vpa: $vpa})", built["query"])
        self.assertIn("MERGE (pr)-[:TO]->(pe)", built["query"])
        self.assertEqual(built["params"]["vpa"], "scammer@oksbi")


if __name__ == "__main__":
    unittest.main()
