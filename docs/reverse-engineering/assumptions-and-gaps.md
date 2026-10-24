# Assumptions, Technical Gaps & Operational Realities

This document records technical assumptions, identifies gaps between proprietary public platforms (RBIH DPIP & MuleHunter) and our independent ScamGraph AI platform, and details mitigation strategies.

## Classification Taxonomy
- **`DOCUMENTED`**: Facts established through public whitepapers or project briefs.
- **`INFERRED`**: Inferences regarding system behavior and architectural constraints.
- **`PROPOSED`**: Mitigations, design choices, and fallbacks implemented in ScamGraph AI.

---

## 1. Technical Assumptions & Rationale

| Assumption ID | Description | Classification | Engineering Rationale & Mitigation |
|---|---|---|---|
| **ASM-01** | Identifier Hashing requires Keyed HMAC | **`INFERRED`** | Plain SHA-256 on phone numbers (only $10^{10}$ combinations) or 10-digit Indian bank account numbers allows trivial rainbow table and brute-force enumeration attacks. ScamGraph uses HMAC-SHA-256 with key rotation and version prefixing. |
| **ASM-02** | Dispute Does Not Imply Innocence | **`DOCUMENTED`** / **`INFERRED`** | Filing a dispute cannot immediately erase evidence; criminal rings frequently attempt to dispute accounts to buy time. ScamGraph transitions the state to `DISPUTED`, retains evidence, but tags downstream risk scores with `is_disputed: true`. |
| **ASM-03** | Graph Traversal Must Be Bounded | **`INFERRED`** | Financial transaction graphs exhibit small-world phenomena and power-law degree distributions. Unbounded depth traversal creates exponential path explosions. ScamGraph strictly caps traversal at depth $\le 5$ and page size $\le 100$. |
| **ASM-04** | Propagated Risk Must Decay | **`INFERRED`** | An innocent small merchant who receives payment from a mule account must not receive the exact same 1.0 fraud score as the mule. ScamGraph implements geometric distance decay ($\lambda = 0.5$) and segregates `direct_risk` from `propagated_risk`. |
| **ASM-05** | Real Transaction Data Cannot Be Fabricated | **`DOCUMENTED`** | Regulatory compliance (DPDP Act 2023, RBI Master Directions) strictly prohibits using or storing real unmasked customer financial records in development. ScamGraph uses strictly synthetic transaction datasets. |

---

## 2. Gaps Between Proprietary Systems and Independent ScamGraph

### 2.1 Model Weights & Production Features (MuleHunter)
- **The Gap**: RBIH has proprietary access to nationwide transaction ledgers across participating banks, from which it derived its 19 behavioral patterns and trained internal production models. Model weights, hyper-parameters, and exact threshold values are confidential.
- **ScamGraph Mitigation**:
  1. We implement the 19 behavioral pattern features using formal financial engineering definitions (velocity, turnover ratio, dwell time, churn, dormancy-burst).
  2. We provide an interpretable, transparent Rules Engine with configurable thresholds.
  3. We provide a supervised ML pipeline (Random Forest / GBDT) trained on verifiable synthetic/open benchmarks, reporting honest precision, recall, and calibration rather than claiming arbitrary 90%+ performance.

### 2.2 Network Interoperability & Identity Proofing (DPIP)
- **The Gap**: DPIP operates as a closed consortium accessible only to regulated entities via RBI/NPCI infrastructure (INFINET/SFMS) with cryptographic participant signing.
- **ScamGraph Mitigation**:
  1. We provide standard RESTful microservices with API key and HMAC header verification.
  2. We model institutional tenancy (`reporting_org`, `caller_org`) and enforce role-based access control (RBAC).

### 2.3 Live Graph Scalability & In-Memory Fallback
- **The Gap**: Production bank graphs contain hundreds of millions of nodes requiring distributed graph databases (Neo4j Enterprise, TigerGraph, Amazon Neptune).
- **ScamGraph Mitigation**:
  1. ScamGraph is architected to operate with Neo4j when available.
  2. ScamGraph also provides a robust, zero-dependency in-memory graph repository using Python sets, BFS, and NetworkX, ensuring full functionality and deterministic test pass rates even when Docker or Neo4j are not running locally.

---

## 3. Graceful Degradation Strategy

| Failure Scenario | Subsystem Impact | ScamGraph Graceful Behavior |
|---|---|---|
| Neo4j Unavailable | Graph Correlation | Falls back to in-memory Graph Repository; returns local entity relations; sets `graph_status: "in_memory_fallback"`. |
| ML Model Artifact Missing | Mule Detection | Falls back to deterministic Baseline Rules Engine; sets `model_mode: "rules_only"`. |
| External Threat Intel Unreachable | TinyFish / DNS | Returns local heuristics & lexical pattern matching; sets `url_analysis: "lexical_only"`. |
| Incomplete Transaction Context | Mule Feature Extractor | Flags missing features, returns uncertainty scores, avoids zero-risk assumptions; sets `uncertainty_level: "HIGH"`. |
