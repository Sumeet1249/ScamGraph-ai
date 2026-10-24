# ScamGraph AI — Reference Repository Deep Analysis

> **Scope**: Pure architectural & security research.  
> **Mandate**: DO NOT merge whole repositories. DO NOT copy full directory trees. DO NOT pollute the ScamGraph environment with foreign dependencies. Adapt harvested concepts behind ScamGraph canonical interfaces.

---

## 1. Repository-by-Repository Research Analysis

### 1.1 TinyFish Cookbook (`tinyfish-io/tinyfish-cookbook`)
- **License**: MIT
- **Languages / Frameworks**: Python, TypeScript, Node.js, HTTP SSE
- **Main Entry Points**: `skills/`, `AABW_Vietnam_Hackathon_Samples/`, `plugins/`
- **Reusable Algorithms**: DOM element selection recipes, form field detection heuristics, observable brand and text extraction prompts.
- **Reusable Schemas / Data Models**: JSON extraction schemas for web observables (inputs, buttons, forms, redirects).
- **External Dependencies**: `httpx`, `pydantic`, official TinyFish API client.
- **Security-Sensitive Code**:
  - API key handling (MUST remain strictly server-side in `services/investigation`).
  - Web fetching risk: must never trigger direct client browser requests.
- **Irrelevant to ScamGraph**: All unrelated vertical demo apps (e.g., `anime-watch-hub`, `district-rent-shark`, `lego-hunter`, `restaurant-comparison-tool`).
- **License Compatibility**: Fully compatible (MIT allows adaptation with copyright retention).
- **Integration Strategy**: **Type A / C** (Use API client directly behind ScamGraph `WebInvestigator` interface; adapt observable prompt/parsing concepts).
- **Code Reuse Status**: NO direct copy of demo apps. Reimplement canonical `WebInvestigator` client in `services/investigation/tinyfish/`.
- **Priority**: **P0 (Mandatory)**

---

### 1.2 PhishGraph (`AVII-VERSE/PhishGraph`)
- **License**: MIT
- **Languages / Frameworks**: Python 3.11+, FastAPI, SQLAlchemy, Alembic, dnspython, cryptography
- **Main Entry Points**: `app/main.py`, `app/analyzers/`, `app/security/url_safety.py`
- **Reusable Algorithms**:
  - `app/security/url_safety.py`: Strict SSRF protection, IP range checking (rejection of loopback, private, link-local, cloud metadata).
  - `app/analyzers/url_analyzer.py`: URL lexical feature extraction (entropy, hyphenation, brand typosquatting).
  - `app/analyzers/dns_analyzer.py`: Multi-record DNS resolution (A, AAAA, MX, NS, TXT).
  - `app/analyzers/tls_analyzer.py`: Certificate validity, issuer inspection, Let's Encrypt heuristic detection.
  - `app/analyzers/redirect_analyzer.py`: Redirect-chain hop counting and HTTP status code tracking.
- **Reusable Schemas / Data Models**: Typed analyzer result dataclasses.
- **External Dependencies**: `dnspython`, `cryptography`, `tldextract`, `urllib3`.
- **Security-Sensitive Code**: Network socket handling, DNS resolution timeout leaks, potential SSRF vectors if IP parsing is bypassed.
- **Irrelevant to ScamGraph**: Telegram bot (`app/bot/`), original database schema (`app/db/`), Nginx configurations, and custom UI.
- **License Compatibility**: Fully compatible (MIT).
- **Integration Strategy**: **Type C** (Reimplement DNS, RDAP, TLS, SSRF, and redirect concepts cleanly behind ScamGraph canonical interfaces).
- **Code Reuse Status**: Adapt small licensed helper algorithms in `services/investigation/url_analysis/` with authors credited.
- **Priority**: **P0 (Core)**

---

### 1.3 VECTPHISH (`AmadeusITGroup/VECTPHISH`)
- **License**: Apache-2.0
- **Languages / Frameworks**: Python, SentenceTransformers, scikit-learn (DBSCAN), SQLite, Streamlit
- **Main Entry Points**: `main.py`, `dashboard.py`
- **Reusable Algorithms**:
  - `SentenceTransformer` dense semantic vector generation.
  - Cosine distance calculation and pairwise distance matrices.
  - DBSCAN density clustering for grouping related phishing attempts into campaign clusters.
  - TF-IDF / keyword extraction for campaign naming.
- **Reusable Schemas / Data Models**: Campaign cluster metadata representation.
- **External Dependencies**: `sentence-transformers`, `scikit-learn`, `numpy`, `torch`.
- **Security-Sensitive Code**: Heavy memory allocation during large-scale pairwise distance matrix calculations (O($N^2$)).
- **Irrelevant to ScamGraph**: Streamlit interactive dashboard (`dashboard.py`), SQLite relational backend, email file parsing (.eml).
- **License Compatibility**: Fully compatible (Apache-2.0 requires attribution notice).
- **Integration Strategy**: **Type C** (Adapt the concept: pivot from *phishing email clustering* to *multi-stage scam incident clustering* using pgvector and SentenceTransformers).
- **Code Reuse Status**: Reimplement in `services/pattern-engine/semantic/` and `services/graph-engine/campaigns/`.
- **Priority**: **P0 (Core)**

---

### 1.4 Neo4j P2P Fraud (`neo4j-product-examples/demo-fraud-detection-with-p2p`)
- **License**: Apache-2.0
- **Languages / Frameworks**: Python, Cypher, Jupyter Notebooks, Neo4j Graph Data Science (GDS)
- **Main Entry Points**: `fraud-detection-demo-with-p2p.ipynb`, `abridged-demo/`
- **Reusable Algorithms**:
  - Entity resolution Cypher queries for shared identifiers (shared phone, device ID, card).
  - Weakly Connected Components (WCC) and Louvain community detection for identifying fraud rings.
  - Degree centrality and Jaccard similarity for linking coordinated accounts.
- **Reusable Schemas / Data Models**: Financial P2P graph schema (`Account`, `Customer`, `Device`, `Transaction`).
- **External Dependencies**: `neo4j` Python driver, Neo4j GDS library.
- **Security-Sensitive Code**: Large unindexed Cypher traversals that can cause memory spikes on unconstrained graph instances.
- **Irrelevant to ScamGraph**: Credit card chargeback workflows, Jupyter presentation formatting.
- **License Compatibility**: Fully compatible (Apache-2.0).
- **Integration Strategy**: **Type C** (Adapt Cypher entity-sharing patterns to ScamGraph nodes: `:Incident`, `:Sender`, `:UPIHandle`, `:Domain`).
- **Code Reuse Status**: Adapt Cypher queries into `services/graph-engine/neo4j/cypher_builder.py`.
- **Priority**: **P0 (Core)**

---

### 1.5 Cytoscape.js (`cytoscape/cytoscape.js`)
- **License**: MIT
- **Languages / Frameworks**: JavaScript / TypeScript, Canvas/WebGL rendering
- **Main Entry Points**: `dist/cytoscape.esm.js`
- **Reusable Algorithms**: Directed acyclic graph layout (`dagre`), physics force-directed layouts (`cose`, `cola`), shortest path highlighting.
- **Reusable Schemas / Data Models**: Canonical `elements: { nodes: [], edges: [] }` format.
- **External Dependencies**: npm package `cytoscape`, `cytoscape-dagre`.
- **Security-Sensitive Code**: DOM XSS if node labels or tooltips are injected without escaping.
- **Irrelevant to ScamGraph**: Desktop-specific legacy extensions.
- **License Compatibility**: Fully compatible (MIT).
- **Integration Strategy**: **Type A** (Use standard npm library directly in `apps/web/components/graph/`).
- **Code Reuse Status**: Directly import library into Next.js frontend.
- **Priority**: **P0 (Core)**

---

### 1.6 PaySim (`voutilad/PaySim`)
- **License**: MIT
- **Languages / Frameworks**: Python, Java, Agent-based simulation
- **Main Entry Points**: Synthetic financial simulation generators
- **Reusable Algorithms**: Behavioral financial transaction generation, transfer vs cash-out timing patterns, merchant vs individual account ratios.
- **Reusable Schemas / Data Models**: Transaction tuples (`step`, `type`, `amount`, `nameOrig`, `nameDest`, `isFraud`).
- **External Dependencies**: `pandas`, `numpy`.
- **Security-Sensitive Code**: None.
- **Irrelevant to ScamGraph**: Legacy Java agent simulation engine, non-UPI transaction types (cash-out, wire transfers).
- **License Compatibility**: Fully compatible (MIT).
- **Integration Strategy**: **Type C / D** (Use as conceptual guide for generating synthetic UPI collect requests and multi-step journey scenarios in `data/synthetic/`).
- **Code Reuse Status**: No foreign code copied; generate native Pydantic mock incidents.
- **Priority**: **P1 (Synthetic Data)**

---

### 1.7 IOK Phishing Kit Rules (`phish-report/IOK`)
- **License**: CC-BY-SA-4.0
- **Languages / Frameworks**: YAML / YARA-like rule declarations
- **Main Entry Points**: Indicator rule repository
- **Reusable Algorithms**: Pattern matching for credential harvesting kits (Telegram bot exfiltration tokens, fake login templates).
- **Reusable Schemas / Data Models**: Declarative indicator signatures.
- **External Dependencies**: None.
- **Security-Sensitive Code**: Contains real phishing kit signatures and exfiltration URLs (must never be executed live).
- **Irrelevant to ScamGraph**: Non-web phishing kits.
- **License Compatibility**: CC-BY-SA-4.0 requires attribution and share-alike if modified directly.
- **Integration Strategy**: **Type C** (Adapt detection logic into independent Python regex matchers without vendoring the raw rules).
- **Code Reuse Status**: Clean-room implementation in `services/investigation/extractors/`.
- **Priority**: **P1 (Secondary Technique Rules)**

---

### 1.8 urlscan-python (`urlscan/urlscan-python`) & VirusTotal (`VirusTotal/vt-py`)
- **License**: MIT / Apache-2.0
- **Languages / Frameworks**: Python, asyncio, httpx
- **Main Entry Points**: Official client classes
- **Reusable Algorithms**: Automated scan polling, verdict parsing, IP/ASN extraction.
- **External Dependencies**: `httpx`, `pydantic`.
- **Security-Sensitive Code**: External API rate limits; public leak of private URLs on urlscan unauthenticated submissions.
- **Irrelevant to ScamGraph**: Batch file submission tooling.
- **License Compatibility**: Fully compatible.
- **Integration Strategy**: **Type A** (Optional secondary adapters wrapped with circuit breakers in `services/investigation/providers/`).
- **Code Reuse Status**: Standard client integration if API keys are configured.
- **Priority**: **P1 (Optional Adapters)**

---

### 1.9 Research & Complex GNN References (`phishGNN`, `FraudGraph`, `graph-ml-examples`)
- **Licenses**: MIT / Apache-2.0
- **Analysis**: These repositories focus on PyTorch Geometric / DGL GNN embeddings and streaming Kafka pipelines.
- **Conclusion**:
  - GNNs are black-box models that violate Rule 10 & 17 (Explainability & Determinism first).
  - Kafka/Redis introduces heavy infrastructure prohibited by the hackathon architecture guidelines.
- **Integration Strategy**: **Type D (Research Only)**. Kept strictly as academic literature references for post-hackathon evaluation.
- **Priority**: **P3 (Post-Hackathon Research)**

---

## 2. Capability Matrix & Best-Reference Mapping

| Capability | Best Reference | Backup Reference | ScamGraph Destination Module |
|---|---|---|---|
| **Live Web Investigation** | `tinyfish-cookbook` | HTTP/DOM Scraper | `services/investigation/tinyfish/` |
| **URL Normalization & Lexical Analysis** | `PhishGraph` (`url_features.py`) | RFC 3986 spec | `services/investigation/url_analysis/` |
| **SSRF Prevention** | `PhishGraph` (`url_safety.py`) | OWASP SSRF Sheet | `services/investigation/url_analysis/` |
| **DNS Investigation** | `PhishGraph` (`dns_lookup.py`) | dnspython standard | `services/investigation/dns/` |
| **RDAP / Domain Age** | `PhishGraph` (`rdap_client.py`) | whois-python | `services/investigation/rdap/` |
| **TLS Certificate Inspection** | `PhishGraph` (`tls_checker.py`) | Python ssl module | `services/investigation/tls/` |
| **Redirect Analysis** | `PhishGraph` (`redirect_analyzer.py`) | httpx client | `services/investigation/url_analysis/` |
| **Phishing Technique Detection** | `IOK` | MITRE ATT&CK | `services/investigation/extractors/` |
| **Semantic Message Embeddings** | `VECTPHISH` (`embeddings.py`) | sentence-transformers | `services/pattern-engine/semantic/` |
| **Campaign Clustering** | `VECTPHISH` (`clustering.py`) | scikit-learn DBSCAN | `services/pattern-engine/matcher/` |
| **Neo4j Graph Modeling** | `demo-fraud-detection-with-p2p` | `neo4j-fraud-detection` | `services/graph-engine/neo4j/` |
| **Entity Resolution** | `demo-fraud-detection-with-p2p` | Cypher Jaccard Queries | `services/graph-engine/correlation/` |
| **Community Detection** | `demo-fraud-detection-with-p2p` (WCC/Louvain) | NetworkX | `services/graph-engine/algorithms/` |
| **Payment Graph Modeling** | `PaySim` / `demo-fraud-detection-with-p2p` | `finance-ieee-cis-fraud` | `data/synthetic/payment/` |
| **Interactive Cytoscape Visualization** | `cytoscape.js` (core + dagre) | React Flow | `apps/web/components/graph/` |
| **Emerging Scam Detection** | ScamGraph 3-Level Spec | `VECTPHISH` + `PaySim` | `services/pattern-engine/matcher/` |
