# Authentication & Session Security (Prompt 21 / Phase 7A)

## 1. Canonical Identity Model

Every incoming request resolves to an immutable `PrincipalContext`:
- **Human Principals**: `CONSUMER_USER`, `ENTERPRISE_USER`, `SCAMGRAPH_ANALYST`, `SCAMGRAPH_ADMIN`. Authenticated via session tokens or Bearer credentials.
- **Machine Principals**: `API_CLIENT`, `SERVICE_ACCOUNT`. Authenticated via SHA-256 hashed API keys (`sg_live_...`, `sg_test_...`).
- **Anonymous Fallback**: `ANONYMOUS`. Supported intentionally for zero-friction scam checks in ScamGraph Protect. Anonymous principals cannot access history, private evidence, or other tenants' data.

---

## 2. Password Security & PBKDF2 Adaptive Hashing
- **Algorithm**: PBKDF2-HMAC-SHA256 with 100,000 iterations.
- **Salting**: 16-byte cryptographically random salt per user record.
- **Zero Raw Storage**: Passwords are never stored in plaintext, reversible formats, or log entries.
- **Brute-Force Throttling**: 5 consecutive failed login attempts within 5 minutes trigger a temporary 5-minute lockout without permanent account freezing (preventing DoS).

---

## 3. Browser Session Management
- **Token Security**: Tokens are generated using high-entropy random bytes (`secrets.token_urlsafe(32)`).
- **Secure Cookie**: `Set-Cookie: scamgraph_session=<token>; HttpOnly; SameSite=Lax; Max-Age=86400`.
- **Fixation & Revocation**: Session identifiers are rotated upon login and immediately invalidated upon logout or account suspension.
