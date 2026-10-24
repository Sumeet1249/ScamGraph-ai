# Security Pre-Implementation Audit (Prompt 21 / Phase 7A)

## 1. Executive Summary

This security audit inspects the executable state of ScamGraph AI following Prompt 20 (Enterprise API & SDK Platform V2) and prior to establishing the company-grade identity, RBAC, tenant isolation, privacy governance, and evidence security architecture.

---

## 2. Inventory & Classification Matrix

| Security Subsystem | Current State in Repository | Classification | Target in Phase 7A |
|:---|:---|:---|:---|
| **Frontend Authentication** | Consumer interface runs without active identity session; local state only. | **MISSING** | Centralized session management with consumer token/cookie authentication. |
| **Backend Authentication** | Enterprise API keys (`sg_live_...` / `sg_test_...`) hashed with SHA-256. Consumer endpoints unauthenticated. | **PARTIAL** | Unified `PrincipalContext` resolving Human (Consumer, Org User, Analyst, Admin) and Machine (API Client, Service Account). |
| **Sessions & Cookies** | No server-side session store; no HttpOnly cookie rotation. | **MISSING** | Secure session manager with expiration, fixation rotation, and revocation. |
| **Enterprise Organizations** | `EnterpriseOrganization` and `ApiKeyRecord` schemas exist; organization boundary checked in API endpoints. | **PARTIAL** | Hardened `Organization` + `OrganizationMembership` with multi-org support and RBAC. |
| **User Model** | No persistent User class; user feedback models exist in review queue. | **MISSING** | Canonical `User` entity with adaptive password hashing (PBKDF2/SHA-256), email verification, and status. |
| **Database Ownership** | In-memory incident repo and Neo4j nodes lack strict `tenant_id` / `owner_id` indexing. | **PARTIAL** | Explicit `owner_id` (consumer) and `organization_id` (tenant) on every incident, artifact, job, and case. |
| **Evidence & Artifact Storage** | Artifact schema has `privacy_classification` enum, but no backend authorization enforcement on binary media. | **PARTIAL** | Enforceable sensitivity classes (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `HIGHLY_SENSITIVE`, `RESTRICTED`), separate derived vs raw media permissions. |
| **Exports & Reports** | Direct generation in Rescue without job tokens or CSV formula injection defense. | **HIGH_RISK** | Controlled `ExportJob` with short-lived tokens, formula injection defense (`=`, `+`, `-`, `@`), and full audit logging. |
| **Admin & Analyst Routes** | `/api/v1/console/*` accessible without role enforcement; `/api/v1/registry` open to local calls. | **HIGH_RISK** | Centralized `AuthorizationService` enforcing `SCAMGRAPH_ANALYST`, `SCAMGRAPH_ADMIN`, and least privilege. |
| **CORS & Security Headers** | Permissive origins `["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"]`; basic headers only. | **PARTIAL** | Hardened CORS with environment origin binding; CSP, X-Content-Type-Options, Referrer-Policy, HSTS middleware. |
| **CSRF Defense** | No CSRF tokens on state-mutating browser requests. | **MISSING** | SameSite cookie policy and CSRF protection for cookie-authenticated browser sessions. |
| **Rate Limiting** | Contract documented in Prompt 20; in-memory throttling foundation. | **PARTIAL** | Multi-dimensional rate limit enforcement (IP, principal, organization, API key, auth abuse throttle). |
| **Secret Management** | API secrets hashed with SHA-256; secrets displayed once. Settings load from `.env`. | **SECURE** | Preserve zero-raw-secret policy; ensure no hardcoded secrets in source or logs. |
| **Audit Logging** | Domain events emitted; no dedicated immutable security audit log. | **MISSING** | Centralized `AuditEvent` store tracking auth, role changes, evidence access, exports, and administrative actions. |
| **Log Redaction** | Basic logger formatting; secrets could leak if logged directly. | **PARTIAL** | Centralized log redaction filter stripping tokens, keys, passwords, and sensitive evidence. |
| **Consent Management** | No formal consent ledger distinguishing analysis from training. | **MISSING** | Canonical `ConsentRecord` tracking purpose-specific consent (analysis vs model training vs storage). |
| **Data Retention & Deletion** | No automated expiration; deletion does not invalidate dependent graph edges. | **HIGH_RISK** | Configurable retention policies; cascade invalidation of derived graph/ScamDNA/campaign claims upon evidence deletion. |
| **Cross-Victim Privacy** | Masking in Entity intelligence; small cohort protection threshold. | **SECURE** | Preserve and enforce response minimization across all enterprise and consumer endpoints. |
| **Sandbox Isolation** | Synthetic fixture deterministic responses; zero production graph mutation. | **SECURE** | Strict separation between test/sandbox credentials and production intelligence. |

---

## 3. High-Risk Findings Requiring Immediate Hardening

1. **Unprotected Analyst & Console Endpoints**: `/api/v1/console/summary`, `/alerts`, and `/reviews` can be invoked without verifying analyst identity.
2. **Missing IDOR Defense**: An authenticated user could potentially probe `/incidents/{id}` or `/artifacts/{id}` belonging to another consumer or organization without explicit ownership checks.
3. **CSV Formula Injection**: Exported spreadsheets containing hostile scam text (e.g. `=cmd|' /C calc'!A0` or `=HYPERLINK(...)`) could execute if unescaped.
4. **Phantom Claims Post-Deletion**: If an incident or evidence item is deleted, the Knowledge Graph and Campaign Correlation must not retain ghost edges supporting unsubstantiated scam attributions.
