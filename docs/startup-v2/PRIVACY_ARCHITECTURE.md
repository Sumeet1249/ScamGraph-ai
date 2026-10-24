# Privacy Architecture & Cross-Victim Protection (Prompt 21 / Phase 7A)

## 1. Cross-Victim Privacy Principles
ScamGraph leverages cross-victim correlation to power the network effect without ever compromising victim privacy:
- **Zero Attribution Leakage**: An enterprise partner querying a suspicious VPA receives `"Observed in multiple independent reports (6-20)"`. They NEVER learn which bank, fintech, or individual submitted the original report.
- **Small Cohort Protection**: Incident counts below threshold (<3 reports) are bucketed to prevent targeted deanonymization attacks.
- **Anti-Enumeration Guard**: Thresholded results, query velocity limits, and zero victim narrative disclosure prevent automated scraping of banking directories.

---

## 2. Consent Architecture
Consent is granular and auditable through `ConsentRecord`:
- `SCAM_ANALYSIS`: Allows heuristic and multi-signal inspection of active request content.
- `EVIDENCE_STORAGE`: Permits persistent storage of evidence for investigation.
- `NETWORK_INTELLIGENCE_CONTRIBUTION`: Permits privacy-safe derived signals to enter the Knowledge Graph.
- `MODEL_TRAINING`: Explicit opt-in. **Consent to analyze does NOT permit model training.**
- `AUDIO_PROCESSING`: Allows automatic speech-to-text transcription.
- `CASE_EXPORT`: Allows inclusion in law enforcement packages.
