# ScamGraph AI — Psychological Tactic Annotation Guide

## 1. Purpose & Standards
This guide establishes operational standards for human analysts and automated LLM annotators labeling psychological manipulation tactics in multi-lingual scam datasets (English, Hindi, Hinglish).

---

## 2. Universal Annotation Principles

1. **Evidence-First Rule**: A tactic label MUST be backed by at least one explicit evidence text span. Do not annotate a tactic based on intuition alone.
2. **Context Negation Rule**: If a phrase contains tactic keywords in a protective, educational, or cautionary context (e.g. *"Never share your OTP"*), DO NOT annotate the tactic. Mark `is_negated: true` or suppress.
3. **Quoted Inquiry Rule**: When a victim asks *"Someone told me 'pay immediately or go to jail'. Is this real?"*, annotate the quoted text with `is_quoted: true` and attribute the speech to the external actor, NOT the victim.
4. **Speaker Role Distinction**:
   - `SUSPECTED_ACTOR` / `SCAMMER`: Primary target for manipulation tactics.
   - `VICTIM` / `USER`: Do not annotate actor tactics unless evaluating vulnerability signals.
   - `SYSTEM_NOTIFICATION`: Legitimate automated receipts or routine updates.

---

## 3. Detailed Tactic Guidelines & Examples

### 1. `CREDENTIAL_PRESSURE`
- **Definition**: Demanding one-time passwords, netbanking passwords, ATM PINs, or card CVVs.
- **Positive Example**: *"Please share the 6-digit OTP you received on your mobile to complete KYC."*
- **Negative Example**: *"Your OTP is 492019. Never share this code with anyone, including bank staff."*
- **Borderline Example**: *"Please enter your password on the login screen."* (Annotate ONLY if domain is unverified/suspicious).
- **Confusable With**: `REMOTE_ACCESS_PRESSURE` (differentiated by asking for codes vs asking for app installation).

### 2. `AUTHORITY`
- **Definition**: Actor invokes law enforcement, judicial, or governmental identity to enforce compliance.
- **Positive Example**: *"I am Inspector Rajesh Sharma calling from Mumbai Cyber Crime Branch regarding an FIR."*
- **Negative Example**: *"Cyber police advisory: Beware of fraudulent investment groups on Telegram."*
- **Borderline Example**: *"Customer service representative from SBI."* (Annotate as `IMPERSONATION` unless law/regulatory status is asserted).

### 3. `SECRECY`
- **Definition**: Explicitly instructing the victim not to consult family, friends, police, or bank staff.
- **Positive Example**: *"Do not discuss this case with anyone, not even your spouse, as it is a secret CBI operation."*
- **Negative Example**: *"Our enterprise non-disclosure agreement requires confidentiality."*

### 4. `ISOLATION`
- **Definition**: Coercively confining the victim to a call or physical room to prevent independent verification.
- **Positive Example**: *"Stay on this video call, do not disconnect, and lock the room door until clearance is given."*
- **Negative Example**: *"Please hold the line while I check your flight booking."*

### 5. `PAYMENT_PRESSURE`
- **Definition**: Urgently demanding an immediate money transfer, UPI payment, or deposit.
- **Positive Example**: *"Deposit ₹15,000 immediately to verify your clean status, or approve the UPI collect prompt."*
- **Negative Example**: *"Your monthly electricity bill of ₹650 is due on October 30."*

---

## 4. Multi-Annotator Agreement & Adjudication
- Inter-annotator agreement is measured using **Krippendorff's Alpha** ($\alpha \ge 0.80$ required for gold set).
- Disagreements between annotators are automatically routed to senior fraud review for authoritative adjudication.
