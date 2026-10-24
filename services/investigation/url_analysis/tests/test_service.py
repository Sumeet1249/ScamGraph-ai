"""Unit tests for URLInvestigationService (Step 16)."""

import asyncio
import unittest
from services.investigation.url_analysis.service import URLInvestigationService


class TestURLInvestigationService(unittest.TestCase):
    def setUp(self):
        self.service = URLInvestigationService()

    def test_safe_url_investigation_completes(self):
        res = asyncio.run(
            self.service.investigate_url("inc-123", "https://example.com/test-path?param=value")
        )
        self.assertIn(res.status, ["completed", "partial"])
        self.assertTrue(res.safety.is_safe)
        self.assertIsNotNone(res.normalized_url)
        self.assertEqual(res.normalized_url.hostname, "example.com")
        self.assertIsNotNone(res.features)
        self.assertGreater(len(res.evidence), 0)
        self.assertGreater(len(res.entities), 0)

    def test_ssrf_unsafe_url_is_rejected_before_network_calls(self):
        res = asyncio.run(
            self.service.investigate_url("inc-456", "http://127.0.0.1:8000/admin")
        )
        self.assertEqual(res.status, "rejected")
        self.assertFalse(res.safety.is_safe)
        self.assertIn("127.0.0.0/8", str(res.safety.blocked_range))

    def test_private_ip_is_rejected(self):
        res = asyncio.run(
            self.service.investigate_url("inc-789", "http://192.168.1.1/setup")
        )
        self.assertEqual(res.status, "rejected")
        self.assertFalse(res.safety.is_safe)

    def test_synthetic_test_domain_handled_gracefully(self):
        res = asyncio.run(
            self.service.investigate_url("inc-test", "https://sbi-verify.example.test/kyc")
        )
        self.assertIn(res.status, ["completed", "partial"])
        self.assertTrue(res.safety.is_safe)
        self.assertGreater(len(res.evidence), 0)


if __name__ == "__main__":
    unittest.main()
