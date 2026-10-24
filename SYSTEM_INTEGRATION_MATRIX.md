# ScamGraph AI — System Integration Matrix (Prompts 1–17)

## Complete Pipeline Connection Audit

This document serves as the formal architectural proof of integration across all 17 phases of ScamGraph AI, demonstrating runtime data flow from raw input through multilingual intelligence, entity extraction, journey modeling, behavioral ScamDNA, correlation, campaign intelligence, unified assessment, and localized consumer interventions.

```
INPUT
  │
  ▼
Artifact / Event Store (Prompts 1–2)
  │
  ▼
Language Intelligence Service (Prompt 17)
  ├── ScriptDetector (Latin, Devanagari, Bengali, Mixed)
  ├── IndicTextNormalizer (NFKC, zero-width stripping, token preservation)
  ├── LanguageIntelligenceDetector (Hinglish, Hindi, English, Bengali)
  ├── ProtectiveNegationEngine (Mandatory advisory distinction)
  └── Transliteration & Lexicon Translation Adapters
  │
  ▼
Entity Intelligence V2 (Prompt 6)
  └── Canonical entity mapping (UPI, URLs, phones, handles, brands)
  │
  ▼
Message & Semantic Intelligence (Prompts 4–5)
  └── Multilingual semantic embeddings (multilingual-e5-small)
  │
  ▼
Human Manipulation & Tactic Intelligence (Prompt 7)
  └── 20 Canonical tactics mapped from multilingual evidence spans
  │
  ▼
Scam Journey Engine V1 (Prompt 8)
  └── Single coherent journey across multi-turn cross-language switches
  │
  ▼
ScamDNA V3 Behavioral Fingerprint (Prompt 9)
  └── 8-Dimensional behavior vector invariant to wording & language
  │
  ▼
India Scam Knowledge Graph V2 (Prompt 10)
  └── Graph topology & multi-hop entity linkage
  │
  ▼
Cross-Victim / Incident Correlation Engine (Prompt 11)
  └── Multi-signal correlation surviving language variations
  │
  ▼
Campaign Intelligence V2 & Outbreak Radar (Prompt 12)
  └── Aggregates multi-language incidents without cluster fragmentation
  │
  ▼
Unified Risk + Confidence + Urgency Engine (Prompt 13)
  └── Language-invariant fused risk scoring & tripartite decisions
  │
  ▼
Contextual Intervention Engine (Prompt 14)
  └── Adaptive friction, cooling-off delays, localized safety guidance
  │
  ▼
Protect & Pre-Payment Guard / ScamGraph Rescue (Prompts 15–16)
  └── Localized UI, emergency triage with exact 1930 preservation
```

---

## Connection Verification Table

| Upstream Producer | Produced Contract | Downstream Consumer | Runtime Call | Verification Test | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Language Intelligence** | `LanguageProfile`, `MultilingualTextRepresentation` | **Entity Intelligence** | `EntityNormalizer.normalize(text)` | `test_indic_normalization_preserves_security_tokens` | **CONNECTED** |
| **Language Intelligence** | `BehavioralFeatureSet` | **Message & Semantic ML** | `semantic_encoder.encode(rep.semantic_input_text)` | `test_cross_language_scamdna_similarity` | **CONNECTED** |
| **Language Intelligence** | `NegationSignal`, normalized tokens | **Tactic Engine** | `tactic_detector.detect(features)` | `test_legitimate_bank_warning_collision_avoidance` | **CONNECTED** |
| **Language Intelligence** | Extracted Tactics & Actions | **Journey Engine** | `JourneyEngineService.create_journey(events)` | `test_cross_language_conversation_single_journey` | **CONNECTED** |
| **Journey + Tactics + Entities** | Multi-Dimensional Features | **ScamDNA V3** | `ScamDNABuilder.build(...)` | `test_cross_language_scamdna_similarity` | **CONNECTED** |
| **ScamDNA V3** | `ScamDNA` | **Correlation Engine** | `ScamDNASimilarityEngine.compare(dna1, dna2)` | `test_language_only_negative_no_false_correlation` | **CONNECTED** |
| **Correlation Engine** | `CandidateIncidentGroup` | **Campaign Engine** | `CampaignDiscoveryEngine.evaluate_candidate_group(grp)` | `test_cross_language_campaign_continuity` | **CONNECTED** |
| **Campaign Engine** | `ScamCampaign` | **Outbreak Radar** | `RadarService.get_campaign_breakdown()` | `test_radar_campaign_velocity` | **CONNECTED** |
| **Multi-Subsystem** | Fused Evidence | **Unified Risk (Phase 4A)** | `UnifiedRiskEngine.assess(req)` | `test_tripartite_decision` | **CONNECTED** |
| **Unified Risk** | `TripartiteDecision` | **Contextual Intervention (Phase 4B)** | `ContextualInterventionService.evaluate(...)` | `test_contextual_interventions` | **CONNECTED** |
| **Intervention Engine** | Localized Safety Catalog | **Protect & Guard UI (Phase 5A)** | Header Language Selector $\to$ Localized Interventions | Browser Visual QA (`multilingual_investigate_qa`) | **CONNECTED** |
| **Rescue Engine** | Emergency Triage Plan | **Rescue UI (Phase 5B)** | `RescueService.get_action_plan(iid)` | `test_rescue_triage_hindi_report` | **CONNECTED** |
| **Multimodal Service** | `ExtractedObservations` | **Downstream Journey & DNA** | `MultimodalService.process_artifact(...)` | `test_multimodal_intelligence_step18.py` | **CONNECTED** |
| **Enterprise Platform** | `ApiKeyRecord`, `TenantContext` | **Enterprise API Gateway** | `EnterprisePlatformService.authenticate_api_key(...)` | `test_enterprise_platform_step20.py` | **CONNECTED** |
| **Security Governance** | `PrincipalContext`, `RBAC` | **Data Access Layer** | `SecurityService.authorize_evidence_access(...)` | `test_security_governance_step21.py` | **CONNECTED** |
| **Job Queue (Phase 7B)** | `QueueMessage`, `JobPriority` | **Background Worker Pool** | `JobQueue.dequeue(worker_class)` | `test_req_1_screenshot_async_analysis` | **CONNECTED** |
| **Cache Manager (Phase 7B)** | `TenantIsolatedCache` | **API & Worker Coordination** | `CacheManager.get_or_compute(...)` | `test_req_17_tenant_cache_isolation` | **CONNECTED** |
| **Campaign Worker (Phase 7B)** | `OutbreakEvent` | **Partner Webhook Delivery** | `WebhookWorker.execute_job(...)` | `test_req_11_signed_webhook_delivery` | **CONNECTED** |
| **Telemetry (Phase 7C)** | `SanitizedJSONLog` | **Central Log Aggregation** | `TelemetrySanitizer.sanitize_dict(...)` | `test_req_23_telemetry_redaction_secrets` | **CONNECTED** |
| **Trace Context (Phase 7C)**| `SpanRecord` | **Async Queue & Workers** | `TraceContext.start_span(...)` | `test_req_2_trace_continuity_across_queue` | **CONNECTED** |
| **AI Quality (Phase 7C)** | `GoldenRegressionReport`| **CI/CD Release Gate** | `AIQualityEngine.run_golden_regression(...)`| `test_req_22_critical_regression_blocks_release` | **CONNECTED** |
| **Drift Detector (Phase 7C)**| `DriftAlert` | **Command Center & Runbooks** | `DriftDetector.evaluate_campaign_drift(...)` | `test_req_19_scamdna_cluster_drift` | **CONNECTED** |
| **Health Service (Phase 7C)**| `SLORecord`, `HealthStatus` | **Operator Inspection Endpoints**| `HealthCheckService.check_deep_health()` | `test_req_11_radar_freshness_transition` | **CONNECTED** |
| **Circuit Breaker (Phase 7D)**| `CircuitState` | **Provider Call Wrapper** | `CircuitBreaker.can_execute()` | `test_load_8_provider_slowdown_circuit_breaker` | **CONNECTED** |
| **Backpressure (Phase 7D)** | `DegradationLevel`, `Admission`| **Job Enqueue & API Gateway** | `BackpressureController.evaluate_admission()` | `test_load_30_load_shedding_critical_safety_priority` | **CONNECTED** |
| **Capacity Engine (Phase 7D)**| `ScaleScenarioReport` | **Financial & Infrastructure Ops** | `CapacityModelEngine.calculate_scenario()` | `test_load_35_capacity_model_10k_dau` | **CONNECTED** |
| **Final Launch Gate (Phase 7F)**| `CONDITIONAL_GO`, `CLOSED_BETA`| **Authoritative Launch Core** | `tests/scenarios/test_launch_e2e_step26.py` | `test_final_e2e_1_unknown_text_protect` | **CONNECTED** |
