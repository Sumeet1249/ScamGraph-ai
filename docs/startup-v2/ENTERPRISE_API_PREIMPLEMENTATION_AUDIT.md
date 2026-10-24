# Enterprise API Platform V2 — Pre-Implementation Audit (Phase 6B)

## 1. Executive Summary

This audit validates the readiness of the entire ScamGraph intelligence stack (Prompts 1 through 19) before productizing it into the **Enterprise API & SDK Platform V2 (Phase 6B)**.

The enterprise API is a **product surface**, NOT a duplicate intelligence engine. It wraps canonical domain services in customer-safe Data Transfer Objects (DTOs), API key authentication, rate-limiting contracts, SSRF-hardened networking, and verifiable webhook delivery.

---

## 2. Canonical Intelligence Dependencies Audit

| Intelligence Layer | Canonical Implementation | Enterprise API Product Consumer | Status |
| :--- | :--- | :--- | :--- |
| __Entity Intelligence V2__ | `EntityIntelligenceService` (`services/entity_engine/`) | `POST /api/v1/entities/check`, Guard VPA verification | __CONNECTED__ |
| __Tactic & Negation Engine__ | `LanguageIntelligenceService` (`services/language_intelligence/`) | `POST /api/v1/check` behavioral extraction | __CONNECTED__ |
| __Journey Engine V1__ | `JourneyEngineService` (`services/journey_engine/`) | `POST /api/v1/journey/analyze`, Guard stage proximity | __CONNECTED__ |
| __ScamDNA V3__ | `ScamDNAService` (`services/scam_dna/`) | Customer-safe behavioral similarity & cluster matching | __CONNECTED__ |
| __Knowledge Graph V2__ | `KnowledgeGraphService` (`services/graph-engine/`) | 1-hop / 2-hop entity network relationships | __CONNECTED__ |
| __Cross-Incident Correlation__ | `CrossIncidentCorrelationService` (`services/correlation/`) | `POST /api/v1/network/check` network signals | __CONNECTED__ |
| __Campaign Intelligence V2__ | `CampaignIntelligenceService` (`services/campaign_engine/`) | `GET /api/v1/campaigns`, Outbreak intelligence feeds | __CONNECTED__ |
| __Unified Decision Engine__ | `UnifiedDecisionService` (`services/risk_engine/unified_decision.py`) | Tripartite assessment ($R, C, U$) for Check & Guard | __CONNECTED__ |
| __Intervention Engine__ | `ContextualInterventionService`, `PrePaymentGuardService` | Pre-Payment Guard actions (0–6 friction levels) | __CONNECTED__ |
| __Rescue Engine__ | `RescueService` (`services/rescue/`) | Post-loss triage, NCRP/1930 packaging | __CONNECTED__ |
| __Multilingual Intelligence__ | `LanguageIntelligenceService` | Hindi, Hinglish, Bengali Unicode request processing | __CONNECTED__ |
| __Multimodal Intelligence__ | `MultimodalIntelligenceService` (`services/multimodal/`) | Async artifact uploads (Screenshot OCR, QR, Call STT) | __CONNECTED__ |
| __Console Intelligence__ | `ConsoleIntelligenceService` (`services/console/`) | Internal / Analyst telemetry and review queue | __CONNECTED__ |

---

## 3. Route Classification Audit

| Existing Route | Current Classification | Enterprise Platform Strategy |
| :--- | :--- | :--- |
| `/api/v1/analyze` | Legacy Internal | Maintain for backward compatibility; route via UnifiedDecision |
| `/api/v1/investigate` | Public Web Product | Retain for consumer & demo web apps |
| `/api/v1/incidents` | Core Data | Expose only customer-safe pseudonymized incidents |
| `/api/v1/campaigns` | Core Intelligence | Wrap in `EnterpriseCampaignSummary` & detail DTOs |
| `/api/v1/radar` | Visual Intelligence | Expose clean outbreak alerts stream via `/api/v1/outbreak/feed` |
| `/api/v1/entities` | Core Intelligence | Elevate to enterprise `/api/v1/entities/check` with anti-harvesting |
| `/api/v1/risk` | Legacy Scorer | Deprecate in favor of canonical `UnifiedDecision` |
| `/api/v1/payment-guard` | Core Intervention | Elevate to enterprise `/api/v1/guard/check` with fast-path latency |
| `/api/v1/multimodal` | Media Pipeline | Connect to `/api/v1/artifacts` and async `AnalysisJob` |
| `/api/v1/console` | Analyst Only | Restrict to authorized internal operations console |
| `/api/v1/simulator` | Developer / Lab | Keep isolated from production enterprise gateway |
