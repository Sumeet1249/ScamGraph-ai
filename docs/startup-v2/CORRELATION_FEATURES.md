# Correlation Feature Registry & Lineage (Phase 3B)

## 1. Feature Registry

| Feature Name | Dimension | Range | Informativeness | Description |
|---|---|---|---|---|
| `exact_payment_overlap` | ENTITY | `[0.0, 1.0]` | Very High (1.00) | 1.0 if identical canonical UPI VPA or bank token is shared. |
| `exact_phone_overlap` | ENTITY | `[0.0, 1.0]` | High (0.85) | 1.0 if identical normalized E.164 phone is shared. |
| `exact_domain_overlap` | ENTITY | `[0.0, 1.0]` | High (0.80) | 1.0 if identical non-CDN domain is shared. |
| `exact_social_overlap` | ENTITY | `[0.0, 1.0]` | Medium-High (0.75) | 1.0 if identical Telegram/social handle is shared. |
| `weighted_entity_overlap`| ENTITY | `[0.0, 1.0]` | High | Informativeness-weighted Jaccard over all mutual rare entities. |
| `infrastructure_similarity`| INFRA | `[0.0, 1.0]` | Medium (0.15 cap)| Ratio of aligned platform migration steps (e.g. WA > TG > UPI). |
| `dna_similarity` | BEHAVIORAL| `[0.0, 1.0]` | High (0.35 cap) | Multi-dimensional ScamDNA V3 match score. |
| `dna_coverage` | BEHAVIORAL| `[0.0, 1.0]` | Moderate | Comparable dimensions count / 8.0. |
| `journey_similarity` | BEHAVIORAL| `[0.0, 1.0]` | High | Sequence alignment ratio of scam journey stages. |
| `tactic_similarity` | BEHAVIORAL| `[0.0, 1.0]` | Medium | Informativeness-weighted Jaccard over psychological tactics. |
| `semantic_similarity` | SEMANTIC | `[0.0, 1.0]` | Low-Medium | Text / narrative sequence alignment. |
| `temporal_similarity` | TEMPORAL | `[0.0, 1.0]` | Moderate (0.15) | Linear decay over 90-day window; burst bonus if $\le 7$ days. |
| `graph_path_score` | GRAPH | `[0.0, 1.0]` | Moderate (0.15) | 1.0 for 1-hop rare entity; 0.6 for 2-hop infra; 0.0 for supernode. |
| `contradiction_score` | QUALITY | `[0.0, 1.0]` | Severe Negative | Penalty score from verified legitimate status or journey divergence. |

---

## 2. Double-Count Controls

Because ScamDNA already encapsulates journey, tactics, and payment behavior:
- Group 2 (`BEHAVIORAL`) takes the **maximum** of `dna_similarity` or the combination of Journey and Tactics.
- The behavioral group contribution is strictly capped at **0.35**.
- Entity contribution is strictly capped at **0.45**.
- This guarantees that two task scams cannot be classified as `STRONGLY_RELATED` on behavioral similarity alone without shared rare identifiers or multi-signal corroboration.
