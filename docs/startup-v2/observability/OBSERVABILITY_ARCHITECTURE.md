# PRODUCTION OBSERVABILITY & AI QUALITY ARCHITECTURE V3
**ScamGraph AI — Comprehensive System & Intelligence Monitoring**
*Document Version: 3.0.0 | Date: 2026-10-24*

---

## 1. Architectural Distinction: The Three Pillars

ScamGraph AI strictly isolates three operational monitoring layers:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. APPLICATION OBSERVABILITY                                │
│    Is the software running? (Latency, errors, queues, DB)   │
├─────────────────────────────────────────────────────────────┤
│ 2. AI QUALITY MONITORING                                    │
│    Is intelligence accurate, grounded, calibrated & safe?   │
├─────────────────────────────────────────────────────────────┤
│ 3. SCAM DRIFT INTELLIGENCE                                  │
│    How is the threat ecosystem mutating in India?           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. End-to-End Trace Flow

```
USER REQUEST (Protect / Guard / API)
     │ [x-trace-id, x-request-id]
     ▼
FASTAPI GATEWAY (Latency Percentiles, Error Taxonomy)
     │
     ├──────── SYNCHRONOUS PATH: Cache Hit / Fast Assessment (< 250ms)
     │
     ▼
QUEUE ENQUEUE (trace_id preserved in QueueMessage)
     │
     ▼
WORKER EXECUTION (WorkerContext with Scoped Tenant Permissions)
     ├── OCR Worker (Idempotent artifact observation)
     ├── STT Worker (Audio transcription & tactics)
     ├── Correlation Worker (Bounded candidate pairs)
     └── Campaign Worker (Velocity & Outbreak Radar)
     │
     ▼
DOWNSTREAM UPDATES (Postgres Source-of-Truth -> Neo4j Projection)
     │
     ▼
RADAR CACHE & WEBHOOK NOTIFICATION (HMAC-Signed Partner Delivery)
```

---

## 3. Telemetry Privacy Mandate

- Telemetry **NEVER** contains raw passwords, verification OTPs, payment PINs, CVVs, full card numbers, unmasked phone numbers, or private audio dumps.
- All log streams pass through `TelemetrySanitizer` before serialization.
- Operational dashboards only display resource identifiers (`job_id`, `incident_id`, `org_id`).
