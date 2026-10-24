# ScamDNA V3: Multi-Dimensional Behavioral Fingerprinting & Invariant Signatures

## 1. Mission and Problem Definition
Traditional scam detection relies heavily on superficial artifacts: exact telephone numbers, specific domain names, UPI Virtual Payment Addresses (VPAs), and exact phrasing. Modern scam syndicates continuously rotate these surface identifiers—changing domain names hourly, buying pre-activated SIMs in bulk, rotating mule accounts, and rewriting copy.

**ScamDNA V3** is ScamGraph AI's core proprietary behavioral fingerprinting engine. It asks:
> *"Does the underlying interaction behavior resemble known scam operations even when every surface identifier, message text, and payment handle has mutated?"*

---

## 2. The 8 Modular Behavioral Dimensions
ScamDNA V3 models scam operations across 8 decoupled, invariant dimensions:

```
                                  INCIDENT
                                     │
         ┌───────────────┬───────────┼───────────┬───────────────┐
         ▼               ▼           ▼           ▼               ▼
      Semantic        Journey     Tactic     Payment         Identity
         │               │           │           │               │
         ├───────────────┴───────────┼───────────┴───────────────┤
         ▼                           ▼                           ▼
  Infrastructure                  Temporal                     Graph
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     ▼
                              ┌─────────────┐
                              │ SCAM DNA V3 │
                              └─────────────┘
```

1. **`SEMANTIC`**: Meaning, underlying intent, and requested action vectors (via Phase 0E approved multilingual embeddings and normalized action ontology).
2. **`JOURNEY`**: Ordered progression across universal stages (`DISCOVERY → CONTACT → PLATFORM_MIGRATION → REWARD → PAYMENT → ESCALATION → BLOCK → RECOVERY_FEE`).
3. **`TACTIC`**: Extracted social-engineering manipulation patterns (from Phase 1B 20-tactic ontology: `AUTHORITY`, `ISOLATION`, `SECRECY`, `FAKE_REWARD`, `PAYMENT_PRESSURE`).
4. **`INFRASTRUCTURE`**: Channel progression (`INSTAGRAM → WHATSAPP → TELEGRAM → UPI`), domain structural characteristics, redirect chains, and platform hopping. Zero raw URLs or domains required.
5. **`PAYMENT`**: Behavioral payment progression (`SMALL_REWARD → INITIAL_DEPOSIT → ESCALATED_DEPOSIT → UNFREEZE_FEE`), recipient handle PSP category, and relative escalation ratios.
6. **`IDENTITY`**: Claimed institutional class (`LAW_ENFORCEMENT`, `BANK`, `TASK_JOB_PLATFORM`, `UTILITY`) and identity switching roles.
7. **`TEMPORAL`**: Interaction duration, inter-event gap pace (`RAPID_PRESSURE` vs `PATIENT_GROOMING`), and acceleration patterns.
8. **`GRAPH`**: Structural topology (degree centrality tier, candidate community cluster ID, cross-incident structural motifs).

---

## 3. Core Architectural Guarantees
- **Zero Raw PII Storage**: Phone numbers, VPAs, victim names, and raw credentials are NEVER placed into ScamDNA vectors or signatures. All features are structural, categorized, or masked.
- **Partial DNA Handling**: If an incident provides only a single SMS, dimensions for Payment, Journey, and Graph are marked `available=False` rather than zeroed out. The similarity engine dynamically re-normalizes weights across mutually comparable dimensions.
- **Strict Distinction**:
  $$\text{DNA Quality} \neq \text{Match Confidence} \neq \text{Similarity Index} \neq \text{Incident Risk}$$
- **Sub-Linear Candidate Retrieval**: Inverted candidate indexing allows fast pre-filtering on family, journey prefix, and key tactics before performing expensive 8-dimensional pairwise calculations.
