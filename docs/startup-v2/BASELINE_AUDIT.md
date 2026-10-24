# ScamGraph AI — Baseline Audit & Technical Health Report
**Phase 0A: Repository Baseline, Architecture & Integrity Audit**
**Date:** October 24, 2026  
**Auditor:** Principal Software Architect, Cybersecurity & ML Technical Auditor  
**Branch:** `startup-v2` (Baseline commit state preserved)

---

## 1. Executive Summary

ScamGraph AI was conceived as an India-first scam investigation and signal correlation framework targeting multi-channel scam journeys (communications, impersonation, phishing, UPI/payment intent).

The repository contains an impressive conceptual foundation, clean interface definitions (Pydantic v2 domain models), and a well-thought-out multi-signal philosophy ("no single model declares fraud"). However, the codebase is currently an **advanced prototype/hackathon platform** with significant gaps between documented capabilities and production realities:

1. **Storage & Persistence Illusion**: While architectural documents extensively detail PostgreSQL, pgvector, and Neo4j graph databases, the backend relies heavily on **in-memory repositories** (e.g., in-memory dictionaries for incidents, registry, vector embeddings, and graph storage when Neo4j is absent). Data does not survive container/process restarts.
2. **ML Quality vs Claims**: The message classifier is a valid, functioning TF-IDF + Logistic Regression model (with verified 5,000-term vocabulary). However, the "URL ML Classifier" and "Payment Risk Classifier" are **hand-crafted heuristic weighted linear scorers** using static YAML configs, not models trained on ground-truth datasets.
3. **Frontend Build & Route Status**: The Next.js frontend has rich views (`/investigate`, `/lab`, `/incidents`, `/campaigns`, `/graph`, `/registry`, `/mulehunter`), but `npm run build` fails due to a TypeScript typing error in dynamic routing (`app/incidents/[id]/page.tsx:115:53`), and several views rely on mock demo fixtures rather than persistent backend streams.
4. **Test Suite Fragility**: Test collection yields **14 collection errors out of 153 collected tests** because optional dependencies (`neo4j`) are imported at module level without graceful fallback guards, causing test suite collection to abort.

---

## 2. Startup Readiness Score (0 to 10 Scale)

| Dimension | Score (0-10) | Evidence & Rationale |
| :--- | :---: | :--- |
| **Product Architecture** | **7 / 10** | Strong vision ("See the scam journey, not just the transaction"), high-clarity India-first focus (UPI, Aadhaar, KYC, electricity scams). Clear separation of concerns. |
| **Backend Architecture** | **5 / 10** | Clean FastAPI design, typed schemas, and structured modular endpoints, but compromised by lack of persistent ORM models, missing database migrations, and in-memory mock repositories. |
| **Frontend Architecture** | **6 / 10** | Polished visual aesthetics, Cytoscape graph rendering, dark mode, rich design system, but broken production build (`npm run build` type error) and tight coupling to demo fixtures. |
| **Dataset Quality** | **3 / 10** | Registry defines 3 datasets; however, local `data/raw`, `data/processed`, and `data/synthetic` are empty (`.gitkeep` only). Benchmarks rely on synthetic scenarios and small samples (2,272 rows). |
| **ML Quality** | **4 / 10** | Message NLP model is genuine and functional. URL and Payment "ML" are heuristic config weights disguised as models. Embeddings fall back to CPU or in-memory vectors. |
| **Evaluation Integrity** | **4 / 10** | Metrics reported (95.6% accuracy, 3.9% FPR) exist on small mixed datasets where template and campaign leakage are likely unmitigated. |
| **Graph Intelligence** | **4 / 10** | Comprehensive Cypher queries and schema definitions exist, but defaults to in-memory graph fallback. Graph serves mainly visualization rather than automated real-time multi-hop graph mining. |
| **Journey Intelligence** | **4 / 10** | Scenario simulation engine is functional (`/lab`), but dynamic Journey Reconstruction from unstructured arbitrary telemetry is largely rule/keyword-based, not an adaptive journey engine. |
| **Campaign Intelligence** | **4 / 10** | DBSCAN clustering logic exists, but runs on mock/in-memory incident lists rather than incremental real-time vector streams. |
| **Security Architecture** | **4 / 10** | Basic URL validation exists in investigation orchestrator, but lacks hardened SSRF defense, tenant isolation, API authentication/authorization, and rate limiting. |
| **Privacy Architecture** | **2 / 10** | Raw phone numbers, message bodies, and UPI VPAs are accepted and stored in plain text in memory/logs. No field-level encryption, PII masking, or retention/deletion lifecycle. |
| **Observability** | **3 / 10** | Standard Python logging and Next.js console logs. No OpenTelemetry, distributed tracing across signal extractors, Prometheus metrics, or structured error reporting (e.g. Sentry). |
| **Scalability** | **3 / 10** | In-memory data structures will exhaust RAM under load. Cannot horizontally scale backend instances without a shared database/cache cluster. |
| **Developer Experience** | **5 / 10** | Clear markdown guides and modular directory structure, but broken test collection due to hard `neo4j` import requirements without fallback in test environments. |
| **Production Readiness** | **3 / 10** | Not ready for live consumer or bank traffic without persistent storage, auth, hardened SSRF/rate limiting, and CI/CD pipelines. |
| **Overall Startup Baseline** | **3.9 / 10** | **Strong Prototype / High Potential Seed Asset** |

---

## 3. Critical Questions Answered

### 1. What actually works today?
- **Backend API Server**: FastAPI boots on port 8001. Main endpoints (`/api/v1/investigate`, `/api/v1/incidents`, `/api/v1/simulator/scenarios`) respond synchronously.
- **Frontend App**: Next.js runs in development mode (`npm run dev`) on port 3001 with interactive investigation input and Cytoscape graph rendering.
- **Message Model Classifier**: TF-IDF vectorizer + Logistic Regression model is serialized, loadable, and predicts message scam probabilities.
- **Interactive Lab Simulator**: Branching scenario runner (`simulator_electricity_bill.yaml`) works and allows step-by-step decision simulations.
- **Pattern Matchers**: Regex/keyword YAML patterns for KYC, digital arrest, job scams, and electricity scams parse correctly.

### 2. What exists only in documentation?
- **Enterprise Bank Integration**: No webhooks, mTLS, or ISO20022/UPI settlement engine connectors.
- **Continuous Campaign Threat Intelligence**: Documented as an autonomous background clustering radar; in practice, it is triggered on-demand against in-memory arrays.
- **ScamDNA V3**: Documented as an evolving genomic fingerprint; currently implemented as a static dictionary of weighted sub-scores (`ScamFingerprintV2`).

### 3. What is demo/synthetic?
- `data/scenarios/` (35 synthetic sample progression files).
- Payment risk classifier features and weights (heuristic logistic formula using hand-crafted numbers in `config/payment_ml.yaml`).
- Incident feeds on the dashboard (falls back to mock sample lists if Postgres/Neo4j queries return empty).

### 4. Which current features should become startup core?
1. **Multi-Signal Evidence Orchestrator** (`services/investigation/orchestrator.py`): The core philosophy of fusing message, URL, payment, and entity signals into a unified evidence model.
2. **Indian Scam Taxonomy & Pattern Schemas** (`packages/schemas/` & `data/patterns/`): Capturing India-specific typologies (Digital Arrest, Electricity disconnection, Part-time job task, APK sideloading).
3. **Scam Journey Graph Visualizer**: Explaining the *progression* of fraud rather than presenting an opaque black-box score.

### 5. Which features should be demoted or simplified?
- **Mule Hunter Engine** (`services/mule_engine/`): Out of scope for consumer pre-payment defense. Mule account ring detection is a core banking core/AML problem that distracts from consumer journey intervention.
- **Fake Activity Simulators**: Demote synthetic random telemetry generators to internal test utilities.

### 6. Which features are duplicated?
- **Risk Scoring**: Implemented simultaneously in `services/risk_engine/unified_engine.py`, `services/pattern-engine/matcher/risk_engine.py`, and `services/pattern-engine/matcher/risk_engine_v1.py`.
- **Navigation & Layout Components**: Duplicate navigation bars between `apps/web/components/Navbar.tsx` and `apps/web/components/shell/TopNav.tsx`.

### 7. Which components are unsafe to delete?
- `packages/schemas/`: The bedrock Pydantic data contracts across services.
- `services/api/app/`: The central API routing and orchestration harness.
- `ml/message/artifacts/`: Pretrained model artifacts (`model.joblib`, `vectorizer.joblib`).

### 8. Which current models are production candidates?
- **Message NLP Classifier** (`ml/message/`): Candidate baseline. Clean, low latency, 95% accuracy on tested text, easy to serve with minimal CPU footprint.

### 9. Which models should be rejected?
- **Payment ML Classifier** (`ml/payment/classifier.py`): Must NOT be advertised as ML. It is a linear heuristic formula with arbitrary weights.
- **URL ML Classifier** (`ml/url/classifier.py`): Requires retraining against actual benign/malicious Indian phishing domains rather than hand-tuned logistic biases.

### 10. Are current ML metrics trustworthy?
- **Partially**. While the confusion matrix is internally consistent, the test dataset is small (~809 samples) and contains duplicate templates and synthetic examples. Generalization against real, evolving Indian dialect variations (Hinglish, regional terms) is likely lower than the claimed 95.6%.

### 11. What datasets are actually being used?
- Only registered datasets referenced in `data/registry/datasets.yaml` (`scam-ham-india`, `indian-scam-sms-synthetic-audited`, `scamgraph-canonical-journeys`). Local folders `data/raw/` and `data/processed/` only contain `.gitkeep`.

### 12. How much data is real vs synthetic vs unknown?
- Approximately **65% synthetic or synthetic-audited**, **35% real raw SMS**. Zero live banking or telecommunications network feeds.

### 13. Where can train/test leakage occur?
- Template leakage (identical notification structures with only phone numbers/names altered appearing in both train and test splits).
- Random row-based splitting rather than campaign-based or temporal-based train/test splitting.

### 14. Is Journey Engine real or mostly conceptual?
- **Hybrid Scenario Engine**: It successfully maps predefined stages (`CONTACT -> IMPERSONATION -> URGENCY -> CREDENTIAL -> PAYMENT`), but does not dynamically reconstruct arbitrary multi-channel breadcrumbs in real-time.

### 15. Is ScamFingerprintV2 implemented?
- **Yes**, implemented in `services/registry/fingerprint.py`, but it computes a static weighted dictionary hash rather than a true similarity-preserving fuzzy genomic representation.

### 16. Is graph correlation genuinely functional?
- **Functional with Neo4j running**, but instantly falls back to an in-memory dictionary graph if Neo4j is offline. The fallback graph cannot persist relationships across restarts.

### 17. Is campaign detection based on real persisted incidents?
- **No**. Campaign clustering currently runs against in-memory incident buffers or mocked test fixtures, not on a persistent historical incident database.

### 18. Which systems use memory rather than persistent storage?
- Vector similarity search (`services/storage/vector/in_memory.py` is default when pgvector is unconfigured).
- Incident storage (`services/api/app/repository/memory.py`).
- Graph storage (`services/graph-engine/neo4j/repository.py` fallback mode).
- Registry records.

### 19. Which frontend screens use mock/demo data?
- `/incidents`: Falls back to mock incidents when API is empty.
- `/campaigns`: Renders hard-coded campaign cards when clustering endpoint returns no clusters.
- `/graph`: Features demo graph generator buttons.

### 20. What prevents ScamGraph from serving 1 million users today?
- State is held in Python memory. A single process crash loses all context.
- No distributed caching (Redis).
- Synchronous blocking HTTP calls in investigation pipelines.
- No rate limiting or abuse protection.

### 21. What prevents ScamGraph from serving a bank/fintech today?
- Zero enterprise compliance (ISO 27001, SOC 2, RBI data localization guidelines).
- No API authentication, tenant keys, or role-based access control (RBAC).
- Lack of field-level encryption for sensitive Indian financial identifiers (Aadhaar, UPI VPA, Bank Account numbers).
- Inability to provide deterministic SLA guarantees.

### 22. What is the single most important technical change after this audit?
- **Phase 0B: Unifying the Core Data Contract (`ScamGraphRecordV2`), establishing real database persistence (Postgres + pgvector), and eliminating competing risk engine implementations.**

---

## 4. Top 10 Technical Risks

1. **In-Memory Volatility**: Data loss on restart due to in-memory repositories.
2. **SSRF Vulnerability in URL Investigation**: External fetching mechanisms could be tricked into querying cloud metadata endpoints (`169.254.169.254`) or internal subnets if URL sanitization is bypassed.
3. **Competing Risk Engines**: Discrepancies between `services/risk_engine/unified_engine.py` and `services/pattern-engine/matcher/risk_engine.py` lead to inconsistent risk scores.
4. **Hard Neo4j Import Dependency**: Causes 14 test collection failures whenever `neo4j` driver is missing or offline.
5. **Frontend Build Failure**: Next.js production build (`npm run build`) fails on TypeScript type error in `app/incidents/[id]/page.tsx`.
6. **Hand-Crafted "ML" Models**: URL and Payment risk scoring use arbitrary linear weights rather than empirical models, risking high false-positive rates on legitimate merchants.
7. **Unprotected PII Storage**: Plaintext storage of victim phone numbers, UPI IDs, and chat contents.
8. **Lack of Authentication/Authorization**: All backend REST endpoints are unauthenticated and open.
9. **Data Leakage in Evaluation**: Train/test splits do not account for identical SMS templates, inflating reported model accuracy.
10. **Synchronous Investigation Bottlenecks**: Analysis orchestrator runs multiple network/DNS/RDAP tasks synchronously, risking timeouts under slow network conditions.

---

## 5. Top 10 Startup Opportunities

1. **Defensible Scam Journey Moat**: Incumbents (Truecaller, Google Pay) only see their own silo. ScamGraph's multi-stage journey correlation across SMS -> Web -> UPI is a distinct differentiator.
2. **Real-time UPI VPA Entity Resolver**: Detecting handle mismatches (e.g. claiming to be "SBI Customer Care" but paying `xyz@okhdfcbank`) before money moves.
3. **India Scam Taxonomy Leadership**: Codifying emerging Indian scam templates (Digital Arrest, Courier FedEx customs, Part-time Telegram tasks).
4. **Rescue & Post-Fraud Intervention**: Providing actionable step-by-step 1930 / Chakshu / Cyber Crime portal reporting guidance.
5. **Lightweight Edge Verification**: The Logistic Regression + TF-IDF model is fast enough (<5ms) to run at massive scale with minimal cloud compute costs.
6. **Cross-Victim Correlation Engine**: Connecting separate victims targeted by the same payment handle or phone number cluster.
7. **Enterprise Fraud Intelligence Feed**: Selling high-fidelity, verified scam infrastructure indicators (domains, VPAs, sender IDs) to fintechs and banks.
8. **Explainable Scam DNA**: Generating clear, human-readable explanations of *why* an interaction is dangerous to reduce user alert fatigue.
9. **Multilingual Code-Mixed Defense**: Expanding NLP coverage to code-mixed Hinglish, Tamil, Telugu, and Bengali scam dialectics.
10. **Zero-Knowledge Evidence Privacy**: Differentiating on privacy by hashing or anonymizing sensitive victim PII before central intelligence aggregation.

---

## 6. Documented vs Implementation Reality

| Major Component | Claimed Status | Actual Implementation Status | Classification |
| :--- | :--- | :--- | :--- |
| **Message Classifier** | Production NLP model | Functional TF-IDF + Logistic Regression (5,000 vocab) | `PRODUCTION_CANDIDATE` |
| **URL Risk Engine** | Calibrated ML model | Heuristic formula based on static YAML config | `DEMO_ONLY` / `HEURISTIC` |
| **Payment Risk Engine**| Logistic ML model | Hand-crafted linear weights in YAML | `DEMO_ONLY` / `HEURISTIC` |
| **ScamFingerprintV2** | Genomic vector representation | Static dictionary of 5 sub-scores | `PARTIALLY_IMPLEMENTED` |
| **Journey Engine** | Adaptive journey inference | YAML scenario runner & keyword rule matcher | `PARTIALLY_IMPLEMENTED` |
| **Graph Intelligence** | Neo4j cluster & analytics | Functional Cypher queries, but falls back to in-memory dict | `HYBRID` / `DEMO_FALLBACK` |
| **Campaign Engine** | Dynamic vector clustering | DBSCAN logic present, runs on in-memory buffers | `PARTIALLY_IMPLEMENTED` |
| **Smart Registry** | Blockchain/Merkle verified trust | In-memory CRUD store with dispute schemas | `STUB` / `IN_MEMORY` |
| **Vector Storage** | pgvector high-dimensional DB | `pgvector_store.py` exists, but defaults to in-memory NumPy | `PARTIALLY_IMPLEMENTED` |
| **Investigation API** | Enterprise orchestrator | Synchronous orchestrator with basic DNS/TinyFish hooks | `PARTIALLY_IMPLEMENTED` |

---

## 7. Migration Plan Summary

- **KEEP**:
  - `packages/schemas/`: Core Pydantic contracts.
  - `ml/message/artifacts/`: Verified working NLP model.
  - `data/patterns/`: High-value India scam taxonomy.
  - `services/api/app/main.py`: FastAPI structure and middleware foundation.
- **KEEP + IMPROVE**:
  - `services/investigation/orchestrator.py`: Harden with SSRF controls, timeouts, and async task queues.
  - `apps/web/`: Fix TypeScript errors, decouple from mock fixtures, streamline UI components.
  - `services/storage/vector/`: Make pgvector default and enforce persistent storage.
- **REFACTOR / MERGE**:
  - **Risk Engines**: Consolidate `services/risk_engine/unified_engine.py` and `services/pattern-engine/matcher/risk_engine.py` into a single canonical risk engine.
  - **Graph Layer**: Decouple Neo4j queries behind a strict interface; eliminate module-level import crashes.
- **DEMOTE**:
  - `services/mule_engine/`: Demote from primary consumer flow to experimental enterprise backlog.
  - Mock scenario generators: Demote to test fixtures.
