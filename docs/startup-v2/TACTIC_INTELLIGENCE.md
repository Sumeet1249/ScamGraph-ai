# ScamGraph AI — Psychological Manipulation & Tactic Intelligence Engine V2 (Phase 1B)

## 1. Executive Summary & Phase Mission
Conventional scam detectors ask: *"Does this message look suspicious?"*
ScamGraph AI asks a radically more powerful question:
> **"How is this person being manipulated, where is the evidence, how far has that manipulation escalated, what action is being demanded, and what proactive intervention will interrupt it?"**

Phase 1B constructs the **Human Manipulation, Social-Engineering & Tactic Intelligence Engine**. It shifts ScamGraph from single-token regex detection into an evidence-grounded, multi-lingual behavioral intelligence platform across single messages, multi-turn dialogues, and incident timelines.

---

## 2. Fundamental Cognitive Separations
To prevent catastrophic false positives and protect legitimate communication, ScamGraph enforces strict cognitive separation:

$$\text{CONTENT} \neq \text{TACTIC} \neq \text{INTENT} \neq \text{REQUESTED ACTION} \neq \text{JOURNEY STAGE}$$

| Dimension | Definition | Example |
| :--- | :--- | :--- |
| **Content** | The raw lexical utterance | *"Your account will be blocked today."* |
| **Tactic** | Psychological influence vector | `FEAR`, `URGENCY` |
| **Intent** | Actor's operational goal | Pressure victim into immediate compliance without deliberation |
| **Requested Action** | Behavioral call-to-action demanded | `CLICK_LINK` / `SEND_PAYMENT` |
| **Journey Stage** | Lifecycle position in fraud funnel | Inferred later by Journey Engine V1 (`MONETIZATION`) |

### Critical Principle: No Naive Keyword Detection
Keywords alone **never** equal manipulation:
- *"Police have advised citizens never to share OTPs."* $\rightarrow$ Contains `police` and `OTP`, but is an **authoritative advisory**, NOT manipulation.
- *"Your electricity bill was paid successfully."* $\rightarrow$ Routine notification, NOT payment pressure.
- *"Your interview is scheduled for tomorrow at 10 AM."* $\rightarrow$ Routine schedule, NOT urgency.

---

## 3. Hybrid Multi-Tier Inference Architecture
In accordance with Phase 0E inference routing, Tactic Intelligence operates across calibrated tiers:

```
                          Incoming Artifact / Turn
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
       [Quoted Inquiry Check]                 [Global Advisory Guard]
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     │
                                     ▼
                      Tier 0: Rule-Based Tactic Engine
                      (English, Hindi, Hinglish Regexes
                       + Negative Protective Patterns)
                                     │
                                     ▼
                      Tier 1: Semantic Prototype Matcher
                      (Calibrated Cosine Similarity on
                       Positive vs Negative Prototypes)
                                     │
                                     ▼
                     Hybrid Multi-Label Classification
                      (Agreement, Disagreement Flagging,
                       Evidence Span Offset Extraction)
                                     │
                                     ▼
                      Services / Timeline Orchestration
                      (Entity Linking, Timeline Escalation,
                       Density, Intervention Candidates)
```

1. **Tier 0 (Deterministic Rules)**: 38 versioned rules (`TACTIC-*-001`) with bidirectional positive and negative contextual patterns. Executes in $<0.2\text{ ms}$.
2. **Tier 1 (Semantic Prototypes)**: Calibrated positive exemplars and hard-negative anchors using token-vector projections. Executes in $<1.5\text{ ms}$.
3. **Multi-Label Combiner**: Detects detector agreement, boosts confidence upon convergence, and flags disagreements.
4. **Degraded Mode Resilience**: If semantic or downstream modules fail, the engine degrades gracefully to Tier 0 deterministic rules, logging `degraded: true` without dropping user protection.

---

## 4. Multi-Turn Timeline & Escalation Intelligence
Single-message detection cannot capture grooming. ScamGraph tracks **chronological tactic evolution**:

```
Turn 1 (Instagram/Job):  OPPORTUNITY / GREED          ("Work from home earn ₹3,000/day")
Turn 2 (WhatsApp):       TRUST_BUILDING               ("Complete test task, here is ₹150")
Turn 3 (Telegram):       PLATFORM_MIGRATION           ("Join VIP group for official payout")
Turn 4 (Telegram):       FAKE_REWARD + RECIPROCITY    ("You earned ₹1,200! Now recharge ₹5,000")
Turn 5 (Telegram):       PAYMENT_PRESSURE + URGENCY   ("Deposit ₹5,000 immediately or forfeit")
Turn 6 (Telegram):       LOSS_AVERSION + THREAT       ("Pay ₹10,000 tax or police case will be filed")
```

### Key Timeline Metrics:
- **Tactic Vector**: Normalized $\{ \text{Tactic}: \text{Score} \}$ representation serving as the behavioral dimension for future **ScamDNA**.
- **Manipulation Density**: Ratio of coercive tactic signals to conversation turns:
  $$\text{Density} = \frac{\sum \text{Active Coercive Signals}}{\max(1, \text{Total Message Turns})}$$
- **Escalation Signal**: Automated trigger fired when communication shifts from early reward/grooming to late-stage financial coercion or threats.

---

## 5. Proactive Intervention Candidates
Tactic signals feed directly into candidate protective interventions:

1. **`ANTI_ISOLATION_INTERVENTION_CANDIDATE`**:
   Triggered when `SECRECY` or `ISOLATION` coincides with `PAYMENT_PRESSURE`, `CREDENTIAL_PRESSURE`, or `REMOTE_ACCESS_PRESSURE`.
2. **`PAYMENT_INTERVENTION_CANDIDATE`**:
   Triggered on high-confidence `PAYMENT_PRESSURE`.
3. **`CREDENTIAL_PROTECTION_CANDIDATE`**:
   Triggered on `CREDENTIAL_PRESSURE` (OTP, PIN, Password harvest).
4. **`REMOTE_ACCESS_WARNING_CANDIDATE`**:
   Triggered on `REMOTE_ACCESS_PRESSURE` (AnyDesk, QuickSupport, screen sharing).
5. **`INDEPENDENT_VERIFICATION_CANDIDATE`**:
   Triggered on `AUTHORITY` or `IMPERSONATION` claims.

---

## 6. Multi-Lingual & Hinglish Code-Mixing
ScamGraph natively supports English, Hindi (Devanagari), and Hinglish (Latin script code-mixed phonetics):
- *“abhi payment karo varna bijli cut ho jayegi”* $\rightarrow$ `PAYMENT_PRESSURE`, `URGENCY`, `FEAR`.
- *“kisi ko mat batana, CBI ki gupt janch hai”* $\rightarrow$ `SECRECY`, `AUTHORITY`.
- *“AnyDesk download karke screen share karo”* $\rightarrow$ `REMOTE_ACCESS_PRESSURE`.
- *“otp share karo verification ke liye”* $\rightarrow$ `CREDENTIAL_PRESSURE`.
- *“kabhi bhi OTP share mat karna”* $\rightarrow$ **Negated / Advisory (Suppressed)**.
