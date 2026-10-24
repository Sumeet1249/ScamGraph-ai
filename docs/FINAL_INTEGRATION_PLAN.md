# ScamGraph AI — Final Integration & Architecture Plan

> **Executive Principle**: We are **NOT** merging 15–17 disparate applications into a bloated monolith. We are harvesting **5 core capabilities** for the MVP, supported by secondary adapters and synthetic generators, while strictly rejecting redundant frameworks, copycat architectures, and experimental complexity.

---

## 1. Minimal Viable Architecture (The MVP Core Selection)

To build the strongest, most stable hackathon project, we select the **minimum necessary set of repositories**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CORE MVP HARVEST (5 ASSETS)                     │
├──────────────────────────┬───────────────────────┬─────────────────────┤
│ Capability               │ Source Reference      │ ScamGraph Location  │
├──────────────────────────┼───────────────────────┼─────────────────────┤
│ 1. Live Web Investigation│ TinyFish Cookbook     │ services/investigation/tinyfish │
│ 2. Infra / URL Security  │ PhishGraph            │ services/investigation/url_analysis │
│ 3. Semantic Clustering   │ VECTPHISH             │ services/pattern-engine/semantic │
│ 4. Graph Entity Fusion   │ Neo4j P2P Fraud       │ services/graph-engine/ │
│ 5. Graph UI Visualizer   │ Cytoscape.js          │ apps/web/components/graph │
└──────────────────────────┴───────────────────────┴─────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│                    SECONDARY ADAPTERS & SYNTHETIC DATA                 │
├──────────────────────────┬───────────────────────┬─────────────────────┤
│ 6. Synthetic UPI/Banking │ PaySim                │ data/synthetic/payment/ │
│ 7. Phishing Techniques   │ IOK                   │ services/investigation/extractors/ │
│ 8. Optional Threat APIs  │ urlscan / vt-py       │ services/investigation/providers/ │
└──────────────────────────┴───────────────────────┴─────────────────────┘
```

### Explicitly Rejected Redundancies
1. **`neomodel` (REJECTED)**: Native official `neo4j` Python async driver is faster, lighter, and avoids rigid OGM abstractions that complicate multi-hop Cypher queries.
2. **`agentql` (REJECTED)**: Redundant with TinyFish. Requires heavy local Playwright/Chromium runtimes without adding new intelligence capabilities.
3. **`FraudGraph` & Kafka/Redis (REJECTED)**: Distributed message brokers and streaming complexity are anti-patterns for a local hackathon prototype.
4. **`phishGNN` & GNN Pipelines (REJECTED FOR MVP)**: Black-box graph neural networks violate Rule 10 & 17 (Explainability & Determinism first). Retained strictly as future academic research.

---

## 2. End-to-End Target ScamGraph Architecture

```
INPUTS
[Message | URL | QR | UPI URI | Payment Request | Call Context]
                           │
                           ▼
                    INCIDENT FUSION
                           │
                           ▼
                    EVENT EXTRACTION
                           │
                           ▼
                SPECIALIZED INTELLIGENCE
  ┌───────────────┬───────────────┬───────────────┬───────────────┐
  │  Message AI   │    URL ML     │   TinyFish    │Payment Context│
  │  (NLP/Urgency)│  (DNS/RDAP)   │ (Web Telemetry│ (VPA Mismatch)│
  └───────────────┴───────────────┴───────────────┴───────────────┘
                           │
                           ▼
                CANONICAL EVIDENCE LAYER
                           │
                           ▼
                  SCAM JOURNEY GRAPH
                           │
                           ▼
                TEMPORAL PATTERN ENGINE
                           │
                           ▼
                    SCAM FINGERPRINT
                           │
                           ▼
             SEMANTIC SIMILARITY (pgvector)
                           │
                           ▼
             GRAPH CORRELATION (Neo4j Cypher)
                           │
                           ▼
                   CAMPAIGN DISCOVERY
                           │
                           ▼
                EMERGING VARIANT DETECTOR
                           │
                           ▼
                  DUAL-AXIS ASSESSMENT
             [Threat Risk + Evidence Confidence]
                           │
                           ▼
                   INTERVENTION POLICY
```

---

## 3. Advanced Scam Fingerprint

Every incident generates an invariant, multi-dimensional fingerprint designed to recognize mutated scam campaigns even when phone numbers, domains, UPI handles, or exact phrasings change:

```json
{
  "fingerprint_id": "fp_8c3b4a12-e567-4f89",
  "incident_id": "inc_7a6b5c4d-1e2f-3a4b",
  "semantic_vector": [0.024, -0.118, 0.452, "... (384 dimensions)"],
  "claimed_identity": "STATE_ELECTRICITY_BOARD",
  "social_engineering_tactics": ["FEAR_OF_DISCONNECTION", "IMMINENT_DEADLINE", "IMPERSONATION"],
  "requested_action": "PAY_NOMINAL_VERIFICATION_FEE",
  "stage_sequence": ["INITIAL_CONTACT", "OFFICIAL_IMPERSONATION", "PHISHING_URL", "UPI_COLLECT"],
  "temporal_pace_seconds": 184,
  "url_lexical_markers": ["suspicious_tld", "hyphenated_brand", "ip_in_url:false"],
  "web_behavior": {
    "has_login_form": false,
    "has_otp_harvesting": true,
    "has_apk_download": false
  },
  "infrastructure_hash": {
    "asn": "AS13335",
    "registrar": "NameCheap",
    "certificate_issuer": "Let's Encrypt",
    "nameserver_suffix": "cloudflare.com"
  },
  "payment_entity_profile": {
    "vpa_domain": "oksbi",
    "is_individual_account": true,
    "merchant_claimed": false
  },
  "campaign_match_id": "camp_electricity_bill_v4"
}
```

---

## 4. Advanced Dual Graph Model

ScamGraph maintains **TWO interconnected graph perspectives** joined through the central `:Incident` node:

```
                    ┌────────────────────────┐
                    │       [:Incident]      │
                    └───┬────────────────┬───┘
                        │                │
            CONTAINS_STEP                EXPOSES_ARTIFACT
                        │                │
                        ▼                ▼
     ┌────────────────────────┐    ┌────────────────────────┐
     │  GRAPH A: SCAM JOURNEY │    │ GRAPH B: INFRASTRUCTURE│
     │     (Psychological)    │    │      (Technical)       │
     └────────────────────────┘    └────────────────────────┘
```

### Graph A — Scam Journey (Psychological Grooming Progression)
- **Nodes**: `:JourneyStep`, `:Message`, `:UrlClick`, `:PaymentRequest`
- **Edges**:
  - `(:JourneyStep)-[:FOLLOWED_BY {timeDeltaSeconds: 45}]->(:JourneyStep)`
  - `(:JourneyStep)-[:BEFORE]->(:JourneyStep)`
  - `(:JourneyStep)-[:WITHIN_TIME_WINDOW {window: "RAPID"}]->(:JourneyStep)`

### Graph B — Infrastructure Graph (Technical Entity Network)
- **Nodes**: `:Url`, `:Domain`, `:IP`, `:ASN`, `:Certificate`, `:Nameserver`, `:Phone`, `:UPIHandle`, `:BankAccount`, `:Campaign`
- **Edges**:
  - `(:Url)-[:HOSTED_ON]->(:Domain)`
  - `(:Domain)-[:RESOLVES_TO]->(:IP)`
  - `(:IP)-[:BELONGS_TO]->(:ASN)`
  - `(:Domain)-[:USES_CERTIFICATE]->(:Certificate)`
  - `(:Domain)-[:SERVED_BY]->(:Nameserver)`
  - `(:Incident)-[:ORIGINATED_FROM]->(:Phone)`
  - `(:PaymentRequest)-[:TARGETS]->(:UPIHandle)`
  - `(:Incident)-[:BELONGS_TO_CAMPAIGN]->(:Campaign)`

---

## 5. Three-Level Emerging Scam Detection

```
Level 1: KNOWN PATTERN
├── Known telephone / VPA / domain
└── Known step progression & template

Level 2: MUTATED VARIANT
├── Brand new telephone / VPA / domain (freshly registered)
└── High cosine similarity to known campaign workflow & tactics

Level 3: EMERGING CAMPAIGN
├── Brand new identifiers
├── Partially novel sequence (e.g. pivoting from Telegram to APK to UPI collect)
├── Clustered with >= 3 recent incidents via DBSCAN / pgvector
└── Shared behavioral fingerprint
```

**Output Status**:
- `KNOWN_PATTERN`: Verified historical signature.
- `MUTATED_VARIANT`: Evolving evasion tactic using fresh endpoints.
- `POSSIBLE_EMERGING_CAMPAIGN`: Novel threat cluster requiring heightened scrutiny.

---

## 6. Next-Step Prediction

By matching an active incident's sequence against the Scam Journey Graph, the engine identifies the victim's **current position** on the grooming ladder and anticipates the scammer's **next move**:

| Current Detected Stage | Anticipated Next Step | Preventive Intervention Trigger |
|---|---|---|
| Initial impersonation text received | Suspicious verification link delivery | Warn user: "Bank never sends APK/shortened links" |
| Phishing landing page visited | Credential / OTP harvest attempt | Flag domain freshness, recommend closing tab |
| Fake earnings displayed on task site | Fee / deposit payment collect request | Pre-payment friction: warn about task deposit scam |
| UPI Collect request initiated | Immediate biometric approval prompt | High-friction 10s delay banner explaining collect danger |

---

## 7. Adaptive Alert Fatigue Policy

Alert fatigue causes users to dismiss critical warnings. Interventions are calibrated against **Risk Level**, **Evidence Confidence**, and **Proximity to Financial Harm**:

```
                       [Proximity to Payment]
                                 │
           Low Proximity         │         High Proximity
       (Message / Link Stage)    │      (UPI Intent / Collect)
   ──────────────────────────────┼──────────────────────────────
High      CAUTION                │ PRE_PAYMENT_INTERVENTION
Conf:     (Contextual Banner)    │ (10s Countdown + Step-up)
                                 │
Low       PASSIVE                │ STRONG_WARNING
Conf:     (Silent Telemetry Log) │ (Verify Recipient Banner)
```

**Action Outcomes**:
1. `NONE`: Normal interaction, no flags.
2. `PASSIVE`: Background evidence logging; no visible UI intrusion.
3. `CAUTION`: Non-intrusive warning tag explaining unverified sender.
4. `STRONG_WARNING`: Prominent banner detailing payee mismatch.
5. `PRE_PAYMENT_INTERVENTION`: Mandatory 10-second countdown friction before payment intent confirmation with explicit journey breakdown.

---

## 8. The Explainability Standard (7 Essential Answers)

Every final assessment presented to an operator or end-user MUST answer:

1. **WHAT happened?** Clear summary of observed steps (e.g., "SMS received -> phishing site visited -> UPI collect requested").
2. **WHY is it suspicious?** Cites concrete contradictions (e.g., "Claimed: Maharashtra State Electricity; Actual Payee: Individual VPA on Axis Bank").
3. **WHEN in the journey did risk escalate?** Highlights the inflection point on the timeline.
4. **WHICH evidence supports it?** Lists all active evidence signals, weights, and confidence levels.
5. **WHICH sources produced evidence?** Full provenance (e.g., TinyFish web scraper, NLP urgency detector, Neo4j handle lookup).
6. **WHAT contradictory or counter-evidence exists?** Notes benign indicators (e.g., "Phone number has 3-year history with user; domain registered 5 years ago").
7. **HOW confident is the system?** Explicit `LOW` / `MEDIUM` / `HIGH` confidence, or `INSUFFICIENT_EVIDENCE`.
8. **WHAT should the user safely do next?** Specific, actionable guidance (e.g., "Decline the UPI collect request. Pay bills exclusively through the official utility app").
