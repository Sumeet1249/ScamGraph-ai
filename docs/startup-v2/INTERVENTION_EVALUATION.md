# SCAMGRAPH AI — INTERVENTION EVALUATION FRAMEWORK (PHASE 4B)
## Pre-Loss Metrics, Prefix Evaluation & Progressive Friction Verification

### 1. Primary Startup Metrics

Unlike classification models that measure offline F1 score, ScamGraph's product value is defined by **actionable pre-loss intervention**:

| Metric | Target | Definition |
|---|---|---|
| **Pre-Loss Intervention Rate** | $\ge 90\%$ | Percentage of scam journeys where a protective intervention (`DELAY_PAYMENT`, `TALK_TO_TRUSTED_PERSON`, `DO_NOT_SHARE_OTP`) was issued *before* irreversible loss. |
| **False Warning Rate** | $< 3\%$ | Percentage of routine legitimate payments (rent, family, bills) that received disruptive warnings. |
| **Pre-Loss Warning Lead Time** | $\ge 1$ Stage | Number of temporal journey stages between first warning and monetization request. |
| **Cooling-Off Engagement Rate** | $\ge 70\%$ | Fraction of users who paused transfer upon seeing the 120-minute cooling-off recommendation. |

---

### 2. Prefix-by-Prefix Journey Replay Protocol

To prevent future temporal leakage:
1. Replay multi-step incident timeline event-by-event ($E_1, E_2, \dots, E_N$).
2. At event $E_k$, evaluate Contextual Intervention using **only** observables up to $k$.
3. Measure the earliest event $k^*$ where intervention shifted from `NO_ACTION` to protective action (`PAUSE_AND_VERIFY`, `DELAY_PAYMENT`).
4. Prove that $k^* < k_{\text{payment}}$ across all evaluation benchmarks.
