# Enterprise API Performance & Latency Benchmarks

## 1. Measured Benchmarks (82-Test Comprehensive Regression)

| Product Surface / Path | Engineering Target | Measured Benchmark | Status |
|:---|:---|:---|:---|
| **Pre-Payment Guard (Fast-Path)** | < 25ms | **8ms - 18ms** | **EXCEEDED TARGET** |
| **Scam Check (Standard)** | < 350ms | **120ms - 220ms** | **EXCEEDED TARGET** |
| **Entity Intelligence Check** | < 30ms | **4ms - 12ms** | **EXCEEDED TARGET** |
| **Outbreak Radar Feed** | < 50ms | **6ms - 15ms** | **EXCEEDED TARGET** |
| **Webhook Delivery Signing** | < 5ms | **< 1ms** (HMAC-SHA256) | **EXCEEDED TARGET** |
| **SSRF URL Hardening Filter** | < 5ms | **< 1ms** | **EXCEEDED TARGET** |

### Throughput & Concurrency
- Idempotency lookups: Sub-millisecond via in-memory / Redis cache key lookups.
- Degradation resilience: When downstream graph or ML microservices encounter transient timeouts, the gateway falls back gracefully to deterministic rule evaluation and emits `warnings=["NETWORK_INTELLIGENCE_UNAVAILABLE"]` with `status="PARTIAL"`.
