# Cross-Victim & Cross-Incident Correlation Engine (Phase 3B)

## 1. Executive Summary

ScamGraph's Cross-Incident Correlation Engine transforms isolated incident assessments into collective network intelligence. Rather than judging whether each user's report looks like a scam in a vacuum, the engine links incidents across multiple independent evidence classes:

1. **Entity Evidence**: Shared rare UPI VPAs, phone numbers, dedicated phishing domains, and Telegram handles.
2. **Behavioral DNA**: Invariant multi-step scam journeys and tactic profiles via **ScamDNA V3**.
3. **Infrastructure**: Shared platform migration paths and technical indicators, with zero weight given to common CDNs.
4. **Temporal Intelligence**: Concurrent burst activity and inter-incident spacing.
5. **Graph Paths**: Meaningful entity-incident bipartite graph hops.

Crucially, **correlation is never attribution**. The engine outputs calibrated relationship statuses (`POSSIBLY_RELATED`, `LIKELY_RELATED_PATTERN`, `STRONGLY_RELATED`) and never accuses real-world individuals (`SAME_CRIMINAL` is strictly prohibited).

---

## 2. Two-Stage Candidate Retrieval Architecture

To prevent dangerous $O(N^2)$ cross-incident comparisons at startup scale (tens of thousands to millions of incidents), the engine utilizes a strict two-stage pipeline:

```
[ New Incident Arrives ]
           │
           ▼
Stage 1: Multi-Source Candidate Retrieval (<10ms)
├── Exact & Normalized Rare Identifier Index
├── ScamDNA Nearest Neighbors (DNACandidateIndex)
├── Scam Family & Temporal Window Neighborhood (90-day window)
└── Budget Cap: Max 25 per source, Max 60 candidates total
           │
           ▼
Stage 2: Detailed Correlation Scoring & Gating
├── Feature Extraction (Entity, Infra, Behavioral, Temporal, Graph)
├── Super-Node Suppression (SBI, Telegram, Cloudflare downweighted to 0)
├── Double-Counting Protection (Group caps)
├── Contradiction Penalty Factor
└── Materialization (Symmetric canonical ID: corr_min_max)
           │
           ▼
[ Materialized Relationships & Privacy-Safe Alerts ]
```

---

## 3. Relationship Status & Calibration

| Status | Threshold | Confidence | Evidence Strength | Action / Meaning |
|---|---|---|---|---|
| `STRONGLY_RELATED` | $\ge 0.78$ | $\ge 0.85$ | `VERY_STRONG` | Multi-signal link (e.g. shared rare UPI + identical task journey). |
| `LIKELY_RELATED_PATTERN` | $\ge 0.62$ | $\ge 0.70$ | `STRONG` | Distinctive behavioral alignment with supporting infrastructure. |
| `POSSIBLY_RELATED` | $\ge 0.45$ | $\ge 0.60$ | `MODERATE` | Behavioral candidate (e.g. 100% rotated identifiers with ScamDNA). |
| `WEAK_SIGNAL` | $\ge 0.28$ | $< 0.60$ | `WEAK` | Superficial overlap without distinctive proof. Not materialized. |
| `NOT_RELATED` | $< 0.28$ | Any | `WEAK` | Unrelated or filtered by hard negative super-node gates. |
| `INSUFFICIENT_EVIDENCE`| N/A | $< 0.40$ | `WEAK` | Abstains from linking due to lack of comparable dimensions. |
| `NEEDS_REVIEW` | Borderline | Variable | Variable | Flagged for expert fraud analyst queue. |

---

## 4. Super-Node & Anti-Collision Policy

- **Generic Brands**: SBI, HDFC, ICICI, RBI, Amazon, Flipkart, FedEx, TRAI, Police, CBI. If two incidents only share a generic brand mention, `overall_score = 0.0` and status is `NOT_RELATED`.
- **Common CDNs & Infrastructure**: Cloudflare, Cloudfront, AWS, Fastly, Akamai, Bitly, wa.me. Contributing weight is hard-coded to `0.0`.
- **Contradiction Penalty**: If one incident is verified legitimate while the other is malicious, or if payment identifiers match but journeys diverge completely, a severe penalty ($\min(0.65, n \times 0.40)$) is applied.
