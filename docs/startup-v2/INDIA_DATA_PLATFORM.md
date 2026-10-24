# India Data Platform Architecture
**Phase 0D: Engineering Specification**  
**Date:** October 24, 2026

---

## 1. Multi-Layer Data Platform

To support multi-channel fraud intelligence at startup scale without falling into the "one giant messy CSV" trap, the ScamGraph Data Platform defines 8 logical layers:

```mermaid
graph TD
    L0[Layer 0: Raw Source (External Archives, Web, Partner Feeds)] --> L1[Layer 1: Normalized (ScamGraphRecordV2 Standard)]
    L1 --> L2[Layer 2: Deduplicated (Exact & Structural Template Grouping)]
    L2 --> L3[Layer 3: Annotated (Human Consensus Ground Truth vs Rule Inferred)]
    L3 --> L4[Layer 4: Journey & Entity Enriched (Correlated Incidents & Breadcrumbs)]
    L4 --> L5[Layer 5: Training Candidate Snapshots]
    L4 --> L6[Layer 6: Benchmark Holdout Sets]
    L4 --> L7[Layer 7: Independent India Gold Set (Strictly Isolated)]
```

---

## 2. Specialized Corpora

Rather than flattening all data into binary message text:
1. **Message Corpus**: Single SMS and transactional notifications.
2. **Conversation Corpus**: Multi-turn WhatsApp/Telegram chat logs and voice transcripts with ordered speaker turns (`SpeakerRole`).
3. **Journey Corpus**: End-to-end longitudinal tracks capturing transitions across contact, impersonation, urgency, credential harvesting, and payment intent.
4. **Tactics Corpus**: Multi-label psychological coercion indicators (Authority, Urgency, Fear, Isolation, Secrecy).
5. **Payment Context Corpus**: Pre-transfer parameters (claimed reason, payment method, prior reward bait, cooling-off recommendation).
6. **Entity Corpus**: Canonical, masked, and hashed identifiers (phones, VPAs, domains) linked across incidents.
7. **Hard-Negative Corpus**: Legitimate bank and discom alerts containing scam-like words to prevent false alarms.
