"""Low-Level TinyFish API Client with Live & Mock Modes (Step 17).

Enforces:
- Rule 6: Server-side credentials only (TINYFISH_API_KEY from environment).
- Rule 21: Bounded 4s timeouts and 2 retries with exponential backoff.
- Rule 22: Graceful error recovery without crashing the overall assessment.
- Mock mode support (TINYFISH_MODE=mock | live).
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
import httpx

from services.api.app.core.config import settings
from services.investigation.tinyfish.exceptions import (
    TinyFishConfigError,
    TinyFishMalformedResponseError,
    TinyFishRateLimitError,
    TinyFishTimeoutError,
)
from services.investigation.tinyfish.prompts import TINYFISH_EXTRACTION_PROMPT, TINYFISH_SYSTEM_PROMPT

logger = logging.getLogger("investigation.tinyfish.client")

FIXTURES_DIR = Path("s:/ScamGraph-AI/tests/fixtures/tinyfish")


class TinyFishClient:
    """Async client communicating with TinyFish endpoint or controlled fixtures."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        mode: Optional[str] = None,
        fixtures_path: Optional[Path] = None,
    ):
        self.api_key = api_key or getattr(settings, "TINYFISH_API_KEY", None) or os.getenv("TINYFISH_API_KEY")
        self.base_url = (base_url or getattr(settings, "TINYFISH_BASE_URL", "https://api.tinyfish.io/v1")).rstrip("/")
        # Mode: "mock" or "live"
        self.mode = mode or os.getenv("TINYFISH_MODE", "mock").lower()
        self.fixtures_path = fixtures_path or FIXTURES_DIR
        self.timeout = 4.0
        self.max_retries = 2

    async def fetch_page_observables(self, target_url: str) -> Optional[Dict[str, Any]]:
        """Fetches page observables either from the live API or mock fixtures."""
        if self.mode == "mock":
            return self._fetch_mock_observables(target_url)

        # ── LIVE MODE ──
        if not self.api_key:
            logger.warning("TinyFish API key not configured; live fetch cannot proceed.")
            raise TinyFishConfigError("TINYFISH_API_KEY environment variable is required for live mode.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "url": target_url,
            "system_prompt": TINYFISH_SYSTEM_PROMPT,
            "prompt": TINYFISH_EXTRACTION_PROMPT,
        }

        last_error = None
        for attempt in range(1, self.max_retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(f"{self.base_url}/investigate", json=payload, headers=headers)

                    if resp.status_code == 200:
                        try:
                            data = resp.json()
                            if isinstance(data, dict):
                                return data
                            raise TinyFishMalformedResponseError(f"Expected dict from TinyFish, got {type(data)}")
                        except Exception as parse_err:
                            raise TinyFishMalformedResponseError(f"Failed to parse TinyFish JSON: {parse_err}")

                    elif resp.status_code == 429:
                        raise TinyFishRateLimitError("TinyFish rate limit exceeded (HTTP 429).")

                    elif resp.status_code >= 500:
                        logger.warning("TinyFish 5xx error (%s). Attempt %d/%d.", resp.status_code, attempt, self.max_retries + 1)
                        last_error = Exception(f"HTTP {resp.status_code}")
                    else:
                        logger.warning("TinyFish client error (%s): %s", resp.status_code, resp.text[:120])
                        return None

            except (httpx.TimeoutException, asyncio.TimeoutError) as to_err:
                logger.warning("TinyFish timeout on attempt %d/%d for %s", attempt, self.max_retries + 1, target_url)
                last_error = TinyFishTimeoutError(f"Timeout querying {target_url}: {to_err}")
            except (httpx.NetworkError, OSError) as net_err:
                logger.warning("TinyFish network issue on attempt %d/%d: %s", attempt, self.max_retries + 1, net_err)
                last_error = net_err

            if attempt <= self.max_retries:
                await asyncio.sleep(0.4 * attempt)

        if isinstance(last_error, TinyFishTimeoutError):
            raise last_error
        return None

    def _fetch_mock_observables(self, target_url: str) -> Optional[Dict[str, Any]]:
        """Returns deterministic fixture JSON for controlled hackathon testing."""
        lowered = target_url.lower()

        if "malform" in lowered:
            fixture_file = self.fixtures_path / "malformed_response.json"
        elif any(k in lowered for k in ["kyc", "sbi", "bank", "verify-portal"]):
            fixture_file = self.fixtures_path / "kyc_test_site.json"
        elif any(k in lowered for k in ["invest", "crypto", "trading", "yield"]):
            fixture_file = self.fixtures_path / "investment_test_site.json"
        else:
            fixture_file = self.fixtures_path / "benign_site.json"

        if not fixture_file.exists():
            logger.warning("Fixture file not found: %s", fixture_file)
            return None

        with open(fixture_file, "r", encoding="utf-8") as f:
            return json.load(f)
