# API Idempotency & Error Model

## 1. Idempotency Key Semantics
Clients pass `Idempotency-Key: <unique_string>` on mutation and analysis endpoints (`/check`, `/guard/check`, `/jobs`).
- **Cache Hit**: Identical key + identical payload returns the previously cached response immediately with `X-Cache-Lookup: HIT`.
- **Payload Conflict**: Identical key + different payload raises HTTP 409 Conflict with code `IDEMPOTENCY_CONFLICT`.
- **TTL**: Records are retained for 24 hours.

## 2. Standard Enterprise Error Model
```json
{
  "code": "INVALID_REQUEST",
  "message": "Missing required field 'vpa'",
  "request_id": "req_889911",
  "details": { "field": "vpa" },
  "retryable": false,
  "documentation_url": "https://docs.scamgraph.ai/errors#INVALID_REQUEST"
}
```

### Error Codes
- `UNAUTHORIZED` (401): Invalid or revoked API key
- `FORBIDDEN` (403): Missing required scope
- `CONFLICT` (409): Idempotency key fingerprint mismatch
- `RATE_LIMITED` (429): Quota exceeded
- `SERVICE_DEGRADED` (503): Downstream graph or model failure
