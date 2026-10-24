# Cross-Victim Privacy & Anti-Enumeration Firewall (Phase 3B)

## 1. Core Privacy Doctrine: Collective Defense Without Victim Exposure

In ScamGraph, **cross-victim intelligence is strictly segregated from victim identity**:

> **A user must benefit from the fact that an identifier was reported by other victims without ever learning WHO reported it, WHERE they are located, WHAT private messages were exchanged, or WHICH incident ID corresponds to their report.**

---

## 2. Privacy Guarantees by Access Tier

### Consumer Tier (`GET /api/v1/incidents/{id}/network-signal` or `access_tier=CONSUMER`)
1. **Zero Foreign Identifiers**: Foreign incident IDs, user IDs, phone numbers, UPI VPAs, and raw message texts are completely stripped.
2. **Aggregated Reporting Bands**: The engine never states *"reported by exactly 1 other user"* (which could allow targeted re-identification). Instead, it uses qualitative bands:
   - `NO_PRIOR_REPORTS`: 0 related reports.
   - `LIMITED_REPORTS`: 1 report (suppressed to generic caution).
   - `MULTIPLE_REPORTS`: 2–4 verified related reports.
   - `EXTENSIVE_REPORTS`: 5+ verified related reports.
3. **Anti-Small-Cohort Threshold**: Configurable `minimum_cohort_size_for_disclosure = 2`.
4. **Actionable Plain-Language Guidance**: Instead of displaying network graphs or similarity scores, consumers receive clear advice:
   - *"The payment destination in this interaction has appeared in other suspicious reports."*
   - *"Do NOT transfer money to this payment identifier. Verify with bank or report to cybercrime.gov.in (1930)."*

### Analyst Tier (`access_tier=ANALYST`)
- Full feature attribution, explainable graph paths, and masked canonical entity references (e.g. `98200***21`, `paytm***@upi`).
- Audit trail recording which models and rule versions produced the correlation.
