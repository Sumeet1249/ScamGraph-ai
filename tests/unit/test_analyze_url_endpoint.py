"""Unit tests for POST /api/v1/analyze/url endpoint (Step 16)."""

import unittest
from fastapi.testclient import TestClient
from services.api.app.main import app


class TestAnalyzeURLEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Create an incident to attach URL investigation results
        resp = self.client.post(
            "/api/v1/incidents",
            json={
                "user_identifier_hash": "victim_url_test_101",
                "channel": "SMS",
                "metadata": {"title": "URL Analysis Test Incident"},
            },
        )
        self.assertEqual(resp.status_code, 201)
        self.incident_id = resp.json()["id"]

    def test_analyze_valid_public_url(self):
        resp = self.client.post(
            "/api/v1/analyze/url",
            json={"incident_id": self.incident_id, "url": "https://example.com/test"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("investigation_id", data)
        self.assertIn(data["status"], ["completed", "partial"])
        self.assertIn("https://example.com/test", data["normalized_url"])
        self.assertIsNotNone(data["features"])
        self.assertGreater(len(data["evidence"]), 0)

        # Check evidence attached to incident in repository
        ev_resp = self.client.get(f"/api/v1/incidents/{self.incident_id}/evidence")
        self.assertEqual(ev_resp.status_code, 200)
        self.assertGreater(len(ev_resp.json()), 0)

    def test_ssrf_loopback_rejection(self):
        resp = self.client.post(
            "/api/v1/analyze/url",
            json={"incident_id": self.incident_id, "url": "http://127.0.0.1:8000/admin"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "rejected")
        self.assertGreater(len(data["errors"]), 0)

    def test_ssrf_private_ip_rejection(self):
        resp = self.client.post(
            "/api/v1/analyze/url",
            json={"incident_id": self.incident_id, "url": "http://192.168.1.1/setup"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "rejected")

    def test_unknown_incident_returns_404(self):
        resp = self.client.post(
            "/api/v1/analyze/url",
            json={"incident_id": "00000000-0000-0000-0000-000000000000", "url": "https://example.com"},
        )
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
