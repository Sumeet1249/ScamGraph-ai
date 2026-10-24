"""Unit tests for Step 11: Foundation FastAPI Incident Engine.

Verifies:
1. GET /health
2. POST /api/v1/incidents (create incident)
3. GET /api/v1/incidents/{id} (retrieve incident)
4. GET /api/v1/incidents/{unknown_id} (returns 404)
5. POST /api/v1/incidents/{id}/events (add event)
6. GET /api/v1/incidents/{id}/events (retrieve events)
7. GET /api/v1/incidents/{id}/timeline (chronological ordering)
8. POST /api/v1/incidents/{id}/evidence (add canonical evidence)
9. GET /api/v1/incidents/{id}/evidence (retrieve evidence)
10. Invalid event payload handling (returns 422)
11. Invalid evidence payload handling (returns 422)
"""

import unittest
from datetime import datetime, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from services.api.app.main import app


class TestIncidentEngineStep11(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "healthy")

    def test_unknown_incident_returns_404(self):
        res = self.client.get(f"/api/v1/incidents/nonexistent_{uuid4().hex[:8]}")
        self.assertEqual(res.status_code, 404)

    def test_incident_engine_full_lifecycle(self):
        # 1. Create Incident
        create_res = self.client.post(
            "/api/v1/incidents",
            json={
                "user_identifier_hash": "victim_hash_101",
                "channel": "SMS",
                "metadata": {"source_app": "TrueCaller"},
            },
        )
        self.assertEqual(create_res.status_code, 201)
        inc_data = create_res.json()
        incident_id = inc_data["id"]
        self.assertEqual(inc_data["status"], "ACTIVE")

        # 2. Retrieve Incident
        get_res = self.client.get(f"/api/v1/incidents/{incident_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["id"], incident_id)

        # 3. Add Event 1: Message
        now = datetime.now(timezone.utc)
        ev1_res = self.client.post(
            f"/api/v1/incidents/{incident_id}/events",
            json={
                "event_type": "MESSAGE_RECEIVED",
                "sequence_number": 1,
                "timestamp": now.isoformat(),
                "payload": {"text": "Your electricity power will be cutoff tonight at 9:30 PM."},
            },
        )
        self.assertEqual(ev1_res.status_code, 201)

        # 4. Add Event 2: URL Clicked
        ev2_res = self.client.post(
            f"/api/v1/incidents/{incident_id}/events",
            json={
                "event_type": "LINK_CLICKED",
                "sequence_number": 2,
                "timestamp": now.isoformat(),
                "payload": {"raw_url": "http://power-bill-update.online"},
            },
        )
        self.assertEqual(ev2_res.status_code, 201)

        # 5. Retrieve all raw events
        events_res = self.client.get(f"/api/v1/incidents/{incident_id}/events")
        self.assertEqual(events_res.status_code, 200)
        events_list = events_res.json()
        self.assertEqual(len(events_list), 2)

        # 6. Retrieve ordered timeline
        timeline_res = self.client.get(f"/api/v1/incidents/{incident_id}/timeline")
        self.assertEqual(timeline_res.status_code, 200)
        timeline = timeline_res.json()
        self.assertEqual(timeline["total_events"], 2)
        self.assertEqual(timeline["events"][0]["event_type"], "MESSAGE_RECEIVED")
        self.assertEqual(timeline["events"][1]["event_type"], "LINK_CLICKED")

        # 7. Add Canonical Evidence
        evid_res = self.client.post(
            f"/api/v1/incidents/{incident_id}/evidence",
            json={
                "source": "URL_ANALYZER",
                "signal": "BRAND_TYPOSQUATTING_DETECTED",
                "observation": "Domain power-bill-update.online newly registered in untrusted ASN",
                "confidence": 0.94,
                "timestamp": now.isoformat(),
                "entity_ids": [str(uuid4())],
                "event_ids": [str(uuid4())],
            },
        )
        self.assertEqual(evid_res.status_code, 201)
        self.assertEqual(evid_res.json()["signal"], "BRAND_TYPOSQUATTING_DETECTED")

        # 8. Retrieve Evidence list
        get_evid = self.client.get(f"/api/v1/incidents/{incident_id}/evidence")
        self.assertEqual(get_evid.status_code, 200)
        self.assertEqual(len(get_evid.json()), 1)

    def test_invalid_event_payload_returns_422(self):
        inc_id = f"inc_{uuid4().hex[:8]}"
        res = self.client.post(
            f"/api/v1/incidents/{inc_id}/events",
            json={
                "event_type": "NON_EXISTENT_TYPE",  # Invalid enum value!
            },
        )
        self.assertEqual(res.status_code, 422)

    def test_invalid_evidence_confidence_returns_422(self):
        # Create incident
        create_res = self.client.post(
            "/api/v1/incidents",
            json={"user_identifier_hash": "victim_usr", "channel": "SMS"},
        )
        incident_id = create_res.json()["id"]

        # Confidence > 1.0 must fail with 422
        res = self.client.post(
            f"/api/v1/incidents/{incident_id}/evidence",
            json={
                "source": "TINYFISH",
                "signal": "TEST_SIGNAL",
                "observation": "Test observation",
                "confidence": 1.5,  # Exceeds 1.0!
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        self.assertEqual(res.status_code, 422)


if __name__ == "__main__":
    unittest.main()
