# ScamGraph AI — Evidence Fusion and Risk Engine V1 (Step 13)

## 1. Architectural Philosophy: Risk ≠ Confidence

A core design principle of ScamGraph AI is that **Risk and Confidence are distinct, orthogonal dimensions**:

* **Threat Risk Index ($0$ to $100$ integer)**:
  Measures *how dangerous and malicious the observed incident journey appears*. It is derived from structural signals, tactical scam hallmarks (impersonation, urgency, OTP capture, deceptive links), and pattern match severity.
  > **Note**: Threat Risk Index is explicitly **not** a probability. It is an explainable heuristic threat severity score.

* **Evidence Confidence (`LOW`, `MEDIUM`, `HIGH`)**:
  Measures *how complete, reliable, and mutually corroborating the supporting evidence sources are*. Even if an incident matches a devastating scam blueprint, the confidence is calibrated down if observation originates from only a single unverified source.

```
       ▲ High
       │
       │  [Elevated Threat / Low Evidence]      [Confirmed Weaponized Attack]
       │  Strong pattern match, but             Multiple verified signals from
       │  sparse or single-source evidence      TinyFish, URL intel, and message
T      │  ➔ Flag for immediate investigation    ➔ Urgent automated mitigation
H      │
R      │  [Benign / False Positive]             [Verified Normal Activity]
E      │  No scam indicators, low certainty     Legitimate communication verified
A      │  ➔ Auto-closed / low priority          by counter-evidence and whitelists
T      │
       └─────────────────────────────────────────────────────────────► High
                                  EVIDENCE CONFIDENCE
```

---

## 2. Centralized Configuration & Heuristics

All weights, penalty factors, and classification thresholds are centralized in [risk_config.py](file:///s:/ScamGraph-AI/services/pattern-engine/matcher/risk_config.py), eliminating magic constants across the codebase.

### Base Threat Category Points
| Category | Heuristic Points | Description |
| :--- | :---: | :--- |
| `OTP_REQUEST` | $+35$ | Interception of one-time authentication codes |
| `CREDENTIAL_REQUEST` | $+30$ | Phishing of banking passwords, PINs, or credentials |
| `IMPERSONATION` | $+25$ | Posing as trusted organizations (SBI, Police, Tax dept) |
| `PAYMENT_REQUEST` | $+25$ | Direct transfer prompts, QR code deception, UPI requests |
| `SUSPICIOUS_URL` | $+25$ | Newly registered domains, typosquats, dynamic IP targets |
| `URGENCY` | $+20$ | Artificial deadlines ("within 2 hours", "immediate arrest") |
| `KNOWN_RELATIONSHIP` | $+10$ | Link to known suspect phone numbers, IPs, or campaigns |

### Pattern Amplification Bonuses
* **`STRONG` Pattern Match**: $+18$ points
* **`MODERATE` Pattern Match**: $+10$ points
* **`WEAK` Pattern Match**: $+4$ points
* **`NONE`**: $+0$ points

### Counter-Evidence Discounts
* **Counter-Evidence Deduction**: $-25$ points per verified benign indicator (e.g., official whitelisted bank domain, legitimate customer service confirmation), ensuring counter-evidence directly tempers false alarms.

### Risk Level Thresholds
* **`HIGH` Risk**: Score $\ge 65$
* **`MEDIUM` Risk**: Score $\ge 35$
* **`LOW` Risk**: Score $< 35$

---

## 3. Prevention of Double-Counting (Evidence Deduplication)

When multiple independent detection pipelines analyze an incident, they frequently observe the identical underlying threat artifact. For example:
* **TinyFish Visual Parser** detects an OTP input field on the DOM.
* **URL Static Analyzer** flags `/verify-otp.php` in the query URI.

Blindly summing $+35 + 35 = 70$ points for these two observations artificially inflates the threat score.

**Deduplication Solution in `RiskEngineV1`**:
1. All incoming `Evidence` items are normalized and clustered by **Threat Category** (`OTP_REQUEST`, `CREDENTIAL_REQUEST`, `IMPERSONATION`, etc.).
2. For each unique threat category, the engine selects the highest-confidence evidence observation and awards the category score **exactly once**.
3. All supporting evidence IDs across different sources are consolidated and cited in the explainability trail (`[RC_OTP_REQUEST] Evidence ID(s): <id-1>, <id-2>`), providing complete forensic provenance without duplicating risk weight.

---

## 4. Handling Ambiguity & Insufficient Evidence

ScamGraph AI treats ambiguity as a first-class state:
* When an isolated signal is observed (e.g. a payment request link without impersonation, without urgency, without credential capture, and without suspicious URL intelligence), it is categorized with:
  ```python
  insufficient_evidence = True
  risk_level = RiskLevel.UNKNOWN  # or LOW
  ```
* This prevents regular e-commerce receipts, innocent invoices, or normal merchant links from being misclassified as fraudulent attacks.

---

## 5. Confidence Calibration Algorithm

Confidence is dynamically determined through an explainable multi-factor formula:
1. **Source Diversity**: Counts distinct `EvidenceSource` origins (e.g., `MESSAGE_ANALYZER`, `TINYFISH_CRAWLER`, `URL_INTEL`, `GRAPH_ANALYTICS`).
   * $\ge 3$ sources $\rightarrow$ Eligible for `HIGH` confidence.
   * $2$ sources $\rightarrow$ `MEDIUM` confidence baseline.
   * $1$ source $\rightarrow$ `LOW` confidence cap.
2. **Signal Completeness**: Checks presence of core threat categories versus missing investigation leads.
3. **Contradiction Penalty**: If counter-evidence conflicts with scam signals, confidence reflects that divergence and counter-evidence reasons are retained in the final assessment.

---

## 6. Verification & Test Suite

The test suite in [tests/unit/test_risk_engine_v1.py](file:///s:/ScamGraph-AI/tests/unit/test_risk_engine_v1.py) validates the 6 required scenarios and deduplication:
1. **Obvious KYC Scam**: Multiple correlated signals $\rightarrow$ Score $\ge 85$ (`HIGH` risk, `HIGH` confidence).
2. **Normal Payment**: Whitelisted payment link with official receipts $\rightarrow$ Score $0$ (`LOW` risk, counter-evidence retained).
3. **Ambiguous Payment Link**: Isolated payment link $\rightarrow$ `insufficient_evidence = True`, `risk_level = UNKNOWN`.
4. **Strong Pattern with Sparse Evidence**: Strong pattern bonus elevated, but single evidence source forces `confidence = LOW`.
5. **Multiple Independent Sources**: Cross-validation elevates confidence to `HIGH`.
6. **Contradictory Evidence**: Preserves counter-evidence in reason codes and discounts risk index by 25 points.
7. **Deduplication Validation**: Dual detection of OTP by TinyFish and URL Intel awards points once while combining provenance IDs.
