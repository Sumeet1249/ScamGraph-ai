# ScamGraph AI — System Architecture

## 1. Executive Summary & Purpose

**ScamGraph AI** is an AI-driven scam-pattern-recognition system specifically designed for UPI, banking, and digital wallet contexts.

> **Core Philosophy**: ScamGraph AI does **NOT** replace PhonePe, Google Pay, Paytm, bank fraud engines, or NPCI transaction filters.
>
> Its unique purpose is to **reconstruct, correlate, and analyze the end-to-end scam journey** that grooms and manipulates a user toward making an unauthorized payment or sharing credentials.

### Example Scam Journey Progression

```ini {"metadata":"[object Object]"}
[Unknown Contact]
       │
       ▼
[Impersonation (Bank/Courier/Utility/Govt)]
       │
       ▼
[Urgency / Fear / Psychological Pressure]
       │
       ▼
[Suspicious URL / Phishing Landing Page]
       │
       ▼
[Credential / OTP / Remote Access App Request]
       │
       ▼
[Payment Request / Collect Request / QR Code]
       │
       ▼
[UPI / Payment Intent Execution]
```

---

## 2. Fundamental Architectural Principles

### 2.1 No Single Model Declares Fraud

**Strict Rule**: No single LLM, ML model, or heuristic rule is allowed to unilaterally declare an entity or interaction "fraudulent".

- Models and heuristic detectors output **evidence items** and **signals** (with local confidence metrics and provenance).
- The final assessment engine evaluates the **coalescence of multi-signal evidence**.

### 2.2 Dual-Axis Assessment: Risk & Evidence Confidence

Every journey analysis produces two orthogonal metrics:

1. **Risk Level**: `LOW` | `MEDIUM` | `HIGH`
2. **Evidence Confidence**: `LOW` | `MEDIUM` | `HIGH`

The system explicitly supports and defaults to __`INSUFFICIENT_EVIDENCE`__ when data points are sparse, contradictory, or unverified, avoiding false-positive hallucinations.

### 2.3 Adaptive Intervention

Rather than trigger repetitive warning dialogs (leading to alert fatigue), interventions are dynamically calibrated against user vulnerability and stage in the scam journey (e.g., passive warning banners vs. delayed UPI intent vs. biometric friction).

---

## 3. Seven Dimensions of Evidence Correlation

ScamGraph AI correlates signals across seven distinct dimensions:

```ini {"metadata":"[object Object]"}
┌────────────────────────────────────────────────────────────────────────┐
│                        ScamGraph AI Correlation Core                   │
├────────────────────────────┬───────────────────────────────────────────┤
│ 1. Semantic Message Signals│ Impersonation, urgency, coercion, dialect │
│ 2. URL & Web Evidence      │ Domain age, SSL, TinyFish API telemetry   │
│ 3. Payment Context         │ VPA format, collect requests, mismatch    │
│ 4. Temporal Event Sequence │ Interval anomalies, step transitions      │
│ 5. Infrastructure Links    │ Shared hosting, registrar, phone prefixes │
│ 6. Historical Incidents    │ Prior reported journeys, known vectors    │
│ 7. Campaign Similarity     │ Vector cosine distance, pattern clusters  │
└────────────────────────────┴───────────────────────────────────────────┘
```

---

## 4. High-Level System Architecture

```mermaid
graph TD
    subgraph Client Tier
        UI[Next.js + Cytoscape.js Frontend]
        ExtApp[UPI / Banking Host App Mock / SDK]
    end

    subgraph API Tier
        API[FastAPI Gateway (services/api)]
    end

    subgraph Service Tier
        PE[Pattern Engine (services/pattern-engine)]
        GE[Graph Engine (services/graph-engine)]
        INV[Investigation Service (services/investigation)]
    end

    subgraph Storage & Index Tier
        PG[(PostgreSQL + pgvector)]
        NEO[(Neo4j Graph Database)]
    end

    subgraph External & ML
        TF[TinyFish API / Web Intel]
        ML[Multilingual Embeddings / ML Models]
    end

    UI -->|REST / SSE / WebSocket| API
    ExtApp -->|Ingest Events| API
    API --> PE
    API --> GE
    API --> INV
    
    PE --> ML
    PE --> PG
    INV --> TF
    GE --> NEO
    GE --> PG
    
    PE -->|Query Cross-Campaign Similarity| PG
    GE -->|Query Journey Paths & Clusters| NEO
```

---

## 5. Subsystem Breakdown

### 5.1 Frontend (`apps/web`)

- **Framework**: Next.js (App Router), TypeScript, Tailwind CSS.
- **Visualization**: Cytoscape.js for rendering the interactive **Scam Journey Graph**, node-level evidence inspection, timeline views, and campaign clusters.
- **Panels**:
   - Journey Timeline (Step-by-step psychological progression)
   - Evidence Inspector (Signal breakdown and provenance)
   - Risk & Confidence Matrix
   - Adaptive Intervention Simulator

### 5.2 API Service (`services/api`)

- **Framework**: FastAPI (Python 3.11+), Pydantic v2.
- **Responsibilities**:
   - Ingestion of interaction events (SMS, WhatsApp, call metadata, URL clicks, UPI collect requests).
   - Auth, validation, rate limiting, and session correlation.
   - Streaming journey graph updates and assessment payloads to the frontend.

### 5.3 Investigation Service (`services/investigation`)

- **Responsibilities**:
   - Enrichment of URLs, domains, and web artifacts.
   - Integration with **TinyFish API** for real-time domain age, registrar metadata, web footprint, and risk telemetry.
   - Caching and deduplication of domain intelligence.

### 5.4 Pattern Engine (`services/pattern-engine`)

- **Responsibilities**:
   - Extraction of semantic signals using multilingual embeddings (`sentence-transformers`).
   - Sequence detection (Markov / transition rule checks for scam progression stages).
   - Campaign fingerprint generation and vector similarity search against historical incidents.
   - Multi-signal fusion logic to compute Risk Score, Confidence Score, and Intervention decisions.

### 5.5 Graph Engine (`services/graph-engine`)

- **Responsibilities**:
   - Management of Neo4j graph operations (Cypher queries).
   - Mapping chronological events into journey subgraphs (`Step` -> `NEXT` -> `Step`).
   - Entity fusion (linking shared VPAs, phone numbers, device IDs, and hosting infrastructure).
   - Extraction of graph topologies for visualization in Cytoscape.js.

### 5.6 Shared Schemas (`packages/schemas`)

- Canonical Pydantic and JSON schemas shared across backend services and frontends to guarantee contract integrity.

---

## 6. Technology Stack Justification

| Layer | Choice | Rationale |
|---|---|---|
| Frontend | Next.js + Cytoscape.js | Fast SSR/SPA hybrid, rich graph layout support for path visualization |
| API | FastAPI + Pydantic v2 | High-throughput async Python, robust typing, native OpenAPI specs |
| Relational & Vector | PostgreSQL + pgvector | Unified relational storage for incidents + high-performance vector search |
| Graph Store | Neo4j 5.x | Native property graph with Cypher for complex multi-hop path and entity traversal |
| Embeddings | sentence-transformers | Multilingual support for Hindi, Hinglish, and Indian regional languages |
| Investigation | TinyFish API | Low-latency URL and domain intelligence |

> **Constraint Compliance**: No Kafka, Kubernetes, or microservice proliferation. Services run in a modular monorepo structure with clear boundaries, deployable locally via standard Python tooling and Docker Compose.
