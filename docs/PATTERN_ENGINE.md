# Pattern Engine Architecture & Specification (Deterministic V1)

## 1. Role in ScamGraph AI

The **Pattern Engine** (`services/pattern-engine`) is the deterministic, explainable reasoning core of ScamGraph AI. It transforms atomic events and unstructured observations into canonical `PatternMatch` assessments without relying on black-box ML or LLMs.

> **Crucial Rule**: The Pattern Engine never makes a binary "fraud / not fraud" verdict. It evaluates structural alignment against known scam workflows, generating explainable match levels (`NONE`, `WEAK`, `MODERATE`, `STRONG`).

---

## 2. Declarative Patterns (`data/patterns/`)

The 5 canonical scam patterns in the Indian digital finance ecosystem:

1. **`kyc_impersonation.yaml`**: Urgent account suspension threat claiming bank/KYC non-compliance leading to credential/OTP harvesting and micro-payments.
2. **`investment_scam.yaml`**: Astronomical daily return promises over Telegram channels with upfront recharge traps.
3. **`job_task_scam.yaml`**: Remote part-time reviewer/rating jobs requiring refundable security badge fees.
4. **`fake_support_refund.yaml`**: Courier/e-commerce refund claims attempting reverse UPI PIN collection or QR code inversion.
5. **`digital_arrest.yaml`**: Authority intimidation (police/customs/CBI) demanding secret video-call detention and asset clearance transfers.

---

## 3. Explainable Weighted Sequence Matching Algorithm

The matching algorithm computes three independent dimensions:

### 3.1 Required Signal Score ($W_{\text{req}} = 0.50$)
Measures the coverage of mandatory signals:
$$\text{Score}_{\text{req}} = \frac{|\text{Matched Required Signals}|}{|\text{Total Required Signals}|}$$
*Rule*: A `STRONG` match strictly requires all mandatory signals to be present.

### 3.2 Supporting Signal Score ($W_{\text{sup}} = 0.30$)
Rewards auxiliary corroborated evidence (e.g. typosquatted TLD, unlisted VPA):
$$\text{Score}_{\text{sup}} = \frac{|\text{Matched Supporting Signals}|}{|\text{Total Supporting Signals}|}$$

### 3.3 Temporal Sequence Order Score ($W_{\text{seq}} = 0.20$)
Evaluates chronological adherence to the expected grooming progression:
$$\text{Score}_{\text{seq}} = 0.60 \times \text{In-Order Ratio} + 0.40 \times \text{Coverage Ratio}$$
Where:
- $\text{In-Order Ratio} = \frac{\text{Strictly Increasing Subsequence Count}}{|\text{Matched Events}|}$
- Events appearing in reverse or random order are penalized automatically.

### 3.4 Contradictory Evidence Penalty ($-0.35$)
If counter-evidence is verified (e.g., official long-term bank domain or verified enterprise merchant VPA), 35 points are deducted from the composite score.

---

## 4. Match Level Scale (Index, NOT a Probability)

$$\text{Composite Score} = 0.50 \cdot \text{Score}_{\text{req}} + 0.30 \cdot \text{Score}_{\text{sup}} + 0.20 \cdot \text{Score}_{\text{seq}} - \text{Penalty}_{\text{contra}}$$

| Match Level | Score Threshold | Criteria |
| :--- | :--- | :--- |
| **`STRONG`** | $\ge 0.70$ | Requires $100\%$ of mandatory signals present in correct sequence |
| **`MODERATE`** | $0.45 \le \text{Score} < 0.70$ | Corroborated partial journey observed |
| **`WEAK`** | $0.20 \le \text{Score} < 0.45$ | Sparse or ambiguous indicators |
| **`NONE`** | $< 0.20$ | Benign or irrelevant communication |
