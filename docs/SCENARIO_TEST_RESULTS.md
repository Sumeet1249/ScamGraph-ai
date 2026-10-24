# ScamGraph AI — Safe Synthetic Scenario Test Results (Step 15)

## 1. Executive Summary

This document records the automated execution of the **ScamGraph Scenario Runner** across all 6 safe synthetic scenarios. 

* **Safety Invariant**: Scenarios utilize **ONLY** `example.com` / `example.test` reserved domains, fictional telephone numbers (`+9198765xxxxx`), and synthetic payment addresses (`*.fakeupi`). No real scam infrastructure or live phishing targets are ever contacted.
* **Deterministic Intelligence**: Results are produced autonomously by ScamGraph's core analytical pipeline without external LLMs, machine learning, or mock stubs:
  $$\text{Incident} \longrightarrow \text{Timeline} \longrightarrow \text{PatternEngine V1} \longrightarrow \text{EvidenceFusion / RiskEngine V1} \longrightarrow \text{AdaptiveInterventionEngine}$$

---

## 2. Multi-Scenario Execution Matrix

| # | Scenario Name | Matched Pattern | Match Level | Threat Risk Index | Risk Level | Evidence Confidence | Intervention Action | Friction Delay | Payment Blocked |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **01** | Normal Utility Payment | *None / Negligible* | `WEAK` | **15 / 100** | `LOW` | `LOW` | **`NONE`** | 0s | **No** |
| **02** | KYC Bank Impersonation | KYC_IMPERSONATION | `STRONG` | **100 / 100** | `HIGH` | `HIGH` | **`PRE_PAYMENT_INTERVENTION`** | 10s | **Yes** |
| **03** | High-Yield Crypto Scam | INVESTMENT_SCAM | `STRONG` | **84 / 100** | `HIGH` | `HIGH` | **`PRE_PAYMENT_INTERVENTION`** | 10s | **Yes** |
| **04** | Fake Job & Review Task | JOB_TASK_SCAM | `STRONG` | **89 / 100** | `HIGH` | `HIGH` | **`PRE_PAYMENT_INTERVENTION`** | 10s | **Yes** |
| **05** | Ambiguous Peer Payment | *None* | `NONE` | **15 / 100** | `LOW` *(Insufficient)* | `LOW` | **`NONE`** | 0s | **No** |
| **06** | Digital Arrest / Coercion | DIGITAL_ARREST | `STRONG` | **85 / 100** | `HIGH` | `MEDIUM` | **`PRE_PAYMENT_INTERVENTION`** | 10s | **Yes** |

---

## 3. Detailed Scenario Breakdowns

### Scenario 01: Normal Utility Payment
* **Journey**:
  - `T+00s` `MESSAGE_RECEIVED`: SMS utility bill reminder for INR 1,450.
  - `T+30s` `URL_OPENED`: User visits `https://utility.example.com/bill`.
  - `T+60s` `PAYMENT_REQUEST`: Payment gateway requests transfer to `utility@officialbank`.
  - `T+85s` `PAYMENT_INTENT`: User confirms payment.
* **Corroborating Evidence**:
  - `ESTABLISHED_LONG_TERM_DOMAIN`: Domain registered 14 years ago (DNS).
  - `OFFICIAL_MERCHANT_VPA_VERIFIED`: Verified public utility merchant handle.
* **Engine Output**:
  - **Threat Risk Index**: 15 / 100 (`LOW`)
  - **Counter-Evidence Deductions**: Verified domain and official merchant VPA retained.
  - **Intervention Decision**: `NONE` (0s friction, payment allowed smoothly).
  - **Alert-Fatigue Outcome**: Zero intrusive modals; legitimate commerce is never disrupted.

---

### Scenario 02: KYC Bank Impersonation Scam
* **Journey**:
  - `T+00s` `MESSAGE_RECEIVED`: "SBI Alert: Netbanking blocked due to KYC. Update at https://sbi-verify.example.test/kyc"
  - `T+25s` `URL_OPENED`: Phishing domain opened.
  - `T+50s` `CREDENTIAL_REQUEST`: Netbanking username and password requested.
  - `T+75s` `OTP_REQUEST`: Prompt for 6-digit one-time password.
  - `T+100s` `PAYMENT_REQUEST`: Deceptive authorization of INR 25,000 to `fraudster.wallet@fakeupi`.
  - `T+115s` `PAYMENT_INTENT`: Victim on final authorization screen.
* **Corroborating Evidence**:
  - `OFFICIAL_ENTITY_IMPERSONATION`: Sender poses as SBI Netbanking Security.
  - `URGENCY_PRESSURE_DETECTED`: "Blocked within 2 hours".
  - `SUSPICIOUS_URL_PRESENT`: Typosquatted domain mimicking official brand.
  - `OTP_INPUT_FORM_OBSERVED`: Sensitive OTP capture on unverified origin (TinyFish DOM).
  - `INDIVIDUAL_VPA_PAYMENT_TARGETED`: Destination belongs to individual handle.
* **Engine Output**:
  - **Pattern**: `KYC_IMPERSONATION` (`STRONG` match).
  - **Threat Risk Index**: 100 / 100 (`HIGH`).
  - **Evidence Confidence**: `HIGH` (Multi-source corroboration across message analyzer, URL analyzer, TinyFish DOM, and payment model).
  - **Intervention Decision**: `PRE_PAYMENT_INTERVENTION` (10s mandatory step-up friction cooldown, payment authorization blocked).

---

### Scenario 03: High-Yield Crypto Investment Scam
* **Journey**:
  - `T+00s` `MESSAGE_RECEIVED`: "Earn guaranteed 30% daily return on AI crypto trading."
  - `T+30s` `URL_OPENED`: Deceptive portal `https://crypto-vip.example.test`.
  - `T+75s` `PAYMENT_REQUEST`: Deposit 20,000 INR to `invest.pool@fakeupi` for Tier 1 activation.
  - `T+95s` `PAYMENT_INTENT`: User on checkout screen.
* **Corroborating Evidence**:
  - `HIGH_RETURN_PROMISE`: Unrealistically inflated daily yield guarantee.
  - `SUSPICIOUS_URL_PRESENT`: Fast-flux unverified domain.
  - `CRYPTO_OR_UPI_DEPOSIT_REQUEST`: Demands irreversible wallet deposit.
* **Engine Output**:
  - **Pattern**: `INVESTMENT_SCAM` (`STRONG` match).
  - **Threat Risk Index**: 84 / 100 (`HIGH`).
  - **Evidence Confidence**: `HIGH`.
  - **Intervention Decision**: `PRE_PAYMENT_INTERVENTION` (10s friction, payment blocked).

---

### Scenario 04: Fake Job & Reviewer Task Scam
* **Journey**:
  - `T+00s` `MESSAGE_RECEIVED`: "Work from home earning 2,000-5,000 INR/day rating hotels online."
  - `T+25s` `URL_OPENED`: Task website `https://easy-ratings.example.test`.
  - `T+60s` `CREDENTIAL_REQUEST`: Worker registration and identity capture.
  - `T+90s` `PAYMENT_REQUEST`: 5,000 INR prepaid task pledge deposit required to unlock commissions.
  - `T+110s` `PAYMENT_INTENT`: User initiates transfer.
* **Corroborating Evidence**:
  - `EMPLOYMENT_OFFER_CONTEXT`: Remote flexible review job lure.
  - `REGISTRATION_OR_BADGE_FEE`: Mandatory candidate upfront deposit.
  - `UNVERIFIED_EMPLOYER_DOMAIN`: No corporate registration or domain longevity.
  - `PERSONAL_VPA_PAYMENT_TARGETED`: Fund destination is private individual VPA.
* **Engine Output**:
  - **Pattern**: `JOB_TASK_SCAM` (`STRONG` match).
  - **Threat Risk Index**: 89 / 100 (`HIGH`).
  - **Evidence Confidence**: `HIGH`.
  - **Intervention Decision**: `PRE_PAYMENT_INTERVENTION` (10s friction, payment blocked).

---

### Scenario 05: Ambiguous Peer-to-Peer Payment Link
* **Journey**:
  - `T+00s` `MESSAGE_RECEIVED`: "Hey, please send over the 500 INR for dinner."
  - `T+30s` `PAYMENT_REQUEST`: Payment link for 500 INR to `peer.split@example.test`.
* **Corroborating Evidence**:
  - Isolated `PAYMENT_REQUEST` with no impersonation, no urgency, no suspicious URL, and no campaign links.
* **Engine Output**:
  - **Pattern**: `NONE`.
  - **Threat Risk Index**: 15 / 100 (`LOW`).
  - **Evidence State**: `insufficient_evidence = True` (`RiskLevel.LOW` / `UNKNOWN`).
  - **Intervention Decision**: `NONE` (Payment allowed, no disruption).
  - **Alert-Fatigue Outcome**: Normal peer-to-peer transfers are protected from false positives.

---

### Scenario 06: Digital Arrest / Authority Coercion Variant
* **Journey**:
  - `T+00s` `CALL_REPORTED`: Automated call claiming Telecom Regulatory Authority disconnect notice.
  - `T+25s` `MESSAGE_RECEIVED`: WhatsApp CBI arrest warrant for money laundering.
  - `T+55s` `CREDENTIAL_REQUEST`: Coercive demand for Aadhaar/PAN clearance verification.
  - `T+90s` `PAYMENT_REQUEST`: Demand for 100,000 INR transfer to "Supreme Court Escrow" `escrow.verify@fakeupi`.
  - `T+110s` `PAYMENT_INTENT`: Victim prepares wire transfer under intimidation.
* **Corroborating Evidence**:
  - `LAW_ENFORCEMENT_IMPERSONATION`: Posing as CBI & Mumbai Cyber Crime Cell.
  - `LEGAL_PENALTY_FEAR_THREAT`: Threats of immediate physical arrest and asset forfeiture.
  - `VIDEO_CALL_ISOLATION_REQUEST`: Order to maintain 24h surveillance call.
  - `FAKE_ARREST_WARRANT_PRESENTED`: Forged legal documents.
  - `SECURITY_DEPOSIT_DEMAND`: Coercive asset clearance deposit.
* **Engine Output**:
  - **Pattern**: `DIGITAL_ARREST` (`STRONG` match).
  - **Threat Risk Index**: 85 / 100 (`HIGH`).
  - **Evidence Confidence**: `MEDIUM` (Corroborated message and payment signals).
  - **Intervention Decision**: `PRE_PAYMENT_INTERVENTION` (10s friction, payment blocked).

---

## 4. Test Invariant Summary

1. **Zero External Dependency**: Pure deterministic Python with Pydantic schemas.
2. **Alert Fatigue Prevention**: Benign and ambiguous scenarios (01 and 05) produced **ZERO** disruptive friction.
3. **Targeted Protection**: Harmful journeys (02, 03, 04, 06) were caught before funds moved with **10-second step-up cooling friction**.
