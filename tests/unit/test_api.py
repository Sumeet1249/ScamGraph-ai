"""Unit tests for FastAPI endpoints."""

import unittest
from fastapi.testclient import TestClient

from services.api.app.main import app
from packages.schemas import ChannelType, EventType


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")

    def test_ingest_and_insufficient_evidence(self):
        incident_id = "test_inc_401"
        event_payload = {
            "incident_id": incident_id,
            "sequence_number": 1,
            "event_type": "MESSAGE_RECEIVED",
            "payload": {
                "sender_id": "+919876543210",
                "recipient_id_hash": "user_hash_401",
                "text": "Your account KYC is expired. Update immediately.",
                "channel": "SMS",
            },
        }
        ingest_resp = self.client.post("/api/v1/incidents/ingest", json=event_payload)
        self.assertEqual(ingest_resp.status_code, 201)
        self.assertEqual(ingest_resp.json()["status"], "received")

        # Single event must trigger INSUFFICIENT_EVIDENCE (Rule 13)
        assess_resp = self.client.get(f"/api/v1/incidents/{incident_id}/assessment")
        self.assertEqual(assess_resp.status_code, 200)
        assess_data = assess_resp.json()
        self.assertEqual(assess_data["risk_level"], "INSUFFICIENT_EVIDENCE")
        self.assertTrue(assess_data["is_insufficient_evidence"])

    def test_multi_step_journey_and_graph(self):
        incident_id = "test_inc_402"

        # Step 1: SMS
        self.client.post(
            "/api/v1/incidents/ingest",
            json={
                "incident_id": incident_id,
                "sequence_number": 1,
                "event_type": "MESSAGE_RECEIVED",
                "payload": {
                    "sender_id": "+919999999999",
                    "recipient_id_hash": "user_hash_402",
                    "text": "Electricity bill unpaid.",
                    "channel": "SMS",
                },
            },
        )

        # Step 2: URL click
        self.client.post(
            "/api/v1/incidents/ingest",
            json={
                "incident_id": incident_id,
                "sequence_number": 2,
                "event_type": "LINK_CLICKED",
                "payload": {
                    "raw_url": "http://power-bill-update.info",
                },
            },
        )

        # Step 3: Collect Request
        self.client.post(
            "/api/v1/incidents/ingest",
            json={
                "incident_id": incident_id,
                "sequence_number": 3,
                "event_type": "COLLECT_REQUEST_RECEIVED",
                "payload": {
                    "vpa": "fraudster@oksbi",
                    "amount": 10.0,
                    "transaction_type": "COLLECT",
                },
            },
        )

        # Verify Journey
        journey_resp = self.client.get(f"/api/v1/incidents/{incident_id}/journey")
        self.assertEqual(journey_resp.status_code, 200)
        journey_data = journey_resp.json()
        self.assertEqual(len(journey_data["steps"]), 3)
        self.assertIn(journey_data["current_stage"], ["PAYMENT_REQUEST", "INITIAL_PAYMENT"])

        # Verify Cytoscape Graph
        graph_resp = self.client.get(f"/api/v1/incidents/{incident_id}/graph")
        self.assertEqual(graph_resp.status_code, 200)
        graph_data = graph_resp.json()
        # 1 incident root + 3 step nodes = 4 nodes
        self.assertEqual(len(graph_data["nodes"]), 4)
        # 3 CONTAINS_STEP edges + 2 FOLLOWED_BY edges = 5 edges
        self.assertEqual(len(graph_data["edges"]), 5)


if __name__ == "__main__":
    unittest.main()
