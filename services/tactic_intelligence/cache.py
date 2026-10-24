"""Intelligence Cache for Tactic Inference in ScamGraph AI V2.

Caches tactic inference results keyed by content hash, context hash, and engine version.
"""

from datetime import datetime, timezone, timedelta
import hashlib
from typing import Any, Dict, List, Optional
from packages.schemas.tactics import TacticSignal


class TacticCache:
    """Thread-safe in-memory cache with TTL for tactic detection results."""

    def __init__(self, ttl_seconds: int = 3600, engine_version: str = "2.0.0"):
        self.ttl = timedelta(seconds=ttl_seconds)
        self.engine_version = engine_version
        self._store: Dict[str, Dict[str, Any]] = {}

    def _compute_key(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        ctx_str = str(sorted(context.items())) if context else ""
        raw = f"{text.strip().lower()}|{ctx_str}|{self.engine_version}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, text: str, context: Optional[Dict[str, Any]] = None) -> Optional[List[TacticSignal]]:
        key = self._compute_key(text, context)
        entry = self._store.get(key)
        if not entry:
            return None
        if datetime.now(timezone.utc) > entry["expires_at"]:
            del self._store[key]
            return None
        return entry["signals"]

    def set(self, text: str, signals: List[TacticSignal], context: Optional[Dict[str, Any]] = None) -> None:
        key = self._compute_key(text, context)
        self._store[key] = {
            "signals": signals,
            "expires_at": datetime.now(timezone.utc) + self.ttl,
            "created_at": datetime.now(timezone.utc),
        }

    def clear(self) -> None:
        self._store.clear()
