# ScamGraph Rescue: Post-Loss Emergency Architecture (Prompt 16 / Phase 5B)

## Executive Summary
ScamGraph Rescue activates when prevention has failed: a user sent money, disclosed an OTP or banking credentials, installed remote-control software (AnyDesk, TeamViewer), or experienced account takeover. 

Rescue does **NOT** operate as a detached complaint app. Instead, it reuses the canonical **Incident → Journey → Evidence → Assessment** foundation, transforming intelligence gathered across the network into:
1. Immediate protective actions (DO NOW, DO NEXT, PRESERVE, REPORT, MONITOR)
2. Structured incident reconstruction
3. Immutable evidence preservation
4. Multi-payment loss timeline (e.g., ₹500 → ₹5,000 → ₹20,000)
5. Verified official India reporting preparation (1930 Helpline, NCRP portal, bank 24/7 emergency fraud desks)
6. Exposure assessment (Credential, Device, Identity document)
7. Recovery-scam defense (warnings against secondary advance-fee fraud)
8. Privacy-safe Case Package export

---

## Architecture Principles & Guardrails
- **Zero Fraudulent Promises**: ScamGraph never claims transactions can be guaranteed reversed or funds guaranteed recovered.
- **No Unauthorized Filing**: ScamGraph does NOT fabricate FIR numbers or pretend to file complaints automatically without authorized integrations.
- **Tripartite Delineation**:
  - `USER_REPORTED`: Facts provided by the victim (amounts, times, recipient VPA).
  - `SCAMGRAPH_INFERRED`: Typology inference, stage progression, manipulation tactics, campaign links.
  - `EXTERNALLY_VERIFIED`: Confirmed by official banking core feeds or law enforcement portals.
- **Continuous Lifecycle**: Protect, Guard, and Rescue operate on the exact same `Incident` entity. An incident evaluated during pre-payment check transitions seamlessly into Rescue when the user clicks "I Already Paid".

---

## Flywheel Network Feedback Loop
```
RESCUE INCIDENT (Post-Loss Evidence)
         │
         ▼
Entity Extraction (Mule VPA, Phone, URL)
         │
         ▼
Canonical Incident & Journey Update
         │
         ▼
ScamDNA V3 Mutation Recomputation
         │
         ▼
Knowledge Graph V2 Multi-Hop Projection
         │
         ▼
Cross-Victim Correlation Engine
         │
         ▼
Campaign Intelligence V2 Candidate Update
         │
         ▼
Unified Reassessment & Pre-Payment Guard Warning
(Protects Future Users Before They Pay)
```
