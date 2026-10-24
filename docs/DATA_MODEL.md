# ScamGraph AI — Data Model Specification

## 1. Overview

ScamGraph AI utilizes a **hybrid polyglot storage architecture**:
1. **Canonical Domain Models (`services/api/app/domain/`)**: Unified Pydantic v2 domain contracts shared across all specialized components (TinyFish, ML, Neo4j, URL Intelligence, and Semantic Pattern Engine).
2. **PostgreSQL + pgvector**: Stores transactional incident records, event payloads, structured evidence signals, and high-dimensional semantic embeddings for cosine similarity indexing.
3. **Neo4j**: Stores the topological **Scam Journey Graph**, entities (senders, handles, accounts, URLs, domains), and cross-incident fusion edges.

---

## 2. Canonical Domain Models (`services/api/app/domain/`)

The core architectural requirement is that all intelligence modules speak one common language:

```
TinyFish ─────────┐
URL model ────────┤
Message AI ───────┤
DNS/RDAP ─────────┤
Graph engine ─────┼──→ Evidence ──→ Pattern Engine ──→ Risk Assessment ──→ Intervention Decision
Pattern engine ───┤
Payment model ────┘
```

### 2.1 Canonical Enums (`enums.py`)
- **`RiskLevel`**: `LOW`, `MEDIUM`, `HIGH`, `UNKNOWN`
- **`ConfidenceLevel`**: `LOW`, `MEDIUM`, `HIGH`
- **`IncidentStatus`**: `OPEN`, `INVESTIGATING`, `ASSESSED`, `CLOSED`
- **`EventType`**: `MESSAGE_RECEIVED`, `CALL_REPORTED`, `URL_RECEIVED`, `URL_OPENED`, `CREDENTIAL_REQUEST`, `OTP_REQUEST`, `QR_RECEIVED`, `PAYMENT_REQUEST`, `PAYMENT_INTENT`, `PAYMENT_REPORTED`, `OTHER`
- **`EntityType`**: `PHONE`, `EMAIL`, `URL`, `DOMAIN`, `IP`, `ASN`, `BRAND`, `PAYMENT_ENTITY`, `CERTIFICATE`, `NAMESERVER`
- **`EvidenceSource`**: `USER_INPUT`, `MESSAGE_ANALYZER`, `URL_ANALYZER`, `TINYFISH`, `DNS`, `RDAP`, `TLS`, `THREAT_INTELLIGENCE`, `GRAPH_ENGINE`, `PATTERN_ENGINE`, `PAYMENT_MODEL`, `SIMULATOR`
- **`InterventionType`**: `NONE`, `PASSIVE`, `CAUTION`, `STRONG_WARNING`, `PRE_PAYMENT_INTERVENTION`
- **`MatchLevel`**: `NONE`, `WEAK`, `MODERATE`, `STRONG` *(Non-probabilistic index)*

### 2.2 Canonical Entities & Relationships (`models.py`)

#### `Incident`
Represents an ongoing or completed victim interaction session.
- `id`: str (UUID-compatible)
- `created_at`: datetime (timezone-aware)
- `updated_at`: datetime (timezone-aware)
- `status`: IncidentStatus
- `title`: str (non-empty)
- `source`: str
- `metadata`: Dict[str, Any]

#### `Event`
Chronological event within a grooming journey. Supports temporal ordering (`__lt__` comparing `timestamp`).
- `id`: str (UUID-compatible)
- `incident_id`: str (UUID-compatible)
- `timestamp`: datetime (timezone-aware)
- `event_type`: EventType
- `source`: EvidenceSource
- `confidence`: float (0.0 to 1.0)
- `payload`: Dict[str, Any]
- `evidence_ids`: List[str]

#### `Entity`
Observable infrastructure or psychological identity node. Strictly prohibits storing credentials (`pin`, `password`, `otp`) in metadata.
- `id`: str (UUID-compatible)
- `entity_type`: EntityType
- `normalized_value`: str
- `display_value`: str
- `metadata`: Dict[str, Any]

#### `Evidence`
Represents an objective observation. **MUST NOT** itself contain a final scam verdict.
- `id`: str (UUID-compatible)
- `incident_id`: str (UUID-compatible)
- `source`: EvidenceSource
- `signal`: str
- `observation`: str
- `confidence`: float (0.0 to 1.0)
- `timestamp`: datetime (timezone-aware)
- `entity_ids`: List[str]
- `event_ids`: List[str]
- `source_reference`: Optional[str]
- `metadata`: Dict[str, Any]

#### `Relationship`
Correlated graph edge connecting two entities.
- `id`: str (UUID-compatible)
- `source_entity_id`: str
- `target_entity_id`: str
- `relationship_type`: str
- `confidence`: float (0.0 to 1.0)
- `evidence_ids`: List[str]
- `first_seen`: datetime (timezone-aware)
- `last_seen`: datetime (timezone-aware)
- `metadata`: Dict[str, Any]

#### `Observation`
Raw telemetry data capture before signal extraction.
- `id`: str (UUID-compatible)
- `source`: EvidenceSource
- `raw_data`: Dict[str, Any]
- `observed_at`: datetime (timezone-aware)
- `metadata`: Dict[str, Any]

#### `ScamPattern` & `PatternMatch`
Structural definition and match assessment for known scam workflows.
- `PatternMatch.match_level`: Discrete enum (`NONE`, `WEAK`, `MODERATE`, `STRONG`), not a probability.
- `PatternMatch.matched_events`, `missing_events`, `supporting_evidence_ids`.

#### `GraphCorrelation`
Cross-incident graph traversal results linking shared entities and infrastructure paths.
- `related_incident_id`: str
- `shared_entities`: List[str]
- `shared_infrastructure`: List[str]
- `relationship_paths`: List[str]
- `confidence`: float (0.0 to 1.0)
- `evidence_ids`: List[str]

#### `Campaign`
Syndicated attack cluster aggregating multiple related incidents.
- `id`: str
- `name`: str
- `pattern_type`: str
- `first_seen`: datetime (timezone-aware)
- `last_seen`: datetime (timezone-aware)
- `incident_ids`: List[str]
- `entity_ids`: List[str]
- `metadata`: Dict[str, Any]

#### `RiskAssessment`
Unified multi-signal assessment.
- `risk_score`: int (0–100 **INDEX**, not a probability).
- `risk_level`: RiskLevel (`LOW`, `MEDIUM`, `HIGH`, `UNKNOWN`).
- `evidence_confidence`: ConfidenceLevel.
- `reason_codes`: List of findings referencing Evidence IDs.
- `insufficient_evidence`: bool.

#### `InterventionDecision`
Calibrated user prompt decision.
- `intervention_type`: InterventionType.
- `reason`: str (strictly required non-empty string).
- `triggering_evidence_ids`: List[str].
- `payment_proximity`: bool.
- `created_at`: datetime (timezone-aware).

---

## 3. PostgreSQL + pgvector Schema

### 3.1 Table: `incidents`
Tracks a reported or detected scam attempt session.
```sql
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(128) NOT NULL UNIQUE,
    user_identifier_hash VARCHAR(64) NOT NULL, -- Pseudonymized user ID
    channel VARCHAR(32) NOT NULL,              -- SMS, WhatsApp, Telegram, Call, Web
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, RESOLVED, DISMISSED
    risk_level VARCHAR(16) NOT NULL DEFAULT 'LOW', -- LOW, MEDIUM, HIGH, INSUFFICIENT_EVIDENCE
    evidence_confidence VARCHAR(16) NOT NULL DEFAULT 'LOW', -- LOW, MEDIUM, HIGH
    risk_score INT NOT NULL DEFAULT 0,         -- Index 0 - 100
    confidence_score FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_incidents_session ON incidents(session_id);
CREATE INDEX idx_incidents_risk ON incidents(risk_level, evidence_confidence);
```

### 3.2 Table: `events`
Chronological raw events observed within an incident.
```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    sequence_number INT NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    raw_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_events_incident_seq ON events(incident_id, sequence_number);
```

---

## 4. Neo4j Property Graph Schema

### 4.1 Node Labels
- `:Incident {id, status, risk_score, created_at}`
- `:Event {id, sequence_number, event_type, timestamp}`
- `:Message {id, channel, text_snippet, embedding_vector}`
- `:URL {id, raw_url, domain, is_phishing_detected}`
- `:Domain {name, registrar, age_days, is_typosquatting}`
- `:IP {address, asn, country_code}`
- `:PaymentEntity {vpa, claimed_name, psp_handle}`
- `:Campaign {id, name, pattern_type, severity}`

### 4.2 Relationship Types
- `(:Incident)-[:HAS_EVENT]->(:Event)`
- `(:Event)-[:FOLLOWED_BY]->(:Event)`
- `(:Message)-[:CONTAINS]->(:URL)`
- `(:URL)-[:HOSTED_ON]->(:Domain)`
- `(:Domain)-[:RESOLVES_TO]->(:IP)`
- `(:PaymentRequest)-[:TARGETS_BENEFICIARY]->(:PaymentEntity)`
- `(:Campaign)-[:CONTROLS]->(:Domain)`
- `(:Campaign)-[:COLLECTS_VIA]->(:PaymentEntity)`
