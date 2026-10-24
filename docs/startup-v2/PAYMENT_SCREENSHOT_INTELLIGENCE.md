# Payment Screenshot Intelligence Specification

## 1. Extraction Scope
Extracts transaction evidence from post-payment screenshots (PhonePe, Google Pay, Paytm, BHIM, bank net-banking receipts).

### Extracted Dimensions:
- **Amount & Currency**: Normalized numeric value (e.g., `₹25,000` $\to$ `25000.0 INR`).
- **Payee VPA / Identifier**: Canonical payment recipient handle.
- **Payee Name Claim**: Display name on receipt (recorded as user claim).
- **Payment Reference / UTR**: Tokenized bank reference identifier.
- **Payment Status Claim**: Explicit status on image (`SUCCESSFUL`, `COMPLETED`, `PENDING`, `FAILED`).

## 2. Verification State & Rescue Integration
- **Unverified Status**: Screenshot text claiming "Paid Successfully" is user-reported evidence, **never** bank-verified transaction confirmation (`verification_state = "UNVERIFIED"`).
- **Direct Rescue Feed**: Automatic conversion to `LossEvent` (Prompt 16) for triage, official complaint packaging (NCRP 1930 / cybercrime.gov.in), and emergency action planning.
- **Deduplication**: In-memory cache hashes `(amount, reference_id, vpa)` to avoid creating duplicate loss events when the same screenshot is repeatedly submitted.
