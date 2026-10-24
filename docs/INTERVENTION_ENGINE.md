# ScamGraph AI — Adaptive Intervention Engine (Step 14)

## 1. Executive Summary & Purpose

The **Adaptive Intervention Engine** addresses the fundamental flaw of legacy anti-fraud systems: **alert fatigue**.

> **Core Philosophy**:
> The intervention engine's job is **NOT** scam classification.
> Its job is to decide **WHEN and HOW the user should be interrupted**.
> It must **never** generate disruptive, blocker-style alerts merely because a single suspicious event was observed.

By conditioning disruption on the convergence of journey stage, payment proximity, evidence confidence, and verified counter-evidence, ScamGraph AI reserves intrusive friction for the precise moment of financial vulnerability (just prior to transfer authorization).

```
   [Journey Phase]             [Threat Index]       [Intervention Tier]          [User Experience]
   Unknown message             Risk 15              ➔ NONE                       Silent background logging
   Impersonation claim         Risk 28              ➔ PASSIVE                    Subtle icon / unverified tag
   Urgency + Suspicious URL    Risk 48              ➔ CAUTION                    Informational banner (dismissible)
   OTP Request                 Risk 68              ➔ STRONG_WARNING             Step-up warning (5s pause)
   Payment Request Intent      Risk 86              ➔ PRE_PAYMENT_INTERVENTION   10s Cooldown + Action Blocker
```

---

## 2. Configurable Prototype Thresholds

All thresholds and friction durations are centralized in [intervention_config.py](file:///s:/ScamGraph-AI/services/pattern-engine/matcher/intervention_config.py):

| Intervention Tier | Min Threat Risk Index | Mandatory Friction Cooldown | Dismissible | Payment Action Blocked |
| :--- | :---: | :---: | :---: | :---: |
| **`NONE`** | 0 | 0s | Yes | No |
| **`PASSIVE`** | 20 | 0s | Yes | No |
| **`CAUTION`** | 40 | 2s | Yes | No |
| **`STRONG_WARNING`** | 65 | 5s | Yes | No |
| **`PRE_PAYMENT_INTERVENTION`** | 80 | 10s | No | **Yes** |

---

## 3. Contextual Escalation & De-escalation Rules

The decision logic in [intervention_engine.py](file:///s:/ScamGraph-AI/services/pattern-engine/matcher/intervention_engine.py) evaluates 5 environmental factors:

### A. Single Suspicious Message Protection (Alert-Fatigue Shield)
* **Rule**: When `num_events < 2`, the engine explicitly caps the intervention at `CAUTION`.
* **Rationale**: Even if a single message triggers keyword flags or high initial threat index, it must never block the user or present modal friction without journey confirmation.

### B. Payment Proximity Escalation
* **Rule**: If `payment_proximity = True` (or stage is `PAYMENT_REQUEST` / `PAYMENT_INTENT`):
  * If Threat Risk Index $\ge 75$ and events $\ge 2$: Automatically escalates to `PRE_PAYMENT_INTERVENTION`.
  * If Threat Risk Index $\ge 45$: Escalates from `CAUTION` to `STRONG_WARNING`.
* **Rationale**: Friction is timed to protect the user before fund departure.

### C. Low Confidence De-escalation
* **Rule**: When `evidence_confidence == LOW`:
  * Maximum permitted tier is capped at `STRONG_WARNING` (never `PRE_PAYMENT_INTERVENTION`).
  * If base tier was `STRONG_WARNING` and risk $< 75$, it de-escalates to `CAUTION`.
* **Rationale**: Users should not be hard-blocked on sparse or uncorroborated single-source signals.

### D. Counter-Evidence De-escalation
* **Rule**: When verified counter-evidence exists (e.g. `ESTABLISHED_LONG_TERM_DOMAIN`, `OFFICIAL_MERCHANT_VPA_VERIFIED`):
  * Maximum tier is strictly capped at `CAUTION`.
  * If risk $< 50$, the warning is reduced to `PASSIVE`.
* **Rationale**: Validated official banking communications or merchant payments must not suffer disruptive false alarms.

---

## 4. Verification & Unit Tests

Unit tests in [tests/unit/test_intervention_engine.py](file:///s:/ScamGraph-AI/tests/unit/test_intervention_engine.py) validate all operational invariants:

1. **Benign Journey**: Risk 8 $\rightarrow$ `NONE`, 0s friction, payment unblocked.
2. **Single Message Protection**: Risk 85 with 1 event $\rightarrow$ Capped at `CAUTION`, never `PRE_PAYMENT_INTERVENTION`.
3. **Graduated Journey Progression**: Step-by-step validation of `NONE` $\rightarrow$ `PASSIVE` $\rightarrow$ `CAUTION` $\rightarrow$ `STRONG_WARNING` $\rightarrow$ `PRE_PAYMENT_INTERVENTION`.
4. **Payment Proximity Escalation**: Risk 50 promoted to `STRONG_WARNING`; Risk 76 promoted to `PRE_PAYMENT_INTERVENTION`.
5. **Low Confidence De-escalation**: Risk 85 with low confidence stepped down from `PRE_PAYMENT_INTERVENTION` to `STRONG_WARNING`.
6. **Counter-Evidence De-escalation**: Risk 70 with verified merchant whitelisting stepped down from `STRONG_WARNING` to `CAUTION`.
