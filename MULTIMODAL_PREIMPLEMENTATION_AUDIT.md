# ScamGraph AI — Multimodal Pre-Implementation Audit (Prompt 18 / Phase 5D)

**Date**: October 2026  
**Phase**: Pre-Implementation Audit for Multimodal Intelligence V2  
**Scope**: Executable Code Verification across Prompts 1 through 17

---

## 1. Upstream Dependency Integration Audit

| Subsystem / Phase | Source Path | Canonical Contract | Integration Status | Audit Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Data Foundation (Prompts 1–2)** | `packages/schemas/artifact.py`, `packages/schemas/events.py` | `Artifact`, `ArtifactType`, `ClaimEvidenceRecord` | **CONNECTED** | Clean base artifact contracts with provenance, SHA-256 hashing, and privacy classifications. |
| **Evaluation Integrity (Prompt 3)** | `packages/schemas/evaluation.py` | `EvaluationMetricReport`, `BenchmarkRun` | **CONNECTED** | Evaluator tests calibration, FPR, and gold sets independently from training. |
| **Model Arena (Prompt 5)** | `ml/embeddings/encoder.py`, `services/arena/` | `SemanticEncoder`, `multilingual-e5-small` | **CONNECTED** | Local SentenceTransformer with deterministic fallbacks and in-memory LRU caching. |
| **Entity Intelligence V2 (Prompt 6)** | `services/graph_engine/correlation/entity_service.py` | `Entity`, `EntityMention`, `CanonicalEntity` | **CONNECTED** | Normalizes UPI VPAs, phone numbers, URLs, domains, handles, and organization aliases across Indic variations. |
| **Tactic Intelligence (Prompt 7)** | `packages/schemas/tactics.py` | `TacticType` (20 tactics), `ActionRequestedType` (16 actions) | **CONNECTED** | Universal ontology independent of language and modality. |
| **Scam Journey Engine V1 (Prompt 8)** | `services/journey_engine/service.py` | `ScamJourney`, `JourneyEvent`, `JourneyStage` | **CONNECTED** | Ingests chronological multi-turn events, infers stage transitions, tracks monetization boundaries. |
| **ScamDNA V3 (Prompt 9)** | `services/dna_engine/builder.py`, `similarity.py` | `ScamDNA`, `DNADimension` (8 dimensions) | **CONNECTED** | Invariant behavioral fingerprinting weighting journey, tactics, and payment above raw text. |
| **Knowledge Graph V2 (Prompt 10)** | `services/graph_engine/` | `GraphNode`, `GraphEdge`, `Neo4j` adapter | **CONNECTED** | Connects incidents, entities, infrastructure, and claims with bounded traversals. |
| **Cross-Incident Correlation (Prompt 11)**| `services/correlation_engine/service.py` | `CorrelationScore`, `CandidateIncidentGroup` | **CONNECTED** | Multi-signal correlation combining entities, DNA, journey, and temporal proximity. |
| **Campaign Intelligence V2 (Prompt 12)** | `services/campaign_engine/discovery.py` | `ScamCampaign`, `CampaignLifecycleState` | **CONNECTED** | Clusters correlated candidate groups, computes velocity, outbreak status, and resurgence. |
| **Outbreak Radar (Prompt 12)** | `packages/schemas/radar.py`, `services/radar/` | `RadarSnapshot`, `CampaignVelocity` | **CONNECTED** | Provides near-real-time campaign tracking, velocity indicators, and language/channel mix. |
| **Unified Risk + Urgency (Prompt 13)** | `services/risk_engine/unified_engine.py` | `UnifiedRiskAssessment`, `TripartiteDecision` | **CONNECTED** | Sole authoritative fused risk decision engine across all intelligence subsystems. |
| **Contextual Intervention (Prompt 14)** | `services/intervention_engine/service.py` | `ContextualInterventionDecision` | **CONNECTED** | Adaptive friction, cooling-off delays, payment-pause barriers, and safety warnings. |
| **Pre-Payment Guard & Protect (Prompt 15)**| `apps/web/app/shield/`, `components/shield/` | `UniversalCheckResult`, `GuardDecision` | **CONNECTED** | Consumer-facing instant verification with high-stakes pre-loss protection. |
| **ScamGraph Rescue (Prompt 16)** | `services/rescue_engine/service.py` | `LossEvent`, `RescueTimeline`, `CasePackage` | **CONNECTED** | Post-loss triage, 1930 emergency dialer, evidence preservation, recovery scam warnings. |
| **Multilingual Intelligence V2 (Prompt 17)**| `services/language_intelligence/service.py` | `LanguageProfile`, `MultilingualTextRepresentation`, `NegationSignal` | **CONNECTED** | Indic normalizer, Devanagari/Latin/Bengali script detection, Hinglish code-mix scoring, protective negation. |

---

## 2. Pre-Implementation Recommendations for Prompt 18

1. **Re-use Existing `Artifact` Parent**: Do not create disjoint `ScreenshotRecord` or `VoiceRecord` tables; extend `ArtifactType` and attach `DerivedObservation` objects linked to the parent `artifact_id`.
2. **Preserve Raw Evidence**: Store original media files immutably; derived OCR text, QR payloads, transcripts, and bounding boxes are child observations.
3. **Multilingual Flow for Modalities**:
   - Screenshot $\to$ OCR $\to$ `LanguageIntelligenceService` (normalizer + negation).
   - Audio $\to$ STT $\to$ `LanguageIntelligenceService` (normalizer + negation).
4. **Prevent Double-Counting in Evidence Fusion**: A screenshot, its OCR text, and a phone number extracted from the OCR text must be recognized as a single evidence chain, not three independent corroborating sources.
5. **Strict Security Boundaries**:
   - No biometric facial recognition or voiceprints.
   - Decompress bomb protection for images.
   - Safe QR parsing without auto-executing payments or auto-browsing URLs.
   - Treat in-image text as untrusted evidence to defeat prompt injections.
