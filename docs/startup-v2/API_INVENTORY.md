# ScamGraph AI — API Inventory & Contract Audit
**Phase 0A: Baseline Audit Artifact**  
**Date:** October 24, 2026

---

## 1. FastAPI Endpoints Inventory (Port 8001)

| HTTP Method | Route | Endpoint Handler | Domain | Auth Required | Persistence Mechanism | Real / Demo Status | Target Classification |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `GET` | `/` | `root_handler` | System | None | In-memory metadata | Real | System / Health |
| `GET` | `/health` | `health_handler` | System | None | In-memory ping | Real | System / Health |
| `POST` | `/api/v1/investigate` | `investigate_incident` | Investigation | None | In-memory incident buffer | Real Orchestrator + Heuristics | Consumer / Analyst Core |
| `POST` | `/api/v1/analyze/url` | `analyze_url_endpoint` | Investigation | None | Stateless | Real Heuristic Evaluation | Internal / Extractor |
| `POST` | `/api/v1/analyze/message` | `analyze_message_endpoint` | Investigation | None | Stateless | Real NLP Model Evaluation | Internal / Extractor |
| `GET` | `/api/v1/incidents` | `list_incidents` | Incidents | None | In-memory dictionary repository | Real (Falls back to empty/mock) | Analyst |
| `GET` | `/api/v1/incidents/{id}` | `get_incident` | Incidents | None | In-memory dictionary repository | Real (Falls back to 404) | Analyst |
| `POST` | `/api/v1/incidents/ingest` | `ingest_incident` | Incidents | None | In-memory dictionary repository | Real Ingestion | Enterprise / Ingestion |
| `GET` | `/api/v1/campaigns` | `get_campaigns` | Threat Intel | None | In-memory clustering | Partial (Clustering on active memory) | Analyst |
| `GET` | `/api/v1/graph/query` | `query_graph` | Graph | None | Neo4j client (Falls back to memory) | Hybrid / Demo Fallback | Analyst / Exploration |
| `GET` | `/api/v1/graph/stats` | `get_graph_stats` | Graph | None | Neo4j client (Falls back to memory) | Hybrid / Demo Fallback | Analyst / Monitoring |
| `GET` | `/api/v1/registry/entries` | `list_registry_entries` | Registry | None | In-memory registry repository | Partial / In-Memory | Trust & Safety |
| `POST` | `/api/v1/registry/entries` | `create_registry_entry` | Registry | None | In-memory registry repository | Partial / In-Memory | Trust & Safety |
| `GET` | `/api/v1/simulator/scenarios` | `list_scenarios` | Simulation | None | Static YAML/JSON filesystem read | Real | Consumer Lab / Demo |
| `POST` | `/api/v1/simulator/start` | `start_simulation` | Simulation | None | In-memory session state | Real Interactive Session | Consumer Lab / Demo |
| `POST` | `/api/v1/simulator/decision` | `submit_decision` | Simulation | None | In-memory session state | Real Interactive Session | Consumer Lab / Demo |
| `POST` | `/api/v1/mule/evaluate` | `evaluate_mule_account` | Mule Engine | None | Stateless heuristic model | Experimental / Demo | Enterprise AML |
