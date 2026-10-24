"""TinyFish API Web Investigator Client.

Harvested from tinyfish-cookbook patterns.
Adheres strictly to:
- Rule 6: Credentials remain strictly server-side.
- Rule 10: Facts collected are observable evidence, never a final fraud verdict.
- Rule 21: Enforces tight network timeouts.
- Rule 22: Continues with partial evidence if TinyFish is unreachable or API key is absent.
"""

import logging
from typing import Any, Dict, List, Optional
import httpx

from services.api.app.core.config import settings
from services.investigation.url_analysis.safety import URLSafetyValidator
from packages.schemas import EvidenceSignal, SignalDimension, SignalSeverity, ProvenanceRecord

logger = logging.getLogger("investigation.tinyfish")


class WebInvestigator:
    """Investigates public web landing pages and extracts observable technical facts."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.TINYFISH_API_KEY
        self.base_url = (base_url or settings.TINYFISH_BASE_URL).rstrip("/")
        self.timeout = 4.0  # Strict 4s timeout (Rule 21)

    async def investigate_url(self, incident_id: str, target_url: str) -> Dict[str, Any]:
        """Investigates a target URL and returns extracted factual evidence signals."""
        # Enforce Rule 9 (SSRF guard) before making any outbound investigation call
        if not URLSafetyValidator.is_safe_public_url(target_url):
            logger.warning("SSRF Guard: target_url rejected: %s", target_url)
            return {
                "status": "REJECTED_UNSAFE_HOST",
                "signals": [
                    EvidenceSignal(
                        incident_id=incident_id,
                        dimension=SignalDimension.URL,
                        signal_type="PRIVATE_OR_UNRESOLVABLE_IP_TARGETED",
                        severity=SignalSeverity.CRITICAL,
                        confidence=1.0,
                        weight=2.0,
                        description="Attempted connection to private, loopback, or internal address.",
                        provenance=ProvenanceRecord(
                            source_service="services/investigation",
                            detector_name="SSRF Guard",
                            target_artifact=target_url,
                            raw_evidence={"ssrf_blocked": True},
                        ),
                    )
                ],
            }

        if not self.api_key:
            logger.info("TinyFish API key not configured. Running in offline/heuristic mode.")
            return {
                "status": "PROVIDER_UNCONFIGURED",
                "signals": [],
            }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "url": target_url,
                    "extract": ["forms", "otp_inputs", "brand_claims", "redirects", "domain_age"],
                }
                resp = await client.post(f"{self.base_url}/investigate", json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    signals = self._parse_tinyfish_observables(incident_id, target_url, data)
                    return {"status": "SUCCESS", "data": data, "signals": signals}
                else:
                    logger.warning("TinyFish API returned status %s", resp.status_code)
                    return {"status": "PROVIDER_ERROR", "signals": []}

        except httpx.TimeoutException:
            logger.warning("TinyFish API timed out for URL %s. Graceful fallback.", target_url)
            return {"status": "TIMEOUT_FALLBACK", "signals": []}
        except Exception as e:
            logger.error("TinyFish API request failed: %s", e)
            return {"status": "ERROR_FALLBACK", "signals": []}

    def _parse_tinyfish_observables(self, incident_id: str, url: str, data: Dict[str, Any]) -> List[EvidenceSignal]:
        """Translates raw factual telemetry into canonical EvidenceSignals."""
        signals: List[EvidenceSignal] = []

        # 1. Check for OTP / Credential Harvesting Fields
        if data.get("has_otp_field"):
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.URL,
                    signal_type="OTP_INPUT_FORM_OBSERVED",
                    severity=SignalSeverity.CRITICAL,
                    confidence=0.98,
                    weight=2.0,
                    description="Web page actively contains an OTP or banking credential input form.",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="TinyFish WebInvestigator",
                        target_artifact=url,
                        raw_evidence=data,
                    ),
                )
            )

        # 2. Check Domain Age
        domain_age = data.get("domain_age_days")
        if domain_age is not None and domain_age < 14:
            signals.append(
                EvidenceSignal(
                    incident_id=incident_id,
                    dimension=SignalDimension.INFRASTRUCTURE,
                    signal_type="NEWLY_REGISTERED_DOMAIN",
                    severity=SignalSeverity.HIGH,
                    confidence=0.95,
                    weight=1.5,
                    description=f"Domain was registered only {domain_age} days ago.",
                    provenance=ProvenanceRecord(
                        source_service="services/investigation",
                        detector_name="TinyFish WebInvestigator",
                        target_artifact=url,
                        raw_evidence={"domain_age_days": domain_age},
                    ),
                )
            )

        return signals
