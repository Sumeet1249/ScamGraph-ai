# Scam Outbreak Radar System

## Conceptual Definition
The **Scam Outbreak Radar** is an analytical, non-physical intelligence visualization that projects active scam campaigns onto three concentric rings based on operational urgency, report velocity, and real-world impact:

```
                      OUTER RING: EMERGING / WATCH (r=275px)
                  ┌──────────────────────────────────────────────┐
                  │                 ○ KYC-27                     │
                  │                                              │
                  │       MIDDLE RING: SURGING (r=195px)         │
                  │      ┌─────────────────────────────┐         │
                  │      │         ● TASK-14           │         │
                  │      │                             │         │
                  │      │    INNER RING: CRITICAL     │         │
                  │      │    ┌──────────────────┐     │         │
                  │      │    │     ● DA-08      │     │         │
                  │      │    │  (Digital Arrest)│     │         │
                  │      │    └──────────────────┘     │         │
                  │      └─────────────────────────────┘         │
                  │ ○ INVEST-11                                  │
                  └──────────────────────────────────────────────┘
```

### Visual Encodings
- **Concentric Ring**: Urgency & Outbreak tier (Inner = Critical/Outbreak, Middle = Surging, Outer = Emerging/Watch).
- **Position Angle**: Derived deterministically from scam family and campaign ID hash to guarantee visual stability across reloads without fake physical geography.
- **Node Size**: Reflects verified incident volume.
- **Pulse Frequency**: Reflects normalized growth multiplier over historical baseline.
- **Confidence Halo**: Reflects multi-signal corroboration quality ($0.40 - 0.98$).

---

## Outbreak Signal Taxonomy (`OutbreakSignal`)

| Signal Type | Trigger Condition | Default Severity |
| :--- | :--- | :--- |
| `HIGH_RISK_OUTBREAK` | $>3.5\times$ growth over baseline and $\ge 8$ reports/24h | `CRITICAL` |
| `RAPID_GROWTH` | $>2.2\times$ growth over baseline | `HIGH` |
| `RESURGENCE` | Dormant campaign active again after $\ge 30$ days | `HIGH` |
| `PAYMENT_REUSE_SPIKE` | New high-velocity UPI handle detected in active campaign | `ELEVATED` |
| `INFRASTRUCTURE_ROTATION` | New phone/domain linked to existing ScamDNA | `ELEVATED` |
| `CHANNEL_MIGRATION` | Ingestion flags shift to new medium (e.g. WhatsApp $\to$ Telegram) | `WATCH` |
| `NEW_CAMPAIGN` | Cohesive ScamDNA cluster meeting candidacy thresholds | `WATCH` |
