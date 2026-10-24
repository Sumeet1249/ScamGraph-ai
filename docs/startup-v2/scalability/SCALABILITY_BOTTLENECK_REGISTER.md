# SCALABILITY BOTTLENECK REGISTER
**ScamGraph AI — Phase 7D Empirical Bottlenecks & Fixes**
*Document Version: 4.0.0 | Date: 2026-10-24*

---

| ID | Component | Symptom | Root Cause | Severity | Applied Fix | Before | After | Remaining Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BTN-01** | **Correlation** | Slowdown on large incident batch | Unbounded all-pairs Cartesian product | High | Bounded top-10 candidate retrieval | O(N^2) | O(K) where K=10 | Extreme incident bursts |
| **BTN-02** | **Cache** | Database spike on hot key expiration | Multiple concurrent workers recomputing | Medium | Single-flight stampede lock | 10 DB calls | 1 DB call | Distributed node restarts |
| **BTN-03** | **Campaign** | State race condition on simultaneous update | Concurrent workers updating velocity | High | Distributed lock (`acquire_lock`) | State corruption | Deterministic skip | Lock timeout edge case |
| **BTN-04** | **Provider** | Retry storm when upstream provider 503s | Immediate unjittered retries | High | Exponential backoff + jitter + dead letter | 50 retries/sec | Bounded 3 retries | Extended partner outages |
| **BTN-05** | **Pagination** | High latency on 1,000+ incident list | Offset pagination (`OFFSET 1000`) | Medium | Keyset/cursor pagination | O(N) scan | O(1) indexed cursor | Complex multi-filter sorts |
