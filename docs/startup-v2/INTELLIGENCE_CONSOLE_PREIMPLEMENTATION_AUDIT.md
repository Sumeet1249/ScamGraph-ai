# Intelligence Console V2 — Pre-Implementation Audit (Phase 6A)

## 1. Executive Summary
This audit validates the readiness of the ScamGraph AI intelligence stack (Prompts 1 through 18) before constructing the **ScamGraph Intelligence Console V2 (Phase 6A)**. The objective is to turn the foundational intelligence into an operational operating system for fraud analysts, cybercrime teams, banks, and trust & safety investigators.

---

## 2. Intelligence Foundation Subsystem Audit

| Subsystem | Verified Schemas & Contracts | Runtime Providers & Consuming Services | Classification |
| :--- | :--- | :--- | :--- |
| **Artifact & Provenance (Prompt 2)** | `packages/schemas/artifact.py`, `ProvenanceRecord` | `FileUploadSecurityValidator`, `EvidenceFusionEngine` | **CONNECTED** |
| **Event & Incident (Prompt 2)** | `packages/schemas/events.py`, `Incident` | `InvestigationOrchestrator`, `/api/v1/incidents` | **CONNECTED** |
| **Evidence & Claim (Prompt 2)** | `packages/schemas/signals.py`, `Claim`, `EvidenceLineage` | Evidence preservation, claim unverified flag | **CONNECTED** |
| **Entity Intelligence V2 (Prompt 6)** | `packages/schemas/entity.py` (`Phone`, `UPI`, `Domain`) | `EntityIntelligenceService`, canonical resolution | **CONNECTED** |
| **Tactic Intelligence (Prompt 7)** | `TacticType`, `ActionRequestedType` | `TacticDetector`, 20 canonical tactics | **CONNECTED** |
| **Journey Engine V1 (Prompt 8)** | `ScamJourney`, `JourneyStage`, pre-loss flags | `JourneyEngineService`, chronological timelines | **CONNECTED** |
| **ScamDNA V3 (Prompt 9)** | 8-dimension `ScamDNA`, cosine similarity | `ScamDNAService`, cross-incident matching | **CONNECTED** |
| **Knowledge Graph V2 (Prompt 10)** | Neo4j / InMemory bipartite relationships | `KnowledgeGraphService`, 1-hop / 2-hop paths | **CONNECTED** |
| **Cross-Incident Correlation (Prompt 11)** | `CandidateIncidentGroup`, `IncidentCorrelation` | `CrossIncidentCorrelationService`, entity overlap | **CONNECTED** |
| **Campaign Intelligence V2 (Prompt 12)** | `ScamCampaign`, lifecycle & activity states | `CampaignDiscoveryEngine`, velocity tracker | **CONNECTED** |
| **Scam Outbreak Radar (Prompt 12)** | `OutbreakSignal`, velocity & acceleration metrics | `OutbreakRadarService`, real-time updates | **CONNECTED** |
| **Unified Risk & Decision (Prompt 13)** | `TripartiteDecision` ($R, C, U$), calibrated thresholds | `UnifiedDecisionService`, counter-evidence | **CONNECTED** |
| **Intervention Engine (Prompt 14)** | `InterventionDecision`, friction levels 0–6 | `ContextualInterventionService`, Pre-Payment Guard | **CONNECTED** |
| **Protect Mode (Prompt 15)** | Universal consumer check, multi-signal ingestion | Consumer UX, risk explanation, guidance | **CONNECTED** |
| **ScamGraph Rescue (Prompt 16)** | `LossEvent`, `EmergencyActionPlan`, `RescueCasePackage` | `RescueService`, official 1930/NCRP preparation | **CONNECTED** |
| **Multilingual Intelligence (Prompt 17)** | Indic normalization, transliteration, protective negation | `LanguageIntelligenceService`, Hindi/Hinglish/Bengali | **CONNECTED** |
| **Multimodal Intelligence (Prompt 18)** | `DerivedObservation`, OCR, QR, ASR transcripts | `MultimodalIntelligenceService`, `EvidenceFusionEngine` | **CONNECTED** |

---

## 3. Frontend Route & Component Audit

| Route / Area | Current State | Audit Decision | Phase 6A Strategy |
| :--- | :--- | :--- | :--- |
| `/` | Landing page with ThreatNetworkScene & actions | **KEEP** | Enhance with operational telemetry snapshot |
| `/command` | National threat telemetry & stats | **IMPROVE** | Elevate to primary analyst Command Center with actionable queue |
| `/radar` | Regional velocity & outbreak radar | **IMPROVE** | Bind directly to backend Campaign + ScamDNA + Journey data |
| `/campaigns` | Campaign cluster table & filters | **IMPROVE** | Operational table with lifecycle & velocity sorts |
| `/campaigns/[id]` | Campaign detail view | **IMPROVE** | Full 10-tab investigation workspace (DNA, Journey, Network, Lineage) |
| `/incidents` | Incident list stream | **IMPROVE** | Bounded tables with risk, urgency, and review flags |
| `/incidents/[id]` | Incident detail view | **IMPROVE** | Unified multimodal timeline & evidence provenance trace |
| `/investigate` | Multi-signal composer & result | **IMPROVE** | 3-column analyst workspace with contextual graph & evidence drawer |
| `/graph` | Cytoscape interactive graph | **IMPROVE** | Bounded traversal, supernode filtering, and degraded-mode resilience |
| `/alerts` | Currently missing as dedicated route | **ADD** | Alert Center with deduplication, severity, and workflow states |
| `/reviews` | Embedded in registry | **ADD** | Dedicated Human-in-the-loop Review Center (Merge/Split, Correlation) |
| `/entities/[id]` | Entity details modal | **ADD** | Entity Workspace with timeline, reputation, and network context |
| `/cases` | Missing | **ADD** | Lightweight Case Management Foundation |
| `/mulehunter` | Mule account tracker | **KEEP / MERGE** | Connect entity insights into core graph explorer |
| `/registry` | ML model / dataset registry | **KEEP** | Retain for developer & ML ops workflows |
| `/shield` | Consumer protection prototype | **KEEP / MERGE** | Keep separated under consumer tools |
| `/lab` | Outbreak simulator lab | **KEEP** | Retain for synthetic experimentation |
