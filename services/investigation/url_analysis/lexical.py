"""Lexical URL Feature Extractor (Step 16).

Deterministic feature extraction for machine learning models and heuristic analysis.
Emits canonical Evidence without making premature fraud verdicts.
"""

import math
import re
from collections import Counter
from datetime import datetime, timezone
from typing import List, Tuple
from uuid import uuid4

from services.api.app.domain.enums import EvidenceSource
from services.api.app.domain.models import Evidence
from services.investigation.url_analysis.models import NormalizedURL, URLFeatureSet

SUSPICIOUS_TOKENS = {
    "login", "signin", "verify", "verification", "secure", "security",
    "account", "banking", "update", "kyc", "wallet", "support",
    "service", "portal", "confirm", "free", "claim", "reward", "token",
    "refund", "police", "arrest", "cbi", "rbi", "court", "bill"
}


class LexicalAnalyzer:
    """Extracts deterministic lexical feature sets and canonical Evidence."""

    @classmethod
    def extract_features(cls, norm_url: NormalizedURL) -> URLFeatureSet:
        url_str = norm_url.normalized_url
        hostname = norm_url.hostname
        path = norm_url.path

        # Basic lengths
        url_length = len(url_str)
        hostname_length = len(hostname)
        path_length = len(path)

        # Character counts
        number_of_dots = url_str.count(".")
        number_of_hyphens = url_str.count("-")
        number_of_digits = sum(1 for c in url_str if c.isdigit())

        # Subdomains
        parts = hostname.split(".")
        subdomain_count = max(0, len(parts) - 2)

        # Flags
        has_ip = norm_url.is_ip_host
        has_punycode = hostname.startswith("xn--") or ".xn--" in hostname
        https_scheme = norm_url.scheme == "https"

        # Entropy calculation on hostname
        hostname_entropy = cls._calculate_shannon_entropy(hostname)

        # Suspicious token occurrences in full URL
        lowered = url_str.lower()
        suspicious_token_count = sum(1 for token in SUSPICIOUS_TOKENS if token in lowered)

        # Encoded characters count (%xx)
        encoded_character_count = len(re.findall(r"%[0-9a-fA-F]{2}", url_str))

        # Query parameter count
        query_parameter_count = 0
        if norm_url.query:
            query_parameter_count = len(norm_url.query.split("&"))

        return URLFeatureSet(
            url_length=url_length,
            hostname_length=hostname_length,
            path_length=path_length,
            number_of_dots=number_of_dots,
            number_of_hyphens=number_of_hyphens,
            number_of_digits=number_of_digits,
            subdomain_count=subdomain_count,
            has_ip_hostname=has_ip,
            has_punycode=has_punycode,
            https_scheme=https_scheme,
            hostname_entropy=round(hostname_entropy, 3),
            suspicious_token_count=suspicious_token_count,
            encoded_character_count=encoded_character_count,
            query_parameter_count=query_parameter_count,
        )

    @classmethod
    def generate_evidence(
        cls,
        incident_id: str,
        norm_url: NormalizedURL,
        features: URLFeatureSet,
    ) -> List[Evidence]:
        """Translates lexical observations into canonical ScamGraph Evidence."""
        evidence_items: List[Evidence] = []
        now = datetime.now(timezone.utc)

        # 1. Base Lexical Observation
        evidence_items.append(
            Evidence(
                id=f"evi-lex-{uuid4().hex[:8]}",
                incident_id=incident_id,
                source=EvidenceSource.URL_ANALYZER,
                signal="URL_LEXICAL_OBSERVATION",
                observation=(
                    f"URL length: {features.url_length}, Dots: {features.number_of_dots}, "
                    f"Suspicious tokens: {features.suspicious_token_count}, Entropy: {features.hostname_entropy}"
                ),
                confidence=0.85,
                timestamp=now,
            )
        )

        # 2. IP Hostname Alert
        if features.has_ip_hostname:
            evidence_items.append(
                Evidence(
                    id=f"evi-iphost-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.URL_ANALYZER,
                    signal="DIRECT_IP_HOST_OBSERVED",
                    observation=f"Destination uses raw IP address instead of registered domain: {norm_url.hostname}",
                    confidence=0.92,
                    timestamp=now,
                )
            )

        # 3. Punycode / Homograph Alert
        if features.has_punycode:
            evidence_items.append(
                Evidence(
                    id=f"evi-puny-{uuid4().hex[:8]}",
                    incident_id=incident_id,
                    source=EvidenceSource.URL_ANALYZER,
                    signal="PUNYCODE_HOMOGRAPH_OBSERVED",
                    observation=f"Hostname contains internationalized punycode sequence: {norm_url.hostname}",
                    confidence=0.90,
                    timestamp=now,
                )
            )

        return evidence_items

    @staticmethod
    def _calculate_shannon_entropy(text: str) -> float:
        """Calculates Shannon entropy in bits for character diversity."""
        if not text:
            return 0.0
        counts = Counter(text)
        length = len(text)
        return -sum((c / length) * math.log2(c / length) for c in counts.values())
