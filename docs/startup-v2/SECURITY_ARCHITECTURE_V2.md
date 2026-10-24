# Security Architecture V2 (Prompt 21 / Phase 7A)

## 1. Executive Summary

ScamGraph AI enforces enforceable security at every application layer. Security is **never** purely cosmetic UI hiding or standalone middleware.

### Core Architecture Axioms
1. **EVERY REQUEST HAS AN IDENTITY**: Every operation is bound to a validated `PrincipalContext`.
2. **EVERY RESOURCE HAS AN OWNER / SECURITY BOUNDARY**: Consumers own their incidents; enterprise tenants own their jobs, keys, and private evaluations.
3. **EVERY SENSITIVE ACTION HAS AN AUTHORIZATION DECISION**: Centralized RBAC and resource-level checks prevent Insecure Direct Object References (IDOR).
4. **EVERY IMPORTANT MUTATION HAS AN AUDIT TRAIL**: Immutable audit logging records identity, action, resource, result, and timestamp.
5. **EVERY PIECE OF SENSITIVE EVIDENCE HAS A LIFECYCLE**: Raw media is separated from derived indicators; evidence deletion cascade-invalidates dependent graph claims.

```
                         REQUEST
                            │
                    AUTHENTICATION
           (PBKDF2 Password / Session Cookie / API Key)
                            │
                     PrincipalContext
                            │
                     Tenant Resolution
                     (owner_id / org_id)
                            │
                      AUTHORIZATION
              (Centralized RBAC + IDOR Checks)
                            │
                 ┌──────────┴──────────┐
                 │                     │
            Service Layer         Audit Decision
                 │
          Tenant-Aware Repository
                 │
             DATA / EVIDENCE
          (Derived vs Raw Media)
                 │
            Privacy Policy
       (PRIVATE_ONLY / NETWORK_ALLOWED)
                 │
        Customer-Safe Serializer
```

---

## 2. Four Separated Data Planes

1. **CONSUMER PRIVATE DATA**:
   - Victims' incident narratives, uploaded screenshots, loss reports, Rescue emergency action plans.
   - Strictly isolated by `owner_id == principal.user_id`.
2. **ENTERPRISE TENANT-PRIVATE DATA**:
   - Pre-Payment Guard requests, transaction references, partner API keys, webhook signing secrets.
   - Strictly isolated by `org_id == principal.organization_id`.
3. **SCAMGRAPH RESTRICTED ANALYST DATA**:
   - Review queue, campaign clustering decisions, investigation case packages, threat telemetry.
   - Enforced by `SCAMGRAPH_ANALYST` and `SCAMGRAPH_SENIOR_ANALYST` least-privilege roles.
4. **PRIVACY-SAFE GLOBAL SCAM INTELLIGENCE**:
   - Knowledge Graph structural linkages, aggregated campaign velocity, Outbreak Radar blips.
   - Strips victim identities, suppresses small cohorts (<3 reports bucketed as `1-5`), and strictly obeys enterprise data contribution policies.
