# API Sandbox Isolation Specification

## 1. Zero-Contamination Sandbox Contract

The ScamGraph Sandbox (`environment="SANDBOX"` or `sg_test_...` key) allows enterprise engineering teams to integrate and load test without polluting real-world scam intelligence.

### Deterministic Test Fixtures:
1. **Digital Arrest Coercion**:
   - Input: `"CBI officer demands ₹50,000 security deposit"`
   - Output: Risk 85 (HIGH), Action: `PAUSE_BEFORE_PAYMENT`, Signal: `SYNTHETIC_SANDBOX_FIXTURE`
2. **Task / Part-Time Job Scam**:
   - Input: `"Telegram VIP task verification pay 5000"`
   - Output: Risk 85 (HIGH), Action: `PAUSE_BEFORE_PAYMENT`, Signal: `SYNTHETIC_SANDBOX_FIXTURE`
3. **Legitimate Merchant Baseline**:
   - Input: `"Grocery supermarket payment 340"`
   - Output: Risk 12 (LOW), Action: `ALLOW_NORMAL_FLOW`
4. **Insufficient Context**:
   - Input: `""` (Empty message)
   - Output: Risk 0, Level: `INSUFFICIENT_EVIDENCE`

### Isolation Guarantee:
Sandbox incidents are **NEVER** inserted into production Neo4j graphs, never increment entity observation counters, and never trigger public outbreak radar alerts.
