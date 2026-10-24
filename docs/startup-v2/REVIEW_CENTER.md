# Human-in-the-Loop Review Center Specification

## 1. Adjudication Queue Architecture
The `/reviews` workspace hosts candidate automated proposals requiring expert human judgment before impacting global threat intelligence:
- **Queue Types**: `CAMPAIGN_MERGE`, `CAMPAIGN_SPLIT`, `ENTITY_SPLIT` (supernode separation), `CORRELATION` validation, and `NOVEL_VARIANT` confirmation.
- **Priority Scoring**: Items are ranked by an operational impact score (0.0–1.0) derived from campaign velocity, affected victim count, and financial exposure.
- **Adjudication Outcomes**:
  - `CONFIRM`: Approves the proposed relationship and merges/links the entities.
  - `REJECT`: Dismisses candidate connection (e.g. rejects merging onto a legitimate bank toll-free number).
  - `UNCERTAIN`: Flags item for further investigation or external verification.
- **Auditable Lineage**: Stores reviewer ID, timestamp, decision, and rationale notes without modifying raw underlying victim reports.
