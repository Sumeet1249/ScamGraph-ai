# Product Intelligence Requirements & Data Mapping
**Phase 0D: Product Intelligence Matrix**  
**Date:** October 24, 2026

---

## 1. The Three Protection Moments

```mermaid
graph LR
    subgraph MOMENT 1: PREVENT (Before Loss)
        M1[Universal Scam Check: 'Am I being scammed?']
    end
    subgraph MOMENT 2: INTERRUPT (During Manipulation)
        M2[Contextual Payment Guard & Progress Meter]
    end
    subgraph MOMENT 3: RESPOND (After Loss)
        M3[ScamGraph Rescue & Official 1930 / Cyber Reporting]
    end

    M1 --> M2 --> M3
```

---

## 2. Data to Product Intelligence Matrix

| Data Corpus | Intelligence Engine | Product Feature / Capability | Consumer Experience |
| :--- | :--- | :--- | :--- |
| **Message Corpus** | Message NLP Classifier | **Universal Scam Check** | Instant analysis of suspicious SMS or WhatsApp messages. |
| **Conversation Corpus** | Conversation Intelligence | **Dialogue Threat Monitor** | Analyzes streaming chat logs to detect escalation from casual chat to fraud. |
| **Journey Corpus** | Journey Engine | **Scam Progress Meter** | Visual indicator: `Contact ✓ → Trust Building ✓ → Payment Request [YOU ARE HERE]`. |
| **Tactics Corpus** | Tactic Intelligence | **Manipulation Warning** | Plain-language explanation: *"We detected Authority + Secrecy + Payment Pressure."* |
| **Payment Context** | Contextual Payment Guard | **Pre-Payment Cooling Off** | Recommends: *"Stop. Do not send ₹20,000 for a part-time job task deposit."* |
| **Entity Corpus** | Entity Correlation Engine | **Cross-Victim Intelligence** | Alerts: *"This UPI ID has been reported by 4 other victims across India."* |
| **Campaign Corpus** | Outbreak Radar | **Proactive Threat Alerts** | Warns users in specific circles of surging regional scam waves. |
| **Evidence Corpus** | Evidence Synthesis Engine | **Explainability & Counter-Evidence**| Shows both risk indicators and legitimate verified domains to prevent blind fear. |
| **Hard-Negative Corpus**| False-Alarm Suppressor | **Legitimate Notification Shield** | Prevents false alarms on routine SBI/HDFC OTPs and discom electricity bills. |

---

## 3. Product Feature Roadmap Priorities

- **P0 (Startup Core)**:
  - Universal Scam Check (unified text/link/UPI input)
  - Journey-aware warnings with explainable reasons
  - Scam Progress Meter
  - Independent verification assistance (official bank/discom portals)
- **P1 (Intervention & Recovery)**:
  - Contextual Payment Guard (pre-transfer cooling-off prompt)
  - ScamGraph Rescue (1930 helpline guidance, bank freeze checklist, evidence pack export)
  - Case history tracking
  - Hindi & Hinglish support
- **P2 (Scale & Multi-Channel)**:
  - Voice-assisted scam check
  - Regional language expansion (Tamil, Telugu, Bengali, Marathi)
  - Proactive campaign alerts
