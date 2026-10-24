"""Unit tests for Step 13: PhishGraph concepts (DNS, RDAP, TLS, Redirects)."""

import unittest
from services.investigation.url_analysis.analyzers import (
    DNSAnalyzer,
    RDAPAnalyzer,
    TLSAnalyzer,
    RedirectAnalyzer,
)
from packages.schemas import SignalDimension, SignalSeverity


class TestUrlAnalyzersStep13(unittest.TestCase):
    def test_rdap_analyzer_fresh_domain(self):
        signals = RDAPAnalyzer.evaluate_domain_age("inc_s13_01", "bill-update.info", age_days=3)
        self.assertEqual(len(signals), 1)
        sig = signals[0]
        self.assertEqual(sig.signal_type, "FRESHLY_REGISTERED_DOMAIN")
        self.assertEqual(sig.severity, SignalSeverity.HIGH)
        self.assertFalse(sig.is_counter_evidence)

    def test_rdap_analyzer_established_domain(self):
        signals = RDAPAnalyzer.evaluate_domain_age("inc_s13_02", "onlinesbi.sbi", age_days=1500)
        self.assertEqual(len(signals), 1)
        sig = signals[0]
        self.assertEqual(sig.signal_type, "ESTABLISHED_LONG_TERM_DOMAIN")
        self.assertTrue(sig.is_counter_evidence)

    def test_tls_analyzer_free_ssl_on_bank(self):
        signals = TLSAnalyzer.evaluate_certificate_metadata(
            incident_id="inc_s13_03",
            domain="sbi-secure-portal.online",
            issuer="Let's Encrypt Authority X3",
            validity_days=90,
            claimed_bank="State Bank of India",
        )
        self.assertEqual(len(signals), 1)
        sig = signals[0]
        self.assertEqual(sig.signal_type, "FREE_SSL_ON_PURPORTED_BANK")
        self.assertEqual(sig.severity, SignalSeverity.HIGH)

    def test_redirect_analyzer_multi_hop_cross_domain(self):
        chain = ["https://tinyurl.com/pay123", "https://redirect-portal.net/go", "http://billpay-update.info/login"]
        signals = RedirectAnalyzer.evaluate_redirect_chain(
            incident_id="inc_s13_04",
            initial_url="https://tinyurl.com/pay123",
            redirect_chain=chain,
        )
        self.assertGreaterEqual(len(signals), 2)
        types = [s.signal_type for s in signals]
        self.assertIn("MULTI_HOP_REDIRECT_CHAIN", types)
        self.assertIn("CROSS_DOMAIN_REDIRECT_OBSERVED", types)


if __name__ == "__main__":
    unittest.main()
