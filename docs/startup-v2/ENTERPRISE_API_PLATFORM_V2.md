# Enterprise API & SDK Platform V2 (Prompt 20 / Phase 6B)

## Executive Summary

The **ScamGraph Enterprise API & SDK Platform V2** productizes ScamGraph AI into a carrier-grade, low-latency, privacy-safe intelligence gateway for banks, fintech applications, UPI/payment platforms, e-commerce marketplaces, telecom providers, and cyber fraud investigation units.

### Core Architecture Philosophy
> **"THE API IS A PRODUCT SURFACE. IT IS NOT ANOTHER INTELLIGENCE ENGINE."**

The Enterprise API Gateway is strictly an orchestration and serialization facade. It performs authentication, rate limiting, idempotency tracking, SSRF filtering, and customer-safe serialization while delegating 100% of risk scoring, graph traversal, entity reputation, campaign clustering, and intervention generation to the **canonical intelligence engines** established across Prompts 1–19.

---

## 1. Enterprise Product Surfaces

```
                    PARTNER APPLICATION
                           │
                           ▼
                  SCAMGRAPH API PLATFORM
             (/api/v1/check, /api/v1/guard/check)
                           │
               ┌───────────┼───────────┐
               │           │           │
             CHECK       GUARD      INTELLIGENCE
               │           │           │
               └───────────┼───────────┘
                           ▼
                  CANONICAL SERVICES
                           │
       ┌───────────────────┼────────────────────┐
       │                   │                    │
     ENTITY             JOURNEY              SCAMDNA
       │                   │                    │
       └───────────────────┼────────────────────┘
                           ▼
                  KNOWLEDGE GRAPH
                           │
                     CORRELATION
                           │
                      CAMPAIGNS
                           │
                  OUTBREAK INTELLIGENCE
                           │
                  UNIFIED ASSESSMENT
                           │
                     INTERVENTION
                           │
                           ▼
                  CUSTOMER-SAFE DTOs
```

### Products Exposed:
1. **ScamGraph Check API (`POST /api/v1/check`)**: General-purpose multimodal scam assessment for messages, links, phones, and VPAs.
2. **Pre-Payment Guard API (`POST /api/v1/guard/check`)**: Sub-25ms fast-path intercept for UPI apps and net banking prior to fund authorization.
3. **Entity Intelligence API (`POST /api/v1/entities/check`)**: Privacy-safe directory and network reputation check without exposing victim PII or incident narratives.
4. **Outbreak Intelligence Feed (`GET /api/v1/outbreak/feed`)**: Real-time early warning feed for surging syndicates and rapid cross-victim campaigns.
5. **Async Analysis Engine (`POST /api/v1/jobs`, `GET /api/v1/jobs/{job_id}`)**: Non-blocking asynchronous processing for heavy media artifacts (audio/documents/images).
6. **Signed Enterprise Webhooks (`POST /api/v1/webhooks`)**: HMAC-SHA256 event streams with replay protection for real-time risk alerts and campaign outbreaks.
7. **Developer SDKs**: Official TypeScript and Python SDKs with built-in retries, timeouts, idempotency handling, and webhook verification helpers.
