# services/pattern-engine — Scam Pattern & Evidence Fusion Engine

## Overview
Core intelligence engine responsible for:
- Semantic message signal extraction (urgency, impersonation, fear, social engineering cues).
- Temporal journey sequence tracking (detecting progression along the grooming ladder).
- Vector similarity search against known campaign clusters via pgvector.
- **Multi-Signal Fusion**: Aggregating signals across all 7 dimensions to compute calibrated Risk Score and Evidence Confidence.
- Enforcing the architectural rule: *No single model declares fraud*.
- Generating adaptive intervention recommendations to prevent alert fatigue.
