# Incident Workspace & Multimodal Timeline Specification

## 1. Single Incident Operational View
The `/incidents/[id]` workspace presents a comprehensive analysis of an individual scam report:
- **Unified Tripartite Assessment**: Risk Score (0–100), Evidence Confidence (LOW/MEDIUM/HIGH), and Urgency level.
- **Multimodal Timeline**: Merges text messages, call recordings, WhatsApp screenshots, QR codes, and transaction receipts into a unified chronological sequence.
- **Time Confidence Ratings**: Explicitly distinguishes between `EXACT` (bank timestamp / API payload), `APPROXIMATE` (victim statement), `INFERRED` (sequence heuristics), and `ORDER_ONLY`.
- **Intervention History**: Displays what warning or friction level was shown to the user (e.g. `PAUSE_BEFORE_PAYMENT`, `BREAK_CONTACT_AND_VERIFY`).
