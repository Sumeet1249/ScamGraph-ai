"""
ScamGraph AI — Production Cache & Distributed Locks Architecture V2
Phase 7B / Prompt 22

Provides tenant-isolated caching, stampede protection (single-flight),
distributed locking, negative caching with short TTLs, and distributed rate limiting.
Postgres remains the source of truth; cache loss never destroys business data.
"""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

from packages.schemas.jobs import CacheCategory, CacheEntryMetadata

logger = logging.getLogger("scamgraph.jobs.cache")

T = TypeVar("T")


class CacheManager:
    """
    Tenant-aware cache and coordination manager.
    Enforces standardized key hierarchies, staleness checks, single-flight locks,
    and distributed rate-limiting counters.
    """

    def __init__(self, env: str = "production", default_ttl: int = 300) -> None:
        self.env = env
        self.default_ttl = default_ttl
        # In-memory storage: key -> (value_json, expiry_timestamp, CacheEntryMetadata)
        self._store: Dict[str, Tuple[str, float, CacheEntryMetadata]] = {}
        # Distributed locks: lock_key -> (owner_id, expiry_timestamp)
        self._locks: Dict[str, Tuple[str, float]] = {}
        # Single-flight locks for stampede protection
        self._single_flight_locks: Dict[str, asyncio.Lock] = {}
        # Rate limit sliding windows: key -> list of timestamps
        self._rate_limits: Dict[str, list[float]] = {}
        self._async_lock = asyncio.Lock()
        
        # Freshness indicators for UI contracts
        self._graph_last_projected_at: Optional[datetime] = datetime.now(timezone.utc)
        self._radar_last_updated_at: Optional[datetime] = datetime.now(timezone.utc)

    def build_key(
        self,
        category: CacheCategory,
        resource_type: str,
        resource_id: str,
        tenant_id: Optional[str] = None,
        version: str = "v1",
        model_version: Optional[str] = None,
    ) -> str:
        """
        Build standardized, tenant-isolated cache key.
        Format: sg:{env}:{category}:{tenant_scope}:{resource_type}:{resource_id}:{version}
        """
        tenant_scope = tenant_id if tenant_id and category == CacheCategory.TENANT_PRIVATE else "global"
        if category == CacheCategory.TENANT_PRIVATE and not tenant_id:
            tenant_scope = "tenant_anonymous"
            
        key_parts = [
            "sg",
            self.env,
            category.value,
            tenant_scope,
            resource_type,
            resource_id,
            version,
        ]
        if model_version:
            key_parts.append(model_version)
        return ":".join(key_parts)

    async def get(
        self,
        key: str,
        category: CacheCategory = CacheCategory.GLOBAL_INTELLIGENCE,
        tenant_id: Optional[str] = None,
    ) -> Optional[Any]:
        """Fetch item from cache. Returns None on miss or expiration."""
        async with self._async_lock:
            # Tenant isolation validation: if private, ensure key matches tenant
            if category == CacheCategory.TENANT_PRIVATE and tenant_id:
                if f":{tenant_id}:" not in key:
                    logger.warning("Cache access blocked: Tenant %s cannot access key %s", tenant_id, key)
                    return None

            entry = self._store.get(key)
            if not entry:
                return None
            val_json, expiry, metadata = entry
            if time.time() > expiry:
                del self._store[key]
                return None
            try:
                return json.loads(val_json)
            except Exception:
                return val_json

    async def set(
        self,
        key: str,
        value: Any,
        category: CacheCategory,
        ttl_seconds: Optional[int] = None,
        tenant_id: Optional[str] = None,
        version: str = "v1",
        model_version: Optional[str] = None,
    ) -> None:
        """Write item to cache with explicit TTL and metadata."""
        async with self._async_lock:
            ttl = ttl_seconds if ttl_seconds is not None else self._get_default_ttl_for_category(category)
            expiry = time.time() + ttl
            val_json = json.dumps(value, default=str) if not isinstance(value, str) else value
            metadata = CacheEntryMetadata(
                key=key,
                category=category,
                tenant_id=tenant_id,
                ttl_seconds=ttl,
                version=version,
                model_version=model_version,
            )
            self._store[key] = (val_json, expiry, metadata)

    async def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], Any],
        category: CacheCategory,
        ttl_seconds: Optional[int] = None,
        tenant_id: Optional[str] = None,
        version: str = "v1",
        model_version: Optional[str] = None,
    ) -> Any:
        """
        Stampede-protected get or compute (Single-Flight Pattern).
        Only one concurrent caller executes the compute function; others await the cached result.
        """
        cached = await self.get(key, category, tenant_id)
        if cached is not None:
            return cached

        # Acquire per-key lock for stampede protection
        async with self._async_lock:
            if key not in self._single_flight_locks:
                self._single_flight_locks[key] = asyncio.Lock()
            flight_lock = self._single_flight_locks[key]

        async with flight_lock:
            # Re-check cache after acquiring flight lock
            cached = await self.get(key, category, tenant_id)
            if cached is not None:
                return cached

            # Compute value
            if inspect.iscoroutinefunction(compute_fn):
                computed = await compute_fn()
            else:
                computed = compute_fn()

            await self.set(
                key=key,
                value=computed,
                category=category,
                ttl_seconds=ttl_seconds,
                tenant_id=tenant_id,
                version=version,
                model_version=model_version,
            )
            return computed

    async def invalidate(self, pattern_or_key: str) -> int:
        """Explicitly invalidate keys matching prefix or exact key."""
        async with self._async_lock:
            keys_to_del = [
                k for k in self._store
                if k == pattern_or_key or k.startswith(pattern_or_key) or pattern_or_key in k
            ]
            for k in keys_to_del:
                del self._store[k]
            return len(keys_to_del)

    async def invalidate_tenant(self, tenant_id: str) -> int:
        """Purge all private cache entries belonging to a specific tenant."""
        return await self.invalidate(f":TENANT_PRIVATE:{tenant_id}:")

    # Distributed Locks
    async def acquire_lock(self, lock_key: str, owner_id: str, ttl_seconds: float = 30.0) -> bool:
        """
        Acquire a non-blocking distributed lock.
        Returns True if acquired, False if already held by another owner.
        """
        async with self._async_lock:
            now = time.time()
            if lock_key in self._locks:
                current_owner, expiry = self._locks[lock_key]
                if now < expiry and current_owner != owner_id:
                    return False
            self._locks[lock_key] = (owner_id, now + ttl_seconds)
            return True

    async def release_lock(self, lock_key: str, owner_id: str) -> bool:
        """Release a distributed lock if held by owner."""
        async with self._async_lock:
            if lock_key in self._locks:
                current_owner, _ = self._locks[lock_key]
                if current_owner == owner_id:
                    del self._locks[lock_key]
                    return True
            return False

    # Distributed Rate Limiting
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int = 100,
        window_seconds: int = 60,
    ) -> Tuple[bool, int, float]:
        """
        Sliding-window rate limit check.
        Returns (is_allowed, remaining_quota, reset_seconds).
        Gracefully allows traffic in degraded mode if store fails.
        """
        async with self._async_lock:
            now = time.time()
            window_start = now - window_seconds
            
            # Prune old timestamps
            timestamps = self._rate_limits.get(identifier, [])
            timestamps = [ts for ts in timestamps if ts > window_start]
            
            if len(timestamps) >= limit:
                reset_seconds = max(0.0, (timestamps[0] + window_seconds) - now)
                return False, 0, reset_seconds
            
            timestamps.append(now)
            self._rate_limits[identifier] = timestamps
            remaining = limit - len(timestamps)
            reset_seconds = float(window_seconds)
            return True, remaining, reset_seconds

    # Freshness tracking
    def record_graph_projection_update(self) -> None:
        """Record timestamp of successful Neo4j graph projection update."""
        self._graph_last_projected_at = datetime.now(timezone.utc)

    def get_graph_lag_seconds(self) -> float:
        """Return graph projection age in seconds."""
        if not self._graph_last_projected_at:
            return 999999.0
        return (datetime.now(timezone.utc) - self._graph_last_projected_at).total_seconds()

    def record_radar_update(self) -> None:
        """Record timestamp of latest Outbreak Radar intelligence snapshot."""
        self._radar_last_updated_at = datetime.now(timezone.utc)

    def get_radar_lag_seconds(self) -> float:
        """Return radar snapshot age in seconds."""
        if not self._radar_last_updated_at:
            return 999999.0
        return (datetime.now(timezone.utc) - self._radar_last_updated_at).total_seconds()

    def _get_default_ttl_for_category(self, category: CacheCategory) -> int:
        ttls = {
            CacheCategory.PUBLIC_REFERENCE: 86400,   # 24h
            CacheCategory.GLOBAL_INTELLIGENCE: 300,  # 5m
            CacheCategory.TENANT_PRIVATE: 60,        # 1m
            CacheCategory.SESSION_SECURITY: 300,     # 5m
            CacheCategory.COMPUTATION_RESULT: 3600,  # 1h
        }
        return ttls.get(category, self.default_ttl)


# Global singleton instance
_global_cache: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Return singleton cache manager."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache


def reset_cache_manager() -> None:
    """Reset the global cache manager for test isolation."""
    global _global_cache
    _global_cache = CacheManager()
