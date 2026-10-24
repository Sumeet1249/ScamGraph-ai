# Audit Logging, Security Logging & Secret Management (Prompt 21 / Phase 7A)

## 1. Immutable Audit Logging
The `AuditEvent` ledger tracks all security-sensitive operations across ScamGraph:
- `LOGIN`, `LOGOUT`, `LOGIN_FAILURE`
- `ROLE_CHANGED`, `MEMBER_ADDED`, `MEMBER_REMOVED`
- `API_KEY_CREATED`, `API_KEY_REVOKED`
- `EVIDENCE_VIEWED`, `EVIDENCE_DOWNLOADED`, `EVIDENCE_DELETED`
- `EXPORT_REQUESTED`, `EXPORT_DOWNLOADED`
- `REVIEW_DECISION`, `ENTITY_MERGE`, `ENTITY_SPLIT`
- `PRIVACY_SETTING_CHANGED`, `ADMIN_ACTION`

### Automatic Secret Redaction
The audit service automatically scrubs values associated with `password`, `secret`, `token`, `api_key`, `cookie`, and `auth` from audit details, preserving only safe diagnostic tags like `key_prefix`.

---

## 2. Secret Management
- **Zero Raw Secrets**: API keys, webhook signing tokens, and passwords are never persisted in plaintext.
- **Environment Isolation**: Secrets are loaded exclusively from `.env` or cloud secret managers via `pydantic-settings`.
- **Constant-Time Comparison**: Cryptographic comparisons use `secrets.compare_digest` or `hmac.compare_digest` to prevent timing attacks.
