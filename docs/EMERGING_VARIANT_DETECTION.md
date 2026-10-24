# Emerging Variant Detection V1

## Executive Summary

Traditional fraud and phishing detection systems rely heavily on static Indicators of Compromise (IOCs)—blacklisted phone numbers, malicious domain lists, IP blocks, and reported mule bank accounts/VPAs. 

In modern fraud syndicates (especially across India and SE Asia), **adversaries treat surface infrastructure as disposable**. A single syndicate rotates through hundreds of fresh virtual numbers, newly registered typosquatted domains, and freshly provisioned mule UPI handles every week. Consequently, naive IOC-based matching experiences severe blind spots.

**EmergingVariantDetector** in ScamGraph AI solves this fundamental challenge. It evaluates incoming incidents across two decoupled axes:
1. **Endpoint Identifier Overlap** (Phones, Domains, IPs, VPAs/Bank Accounts).
2. **Structural Workflow Invariance** (Multi-stage grooming sequence, semantic intent embeddings, coercive tactics, and behavioral patterns).

When an incident exhibits **zero identifier overlap** but matches the **structural operational blueprint** of known fraud campaigns, the engine classifies it as `POSSIBLE_EMERGING_CAMPAIGN` or `MUTATED_VARIANT`, alerting security teams to an active mutation in real-time.

---

## 1. Decision Matrix & Classification States

The detector maps every interaction into one of five definitive statuses (`EmergingStatus`):

```
                               ┌────────────────────────────────────────┐
                               │  Incoming Incident + Fingerprint V2    │
                               └───────────────────┬────────────────────┘
                                                   │
                                     [Event Count < Min Events?]
                                           /               \
                                         YES                NO
                                         /                    \
                         ┌───────────────────────┐             ▼
                         │ INSUFFICIENT_EVIDENCE │      [Any Known Identifiers?]
                         └───────────────────────┘           /            \
                                                           YES             NO
                                                           /                 \
                                   ┌───────────────────────┐                  ▼
                                   │     KNOWN_PATTERN     │         [Workflow Match?]
                                   └───────────────────────┘          /              \
                                                                    HIGH             LOW
                                                                    /                  \
                                          ┌────────────────────────────┐    ┌──────────────────────┐
                                          │ POSSIBLE_EMERGING_CAMPAIGN │    │ NO_SIGNIFICANT_MATCH │
                                          │      / MUTATED_VARIANT     │    └──────────────────────┘
                                          └────────────────────────────┘
```

| Status | Condition | Description |
|---|---|---|
| `KNOWN_PATTERN` | Known phone, domain, IP, or VPA matches historical scam infrastructure **AND** pattern or similarity is high. | The adversary is reusing existing, documented infrastructure. |
| `MUTATED_VARIANT` | Zero identifier overlap, but composite fingerprint similarity $\ge 0.65$ or strong semantic and behavioral pattern alignment. | The adversary has swapped identifiers while retaining the core operational blueprint. |
| `POSSIBLE_EMERGING_CAMPAIGN` | Zero identifier overlap, semantic alignment $\ge 0.70$, temporal grooming pace between 15s–1200s, and multi-stage pattern match present. | **Hero match**: A newly launched, coordinated syndicate mutation evading traditional blacklists. |
| `NO_SIGNIFICANT_MATCH` | Zero identifier overlap and composite similarity $< 0.40$. | Normal, benign activities (e.g. e-commerce payments, utility bills) or unrelated benign interactions. |
| `INSUFFICIENT_EVIDENCE` | Event count $< 2$ with no recognized patterns or corroborating signals. | Sparse telemetry; prevents premature false alarms. |

---

## 2. Configuration (`config/emerging_variant.yaml`)

All detection thresholds and operational bounds are externally configurable:

```yaml
version: "1.0"

thresholds:
  mutated_variant_threshold: 0.65
  known_pattern_similarity_threshold: 0.80
  semantic_workflow_threshold: 0.70
  journey_workflow_threshold: 0.70
  no_match_threshold: 0.40
  min_events_for_evaluation: 2

identifiers:
  check_phone: true
  check_domain: true
  check_vpa: true
  check_ip: true
  check_bank_account: true

temporal_bounds:
  min_grooming_seconds: 15
  max_grooming_seconds: 1200
```

---

## 3. Integration with ScamFingerprintV2 & Neo4j Analytics

When evaluating an incoming incident against historical incidents:
1. `EmergingVariantDetector` utilizes `ScamFingerprintSimilarityEngine` to compute 5-dimensional pairwise similarity against historical seed fingerprints:
   - **Semantic vector cosine similarity** (via BGE-M3 or Multilingual-E5 embeddings).
   - **Journey sequence alignment** (tolerant of slight reorderings/insertions).
   - **Infrastructure structural features** (URL lexical attributes, TinyFish DOM observations).
   - **Payment profiles** (VPA prefixes, transaction channels).
   - **Pattern rule overlap**.
2. If the incident matches a candidate campaign community discovered via Neo4j Graph Analytics (Step 24), the matched campaign community ID (`matched_campaign`) is attributed directly in the report.

---

## 4. Hero Scenario Walkthrough

### Scenario Comparison:
- **Historical Seed (Incident A)**:
  - Brand: State Bank of India (SBI)
  - Phone: `+91-9876543210`
  - Phishing Domain: `sbi-kyc-update.xyz`
  - Payment VPA: `sbi.fraud@ybl`
  - Journey: `INITIAL_CONTACT` $\to$ `IMPERSONATION` $\to$ `SUSPICIOUS_LINK` $\to$ `CREDENTIAL_SUBMIT` $\to$ `PAYMENT_REQUEST`

- **Incoming Incident (Incident B)**:
  - Brand: HDFC Bank
  - Phone: `+91-9123456789` (*Unseen*)
  - Phishing Domain: `hdfc-netbanking-verify.top` (*Unseen*)
  - Payment VPA: `hdfc.verify@paytm` (*Unseen*)
  - Journey: `INITIAL_CONTACT` $\to$ `IMPERSONATION` $\to$ `SUSPICIOUS_LINK` $\to$ `CREDENTIAL_SUBMIT` $\to$ `PAYMENT_REQUEST`

### Evaluation Output:
```json
{
  "incident_id": "inc_hdfc_new",
  "status": "POSSIBLE_EMERGING_CAMPAIGN",
  "identifier_match": {
    "phone_matched": false,
    "domain_matched": false,
    "payment_matched": false,
    "ip_matched": false,
    "has_any_match": false
  },
  "workflow_match": {
    "semantic_level": "HIGH",
    "temporal_level": "HIGH",
    "pattern_level": "HIGH",
    "composite_similarity": 0.78
  },
  "matched_incident_id": "inc_sbi_seed",
  "matched_campaign": "campaign_bank_phish_cluster_01",
  "verdict_explanation": "HERO MATCH: All identifiers (Phone, Domain, VPA) are brand-new/unseen, yet the psychological coercion, temporal transition speed, and multi-stage workflow exhibit high structural similarity to known banking scam campaigns."
}
```

---

## 5. Verification & Test Coverage

The test suite covers all matrix branches:
- `test_backward_compatibility_v1_fingerprint`: Verifies existing Step 21 signatures and `lab.py` endpoints.
- `test_hero_mutated_variant_with_scam_fingerprint_v2`: Verifies zero identifier overlap + invariant workflow yielding `POSSIBLE_EMERGING_CAMPAIGN`.
- `test_known_pattern_with_recycled_infrastructure`: Verifies recycled burner numbers yielding `KNOWN_PATTERN`.
- `test_benign_normal_payment_yields_no_significant_match`: Verifies normal payment traffic yielding `NO_SIGNIFICANT_MATCH`.
- `test_sparse_telemetry_yields_insufficient_evidence`: Verifies single-event uncorroborated traffic yielding `INSUFFICIENT_EVIDENCE`.

Test suite: [tests/unit/test_emerging_variant_step26.py](file:///s:/ScamGraph-AI/tests/unit/test_emerging_variant_step26.py)
