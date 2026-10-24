# ScamGraph AI — Scam Journey Engine V1 Architecture (Phase 2A)

## 1. Executive Mission & Strategic Differentiation
Conventional scam detection treats each communication in isolation:
- Is this SMS text fraudulent?
- Is this URL malicious?
- Is this UPI ID reported?

ScamGraph AI V2 introduces the **Scam Journey Engine V1**—a longitudinal, cross-channel behavioral intelligence system that asks:
> **"What is happening to this victim, in what order, which stage has this interaction reached, is it moving toward financial extraction, and what actionable intervention will interrupt the loss before money is sent?"**

By reconstructing the temporal sequence of events across multiple channels (Instagram $\rightarrow$ WhatsApp $\rightarrow$ Telegram $\rightarrow$ UPI), ScamGraph moves from reactive classification to **pre-loss disruption**.

---

## 2. Fundamental Cognitive Separations

To ensure robust evaluation and avoid categorical confusion, ScamGraph enforces three distinct boundaries:

$$\text{STAGE} \neq \text{TACTIC} \neq \text{SCAM FAMILY}$$

1. **Stage $\neq$ Tactic**:
   - `TACTIC` (Phase 1B): Psychological manipulation vectors (`URGENCY`, `FEAR`, `SECRECY`, `AUTHORITY`, `RECIPROCITY`).
   - `STAGE` (Phase 2A): Structural position in the fraud lifecycle (`INITIAL_PAYMENT`, `PAYMENT_ESCALATION`, `WITHDRAWAL_BLOCK`).
   - *Example*: The tactic `URGENCY` can occur during `CONTACT`, `INITIAL_PAYMENT`, or `WITHDRAWAL_BLOCK`.
2. **Stage $\neq$ Scam Family**:
   - `SCAM FAMILY`: Typology of fraud (`JOB_TASK`, `INVESTMENT`, `DIGITAL_ARREST`, `KYC_BANK`).
   - Multiple families share identical stages (e.g. both `JOB_TASK` and `INVESTMENT` share `INITIAL_PAYMENT` $\rightarrow$ `PAYMENT_ESCALATION` $\rightarrow$ `WITHDRAWAL_BLOCK`).
3. **Observation $\neq$ Conclusion**:
   - An event candidate does not unilaterally alter current stage without sequence alignment and confidence validation.

---

## 3. Non-Linear State Progression Architecture
Real-world cyber scams rarely follow rigid linear state machines. Attackers frequently:
- Skip stages (e.g., direct `CONTACT` $\rightarrow$ `THREAT` $\rightarrow$ `INITIAL_PAYMENT` in aggressive extortion),
- Repeat stages (e.g., multiple deposit cycles in task fraud),
- Overlap stages (e.g., simultaneous `PAYMENT_ESCALATION` and `THREAT_OR_PRESSURE`),
- Submit out-of-order evidence (e.g., victim uploads today's payment receipt first, then earlier chat logs).

The Journey Engine handles this via **Temporal Sequence Alignment** and **Evidence-Grounded Stage Observations**, dynamically maintaining:
- A sorted chronological event stream,
- Historical stage observations with reason codes and evidence IDs,
- A current primary stage + active secondary stages,
- Proactive candidate early warnings.

---

## 4. Multi-Channel Journey Progression
ScamGraph natively stitches cross-channel touchpoints into a unified encounter:

```
[Instagram Ad]          [WhatsApp Onboarding]         [Telegram Group]           [UPI Gateway]
      │                           │                           │                         │
DISCOVERY ────────────> CONTACT & TRUST ─────────> PLATFORM_MIGRATION ───> INITIAL_PAYMENT & ESCALATION
(Job offer seen)        (Test payout ₹150)         (VIP Task Group)        (Deposit ₹5k -> ₹25k)
```

---

## 5. Incremental Processing & Idempotency
Designed for millions of concurrent users:
- **Idempotency**: Repeated ingestion of the same event ID returns the existing journey state without duplicate stage observations or false progress updates.
- **Incremental Processing**: New events update sequence alignment and current stage without triggering expensive re-computation across all historical artifacts.
- **Full Recomputation**: Supported on demand when out-of-order evidence arrives or models are updated.

---

## 6. Pre-Loss Detection & Warning Lead Time
The primary proprietary metric of ScamGraph V1 is **Pre-Loss Detection**:
- **Monetization Boundary**: The first event attempting to extract money, financial credentials, or remote device control.
- **Actionable Warning Timestamp ($T_{\text{warn}}$)**: When the system issues a `STRONG_WARNING` or `IMMEDIATE_PAUSE`.
- **Loss Timestamp ($T_{\text{loss}}$)**: When the victim confirmed irreversible money transfer.
- **Warning Lead Time**:
  $$\Delta T = T_{\text{loss}} - T_{\text{warn}}$$
  Measuring how many minutes or hours of protective lead time ScamGraph provided prior to harm.
