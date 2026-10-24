"""Unit tests for LexicalAnalyzer (Step 16)."""

import unittest
from services.investigation.url_analysis.lexical import LexicalAnalyzer
from services.investigation.url_analysis.normalizer import URLNormalizer


class TestLexicalAnalyzer(unittest.TestCase):
    def test_lexical_feature_extraction(self):
        norm = URLNormalizer.normalize("https://sbi-verify.security-update.example.test/banking/login?token=123&action=verify")
        features = LexicalAnalyzer.extract_features(norm)

        self.assertTrue(features.https_scheme)
        self.assertFalse(features.has_ip_hostname)
        self.assertFalse(features.has_punycode)
        self.assertGreater(features.suspicious_token_count, 2)  # verify, security, update, banking, login
        self.assertEqual(features.query_parameter_count, 2)
        self.assertGreater(features.hostname_entropy, 2.0)
        self.assertEqual(features.subdomain_count, 2)

    def test_ip_host_lexical_features(self):
        norm = URLNormalizer.normalize("http://198.51.100.4:8080/login.php")
        features = LexicalAnalyzer.extract_features(norm)
        self.assertTrue(features.has_ip_hostname)
        self.assertFalse(features.https_scheme)
        self.assertGreaterEqual(features.suspicious_token_count, 1)

    def test_evidence_generation(self):
        norm = URLNormalizer.normalize("http://198.51.100.4/verify-kyc")
        features = LexicalAnalyzer.extract_features(norm)
        evidence = LexicalAnalyzer.generate_evidence("inc-123", norm, features)

        self.assertGreaterEqual(len(evidence), 2)  # Base lexical + Direct IP host
        signals = [e.signal for e in evidence]
        self.assertIn("URL_LEXICAL_OBSERVATION", signals)
        self.assertIn("DIRECT_IP_HOST_OBSERVED", signals)


if __name__ == "__main__":
    unittest.main()
