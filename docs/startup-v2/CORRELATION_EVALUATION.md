# Correlation Engine Evaluation & Validation Protocol (Phase 3B)

## 1. Evaluation Protocol

To prevent test-set leakage and synthetic evaluation bias:
1. **Incident Pairs Protocol**: Incidents are evaluated pairwise. Ground-truth labels are:
   - `RELATED`: Multi-signal or shared rare identifier links.
   - `NOT_RELATED`: Independent incidents or hard negatives.
   - `UNCERTAIN`: Ambiguous/borderline cases flagged for human analyst review.
2. **Hard Negatives Requirement**:
   - Generic brand impersonation pairs (two independent scammers mentioning SBI).
   - Shared common CDN pairs (two phishing sites using Cloudflare).
   - Same-family but independent incidents (two task scams operating months apart with distinct entities).
   - Benign interaction vs scam (real recruiter vs task scam).

---

## 2. Benchmark Metrics

- **`RELATED_PAIR_RECALL`**: Fraction of true related incident pairs retrieved in Stage 1 and scored $\ge 0.62$.
- **`FALSE_RELATION_RATE`**: Fraction of hard negative pairs incorrectly scored as `STRONGLY_RELATED` or `LIKELY_RELATED_PATTERN`. (Must be $< 1.0\%$).
- **`STRONG_RELATION_PRECISION`**: Precision of incidents classified as `STRONGLY_RELATED`.
- **`RETRIEVAL_RECALL@K`**: Candidate coverage at budget $K=60$.
- **`IDENTIFIER_ROTATION_RECALL`**: Fraction of mutated campaigns (all identifiers rotated) correctly recovered as `POSSIBLY_RELATED` via ScamDNA.
