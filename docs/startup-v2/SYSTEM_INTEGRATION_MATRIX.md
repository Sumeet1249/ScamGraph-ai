# ScamGraph AI — System Integration Matrix (Phase 3C Audit)

## 1. Executive Summary

This matrix represents the authoritative integration audit of all core intelligence layers implemented across **Phases 0A through 3B**, verifying runtime callers, downstream consumers, data schemas, persistence tiers, and test coverage before constructing **Campaign Intelligence V2** and the **Scam Outbreak Radar**.

---

## 2. Comprehensive System Integration Matrix

| Component | Input | Output | Caller | Downstream Consumer | Schema | Persistence | API Endpoint | Test Coverage | Status |
|---|---|---|---|---|---|---|---|---|---|
| **Data Foundation V2** | Raw artifacts, events, transcripts | Normalized `Event`, `Artifact`, `ProvenanceRecord` | Ingestion pipeline, test fixtures | Entity Intelligence, Tactic Intelligence | `packages/schemas/events.py`, `signals.py` | PostgreSQL / In-Memory | `/api/v1/incidents/{id}/events` | `test_data_foundation_v2.py` (7 tests) | **CONNECTED** |
| **Dataset Registry V2** | `data/registry/datasets.yaml` | Validated dataset metadata with provenance | Model Benchmark Arena, Training | Evaluation Harness | `packages/schemas/dataset.py` | YAML Catalog | CLI Validator | `test_data_foundation_v2.py` | **CONNECTED** |
| **Model Registry & Arena** | Candidate model binaries, benchmark sets | Scorecards, promotion decisions | Benchmark runner, Model Router | Model Router | `packages/schemas/model_lineage.py` | `model_manifest.json` | Internal | `test_model_benchmark_arena_step5.py` (13 tests) | **CONNECTED** |
| **Inference Router** | Text / payload | Scored inference with fast/deep tier | Message Classifier | Tactic Engine, Investigation | `packages/inference/router.py` | Memory Cache | Internal | `test_model_benchmark_arena_step5.py` | **CONNECTED** |
| **Entity Intelligence V2** | Text, events, URLs, payment metadata | Canonicalized entities (`Phone`, `UPI`, `Domain`) | Message extractor, URL service | Journey Engine, ScamDNA, Correlation | `packages/schemas/entity.py` | Neo4j / In-Memory | `/api/v1/entities` | `test_entity_intelligence_step6.py` (16 tests) | **CONNECTED** |
| **Tactic Intelligence Engine** | Message text, conversation timelines | 20 canonical tactics, requested actions | Event ingestion, Timeline builder | Journey Engine, ScamDNA | `packages/schemas/signals.py`, `TacticType` | Memory / Cache | `/api/v1/incidents/{id}/tactics` | `test_tactic_intelligence_step7.py` (15 tests) | **CONNECTED** |
| **Scam Journey Engine V1** | Chronological events, tactics, payments | `ScamJourney`, current stage, pre-loss warning | Incident timeline, Orchestrator | ScamDNA V3, Correlation Engine | `packages/schemas/journey.py` | PostgreSQL / Memory | `/api/v1/incidents/{id}/journey` | `test_journey_engine_step8.py` (16 tests) | **CONNECTED** |
| **ScamDNA V3 Engine** | Incident, Journey, Tactics, Entities | 8-dimension `ScamDNA`, `ScamDNAMatch` | Incident assessment, Rebuild trigger | Correlation Engine, Variant Detector | `packages/schemas/dna.py` | Inverted Index / Cache | `/api/v1/incidents/{id}/dna` | `test_scam_dna_v3_step9.py` (14 tests) | **CONNECTED** |
| **Knowledge Graph V2** | Incidents, Entities, Journeys, ScamDNA | Typed edges, 1-hop / 2-hop bipartite paths | Entity correlation, Path analysis | Correlation Engine, Cytoscape Canvas | `packages/schemas/graph.py` | Neo4j / InMemoryGraphRepo | `/api/v1/incidents/{id}/graph` | `test_neo4j_integration_step16.py` | **CONNECTED** |
| **Cross-Incident Correlation** | Incident pairs, Entities, ScamDNA, Time | `IncidentCorrelation`, `ConsumerNetworkSignal` | Correlation service, API | Campaign Intelligence V2, UI Radar | `packages/schemas/correlation.py` | Memory / Graph Edge | `/api/v1/incidents/{id}/related` | `test_correlation_engine_step11.py` (12 tests) | **CONNECTED** |
| **Campaign Intelligence V2** | `CandidateIncidentGroup`, Correlation Network | `ScamCampaign`, lifecycle states, mutations | Campaign Discovery Engine, Outbreak Radar | Outbreak Radar, Threat Feeds | `packages/schemas/campaign.py` | PostgreSQL / Memory | `/api/v1/campaigns` | `test_campaign_intelligence_step12.py` | **IMPLEMENTED (Phase 3C)** |
| **Scam Outbreak Radar** | Campaign velocity, burst acceleration | `OutbreakSignal`, Radar blips, summary | Outbreak Radar Service | Web UI (`/radar`), Analyst Command | `packages/schemas/radar.py` | Memory / Snapshots | `/api/v1/radar` | `test_campaign_intelligence_step12.py` | **IMPLEMENTED (Phase 3C)** |
| **Unified Decision Layer** | 7 Subsystem scores, counter-evidence, outbreak state | `TripartiteDecision` ($R, C, U$), `ActionDecision` | UnifiedDecisionService, Orchestrator | Contextual Intervention, Frontend UI | `packages/schemas/unified_decision.py` | Memory / Incident metadata | `/api/v1/risk/decision` | `test_unified_decision_step13.py` (8 tests) | **CONNECTED (Phase 4A)** |
| **Contextual Intervention** | `TripartiteDecision`, Journey stage, tactics, payment reason | `InterventionDecision`, `FrictionLevel` (0-6) | ContextualInterventionService, Orchestrator | Pre-Payment Guard, Consumer UX | `packages/schemas/contextual_intervention.py` | Memory / Incident session | `/api/v1/interventions/evaluate` | `test_contextual_intervention_step14.py` (15 tests) | **CONNECTED (Phase 4B)** |
| **Pre-Payment Guard** | `PrePaymentContext`, stated reason, recipient VPA | `GuardEvaluationResult`, `VerificationPlan` | PrePaymentGuardService, Banking Apps | UPI SDK, Consumer Warning Modal | `packages/schemas/contextual_intervention.py` | Memory / Audit logs | `/api/v1/payment-guard/check` | `test_contextual_intervention_step14.py` | **CONNECTED (Phase 4B)** |
| **TinyFish Web Investigator** | URLs, public web assets | DOM artifacts, screenshots, reputation | URL Analysis Service | Evidence Engine, Entity Extractor | `packages/schemas/evidence.py` | Local Artifacts | Internal Worker | `test_tinyfish_service.py` | **CONNECTED** |

---

## 3. Disconnected Interfaces Detected & Repaired

### Disconnection 1: Orchestrator Did Not Auto-Populate ScamDNA & Correlation
- **Before**: `services/investigation/orchestrator.py` executed URL analysis, TinyFish, PatternEngine V1, and RiskEngine V1, but did not register the incident with `ScamDNAService` or `CrossIncidentCorrelationService`.
- **After**: `orchestrator.py` connects `JourneyEngineService`, `ScamDNAService`, and `CrossIncidentCorrelationService`, populating full behavioral DNA and network correlation candidates during assessment.
- **Why**: Allows any assessed incident to immediately benefit from and contribute to the ScamGraph network effect.

### Disconnection 2: DBSCAN Campaign Clusterer Was Disconnected From Correlation
- **Before**: `services/graph-engine/campaigns/clusterer.py` was an isolated script computing raw cosine DBSCAN on embeddings without entity or journey context.
- **After**: Re-purposed as a candidate pre-clustering utility for `CampaignDiscoveryEngine`, while multi-signal evidence (`CandidateIncidentGroup`) governs campaign formation.
- **Why**: Prevents raw embeddings alone from fabricating false campaigns.

---

## 4. Legacy Duplication Audit Decisions

1. **FingerprintV2 vs ScamDNA V3**:
   - `ScamFingerprintV2` retained with bidirectional adapter (`ScamFingerprintV2Adapter`).
   - All new services and endpoints communicate using `ScamDNA` V3.
2. **Old Entity Correlation vs Correlation Engine V1**:
   - Raw entity counts in `EntityCorrelationService` retained for backward compatibility with Cytoscape graph nodes.
   - Cross-incident linking decisions delegate exclusively to `CrossIncidentCorrelationService`.
3. **Legacy Risk Scorers**:
   - Consolidated behind `EvidenceFusionEngine` and `InvestigationOrchestrator` to prepare for Phase 4A.
