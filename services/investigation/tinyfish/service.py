"""TinyFish WebInvestigator Service Implementation (Step 17).

Implements the WebInvestigator abstraction.
Guarantees:
- URLs are validated against URLSafetyValidator before any call.
- Provider failures return status="unavailable" rather than failing the whole assessment.
- Collects observable facts, never declaring final scam status.
"""

import logging
import time
from typing import Optional
from uuid import uuid4

from services.investigation.tinyfish.client import TinyFishClient
from services.investigation.tinyfish.exceptions import (
    TinyFishConfigError,
    TinyFishError,
    TinyFishMalformedResponseError,
    TinyFishRateLimitError,
    TinyFishTimeoutError,
)
from services.investigation.tinyfish.models import (
    TinyFishObservationData,
    WebInvestigationResult,
    WebInvestigator,
)
from services.investigation.tinyfish.parser import TinyFishParser
from services.investigation.url_analysis.safety import URLSafetyValidator

logger = logging.getLogger("investigation.tinyfish.service")


class TinyFishWebInvestigator(WebInvestigator):
    """Canonical WebInvestigator implementation powered by TinyFish."""

    def __init__(self, client: Optional[TinyFishClient] = None):
        self.client = client or TinyFishClient()

    async def investigate(
        self,
        incident_id: str,
        target_url: str,
    ) -> WebInvestigationResult:
        """Executes live or mock TinyFish web inspection safely."""
        start_time = time.perf_counter()

        # 1. Enforce Rule 9 (SSRF Guard)
        safety = URLSafetyValidator.validate_url(target_url)
        if not safety.is_safe:
            duration = (time.perf_counter() - start_time) * 1000
            logger.warning("SSRF Guard blocked TinyFish investigation of: %s", target_url)
            return WebInvestigationResult(
                provider="TINYFISH",
                status="rejected",
                inspected_url=target_url,
                errors=[f"SSRF Guard: Blocked request to prohibited destination ({', '.join(safety.reasons)})"],
                duration_ms=round(duration, 2),
            )

        # 2. Invoke TinyFish Client (Live or Mock)
        raw_data = None
        error_msgs = []
        try:
            raw_data = await self.client.fetch_page_observables(target_url)
        except TinyFishConfigError as cfg_err:
            error_msgs.append(f"TinyFish configuration error: {cfg_err}")
            logger.info("TinyFish unconfigured: %s", cfg_err)
        except TinyFishTimeoutError as to_err:
            error_msgs.append(f"TinyFish request timed out: {to_err}")
            logger.warning("TinyFish timeout: %s", to_err)
        except TinyFishRateLimitError as rl_err:
            error_msgs.append(f"TinyFish rate limit exceeded: {rl_err}")
            logger.warning("TinyFish rate limit: %s", rl_err)
        except TinyFishMalformedResponseError as mal_err:
            error_msgs.append(f"TinyFish returned malformed data: {mal_err}")
            logger.warning("TinyFish malformed: %s", mal_err)
        except Exception as gen_err:
            error_msgs.append(f"TinyFish provider exception: {gen_err}")
            logger.error("TinyFish error: %s", gen_err)

        duration = (time.perf_counter() - start_time) * 1000

        # If provider failed or returned empty payload
        if not raw_data:
            return WebInvestigationResult(
                provider="TINYFISH",
                status="unavailable",
                inspected_url=target_url,
                errors=error_msgs or ["TinyFish service returned no content."],
                duration_ms=round(duration, 2),
            )

        # 3. Parse Observables into Canonical Evidence & Entities
        obs_data, evidence, entities = TinyFishParser.parse(incident_id, target_url, raw_data)

        # If data was malformed (empty obs_data and empty evidence)
        status = "completed" if evidence else ("partial" if obs_data.page_title else "unavailable")

        return WebInvestigationResult(
            provider="TINYFISH",
            status=status,
            inspected_url=target_url,
            observables=obs_data,
            evidence=evidence,
            entities=entities,
            errors=error_msgs,
            duration_ms=round(duration, 2),
        )


# Global singleton instance
tinyfish_investigator = TinyFishWebInvestigator()
