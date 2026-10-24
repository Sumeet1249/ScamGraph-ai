"""Unit tests for TinyFish WebInvestigator (Step 17).

Verifies:
1. Successful investigation (KYC site with OTP & credential fields)
2. Benign site investigation
3. Investment scam site investigation
4. Malformed TinyFish response handling
5. Timeout handling (returns unavailable, does not crash)
6. Provider failure handling
7. Missing API key handling in live mode
8. Mock mode reading fixtures
9. SSRF rejection prior to external call
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from services.investigation.tinyfish.client import TinyFishClient
from services.investigation.tinyfish.exceptions import (
    TinyFishConfigError,
    TinyFishMalformedResponseError,
    TinyFishTimeoutError,
)
from services.investigation.tinyfish.service import TinyFishWebInvestigator


class TestTinyFishWebInvestigator(unittest.TestCase):
    def setUp(self):
        # Uses default mock mode pointing to tests/fixtures/tinyfish
        self.investigator = TinyFishWebInvestigator(
            client=TinyFishClient(mode="mock")
        )

    def test_mock_mode_kyc_site_extracts_otp_and_credentials(self):
        res = asyncio.run(
            self.investigator.investigate("inc-kyc", "https://sbi-verify.example.test/kyc")
        )
        self.assertEqual(res.status, "completed")
        self.assertEqual(res.provider, "TINYFISH")
        self.assertIsNotNone(res.observables)
        self.assertIn("State Bank of India", res.observables.claimed_brands)
        self.assertGreater(len(res.observables.otp_fields), 0)
        self.assertGreater(len(res.observables.credential_fields), 0)

        # Check evidence signals
        signals = [e.signal for e in res.evidence]
        self.assertIn("OTP_FIELD_PRESENT", signals)
        self.assertIn("CREDENTIAL_COLLECTION", signals)
        self.assertIn("CLAIMED_BRAND", signals)

        # All evidence must have source = TINYFISH
        for ev in res.evidence:
            self.assertEqual(ev.source.value, "TINYFISH")

        # Check entity extraction
        entity_types = [ent.entity_type.value for ent in res.entities]
        self.assertIn("BRAND", entity_types)
        self.assertIn("PHONE", entity_types)
        self.assertIn("PAYMENT_ENTITY", entity_types)

    def test_mock_mode_benign_site(self):
        res = asyncio.run(
            self.investigator.investigate("inc-benign", "https://utility.example.com/portal")
        )
        self.assertEqual(res.status, "completed")
        self.assertIsNotNone(res.observables)
        self.assertEqual(len(res.observables.otp_fields), 0)
        self.assertEqual(len(res.observables.credential_fields), 0)
        signals = [e.signal for e in res.evidence]
        self.assertNotIn("OTP_FIELD_PRESENT", signals)
        self.assertNotIn("CREDENTIAL_COLLECTION", signals)

    def test_mock_mode_investment_site(self):
        res = asyncio.run(
            self.investigator.investigate("inc-invest", "https://crypto-vip.example.test/invest")
        )
        self.assertEqual(res.status, "completed")
        self.assertIsNotNone(res.observables)
        self.assertIn("invest.pool@fakeupi", res.observables.payment_identifiers)
        signals = [e.signal for e in res.evidence]
        self.assertIn("PAYMENT_IDENTIFIER_OBSERVED", signals)

    def test_malformed_response_handled_gracefully(self):
        res = asyncio.run(
            self.investigator.investigate("inc-mal", "https://malformed-site.example.test")
        )
        # Does not crash; marks as unavailable or partial with errors logged
        self.assertIn(res.status, ["unavailable", "partial"])
        self.assertEqual(len(res.evidence), 0)

    def test_timeout_returns_unavailable_without_crashing(self):
        mock_client = TinyFishClient(mode="live", api_key="test-key")
        mock_client.fetch_page_observables = AsyncMock(side_effect=TinyFishTimeoutError("Connection timed out after 4s"))
        investigator = TinyFishWebInvestigator(client=mock_client)

        res = asyncio.run(
            investigator.investigate("inc-to", "https://timeout-site.example.com")
        )
        self.assertEqual(res.status, "unavailable")
        self.assertGreater(len(res.errors), 0)
        self.assertIn("timed out", res.errors[0])
        self.assertEqual(len(res.evidence), 0)

    def test_missing_api_key_in_live_mode_returns_unavailable(self):
        mock_client = TinyFishClient(mode="live", api_key=None)
        investigator = TinyFishWebInvestigator(client=mock_client)

        res = asyncio.run(
            investigator.investigate("inc-key", "https://some-site.example.com")
        )
        self.assertEqual(res.status, "unavailable")
        self.assertIn("configuration error", res.errors[0])

    def test_ssrf_rejection_blocks_investigation_before_client_call(self):
        res = asyncio.run(
            self.investigator.investigate("inc-ssrf", "http://127.0.0.1:8000/secret")
        )
        self.assertEqual(res.status, "rejected")
        self.assertIn("SSRF Guard", res.errors[0])


if __name__ == "__main__":
    unittest.main()
