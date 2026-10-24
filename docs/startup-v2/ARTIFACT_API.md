# Artifact API & Asynchronous Analysis Workflows

## 1. Multimodal Artifact Ingestion
Heavy evidence artifacts (screenshots, audio recordings, PDFs) do not block synchronous check endpoints:
1. `POST /api/v1/jobs` with `artifact_id`
2. Immediate HTTP 202 Accepted response with `job_id`
3. Background execution: OCR / Speech-to-Text / Entity Extraction / Journey Mapping / ScamDNA
4. Partner polls `GET /api/v1/jobs/{job_id}` or receives `analysis.completed` webhook.

## 2. Analysis Job State Machine
- `PENDING` $\to$ `PROCESSING` $\to$ `COMPLETED` / `FAILED`
- Progress stages: `OCR_PROCESSING`, `TRANSCRIPTION`, `JOURNEY_SYNTHESIS`, `DECISION_FUSED`
- Multi-tenant boundary: Organization A can NEVER query Organization B's job ID.
