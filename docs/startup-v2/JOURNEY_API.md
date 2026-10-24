# Journey, Network & Campaign Intelligence APIs

## 1. Journey Stage Intelligence
- Exposes progression without future leakage: evaluated strictly based on evidence available at request time.
- Returns `current_stage`, `monetization_status`, `payment_proximity`, and `urgency`.
- Distinguishes early grooming (`INITIAL_CONTACT`, `TRUST_BUILDING`) from imminent theft (`CREDENTIAL_HARVESTING`, `PAYMENT_EXTRACTION`).

## 2. Network Intelligence Contract
- Maps infrastructure linkages: shared hosting, domain registrar overlap, common mule account clusters.
- Emits cross-incident correlation indicators without disclosing reporter identifiers.

## 3. Campaign & Outbreak Intelligence
- Real-time syndication feed for fraud detection operations.
- Outbreak thresholds flag surges when velocity exceeds 3 standard deviations above baseline.
