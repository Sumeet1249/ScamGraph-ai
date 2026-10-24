# API Contract Findings & ScamGraph Specification

This document records published API design conventions observed from public developer documentation and defines the independent, fully specified ScamGraph AI API contracts.

## 1. Public Observations vs. Independent Design

- **`DOCUMENTED`**: General requirement for RESTful endpoints, JSON request/response formats, idempotent submission, mutual authentication, and granular status reporting.
- **`OBSERVED`**: DPIP/MuleHunter conceptual workflows: Ingesting reports, querying suspect registries, submitting disputes, obtaining risk scores.
- **`INFERRED`**: Exact internal RBIH API paths and schemas are private/restricted to member banks and are **NOT** publicly exposed.
- **`PROPOSED`**: ScamGraph AI specifies clean, fully typed endpoints under `/api/v1/` complying with OpenAPI 3.1 and Pydantic v2 validation standards.

---

## 2. Module A: Smart Registry API Endpoints

### 2.1 Ingest Fraud Report
- **Route**: `POST /api/v1/registry/reports`
- **Description**: Ingests a new suspect report with typed identifiers, evidence, and provenance.
- **Request Payload**:
  ```json
  {
    "reporting_org": "BANK_HDFC_01",
    "entity_name": "Suspicious Merchant Services",
    "category": "MULE_ACCOUNT",
    "reason": "Rapid fund pass-through linked to reported Telegram job scam",
    "identifiers": [
      {
        "identifier_type": "UPI_VPA",
        "raw_value": "quickpay.mule99@oksbi"
      },
      {
        "identifier_type": "PHONE",
        "raw_value": "+919876543210"
      },
      {
        "identifier_type": "BANK_ACCOUNT",
        "raw_value": "SBIN0001234:987654321098"
      }
    ],
    "evidence_references": [
      "https://cybercrime.gov.in/complaints/1930-2026-X99",
      "inc_8f7b2c9e11"
    ],
    "confidence": 0.92
  }
  ```
- **Response Payload (201 Created)**:
  ```json
  {
    "report_id": "rep_9f82ab71",
    "status": "REPORTED",
    "created_at": "2026-10-22T00:15:00Z",
    "fingerprints": [
      {
        "identifier_type": "UPI_VPA",
        "fingerprint": "hmac_v1_e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "key_version": "v1"
      }
    ],
    "message": "Report ingested successfully and queued for review."
  }
  ```

### 2.2 Screen Identifiers
- **Route**: `POST /api/v1/registry/screen`
- **Description**: Real-time screening of one or more typed identifiers against confirmed registry entries.
- **Request Payload**:
  ```json
  {
    "caller_org": "PSP_PHONEPE_02",
    "identifiers": [
      {
        "identifier_type": "UPI_VPA",
        "raw_value": "quickpay.mule99@oksbi"
      }
    ]
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "screening_id": "scr_1a2b3c4d",
    "screened_at": "2026-10-22T00:15:05Z",
    "total_queried": 1,
    "total_hits": 1,
    "matches": [
      {
        "identifier_type": "UPI_VPA",
        "match_type": "EXACT_FINGERPRINT",
        "report_id": "rep_9f82ab71",
        "report_status": "CONFIRMED",
        "category": "MULE_ACCOUNT",
        "reporting_source": "BANK_HDFC_01",
        "reported_at": "2026-10-22T00:15:00Z",
        "is_disputed": false,
        "is_revoked": false,
        "risk_score": 0.95,
        "reason_code": "REGISTRY_CONFIRMED_MULE"
      }
    ]
  }
  ```

### 2.3 Submit Dispute
- **Route**: `POST /api/v1/registry/disputes`
- **Description**: Submits a formal dispute against a reported identifier by an authorized participant.
- **Request Payload**:
  ```json
  {
    "report_id": "rep_9f82ab71",
    "disputing_org": "BANK_ICICI_01",
    "reason": "Account holder completed enhanced video KYC and justified transaction velocity as legitimate agricultural harvest sales",
    "evidence_documents": ["doc_vkyc_verified_2026.pdf"]
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "dispute_id": "dsp_77ac2b19",
    "report_id": "rep_9f82ab71",
    "status": "DISPUTED",
    "updated_at": "2026-10-22T00:15:10Z",
    "audit_event_id": "aud_018b2c4e"
  }
  ```

### 2.4 Revoke Report
- **Route**: `POST /api/v1/registry/revocations`
- **Description**: Revokes a previously filed report upon authorization, invalidating active screening matches while preserving the audit record.
- **Request Payload**:
  ```json
  {
    "report_id": "rep_9f82ab71",
    "authorizing_org": "BANK_HDFC_01",
    "revocation_reason": "Customer demonstrated authorized corporate account delegation; false positive cleared.",
    "authorized_by": "Compliance_Officer_CO_402"
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "revocation_id": "rev_5c91fe22",
    "report_id": "rep_9f82ab71",
    "status": "REVOKED",
    "revoked_at": "2026-10-22T00:15:20Z",
    "screening_active": false
  }
  ```

---

## 3. Module B: Mule Intelligence API Endpoints

### 3.1 Evaluate Account Mule Risk
- **Route**: `POST /api/v1/mule/evaluate`
- **Description**: Evaluates an account's recent transaction history across the 19 behavioral mule patterns.
- **Request Payload**:
  ```json
  {
    "account_id": "ACC_9921827401",
    "transactions": [
      {
        "txn_id": "TXN_001",
        "timestamp": "2026-10-22T08:00:00Z",
        "amount": 95000.00,
        "direction": "CREDIT",
        "counterparty_account": "ACC_VICTIM_01",
        "channel": "UPI"
      },
      {
        "txn_id": "TXN_002",
        "timestamp": "2026-10-22T08:02:15Z",
        "amount": 45000.00,
        "direction": "DEBIT",
        "counterparty_account": "ACC_LAYER_01",
        "channel": "IMPS"
      },
      {
        "txn_id": "TXN_003",
        "timestamp": "2026-10-22T08:03:00Z",
        "amount": 49500.00,
        "direction": "DEBIT",
        "counterparty_account": "ACC_LAYER_02",
        "channel": "IMPS"
      }
    ],
    "account_age_days": 12,
    "historical_avg_daily_volume": 500.00
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "account_id": "ACC_9921827401",
    "risk_score": 0.94,
    "risk_band": "CRITICAL",
    "recommended_action": "FREEZE_SUSPEND",
    "top_contributing_rules": [
      {
        "rule_id": "MULE_RULE_03",
        "name": "Rapid Pass-Through Churn",
        "description": "99.4% of incoming funds transferred out within 3 minutes of arrival.",
        "severity": "HIGH",
        "weight": 0.40
      },
      {
        "rule_id": "MULE_RULE_07",
        "name": "Dormancy / New Account Sudden Burst",
        "description": "Account age < 14 days with > 150x spike above historical baseline.",
        "severity": "HIGH",
        "weight": 0.35
      }
    ],
    "extracted_features": {
      "velocity_1h_count": 3,
      "inbound_outbound_ratio": 0.994,
      "dwell_time_seconds": 135,
      "counterparty_diversity": 1.0,
      "round_amount_chunking_detected": true
    },
    "model_metadata": {
      "model_version": "mule_rules_engine_v1.0.0",
      "evaluated_at": "2026-10-22T00:15:30Z"
    }
  }
  ```

---

## 4. Module C: Graph Correlation API Endpoints

### 4.1 Path Exploration & Multi-Hop Flows
- **Route**: `POST /api/v1/graph/paths`
- **Description**: Discovers transaction flows, rapid layering hops, and circular paths between accounts.
- **Request Payload**:
  ```json
  {
    "source_entity": "ACC_VICTIM_01",
    "max_depth": 4,
    "time_window_hours": 24,
    "min_amount": 1000.00
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "paths_found": 2,
    "circular_flows_detected": false,
    "paths": [
      {
        "path_length": 3,
        "total_amount_transferred": 94500.00,
        "nodes": ["ACC_VICTIM_01", "ACC_9921827401", "ACC_LAYER_01", "ACC_CASH_OUT_99"],
        "edges": [
          {"from": "ACC_VICTIM_01", "to": "ACC_9921827401", "amount": 95000, "txn_id": "TXN_001"},
          {"from": "ACC_9921827401", "to": "ACC_LAYER_01", "amount": 45000, "txn_id": "TXN_002"}
        ],
        "dwell_times_seconds": [135, 240]
      }
    ]
  }
  ```

### 4.2 Risk Propagation Calculation
- **Route**: `POST /api/v1/graph/risk-propagation`
- **Description**: Propagates risk from verified registry seed reports across graph neighbors with distance decay.
- **Request Payload**:
  ```json
  {
    "seed_entity_id": "rep_9f82ab71",
    "seed_risk": 0.95,
    "decay_factor": 0.5,
    "max_hops": 3
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "seed_entity_id": "rep_9f82ab71",
    "propagated_nodes": [
      {
        "entity_id": "ACC_9921827401",
        "distance": 1,
        "direct_risk": 0.0,
        "propagated_risk": 0.475,
        "total_risk": 0.475,
        "path_evidence": ["rep_9f82ab71 -> (LINKED_TO_REPORT) -> ACC_9921827401"]
      },
      {
        "entity_id": "ACC_LAYER_01",
        "distance": 2,
        "direct_risk": 0.0,
        "propagated_risk": 0.237,
        "total_risk": 0.237,
        "path_evidence": ["ACC_9921827401 -> (SENT_TO) -> ACC_LAYER_01"]
      }
    ]
  }
  ```

---

## 5. Module D: Unified ScamGraph Risk API Endpoints

### 5.1 Unified Incident Assessment
- **Route**: `POST /api/v1/risk/unified-assessment`
- **Description**: Synthesizes Smart Registry, Mule Intelligence, Graph Correlation, and Message NLP into an explainable assessment.
- **Request Payload**:
  ```json
  {
    "message_text": "Electricity bill unpaid ₹2847. Power will be cut at 9:30 PM. Pay via UPI: powerdesk@paytm",
    "vpa": "powerdesk@paytm",
    "phone": "+919876543210",
    "url": "https://quick-bill-pay.site"
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "assessment_id": "ass_017b3f99",
    "overall_risk_score": 0.88,
    "risk_band": "HIGH",
    "recommended_action": "STEP_UP_VERIFICATION",
    "signals": {
      "registry_result": {
        "hit": true,
        "status": "CONFIRMED",
        "category": "ELECTRICITY_IMPERSONATION"
      },
      "mule_risk_result": {
        "score": 0.76,
        "band": "HIGH",
        "top_rule": "RAPID_PASS_THROUGH"
      },
      "graph_risk_result": {
        "direct_risk": 0.85,
        "propagated_risk": 0.42,
        "cluster_id": "cluster_elec_phish_04"
      },
      "message_nlp_result": {
        "score": 0.91,
        "signals": ["URGENCY_THREAT", "UTILITY_DISCONNECTION_IMPERSONATION"]
      }
    },
    "reason_codes": [
      "REGISTRY_CONFIRMED_IMPERSONATION",
      "SUSPICIOUS_PERSONAL_VPA_FOR_UTILITY",
      "MESSAGE_SEMANTIC_COERCION"
    ],
    "is_degraded": false
  }
  ```
