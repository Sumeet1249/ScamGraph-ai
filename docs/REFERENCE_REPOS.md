# ScamGraph AI — Reference Repository Registry

> **Purpose**: Formal catalog and governance registry for open-source reference repositories.  
> **Rule**: External repositories are architectural references only. We harvest specialized capabilities behind ScamGraph canonical interfaces; we never vendor, merge, or copy whole foreign applications.

---

## 1. Registry Table

| Repository | URL | License | Capability | Files/Modules Worth Studying | What ScamGraph Needs | Copy Code? | Attribution Required? | Status |
|---|---|---|---|---|---|---|---|---|
| **TinyFish Cookbook** | `https://github.com/tinyfish-io/tinyfish-cookbook` | MIT / Apache-2.0 | Live Web Investigation | Agentic scraping recipes, DOM extraction patterns | Fact-based observable extraction (forms, OTP fields, brands) | NO (Use API / Client) | Yes | **ACTIVE (P0 - Mandatory)** |
| **PhishGraph** | `https://github.com/AVII-VERSE/PhishGraph` | MIT / GPL-3.0 (Verify) | Phishing Infrastructure Intelligence | `analysis/`, `dns_lookup.py`, `rdap_client.py`, `tls_checker.py` | DNS/RDAP/TLS extractors, redirect tracing, SSRF safety | NO (Reimplement concept behind interfaces) | Yes | **ACTIVE (P0 - Core)** |
| **VECTPHISH** | `https://github.com/AmadeusITGroup/VECTPHISH` | Apache-2.0 | Semantic Campaign Clustering | `clustering.py`, `embeddings.py`, cosine similarity pipelines | SentenceTransformers + DBSCAN campaign clustering | NO (Reimplement concept using pgvector) | Yes | **ACTIVE (P0 - Core)** |
| **Neo4j P2P Fraud** | `https://github.com/neo4j-product-examples/demo-fraud-detection-with-p2p` | Apache-2.0 | Graph Fraud Intelligence | Cypher queries, entity resolution, community detection | Cross-incident entity fusion, shared VPA/phone detection | NO (Adapt Cypher patterns) | Yes | **ACTIVE (P0 - Core)** |
| **Cytoscape.js** | `https://github.com/cytoscape/cytoscape.js` | MIT | Graph Visualization | Frontend library distribution | Directed Scam Journey Graph & infrastructure view | NO (Use as npm dependency) | Yes (MIT notice) | **ACTIVE (P0 - Core)** |
| **Neo4j Graph ML Examples** | `https://github.com/neo4j-product-examples/graph-machine-learning-examples` | Apache-2.0 | Advanced Graph Machine Learning | GraphSAGE pipelines, node embeddings | Link prediction research for future variant scoring | NO | Yes | **RESEARCH (P2 - Post-MVP)** |
| **neomodel** | `https://github.com/neo4j-contrib/neomodel` | Apache-2.0 | Python OGM for Neo4j | Schema class models, relationship definitions | Evaluated for FastAPI domain models | NO (Standard official neo4j async driver preferred) | Yes | **REJECTED (Redundant)** |
| **IOK** | `https://github.com/phish-report/IOK` | CC-BY-SA-4.0 / MIT (Inspect) | Phishing Technique Rules | YARA-like web detection rules, kit signatures | Observable technique indicators (credential harvesting forms) | NO (Port rule concepts to python matchers) | Yes (Explicit CC attribution) | **ACTIVE (P1 - Secondary)** |
| **urlscan-python** | `https://github.com/urlscan/urlscan-python` | MIT | URL Intelligence Adapter | API wrapper, scan result parsers | Optional secondary external web evidence provider | NO (Use SDK or HTTP client if key available) | Yes | **OPTIONAL (P1 - Adapter)** |
| **vt-py** | `https://github.com/VirusTotal/vt-py` | Apache-2.0 | Threat Intelligence | Client wrapper, lookup models | Optional threat reputation provider | NO (Use official SDK if key available) | Yes | **OPTIONAL (P1 - Adapter)** |
| **phishGNN** | `https://github.com/TristanBilot/phishGNN` | MIT | GNN Phishing Detection | Graph feature construction, PyG network definitions | Academic benchmarking for graph topology classification | NO | Yes | **RESEARCH (P3 - Academic)** |
| **PaySim** | `https://github.com/voutilad/PaySim` | MIT | Synthetic Financial Simulation | Simulation generators, agent behavior | Synthetic payment transactions & UPI collect requests | NO (Use ideas for synthetic test generation) | Yes | **ACTIVE (P1 - Synthetic Data)** |
| **Neo4j Fraud Detection** | `https://github.com/neo4j-field/neo4j-fraud-detection` | Apache-2.0 | Transaction Graph Features | Graph feature engineering, risk heuristics | Financial and device graph feature ideas | NO (Reimplement queries) | Yes | **ACTIVE (P1 - Reference)** |
| **Neo4j Finance IEEE-CIS** | `https://github.com/neo4j-field/finance-ieee-cis-fraud` | Apache-2.0 | Financial Graph Modeling | Heterogeneous graph schema definitions | Identity, device, and payment relationship modeling | NO (Schema inspiration only) | Yes | **RESEARCH (P2 - Modeling)** |
| **Knowledge Graph Fraud** | `https://github.com/Akash-bu/Fraud-Detection-using-Knowledge-Graphs` | MIT | Fraud KG Architecture | FastAPI + Neo4j integration patterns | End-to-end integration reference | NO (Architecture reference only) | Yes | **RESEARCH (P2 - Reference)** |
| **FraudGraph** | `https://github.com/Svkayy/FraudGraph` | MIT | Advanced Graph ML & Stream Arch | Attention mechanisms, heterogeneous embeddings | Research concepts for complex graph embeddings | NO (Reject Kafka/streaming bloat) | Yes | **RESEARCH (P3 - Academic)** |
| **AgentQL** | `https://github.com/tinyfish-io/agentql` | Apache-2.0 | Semantic DOM Querying | Query language parser, web element finder | Alternative structured extraction evaluation | NO (TinyFish API covers requirements) | Yes | **REJECTED (Redundant with TinyFish)** |

---

## 2. Capability Harvesting: One Job Per Repository

To avoid architectural drift, each retained repository is assigned exactly **ONE specialized capability**:

1. **TinyFish Cookbook** $\rightarrow$ **Live Web Investigation**: Inspects suspicious URLs, renders DOMs, extracts observable form fields, OTP requests, and claimed brand names without editorializing.
2. **PhishGraph** $\rightarrow$ **Phishing Infrastructure Intelligence**: Provides the blueprint for URL normalization, SSRF-safe resolution, RDAP age extraction, and TLS certificate inspection.
3. **VECTPHISH** $\rightarrow$ **Semantic Campaign Detection**: Provides embedding clustering concepts (SentenceTransformers + cosine distance) adapted from phishing emails to multi-stage scam incidents.
4. **Neo4j P2P Fraud** $\rightarrow$ **Entity Resolution & Community Detection**: Guides Cypher graph traversal for detecting shared phone numbers, VPAs, and bank accounts across independent victims.
5. **Cytoscape.js** $\rightarrow$ **Interactive Scam Journey Visualization**: Directly powers the interactive UI graph canvas.
6. **IOK** $\rightarrow$ **Phishing Technique Rules**: Supplies declarative rule patterns for identifying phishing kit behaviors and credential traps.
7. **urlscan-python & vt-py** $\rightarrow$ **Optional Secondary Adapters**: Modular, fault-tolerant adapters for secondary threat signals.
8. **PaySim** $\rightarrow$ **Synthetic Payment Simulation**: Inspires realistic multi-user synthetic UPI collect request test datasets.
9. **Neo4j Fraud Detection & IEEE-CIS** $\rightarrow$ **Financial Graph Modeling**: Guides relationship types and property structures for payment handles and entities.
10. **PhishGNN & FraudGraph** $\rightarrow$ **Research & Evaluation**: Kept strictly as academic literature references for post-hackathon experiments.
