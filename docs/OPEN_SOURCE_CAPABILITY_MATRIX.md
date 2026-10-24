# ScamGraph AI — Open Source Capability Matrix

## 1. Classification & Integration Types

Every evaluated open-source asset is classified into exactly one integration pattern:
- **Type A**: Use library directly (official SDK or package dependency).
- **Type B**: Adapt small licensed module (cleanly ported logic with full license attribution).
- **Type C**: Reimplement concept behind ScamGraph canonical interface (clean-room rewrite tailored to our data model).
- **Type D**: Research only (design reference or academic benchmark, no code introduced).

---

## 2. Comprehensive Capability Matrix

| Repository | License | Primary Capability | Exact Useful Modules/Files | Dependencies | Integration Type | ScamGraph Destination | Priority | Security Concerns | Attribution Requirements | Keep / Reject Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| **tinyfish-cookbook** | MIT / Apache-2.0 | Live Web Investigation | Agentic extraction recipes, web investigation scripts | TinyFish API, httpx | **A / C** | `services/investigation/tinyfish/` | **P0** | API key leakage risk (must remain server-side). | Retain TinyFish copyright notice. | **KEEP (Core Mandatory)** |
| **PhishGraph** | MIT / GPL-3.0 | Phishing Infrastructure Intel | `analysis/dns_lookup.py`, `rdap_client.py`, `tls_checker.py`, `url_features.py` | dnspython, cryptography, tldextract | **C** | `services/investigation/url_analysis/` | **P0** | SSRF risk if fetching arbitrary URLs directly; must enforce private IP blocks. | Cite authors in file headers if logic adapted. | **KEEP (Core Concept)** |
| **VECTPHISH** | Apache-2.0 | Semantic Campaign Clustering | `src/embeddings.py`, `src/clustering.py`, DBSCAN pipeline | sentence-transformers, scikit-learn, numpy | **C** | `services/pattern-engine/semantic/`, `services/graph-engine/campaigns/` | **P0** | High memory usage during large batch clustering. | Apache 2.0 attribution notice. | **KEEP (Core Concept)** |
| **demo-fraud-detection-with-p2p** | Apache-2.0 | Graph Fraud Intelligence | `cypher/queries.cyp`, community detection, entity resolution scripts | Neo4j GDS library, neo4j python driver | **C** | `services/graph-engine/neo4j/`, `services/graph-engine/correlation/` | **P0** | Complex Cypher queries can cause memory exhaustion on large graphs without pagination. | Apache 2.0 license notice. | **KEEP (Core Concept)** |
| **cytoscape.js** | MIT | Interactive Graph Visualization | `cytoscape.min.js`, layout algorithms (dagre, cose, cola) | Node.js, React wrapper | **A** | `apps/web/components/graph/` | **P0** | DOM injection if node labels aren't sanitized. | MIT license header retained in bundled dependencies. | **KEEP (Core Visualizer)** |
| **PaySim** | MIT | Synthetic Financial Simulation | Synthetic agent models, payment transaction simulator | pandas, numpy, scikit-learn | **C / D** | `data/synthetic/payment/`, `ml/payment/` | **P1** | Do not confuse synthetic data with live banking streams. | Include original PaySim citation. | **KEEP (Synthetic Data Generator)** |
| **IOK** | CC-BY-SA-4.0 | Phishing Technique Rules | Detection YAML/JSON rule files, phishing kit indicators | Rule parser | **C** | `services/investigation/extractors/` | **P1** | CC-BY-SA copyleft constraints: do not vendor raw rule files directly; adapt detection concepts. | Explicit CC-BY-SA attribution required if rules are ported. | **KEEP (Technique Reference)** |
| **urlscan-python** | MIT | Secondary URL Intelligence | `urlscan/client.py`, submission models | httpx, pydantic | **A** | `services/investigation/url_analysis/` | **P1** | External quota exhaustion; potential unauthenticated data leak on public scans. | MIT license notice. | **KEEP (Optional Adapter)** |
| **vt-py** | Apache-2.0 | Threat Intelligence | Official VirusTotal Python client wrapper | httpx, asyncio | **A** | `services/investigation/url_analysis/` | **P1** | Rate limits; false sense of security if zero detections on day-zero scam URLs. | Apache 2.0 attribution. | **KEEP (Optional Adapter)** |
| **neo4j-fraud-detection** | Apache-2.0 | Graph Feature Engineering | Transaction graph schema, device-sharing Cypher queries | Neo4j 5.x | **C** | `services/graph-engine/algorithms/` | **P1** | Performance overhead on heavy relationship traversals. | Apache 2.0 notice. | **KEEP (Feature Reference)** |
| **neomodel** | Apache-2.0 | Python OGM for Neo4j | `core.py`, relationship property definitions | neomodel, neo4j | **A** | `services/graph-engine/neo4j/` | **P1** | Adds an unnecessary abstraction layer; slower than official async neo4j driver; schema migrations complex. | Apache 2.0 notice. | **REJECT (Use native neo4j driver)** |
| **finance-ieee-cis-fraud** | Apache-2.0 | Financial Graph Modeling | Heterogeneous node/edge mapping scripts | Neo4j, Python | **D** | `docs/DATA_MODEL.md` | **P2** | Schema too complex and credit-card focused for UPI workflows. | Apache 2.0 notice. | **RESEARCH (Modeling Reference Only)** |
| **Fraud-Detection-using-Knowledge-Graphs** | MIT | Fraud KG Architecture | FastAPI backend harness + React graph view | FastAPI, React, Neo4j | **D** | `services/api/` | **P2** | monolithic architecture; lacks multi-signal fusion and journey tracking. | MIT notice. | **RESEARCH (Architecture Reference Only)** |
| **agentql** | Apache-2.0 | Semantic DOM Querying | Web scraper agent, query parser | Playwright, Chromium | **A / C** | `services/investigation/tinyfish/` | **P2** | Redundant with TinyFish; heavy headless browser dependencies locally. | Apache 2.0 notice. | **REJECT (Redundant with TinyFish)** |
| **graph-machine-learning-examples** | Apache-2.0 | Advanced Graph Machine Learning | GraphSAGE GNN pipelines, node2vec | PyTorch Geometric, DGL | **D** | `ml/emerging/` | **P2** | GNN training is computationally heavy and unexplainable for MVP. | Apache 2.0 notice. | **RESEARCH (Post-MVP Only)** |
| **phishGNN** | MIT | GNN Phishing Detection | Phishing graph builder, GNN classification models | PyTorch, PyG | **D** | `ml/emerging/` | **P3** | Black-box graph classifier; violates explainability mandate. | MIT notice. | **RESEARCH (Academic Only)** |
| **FraudGraph** | MIT | Heterogeneous Graph ML | Kafka consumer, streaming GNN pipelines | Kafka, PyTorch Geometric, Redis | **D** | `ml/emerging/` | **P3** | Massive infrastructure overhead (Kafka, Redis) strictly forbidden by hackathon scope. | MIT notice. | **REJECT / RESEARCH (Too Complex)** |

---

## 3. Summary of Decisions

- **Total Repositories Analyzed**: 17
- **Retained for Core Hackathon MVP (P0)**: 5 (`tinyfish-cookbook`, `PhishGraph`, `VECTPHISH`, `demo-fraud-detection-with-p2p`, `cytoscape.js`)
- **Retained for Secondary / Optional / Synthetic Data (P1)**: 4 (`PaySim`, `IOK`, `urlscan-python`, `vt-py`)
- **Retained as Research / Modeling Reference (P2 / P3)**: 5 (`finance-ieee-cis-fraud`, `Fraud-Detection-using-Knowledge-Graphs`, `graph-machine-learning-examples`, `phishGNN`, `FraudGraph`)
- **Explicitly Rejected**: 3 (`neomodel` [redundant OGM], `agentql` [redundant with TinyFish], `FraudGraph` production integration [excessive Kafka/streaming overhead])
