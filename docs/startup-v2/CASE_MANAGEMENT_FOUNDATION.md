# Case Management Foundation Specification

## 1. Lightweight Investigation Case Entity
The `/cases` workspace allows authorized fraud investigators and bank liaison teams to curate operational cases:
- **Case Representation**: `InvestigationCase` with unique `case_id`, title, priority (`CRITICAL`, `HIGH`, `MEDIUM`), assignment, and lifecycle status (`OPEN`, `INVESTIGATING`, `WAITING`, `RESOLVED`, `ARCHIVED`).
- **Linked Objects**: Binds related `incident_ids`, `campaign_ids`, and `target_entities` into a single operational unit.
- **Append-Only Analyst Notes**: Timestamped chronological log recording subpoenas, banking freeze confirmations, cyber cell liaison communications, and evidence packages.
