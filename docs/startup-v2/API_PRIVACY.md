# API Privacy & Security Architecture

## 1. Zero-Leakage Privacy Contract
- **No Victim Attribution**: Customer A's report of a malicious phone or VPA will NEVER result in Customer B seeing Customer A's name, timestamp, or narrative.
- **Small Cohort Protection**: Incident counts below threshold are bucketed (`1-5`, `6-20`, `20+`).
- **Entity Masking**: Sensitive identifiers are masked (e.g. `******3210`, `n***@oksbi`).

## 2. API Security Controls
- **SSRF Defense**: Strict validation on customer URLs. Blocks `localhost`, `127.0.0.1`, RFC1918 private ranges, and Cloud Instance Metadata (`169.254.169.254`).
- **SQL & Cypher Injection Prevention**: Parameterized queries across Neo4j and Postgres; all text inputs are sanitized.
- **Prompt Injection Defense**: Untrusted text/media inputs are enclosed in isolated data blocks and prevented from modifying system instructions.
- **Replay Protection**: Webhook signatures include timestamps with a strict 300-second window.
