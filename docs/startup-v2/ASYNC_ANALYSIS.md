# Asynchronous Analysis Jobs Specification

## 1. Endpoints
- `POST /api/v1/jobs`: Enqueue heavy multimodal or batch analysis.
- `GET /api/v1/jobs/{job_id}`: Poll status and inspect results.

## 2. Multi-Tenant Job Isolation
Every job record stores `org_id`. Job retrieval requires the authenticated caller's `org_id` to match. Mismatches return HTTP 404 (Resource Not Found) to prevent enumeration of other tenants' job IDs.
