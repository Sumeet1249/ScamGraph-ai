# Centralized RBAC & Resource-Level Authorization (Prompt 21)

## 1. Role-Based Access Control Architecture

ScamGraph eliminates scattered role conditionals (e.g. `if user.role == "admin"`) by routing all access decisions through the centralized `SecurityService.authorize(principal, permission, resource)`.

### Canonical Role Taxonomy
1. `CONSUMER`: Access own incidents, own Rescue cases, own evidence.
2. `ORG_VIEWER`: Read-only access to organization incidents, cases, and global intelligence.
3. `ORG_ANALYST`: Manage organization cases, write review decisions, read org-scoped raw evidence.
4. `ORG_ADMIN`: Manage organization members, rotate API keys, configure webhooks, export evidence, view audit trail.
5. `SCAMGRAPH_ANALYST`: Review syndicate clusters, investigate cross-incident campaigns, access derived indicators.
6. `SCAMGRAPH_SENIOR_ANALYST`: Full investigative authority including cross-tenant raw media and forensic export.
7. `SCAMGRAPH_ADMIN`: Full administrative control, system configuration, master audit access.

---

## 2. Resource-Level IDOR Protection

RBAC permissions are insufficient without resource ownership binding:
- **Consumer Ownership**: If a resource specifies `owner_id`, it must match `principal.user_id` unless the caller is a ScamGraph analyst.
- **Tenant Boundary**: If a resource specifies `org_id`, it must match `principal.organization_id`. Even an Org Admin cannot cross tenant boundaries.
- **Raw Media Gate**: Accessing original screenshots or audio requires both `EVIDENCE_READ_RAW` permission AND ownership/senior analyst authorization.
