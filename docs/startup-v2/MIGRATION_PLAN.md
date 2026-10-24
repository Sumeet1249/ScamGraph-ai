# ScamGraph AI — Migration & Module Action Plan
**Phase 0A: Baseline Audit Artifact**  
**Date:** October 24, 2026

---

## 1. Module Classification & Lifecycle Strategy

| Module / Component | Path | Current Classification | Proposed Action | Rational & Target State |
| :--- | :--- | :--- | :--- | :--- |
| **Pydantic Schemas** | `packages/schemas/` | `VERIFIED_IMPLEMENTED` | **KEEP** | **COMPLETED (Phase 0B & 0D)**: Core contracts extended to V2 (`Artifact`, `Entity`, `Incident`, `ScamGraphRecordV2`, `Conversation`, `TacticType`, `PaymentContextRecord`, `ClaimEvidenceRecord`, `CampaignRecord`, `ProductEvent`). Legacy interfaces 100% backward-compatible. |
| **Data Platform & Adapters** | `packages/data_platform/` | `NEW` | **KEEP** | **COMPLETED (Phase 0D)**: Implemented `DatasetAdapter` base and concrete adapters for `scam_ham_india`, `synthetic_audited`, `icfd_31k`, and `hinglish_scam`. Implemented quality and cross-dataset contamination auditor. |
| **Dataset Candidate Registry**| `data/registry/candidates.yaml`| `NEW` | **KEEP** | **COMPLETED (Phase 0D)**: Evaluated external datasets (`scamshield-dataset`, `icfd-31k`, `hinglish-scam-text-dataset`) with license, provenance, and intended/prohibited uses. |
| **Dataset Registry** | `data/registry/datasets.yaml` | `VERIFIED_IMPLEMENTED` | **KEEP + IMPROVE** | **COMPLETED (Phase 0B)**: Upgraded to v2.0.0 with truthful provenance (`PUBLIC_MIXED`, `SYNTHETIC_LLM`), training/eval approvals, and validation CLI. |
| **Model Registry** | `data/registry/models.yaml` | `NEW` | **KEEP** | **COMPLETED (Phase 0B)**: Model Registry v1.0.0 created with baseline, candidate, rejected statuses and machine-readable manifest (`model_manifest.json`). |
| **Privacy & Masking** | `packages/utils/privacy.py` | `NEW` | **KEEP** | **COMPLETED (Phase 0B)**: Masking for phones, emails, VPAs, accounts, and deterministic canonical hashing implemented and verified. |
| **Message ML Classifier** | `ml/message/` | `PRODUCTION_CANDIDATE` | **KEEP + IMPROVE** | **COMPLETED (Phase 0E)**: Preserved baseline TF-IDF. Built Benchmark Arena (`ml/evaluation/arena/`) evaluating baseline vs char-TF-IDF vs ensemble vs transformer. Word+Char ensemble approved for Tier 1 (<5ms CPU, 0.0% hard-negative FPR). |
| **Production Inference & Router** | `packages/inference/` | `NEW` | **KEEP** | **COMPLETED (Phase 0E)**: 4-tier inference architecture implemented with Fast Path, Deep Path, disagreement escalation, fallback degraded mode, and deterministic cache. |
| **Entity Intelligence V2** | `services/entity_intelligence/` | `NEW` | **KEEP** | **COMPLETED (Phase 1A)**: Comprehensive entity intelligence module (17 entity types, deterministic normalizers, exact/alias resolution, fuzzy review gating, temporal decay reputation, authoritative directory verification, cross-incident graph correlation, privacy masking & anti-enumeration defense). |
| **Tactic Intelligence Engine V2** | `ml/tactics/`, `services/tactic_intelligence/` | `NEW` | **KEEP** | **COMPLETED (Phase 1B)**: Human manipulation & tactic intelligence engine (20 canonical tactics, 17 requested actions, 38 multi-lingual rules, semantic prototypes, multi-message conversation timelines, manipulation density, escalation detection, anti-isolation intervention candidates, consumer/analyst serializers). |
| **Scam Journey Engine V1** | `services/journey_engine/`, `packages/schemas/journey.py` | `NEW` | **KEEP** | **COMPLETED (Phase 2A)**: Scam journey engine (15 canonical stages, 5 family templates, out-of-order temporal reasoning, prefix evaluation with anti-leakage, monetization boundary detection, pre-loss detection rate, warning lead time calculation, consumer progress meter DTO, analyst forensic views). |
| **ScamDNA V3 Engine** | `services/dna_engine/`, `packages/schemas/dna.py` | `NEW / EVOLVED` | **KEEP** | **COMPLETED (Phase 2B)**: ScamDNA V3 multi-dimensional behavioral fingerprinting engine (8 decoupled dimensions, dynamic missing-dimension weight re-normalization, candidate index retrieval, bidirectional V2 adapter, mutation detection, contradiction penalties, consumer & analyst views). |
| **Pattern Taxonomy** | `data/patterns/*.yaml` | `VERIFIED_IMPLEMENTED` | **KEEP** | Genuine high-value taxonomy of Indian scam progressions (KYC, Digital Arrest, Job Scams). |
| **FastAPI Core App** | `services/api/app/main.py` | `VERIFIED_IMPLEMENTED` | **KEEP + IMPROVE** | Clean routing structure. Add auth middleware, rate-limiting, and error envelope handling. |
| **Investigation Orchestrator** | `services/investigation/orchestrator.py` | `PARTIALLY_IMPLEMENTED` | **KEEP + IMPROVE** | Essential evidence synthesis logic. Harden SSRF controls and introduce async task dispatch. |
| **Risk Scoring Engines** | `services/risk_engine/`, `services/pattern-engine/matcher/risk_engine*` | `DUPLICATED` | **MERGE / REFACTOR** | Consolidate 3 competing risk scorers into a single canonical engine with unambiguous weights. |
| **Payment Classifier** | `ml/payment/classifier.py` | `DEMO_ONLY` / `HEURISTIC` | **REFACTOR** | Relabel as `HeuristicPaymentScorer`. Remove false "ML" claims until trained on transaction datasets. |
| **URL Classifier** | `ml/url/classifier.py` | `DEMO_ONLY` / `HEURISTIC` | **REFACTOR** | Relabel as `HeuristicURLScorer`. Decouple rule biases from ML claims. |
| **Vector Storage** | `services/storage/vector/` | `PARTIALLY_IMPLEMENTED` | **KEEP + IMPROVE** | Make PostgreSQL + `pgvector` the primary backend; keep NumPy array store purely as unit test fixture. |
| **Incident Repository** | `services/api/app/repository/memory.py` | `IN_MEMORY` | **REFACTOR** | Migrate to PostgreSQL SQLAlchemy ORM persistence with Alembic migrations. |
| **Graph Engine** | `services/graph-engine/` | `HYBRID` / `DEMO_FALLBACK` | **REFACTOR** | Decouple `neo4j` import to eliminate test collection crashes. Standardize graph queries. |
| **Mule Hunter Engine** | `services/mule_engine/` | `EXPERIMENTAL` | **DEMOTE** | Demote from consumer core path to enterprise research roadmap. Out of scope for pre-payment intervention. |
| **Scenario Runner** | `services/simulation/` | `VERIFIED_IMPLEMENTED` | **KEEP** | Powers the interactive consumer education lab (`/lab`). Keep as interactive simulation tool. |
| **Next.js Web Frontend** | `apps/web/` | `PARTIALLY_IMPLEMENTED` | **KEEP + IMPROVE** | Fix TypeScript type error in `app/incidents/[id]/page.tsx`, remove fake mock falls-backs, polish consumer UX. |
