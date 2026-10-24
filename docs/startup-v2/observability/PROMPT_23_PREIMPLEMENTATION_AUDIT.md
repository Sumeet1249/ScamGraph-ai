# PROMPT 23 PRE-IMPLEMENTATION AUDIT
**ScamGraph AI — Phase 7C Observability, AI Quality & Drift Audit**
*Document Version: 3.0.0 | Date: 2026-10-24*

---

## 1. Executive Summary

This audit assesses the observability, AI quality monitoring, model governance, and scam drift detection capabilities across ScamGraph AI.

Observability is divided into three non-negotiable pillars:
1. **Application Observability**: Is the software stack running correctly (latency, errors, queue depth, cache hit rate, database health, worker status)?
2. **AI Quality Monitoring**: Are model outputs accurate, calibrated, grounded in evidence, explainable, and safe against regressions (FPR, FNR, golden set, negation, multimodal)?
3. **Scam Drift Intelligence**: Is the threat ecosystem mutating (new tactics, altered journey stages, changing UPI/QR patterns, multilingual code-mixing, campaign surges)?

---

## 2. File Decision Classification

| File / Component | Role | Classification | Planned Phase 7C Action |
| :--- | :--- | :--- | :--- |
| `packages/schemas/evaluation.py` | Evaluation metrics schemas | `IMPROVE` | Extend with Golden Regression & Drift metadata |
| `packages/schemas/dataset.py` | Dataset partition schemas | `KEEP` | Preserves leakage-free partition models |
| `services/security/service.py` | Audit & redaction logic | `IMPROVE` | Add centralized telemetry sanitization filter |
| `services/jobs/queue.py` | Job queue & lifecycle | `KEEP` | Exposes queue depth, age, and dead-letter count |
| `services/jobs/cache.py` | Cache & freshness lag | `KEEP` | Exposes graph & radar freshness metrics |
| `services/jobs/workers.py` | Background workers | `IMPROVE` | Integrate trace context & provider monitoring |
| `services/investigation/tinyfish/client.py` | TinyFish provider | `IMPROVE` | Add structured latency & error tracking |
| `services/observability/telemetry.py` | Central Telemetry & Redaction | `ADD` | Privacy-safe structured logging & metrics |
| `services/observability/tracing.py` | Trace propagation engine | `ADD` | Context continuation across HTTP and queues |
| `services/observability/ai_quality.py` | AI Evaluation & Regression | `ADD` | Golden regression, negation, and calibration |
| `services/observability/drift_detector.py`| Scam & Model Drift Engine| `ADD` | Detects data, model, scam, journey & campaign drift |
| `services/observability/health.py` | Liveness, readiness, deep | `ADD` | Standard health endpoints & SLI/SLO tracking |

---

## 3. Privacy-Safe Telemetry Audit

Normal telemetry (logs, metrics, traces) MUST NEVER record:
- Plaintext OTPs (e.g., 6-digit verification codes)
- Payment PINs, CVV codes, or full 16-digit debit/credit card numbers
- Bank account numbers in plaintext
- Raw private audio transcripts or personal conversation dumps
- Full unmasked phone numbers
- Authorization tokens, API keys, or webhook secrets

Centralized regex-based and key-based sanitizers (`TelemetrySanitizer`) strip or mask all sensitive tokens prior to serialization.
