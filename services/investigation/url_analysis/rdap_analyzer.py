"""RDAP Domain Registration Analyzer (Step 16).

Queries public RDAP bootstrap endpoints to collect domain age, registrar,
and nameserver records. Never fabricates domain metadata.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
import httpx

from services.api.app.domain.enums import EntityType, EvidenceSource
from services.api.app.domain.models import Entity, Evidence
from services.investigation.url_analysis.models import NormalizedURL


class RDAPAnalyzer:
    """Safely queries RDAP protocol endpoints for registration metadata."""

    def __init__(self, timeout_seconds: float = 3.0, base_rdap_url: str = "https://rdap.org"):
        self.timeout = timeout_seconds
        self.base_url = base_rdap_url.rstrip("/")

    async def analyze(
        self,
        incident_id: str,
        norm_url: NormalizedURL,
    ) -> Tuple[List[Evidence], List[Entity], List[str]]:
        """Queries RDAP for domain registration details."""
        evidence_items: List[Evidence] = []
        entities: List[Entity] = []
        errors: List[str] = []
        now = datetime.now(timezone.utc)

        domain = norm_url.registered_domain
        if norm_url.is_ip_host or not domain or domain.endswith((".test", ".example", ".invalid", ".local")):
            return evidence_items, entities, errors

        endpoint = f"{self.base_url}/domain/{domain}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(endpoint)

                if response.status_code == 200:
                    data = response.json()
                    parsed_obs = self._parse_rdap_payload(data)

                    # Create canonical domain registration evidence
                    obs_parts = []
                    if parsed_obs.get("registrar"):
                        obs_parts.append(f"Registrar: {parsed_obs['registrar']}")
                    if parsed_obs.get("created_date"):
                        obs_parts.append(f"Created: {parsed_obs['created_date']}")
                    if parsed_obs.get("expires_date"):
                        obs_parts.append(f"Expires: {parsed_obs['expires_date']}")

                    obs_str = "; ".join(obs_parts) if obs_parts else "Domain registration record retrieved"

                    evidence_items.append(
                        Evidence(
                            id=f"evi-rdap-{uuid4().hex[:8]}",
                            incident_id=incident_id,
                            source=EvidenceSource.RDAP,
                            signal="DOMAIN_REGISTRATION_OBSERVATION",
                            observation=f"RDAP for {domain}: {obs_str}",
                            confidence=0.90,
                            timestamp=now,
                        )
                    )

                    # Extract nameserver entities
                    for ns in parsed_obs.get("nameservers", []):
                        entities.append(
                            Entity(
                                id=f"ent-ns-{uuid4().hex[:8]}",
                                entity_type=EntityType.NAMESERVER,
                                normalized_value=ns.lower(),
                                display_value=ns,
                            )
                        )
                elif response.status_code == 404:
                    errors.append(f"RDAP record for {domain} not found (404).")
                else:
                    errors.append(f"RDAP service returned HTTP {response.status_code} for {domain}.")

        except (httpx.TimeoutException, httpx.NetworkError, Exception) as e:
            # RDAP unavailable is NOT evidence of fraud
            errors.append(f"RDAP query unavailable for {domain}: {e}")

        return evidence_items, entities, errors

    @staticmethod
    def _parse_rdap_payload(data: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts key registration fields from RDAP JSON."""
        result: Dict[str, Any] = {
            "registrar": None,
            "created_date": None,
            "expires_date": None,
            "nameservers": [],
        }

        # Entities / Registrar
        for ent in data.get("entities", []):
            roles = ent.get("roles", [])
            if "registrar" in roles:
                vcard = ent.get("vcardArray", [])
                if len(vcard) > 1 and isinstance(vcard[1], list):
                    for item in vcard[1]:
                        if len(item) > 3 and item[0] == "fn":
                            result["registrar"] = item[3]
                            break

        # Events (Registration & Expiration dates)
        for ev in data.get("events", []):
            action = ev.get("eventAction")
            date_str = ev.get("eventDate")
            if action in ("registration", "created"):
                result["created_date"] = date_str
            elif action in ("expiration", "expires"):
                result["expires_date"] = date_str

        # Nameservers
        ns_list = data.get("nameservers", [])
        for ns in ns_list:
            ldh = ns.get("ldhName")
            if ldh:
                result["nameservers"].append(ldh)

        return result
