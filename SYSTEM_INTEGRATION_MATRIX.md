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
