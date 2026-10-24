"""URL Feature Extractor for Machine Learning Models (Step 27).

Extracts dense lexical, structural, brand-targeting, and infrastructure features
from URLs for tabular ML classification.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

import yaml

CONFIG_PATH = Path("config/url_ml.yaml")
if not CONFIG_PATH.exists():
    CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "url_ml.yaml"


class URLFeatureExtractor:
    """Extracts standardized, normalized feature vectors from raw URLs."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config()
        self.suspicious_tlds: Set[str] = set(
            t.lower() for t in self.config.get("suspicious_tlds", [".xyz", ".top", ".tk", ".online", ".site", ".club"])
        )
        self.target_brands: Set[str] = set(
            b.lower() for b in self.config.get("target_brands", ["sbi", "hdfc", "icici", "axis", "tatapower", "paytm"])
        )
        self.official_brand_domains: Set[str] = set(
            d.lower() for d in self.config.get("official_brand_domains", [
                "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com", "tatapower.com", "google.com"
            ])
        )
        self.suspicious_keywords: Set[str] = set(
            k.lower() for k in self.config.get("suspicious_keywords", ["verify", "login", "kyc", "update", "otp", "claim"])
        )

    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                pass
        return {}

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Shannon entropy of a string."""
        if not text:
            return 0.0
        counts = Counter(text)
        length = len(text)
        return -sum((c / length) * math.log2(c / length) for c in counts.values())

    def extract(self, raw_url: str) -> Dict[str, float]:
        """Extract a complete numerical feature dictionary from a URL."""
        url_str = raw_url.strip()
        if "://" not in url_str:
            url_str = f"http://{url_str}"

        parsed = urlparse(url_str)
        hostname = (parsed.hostname or "").lower()
        path = parsed.path or "/"
        query = parsed.query or ""
        scheme = parsed.scheme.lower()

        # 1. Lengths and ratios
        url_len = len(raw_url)
        host_len = len(hostname)
        path_len = len(path)
        digits = sum(1 for c in raw_url if c.isdigit())
        digit_ratio = digits / max(1, url_len)

        # 2. Character counts
        dots = raw_url.count(".")
        hyphens = raw_url.count("-")
        encoded_chars = len(re.findall(r"%[0-9a-fA-F]{2}", raw_url))

        # 3. Structural parts
        host_parts = [p for p in hostname.split(".") if p]
        # Ignore 'www' prefix when counting subdomains
        non_www_subdomains = [p for p in host_parts[:-2] if p != "www"] if len(host_parts) > 2 else []
        subdomain_count = len(non_www_subdomains)
        path_segments = [p for p in path.split("/") if p]
        path_depth = len(path_segments)
        query_params = len(query.split("&")) if query else 0

        # 4. Host flags
        has_ip = 1.0 if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname) else 0.0
        has_punycode = 1.0 if ("xn--" in hostname) else 0.0
        non_https = 0.0 if scheme == "https" else 1.0
        https_discount = 1.0 if scheme == "https" else 0.0

        # 5. TLD Risk
        tld_match = False
        for tld in self.suspicious_tlds:
            if hostname.endswith(tld):
                tld_match = True
                break
        suspicious_tld_flag = 1.0 if tld_match else 0.0

        # 6. Entropy: only penalize entropy in excess of standard English domain distribution (> 3.8 bits)
        host_entropy = self.calculate_entropy(hostname)
        entropy_excess = max(0.0, host_entropy - 3.8)

        # 7. Keyword & Brand Targeting Analysis
        lowered_url = raw_url.lower()
        kw_count = sum(1 for kw in self.suspicious_keywords if kw in lowered_url)

        # Check if the hostname is a verified official brand domain
        is_official = any(hostname == off or hostname.endswith(f".{off}") for off in self.official_brand_domains)

        brand_in_subdomain_or_path = 0.0
        if not is_official:
            reg_domain = ".".join(host_parts[-2:]) if len(host_parts) >= 2 else hostname
            for brand in self.target_brands:
                if brand in hostname:
                    # If brand is in subdomains or registered domain has hyphen/suspicious TLD
                    if tld_match or ("-" in reg_domain) or any(brand in s for s in non_www_subdomains):
                        brand_in_subdomain_or_path = 1.0
                        break
                    # If registered domain is not ending in standard brand domain
                    if not (hostname.endswith(f"{brand}bank.com") or hostname.endswith(f"{brand}.com") or hostname.endswith(f"{brand}.co.in")):
                        brand_in_subdomain_or_path = 1.0
                        break
                elif brand in path.lower() and not is_official:
                    # E.g. "evil.xyz/sbi/verify"
                    brand_in_subdomain_or_path = 1.0
                    break

        return {
            "url_length": float(url_len),
            "url_length_log": float(math.log2(max(1, url_len)) / 3.0),
            "hostname_length": float(host_len),
            "path_length": float(path_len),
            "number_of_dots": float(dots),
            "number_of_hyphens": float(hyphens),
            "hyphen_count": float(hyphens),
            "number_of_digits": float(digits),
            "digit_ratio": float(digit_ratio),
            "subdomain_count": float(subdomain_count),
            "has_ip_host": has_ip,
            "has_punycode": has_punycode,
            "non_https": non_https,
            "https_discount": https_discount,
            "hostname_entropy": round(host_entropy, 3),
            "entropy_excess": round(entropy_excess, 3),
            "suspicious_tld": suspicious_tld_flag,
            "suspicious_keyword_count": float(kw_count),
            "brand_in_subdomain_or_path": brand_in_subdomain_or_path,
            "encoded_char_count": float(encoded_chars),
            "query_parameter_count": float(query_params),
            "path_depth": float(path_depth),
        }
