"""Intelligence Result Cache for ScamGraph AI (Rule 43).

Caches normalized inference results to prevent redundant expensive computation
at scale. Cache keys combine normalized content hash, model version, and intelligence version.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel

from packages.inference.contracts import InferenceResponse


class IntelligenceCache:
    """In-memory TTL cache with normalized content hashing."""

    def __init__(self, max_size: int = 20000, default_ttl_sec: int = 3600):
        self._cache: Dict[str, Tuple[float, InferenceResponse]] = {}
        self._max_size = max_size
        self._default_ttl_sec = default_ttl_sec

    @staticmethod
    def generate_cache_key(
        normalized_text: str,
        model_id: str,
        model_version: str,
        intelligence_version: str = "v1",
    ) -> str:
        """Constructs deterministic hash key (Rule 43)."""
        content_hash = hashlib.sha256(normalized_text.strip().lower().encode("utf-8")).hexdigest()
        return f"{model_id}:{model_version}:{intelligence_version}:{content_hash}"

    def get(self, cache_key: str) -> Optional[InferenceResponse]:
        """Retrieves cached item if present and not expired."""
        entry = self._cache.get(cache_key)
        if entry is None:
            return None
        expires_at, response = entry
        if time.time() > expires_at:
            # Expired
            del self._cache[cache_key]
            return None
        # Return copy with cached_result = True
        cached_resp = response.model_copy()
        cached_resp.cached_result = True
        return cached_resp

    def set(
        self,
        cache_key: str,
        response: InferenceResponse,
        ttl_sec: Optional[int] = None,
    ) -> None:
        """Stores item with TTL."""
        if len(self._cache) >= self._max_size:
            # Evict first 1000 items
            keys_to_remove = list(self._cache.keys())[:1000]
            for k in keys_to_remove:
                del self._cache[k]

        ttl = ttl_sec if ttl_sec is not None else self._default_ttl_sec
        expires_at = time.time() + ttl
        self._cache[cache_key] = (expires_at, response)

    def clear(self) -> None:
        self._cache.clear()

    def __len__(self) -> int:
        return len(self._cache)
