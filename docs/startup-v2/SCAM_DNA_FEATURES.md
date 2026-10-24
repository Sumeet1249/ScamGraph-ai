# ScamDNA V3: Feature Registry & Stability Taxonomy

## 1. Feature Stability Classes
To ensure mutation resilience, features within ScamDNA are categorized into three stability tiers:

| Stability Tier | Description | Examples | Mutation Likelihood |
| :--- | :--- | :--- | :--- |
| **`STABLE`** | Deep behavioral & cognitive patterns that fraudsters cannot easily alter without destroying their business model. | Stage progression sequence, reward-before-deposit pattern, isolation requirement, fear levers. | Very Low (< 10%) |
| **`SEMI_STABLE`** | Structural channels and platform migrations requiring operational effort to pivot. | Cross-channel migration path (Social Media → WhatsApp → Telegram), institutional class (Police, Telecom). | Moderate (30–40%) |
| **`VOLATILE`** | Surface-level identifiers easily rotated or spoofed in bulk. | Exact domain name, phone number, specific UPI handle, exact wording. | Extremely High (> 90%) |

---

## 2. Dimensional Feature Catalog

### 1. Semantic Dimension (`SEMANTIC`)
- `intent_summary`: Standardized summary of demand (`JOB_OFFER`, `AUTHORITY_EXTORTION`, `LOTTERY`, `REFUND`). [STABLE]
- `requested_actions`: Demands imposed on victim (`TRANSFER_FUNDS`, `ENTER_OTP`, `INSTALL_REMOTE_APP`, `JOIN_TELEGRAM_GROUP`). [STABLE]
- `vector_embedding`: Dense vector representing invariant conversational semantics. [SEMI_STABLE]

### 2. Journey Dimension (`JOURNEY`)
- `stage_sequence`: Chronological list of stages observed. [STABLE]
- `current_stage`: Most advanced stage currently reached. [STABLE]
- `monetization_boundary_crossed`: Boolean indicating whether a payment or credential extraction request occurred. [STABLE]
- `monetization_status`: 8-state progression status. [STABLE]
- `pre_loss_warning_issued`: Boolean indicating proactive pre-loss alert status. [STABLE]

### 3. Tactic Dimension (`TACTIC`)
- `tactics`: List of detected social engineering levers from the 20-tactic ontology. [STABLE]
- `primary_tactic`: Leading psychological driver. [STABLE]
- `has_isolation`: Flag for forced isolation or secrecy tactics. [STABLE]
- `has_pressure`: Flag for urgency or legal threats. [STABLE]

### 4. Infrastructure Dimension (`INFRASTRUCTURE`)
- `channels`: Ordered list of communication channels traversed. [SEMI_STABLE]
- `channel_progression`: String sequence (`INSTAGRAM > WHATSAPP > TELEGRAM > UPI`). [SEMI_STABLE]
- `has_platform_migration`: Multi-platform movement indicator. [SEMI_STABLE]
- `uses_private_channel`: Presence of encrypted chat apps. [SEMI_STABLE]

### 5. Payment Dimension (`PAYMENT`)
- `payment_progression`: Sequence of financial demands (`SMALL_REWARD > INITIAL_DEPOSIT > ESCALATED_DEPOSIT > UNFREEZE_FEE`). [STABLE]
- `progression_signature`: String signature of financial extortion. [STABLE]
- `recipient_psp_category`: Classification of recipient handle (`PERSONAL_HANDLE`, `MERCHANT_GATEWAY`, `UNKNOWN`). [SEMI_STABLE]
- `relative_escalation_ratio`: Multiplier between subsequent payment demands. [STABLE]
- `fee_after_block`: Demands for tax or clearance to unlock frozen balances. [STABLE]

### 6. Identity Dimension (`IDENTITY`)
- `impersonated_category`: Class of purported organization (`LAW_ENFORCEMENT`, `BANK`, `TASK_JOB_PLATFORM`, `UTILITY`). [SEMI_STABLE]
- `authority_role_present`: Presence of law enforcement, court, or statutory authority claims. [STABLE]

### 7. Temporal Dimension (`TEMPORAL`)
- `duration_seconds`: Total interaction window. [SEMI_STABLE]
- `temporal_pace`: Pace classification (`RAPID_PRESSURE` vs `PATIENT_GROOMING`). [STABLE]
- `accelerating_pressure`: Boolean flag if event gaps contract rapidly prior to payment. [STABLE]

### 8. Graph Dimension (`GRAPH`)
- `degree_centrality_tier`: Network connectivity classification (`ISOLATED`, `LOW`, `HUB`). [SEMI_STABLE]
- `community_cluster_id`: Pseudonymized cluster identifier from graph engine. [SEMI_STABLE]
