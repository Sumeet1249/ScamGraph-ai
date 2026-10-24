"""Entity normalization engine for Neo4j Evidence Graph.

Ensures that variant representations of domains, URLs, phone numbers,
payment entities, IPs, and ASNs resolve to identical canonical identifiers
while preserving human-readable display values for UI presentation.
"""

from __future__ import annotations

import ipaddress
import re
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


class EntityNormalizer:
    """Provides non-destructive entity normalization for graph nodes."""

    @staticmethod
    def normalize_domain(raw_domain: str) -> Tuple[str, str]:
        """Normalize a domain name.

        Strips protocols, paths, ports, 'www.' prefix, and trailing dots.
        Returns: (normalized_value, display_value)
        """
        if not raw_domain:
            return "", ""

        display = str(raw_domain).strip()
        cleaned = display.lower()

        # If full URL passed, parse host
        if "://" in cleaned or cleaned.startswith("//"):
            try:
                parsed = urlparse(cleaned if "://" in cleaned else f"http:{cleaned}")
                cleaned = parsed.hostname or cleaned
            except Exception:
                pass

        # Remove port if present
        if ":" in cleaned:
            cleaned = cleaned.split(":")[0]

        # Remove trailing slash or period
        cleaned = cleaned.rstrip("/.")

        # Strip leading www.
        if cleaned.startswith("www."):
            cleaned = cleaned[4:]

        return cleaned, display

    @staticmethod
    def normalize_url(raw_url: str) -> Tuple[str, str]:
        """Normalize a URL.

        - Lowercase scheme and hostname
        - Preserve path case (standardize trailing slash)
        - Strip fragment (#...)
        - Deterministically sort query parameters
        - Strip default ports (:80, :443)
        Returns: (normalized_value, display_value)
        """
        if not raw_url:
            return "", ""

        display = str(raw_url).strip()
        url_to_parse = display
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url_to_parse):
            url_to_parse = "https://" + url_to_parse

        try:
            parsed = urlparse(url_to_parse)
            scheme = parsed.scheme.lower() if parsed.scheme else "https"
            netloc = parsed.netloc.lower()

            # Strip default ports
            if scheme == "http" and netloc.endswith(":80"):
                netloc = netloc[:-3]
            elif scheme == "https" and netloc.endswith(":443"):
                netloc = netloc[:-4]

            # Strip www from netloc for canonical match
            if netloc.startswith("www."):
                netloc = netloc[4:]

            # Normalize path
            path = parsed.path
            if not path or path == "":
                path = "/"
            else:
                # Collapse redundant slashes and strip non-root trailing slash
                path = re.sub(r"/+", "/", path)
                if len(path) > 1:
                    path = path.rstrip("/")

            # Sort query parameters deterministically
            query_str = ""
            if parsed.query:
                qs = parse_qs(parsed.query, keep_blank_values=True)
                sorted_qs = sorted(qs.items())
                # Flatten
                flattened = []
                for k, vals in sorted_qs:
                    for v in sorted(vals):
                        flattened.append((k, v))
                query_str = urlencode(flattened)

            # Reconstruct without fragment
            normalized = urlunparse((scheme, netloc, path, "", query_str, ""))
            return normalized, display
        except Exception:
            return display.lower().rstrip("/#"), display

    @staticmethod
    def normalize_phone(raw_phone: str) -> Tuple[str, str]:
        """Normalize a phone number to standard E.164-compatible format.

        Handles Indian (+91, 0 prefix, 10-digit mobile) and generic international numbers.
        Returns: (normalized_value, display_value)
        """
        if not raw_phone:
            return "", ""

        display = str(raw_phone).strip()
        # Keep digits and leading plus
        digits_only = re.sub(r"[^\d+]", "", display)

        if not digits_only:
            return "", display

        # Indian phone normalization
        if digits_only.startswith("+91"):
            clean = digits_only[3:]
        elif digits_only.startswith("91") and len(digits_only) == 12:
            clean = digits_only[2:]
        elif digits_only.startswith("0") and len(digits_only) == 11:
            clean = digits_only[1:]
        else:
            clean = digits_only.lstrip("+")

        # Standard Indian 10-digit mobile starting with 6, 7, 8, or 9
        if len(clean) == 10 and clean[0] in "6789":
            normalized = f"+91{clean}"
        elif digits_only.startswith("+"):
            normalized = f"+{clean}"
        else:
            normalized = clean

        return normalized, display

    @staticmethod
    def normalize_payment_entity(
        raw_payment: str,
        payment_type: str = "UPI",
    ) -> Tuple[str, str]:
        """Normalize a payment identifier (UPI ID / VPA, Bank Account, or Wallet).

        Returns: (normalized_value, display_value)
        """
        if not raw_payment:
            return "", ""

        display = str(raw_payment).strip()
        ptype = payment_type.upper()

        if "@" in display or ptype == "UPI":
            # UPI handles are case-insensitive
            normalized = display.lower().strip()
            # Collapse spaces
            normalized = re.sub(r"\s+", "", normalized)
            return normalized, display

        if ptype in ("BANK_ACCOUNT", "ACCOUNT"):
            # Strip spaces and hyphens from bank accounts
            normalized = re.sub(r"[\s\-]", "", display).upper()
            return normalized, display

        # Generic wallet or identifier
        normalized = re.sub(r"\s+", "", display).lower()
        return normalized, display

    @staticmethod
    def normalize_ip(raw_ip: str) -> Tuple[str, str]:
        """Normalize an IPv4 or IPv6 address.

        Returns: (normalized_value, display_value)
        """
        if not raw_ip:
            return "", ""

        display = str(raw_ip).strip()
        try:
            ip_obj = ipaddress.ip_address(display)
            normalized = str(ip_obj)
            return normalized, display
        except ValueError:
            return display.lower(), display

    @staticmethod
    def normalize_email(raw_email: str) -> Tuple[str, str]:
        """Normalize an email address.

        Returns: (normalized_value, display_value)
        """
        if not raw_email:
            return "", ""

        display = str(raw_email).strip()
        normalized = display.lower().strip()
        return normalized, display

    @staticmethod
    def normalize_asn(raw_asn: str) -> Tuple[str, str]:
        """Normalize an Autonomous System Number (ASN).

        Returns: (normalized_value, display_value)
        """
        if not raw_asn:
            return "", ""

        display = str(raw_asn).strip()
        # Extract number
        digits = re.sub(r"[^\d]", "", display)
        if digits:
            normalized = f"AS{digits}"
        else:
            normalized = display.upper()
        return normalized, display

    @staticmethod
    def normalize_certificate(raw_cert: str) -> Tuple[str, str]:
        """Normalize a certificate SHA256 or SHA1 fingerprint.

        Returns: (normalized_value, display_value)
        """
        if not raw_cert:
            return "", ""

        display = str(raw_cert).strip()
        normalized = re.sub(r"[:\s]", "", display).lower()
        return normalized, display

    @staticmethod
    def normalize_nameserver(raw_ns: str) -> Tuple[str, str]:
        """Normalize a DNS nameserver hostname.

        Returns: (normalized_value, display_value)
        """
        if not raw_ns:
            return "", ""

        display = str(raw_ns).strip()
        normalized = display.lower().rstrip(".")
        return normalized, display

    @staticmethod
    def normalize_brand(raw_brand: str) -> Tuple[str, str]:
        """Normalize an impersonated brand or entity name.

        Returns: (normalized_value, display_value)
        """
        if not raw_brand:
            return "", ""

        display = str(raw_brand).strip()
        normalized = re.sub(r"\s+", " ", display).upper().strip()
        return normalized, display


# Default singleton instance
entity_normalizer = EntityNormalizer()
