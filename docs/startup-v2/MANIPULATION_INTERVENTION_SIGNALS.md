# ScamGraph AI — Manipulation Intervention Signals & Consumer Safety

## 1. Executive Concept
Tactic Intelligence translates internal psychological manipulation signals into **proactive consumer interventions**. The consumer is never shown raw machine learning probabilities (e.g. `p(scam) = 0.87`). Instead, they receive clear, evidence-grounded warnings and immediate protective instructions.

---

## 2. Derived Intervention Candidates

```
                 Tactic Signals (Multi-Turn)
                             │
     ┌───────────────────────┼───────────────────────┐
     ▼                       ▼                       ▼
 [ISOLATION / SECRECY    [PAYMENT_PRESSURE]    [CREDENTIAL_PRESSURE]
  + High Impact Demand]      │                       │
     │                       ▼                       ▼
     ▼                   PAYMENT_            CREDENTIAL_PROTECTION_
ANTI_ISOLATION_        INTERVENTION_               CANDIDATE
 INTERVENTION_           CANDIDATE          ("DO NOT share OTP/PIN")
   CANDIDATE        ("PAUSE before paying")
("TALK to a family
 member or bank")
```

### 1. `ANTI_ISOLATION_INTERVENTION_CANDIDATE`
- **Trigger**: `ISOLATION` or `SECRECY` present simultaneously with `PAYMENT_PRESSURE`, `CREDENTIAL_PRESSURE`, or `REMOTE_ACCESS_PRESSURE`.
- **Consumer Explanation**: *"The caller is attempting to isolate you and demanding secrecy while asking for money or credentials."*
- **Actionable Guidance**: *"Immediately disconnect or talk to a family member or local police station in person. Legitimate law enforcement will never demand secrecy over a call."*

### 2. `PAYMENT_INTERVENTION_CANDIDATE`
- **Trigger**: High-confidence `PAYMENT_PRESSURE`.
- **Consumer Explanation**: *"This message pressures you to transfer money or approve a UPI payment urgently."*
- **Actionable Guidance**: *"PAUSE. Verify the recipient's identity independently before approving any payment."*

### 3. `CREDENTIAL_PROTECTION_CANDIDATE`
- **Trigger**: `CREDENTIAL_PRESSURE`.
- **Consumer Explanation**: *"The sender is requesting secret authentication codes (OTP, PIN, or passwords)."*
- **Actionable Guidance**: *"DO NOT share your OTP. Banks and official agencies will never ask for your one-time passwords."*

### 4. `REMOTE_ACCESS_WARNING_CANDIDATE`
- **Trigger**: `REMOTE_ACCESS_PRESSURE`.
- **Consumer Explanation**: *"The sender is asking you to install remote control apps or share your screen."*
- **Actionable Guidance**: *"DO NOT install AnyDesk or share your screen. Scammers use these apps to steal banking credentials directly from your device."*

### 5. `INDEPENDENT_VERIFICATION_CANDIDATE`
- **Trigger**: `AUTHORITY` or `IMPERSONATION`.
- **Consumer Explanation**: *"The caller claims to represent an official organization or law enforcement agency."*
- **Actionable Guidance**: *"Never use phone numbers provided in the message. Always look up the official phone number on government/bank portals."*

---

## 3. Serialization Contracts
- **Consumer Serializer (`ConsumerTacticWarning`)**: Plain language, zero technical internals, privacy-masked previews, actionable steps.
- **Analyst Serializer (`serialize_analyst_view`)**: Full character offsets, SHA-256 evidence hashes, detector sources (`RULE`, `SEMANTIC`, `COMBINED`), detector agreement/disagreement flags, rule IDs, and timeline progression.
