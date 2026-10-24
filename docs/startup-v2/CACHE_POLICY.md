# CACHE POLICY & COORDINATION ARCHITECTURE V2
**ScamGraph AI — Phase 7B Cache Standard**
*Document Version: 2.0.0 | Date: 2026-10-24*

---

## 1. Core Rule: Cache Is Not the Source of Truth

No business-critical or durable scam data lives exclusively in Redis or volatile cache. On a cache miss, data is reliably reconstituted from PostgreSQL. Redis eviction or restart **NEVER** causes data loss.

---

## 2. Standardized Cache Taxonomy

| Category | Key Pattern | Default TTL | Invalidation Trigger | Staleness Policy |
| :--- | :--- | :--- | :--- | :--- |
| **`PUBLIC_REFERENCE`** | `sg:{env}:PUBLIC_REFERENCE:global:{type}:{id}` | 24 Hours | Admin update | Stale allowable up to 1h |
| **`GLOBAL_INTELLIGENCE`** | `sg:{env}:GLOBAL_INTELLIGENCE:global:{type}:{id}`| 5 Minutes | Campaign / outbreak event | Flagged as STALE if > 5m |
| **`TENANT_PRIVATE`** | `sg:{env}:TENANT_PRIVATE:{tenant}:{type}:{id}` | 60 Seconds | Incident update / retention | Zero staleness tolerance |
| **`SESSION_SECURITY`** | `sg:{env}:SESSION_SECURITY:global:{type}:{id}` | 5 Minutes | Key revocation / logout | Immediate invalidation |
| **`COMPUTATION_RESULT`**| `sg:{env}:COMPUTATION_RESULT:global:{type}:{id}:{model_v}` | 1 Hour | Model promotion / redeploy | Invalidated on version bump |

---

## 3. Negative Caching

When a query finds **no intelligence** (e.g. unknown phone number or new UPI ID), the absence of threat data is cached for **30 seconds maximum**. This prevents rapid-fire queries from overloading the database while ensuring new victim reports immediately update threat status.

---

## 4. Stampede Protection (Single-Flight Pattern)

To protect the system when hundreds of concurrent requests query the same high-velocity campaign or entity:
1. First caller acquires a local/distributed single-flight lock (`flight_lock`).
2. Concurrent callers await the in-flight computation.
3. Computed result is written to cache and shared with all pending callers.

---

## 5. Distributed Locks

Distributed locks coordinate singleton processes (e.g., campaign outbreak evaluation, graph rebuild, scheduled retention):
- Every lock has an **explicit owner** (`owner_id = job_id`).
- Every lock has an **explicit TTL** (default 15–30s) to prevent permanent deadlocks if a worker crashes.
- Unreleased locks expire automatically.
