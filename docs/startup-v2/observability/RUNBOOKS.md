# OPERATIONAL RUNBOOKS & INCIDENT RESPONSE
**ScamGraph AI — Phase 7C Production Runbooks**
*Document Version: 3.0.0 | Date: 2026-10-24*

---

## Runbook 1: Protect Latency Spike (SEV1)
- **Symptom**: Protect API p95 latency > 300ms.
- **Initial Action**: Check Redis cache hit rate and external provider response times.
- **Remediation**: If TinyFish or LLM provider is slow, enable cached heuristic fast-path (`FALLBACK_LOCAL_RULES=true`).

## Runbook 2: Background Queue Backlog (SEV2)
- **Symptom**: Queue depth > 100 or oldest job age > 15 minutes.
- **Initial Action**: Inspect worker status via `/health/deep`.
- **Remediation**: Scale worker concurrency pool for `media` or `intelligence` worker classes.

## Runbook 3: Outbreak Radar Stale (SEV2)
- **Symptom**: Radar freshness status transitions to `DELAYED` or `STALE` (> 15m).
- **Initial Action**: Check if campaign worker has failed or is waiting on distributed lock.
- **Remediation**: Release expired campaign lock or trigger manual campaign snapshot recomputation.

## Runbook 4: AI Quality Regression Detected (SEV1)
- **Symptom**: Golden regression suite detects negation failure (e.g. "Never share OTP" flagged as scam).
- **Initial Action**: Automatic release gate blocks deployment (`is_release_blocked = true`).
- **Remediation**: Rollback candidate model version to previous stable version; inspect prompt/tokenizer.

## Runbook 5: Scam Drift / Campaign Surge (SEV3)
- **Symptom**: Campaign velocity multiplier > 3.0x baseline.
- **Initial Action**: Review emerging victim reports in Command Center.
- **Remediation**: Verify whether a new coordinated cyber fraud syndicate is active; dispatch partner threat alert webhooks.
