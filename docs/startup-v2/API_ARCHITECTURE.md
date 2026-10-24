# API Architecture & Integration Gateway (Enterprise V2)

## 1. System Integration Overview

The ScamGraph API Architecture strictly separates customer ingress from proprietary intelligence engines. The Gateway handles:
- Authorization and credential hashing validation (`sg_live_...` / `sg_test_...`)
- Idempotency deduplication using SHA-256 payload hashes and Redis/in-memory records
- SSRF hardening blocking RFC1918, localhost, loopback, and cloud metadata targets (`169.254.169.254`)
- Privacy-safe Customer DTO mapping (stripping raw embeddings and victim identities)

```
Partner Application
       │
       ▼ (HTTPS POST /api/v1/guard/check)
Enterprise Gateway Middleware
 ├── API Key SHA-256 Hash Auth
 ├── SSRF & Payload Sanitization
 ├── Idempotency Key Validation
 └── Tenant Isolation Context
       │
       ▼
Canonical Intelligence Execution
 ├── Entity Intelligence (Reputation & Directory Match)
 ├── Multilingual Normalization (Hindi/Hinglish/English)
 ├── Journey Stage & Escalation Velocity
 ├── ScamDNA Behavioral Match
 ├── Graph & Network Signals
 └── Unified Decision Engine (Fusion Score & Interventions)
       │
       ▼
Customer-Safe Response DTO (No PII / No Raw Weights)
```

## 2. API Product Directory

| API Route | Product Surface | Latency Tier | Canonical Engine Target |
|:---|:---|:---|:---|
| `POST /api/v1/check` | Scam Check API | Standard (150-350ms) | Language + Entity + Journey + ScamDNA + Unified Decision |
| `POST /api/v1/guard/check` | Pre-Payment Guard API | Fast-Path (<25ms) | Entity Reputation + Behavioral Heuristics + Canonical Interventions |
| `POST /api/v1/entities/check` | Entity Intelligence API | Fast-Path (<20ms) | Entity Intelligence Directory & Corroborated Reputation |
| `GET /api/v1/outbreak/feed` | Outbreak Radar Feed | Read Cache (<15ms) | Campaign Outbreak Intelligence & Syndicated Alerts |
| `POST /api/v1/jobs` | Async Analysis Jobs | Async (<50ms ack) | Multimodal Processing (OCR / Audio / Document Transcription) |
| `POST /api/v1/webhooks` | Webhook Subscription | Standard (<50ms) | HMAC-SHA256 Signed Event Dispatcher |
