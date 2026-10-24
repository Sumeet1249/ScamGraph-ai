# Architecture Findings & Target Technical Design

This document details the architectural findings derived from public evidence and specifies the target clean-room architecture for ScamGraph AI.

## Architectural Classification

- **`DOCUMENTED`**: Architectural components confirmed in public documentation (Central Smart Registry, Multi-tier Mule Detection, Shared Intelligence Platform).
- **`OBSERVED`**: Observed UI/API workflows (Interactive multi-hop node visualizers, dispute submission dialogs).
- **`INFERRED`**: Technical necessity (Separation of raw PII from keyed cryptographic fingerprints, distance-based decay in graph risk propagation).
- **`PROPOSED`**: ScamGraph AI's modular four-layer architecture.

---

## 1. High-Level Target Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │               ScamGraph Investigation UI               │
                    │   (Unified Dashboard, Registry, MuleHunter, Graph)    │
                    └───────────────────────────┬────────────────────────────┘
                                                │ REST / JSON
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                       ScamGraph Unified Risk Engine (Module D)                            │
│  Orchestrates Signals, Applies Fusion Matrix, Resolves Correlations, Assigns Actions      │
└───┬────────────────────────────┬─────────────────────────────┬──────────────────────────┬──┘
    │                            │                             │                          │
    ▼                            ▼                             ▼                          ▼
┌──────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐  ┌──────────────────────┐
│  Smart Registry      │  │  Mule Intelligence    │  │  Graph Correlation    │  │  Existing ScamGraph  │
│  (Module A)          │  │  (Module B)           │  │  (Module C)           │  │  Classifier / NLP    │
│                      │  │                       │  │                       │  │  (Pre-existing)      │
│ • Normalized Tokens  │  │ • 19 Behavioral       │  │ • Multi-Hop Paths     │  │ • Semantic Urgency   │
│ • Keyed HMAC-SHA-256 │  │   Feature Pipeline    │  │ • Fan-In / Fan-Out    │  │ • Impersonation NLP  │
│ • State Machine      │  │ • Interpretable Rules │  │ • Circular Fund Flows │  │ • Phishing URL/DNS   │
│ • Audit & Dispute    │  │ • Supervised Model    │  │ • Weakly Connected    │  │ • TinyFish Web       │
│ • Screening Engine   │  │ • Calibration Metrics │  │   Components (WCC)    │  │   Telemetry          │
│                      │  │ • Drift Monitoring    │  │ • Distance Decay Risk │  │                      │
└──────────────────────┘  └───────────────────────┘  └───────────────────────┘  └──────────────────────┘
```

---

## 2. Module A: Smart Registry Architecture

### Core Responsibilities
1. **Identifier Normalization**: Canonicalize typed identifiers (E.164 phone numbers, lowercase domain/URLs, standard UPI handles `@okaxis`, `@okhdfcbank`, bank IFSC+Account combinations) before hashing.
2. **Keyed HMAC-SHA-256 Fingerprinting**: Protect against offline dictionary attacks on low-entropy phone numbers and VPAs using an external secret key and explicit key versioning (`v1`, `v2`).
3. **Report Lifecycle State Machine**:
   - `REPORTED`: Submitted by reporting entity with initial evidence.
   - `UNDER_REVIEW`: Acknowledged by compliance or pending human review.
   - `CONFIRMED`: Verified fraud/mule identifier, eligible for blocking/screening alerts.
   - `REJECTED`: Insufficient evidence or false positive upon initial intake.
   - `DISPUTED`: Contested by target entity or counterparty bank; actively under re-investigation.
   - `REVOKED`: Withdrawn by reporting entity; historical audit record preserved, but active screening hits are suppressed.
4. **Append-Only Audit Log**: Every report modification, dispute status update, and revocation is stored as an immutable audit event with actor, timestamp, and justification.

---

## 3. Module B: Mule Intelligence Engine Architecture

### Core Responsibilities
1. **Transaction Schema Validation**: Validates transactions with strict checks for negative amounts, future timestamps, missing counterparties, and duplicate IDs.
2. **19 Behavioral Feature Extractors** (Inspired by documented 19 mule patterns):
   - `FEAT-01`: Transaction Velocity (1h, 24h count).
   - `FEAT-02`: Volume Turnover (Total Credits vs. Total Debits ratio).
   - `FEAT-03`: Rapid Pass-Through / Churn (Average dwell time between credit and debit < 5 minutes).
   - `FEAT-04`: Counterparty Diversity Ratio (Unique sending counterparties / total transactions).
   - `FEAT-05`: Fan-In Degree (High unique incoming transactions converging on single account).
   - `FEAT-06`: Fan-Out Degree (Single account dispersing to multiple destination wallets/accounts).
   - `FEAT-07`: Account Age / Dormancy-Burst Indicator (Sudden high transaction volume on newly created or previously dormant account).
   - `FEAT-08`: Odd-Hour Spikes (High ratio of transactions between 12 AM and 5 AM).
   - `FEAT-09`: Round-Amount Chunking (e.g., repeatedly transferring ₹9,999 or ₹49,999 to bypass reporting limits).
   - `FEAT-10`: Immediate Full Balance Extraction (Account balance dropping to near zero within minutes of credit).
   - `FEAT-11`: UPI Handle Hopping (Account linked to multiple rapidly cycling VPAs).
   - `FEAT-12`: High Net Inflow Velocity.
   - `FEAT-13`: Low Average Holding Balance relative to transaction throughput.
   - `FEAT-14`: Geographically dispersed counterparty origins.
   - `FEAT-15`: Micro-credit test transaction followed immediately by high-value spike.
   - `FEAT-16`: Unbalanced Inbound/Outbound Transaction Count.
   - `FEAT-17`: Repeated identical transaction values.
   - `FEAT-18`: High-risk payment channel concentration (UPI collect requests vs peer-to-peer).
   - `FEAT-19`: Centralized suspect registry indicator match.
3. **Dual Decision Layer**:
   - *Baseline Rules Engine*: Fully transparent, configurable threshold rules producing named reason codes (e.g., `RULE_RAPID_PASS_THROUGH`, `RULE_DORMANCY_BURST`).
   - *Supervised ML Model*: Gradient-boosted / ensemble classifier evaluated on time-aware splits, reporting honest Precision, Recall, PR-AUC, and calibration curves.
4. **Human-in-the-Loop & Escalation**: Returns calibrated risk bands (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) with recommended disposition (`ALLOW`, `MONITOR`, `STEP_UP_KYC`, `FREEZE_SUSPEND`).

---

## 4. Module C: Graph Correlation Engine Architecture

### Core Responsibilities
1. **Unified Graph Topology**:
   - Nodes: `Account`, `UPI_VPA`, `Phone`, `Device`, `IP`, `URL`, `Domain`, `Report`, `Incident`.
   - Edges: `SENT_TO`, `RECEIVED_FROM`, `USES_IDENTIFIER`, `USED_DEVICE`, `ACCESSED_FROM`, `LINKED_TO_REPORT`.
2. **Transaction Flow Algorithms**:
   - Multi-Hop Path Search (bounded depth $\le 5$ to prevent combinatorial explosion).
   - Fan-In / Fan-Out Detection (disproportionate in-degree vs out-degree hubs).
   - Circular Fund Flow Detection (cycles where funds return to source or upstream ring members).
   - Rapid Layering Path Detection (chains of transactions occurring within tight temporal windows).
3. **Connected Components & Clustering**:
   - Weakly Connected Components (WCC) over bipartite incident/entity relationships.
   - Candidate Campaign Community identification.
4. **Transparent Risk Propagation**:
   - Baseline risk assigned to confirmed registry reports and validated scam incidents ($R_0 \in [0, 1]$).
   - Propagation formula:
     $$R(v) = \max_{u \in \text{neighbors}} \left( R(u) \times \lambda^{\text{dist}(u, v)} \times W_{e} \times T(t) \right)$$
     where $\lambda = 0.5$ (distance decay factor), $W_e$ is relationship strength, and $T(t)$ is temporal recency decay.
   - Direct risk is strictly segregated from propagated risk in API responses to protect innocent parties interacting with a compromised counterparty.
   - Revocation / dispute of an upstream report triggers instant risk recalculation and audit logging.

---

## 5. Module D: Unified ScamGraph Risk Engine

### Core Responsibilities
1. **Multi-Signal Orchestration**:
   - Aggregates registry screening results, mule account scores, graph correlation paths, and semantic message NLP.
2. **Correlation-Aware Fusion**:
   - Prevents double-counting correlated signals (e.g. if the same phone number appears in both the registry and a graph cluster).
3. **Degraded Mode Resilience**:
   - Explicitly flags when a subsystem (e.g., external graph or ML model) is unavailable or unpopulated, returning `is_degraded: true` with a calculated partial risk rather than silently treating missing signals as zero risk.
4. **Actionable Recommendations**:
   - Generates unambiguous action directives (`ALLOW`, `STEP_UP_VERIFICATION`, `FLAG_FOR_REVIEW`, `ESCALATE`) mapped to explainable evidence codes.
