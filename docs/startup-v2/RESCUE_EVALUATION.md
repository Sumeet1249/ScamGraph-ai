# Rescue Evaluation & Metric Verification (Phase 5B)

## 20-Scenario Acceptance Benchmark
The Prompt 16 test suite (`tests/unit/test_rescue_engine_step16.py`) covers all 20 required acceptance tests:

1. **TEST 1 — Task Scam Multiple Payments**: Accurately aggregates ₹500 + ₹5,000 + ₹20,000 into ₹25,500 total, generating 3 distinct `LossEvent`s without duplication.
2. **TEST 2 — Digital Arrest**: High-priority triage, anti-isolation guidance, and 1930 reporting triggered.
3. **TEST 3 — OTP Disclosure Only**: Correctly tracks credential exposure without fabricating monetary loss.
4. **TEST 4 — Remote Access**: Prioritizes termination of AnyDesk/TeamViewer and Airplane Mode before paperwork.
5. **TEST 5 — Identity Document**: Accurately flags Aadhaar/PAN exposure and routes to UIDAI biometric locking.
6. **TEST 6 — Existing Incident Transition**: Pre-loss incident seamlessly transitions status to `ESCALATED` upon "I already paid".
7. **TEST 7 — New Direct Rescue**: Direct arrival without prior interaction initializes a new incident.
8. **TEST 8 — Recovery Scam Warning**: Flags advance-fee recovery offers with critical risk alerts.
9. **TEST 9 — Additional Payment Escalation**: Recognizes "pay tax to unlock" as `RECOVERY_FEE` / `PAYMENT_ESCALATION`.
10. **TEST 10 — Historical Scam (> 30 days)**: Does not falsely claim immediate stop-payment freeze is active.
11. **TEST 11 — Approximate Timestamps**: Supports `APPROXIMATE`, `ORDER_ONLY`, and `DATE_ONLY` without fabricating hours.
12. **TEST 12 — Partial Information**: Operates effectively when only amount and UPI are known.
13. **TEST 13 — Duplicate Submission**: Deduplicates duplicate transaction submissions deterministically.
14. **TEST 14 — Evidence Integrity**: Preserves original artifacts with SHA-256 hashes and redaction state.
15. **TEST 15 — Case Package Accuracy**: Verifies non-accusatory language, clear fact/inference distinction, and disclaimers.
16. **TEST 16 — Non-Leakage Pre-Loss Evaluation**: Strict temporal isolation between pre-loss and post-loss evidence.
17. **TEST 17 — Campaign Feedback Candidate**: Extracted entities feed into campaign candidate clustering.
18. **TEST 18 — Privacy Controls**: Confirms no cross-victim data or unmasked accounts leak into case package.
19. **TEST 19 — Mobile Action Plan**: Validates that critical DO NOW lifeline actions are immediately accessible.
20. **TEST 20 — Degraded Mode Resilience**: Functions fully when graph or campaign engines are offline.
