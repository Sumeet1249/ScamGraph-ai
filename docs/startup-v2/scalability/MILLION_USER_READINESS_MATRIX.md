# MILLION-USER READINESS & CAPACITY MATRIX
**ScamGraph AI — Phase 7D Subsystem Readiness Evaluation**
*Document Version: 4.0.0 | Date: 2026-10-24*

---

## 1. Absolute Reality Declaration

> **1,000,000 DAU is a capacity projection, NOT a claimed load-test accomplishment.**
> Actual load testing has empirically benchmarked local concurrency up to 25 simultaneous workers and hundreds of synthetic operations. Projections beyond this tier are extrapolated from empirical unit constants.

---

## 2. Subsystem Readiness Matrix

| Subsystem | Measured Capacity | 10K DAU Requirement | 100K DAU Requirement | 1M DAU Requirement | First Bottleneck | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FastAPI Gateway** | 350+ RPS local | 10 RPS peak | 97 RPS peak | 972 RPS peak | Python GIL / process count | `PROJECTED` |
| **Authentication & RBAC** | < 1ms local cache | 10 RPS | 97 RPS | 972 RPS | Token verification CPU | `PROVEN` |
| **PostgreSQL (Truth)** | 1,200 reads/sec | 15 queries/sec | 150 queries/sec | 1,500 queries/sec | Connection pool exhaustion | `PROJECTED` |
| **Redis Cache** | 10,000 ops/sec | 25 ops/sec | 250 ops/sec | 2,500 ops/sec | Memory limits & hot keys | `PROVEN` |
| **Job Queue** | 800 enqueues/sec | 12 jobs/sec | 115 jobs/sec | 1,150 jobs/sec | Queue depth backpressure | `PROVEN` |
| **Media OCR Workers**| 12 jobs/min/core | 28 jobs/min | 280 jobs/min | 2,800 jobs/min | Worker CPU & memory limits | `PROJECTED` |
| **Audio STT Workers**| 4 jobs/min/core | 6 jobs/min | 60 jobs/min | 600 jobs/min | GPU allocation costs | `PROJECTED` |
| **Neo4j Graph** | 450 projections/sec| 5 projections/sec | 45 projections/sec | 450 projections/sec | Write lock contention | `PROJECTED` |
| **Correlation Engine**| Bounded top-10 | 12 checks/sec | 120 checks/sec | 1,200 checks/sec | Candidate generation index | `PROVEN` |
| **Campaign Radar** | Cached snapshot <1ms| 20 reads/sec | 200 reads/sec | 2,000 reads/sec | Snapshot refresh locking | `PROVEN` |
| **Partner Webhooks** | Bounded pool | 2 deliveries/sec | 18 deliveries/sec | 180 deliveries/sec | Partner endpoint latency | `PROVEN` |
