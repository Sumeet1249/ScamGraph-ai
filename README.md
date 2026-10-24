# ScamGraph AI

> **AI-Driven Scam-Journey Recognition & Multi-Signal Correlation for UPI, Banking, and Wallet Contexts**

---

## 1. Project Goal & Unique Purpose

ScamGraph AI does **NOT** replace PhonePe, Google Pay, Paytm, banks, or NPCI UPI fraud engines.

Existing fraud systems evaluate transactions at the point of settlement (e.g., unusual amount, new beneficiary, device velocity). In contrast, ScamGraph AI’s unique purpose is to **reconstruct and analyze the psychological and infrastructural scam journey** that precedes the payment intent.

### The Scam Progression

```ini {"metadata":"[object Object]"}
[Unknown Contact]
       │
       ▼
[Impersonation (Bank / Utility / Courier / Gov)]
       │
       ▼
[Urgency / Fear / Coercion]
       │
       ▼
[Suspicious URL / Phishing Landing Page]
       │
       ▼
[Credential / OTP / Remote App Request]
       │
       ▼
[Payment / Collect Request / QR Code]
       │
       ▼
[UPI / Payment Intent Execution]
```

ScamGraph AI correlates:

1. **Semantic Message Signals**: Urgency, fear, coercion, impersonation keywords, multilingual dialect nuances.
2. **URL / Web Evidence**: Domain age, registrar anomalies, hosting telemetry via **TinyFish API**.
3. **Payment Context**: VPA format analysis, mismatch between purported entity and recipient handle.
4. **Temporal Event Sequence**: Speed of transition across grooming stages.
5. **Infrastructure Relationships**: Shared hosting, IPs, DNS clusters, reused sender numbers.
6. **Historical Incidents**: Graph-linked prior journeys and reported scam instances.
7. **Campaign Similarity**: High-dimensional vector cosine similarity using multilingual sentence embeddings.

---

## 2. Core Architectural Principles

- **No Single Model Declares Fraud**: No LLM or ML classifier is permitted to unilaterally label an interaction as fraudulent. Models solely generate typed, weighted **evidence signals**.
- **Dual-Axis Assessment**:
   - **Risk Level**: `LOW` | `MEDIUM` | `HIGH`
   - **Evidence Confidence**: `LOW` | `MEDIUM` | `HIGH`

- __Explicit `INSUFFICIENT_EVIDENCE` Support__: When data points are sparse or inconclusive, the system defaults to `INSUFFICIENT_EVIDENCE` rather than guessing or causing false alarms.
- **Adaptive Intervention**: Dynamically tailors defensive friction (silent monitoring, contextual warning banners, transaction delay, or intent block) to reduce user alert fatigue.

---

## 3. Technology Stack

- **Frontend**: Next.js, TypeScript, Tailwind CSS, Cytoscape.js
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (asyncpg)
- **Databases**: PostgreSQL (relational event logs) + pgvector (embedding similarity), Neo4j 5.x (journey graph & entity fusion)
- **AI & NLP**: `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`), scikit-learn, LightGBM/XGBoost
- **External Investigation**: TinyFish API
- **Infrastructure**: Docker Compose (clean, minimal footprint — no Kafka, Kubernetes, or microservice bloat)

---

## 4. Monorepo Directory Structure

Every directory in the repository has a focused, single responsibility:

```ini {"metadata":"[object Object]"}
ScamGraph-AI/
├── apps/
│   └── web/
│       ├── app/
│       │   ├── page.tsx
│       │   ├── investigate/
│       │   ├── incidents/
│       │   ├── campaigns/
│       │   ├── command/
│       │   └── lab/
│       ├── components/
│       │   ├── investigation/
│       │   ├── graph/
│       │   ├── timeline/
│       │   ├── risk/
│       │   └── evidence/
│       └── lib/
├── services/
│   ├── api/
│   │   └── app/
│   │       ├── main.py
│   │       ├── api/
│   │       ├── core/
│   │       ├── models/
│   │       └── schemas/
│   ├── investigation/
│   │   ├── tinyfish/
│   │   ├── url_analysis/
│   │   ├── dns/
│   │   ├── rdap/
│   │   ├── tls/
│   │   └── extractors/
│   ├── pattern-engine/
│   │   ├── patterns/
│   │   ├── temporal/
│   │   ├── semantic/
│   │   └── matcher/
│   └── graph-engine/
│       ├── neo4j/
│       ├── correlation/
│       ├── campaigns/
│       └── algorithms/
├── packages/
│   └── schemas/
├── ml/
│   ├── message/
│   ├── url/
│   ├── payment/
│   ├── embeddings/
│   ├── emerging/
│   └── evaluation/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── synthetic/
│   ├── benchmark/
│   └── patterns/
├── references/
│   ├── README.md
│   └── github/
├── infrastructure/
│   ├── postgres/
│   └── neo4j/
├── scripts/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── scenarios/
│   └── benchmark/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE_RULES.md
│   ├── DATA_MODEL.md
│   ├── PATTERN_ENGINE.md
│   ├── EVIDENCE_MODEL.md
│   ├── REFERENCE_REPOS.md
│   ├── REFERENCE_ANALYSIS.md
│   ├── OPEN_SOURCE_CAPABILITY_MATRIX.md
│   ├── FINAL_INTEGRATION_PLAN.md
│   ├── INTEGRATION_PLAN.md
│   └── DEMO.md
├── docker-compose.yml
├── .env.example
└── README.md
```

### Directory Explanations

| Path | Purpose & Responsibility |
|---|---|
| `apps/web/app/` | Next.js App Router pages: `investigate`, `incidents`, `campaigns`, `command`, `lab` |
| `apps/web/components/` | Modular UI components: `graph` (Cytoscape.js), `timeline`, `risk`, `evidence`, and `investigation` |
| `apps/web/lib/` | Frontend utility functions, API clients, and graph visualization layout configs |
| `services/api/app/` | FastAPI application structure (`main.py`, `api/`, `core/`, `models/`, `schemas/`) |
| `services/investigation/` | External intelligence services: TinyFish integration, URL analysis, DNS, RDAP, TLS, and extractors |
| `services/pattern-engine/` | Intelligence core: declarative patterns, temporal progression, multilingual semantics, and matcher |
| `services/graph-engine/` | Neo4j graph driver: Cypher queries, entity correlation, campaign graphs, and network algorithms |
| `packages/schemas/` | Shared canonical Pydantic and TypeScript data contracts across frontend and backend |
| `ml/` | ML models: `message/`, `url/`, `payment/`, `embeddings/`, `emerging/` variants, and `evaluation/` |
| `data/` | Data pipeline folders: `raw/`, `processed/`, `synthetic/`, `benchmark/`, and `patterns/` |
| `references/` | Domain documentation and curated GitHub open-source reference patterns |
| `infrastructure/` | Postgres (with pgvector) and Neo4j initial schemas and DB scripts |
| `scripts/` | Developer operations, seeding utilities, and benchmark runners |
| `tests/` | Granular test suites: `unit/`, `integration/`, `scenarios/`, and `benchmark/` |
| `docs/` | Architecture specs, architectural rules constitution, data model, pattern engine, evidence model, reference repos, and demo guide |

---

## 5. Getting Started (Scaffolding Phase)

### 5.1 Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 5.2 Start Local Database Infrastructure

```bash {"metadata":"[object Object]"}
# Copy environment variables
cp .env.example .env

# Start PostgreSQL (with pgvector) and Neo4j
docker compose up -d postgres neo4j
```

Neo4j Browser will be available at `http://localhost:7474` and PostgreSQL on port `5432`.

---

## 6. RBIH DPIP & MuleHunter Clean-Room Implementation

ScamGraph AI features an independent clean-room implementation inspired by the publicly documented capabilities of the Reserve Bank Innovation Hub (RBIH):

### 6.1 Subsystems Overview

1. **Module A — Smart Registry (DPIP Specification)**:
   - **Keyed Fingerprinting**: HMAC-SHA-256 with key rotation (`v1`, `v0`) preventing brute-force dictionary attacks against low-entropy phone numbers and bank accounts.
   - **Lifecycle State Machine**: `REPORTED` &rarr; `UNDER_REVIEW` &rarr; `CONFIRMED` / `REJECTED` / `DISPUTED` / `REVOKED`.
   - **Real-Time Screening**: Exact & prefix matching with safe masked identifier previews.
   - **Dispute & Revocation Workflow**: Structured dispute handling with authorized revocation suppressing false-positive screening.
   - **Immutable Audit Trail**: SHA-256 hash-chained immutable audit records for regulatory oversight.

2. **Module B — Mule Intelligence Engine (MuleHunter Specification)**:
   - **19 Behavioral Features**: Extracting peak-1h velocity, 24h velocity, volume turnover, dwell time, rapid churn (&lt;5 min), counterparty diversity, fan-in/fan-out counts & ratios, account age, dormancy bursts, odd-hours ratio, round-amount chunking, balance extraction, micro-test spikes, identical repetitions, UPI handles, and registry match.
   - **Heuristic Rules Engine**: 10 transparent heuristic rules with exponential risk saturation (`1 - exp(-1.25 * raw_score)`).
   - **Supervised ML Pipeline**: Calibrated `HistGradientBoostingClassifier` with time-aware cross-validation and honest metrics (PR-AUC, ROC-AUC, Brier score).
   - **Rules Score Floor**: Guarantees confirmed heuristic rule violations are never diluted by uncalibrated ML scores (`max(rules_score, hybrid_score)` when `rules_score >= 0.60`).
   - **Action Guidance**: `FREEZE_SUSPEND`, `STEP_UP_KYC`, `MONITOR`, and `ALLOW`.

3. **Module C — Graph Correlation Engine**:
   - **Multi-Hop Flow Tracing**: Explores directed transaction flows up to 5 hops with dwell-time analysis.
   - **Circular Flow Detection**: Discovers closed laundering wash loops (`is_circular: true`).
   - **Cluster Discovery**: Weakly connected components and shared-identifier rings (phone/device hardware overlap).
   - **Explainable Risk Propagation**: Geometric distance decay ($\text{Risk} = \text{Risk}_{seed} \cdot \lambda^{hops}$, with $\lambda = 0.5$), strictly segregating direct from propagated risk.

4. **Module D — Unified ScamGraph Risk Engine**:
   - **Multi-Signal Fusion**: Blends Smart Registry (0.35), Mule Intelligence (0.30), Graph Correlation (0.20), and Semantic Message NLP (0.15).
   - **Degraded-Mode Weight Redistribution**: Dynamically renormalizes weights when subsystems lack historical telemetry, explicitly logging degraded state.

### 6.2 Reverse-Engineering Documentation

- [Source Inventory & Public Citations](docs/reverse-engineering/source-inventory.md)
- [Capability & Implementation Matrix](docs/reverse-engineering/capability-matrix.md)
- [System Architecture Findings](docs/reverse-engineering/architecture-findings.md)
- [API Contract Findings](docs/reverse-engineering/api-contract-findings.md)
- [Assumptions & Technical Gaps](docs/reverse-engineering/assumptions-and-gaps.md)
- [Security & Privacy Blueprint](docs/reverse-engineering/security-and-privacy.md)

### 6.3 Automated Test Verification

Run all clean-room module test suites:
```bash
python -m pytest tests/unit/test_smart_registry.py tests/unit/test_mule_engine.py tests/unit/test_graph_correlation.py tests/unit/test_unified_risk_engine.py -v
```
Build Next.js web application:
```bash
cd apps/web && npm run build
```
