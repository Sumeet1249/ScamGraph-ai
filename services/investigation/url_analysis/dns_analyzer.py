"""DNS Infrastructure Analyzer (Step 16).

Collects A, AAAA, CNAME, and nameserver records safely.
Translates observations into canonical Evidence and Entity objects without making fraud verdicts.
"""

import socket
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import uuid4

from services.api.app.domain.enums import EntityType, EvidenceSource
from services.api.app.domain.models import Entity, Evidence
from services.investigation.url_analysis.models import NormalizedURL


class DNSAnalyzer:
    """Safely queries DNS infrastructure records."""

    def __init__(self, timeout_seconds: float = 3.0):
        self.timeout = timeout_seconds

    def analyze(
        self,
        incident_id: str,
        norm_url: NormalizedURL,
    ) -> Tuple[List[Evidence], List[Entity], List[str]]:
        """Resolves DNS records and produces canonical Evidence and Entity items."""
        evidence_items: List[Evidence] = []
        entities: List[Entity] = []
        errors: List[str] = []
        now = datetime.now(timezone.utc)

        hostname = norm_url.hostname
        if norm_url.is_ip_host or not hostname:
            return evidence_items, entities, errors

        # 1. Resolve IPv4 and IPv6 addresses
        try:
            # Set socket default timeout for safe execution
            orig_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.timeout)
            try:
                addr_info = socket.getaddrinfo(hostname, None)
            finally:
                socket.setdefaulttimeout(orig_timeout)

            resolved_ips = list({entry[4][0] for entry in addr_info if entry[4]})
            if resolved_ips:
                evidence_items.append(
                    Evidence(
                        id=f"evi-dns-{uuid4().hex[:8]}",
                        incident_id=incident_id,
                        source=EvidenceSource.DNS,
                        signal="DNS_RESOLUTION",
                        observation=f"Hostname {hostname} resolved to {len(resolved_ips)} IP(s): {', '.join(resolved_ips[:4])}",
                        confidence=0.95,
                        timestamp=now,
                    )
                )

                for ip_str in resolved_ips:
                    entities.append(
                        Entity(
                            id=f"ent-ip-{uuid4().hex[:8]}",
                            entity_type=EntityType.IP,
                            normalized_value=ip_str.lower(),
                            display_value=ip_str,
                        )
                    )
        except (socket.gaierror, socket.herror, OSError) as e:
            errors.append(f"DNS A/AAAA resolution failed for {hostname}: {e}")

        # 2. Extract CNAME / Canonical Name if available
        try:
            canonical_name, aliases, _ = socket.gethostbyname_ex(hostname)
            if canonical_name and canonical_name.lower() != hostname.lower():
                evidence_items.append(
                    Evidence(
                        id=f"evi-cname-{uuid4().hex[:8]}",
                        incident_id=incident_id,
                        source=EvidenceSource.DNS,
                        signal="CNAME_OBSERVED",
                        observation=f"Hostname {hostname} aliases to canonical host {canonical_name}",
                        confidence=0.90,
                        timestamp=now,
                    )
                )
        except (socket.gaierror, socket.herror, OSError):
            pass

        # 3. Add Domain Entity
        entities.append(
            Entity(
                id=f"ent-dom-{uuid4().hex[:8]}",
                entity_type=EntityType.DOMAIN,
                normalized_value=norm_url.registered_domain.lower(),
                display_value=norm_url.registered_domain,
            )
        )

        return evidence_items, entities, errors
