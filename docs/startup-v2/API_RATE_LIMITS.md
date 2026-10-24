# API Rate Limits & Quota Contracts

## 1. Rate Limit Tiers

| Tier | Guard API (Fast-Path) | Check API (Standard) | Entity / Network API | Burst Allowance |
|:---|:---|:---|:---|:---|
| **Sandbox / Test** | 50 req/sec | 10 req/sec | 20 req/sec | 1.5x |
| **Standard Enterprise** | 500 req/sec | 100 req/sec | 200 req/sec | 2.0x |
| **Tier-1 Bank / UPI Core**| 5,000 req/sec | 500 req/sec | 1,000 req/sec | 3.0x |

## 2. Rate Limit Headers
When rate limits are approached or exceeded, responses include:
- `X-RateLimit-Limit`: Maximum requests permitted per window
- `X-RateLimit-Remaining`: Remaining request balance
- `X-RateLimit-Reset`: UNIX epoch timestamp when quota resets
- `Retry-After`: Recommended backoff seconds on HTTP 429.
