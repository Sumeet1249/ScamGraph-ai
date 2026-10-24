# ASYNC ARCHITECTURE V2
**ScamGraph AI — Production Asynchronous Infrastructure**
*Document Version: 2.0.0 | Date: 2026-10-24*

---

## 1. Architectural Mandate

ScamGraph AI protects victims, enterprises, and payment systems against fast-moving scams in India. The core operational rule is:
> **Move expensive, retryable, scheduled, and non-interactive work out of user request paths while preserving security, tenant isolation, correctness, and traceability.**

Redis, caches, and queues **NEVER** become the source of truth. PostgreSQL remains the durable source of truth.

---

## 2. High-Level Topology

```
USER / ENTERPRISE REQUEST
        │
        ▼
   API / WEB APP (FastAPI)
        │
        ├──────── FAST SYNCHRONOUS PATH (< 250ms)
        │         ├── Schema validation
        │         ├── RBAC & API key authentication
        │         ├── Tenant isolation check
        │         ├── Fast tactic classification
        │         ├── Cached threat lookup
        │         └── Pre-Payment Guard fast assessment
        │
        ▼
   JOB CREATION (202 Accepted + Durable Job Record in PostgreSQL)
        │
        ▼
    JOB QUEUE (Redis / In-Memory Fallback)
        │
        ├── [media]        OCR Worker (Text, UPI, URLs from screenshots)
        ├── [media]        STT Worker (Whisper audio transcription, journey extraction)
        ├── [intelligence] Multimodal Worker (Fan-out / fan-in fusion)
        ├── [intelligence] Graph Worker (Postgres -> Neo4j asynchronous projection)
        ├── [intelligence] Correlation Worker (Bounded candidate cross-incident linking)
        ├── [intelligence] Campaign Worker (Velocity recomputation & Outbreak Radar)
        ├── [webhooks]     Webhook Worker (HMAC-signed outbound delivery with jitter)
        ├── [exports]      Export Worker (Encrypted evidence archive generation)
        └── [maintenance]  Retention Worker (Dry-run reporting & cascade invalidation)
        │
        ▼
 CANONICAL SERVICE LAYER (Tenant Context & Scoped Permissions)
        │
        ▼
 SOURCE-OF-TRUTH DATABASE (PostgreSQL 16 with pgvector)
```

---

## 3. Worker Segregation & Concurrency

| Worker Class | Queue Name | Workloads Handled | Target Concurrency | Failure Policy |
| :--- | :--- | :--- | :--- | :--- |
| **`interactive`** | `sg:q:interactive` | Pre-Payment Guard continuation | 16 workers | Retry 3x, exponential backoff |
| **`media`** | `sg:q:media` | OCR extraction, STT transcription | 4-8 workers (CPU/GPU bound) | Retry 3x, poison job dead-letter |
| **`intelligence`**| `sg:q:intelligence`| Fusion, correlation, campaign, graph | 8 workers | Bounded candidate pool, retry 3x |
| **`webhooks`** | `sg:q:webhooks` | Partner notification delivery | 16 workers (I/O bound) | Bounded backoff (up to 5x) -> DLQ |
| **`exports`** | `sg:q:exports` | Case-package archive compression | 2 workers | Retry 2x, 24h link expiration |
| **`maintenance`**| `sg:q:maintenance`| Retention dry-run/exec, pruning | 1 worker (Singleton lock) | Fail-safe, audit logged |

---

## 4. Security Principles

1. **Worker != Admin**: Background workers execute with a restricted `WorkerContext`. They cannot bypass tenant privacy policies or data contribution agreements.
2. **No Secrets in Payloads**: Queue messages contain resource IDs (`artifact_id`, `incident_id`, `job_id`), never raw passwords, webhook secrets, or plaintext evidence.
3. **Tenant-Safe Cache**: Private cache keys strictly encode tenant scope (`sg:production:TENANT_PRIVATE:tenant_id:...`). Cross-tenant cache reading is impossible.
