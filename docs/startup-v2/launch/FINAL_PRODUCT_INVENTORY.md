# FINAL PRODUCT INVENTORY
**ScamGraph AI — Comprehensive Startup Product Catalog**
*Document Version: 5.0.0 | Date: 2026-10-24*

---

## 1. Product Surfaces & Capabilities

| Surface / Feature | Target Audience | Canonical Route / API | Backend Engine | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Home Landing** | Consumers / Enterprise | `/` | Next.js App Router | **PRODUCTION_READY** |
| **Protect** | Consumers (Pre-loss) | `/protect`, `POST /api/v1/analyze` | `UnifiedRiskEngine` + `LanguageIntelligence` | **PRODUCTION_READY** |
| **Pre-Payment Guard** | Consumers / Banks | `/guard`, `POST /api/v1/enterprise/guard`| `ContextualInterventionService` | **PRODUCTION_READY** |
| **ScamGraph Rescue** | Victims (Post-loss) | `/rescue`, `POST /api/v1/rescue/triage` | `RescueEngineService` | **PRODUCTION_READY** |
| **Activity History** | Registered Consumers | `/activity`, `GET /api/v1/incidents` | Keyset Pagination Database Query | **PRODUCTION_READY** |
| **Command Center** | Fraud Analysts | `/console` | `ConsoleIntelligenceService` | **PRODUCTION_READY** |
| **Outbreak Radar** | Analysts & Partners | `/radar` | `CampaignDiscoveryEngine` + Redis Snapshot| **PRODUCTION_READY** |
| **Campaign Workspace**| Analysts | `/campaigns/:id` | `CampaignEngine` + Distributed Lock | **PRODUCTION_READY** |
| **Investigation Graph**| Senior Analysts | `/investigate` | Neo4j Topology Repository | **PRODUCTION_READY** |
| **Enterprise API** | Banks / Fintechs / Telcos| `/docs`, `POST /api/v1/enterprise/*` | `EnterprisePlatformService` (API Keys/RBAC) | **PRODUCTION_READY** |
| **Outbound Webhooks** | Partner Threat Systems | `POST /api/v1/webhooks` | `WebhookWorker` with HMAC-SHA256 | **PRODUCTION_READY** |
| **Multilingual Engine** | Pan-India Users | Header Language Selector | Indic Normalizer (EN, HI, HI-Latn, BN) | **PRODUCTION_READY** |
| **Multimodal Engine** | Screenshot / Audio Users| File Upload Modals | `OCRWorker` + `STTWorker` + Fusion | **PRODUCTION_READY** |
| **Evidence Archive** | Compliance / Victims | `/api/v1/evidence/exports` | `ExportWorker` (Encrypted AES-256 ZIP) | **PRODUCTION_READY** |
