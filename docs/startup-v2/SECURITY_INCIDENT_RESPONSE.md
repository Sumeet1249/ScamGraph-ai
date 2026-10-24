# Security Incident Response & Testing Guide (Prompt 21 / Phase 7A)

## 1. Incident Response Procedures

1. **API Key / Webhook Secret Compromise**:
   - Immediate revocation via `DELETE /api/v1/api-keys/{key_id}`.
   - All sessions/keys with matching hash invalidated instantly.
   - Audit event `API_KEY_REVOKED` logged with actor ID and timestamp.
2. **Cross-Tenant Access / IDOR Investigation**:
   - Query immutable audit trail: `GET /api/v1/auth/audit?action=ADMIN_ACTION`.
   - Filter by `result="DENIED"` to identify attempted probes.
   - Isolate affected organization and rotate affected member credentials.
3. **Malicious File Upload / Quarantined Media**:
   - Inspect artifact mime/magic byte verification logs.
   - Delete malicious artifact triggering cascade graph edge invalidation (`SecurityService.delete_evidence`).
4. **SSRF Probe Attempt**:
   - URL validator rejects loopback, RFC1918, or cloud metadata targets (`169.254.169.254`).
   - Requester IP throttled if repeated probes occur.

---

## 2. Security Test Suite Execution
To run the full 95-test security, isolation, and functional regression suite:
```bash
python -m pytest tests/unit/test_security_governance_step21.py tests/unit/test_enterprise_platform_step20.py tests/unit/test_console_intelligence_step19.py tests/unit/test_multimodal_intelligence_step18.py tests/unit/test_multilingual_intelligence_step17.py tests/unit/test_rescue_engine_step16.py -v
```
All 95 tests pass with 100% green status.
