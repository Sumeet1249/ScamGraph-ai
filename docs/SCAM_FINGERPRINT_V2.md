# Scam Fingerprint V2 Architecture

## Overview

**ScamFingerprintV2** represents a multi-dimensional, structured representation of a scam or user journey. It solves a foundational challenge in fraud detection: **adversaries constantly rotate their surface infrastructure** (phone numbers, domains, UPI IDs, bank accounts), rendering naive identifier-matching ineffective.

By fusing semantic representation, temporal event sequence progression, infrastructure characteristics, payment intent signatures, and topological graph community context, ScamFingerprintV2 allows ScamGraph AI to recognize mutated campaign variants even with **zero entity overlap**.

---

## 1. Multi-Dimensional Vector & Structural Representation

Each `ScamFingerprintV2` contains five distinct dimensions:

```
                          ┌─────────────────────────────┐
                          │     ScamFingerprintV2       │
                          └──────────────┬──────────────┘
                                         │
       ┌─────────────────┬───────────────┼───────────────┬────────────────┐
       ▼                 ▼               ▼               ▼                ▼
┌──────────────┐ ┌───────────────┐ ┌───────────┐ ┌──────────────┐ ┌───────────────┐
│   Semantic   │ │    Journey    │ │  Pattern  │ │Infrastructure│ │    Payment    │
│  Embeddings  │ │Sequence & Gaps│ │ Indicators│ │  & TinyFish  │ │Entities & Mule│
└──────────────┘ └───────────────┘ └───────────┘ └──────────────┘ └───────────────┘
```

1. **Semantic Dimension (`semantic_weight = 0.30`)**:
   - Dense vector embeddings generated via `SemanticEncoder` (BAAI/bge-m3 or intfloat/multilingual-e5-small, configurable).
   - Captures deceptive intent, claimed brand identity, social engineering tactics (impersonation, urgency, fear, greed), and requested user actions.
   - Cosine similarity measures vector alignment.

2. **Temporal Journey Dimension (`journey_weight = 0.30`)**:
   - Ordered event sequence: e.g., `["INITIAL_CONTACT", "IMPERSONATION", "SUSPICIOUS_LINK", "OTP_REQUEST", "PAYMENT_REQUEST"]`.
   - Event time delta distribution (`event_time_gaps`).
   - Sequence similarity evaluated via Longest Common Subsequence (LCS) / Gestalt sequence matcher with tolerance for insertions and slight reorderings.

3. **Pattern / Behavioral Dimension (`pattern_weight = 0.15`)**:
   - Matched pattern indicators and behavioral rules.
   - Jaccard similarity across tactics, actions, and pattern rule codes.

4. **Infrastructure & Observation Dimension (`infrastructure_weight = 0.15`)**:
   - URL risk features (entropy, redirection depth, domain age) and TinyFish web investigation observations (e.g., credential harvesting forms, fake APK downloads).
   - Identifiers compared via Overlap/Jaccard; structural features compared via cosine/numeric proximity.

5. **Payment Dimension (`payment_weight = 0.10`)**:
   - Payment channels, UPI handles, IFSC prefixes, and beneficiary patterns.
   - Compares mule account structure, payment urgency, and transaction rail intent.

---

## 2. Configuration (`config/scam_fingerprint.yaml`)

Weights and thresholds are explicitly configurable, preventing opaque averages:

```yaml
version: "2.0"

weights:
  semantic_weight: 0.30
  journey_weight: 0.30
  pattern_weight: 0.15
  infrastructure_weight: 0.15
  payment_weight: 0.10

thresholds:
  exact_match_threshold: 0.90
  strong_variant_threshold: 0.75
  possible_variant_threshold: 0.55
  weak_variant_threshold: 0.35

sequence_matching:
  reordering_penalty: 0.10
  gap_penalty: 0.05
```

---

## 3. Sequence Alignment Algorithm

Standard string edit distance (Levenshtein) penalizes event reordering excessively. In real fraud campaigns, a scammer may send an APK download link *before* or *after* an initial phone call.

The engine uses a composite sequence matcher:
$$\text{Sim}_{\text{sequence}}(S_1, S_2) = 0.70 \times \text{GestaltRatio}(S_1, S_2) + 0.30 \times \text{Jaccard}(S_1, S_2)$$

This guarantees:
- Identical sequences score `1.0`.
- Sequences with minor reorderings or insertions retain high similarity ($\ge 0.75$).
- Inverted or completely distinct workflows are strongly penalized.

---

## 4. Hero Scenario: Mutated Bank KYC Campaign

```
[Incident 1: SBI KYC Scam]
- Claimed Identity: "State Bank of India"
- Phone: +91-9876543210
- Domain: sbi-kyc-update.xyz
- UPI: sbi.fraud@ybl
- Journey: CONTACT -> IMPERSONATION -> SUSPICIOUS_LINK -> CREDENTIAL_SUBMIT -> PAYMENT_REQUEST

[Incident 2: HDFC KYC Scam]
- Claimed Identity: "HDFC Bank"
- Phone: +91-9123456789
- Domain: hdfc-netbanking-verify.top
- UPI: hdfc.verify@paytm
- Journey: CONTACT -> IMPERSONATION -> SUSPICIOUS_LINK -> CREDENTIAL_SUBMIT -> PAYMENT_REQUEST

Result:
- Identifier Overlap: 0.00 (Completely fresh numbers, domains, and UPI IDs)
- Journey Sequence Similarity: 1.00
- Semantic Similarity: 0.88
- Pattern Match Similarity: 0.85
- Composite Similarity Score: 0.78 (Classified as STRONG MUTATED VARIANT)
```

In traditional fraud databases, Incident 2 would evade detection. In ScamGraph AI, the multi-dimensional fingerprint detects the mutation instantly.

---

## 5. Implementation References

- Schema: [packages/schemas/fingerprint.py](file:///s:/ScamGraph-AI/packages/schemas/fingerprint.py)
- Similarity Engine: [services/pattern-engine/semantic/similarity_engine.py](file:///s:/ScamGraph-AI/services/pattern-engine/semantic/similarity_engine.py)
- Builder: [services/pattern-engine/semantic/fingerprint_v2_builder.py](file:///s:/ScamGraph-AI/services/pattern-engine/semantic/fingerprint_v2_builder.py)
- Unit Tests: [tests/unit/test_scam_fingerprint_v2_step25.py](file:///s:/ScamGraph-AI/tests/unit/test_scam_fingerprint_v2_step25.py)
