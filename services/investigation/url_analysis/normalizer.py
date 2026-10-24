"""Deterministic URL Normalizer (Step 16).

Transforms raw user/incident URL strings into canonical NormalizedURL representations.
Rejects malformed inputs and unsupported schemes without silent conversions.
"""

import ipaddress
import re
from typing import Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from services.investigation.url_analysis.models import NormalizedURL

# Two-part public suffixes common in targeted fraud
COMMON_TWO_PART_TLDS = {
    "co.in", "gov.in", "ac.in", "net.in", "org.in", "res.in",
    "co.uk", "org.uk", "gov.uk", "ac.uk",
    "com.au", "net.au", "org.au",
    "com.br", "co.jp", "co.kr", "co.za",
}


class URLNormalizationError(ValueError):
    """Raised when URL is malformed, uses an unsupported scheme, or cannot be parsed."""
    pass


class URLNormalizer:
    """Normalizes raw URLs for consistent, secure investigation."""

    SUPPORTED_SCHEMES = {"http", "https"}

    @classmethod
    def normalize(cls, raw_url: str) -> NormalizedURL:
        if not raw_url or not isinstance(raw_url, str):
            raise URLNormalizationError("URL must be a non-empty string.")

        clean_url = raw_url.strip()
        if not clean_url:
            raise URLNormalizationError("URL cannot be empty or pure whitespace.")

        # If scheme is omitted entirely, reject or check scheme format
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", clean_url):
            # Do not silently accept arbitrary schemes without protocol prefix
            raise URLNormalizationError(f"URL '{raw_url}' missing explicit http/https scheme.")

        try:
            parsed = urlparse(clean_url)
        except Exception as e:
            raise URLNormalizationError(f"Failed to parse URL '{raw_url}': {e}")

        scheme = parsed.scheme.lower()
        if scheme not in cls.SUPPORTED_SCHEMES:
            raise URLNormalizationError(f"Unsupported scheme '{scheme}'. Only HTTP and HTTPS are permitted.")

        raw_hostname = parsed.hostname
        if not raw_hostname:
            raise URLNormalizationError(f"URL '{raw_url}' lacks a valid hostname.")

        # Normalize IDN / Punycode safely
        try:
            # Handle unicode domain names via IDNA
            hostname_ascii = raw_hostname.encode("idna").decode("ascii").lower()
        except Exception:
            hostname_ascii = raw_hostname.lower()

        # Check for IP host
        is_ip = False
        try:
            ipaddress.ip_address(hostname_ascii)
            is_ip = True
        except ValueError:
            is_ip = False

        # Extract registered domain
        registered_domain = cls._extract_registered_domain(hostname_ascii, is_ip)

        # Handle explicit port
        port = parsed.port
        if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
            port = None  # Normalize away default ports

        # Normalize path: ensure at least '/' and remove double slashes
        path = parsed.path or "/"
        path = re.sub(r"/+", "/", path)

        # Normalize query: preserve meaningful parameters sorted deterministically
        query: Optional[str] = None
        if parsed.query:
            query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
            if query_pairs:
                query = urlencode(query_pairs)

        # Exclude fragment entirely from investigation target
        netloc = hostname_ascii
        if port:
            netloc = f"{hostname_ascii}:{port}"

        reconstructed_url = urlunparse((scheme, netloc, path, "", query or "", ""))

        return NormalizedURL(
            original_url=raw_url,
            normalized_url=reconstructed_url,
            scheme=scheme,
            hostname=hostname_ascii,
            port=port,
            path=path,
            query=query,
            registered_domain=registered_domain,
            is_ip_host=is_ip,
        )

    @staticmethod
    def _extract_registered_domain(hostname: str, is_ip: bool) -> str:
        """Extracts the base registered domain (e.g. sbi-verify.example.test -> example.test)."""
        if is_ip or "." not in hostname:
            return hostname

        parts = hostname.split(".")
        if len(parts) <= 2:
            return hostname

        # Check for two-part TLDs (e.g. example.co.in)
        two_part = f"{parts[-2]}.{parts[-1]}"
        if two_part in COMMON_TWO_PART_TLDS and len(parts) >= 3:
            return f"{parts[-3]}.{two_part}"

        return f"{parts[-2]}.{parts[-1]}"
