"""End-to-End Scenario Test: Electricity Bill Disconnection Scam.

Validates the complete journey progression, multi-signal evidence fusion,
INSUFFICIENT_EVIDENCE thresholding, and adaptive intervention friction.
"""

import unittest
from fastapi.testclient import TestClient

from services.api.app.main import app
from packages.schemas import RiskLevel, EvidenceConfidence, InterventionAction


class TestElectricityScamScenario(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.incident_id = "inc_scenario_electricity_001"

    def test_end_to_end_journey_and_calibration(self):
        # ─────────────────────────────────────────────────────────────
        # Stage 1: Initial Contact (SMS with Urgency & Impersonation)
        # ─────────────────────────────────────────────────────────────
        sms_event = {
            "incident_id": self.incident_id,
            "sequence_number": 1,
            "event_type": "MESSAGE_RECEIVED",
            "payload": {
                "sender_id": "+919876543210",
                "recipient_id_hash": "victim_hash_001",
                "text": "Dear consumer, electricity power will be disconnected immediately at 9:30 PM by Electricity Officer. Contact officer urgently.",
                "channel": "SMS",
            },
        }
        res1 = self.client.post("/api/v1/incidents/ingest", json=sms_event)
        self.assertEqual(res1.status_code, 201)
        self.assertGreaterEqual(res1.json()["active_signals_count"], 1)

        # After only Step 1, system MUST return INSUFFICIENT_EVIDENCE (Rule 13 & 14)
        assess1 = self.client.get(f"/api/v1/incidents/{self.incident_id}/assessment").json()
        self.assertEqual(assess1["risk_level"], RiskLevel.INSUFFICIENT_EVIDENCE.value)
        self.assertEqual(assess1["evidence_confidence"], EvidenceConfidence.LOW.value)
        self.assertTrue(assess1["is_insufficient_evidence"])
        self.assertEqual(assess1["intervention"]["action"], InterventionAction.NONE.value)

        # ─────────────────────────────────────────────────────────────
        # Stage 2: Suspicious Link Clicked
        # ─────────────────────────────────────────────────────────────
        url_event = {
            "incident_id": self.incident_id,
            "sequence_number": 2,
            "event_type": "LINK_CLICKED",
            "payload": {
                "raw_url": "http://mahavitaran-billpay.info/update",
            },
        }
        res2 = self.client.post("/api/v1/incidents/ingest", json=url_event)
        self.assertEqual(res2.status_code, 201)

        # After Step 2, signals span 2 dimensions (SEMANTIC + URL)
        assess2 = self.client.get(f"/api/v1/incidents/{self.incident_id}/assessment").json()
        self.assertFalse(assess2["is_insufficient_evidence"])
        self.assertIn(assess2["risk_level"], [RiskLevel.MEDIUM.value, RiskLevel.HIGH.value])
        self.assertEqual(assess2["evidence_confidence"], EvidenceConfidence.MEDIUM.value)
        self.assertEqual(len(assess2["corroborated_dimensions"]), 2)

        # ─────────────────────────────────────────────────────────────
        # Stage 3: Payment Collect Request Received (Personal VPA)
        # ─────────────────────────────────────────────────────────────
        payment_event = {
            "incident_id": self.incident_id,
            "sequence_number": 3,
            "event_type": "COLLECT_REQUEST_RECEIVED",
            "payload": {
                "vpa": "officer.collect@oksbi",
                "claimed_payee_name": "Maharashtra Electricity Board",
                "amount": 10.0,
                "transaction_type": "COLLECT",
                "reference_note": "Bill verification charge",
            },
        }
        res3 = self.client.post("/api/v1/incidents/ingest", json=payment_event)
        self.assertEqual(res3.status_code, 201)

        # After Step 3, signals span 3 independent dimensions (SEMANTIC + URL + PAYMENT)
        assess3 = self.client.get(f"/api/v1/incidents/{self.incident_id}/assessment").json()
        self.assertEqual(assess3["risk_level"], RiskLevel.HIGH.value)
        self.assertEqual(assess3["evidence_confidence"], EvidenceConfidence.HIGH.value)
        self.assertEqual(len(assess3["corroborated_dimensions"]), 3)

        # Pre-payment adaptive intervention triggered with 10s friction
        self.assertEqual(assess3["intervention"]["action"], InterventionAction.PRE_PAYMENT_INTERVENTION.value)
        self.assertEqual(assess3["intervention"]["friction_delay_seconds"], 10)
        self.assertFalse(assess3["intervention"]["dismissible"])

        # ─────────────────────────────────────────────────────────────
        # Validate Scam Journey Reconstructed
        # ─────────────────────────────────────────────────────────────
        journey = self.client.get(f"/api/v1/incidents/{self.incident_id}/journey").json()
        self.assertEqual(len(journey["steps"]), 3)
        self.assertEqual(journey["current_stage"], "PAYMENT_REQUEST")
        self.assertEqual(journey["prediction"]["predicted_next_stage"], "PAYMENT_INTENT")

        # ─────────────────────────────────────────────────────────────
        # Validate Cytoscape Graph Canvas Export
        # ─────────────────────────────────────────────────────────────
        graph = self.client.get(f"/api/v1/incidents/{self.incident_id}/graph").json()
        self.assertEqual(len(graph["nodes"]), 4)  # 1 root incident + 3 steps
        self.assertEqual(len(graph["edges"]), 5)  # 3 CONTAINS_STEP + 2 FOLLOWED_BY


if __name__ == "__main__":
    unittest.main()
