# ScamDNA V3: Multi-Dimensional Similarity & Variant Classification

## 1. Principles of Multi-Dimensional Comparison
ScamDNA V3 rejects the naive approach of compressing an entire incident into a single vector and computing cosine similarity. Real-world fraud variants mutate across specific dimensions while holding other dimensions constant.

Each dimension has a specialized similarity metric:
1. **Semantic**: Cosine similarity on dense embedding vectors + Jaccard similarity on requested actions.
2. **Journey**: Sequence alignment ratio via ordered subsequence matching + monetization boundary concordance.
3. **Tactic**: Weighted multi-label Jaccard similarity where rare, coercive tactics (`ISOLATION`, `AUTHORITY`, `SECRECY`) carry higher discriminative weights than ubiquitous tactics (`URGENCY`).
4. **Infrastructure**: Ordered channel traversal alignment + platform migration concordance.
5. **Payment**: Financial progression sequence alignment + fee-after-block extortion match.
6. **Identity**: Category equivalence matching across institutional archetypes.
7. **Temporal**: Normalized distance on elapsed duration + pace concordance.
8. **Graph**: Topology tier and cluster connectivity concordance.

---

## 2. Missing-Dimension Dynamic Re-normalization
When comparing two incidents where one or both lack certain dimensions (e.g. an incident reported before payment occurred lacks the `PAYMENT` dimension):
1. **Never Zero-Out**: Unavailable dimensions are not assigned a score of `0.0`, which would artificially penalize the similarity index.
2. **Re-normalize Active Weights**: The similarity engine filters the weight configuration to only the dimensions mutually available in both DNA instances:
   $$W_{\text{active}} = \sum_{d \in \text{Mutual}} w_d$$
   $$w'_d = \frac{w_d}{W_{\text{active}}}$$
   $$\text{Similarity} = \sum_{d \in \text{Mutual}} w'_d \cdot S_d$$
3. **Calibrated Match Confidence**: While similarity reflects behavioral alignment on comparable dimensions, `match_confidence` is scaled by dimensional coverage:
   $$\text{Coverage} = \frac{|\text{Mutual Dimensions}|}{8}$$
   $$\text{Confidence} = 0.50 \cdot \text{Coverage} + 0.50 \cdot \bar{C}_{\text{dimensions}}$$

---

## 3. Contradiction Penalization
If two incidents exhibit superficial linguistic similarity but fundamental structural contradictions (e.g., an official bank advisory containing no coercion vs a phishing attack demanding immediate OTPs), a contradiction is flagged:
$$\text{Penalized Similarity} = \text{Similarity} \times (1.0 - \text{Contradiction Penalty Factor})$$

---

## 4. Calibrated Variant Classification
Based on the composite similarity index and match confidence:

| Variant Status | Threshold Criteria | Interpretation |
| :--- | :--- | :--- |
| **`KNOWN_PATTERN`** | Similarity $\ge 0.80$ & Confidence $\ge 0.60$ | High-fidelity behavioral clone of a known scam campaign. |
| **`LIKELY_VARIANT`** | Similarity $\ge 0.65$ & Confidence $\ge 0.50$ | Probable mutation; underlying sequence and tactics match despite rotated identifiers. |
| **`POSSIBLE_VARIANT`** | Similarity $\ge 0.50$ & Confidence $\ge 0.40$ | Emerging pattern sharing partial behavioral traits; warrants analyst review. |
| **`NOVEL_PATTERN`** | Similarity $< 0.38$ with adequate evidence | Unrecognized attack vector; triggers emerging scam taxonomy discovery. |
| **`INSUFFICIENT_EVIDENCE`**| Mutually available dimensions $< 2$ | Inadequate data to render a reliable comparison. |
