# ScamGraph AI — Technical Integration Plan

> **Scope**: Detailed implementation specification mapping harvested open-source capabilities into ScamGraph-native interfaces, modules, and tests.  
> **Mandate**: No application code is written during this documentation stage.

---

## 1. P0 MVP Capability Scope

To ensure a rock-solid hackathon MVP without architectural drift, **P0** is strictly scoped to:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CORE P0 ARCHITECTURE                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. FastAPI Gateway & Incident Engine                                   │
│ 2. PostgreSQL (Event Logs) + Neo4j (Topological Graph)                 │
│ 3. Specialized Analyzers: Message AI, URL/SSRF Safety, TinyFish Web   │
│ 4. Incident Fusion (Cross-Incident Entity Sharing)                     │
│ 5. Scam Journey Graph (Chronological Step Traversal)                   │
│ 6. Five Deterministic Scam Patterns (Electricity, KYC, Task, Courier, QR)│
│ 7. Dual-Axis Evidence Fusion (Risk + Confidence + INSUFFICIENT_EVIDENCE) │
│ 8. Interactive Cytoscape.js Frontend & Scam Simulator                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Capability Pipelines: Source $\rightarrow$ Interface $\rightarrow$ Implementation $\rightarrow$ Test

### 2.1 PhishGraph SSRF & URL Safety Concepts (Priority: P0)
- **Source Idea**: `PhishGraph/app/security/url_safety.py` & `url_features.py`
- **ScamGraph Interface**: `URLSafetyValidator`, `URLNormalizer`, `URLAnalyzer`
- **ScamGraph Implementation**: `services/investigation/url_analysis/safety.py`
- **Associated Tests**: `tests/unit/test_investigation.py` (Validates rejection of `127.0.0.1`, `10.0.0.0/8`, `169.254.169.254`, private IPv6, and lexical typosquatting).

### 2.2 PhishGraph DNS, RDAP, TLS & Redirect Concepts (Priority: P0)
- **Source Idea**: `PhishGraph/app/analyzers/{dns,tls,rdap,redirect}_analyzer.py`
- **ScamGraph Interface**: `DNSAnalyzer`, `RDAPAnalyzer`, `TLSAnalyzer`, `RedirectAnalyzer`
- **ScamGraph Implementation**:
  - `services/investigation/dns/analyzer.py`
  - `services/investigation/rdap/client.py`
  - `services/investigation/tls/inspector.py`
  - `services/investigation/url_analysis/redirects.py`
- **Associated Tests**: `tests/unit/test_url_analyzers.py` (Validates domain age extraction, Let's Encrypt heuristic detection, redirect-chain following).

### 2.3 TinyFish Web Investigation (Priority: P0)
- **Source Idea**: `tinyfish-cookbook` (DOM scraping recipes & fact extraction)
- **ScamGraph Interface**: `WebInvestigator` interface
- **ScamGraph Implementation**:
  - `services/investigation/tinyfish/client.py` (HTTP client with 4s timeouts & retries)
  - `services/investigation/tinyfish/prompts.py` (Fact-only extraction prompts: forms, OTP, brand claims)
  - `services/investigation/tinyfish/parser.py` (Structured JSON $\rightarrow$ canonical `EvidenceSignal`)
  - `services/investigation/tinyfish/service.py` (High-level service with provider fallback)
- **Associated Tests**: `tests/unit/test_tinyfish.py` (Mocked responses, timeout handling, partial evidence tests).

### 2.4 VECTPHISH Semantic Similarity & Campaign Correlation (Priority: P0)
- **Source Idea**: `VECTPHISH/main.py` (SentenceTransformers + cosine similarity + DBSCAN)
- **ScamGraph Interface**: `SemanticEncoder`, `SemanticSimilarityService`, `CampaignClusterer`
- **ScamGraph Implementation**:
  - `services/pattern-engine/semantic/encoder.py` (Multilingual embedding generation)
  - `services/pattern-engine/matcher/similarity.py` (pgvector cosine search)
  - `services/graph-engine/campaigns/clusterer.py` (Incident $\rightarrow$ Campaign clustering)
- **Associated Tests**: `tests/unit/test_semantic_matcher.py` (Proves paraphrased scam messages are closer in vector space than benign messages).

### 2.5 Neo4j P2P Fraud Entity Resolution & Community Detection (Priority: P0)
- **Source Idea**: `demo-fraud-detection-with-p2p` (Cypher entity sharing & community detection)
- **ScamGraph Interface**: `CypherQueryBuilder`, `IncidentFusionEngine`
- **ScamGraph Implementation**:
  - `services/graph-engine/neo4j/cypher_builder.py`
  - `services/graph-engine/correlation/fusion.py`
- **Associated Tests**: `tests/unit/test_graph_engine.py` (Detects shared phone numbers and UPI VPAs across victims).

### 2.6 Cytoscape.js Interactive Graph Visualization (Priority: P0)
- **Source Idea**: `cytoscape.js` (Canvas DAG and force-directed graph layouts)
- **ScamGraph Interface**: `CytoscapeGraph`, `ScamJourneyVisualizer`
- **ScamGraph Implementation**: `apps/web/components/graph/CytoscapeCanvas.tsx`
- **Associated Tests**: `tests/unit/test_schemas.py` & frontend component tests.

### 2.7 PaySim Synthetic Payment Simulation (Priority: P1)
- **Source Idea**: `PaySim` (Synthetic transaction behavior)
- **ScamGraph Interface**: `SyntheticScenarioGenerator`
- **ScamGraph Implementation**: `data/synthetic/payment/generator.py`
- **Associated Tests**: `tests/scenarios/test_synthetic_journeys.py`.

### 2.8 IOK Phishing Technique Indicators (Priority: P1)
- **Source Idea**: `phish-report/IOK` (Phishing kit signatures)
- **ScamGraph Interface**: `TechniqueMatcher`
- **ScamGraph Implementation**: `services/investigation/extractors/techniques.py`
- **Associated Tests**: `tests/unit/test_technique_rules.py`.

---

## 3. Step-by-Step Implementation Roadmap

```
Step 11: Incident Engine Foundation (No AI)
├── POST /incidents
├── POST /incidents/{id}/events
├── GET /incidents/{id}
└── GET /incidents/{id}/timeline
      │
      ▼
Step 12: Scam Journey Graph (Neo4j)
├── Node Creation: (:Incident), (:Event), (:Message), (:URL), (:Domain), (:UPIHandle)
└── Edge Creation: [:HAS_EVENT], [:FOLLOWED_BY], [:CONTAINS], [:HOSTED_ON], [:TO]
      │
      ▼
Step 13: PhishGraph URL & Infrastructure Intelligence
├── URLNormalizer & URLSafetyValidator (SSRF protection)
├── DNSAnalyzer, RDAPAnalyzer, TLSAnalyzer
└── RedirectAnalyzer (Canonical Evidence Output)
      │
      ▼
Step 14: TinyFish WebInvestigator
├── client.py, prompts.py, parser.py, service.py
├── Collects observable facts (login fields, OTP, brand claims)
└── Timeouts, retries, and mocked provider tests
      │
      ▼
Step 15: VECTPHISH Semantic Correlation & Fingerprint
├── SemanticEncoder (sentence-transformers)
├── ScamFingerprint generation
└── pgvector cosine similarity search & DBSCAN clustering
      │
      ▼
Step 16: Five Deterministic Scam Patterns & Dual-Axis Calibrator
├── Electricity Disconnection Pattern
├── KYC / Bank Suspension Threat Pattern
├── Part-Time Telegram Task Pattern
├── Courier / Parcel Delivery Hold Pattern
├── QR Code / Collect Request Inversion Pattern
└── Multi-Signal Fusion (Risk + Confidence + INSUFFICIENT_EVIDENCE)
      │
      ▼
Step 17: Cytoscape.js Frontend & Scam Simulator
├── Interactive directed journey canvas
├── Real-time evidence drawer
└── Adaptive intervention friction modal (10s countdown)
```

---

## 4. Priority Classifications

| Tier | Meaning | Included Capabilities |
|---|---|---|
| **P0** | **Hackathon-Critical** | FastAPI Gateway, Postgres event logs, Neo4j journey paths, SSRF-safe URL analysis, TinyFish WebInvestigator, Semantic NLP, 5 deterministic scam patterns, Dual-axis fusion, Cytoscape graph |
| **P1** | **Strong Demo Enhancers** | PaySim synthetic UPI generator, IOK phishing kit technique matchers, secondary threat adapters (`urlscan`, `vt-py`), pgvector DBSCAN campaign clusterer |
| **P2** | **Optional Additions** | IEEE-CIS financial schema nuances, Knowledge Graph fraud visualization alternatives |
| **P3** | **Post-Hackathon Research** | GNN embeddings (`phishGNN`, GraphSAGE), stream processing architectures (`FraudGraph`) |
