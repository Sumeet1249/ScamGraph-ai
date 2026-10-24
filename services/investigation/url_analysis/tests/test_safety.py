"""Unit tests for URLSafetyValidator and SSRF Protection (Step 16)."""

import socket
import unittest
from services.investigation.url_analysis.safety import URLSafetyValidator


class TestURLSafetyValidator(unittest.TestCase):
    def test_public_urls_allowed(self):
        # Public IP simulation
        def mock_resolver_public(host, port):
            return [(2, 1, 6, "", ("93.184.216.34", 80))]

        res = URLSafetyValidator.validate_url("https://example.com", dns_resolver=mock_resolver_public)
        self.assertTrue(res.is_safe)
        self.assertEqual(res.resolved_ips, ["93.184.216.34"])

    def test_localhost_and_internal_hostnames_rejected(self):
        disallowed = [
            "http://localhost:8000/admin",
            "https://internal.service/api",
            "http://metadata.google.internal/computeMetadata/v1",
            "http://sub.localhost/test",
        ]
        for url in disallowed:
            res = URLSafetyValidator.validate_url(url)
            self.assertFalse(res.is_safe, f"Failed to reject: {url}")

    def test_loopback_127_ip_rejected(self):
        res = URLSafetyValidator.validate_url("http://127.0.0.1:8000/secret")
        self.assertFalse(res.is_safe)
        self.assertTrue(res.is_loopback)

        res2 = URLSafetyValidator.validate_url("http://127.12.34.56/data")
        self.assertFalse(res2.is_safe)

    def test_ipv6_loopback_rejected(self):
        res = URLSafetyValidator.validate_url("http://[::1]:8080/")
        self.assertFalse(res.is_safe)
        self.assertTrue(res.is_loopback)

    def test_private_ipv4_ranges_rejected(self):
        private_ips = [
            "http://10.0.0.1/",
            "http://10.254.12.1/api",
            "http://172.16.0.5/login",
            "http://172.31.255.255/",
            "http://192.168.1.1/router",
            "http://192.168.0.254/",
        ]
        for url in private_ips:
            res = URLSafetyValidator.validate_url(url)
            self.assertFalse(res.is_safe, f"Failed to reject private IP: {url}")
            self.assertTrue(res.is_private)

    def test_cloud_metadata_rejected(self):
        # AWS / GCP metadata IP 169.254.169.254
        res = URLSafetyValidator.validate_url("http://169.254.169.254/latest/meta-data/")
        self.assertFalse(res.is_safe)
        self.assertTrue(res.is_metadata_endpoint)

    def test_dns_rebinding_resolution_to_private_ip_rejected(self):
        # Simulates a domain that resolves to a private IP (e.g. 192.168.1.50)
        def mock_resolver_rebinding(host, port):
            return [(2, 1, 6, "", ("192.168.1.50", 80))]

        res = URLSafetyValidator.validate_url("http://evil-rebind.com/probe", dns_resolver=mock_resolver_rebinding)
        self.assertFalse(res.is_safe)
        self.assertTrue(res.is_private)
        self.assertIn("192.168.1.50", res.resolved_ips)

    def test_unsupported_schemes_rejected(self):
        res = URLSafetyValidator.validate_url("ftp://12.34.56.78/file")
        self.assertFalse(res.is_safe)


if __name__ == "__main__":
    unittest.main()
