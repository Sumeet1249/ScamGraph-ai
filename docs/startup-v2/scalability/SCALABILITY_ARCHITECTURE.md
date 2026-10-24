# SCALABILITY & CAPACITY ARCHITECTURE V3
**ScamGraph AI — Production Load, Backpressure & Scaling Specification**
*Document Version: 4.0.0 | Date: 2026-10-24*

---

## 1. Architectural Philosophy

ScamGraph AI handles fast-moving, high-stakes threat intelligence across India. The central scaling tenet is:
> **Protect, Pre-Payment Guard, and Rescue user-critical safety paths must remain operational under peak traffic spikes, even when deep external scraping, heavy multimodal VLM analysis, or campaign recomputations are degraded or shed.**

Every scalability statement is verified under one of four explicit labels:
- **`MEASURED`**: Empirically measured via reproducible load harnesses.
- **`PROJECTED_FROM_MEASURED_DATA`**: Derived mathematically from verified baseline units.
- **`ARCHITECTURALLY_POSSIBLE`**: Supported by the design topology but not yet benchmarked at multi-cluster scale.
- **`UNVALIDATED`**: Untested assumption requiring future validation.

---

## 2. Load Shedding & Degradation Modes

```
               [TRAFFIC SURGE]
                      │
                      ▼
        [Backpressure Controller]
        (Monitors Queue Depth & Oldest Age)
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
      NORMAL     DEGRADED     CRITICAL SAFETY
                 INTELLIGENCE    ONLY (P0/P1)
```

1. **`NORMAL`**: All interactive checks, media OCR/STT, cross-incident correlations, and campaign clustering run nominally.
2. **`DEGRADED_ENRICHMENT`**: When queue depth $\ge 50$, non-user-facing low-priority batch jobs are delayed.
3. **`DEGRADED_INTELLIGENCE`**: When queue depth $\ge 150$, cross-incident correlation and campaign recomputation are deferred; Protect, Guard, and Rescue remain immediate.
4. **`CRITICAL_SAFETY_ONLY`**: When queue depth $\ge 300$ or oldest job age $> 10$ minutes, only **P0 (Guard critical intervention)** and **P1 (Rescue triage)** are admitted. Low-priority jobs are rejected with 429/503 and explicit `Retry-After`.

---

## 3. Circuit Breaker Architecture

Third-party APIs (LLMs, Whisper, OCR, TinyFish) are wrapped in `CircuitBreaker` instances:
- **`CLOSED`**: Calls pass through; failure counter resets on success.
- **`OPEN`**: Tripped when failure threshold (default 5 consecutive 5xx/timeouts) is reached. Outbound calls fail fast, preventing retry storms.
- **`HALF_OPEN`**: After recovery window (default 30s), limited trial probes test upstream availability.
