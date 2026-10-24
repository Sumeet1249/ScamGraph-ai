# Data Foundation V2 Specification

**Phase 0B: Architecture & Data Foundation**  
**Date:** October 24, 2026

---

## 1. Hierarchy & First-Class Objects

ScamGraph AI introduces an enterprise-grade data hierarchy designed to scale from individual user SMS checks to national-scale cross-victim correlation:

```mermaid
graph TD
    ART[ARTIFACT (Raw Observed Telemetry)] --> EVT[EVENT (Atomic Timestamped Interaction)]
    EVT --> INC[INCIDENT (Multi-Stage Fraud Encounter)]
    INC --> CMP[CAMPAIGN (Unsupervised Clustered Infrastructure)]
    
    subgraph Supporting First-Class Primitives
        ENT[ENTITY (Resolved Identifiers)]
        EVI[EVIDENCE SIGNAL (Typed Multi-Signal Finding)]
        CLM[CLAIM (Asserted Relationship or Impersonation)]
        ASM[ASSESSMENT (Tri-Axis Risk, Confidence, Urgency)]
        JRN[JOURNEY (Multi-Stage Progression State)]
        DNA[SCAM DNA (Cross-Incident Genomic Fingerprint)]
        INT[INTERVENTION (Dynamic Defensive Friction)]
    end

    ART -.-> ENT
    EVT -.-> EVI
    INC -.-> ASM
    INC -.-> JRN
    INC -.-> DNA
```

---

## 2. Core V2 Schemas

### 1. `Artifact` (`packages/schemas/artifact.py`)

Represents an individual submitted or observed digital artifact across any communication channel.

- __`artifact_id`__: Prefixed non-sequential stable ID (`art_<16hex>`).
- __`artifact_type`__: `MESSAGE`, `URL`, `PHONE`, `EMAIL`, `QR`, `PAYMENT_REQUEST`, `SOCIAL_PROFILE`, `SCREENSHOT`, `VOICE_TRANSCRIPT`, `DOCUMENT`, `WEB_PAGE`, `OTHER`.
- **`channel`**: Communication channel (`SMS`, `WHATSAPP`, `TELEGRAM`, `CALL`, `WEB`, `UPI`).
- __`content_reference`__: Object-storage URI or content hash pointer for binary assets.
- __`normalized_content`__: Cleaned/normalized text representation for NLP extraction.
- __`privacy_classification`__: Sensitivity tier (`PUBLIC`, `INTERNAL`, `PERSONAL`, `SENSITIVE`, `HIGHLY_SENSITIVE`).

### 2. `Event` (`packages/schemas/events.py`)

Represents an atomic, chronological event in an incident.

- **Backward Compatibility**: Fully compatible with existing `Event` consumers.
- **V2 Extensions**:
   - `schema_version = "2.0"`
   - `actor_role`: `ActorRole` (`USER`, `UNKNOWN_ACTOR`, `PLATFORM`, `ORGANIZATION`, `SYSTEM`, `UNKNOWN`).
   - `artifact_ids`: Decoupled references to originating `Artifact` instances.
   - `entities`: References to extracted canonical entity nodes.

### 3. `Incident` (`packages/schemas/incident.py`)

The top-level container for a fraud journey encounter.

- __`incident_id`__: Prefixed non-sequential stable ID (`inc_<16hex>`).
- __Decoupled References__: Stores lists of IDs (`event_ids`, `artifact_ids`, `entity_ids`, `evidence_ids`) instead of monolithic nested arrays, enabling horizontal scalability.
- **Tri-Axis Metric Separation**:
   - `current_risk`: `RiskLevelV2` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `UNKNOWN`).
   - `current_confidence`: `ConfidenceLevelV2` (`LOW`, `MEDIUM`, `HIGH`, `UNKNOWN`).
   - `current_urgency`: `UrgencyLevelV2` (`NONE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

- __`status`__: `OPEN`, `ANALYZING`, `ASSESSMENT_READY`, `MONITORING`, `ESCALATED`, `RESOLVED`, `CLOSED`, `INSUFFICIENT_EVIDENCE`.

### 4. `Entity` (`packages/schemas/entity.py`)

Canonical representation of digital/physical identifiers.

- __`entity_type`__: `PHONE`, `EMAIL`, `URL`, `DOMAIN`, `UPI_VPA`, `BANK_ACCOUNT_TOKEN`, `SOCIAL_ACCOUNT`, `TELEGRAM_HANDLE`, `WHATSAPP_NUMBER`, `BRAND`, `ORGANIZATION`, `IP_ADDRESS`, `CRYPTO_ADDRESS`, `DEVICE_TOKEN`, `OTHER`.
- **Privacy Enforcement**:
   - `masked_value`: Safe for display (`******3210`, `s***@oksbi`).
   - `canonical_hash`: Deterministic SHA-256 or HMAC-SHA256 for secure database matching.
   - `canonical_value`: Restricted to internal processing.

- __Verification States__: `UNKNOWN`, `UNVERIFIED`, `OBSERVED`, `CORROBORATED`, `DISPUTED`, `VERIFIED_LEGITIMATE`, `VERIFIED_MALICIOUS`.
   > [!IMPORTANT]
   > `VERIFIED_MALICIOUS` requires verified multi-incident corroboration or official reporting. Single user reports or heuristic scores cannot unilaterally apply this label.

### 5. `ScamGraphRecordV2` (`packages/schemas/dataset.py`)

Canonical training and evaluation record unifying SMS, conversations, journey events, and hard negatives.

- Complete metadata wrappers: `LanguageMetadata`, `QualityMetadata`, `SplitMetadata`, and `SourceProvenanceRecord`.
- Round-trip adapters (`to_legacy()`, `from_legacy()`) ensuring complete backward-compatibility with existing message ML loaders.

---

## 3. Privacy & Masking Utilities (`packages/utils/privacy.py`)

- __Phone Numbers__: Masked as `******3210` (`mask_phone`).
- __Emails__: Masked as `p***@example.com` (`mask_email`).
- __UPI VPAs__: Masked as `s***@oksbi` (`mask_vpa`).
- __Bank Accounts__: Masked as `********9012` (`mask_bank_account`).
- __Canonical Hashing__: Deterministic `canonical_hash(value, secret=None)` with SHA-256 or HMAC support.
