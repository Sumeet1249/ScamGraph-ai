# ScamGraph Intelligence Console V2 — Architectural Overview

## 1. Operating System for Scam Intelligence
The ScamGraph Intelligence Console V2 transforms the underlying multi-signal intelligence engines (Prompts 1 through 18) into a cohesive, company-grade operational platform for fraud analysts, cybercrime teams, financial intelligence units, and trust & safety investigators.

### Canonical Investigation Flow:
```
OUTBREAK (Outbreak Radar)
   ↓
CAMPAIGN (Campaign Workspace)
   ↓
INCIDENT (Incident Operations & Multimodal Timeline)
   ↓
JOURNEY (Chronological Attack Workflow)
   ↓
SCAMDNA (8-Dimensional Behavioral Profile)
   ↓
ENTITY (Canonical Payment, Telecom & Network Identifiers)
   ↓
GRAPH (Bipartite Knowledge Graph Explorer)
   ↓
EVIDENCE (Original vs. Derived Provenance Trace)
   ↓
ASSESSMENT (Tripartite Decision: Risk, Confidence, Urgency)
   ↓
ACTION / REVIEW (Contextual Interventions & Case Notes)
```

## 2. Key Differentiation from Generic Dashboards
Unlike legacy anti-fraud tools that rely on static IP/domain blacklists or disconnected ML scores:
- **Scam Journey Reconstruction**: Shows *how* the scam progresses across channels (SMS $\to$ WhatsApp $\to$ Call $\to$ QR $\to$ UPI Payment).
- **Behavioral DNA**: Compares campaigns across semantic, tactic, payment, and infrastructural dimensions even when fraudsters cycle all contact details.
- **Cross-Victim Correlation**: Discovers latent shared infrastructure and rotating mule accounts without compromising victim privacy.
- **Evidence Lineage**: Differentiates between primary source media (original call/screenshot) and derived extractions (OCR text, extracted VPA) to prevent double counting.
