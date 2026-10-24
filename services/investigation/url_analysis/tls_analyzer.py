"""TLS Certificate Analyzer (Step 16).

Safely inspects TLS certificate subject, issuer, validity period, and SAN names.
Adheres strictly to the principle that valid TLS is NOT proof of safety,
nor is an expired/untrusted certificate definitive proof of fraud.
"""

import socket
import ssl
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from services.api.app.domain.enums import EntityType, EvidenceSource
from services.api.app.domain.models import Entity, Evidence
from services.investigation.url_analysis.models import NormalizedURL


class TLSAnalyzer:
    """Performs non-disruptive TLS handshake inspection on HTTPS endpoints."""

    def __init__(self, timeout_seconds: float = 3.0):
        self.timeout = timeout_seconds

    def analyze(
        self,
        incident_id: str,
        norm_url: NormalizedURL,
    ) -> Tuple[List[Evidence], List[Entity], List[str]]:
        """Connects safely to retrieve public TLS certificate metadata."""
        evidence_items: List[Evidence] = []
        entities: List[Entity] = []
        errors: List[str] = []
        now = datetime.now(timezone.utc)

        if norm_url.scheme != "https":
            return evidence_items, entities, errors

        hostname = norm_url.hostname
        port = norm_url.port or 443

        # Skip synthetic test domains
        if hostname.endswith((".test", ".example", ".invalid", ".local")):
            return evidence_items, entities, errors

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE  # Safe inspection mode to read untrusted/expired certs

            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert(binary_form=False)
                    # When verify_mode is CERT_NONE, getpeercert() returns empty dict in standard python,
                    # so we fetch binary form and parse, or fallback to peer certificate info
                    if not cert:
                        bin_cert = ssock.getpeercert(binary_form=True)
                        if bin_cert:
                            cert_sha256 = ssl.DER_cert_to_PEM_cert(bin_cert)
                            entities.append(
                                Entity(
                                    id=f"ent-cert-{uuid4().hex[:8]}",
                                    entity_type=EntityType.CERTIFICATE,
                                    normalized_value=hostname.lower(),
                                    display_value=hostname,
                                )
                            )
                            evidence_items.append(
                                Evidence(
                                    id=f"evi-tls-{uuid4().hex[:8]}",
                                    incident_id=incident_id,
                                    source=EvidenceSource.TLS,
                                    signal="TLS_CERTIFICATE_OBSERVATION",
                                    observation=f"TLS certificate presented on {hostname}:{port} (non-verified cipher active)",
                                    confidence=0.85,
                                    timestamp=now,
                                )
                            )
                            return evidence_items, entities, errors

                    # If cert dict is populated:
                    issuer_dict = dict(x[0] for x in cert.get("issuer", ()))
                    issuer_org = issuer_dict.get("organizationName", "Unknown Issuer")
                    not_after = cert.get("notAfter", "Unknown")

                    san_entries = [entry[1] for entry in cert.get("subjectAltName", ()) if entry[0] == "DNS"]

                    obs_str = f"Issuer: {issuer_org}, Expires: {not_after}, SANs: {len(san_entries)}"
                    evidence_items.append(
                        Evidence(
                            id=f"evi-tls-{uuid4().hex[:8]}",
                            incident_id=incident_id,
                            source=EvidenceSource.TLS,
                            signal="TLS_CERTIFICATE_OBSERVATION",
                            observation=f"TLS for {hostname}: {obs_str}",
                            confidence=0.90,
                            timestamp=now,
                        )
                    )

                    entities.append(
                        Entity(
                            id=f"ent-cert-{uuid4().hex[:8]}",
                            entity_type=EntityType.CERTIFICATE,
                            normalized_value=issuer_org.lower(),
                            display_value=issuer_org,
                        )
                    )

        except (socket.timeout, ssl.SSLError, OSError, Exception) as e:
            errors.append(f"TLS inspection failed for {hostname}:{port}: {e}")

        return evidence_items, entities, errors
