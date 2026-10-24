# ScamGraph AI — Production Inference Architecture

> **Document Version**: 1.0.0  
> **Status**: APPROVED  
> **Phase**: 0E — Production Inference Architecture & Tiering  
> **Target Scale**: 100K $\rightarrow$ 1M $\rightarrow$ 10M+ Consumer Checks  

---

## 1. Core Architectural Principle

```
RIGHT MODEL FOR RIGHT TASK AT RIGHT COST
```

ScamGraph does not force every incoming message into a 300M+ parameter transformer or expensive commercial LLM. Doing so would bankrupt unit economics and introduce 500ms–2000ms latency on simple mobile connections. Instead, ScamGraph implements a **4-tier inference architecture** running CPU-first at the edge and consumer layer, escalating only when justified by risk signals, ambiguity, or entity impact.

---

## 2. The Four Inference Tiers

```
+-----------------------------------------------------------------------------------+
| TIER 0: DETERMINISTIC EDGE TRIAGE (<1.5ms, Cost: NEGLIGIBLE)                      |
| - Normalization, canonical hashing, regex entity extraction, local cache lookup    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| TIER 1: FAST CONSUMER ML (<15ms CPU, Cost: LOW)                                   |
| - Word + Character TF-IDF Ensemble (scamgraph-word-char-ensemble)                 |
| - Multilingual E5-Small embeddings (intfloat/multilingual-e5-small, 384 dims)     |
| - Disagreement Detection & Calibrated Scoring                                     |
+-----------------------------------------------------------------------------------+
                                         | (Escalation Trigger)
                                         v
+-----------------------------------------------------------------------------------+
| TIER 2: DEEP INTELLIGENCE (15-80ms CPU/GPU, Cost: MEDIUM)                        |
| - Multilingual Transformer Reranker (Horizon-Labs / fine-tuned candidate)         |
| - BGE-M3 High-Dimension Journey Embeddings (1024 dims, 8192 context window)        |
| - Graph Pattern & Campaign Retrievability                                         |
+-----------------------------------------------------------------------------------+
                                         | (Analyst Request / High Harm)
                                         v
+-----------------------------------------------------------------------------------+
| TIER 3: DEEP INVESTIGATION (>80ms, Cost: HIGH / ASYNC WORKER)                     |
| - TinyFish active web inspection & domain crawl                                   |
| - Structured LLM timeline reconstruction & tactic extraction                      |
| - Law enforcement reporting pack compilation                                      |
+-----------------------------------------------------------------------------------+
```

### Detailed Tier Specifications

| Tier | Name | Target p95 Latency | Max Timeout | Hardware | Compute Cost | Primary Components |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **Tier 0** | Deterministic Edge | <1.5 ms | 5.0 ms | CPU / Edge | `NEGLIGIBLE` | Normalization, regex impersonation patterns, canonical hash cache |
| **Tier 1** | Fast Consumer ML | <15.0 ms | 50.0 ms | Multi-core CPU | `LOW` | `scamgraph-word-char-ensemble`, `multilingual-e5-small` |
| **Tier 2** | Deep Intelligence | <75.0 ms | 250.0 ms | CPU / GPU | `MEDIUM` | Transformer sequence classifier, `bge-m3` journey retrieval |
| **Tier 3** | Deep Investigation | <1500.0 ms | 5000.0 ms | Async Workers | `HIGH / PAID` | TinyFish web crawler, structured LLM extraction, graph mining |

---

## 3. Fast Path vs Deep Path Routing

### Fast Path (Benign Triage)
1. Message exhibits legitimate transactional alert signature (`credited to your a/c`, `ref no`, `debited`).
2. No credential solicitation (`OTP`, `PIN`, `KYC update`) detected.
3. No coercive urgency tactics detected.
4. Tier 1 ensemble produces high confidence ($p < 0.15$ or $p > 0.85$) with $0.0$ disagreement delta.
5. **Action**: Immediate response returned in <5ms without escalating to Tier 2/3.

### Deep Path (Escalation Triggers)
A check escalates from Tier 1 to Tier 2 when any of the following conditions occur:
1. **Model Disagreement**: Word TF-IDF and Character TF-IDF probabilities diverge by $\ge 0.35$.
2. **Ambiguous Confidence Zone**: Calibrated scam probability falls between $0.35$ and $0.65$.
3. **High-Harm Impersonation**: Claimed authority involves Police, CBI, Cyber Cell, High Court, Customs, or Electricity Department.
4. **Platform Migration**: Request instructs victim to move conversation to Telegram, WhatsApp, or APK download.
5. **Rule-Model Contradiction**: Deterministic rules detect $\ge 2$ coercive tactics, but lexical classifier predicts benign.

---

## 4. Fallback Architecture & Degraded Mode (Rule 44)

> [!CAUTION]
> **Fundamental Safety Rule**: External service failure or model timeout **NEVER** defaults to `SAFE` / `LIKELY_SAFE`. An outage is not evidence of safety.

```
Model/Service Fails
       |
       +---> Has Local Tier 1 Result? ---> Use Tier 1 Result with confidence penalty
       |
       +---> Complete Outage?       ---> Return INSUFFICIENT_EVIDENCE
                                          (Flag: degraded_mode=True, missing_capabilities=[...])
```

- When Tier 2 transformer fails or times out: Fallback immediately to Tier 1 `scamgraph-word-char-ensemble`. Set `fallback_used = True`.
- When semantic embedding encoder fails: Fallback to deterministic n-gram hash projection.
- When external crawling (TinyFish) fails: Return partial intelligence package with user-facing message: *"Some verification sources are temporarily unavailable."*

---

## 5. Cache Architecture (Rule 43)

- **Key Format**: `sha256(canonical_normalized_text) + ":" + model_id + ":" + model_version + ":" + intelligence_version`
- **Normalization**: Unicode canonical decomposition, lowercase, whitespace collapse, punctuation stripping.
- **TTL Policies**:
  - Message classification results: 1 hour (3600s)
  - URL threat results: 15 minutes (900s)
  - VPA / Payment recipient intelligence: 30 minutes (1800s)
  - Entity threat status: 2 hours (7200s)

---

## 6. CPU-First Scaling Economics

- **1M monthly checks**: At ~5ms per check on CPU, 1M checks require ~1.4 CPU hours total compute per month, easily served by a single 4-core virtual instance ($30/month).
- **10M monthly checks**: With 40% cached, 6M active inferences require ~8 CPU hours/day, served by a 3-node cluster ($150/month).
- **If every check used an un-tiered LLM**: 10M checks $\times$ $0.002 = $20,000/month.
- **ScamGraph Tiered Architecture Cost Efficiency**: >98% infrastructure cost reduction while achieving sub-20ms latency for consumers.
