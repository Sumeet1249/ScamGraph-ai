# Capability Matrix & Public Evidence Comparison

This matrix compares the publicly evidenced capabilities of the Reserve Bank Innovation Hub (RBIH) Digital Payments Intelligence Platform (DPIP) and MuleHunter against ScamGraph AI's independent implementation and verification strategy.

## Evidence Taxonomy
- **`DOCUMENTED`**: Explicitly affirmed in public documentation, speeches, whitepapers, or press releases.
- **`OBSERVED`**: Inferred from observable web portals, UI workflows, or partner integrations.
- **`INFERRED`**: Technical deduction from standard financial-crime regulations and architectural necessity.
- **`PROPOSED`**: ScamGraph AI's clean-room design and implementation.

---

## Comparative Capability Matrix

| Capability | Public Evidence & Classification | ScamGraph AI Independent Implementation | Verification Strategy |
|---|---|---|---|
| **Smart Registry Ingestion** | **`DOCUMENTED`** (SRC-002, SRC-003, SRC-007): Centralized repository where participating institutions submit suspect accounts, identifiers, and fraud evidence. | **`PROPOSED`**: Fully typed identifier ingestion (`Phone`, `UPI_VPA`, `Bank_Account`, `Device_ID`, `IP_Address`, `URL_Domain`, `Email`) with schema validation, provenance records, and keyed HMAC-SHA-256 fingerprinting. | Automated unit & integration tests (`test_registry_service.py`, `test_registry_api.py`). |
| **Identifier Screening** | **`DOCUMENTED`** (SRC-003): Real-time querying by member institutions before/during transaction authorization to intercept fraud. | **`PROPOSED`**: Real-time screening engine matching normalized canonical fingerprints against confirmed active reports, returning match status, confidence, recency, dispute status, and risk bands. | Exact-match, canonical normalization, and key-rotation unit tests (`test_identifier_screening.py`). |
| **Disputes & Revocation** | **`DOCUMENTED`** (SRC-003): Structured workflow allowing entities to challenge incorrect flags and reporting banks to revoke flags upon remediation. | **`PROPOSED`**: Explicit state machine (`REPORTED` → `UNDER_REVIEW` → `CONFIRMED` / `REJECTED` / `DISPUTED` / `REVOKED`) with immutable audit trails, role authorization, and automatic graph risk recalculation. | State machine transition tests, permission boundary checks, and audit log verification. |
| **Mule Account Risk Detection** | **`DOCUMENTED`** (SRC-004, SRC-005): AI/ML tool analyzing transaction data across banks using 19 behavioral patterns of money mules to spot layering and rapid churn. | **`PROPOSED`**: Independent Mule Intelligence Engine featuring 19 behavioral features (velocity, dormancy-burst, turnover ratio, counterparty diversity, rapid fund hop, fan-in/fan-out) paired with an interpretable baseline rules engine and calibrated supervised model. | Benchmark evaluation, Confusion Matrix, Precision-Recall AUC, and honest calibration metrics (`test_mule_engine.py`). |
| **Transaction Graph & Flow Analysis** | **`DOCUMENTED`** (SRC-001, SRC-004): Uncovering multi-tier money flow rings, layering chains across multiple bank accounts. | **`PROPOSED`**: Graph Correlation Engine supporting multi-hop path search, fan-in/fan-out aggregation, circular fund flow detection, rapid pass-through chains, and connected component clustering. | Network path traversal tests, cycle detection tests, and synthetic fraud ring benchmark scenarios (`test_graph_correlation.py`). |
| **Explainable Risk Propagation** | **`INFERRED`** (SRC-003, SRC-004): Necessary for AML compliance and regulatory transparency (explainable alerts rather than black-box blocks). | **`PROPOSED`**: Transparent graph risk propagation algorithm with distance decay ($\lambda=0.5$), temporal decay, evidence weight factoring, and explicit segregation between direct evidence and propagated topological risk. | Decay formula verification, distance threshold bounds tests, dispute recalculation audit tests. |
| **Unified Fraud Intelligence Fusion** | **`DOCUMENTED`** (SRC-002): Combining registry hits, mule indicators, and cyber intelligence into actionable signals. | **`PROPOSED`**: Unified ScamGraph Risk Engine orchestrating Smart Registry matches, Mule Intelligence, Graph Correlation, and Semantic Message NLP with configurable fusion, explicit uncertainty, and action recommendations (`ALLOW`, `STEP_UP_VERIFICATION`, `FLAG_FOR_REVIEW`, `ESCALATE`). | Multi-signal fusion tests, degraded mode (missing component) tests, and decision boundary tests. |
| **Feedback Mechanism** | **`DOCUMENTED`** (SRC-003): Continuous feedback loop where institutions submit hit verification to refine systemic detection. | **`PROPOSED`**: Registry feedback endpoint logging true/false positives, updating model evaluation metrics, and maintaining institutional hit-rate audit logs. | End-to-end feedback ingestion tests and metrics update verification. |

---

## Detailed Gap Analysis (Proprietary vs. Independent)

1. **Model Weights & Exact Algorithms**:
   - *Public Evidence*: RBIH documentation highlights that MuleHunter uses AI/ML with 85%+ accuracy and 19 behavioral patterns, but does not publish model weights, training hyper-parameters, or production feature weights.
   - *ScamGraph Action*: Implement independent, mathematically sound financial engineering indicators (19 feature extractors) and provide a reproducible training pipeline on synthetic/open datasets with honest baseline reporting.
2. **Proprietary Network Interconnects**:
   - *Public Evidence*: DPIP uses private inter-bank networks (SFMS/INFINET) and authenticated government gateways (I4C).
   - *ScamGraph Action*: Implement modern, secure RESTful JSON APIs with mTLS-ready headers, HMAC signature verification, API keys, and strict tenant isolation.
3. **Database Schemas**:
   - *Public Evidence*: High-level entity relations are described in public summaries, but relational DDL and graph schema definitions are private.
   - *ScamGraph Action*: Design clean canonical schemas in Pydantic v2 and PostgreSQL/Neo4j with complete type annotations and validation.
