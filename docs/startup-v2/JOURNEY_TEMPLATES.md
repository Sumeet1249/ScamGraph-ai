# ScamGraph AI — Scam Family Journey Templates & Transition Graphs

## 1. Overview
ScamGraph AI V2 maintains declarative, versioned journey templates representing the primary cyber-fraud typologies targeting Indian consumers.

---

## 2. Core Family Templates

### 1. `JOB_TASK` (Part-Time Job & Task Scam)
- **Typology**: Social media lure $\rightarrow$ YouTube like/review tasks $\rightarrow$ ₹150 profit $\rightarrow$ Telegram VIP group $\rightarrow$ escalating deposit tiers $\rightarrow$ blocked withdrawal $\rightarrow$ tax fee.
- **Expected Sequence**:
  $$\text{DISCOVERY} \rightarrow \text{CONTACT} \rightarrow \text{MIGRATION} \rightarrow \text{TRUST} \rightarrow \text{REWARD} \rightarrow \text{INITIAL\_PAYMENT} \rightarrow \text{ESCALATION} \rightarrow \text{BLOCK} \rightarrow \text{RECOVERY\_FEE} \rightarrow \text{EXIT}$$
- **Required Stages**: `CONTACT`, `INITIAL_PAYMENT`.
- **Allowed Transitions**:
  - `CONTACT` $\rightarrow$ `PLATFORM_MIGRATION`, `TRUST_BUILDING`
  - `PLATFORM_MIGRATION` $\rightarrow$ `TRUST_BUILDING`, `REWARD_OR_FAKE_PROFIT`
  - `REWARD_OR_FAKE_PROFIT` $\rightarrow$ `INITIAL_PAYMENT`
  - `INITIAL_PAYMENT` $\rightarrow$ `PAYMENT_ESCALATION`
  - `PAYMENT_ESCALATION` $\rightarrow$ `WITHDRAWAL_BLOCK` $\rightarrow$ `RECOVERY_FEE`

---

### 2. `INVESTMENT` (High-Return Trading Fraud)
- **Typology**: WhatsApp group lure $\rightarrow$ fake trading portal $\rightarrow$ demo balance $\rightarrow$ ₹10,000 initial transfer $\rightarrow$ fake dashboard profits $\rightarrow$ ₹50,000 top-up $\rightarrow$ 30% capital gains tax lock.
- **Expected Sequence**:
  $$\text{DISCOVERY} \rightarrow \text{CONTACT} \rightarrow \text{TRUST} \rightarrow \text{MIGRATION} \rightarrow \text{INITIAL\_PAYMENT} \rightarrow \text{REWARD} \rightarrow \text{ESCALATION} \rightarrow \text{BLOCK} \rightarrow \text{RECOVERY\_FEE}$$
- **Required Stages**: `CONTACT`, `INITIAL_PAYMENT`.

---

### 3. `DIGITAL_ARREST` (Law Enforcement Impersonation & Extortion)
- **Typology**: Cold call $\rightarrow$ fake CBI/Mumbai police claim $\rightarrow$ illegal drugs in intercepted parcel $\rightarrow$ non-bailable warrant $\rightarrow$ video-call confinement & room lock $\rightarrow$ asset verification transfer.
- **Expected Sequence**:
  $$\text{CONTACT} \rightarrow \text{IMPERSONATION} \rightarrow \text{URGENCY} \rightarrow \text{THREAT\_OR\_PRESSURE} \rightarrow \text{INITIAL\_PAYMENT} \rightarrow \text{ESCALATION}$$
- **Required Stages**: `CONTACT`, `IMPERSONATION`, `THREAT_OR_PRESSURE`.

---

### 4. `KYC_BANK` (Banking & Utility Impersonation)
- **Typology**: Urgency SMS ("Account will be blocked at 9:30 PM") $\rightarrow$ fake netbanking link $\rightarrow$ OTP requested $\rightarrow$ unauthorized account debit.
- **Expected Sequence**:
  $$\text{CONTACT} \rightarrow \text{IMPERSONATION} \rightarrow \text{URGENCY} \rightarrow \text{CREDENTIAL\_REQUEST} \rightarrow \text{INITIAL\_PAYMENT}$$
- **Required Stages**: `CONTACT`, `URGENCY`.

---

### 5. `FAKE_SUPPORT_REFUND` (Remote Access Support Scam)
- **Typology**: E-commerce/wallet refund offer $\rightarrow$ customer service impersonation $\rightarrow$ AnyDesk/QuickSupport installation $\rightarrow$ screen sharing $\rightarrow$ unauthorized fund debit.
- **Expected Sequence**:
  $$\text{CONTACT} \rightarrow \text{IMPERSONATION} \rightarrow \text{TRUST} \rightarrow \text{CREDENTIAL\_REQUEST} \rightarrow \text{INITIAL\_PAYMENT}$$
- **Required Stages**: `CONTACT`, `IMPERSONATION`.

---

## 3. Emerging / Unknown Journeys
When an observed stage sequence achieves $<0.45$ alignment against all registered templates:
- It is classified as **`UNKNOWN / EMERGING JOURNEY`**.
- The engine preserves all observed stages, tactics, and monetization statuses without forcing an incorrect classification.
- Flagged for automated clustering and emerging campaign pattern analysis.
