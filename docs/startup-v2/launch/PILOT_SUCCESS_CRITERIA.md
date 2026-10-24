# PILOT SUCCESS CRITERIA & STOP CONDITIONS
**ScamGraph AI — Phase 7F Launch Criteria**
*Document Version: 5.0.0 | Date: 2026-10-24*

---

## 1. Pilot Success Criteria (Defined Pre-Launch)

| Criterion | Target Metric | Minimum Acceptance Floor | Measurement Method |
| :--- | :--- | :--- | :--- |
| **Protect Assessment Comprehension** | $\ge 90\%$ | $85\%$ | Post-check neutral comprehension query |
| **Guard Payment Pause Rate** | $\ge 75\%$ | $65\%$ | User-reported payment outcome event |
| **Rescue Actionable Understanding** | $\ge 90\%$ | $80\%$ | Dial-1930 / bank freezing step completion |
| **False-Alarm (FP) Rate on Benign**| $\le 3.0\%$ | $\le 5.0\%$ | Golden benchmark & reported feedback |
| **Protect Response Latency (p95)**| $\le 250\text{ ms}$ | $\le 400\text{ ms}$ | Production Prometheus metrics |
| **Zero Security / Tenant Leakage** | 0 events | 0 events | Security audit logs & tenant tests |

---

## 2. Mandatory Pilot Stop Conditions

The pilot must be immediately paused or rolled back to safe mode upon any of the following:
1. **Cross-Tenant Data Exposure**: Any incident, evidence, or cache key belonging to Tenant A becomes visible to Tenant B.
2. **Critical Safety Misguidance**: Any high-risk coercive scam (e.g. digital arrest or OTP theft) incorrectly classified as verified safe.
3. **Emergency Resource Corruption**: Rescue failing to provide the exact official 1930 helpline number or official cybercrime reporting URL.
4. **Catastrophic Infrastructure Failure**: Database corruption, unrecoverable data loss, or cascading provider retry storms.
