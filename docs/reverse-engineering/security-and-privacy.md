# Security, Privacy & Abuse-Resistance Architecture

This document outlines the security, privacy-preserving cryptographic design, data protection controls, and abuse-mitigation mechanisms implemented in ScamGraph AI.

## 1. Privacy-Preserving Identifier Fingerprinting

### The Threat: Dictionary & Rainbow Table Enumeration
Identifiers in consumer payments—such as 10-digit Indian mobile numbers (`+91 9XXXXXXXXX`) or standard 11-16 digit bank account numbers—have very low entropy ($10^{10}$ combinations).
A simple unsalted or globally salted SHA-256 hash can be precomputed in hours on commodity GPU hardware, exposing innocent user phone numbers and transactions.

### ScamGraph Implementation: Keyed HMAC-SHA-256 with Versioning
1. **Canonical Normalization**:
   - Phone Numbers: Trim whitespace, remove non-digits, format with E.164 country code (`+919876543210`).
   - UPI VPAs: Lowercase, strip whitespace, normalize handle suffix (`merchant@oksbi`).
   - URLs/Domains: Lowercase host, strip tracking query parameters, normalize trailing slashes.
   - Bank Accounts: Format as `IFSC:ACCOUNT_NUMBER` (e.g., `SBIN0001234:987654321098`) without stripping necessary leading zeros.
2. **Type-Prefixed Payload**:
   ```
   message_to_hash = f"{identifier_type.upper()}:{canonical_value}"
   ```
3. **Keyed HMAC**:
   - Evaluated using `hmac.new(secret_key, message_to_hash, hashlib.sha256).hexdigest()`.
   - Fingerprint format: `hmac_{key_version}_{hash_hex}` (e.g., `hmac_v1_e3b0c442...`).
4. **Key Rotation Lifecycle**:
   - `ACTIVE_KEY_VERSION` is used for generating new screening and report fingerprints.
   - Secondary historical keys (e.g., `RETIRED_KEYS = ["v0"]`) are maintained in configuration to allow smooth dual-verification during rotation windows.

---

## 2. Data Minimization & PII Handling

1. **Redaction in Application Logs**:
   - Raw phone numbers, bank account numbers, and unmasked VPAs are masked before writing to log streams:
     `+919876543210` $\rightarrow$ `+9198****3210`.
2. **Encryption at Rest**:
   - When raw identifiers must be retained for operational compliance or evidence verification, they are stored encrypted with AES-256-GCM.
3. **Zero Raw PII in Graph Visualizations**:
   - Cytoscape and graph nodes display masked labels or pseudonymized entity tokens (`ent_phone_98...3210`, `acc_...4501`) rather than raw customer data.

---

## 3. Abuse Resistance & Registry Defense

1. **Anti-Enumeration Protections**:
   - Rate limiting on `POST /api/v1/registry/screen` (e.g., 60 requests/minute per caller).
   - Maximum batch query size bounded to 50 identifiers per request.
   - Generic response for unconfirmed reports to prevent attackers probing which of their burner accounts have been reported.
2. **Bounded Graph Traversals**:
   - Enforce `max_depth <= 5` and hard pagination (`limit <= 100`) on all path search queries to mitigate DoS via resource exhaustion.
3. **State Machine & Role Authorization**:
   - Only the reporting organization (`reporting_org`) or an authenticated system administrator may submit a `REVOCATION`.
   - Disputes require substantive justification and documented evidence before transitioning report state.

---

## 4. Immutable Audit Trails

Every state transition in the Smart Registry emits an immutable audit event:
```json
{
  "audit_id": "aud_018274ba",
  "timestamp": "2026-10-22T00:15:20Z",
  "entity_type": "REGISTRY_REPORT",
  "entity_id": "rep_9f82ab71",
  "action": "REVOCATION_SUBMITTED",
  "actor_org": "BANK_HDFC_01",
  "actor_user": "Compliance_Officer_CO_402",
  "previous_state": "CONFIRMED",
  "new_state": "REVOKED",
  "reason": "Customer demonstrated authorized corporate account delegation; false positive cleared.",
  "integrity_hash": "sha256_hash_of_audit_payload"
}
```
Audit records are append-only and cannot be updated or deleted by normal API callers.
