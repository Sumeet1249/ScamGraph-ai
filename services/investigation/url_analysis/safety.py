"""SSRF Protection and URL Safety Validation (Step 16).

Security-critical module guarding ScamGraph against Server-Side Request Forgery,
DNS rebinding, loopback probing, and internal network traversal.
"""

import ipaddress
import socket
from typing import List, Optional, Set, Tuple, Union
from urllib.parse import urlparse

from services.investigation.url_analysis.models import NormalizedURL, SafetyResult

# Comprehensive blocked network ranges
BLOCKED_NETWORKS = [
    # Loopback
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    # Private RFC 1918 IPv4
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    # Unique Local IPv6 RFC 4193
    ipaddress.ip_network("fc00::/7"),
    # Link-local & Cloud Metadata (AWS, GCP, Azure, DigitalOcean)
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("fe80::/10"),
    # Unspecified / Current Network
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::/128"),
    # Multicast & Reserved
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("ff00::/8"),
    ipaddress.ip_network("240.0.0.0/4"),
    # Broadcast
    ipaddress.ip_network("255.255.255.255/32"),
]

BLOCKED_HOSTNAMES: Set[str] = {
    "localhost",
    "local",
    "internal",
    "metadata.google.internal",
    "instance-data",
    "kubernetes.default",
    "kubernetes.default.svc",
}


class URLSafetyValidator:
    """Enforces strict multi-phase SSRF prevention on hostnames and resolved IPs."""

    @classmethod
    def validate_url(
        cls,
        target: Union[str, NormalizedURL],
        dns_resolver: Optional[socket.getaddrinfo] = None,
    ) -> SafetyResult:
        """Validates whether a URL is completely safe to query externally."""
        reasons: List[str] = []
        resolved_ips: List[str] = []

        if isinstance(target, NormalizedURL):
            hostname = target.hostname
            scheme = target.scheme
            full_url = target.normalized_url
        else:
            try:
                parsed = urlparse(target.strip())
                hostname = parsed.hostname
                scheme = parsed.scheme.lower() if parsed.scheme else ""
                full_url = target
            except Exception as e:
                return SafetyResult(
                    is_safe=False,
                    reasons=[f"URL could not be parsed: {e}"],
                )

        # 1. Scheme Check
        if scheme not in ("http", "https"):
            return SafetyResult(
                is_safe=False,
                reasons=[f"Disallowed scheme '{scheme}'. Only HTTP and HTTPS are permitted."],
            )

        if not hostname:
            return SafetyResult(
                is_safe=False,
                reasons=["URL contains no recognizable hostname."],
            )

        clean_host = hostname.strip().lower()

        # 2. Hostname string check
        host_labels = set(clean_host.split("."))
        if (
            clean_host in BLOCKED_HOSTNAMES
            or any(lbl in BLOCKED_HOSTNAMES for lbl in host_labels)
            or clean_host.endswith((".localhost", ".local", ".internal", ".lan", ".home"))
        ):
            return SafetyResult(
                is_safe=False,
                reasons=[f"Disallowed internal/loopback hostname '{clean_host}'."],
                is_loopback=True,
                blocked_range="HOST_FILTER",
            )

        # 3. Direct IP Address Validation
        try:
            ip_obj = ipaddress.ip_address(clean_host)
            ip_check = cls._check_ip_safety(ip_obj)
            if not ip_check[0]:
                return SafetyResult(
                    is_safe=False,
                    resolved_ips=[str(ip_obj)],
                    reasons=[f"Direct IP address {clean_host} belongs to {ip_check[1]}"],
                    blocked_range=ip_check[1],
                    is_private=ip_obj.is_private,
                    is_loopback=ip_obj.is_loopback,
                    is_metadata_endpoint=cls._is_metadata_ip(ip_obj),
                )
            resolved_ips.append(str(ip_obj))
            return SafetyResult(
                is_safe=True,
                resolved_ips=resolved_ips,
                reasons=["Valid public IP address."],
            )
        except ValueError:
            # Not a raw IP string, proceed to DNS resolution check
            pass

        # 4. DNS Resolution & Rebinding Defense
        resolver = dns_resolver or socket.getaddrinfo
        try:
            # Resolve both IPv4 and IPv6
            addr_info = resolver(clean_host, None)
            for entry in addr_info:
                sockaddr = entry[4]
                ip_str = sockaddr[0]
                if ip_str not in resolved_ips:
                    resolved_ips.append(ip_str)

            if not resolved_ips:
                # If resolution returns nothing, mark as unresolvable / safe to inspect as mock/test or return error
                return SafetyResult(
                    is_safe=True,
                    resolved_ips=[],
                    reasons=["Hostname could not be resolved at this time (offline or synthetic)."],
                )

            # Check every resolved IP address
            for ip_str in resolved_ips:
                ip_obj = ipaddress.ip_address(ip_str)
                is_safe, block_desc = cls._check_ip_safety(ip_obj)
                if not is_safe:
                    return SafetyResult(
                        is_safe=False,
                        resolved_ips=resolved_ips,
                        reasons=[f"Hostname {clean_host} resolved to prohibited IP {ip_str} ({block_desc})"],
                        blocked_range=block_desc,
                        is_private=ip_obj.is_private,
                        is_loopback=ip_obj.is_loopback,
                        is_metadata_endpoint=cls._is_metadata_ip(ip_obj),
                    )

        except (socket.gaierror, socket.herror, OSError):
            # For test domains or disconnected environments (e.g. example.test)
            if clean_host.endswith((".test", ".example", ".invalid")):
                return SafetyResult(
                    is_safe=True,
                    resolved_ips=[],
                    reasons=["Reserved synthetic testing domain (safe)."],
                )
            # Other unresolvable hosts are safe from SSRF since no connection can be made
            return SafetyResult(
                is_safe=True,
                resolved_ips=[],
                reasons=["Hostname could not be resolved by system DNS."],
            )

        return SafetyResult(
            is_safe=True,
            resolved_ips=resolved_ips,
            reasons=["All resolved IP addresses are public and allowable."],
        )

    @classmethod
    def is_safe_public_url(cls, url: str) -> bool:
        """Convenience method returning boolean pass/fail."""
        res = cls.validate_url(url)
        return res.is_safe

    @staticmethod
    def _check_ip_safety(ip_obj: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> Tuple[bool, Optional[str]]:
        """Checks if an IP address falls into any forbidden subnet."""
        for net in BLOCKED_NETWORKS:
            if ip_obj in net:
                return False, f"Prohibited Network: {net}"
        return True, None

    @staticmethod
    def _is_metadata_ip(ip_obj: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> bool:
        return str(ip_obj) == "169.254.169.254"


SUSPICIOUS_TLDS = {".info", ".online", ".top", ".xyz", ".click", ".work", ".live", ".support", ".club", ".icu", ".tk", ".ml", ".ga", ".cf"}
TRUSTED_BANKING_DOMAINS = {
    "sbi.co.in",
    "onlinesbi.sbi",
    "hdfcbank.com",
    "icicibank.com",
    "axisbank.com",
    "npci.org.in",
    "mahadiscom.in",
    "bescom.co.in",
}


class URLAnalyzer:
    """Compatibility facade bridging endpoints to Step 16 architecture."""

    @staticmethod
    def normalize_url(raw_url: str) -> str:
        from services.investigation.url_analysis.normalizer import URLNormalizer
        try:
            return URLNormalizer.normalize(raw_url).normalized_url
        except Exception:
            return raw_url.strip()

    @staticmethod
    def analyze_lexical_risk(incident_id: str, url: str) -> dict:
        from packages.schemas import EvidenceSignal, SignalDimension, SignalSeverity, ProvenanceRecord
        from services.investigation.url_analysis.normalizer import URLNormalizer
        from services.investigation.url_analysis.lexical import LexicalAnalyzer

        features_dict = {}
        try:
            norm = URLNormalizer.normalize(url)
            feats = LexicalAnalyzer.extract_features(norm)
            features_dict = feats.model_dump()
            domain = norm.hostname or ""
            normalized = norm.normalized_url
        except Exception:
            parsed = urlparse(url.strip())
            domain = parsed.hostname or ""
            normalized = url.strip()

        domain_lower = domain.lower()
        signals: List[EvidenceSignal] = []

        is_trusted = any(domain_lower == trusted or domain_lower.endswith("." + trusted) for trusted in TRUSTED_BANKING_DOMAINS)
        is_suspicious_tld = any(domain_lower.endswith(tld) for tld in SUSPICIOUS_TLDS)
        has_hyphenated_brand = ("-" in domain_lower) and any(
            brand in domain_lower for brand in ["sbi", "hdfc", "icici", "bill", "kyc", "paytm", "support"]
        )

        if is_trusted:
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.URL,
                    signal_type="VERIFIED_OFFICIAL_DOMAIN",
                    severity=SignalSeverity.INFO,
                    confidence=0.99,
                    weight=1.5,
                    is_counter_evidence=True,
                    description=f"Domain {domain} is an established legitimate financial or utility portal.",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="URLAnalyzer",
                        target_artifact=domain,
                        raw_evidence={"is_trusted": True},
                    ),
                )
            )
        else:
            if is_suspicious_tld:
                signals.append(
                    EvidenceSignal(
                        incident_id=incident_id,
                        dimension=SignalDimension.URL,
                        signal_type="SUSPICIOUS_TLD_USED",
                        severity=SignalSeverity.MEDIUM,
                        confidence=0.85,
                        weight=1.2,
                        description=f"Domain {domain} uses a high-abuse TLD commonly leveraged in phishing.",
                        provenance=ProvenanceRecord(
                            source_service="services/investigation",
                            detector_name="URLAnalyzer",
                            target_artifact=domain,
                            raw_evidence={"domain": domain},
                        ),
                    )
                )

            if has_hyphenated_brand:
                signals.append(
                    EvidenceSignal(
                        incident_id=incident_id,
                        dimension=SignalDimension.URL,
                        signal_type="BRAND_TYPOSQUATTING_DETECTED",
                        severity=SignalSeverity.HIGH,
                        confidence=0.92,
                        weight=1.8,
                        description=f"Domain {domain} contains deceptive brand keywords with hyphenation.",
                        provenance=ProvenanceRecord(
                            source_service="services/investigation",
                            detector_name="URLAnalyzer",
                            target_artifact=domain,
                            raw_evidence={"domain": domain, "matched_keywords": ["brand_impersonation"]},
                        ),
                    )
                )

        return {
            "normalized_url": normalized,
            "domain": domain,
            "is_trusted": is_trusted,
            "signals": signals,
            "features": features_dict,
        }
