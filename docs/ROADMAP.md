# ScamGraph AI — Hackathon Roadmap

## Milestone Overview

```
Phase 1: Foundation & Scaffolding   [CURRENT]
    │
    ▼
Phase 2: Shared Schemas & Ingestion API
    │
    ▼
Phase 3: Neo4j Journey Graph & Entity Fusion Engine
    │
    ▼
Phase 4: Multilingual Embeddings & Pattern Engine
    │
    ▼
Phase 5: TinyFish API Web & Infrastructure Enrichment
    │
    ▼
Phase 6: Multi-Signal Evidence Fusion & Risk Calibration
    │
    ▼
Phase 7: Next.js + Cytoscape.js Interactive Visualizer
    │
    ▼
Phase 8: End-to-End Testing & Demo Simulation
```

---

## Detailed Phases

### Phase 1: Foundation & Scaffolding (Current Task)
- [x] Initial monorepo directory layout
- [x] Project architecture, data model, and roadmap documentation
- [x] `.gitignore`, `.env.example`, `docker-compose.yml` local environment harness
- [x] Service module boundaries setup without business logic

### Phase 2: Shared Schemas & Ingestion Service
- [ ] Define canonical Pydantic v2 data models in `packages/schemas/`:
  - `Event`, `MessagePayload`, `UrlPayload`, `PaymentPayload`
  - `EvidenceSignal`, `AssessmentResult`, `ScamJourney`
- [ ] Implement FastAPI ingestion endpoints (`services/api`):
  - `POST /api/v1/incidents/ingest`: Stream multi-channel events
  - `GET /api/v1/incidents/{id}/journey`: Retrieve current reconstructed journey
  - `GET /api/v1/incidents/{id}/assessment`: Retrieve dual-axis risk & confidence

### Phase 3: Neo4j Journey Graph & Entity Fusion Engine
- [ ] Neo4j async client and Cypher query builder (`services/graph-engine`):
  - Construct temporal sequences (`Step` -> `NEXT` -> `Step`)
  - Entity nodes: `Sender`, `Message`, `Url`, `Domain`, `UPIHandle`, `BankAccount`
  - Cross-incident entity fusion (detecting shared VPAs or phone numbers across independent targets)
  - Subgraph extraction for Cytoscape.js JSON format

### Phase 4: Multilingual Embeddings & Pattern Engine
- [ ] Multilingual embedding pipeline using `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`):
  - Support Hindi, Hinglish, English, and regional dialect scam templates
  - Store & query embeddings in PostgreSQL with `pgvector`
- [ ] Heuristic and semantic feature extraction:
  - Urgency & coercion cues
  - Impersonation classification (Bank, Electricity dept, Courier, Tax authority)
  - VPA mismatch detectors (e.g., claiming to be SBI but using personal handle)

### Phase 5: Investigation Service (TinyFish API)
- [ ] Integrate TinyFish API in `services/investigation`:
  - URL inspection, redirect-chain following
  - Domain age, registrar anomaly score, and hosting infrastructure analysis
  - Caching and rate-limit guardrails

### Phase 6: Multi-Signal Fusion & Dual-Axis Calibration
- [ ] Multi-signal correlation engine in `services/pattern-engine`:
  - Implement the fundamental rule: **No single model declares fraud**
  - Synthesize signals across all 7 dimensions
  - Output strict dual-axis: Risk (`LOW`/`MEDIUM`/`HIGH`) and Confidence (`LOW`/`MEDIUM`/`HIGH`)
  - Explicit fallback to `INSUFFICIENT_EVIDENCE`
  - Adaptive intervention recommender (reducing alert fatigue)

### Phase 7: Interactive Journey Visualizer (`apps/web`)
- [ ] Next.js (App Router) + Tailwind CSS dashboard:
  - **Scam Journey Graph**: Cytoscape.js directed chronological journey path
  - **Evidence Drawer**: Node-by-node inspection of raw signal provenance
  - **Risk & Confidence Badge**: Clear visual dual-axis indicator
  - **Intervention Simulator**: Live demo of how the system would prompt the user before a payment intent

### Phase 8: E2E Testing, Scenarios & Hackathon Presentation
- [ ] Pre-load realistic scam journeys in `data/`:
  - Scenario A: Electricity bill disconnection threat -> APK/phishing URL -> collect request
  - Scenario B: Work-from-home job scam -> Telegram -> bogus task platform -> crypto/UPI payment
  - Scenario C: Low-evidence / benign customer interaction (testing `INSUFFICIENT_EVIDENCE`)
- [ ] Benchmark query response time and graph traversal latency.
