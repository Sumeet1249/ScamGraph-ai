# ASYNC INFRASTRUCTURE & WORKLOAD AUDIT V2
**ScamGraph AI — Phase 7B Pre-Implementation Audit**
*Document Version: 2.0.0 | Date: 2026-10-24*

---

## 1. Executive Summary

This pre-implementation audit examines the existing ScamGraph codebase across Python services, FastAPI endpoints, Next.js frontend, database schemas, and background tasks. The mandate is to **move expensive, retryable, scheduled, and non-interactive work out of user request paths while preserving tenant isolation, correctness, security, and traceability**, without introducing premature distributed-system complexity.

PostgreSQL remains the canonical, durable **Source of Truth**. Redis is introduced as a fast, volatile coordination layer (job queue, caching, rate limiting, distributed locks, and deduplication). In-memory fallbacks ensure that local testing, offline development, and degraded modes operate seamlessly without requiring a live external Redis daemon.

---

## 2. Infrastructure Inventory

| Component | Current Stack | Phase 7B Target | Notes / Role |
| :--- | :--- | :--- | :--- |
| **Primary Database** | PostgreSQL 16 (pgvector) | PostgreSQL 16 (pgvector) | Durable source of truth for all incidents, jobs, organizations, and entities |
| **Graph Database** | Neo4j 5.20 Community | Neo4j 5.20 Community | Asynchronous projection target for investigation topology and path queries |
| **Coordination / Cache** | In-memory dicts | Redis 7.2 + In-Memory Fallback | Volatile cache, distributed rate limiting, queue transport, distributed locks |
| **Queue Technology** | None (sync routes) | Unified `JobQueue` (Redis/Memory) | Priority-driven, bounded retries, dead-letter storage, tenant-context preserving |
| **Worker Concurrency**| Single-process async | Async Worker Pool with classes | Separate pools: `interactive`, `media`, `intelligence`, `webhooks`, `exports`, `maintenance` |
| **Web Framework** | FastAPI (Python 3.14) | FastAPI (Python 3.14) | Fast synchronous edge gateway with async 202 Job Creation |
| **Frontend** | Next.js 14 (App Router) | Next.js 14 (App Router) | Standardized status polling contract (`idle`, `processing`, `partial`, `complete`, `failed`) |

---

## 3. Workload Classification Matrix

Every system workload is audited and classified into:
- **`SYNC_REQUIRED`**: Must complete within HTTP request (< 500ms).
- **`ASYNC_REQUIRED`**: Must be offloaded to queue/workers to protect user experience.
- **`ASYNC_OPTIONAL`**: Can execute asynchronously or deferred.
- **`SCHEDULED`**: Cron / periodic background maintenance.
- **`EVENT_DRIVEN`**: Triggered by state transitions via Domain Events / Outbox.
- **`LEGACY`**: To be refactored or retired in Phase 7B.

| Workload | Classification | Latency SLA | CPU / Mem | Tenant Scope | Failure Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HTTP Auth & RBAC Check** | `SYNC_REQUIRED` | < 15ms | Low / Low | Strict Tenant | 401/403 Immediate |
| **Input Validation & Sanitize**| `SYNC_REQUIRED` | < 10ms | Low / Low | Context Free | 422 Immediate |
| **Pre-payment Guard Fast Path**| `SYNC_REQUIRED` | < 250ms | Med / Med | Global + Private | Synchronous fallback assessment |
| **Cached Entity / Campaign Lookup**| `SYNC_REQUIRED` | < 20ms | Low / Low | Tenant Isolated | Cache miss -> DB lookup |
| **OCR Text Extraction** | `ASYNC_REQUIRED` | 2 - 15s | High / High | Artifact Bound | Retry with exponential backoff |
| **Speech-to-Text (STT) Audio** | `ASYNC_REQUIRED` | 5 - 45s | High / High (GPU) | Artifact Bound | Retry transient; fail preserved |
| **Multimodal Evidence Fusion** | `ASYNC_REQUIRED` | 1 - 5s | Med / Med | Incident Bound | Partial assessment on branch failure |
| **Postgres -> Neo4j Projection**| `ASYNC_REQUIRED` | 200 - 1500ms | Med / Low | Global Intelligence| Outbox retry; mark graph lag |
| **Cross-Incident Correlation** | `ASYNC_REQUIRED` | 1 - 8s | Med / Med | Bounded Candidates | Deduplicate triggers; candidate queue |
| **Campaign Recomputation & Velocity**| `ASYNC_REQUIRED` | 2 - 10s | Med / Med | Global Intelligence| Distributed lock single-flight |
| **Outbreak Radar Snapshot Rebuild**| `ASYNC_REQUIRED` | 500 - 3000ms | Med / Low | Global Intelligence| Invalidate cache; mark freshness |
| **Partner Webhook Delivery** | `ASYNC_REQUIRED` | 100 - 2000ms | Low / Low | Partner Org Bound | Bounded backoff -> Dead Letter |
| **Evidence Archive Export** | `ASYNC_REQUIRED` | 3 - 30s | Med / High | Strict Org Bound | Signed URL expiration (24h) |
| **Data Retention & Anonymization**| `SCHEDULED` | 10 - 120s | Med / Med | Strict Tenant | Audit logged; dry-run supported |
| **Outbreak Periodic Reconciliation**| `SCHEDULED` | 5 - 15s | Med / Med | Global Intelligence| Runs every 10 min |
| **Expired Export File Pruning** | `SCHEDULED` | 1 - 5s | Low / Low | System | Runs hourly |
| **Cache Maintenance / Eviction**| `SCHEDULED` | 500ms | Low / Low | System | Automatic via Redis TTL + cleaner |
| **Incident Created Event** | `EVENT_DRIVEN` | Immediate | Low / Low | Incident Bound | Enqueues correlation & projection |
| **Campaign Status Outbreak** | `EVENT_DRIVEN` | Immediate | Low / Low | Campaign Bound | Enqueues partner webhooks |
| **Evidence Deleted Event** | `EVENT_DRIVEN` | Immediate | Med / Med | Incident Bound | Enqueues cascade recomputation |
| **Synchronous In-Route Webhook** | `LEGACY` | Deprecate | - | - | Replaced by durable `WebhookWorker` |
| **Direct Route Blocking OCR** | `LEGACY` | Deprecate | - | - | Replaced by `OCRWorker` + 202 Accepted |

---

## 4. Latency & Resource Inventory

| Pipeline | Typical Runtime | CPU Bound | Memory Bound | External Dep | Retryable? | Idempotency Key |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OCR Pipeline** | 3.5s | Yes | Yes (Images) | Local/Vision API | Yes | `hash(artifact_id, ocr_engine_v)` |
| **STT Pipeline** | 12.0s | Yes | Yes (Audio buffer) | Local/Whisper | Yes | `hash(artifact_id, stt_engine_v)` |
| **Fusion Pipeline**| 1.8s | No | Moderate | None | Yes | `hash(incident_id, derived_obs_v)` |
| **Correlation** | 2.2s | Moderate | Moderate | Postgres/Vector | Yes | `hash(incident_id, candidate_batch)` |
| **Graph Projection**| 450ms | Low | Low | Neo4j Bolt | Yes | `hash(entity_id, version)` |
| **Campaign Update**| 3.1s | Moderate | Moderate | Postgres | Yes | `hash(campaign_id, trigger_event)` |
| **Webhook Delivery**| 650ms | Low | Low | Partner HTTP | Yes (bounded) | `hash(delivery_id, attempt)` |
| **Export Generator**| 6.5s | Moderate | Moderate | Zip/Crypto | Yes | `hash(export_request_id)` |
| **Retention Job** | 15.0s | Low | Moderate | Postgres | Yes | `hash(tenant_id, run_date)` |

---

## 5. Security & Payload Architecture

1. **No Secrets in Queue**:
   Queue messages NEVER contain passwords, API keys, webhook signing secrets, session tokens, or raw credentials.
2. **References Over Payloads**:
   Queue messages store minimal reference identifiers (`job_id`, `artifact_id`, `incident_id`, `org_id`). Workers fetch authorized state through canonical service boundaries.
3. **Tenant Boundary Preservation**:
   Every background job carries `org_id` and `principal_id`. Worker execution evaluates tenant privacy and contribution policies before writing or querying data.
4. **Worker Permission Scoping**:
   Workers do not possess global unrestricted admin privileges. They run within scoped service roles (`WorkerContext`) bounded by the triggering tenant's visibility rules.
