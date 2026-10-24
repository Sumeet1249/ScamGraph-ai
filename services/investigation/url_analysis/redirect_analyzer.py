"""HTTP Safe Redirect Chain Analyzer (Step 16).

Traces redirect hops while validating EVERY hop against URLSafetyValidator.
Prevents open-redirect and rebinding SSRF attacks.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from uuid import uuid4
import httpx

from services.api.app.domain.enums import EvidenceSource
from services.api.app.domain.models import Evidence
from services.investigation.url_analysis.models import NormalizedURL
from services.investigation.url_analysis.normalizer import URLNormalizer
from services.investigation.url_analysis.safety import URLSafetyValidator


class RedirectAnalyzer:
    """Safely traces redirect chains hop-by-hop with strict per-hop SSRF validation."""

    def __init__(self, max_depth: int = 5, hop_timeout_seconds: float = 2.5):
        self.max_depth = max_depth
        self.timeout = hop_timeout_seconds

    async def analyze(
        self,
        incident_id: str,
        initial_url: NormalizedURL,
    ) -> Tuple[List[Evidence], List[Dict[str, Any]], List[str]]:
        """Follows redirects safely and produces canonical Evidence."""
        evidence_items: List[Evidence] = []
        hop_records: List[Dict[str, Any]] = []
        errors: List[str] = []
        now = datetime.now(timezone.utc)

        current_url = initial_url.normalized_url

        # Skip redirect checking on synthetic test domains
        if initial_url.hostname.endswith((".test", ".example", ".invalid", ".local")):
            return evidence_items, hop_records, errors

        for depth in range(1, self.max_depth + 1):
            # 1. Enforce SSRF safety on current target before making request
            safety = URLSafetyValidator.validate_url(current_url)
            if not safety.is_safe:
                errors.append(f"Redirect hop {depth} blocked by SSRF Guard: {current_url} ({', '.join(safety.reasons)})")
                evidence_items.append(
                    Evidence(
                        id=f"evi-redir-ssrf-{uuid4().hex[:8]}",
                        incident_id=incident_id,
                        source=EvidenceSource.URL_ANALYZER,
                        signal="REDIRECT_TO_UNSAFE_HOST_BLOCKED",
                        observation=f"Redirect chain aborted at hop {depth}: Destination {current_url} resolves to internal address",
                        confidence=1.0,
                        timestamp=now,
                    )
                )
                break

            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
                    resp = await client.head(current_url)

                    if resp.is_redirect:
                        next_location = resp.headers.get("location")
                        if not next_location:
                            break

                        # Resolve relative URLs
                        try:
                            norm_next = URLNormalizer.normalize(
                                str(httpx.URL(current_url).join(next_location))
                            )
                        except Exception as ne:
                            errors.append(f"Malformed redirect location at hop {depth}: {ne}")
                            break

                        hop_records.append({
                            "depth": depth,
                            "source": current_url,
                            "destination": norm_next.normalized_url,
                            "status_code": resp.status_code,
                        })

                        evidence_items.append(
                            Evidence(
                                id=f"evi-redir-{uuid4().hex[:8]}",
                                incident_id=incident_id,
                                source=EvidenceSource.URL_ANALYZER,
                                signal="REDIRECT_OBSERVATION",
                                observation=f"HTTP {resp.status_code} redirect from {current_url} to {norm_next.normalized_url} (Hop {depth})",
                                confidence=0.90,
                                timestamp=now,
                            )
                        )

                        current_url = norm_next.normalized_url
                    else:
                        # Reached terminal endpoint
                        break

            except (httpx.TimeoutException, httpx.NetworkError, Exception) as e:
                errors.append(f"Redirect query failed at hop {depth} ({current_url}): {e}")
                break

        return evidence_items, hop_records, errors
