# ScamGraph AI — Current State Audit Report

> **Generated at**: 2026-10-21T00:58:00+05:30  
> **Audited by**: Antigravity Lead Architect  
> **Mandate**: Strict codebase audit without writing new implementation code or modifying external references.

---

## 1. Existing Repository Structure

```
ScamGraph-AI/
├── .agents/
│   └── rules/
│       └── scamgraph_rules.md            # Persistent architectural rules
├── .env.example                          # Environment secrets template
├── .gitignore                            # Standard Python & Node gitignore
├── docker-compose.yml                    # Local Postgres (pgvector) & Neo4j orchestration
├── README.md                             # High-level architecture & quickstart
├── docs/                                 # Architectural & Governance Documentation
│   ├── ARCHITECTURE.md                   # Multi-signal pipeline & 7 correlation dimensions
│   ├── ARCHITECTURE_RULES.md             # 25 binding architectural invariants
│   ├── CURRENT_STATE.md                  # This audit document
│   ├── DATA_MODEL.md                     # Relational + Vector + Property Graph schemas
│   ├── DEMO.md                           # Hackathon judge walkthrough script
│   ├── EVIDENCE_MODEL.md                 # Provenance & signal scoring specification
│   ├── FINAL_INTEGRATION_PLAN.md         # Final capability selection & architecture
│   ├── INTEGRATION_PLAN.md               # Source -> Interface -> Implementation pipeline
│   ├── OPEN_SOURCE_CAPABILITY_MATRIX.md  # 17-repo capability harvest mapping
│   ├── PATTERN_ENGINE.md                 # Deterministic scam pattern specifications
│   ├── REFERENCE_ANALYSIS.md             # 11-point inspection of candidate repositories
│   ├── REFERENCE_REPOS.md                # Reference registry with licenses & attributions
│   └── ROADMAP.md                        # Phase 1 through Phase 8 delivery roadmap
├── packages/
│   └── schemas/                          # Canonical Pydantic v2 schemas
│       ├── __init__.py
│       ├── assessment.py                 # RiskLevel, EvidenceConfidence, AssessmentResult
│       ├── events.py                     # Event, EventType, Message/URL/Payment payloads
│       ├── fingerprint.py                # ScamFingerprint model
│       ├── graph.py                      # CytoscapeNode, CytoscapeEdge, GraphNodeType
│       ├── journey.py                    # ScamJourney, JourneyStep, JourneyStage
│       └── signals.py                    # EvidenceSignal, SignalDimension, ProvenanceRecord
├── services/
│   ├── __init__.py                       # Package aliasing for hyphenated service names
│   ├── api/                              # FastAPI Gateway
│   │   └── app/
│   │       ├── main.py                   # FastAPI app entry point & CORS
│   │       ├── core/config.py            # Settings with pydantic-settings
│   │       └── api/v1/
│   │           ├── api.py                # Router aggregator
│   │           └── endpoints/
│   │               ├── incidents.py      # Incident lifecycle, event ingestion, journey, graph
│   │               ├── investigate.py    # Ad-hoc message/URL/VPA deep analysis
│   │               ├── lab.py            # Step 20 Judge Simulator dynamic execution
│   │               └── campaigns.py      # Campaign clusters & syndicate topology
│   ├── investigation/                    # Web & Infrastructure Safety
│   │   ├── url_analysis/
│   │   │   ├── safety.py                 # URLSafetyValidator (SSRF Guard) & URLAnalyzer
│   │   │   └── analyzers.py              # DNSAnalyzer, RDAPAnalyzer, TLSAnalyzer, RedirectAnalyzer
│   │   └── tinyfish/
│   │       ├── client.py                 # Async HTTP client with timeout/retry safety
│   │       ├── prompts.py                # Fact-only DOM extraction prompts
│   │       ├── parser.py                 # Structured DOM JSON -> EvidenceSignal parser
│   │       └── service.py                # WebInvestigatorService with provider fallback
│   ├── pattern-engine/                   # Signal Processing, Patterns & Risk
│   │   ├── semantic/
│   │   │   ├── nlp.py                    # Multilingual Hindi/Hinglish/English regex extractors
│   │   │   ├── encoder.py                # SentenceTransformers (MiniLM-L12-v2)
│   │   │   └── fingerprint_builder.py    # ScamFingerprintBuilder
│   │   ├── patterns/
│   │   │   └── scam_patterns.py          # 5 canonical patterns & PatternMatcher
│   │   └── matcher/
│   │       ├── similarity.py             # Cosine similarity against seed templates
│   │       ├── fusion.py                 # Baseline EvidenceFusionEngine
│   │       ├── risk_engine.py            # Step 18 Explainable RiskEngine
│   │       └── variant_detector.py       # Step 21 Hero EmergingVariantDetector
│   └── graph-engine/                     # Neo4j Scam Journey & Entity Resolution
│       ├── neo4j/
│       │   ├── client.py                 # Async Neo4j client with safety timeouts
│       │   ├── journey_graph.py          # Cypher journey queries
│       │   └── repository.py             # GraphRepository with in-memory graph fallback
│       ├── correlation/
│       │   └── entity_service.py         # EntityCorrelationService (shared entity counts & paths)
│       └── campaigns/
│           └── clusterer.py              # DBSCAN clustering over embedding vectors
├── apps/
│   └── web/                              # Next.js 14 App Router Frontend
│       ├── app/
│       │   ├── layout.tsx                # Glassmorphic layout with Lucide navigation
│       │   ├── globals.css               # Google Fonts, ambient glows, radar animations
│       │   ├── page.tsx                  # Consumer Shield (interactive phone mockup)
│       │   ├── investigate/page.tsx      # Multi-signal investigation workspace with presets
│       │   ├── incidents/page.tsx        # Active journey incidents list
│       │   ├── incidents/[id]/page.tsx   # Cytoscape directed journey graph & timeline
│       │   ├── command/page.tsx          # SOC Analyst Command Center & entity resolution
│       │   ├── campaigns/page.tsx        # Syndicate campaigns list
│       │   ├── campaigns/[id]/page.tsx   # Cytoscape syndicate topology graph
│       │   └── lab/page.tsx              # Step 20 & 21 Judge Simulator with animated replay
│       ├── components/
│       │   ├── graph/CytoscapeCanvas.tsx # Interactive Cytoscape.js directed canvas
│       │   ├── risk/RiskBadge.tsx        # Dual-axis Risk Index + Confidence badge
│       │   ├── risk/InterventionModal.tsx# 10s Adaptive friction countdown modal
│       │   ├── evidence/EvidenceDrawer.tsx # Signal provenance inspector drawer
│       │   └── timeline/JourneyTimeline.tsx# Chronological grooming sequence
│       ├── package.json
│       ├── tsconfig.json
│       └── tailwind.config.js
├── ml/                                   # Offline ML stubs (inference is in pattern-engine)
├── data/                                 # Data storage stubs (active payloads in endpoints/tests)
├── references/github/                    # Shallow research clones (READ-ONLY)
│   ├── PhishGraph/
│   ├── VECTPHISH/
│   ├── demo-fraud-detection-with-p2p/
│   └── tinyfish-cookbook/
└── tests/                                # Automated test suite (42 passing tests)
    ├── unit/                             # 12 unit test files
    ├── scenarios/                        # 2 scenario test files
    ├── integration/                      # Placeholder __init__.py
    └── benchmark/                        # Placeholder __init__.py
```

---

## 2. What Has Actually Been Implemented

1. **Canonical Schemas (`packages/schemas/`)**:
   - Fully written and tested Pydantic v2 models for events, evidence signals, journeys, assessments, fingerprints, and Cytoscape graphs.
2. **FastAPI Gateway (`services/api/`)**:
   - `POST /incidents`, `GET /incidents/{id}`, `POST /incidents/{id}/events`, `GET /incidents/{id}/timeline`.
   - `POST /incidents/ingest`, `GET /incidents/{id}/journey`, `GET /incidents/{id}/assessment`, `GET /incidents/{id}/graph`.
   - `POST /investigate` (deep analysis of text, URL, VPA, and QR data).
   - `GET /lab/scenarios`, `POST /lab/simulate` (executing 6 scenarios with evolving risk indices).
   - `GET /campaigns`, `GET /campaigns/{id}/graph` (syndicate campaign list and Cytoscape graph).
3. **Investigation Service (`services/investigation/`)**:
   - `URLSafetyValidator`: Strict SSRF guard blocking private IP spaces, loopbacks, and cloud metadata.
   - `URLAnalyzer`: Lexical typosquatting, entropy, and brand impersonation detection.
   - `DNSAnalyzer`, `RDAPAnalyzer`, `TLSAnalyzer`, `RedirectAnalyzer`: Network telemetry.
   - `TinyFish`: Async client, fact-extraction prompts, JSON parser, and service wrapper with provider fallback.
4. **Pattern & Risk Engine (`services/pattern-engine/`)**:
   - `SemanticSignalExtractor`: Multilingual Hindi/Hinglish/English regex & keyword extractors.
   - `SemanticEncoder`: 384-dimensional dense multilingual embeddings via `sentence-transformers`.
   - `PatternMatcher`: 5 canonical patterns (`KYC_IMPERSONATION`, `ELECTRICITY_DISCONNECTION_FRAUD`, `PART_TIME_JOB_FRAUD`, `COURIER_PARCEL_HOLD`, `QR_COLLECT_INVERSION`).
   - `RiskEngine` (Step 18): Explainable non-probabilistic Risk Index (0–100), dual-axis calibration, reason codes linked to Evidence IDs, and counter-evidence discounts.
   - `EmergingVariantDetector` (Step 21): Hero detector evaluating known identifier matches vs workflow matches.
5. **Graph Engine (`services/graph-engine/`)**:
   - `Neo4jClient` & `JourneyGraphService`: Cypher queries for journey traversal.
   - `GraphRepository`: Graph operations with in-memory graph fallback.
   - `EntityCorrelationService`: Computes shared entity counts and Cypher explanation paths.
   - `CampaignClusterer`: DBSCAN clustering over embeddings.
6. **Next.js Frontend (`apps/web/`)**:
   - Complete 9-route Next.js 14 App Router application with Cytoscape directed canvas, interactive phone mockup, 6-scenario simulator with animated risk evolution, and 10s friction interlock.

---

## 3. What is Documentation Only

1. **PostgreSQL Relational & `pgvector` Tables**:
   - Documented in `docs/DATA_MODEL.md` and Docker Compose, but the application currently operates using in-memory session dictionaries and in-memory graphs for rapid hackathon execution.
2. **`ml/` Subdirectories**:
   - Folders `ml/embeddings`, `ml/emerging`, `ml/evaluation`, `ml/message`, `ml/payment`, `ml/url` contain only `__init__.py` files. All active ML/NLP logic was placed in `services/pattern-engine/` and `services/investigation/`.
3. **`data/` Subdirectories**:
   - Folders `data/raw`, `data/processed`, `data/scenarios`, `data/synthetic` contain only `README.md` files. Synthetic test payloads are embedded directly in code and scenario tests.
4. **`tests/benchmark/` & `tests/integration/`**:
   - Folders contain only `__init__.py` files. E2E and scenario tests currently run inside `tests/scenarios/` and `tests/unit/`.

---

## 4. Existing Dependencies

### Python (`pyproject.toml` / environment)
- `fastapi`: 0.115+
- `uvicorn`: 0.40.0
- `pydantic`: 2.9+
- `pydantic-settings`: 2.6+
- `httpx`: 0.27+
- `sentence-transformers`: 3.2+ (`paraphrase-multilingual-MiniLM-L12-v2`)
- `scikit-learn`: 1.5+
- `numpy`: 2.1+
- `neo4j`: 5.25+

### Frontend (`apps/web/package.json`)
- `next`: 14.2.35
- `react` / `react-dom`: 18.3.1
- `cytoscape`: 3.30.2
- `cytoscape-dagre`: 2.5.0
- `lucide-react`: 0.453.0
- `tailwindcss`: 3.4.14
- `typescript`: 5.6.3

---

## 5. Existing Tests

**Total Automated Tests**: 42 tests across 14 test modules.  
**Execution Command**: `python -m unittest discover tests`  
**Execution Time**: ~5.5 seconds  
**Pass Rate**: 100% (42/42 passing)

1. `tests/unit/test_api.py`: FastAPI health and incident routing.
2. `tests/unit/test_incident_engine.py`: Step 11 incident creation, event ingestion, and timeline delta.
3. `tests/unit/test_journey_graph_step12.py`: Neo4j Cypher query generation for journey steps.
4. `tests/unit/test_url_analyzers_step13.py`: DNS, RDAP, TLS, and redirect analysis.
5. `tests/unit/test_investigation.py`: SSRF guard blocking loopback, private RFC1918, and metadata IPs.
6. `tests/unit/test_tinyfish_step14.py`: TinyFish client, prompt formatting, and fallback parsing.
7. `tests/unit/test_vectphish_step15.py`: Semantic embeddings and DBSCAN campaign clustering.
8. `tests/unit/test_neo4j_integration_step16.py`: GraphRepository entity upserts and correlation paths.
9. `tests/unit/test_pattern_engine.py`: 5 canonical scam patterns and regex feature extractors.
10. `tests/unit/test_risk_engine_step18.py`: Risk Index calculation, INSUFFICIENT_EVIDENCE enforcement, and reason code provenance.
11. `tests/unit/test_schemas.py`: Validation of all Pydantic v2 canonical schemas.
12. `tests/unit/test_graph_engine.py`: Cytoscape JSON serialization and graph node types.
13. `tests/scenarios/test_electricity_scam_scenario.py`: End-to-end multi-step electricity cutoff grooming path.
14. `tests/scenarios/test_hero_emerging_variant.py`: Step 21 Hero test verifying unknown identifiers with known workflow.

---

## 6. Missing Files

1. `tests/benchmark/test_benchmarks.py`: Throughput and latency benchmark tests under synthetic event load.
2. `tests/integration/test_docker_services.py`: Live integration tests verifying actual connections against live PostgreSQL and Neo4j Docker containers.
3. Static datasets in `data/synthetic/`: Offline synthetic datasets (e.g. PaySim UPI transactions) for reproducible offline benchmarking.

---

## 7. Architecture Inconsistencies

1. **Hyphenated Directory Names in Python Packages**:
   - `services/graph-engine` and `services/pattern-engine` contain hyphens, which cannot be imported directly in Python (`import services.graph-engine` is a syntax error).
   - **Resolution applied**: `services/__init__.py` registers sys.modules aliases (`services.graph_engine` and `services.pattern_engine`), and tests use `importlib.import_module` where appropriate.
2. **Two Fusion Modules in Pattern Engine**:
   - `EvidenceFusionEngine` (`services/pattern-engine/matcher/fusion.py`) was created earlier as a baseline fusion engine.
   - `RiskEngine` (`services/pattern-engine/matcher/risk_engine.py`) was implemented for Step 18 to incorporate pattern match scores and graph correlation reports. Both follow identical dual-axis rules, but `RiskEngine` is the canonical implementation.
3. **In-Memory Storage vs Database Storage**:
   - While Docker Compose defines PostgreSQL and Neo4j containers, the running application uses thread-safe in-memory dictionaries for incident metadata and fallback graph models so tests run in 5 seconds without external service dependencies.

---

## 8. Duplicate Modules

1. `ml/` stubs vs `services/pattern-engine/semantic/`:
   - `ml/` contains empty directory stubs; all active machine learning code lives in `services/pattern-engine/semantic/`.
2. `fusion.py` vs `risk_engine.py`:
   - `risk_engine.py` supersedes `fusion.py` by incorporating graph correlation and pattern match features.

---

## 9. Broken Imports / Configuration

- **Status**: **ZERO broken imports or configuration errors.**
- All 42 Python tests run and pass without errors.
- Next.js production build (`npm run build`) compiles cleanly across all 9 routes with 0 lint and 0 type errors.

---

## 10. External Repositories Currently Cloned

Located under `references/github/` (shallow clones, strictly READ-ONLY):
1. `references/github/PhishGraph`
2. `references/github/VECTPHISH`
3. `references/github/demo-fraud-detection-with-p2p`
4. `references/github/tinyfish-cookbook`

---

## 11. License Information Already Recorded

Documented in `docs/REFERENCE_REPOS.md`:
- `tinyfish-cookbook`: MIT (concept adapted, provider wrapper implemented)
- `PhishGraph`: Apache 2.0 (SSRF & lexical safety concepts adapted)
- `VECTPHISH`: MIT (SentenceTransformers & DBSCAN concept adapted)
- `demo-fraud-detection-with-p2p`: Apache 2.0 (graph entity resolution & Cypher schema adapted)
- 13 other repositories cataloged with license, capability, and attribution requirements.

---

## 12. P0/P1/P2/P3 Integration Status

- **P0 (Core MVP Architecture)**: **100% COMPLETE**
  - Canonical schemas, FastAPI incident endpoints, SSRF guard, TinyFish client/parser, multilingual embeddings, 5 deterministic scam patterns, dual-axis RiskEngine, Neo4j GraphRepository & EntityCorrelationService, Next.js frontend with Cytoscape.js canvas, and Judge Simulator.
- **P1 (Cloud Services & Live Telemetry)**: **PARTIAL**
  - Live TinyFish API calls are ready with environment variables; provider fallback operates when API key is unconfigured.
  - Neo4j async client is ready; operates with in-memory graph fallback when container is offline.
- **P2 (Relational Persistence & Offline Data)**: **PENDING**
  - Alembic migrations and PaySim synthetic transaction dumps.
- **P3 (Academic Research & Distributed Brokers)**: **EXPLICITLY REJECTED**
  - Kafka, Redis, and GNN pipelines deferred per Rule 10 & 17.

---

## Master Checklist

### FOUNDATION
- [x] Monorepo structure
- [x] Architecture rules (`docs/ARCHITECTURE_RULES.md`)
- [x] Environment template (`.env.example`)
- [x] Reference analysis (`docs/REFERENCE_ANALYSIS.md`)
- [x] Integration plan (`docs/INTEGRATION_PLAN.md` & `FINAL_INTEGRATION_PLAN.md`)

### BACKEND
- [x] Canonical schemas (`packages/schemas/`)
- [x] FastAPI (`services/api/app/main.py`)
- [x] Incident API (`POST /incidents`, `GET /incidents/{id}`)
- [x] Event API (`POST /incidents/{id}/events`, `POST /ingest`)
- [x] Evidence API (`POST /investigate`, `GET /incidents/{id}/assessment`)
- [x] Timeline (`GET /incidents/{id}/timeline`, `GET /incidents/{id}/journey`)

### INTELLIGENCE
- [x] Pattern engine (5 canonical scam patterns & `PatternMatcher`)
- [x] Risk engine (Explainable 0–100 index with reason codes linked to Evidence IDs)
- [x] Confidence engine (Calibrated separately based on multi-dimensional corroboration)
- [x] Intervention engine (Adaptive friction interlock with 10s countdown)

### INVESTIGATION
- [x] URL safety (`URLSafetyValidator` with private IP & cloud metadata SSRF guard)
- [x] TinyFish (`WebInvestigatorService`, fact-only prompts, structured parser)
- [x] Infrastructure analysis (DNS, RDAP, TLS, and redirect analyzers)

### GRAPH
- [x] Neo4j (Async driver & Cypher journey queries)
- [x] Entity correlation (`EntityCorrelationService` with shared phone/domain/VPA counts)
- [x] Campaign detection (`CampaignClusterer` with DBSCAN clustering)

### AI
- [x] Semantic embeddings (`SentenceTransformer` multilingual embeddings)
- [x] Message extraction (`SemanticSignalExtractor` for urgency and impersonation)
- [x] URL model (`URLAnalyzer` with lexical typosquatting heuristics)
- [x] Emerging variant detector (`EmergingVariantDetector` - Step 21 Hero engine)

### FRONTEND
- [x] Shield (`/` with interactive phone simulator and live toggle)
- [x] Incident workspace (`/investigate` and `/incidents/[id]`)
- [x] Command Center (`/command` with SOC telemetry and entity resolution)
- [x] ScamGraph Lab (`/lab` with 6 scenario buttons and animated risk evolution)

### TESTING
- [x] Unit tests (12 test modules, 40 tests)
- [ ] Integration tests (Dedicated live Docker integration suite)
- [x] Scenario tests (2 end-to-end scenario tests: Electricity scam and Hero emerging variant)
- [ ] Benchmark tests (Dedicated throughput and latency test suite)

---

## NEXT RECOMMENDED TASK

Implement the dedicated benchmark test suite in `tests/benchmark/test_benchmarks.py` to evaluate pipeline throughput, event ingestion latency, and graph traversal performance under high synthetic event volumes.
