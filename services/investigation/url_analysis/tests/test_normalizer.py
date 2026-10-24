"""Unit tests for URLNormalizer (Step 16)."""

import unittest
from services.investigation.url_analysis.normalizer import URLNormalizationError, URLNormalizer


class TestURLNormalizer(unittest.TestCase):
    def test_valid_https_url_normalization(self):
        raw = "   HTTPS://Example.COM:443/Path/To/Resource?b=2&a=1#section1   "
        norm = URLNormalizer.normalize(raw)
        self.assertEqual(norm.scheme, "https")
        self.assertEqual(norm.hostname, "example.com")
        self.assertIsNone(norm.port)  # 443 normalized away for https
        self.assertEqual(norm.path, "/Path/To/Resource")
        self.assertEqual(norm.query, "b=2&a=1")
        self.assertNotIn("section1", norm.normalized_url)  # Fragment removed
        self.assertEqual(norm.registered_domain, "example.com")
        self.assertFalse(norm.is_ip_host)

    def test_explicit_non_standard_port(self):
        norm = URLNormalizer.normalize("http://example.com:8080/api")
        self.assertEqual(norm.port, 8080)
        self.assertEqual(norm.normalized_url, "http://example.com:8080/api")

    def test_punycode_and_idn_handling(self):
        # Unicode domain Bücher.example -> xn--bcher-kva.example
        norm = URLNormalizer.normalize("https://münchen.de/portal")
        self.assertTrue(norm.hostname.startswith("xn--") or "xn--" in norm.hostname)

    def test_ip_address_host_recognition(self):
        norm = URLNormalizer.normalize("http://93.184.216.34:80/index.html")
        self.assertTrue(norm.is_ip_host)
        self.assertEqual(norm.hostname, "93.184.216.34")
        self.assertIsNone(norm.port)

    def test_two_part_tld_registered_domain(self):
        norm = URLNormalizer.normalize("https://sub.portal.sbi.co.in/banking")
        self.assertEqual(norm.registered_domain, "sbi.co.in")

    def test_unsupported_schemes_rejected(self):
        unsupported = [
            "ftp://files.example.com",
            "javascript:alert(1)",
            "data:text/html,<html>",
            "file:///etc/passwd",
        ]
        for u in unsupported:
            with self.assertRaises(URLNormalizationError):
                URLNormalizer.normalize(u)

    def test_malformed_urls_rejected(self):
        malformed = ["", "   ", "not-a-url", "://missing-scheme.com"]
        for m in malformed:
            with self.assertRaises(URLNormalizationError):
                URLNormalizer.normalize(m)


if __name__ == "__main__":
    unittest.main()
