# Threat Model V2 (ScamGraph AI Security Architecture)

## 1. Protected Assets & Critical Sensitivity Tiers

1. **Consumer Identity & Data**:
   - Victims' real names, primary phone numbers, emails, home addresses.
   - Private incident narratives, loss amounts, police complaint numbers.
2. **Enterprise Confidentiality**:
   - Organization tenant boundaries, customer transaction references, internal fraud tickets.
   - Unreleased partner API keys (`sg_live_...`, `sg_test_...`) and webhook signing secrets (`whsec_...`).
3. **Sensitive Digital Evidence**:
   - Raw victim screenshots (chat logs, bank balances, Aadhaar/PAN cards).
   - Audio call recordings, voicemails, and high-fidelity transcripts.
   - Banking tokens, UPI VPAs, IFSCs, and destination accounts.
4. **Proprietary Intelligence & Integrity**:
   - Knowledge Graph topological edges and cross-incident correlation links.
   - Campaign syndicate clusters and outbreak detection velocity models.
   - ScamDNA proprietary behavioral gene definitions and weight matrices.
   - Analyst notes, internal case hypotheses, and law-enforcement packages.

---

## 2. Threat Actors & Attack Vectors

| Threat Actor | Capabilities & Motivation | Primary Attack Vectors | Countermeasures |
|:---|:---|:---|:---|
| **Unauthenticated External Attacker** | High-volume automated requests, internet access. | Enumeration of entity reputation, credential stuffing, SSRF probe via URL analysis, API abuse. | Strict rate limits, anti-enumeration buckets, SSRF IP/scheme filters, anonymous data isolation. |
| **Malicious / Compromised Consumer** | Valid account credentials. | Insecure Direct Object References (IDOR) to view others' incidents/evidence, prompt injection in chat inputs, fake scam reports. | Resource ownership checks (`owner_id == principal.user_id`), data sanitization, sybil-resistant reputation weighting. |
| **Cross-Tenant Competitor / Attacker** | Valid enterprise API credential (`org_A`). | Querying `org_B`'s jobs, artifacts, webhooks, or private incident evaluations. | Strict tenant boundary enforcement at repository/query level (`org_id == principal.organization_id`). |
| **Scammer Syndicate (Intelligence Poisoner)** | Coordinated fraudulent accounts. | Submitting synthetic fake reports to falsely flag legitimate competitor VPAs/domains or dilute syndicate outbreak velocity. | Independent evidence corroboration, multi-tenant diversity threshold, reputation dispute lifecycle. |
| **Compromised Analyst / Insider Threat** | Analyst console credentials. | Bulk scraping raw victim media (screenshots/recordings) or leaking campaign intelligence. | Least-privilege RBAC: separation of derived signals vs raw media permissions; full immutable audit logging of media downloads. |
| **Hostile Evidence Payload** | Untrusted user-submitted files. | Stored XSS via scam message text, CSV spreadsheet formula injection (`=HYPERLINK`), zip bombs, polyglot file uploads. | Text context encoding, CSV formula sanitization (`'` prefix), file magic byte verification, strict upload size limits. |

---

## 3. Explicit Security Boundaries

```
[ UNTRUSTED INTERNET ]
         │
    (API Gateway / Auth Middleware)
         │
┌────────▼──────────────────────────────────────────────────────────────┐
│ 1. PUBLIC ZONE: Anonymous checks, health probes, documentation.       │
└────────┬──────────────────────────────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────────────────────────────┐
│ 2. CONSUMER PRIVATE PLANE: Own incidents, own Rescue cases, own files. │
└────────┬──────────────────────────────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────────────────────────────┐
│ 3. ENTERPRISE TENANT PLANE: Org-scoped checks, guard, jobs, webhooks. │
└────────┬──────────────────────────────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────────────────────────────┐
│ 4. ANALYST RESTRICTED ZONE: Review queue, cases, campaign explorer.   │
└────────┬──────────────────────────────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────────────────────────────┐
│ 5. GLOBAL DERIVED INTELLIGENCE: Privacy-safe cross-tenant radar/graph.│
└───────────────────────────────────────────────────────────────────────┘
```
