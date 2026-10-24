# ScamGraph AI — Frontend Route & Navigation Inventory
**Phase 0A: Baseline Audit Artifact**  
**Date:** October 24, 2026

---

## 1. Current Frontend Routes Inventory (Next.js Port 3001)

| Route | Page Title / Purpose | Target User | Data Source | Real / Demo Status | Navigation Origin | Recommended Future Route |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | Landing / Hero Portal | Consumer / Public | Static marketing content | Real | Root Entry | `/` (Consumer landing) |
| `/investigate` | Multi-Signal Investigation Console | Consumer & Analyst | `/api/v1/investigate` | Real Backend Connected | TopNav / Hero CTA | `/check` (Consumer) & `/intelligence/investigate` (Analyst) |
| `/lab` | Interactive Scam Simulator | Consumer (Education) | `/api/v1/simulator/*` | Real Interactive Scenario | TopNav | `/learn` or `/simulator` (Consumer) |
| `/incidents` | Incident Audit Feed | Fraud Analyst | `/api/v1/incidents` | Partial (Mock fallback on empty) | TopNav | `/intelligence/incidents` (Analyst) |
| `/incidents/[id]` | Incident Detail & Counter-Evidence | Fraud Analyst | `/api/v1/incidents/{id}` | Real / Breaks build (`type error`) | Incidents list | `/intelligence/incidents/[id]` |
| `/campaigns` | Emerging Campaign Radar | Threat Intel Analyst | `/api/v1/campaigns` | Partial (Mock cards on empty) | TopNav | `/intelligence/campaigns` (Analyst) |
| `/graph` | Entity & Relationship Cytoscape Graph | Fraud Investigator | `/api/v1/graph/*` | Hybrid (In-memory/Neo4j fallback) | TopNav | `/intelligence/graph` (Analyst) |
| `/registry` | Scam Indicator Trust Registry | Trust & Safety Team | `/api/v1/registry/*` | In-memory CRUD backend | TopNav | `/intelligence/registry` (Analyst) |
| `/mulehunter` | Mule Ring & Account Graph Detector | Enterprise AML | `/api/v1/mule/*` | Experimental / Demo | TopNav | Demote to enterprise backlog |
| `/command` | Operations Command Center | Operations / Admin | Aggregate API queries | Experimental / Demo | TopNav | `/admin/operations` |
| `/shield` | Consumer Pre-Payment Shield | Consumer | Local heuristic checks | Demo Prototype | Direct link | `/protect` (Consumer) |

---

## 2. Recommended Persona Separation

Currently, consumer-facing tools (`/investigate`, `/shield`, `/lab`) and complex enterprise intelligence tools (`/mulehunter`, `/graph`, `/registry`, `/campaigns`) are intermingled in a single top navigation bar.

**Future Architecture Separation:**
- **Consumer Portal**:
  - `/` — Fast landing & scam alert feed
  - `/check` — Check a suspicious message, link, or UPI ID
  - `/protect` — Proactive device & payment shield
  - `/rescue` — Emergency post-fraud checklist (1930, bank helpline, Cyber Crime portal guide)
  - `/learn` — Interactive scam simulator
- **Enterprise / Analyst Console**:
  - `/intelligence/` — Overview & emerging threat radar
  - `/intelligence/investigate` — Deep-dive multi-signal analysis
  - `/intelligence/incidents` — Correlated victim incidents
  - `/intelligence/campaigns` — Unsupervised campaign clusters
  - `/intelligence/graph` — Multi-hop entity graph exploration
  - `/intelligence/registry` — Threat indicators & dispute management
