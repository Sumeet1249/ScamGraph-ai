# Enterprise Error Model Specification

## HTTP Status Codes & Error Mapping

| HTTP Code | Error Code | Retryable | Description |
|:---|:---|:---|:---|
| 400 | `INVALID_REQUEST` | No | Validation error or malformed JSON |
| 401 | `UNAUTHORIZED` | No | API key missing, invalid, or expired |
| 403 | `FORBIDDEN` | No | Insufficient scope or cross-tenant resource access |
| 404 | `RESOURCE_NOT_FOUND` | No | Requested job, webhook, or entity does not exist |
| 409 | `CONFLICT` | No | Idempotency payload mismatch |
| 413 | `PAYLOAD_TOO_LARGE` | No | Media artifact exceeds size limit (e.g. >25MB) |
| 422 | `UNPROCESSABLE_ENTITY`| No | Schema validation failure |
| 429 | `RATE_LIMITED` | Yes | Organization or key rate limit exceeded |
| 500 | `PROCESSING_FAILED` | Yes | Internal engine error |
| 503 | `SERVICE_DEGRADED` | Yes | Neo4j or downstream ML provider unavailable |

Stack traces, internal server IPs, and database connection strings are strictly suppressed from all error responses.
