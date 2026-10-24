"""Unit tests for Investigation Service (SSRF Safety, Lexical Analysis)."""

import unittest
from services.investigation.url_analysis.safety import URLSafetyValidator, URLAnalyzer
from packages.schemas import SignalDimension, SignalSeverity


class TestInvestigationSafety(unittest.TestCase):
    def test_ssrf_blocks_private_and_loopback_ips(self):
        self.assertFalse(URLSafetyValidator.is_safe_public_url("http://127.0.0.1/admin"))
        self.assertFalse(URLSafetyValidator.is_safe_public_url("http://localhost:8080/"))
        self.assertFalse(URLSafetyValidator.is_safe_public_url("http://10.0.0.5/api"))
        self.assertFalse(URLSafetyValidator.is_safe_public_url("http://192.168.1.1/router"))
        self.assertFalse(URLSafetyValidator.is_safe_public_url("http://169.254.169.254/latest/meta-data/"))
        self.assertFalse(URLSafetyValidator.is_safe_public_url("file:///etc/passwd"))
        self.assertFalse(URLSafetyValidator.is_safe_public_url("ftp://server/file"))

    def test_lexical_analysis_typosquatting(self):
        res = URLAnalyzer.analyze_lexical_risk("inc_101", "http://sbi-kyc-update.info/login")
        self.assertFalse(res["is_trusted"])
        self.assertEqual(len(res["signals"]), 2)
        types = [s.signal_type for s in res["signals"]]
        self.assertIn("SUSPICIOUS_TLD_USED", types)
        self.assertIn("BRAND_TYPOSQUATTING_DETECTED", types)

    def test_lexical_analysis_trusted_domain(self):
        res = URLAnalyzer.analyze_lexical_risk("inc_102", "https://onlinesbi.sbi/portal")
        self.assertTrue(res["is_trusted"])
        self.assertEqual(len(res["signals"]), 1)
        self.assertTrue(res["signals"][0].is_counter_evidence)


if __name__ == "__main__":
    unittest.main()
