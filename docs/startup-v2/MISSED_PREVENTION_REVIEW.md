# Missed-Prevention Review & Non-Leakage Architecture (Phase 5B)

## Pre-Loss vs Post-Loss Isolation
Evaluating whether ScamGraph could have prevented an incident requires strict temporal integrity:
- **`financial_loss_observed_boundary`**: The exact timestamp of the very first financial loss event.
- **Evidence Partitioning**:
  - `pre_loss_evidence`: Artifacts, messages, and signals received *prior* to `financial_loss_observed_boundary`.
  - `post_loss_evidence`: Evidence obtained during rescue or after payment execution.

> [!CRITICAL]
> **Zero Future Leakage Principle**:
> Historical prevention performance must NEVER be evaluated using post-loss evidence. Benchmarks of pre-payment detection rate must strictly condition only on `pre_loss_evidence`.

---

## Failure Category Taxonomy
Post-loss reviews categorize the reason prevention failed without blaming the user:

| Category | Definition | Startup Learning Feedback |
|---|---|---|
| `NO_PRELOSS_CHECK` | User only interacted with ScamGraph after loss | Expand pre-loss distribution & browser extension footprint |
| `INSUFFICIENT_EVIDENCE` | No pre-loss signals available before transfer | Improve zero-shot detection on initial outreach |
| `MODEL_MISS` | Analysis under-scored early stealth grooming | Train on subtle trust-building signals |
| `JOURNEY_MISS` | Proximity check failed to trigger before payment | Tighten transition rules for initial payment requests |
| `USER_CONTINUED_AFTER_WARNING` | Pre-loss warning shown, but victim proceeded under severe fear/isolation | Strengthen anti-isolation and delay-friction interventions |
