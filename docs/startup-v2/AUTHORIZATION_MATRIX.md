# Canonical Authorization Matrix (Prompt 21 / Phase 7A)

| Permission / Action | ANONYMOUS | CONSUMER | ORG_VIEWER | ORG_ANALYST | ORG_ADMIN | SCAMGRAPH_ANALYST | SENIOR_ANALYST | SCAMGRAPH_ADMIN | API_CLIENT |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `incident:read_own` | ❌ | ✅ (Own) | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| `incident:read_org` | ❌ | ❌ | ✅ (Org) | ✅ (Org) | ✅ (Org) | ❌ | ❌ | ✅ | ✅ (Scope) |
| `incident:review` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| `campaign:read` | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Scope) |
| `campaign:review` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| `entity:read` | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Scope) |
| `graph:read` | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `evidence:read_derived` | ❌ | ✅ (Own) | ✅ (Org) | ✅ (Org) | ✅ (Org) | ✅ | ✅ | ✅ | ❌ |
| `evidence:read_raw` | ❌ | ✅ (Own) | ❌ | ✅ (Org) | ✅ (Org) | ❌ (Redacted) | ✅ | ✅ | ❌ |
| `evidence:export` | ❌ | ❌ | ❌ | ❌ | ✅ (Org) | ❌ | ✅ | ✅ | ❌ |
| `case:read_own` | ❌ | ✅ (Own) | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| `case:read_org` | ❌ | ❌ | ✅ (Org) | ✅ (Org) | ✅ (Org) | ✅ | ✅ | ✅ | ❌ |
| `case:write` | ❌ | ❌ | ❌ | ✅ (Org) | ✅ (Org) | ✅ | ✅ | ✅ | ❌ |
| `review:write` | ❌ | ❌ | ❌ | ✅ (Org) | ✅ (Org) | ✅ | ✅ | ✅ | ❌ |
| `alert:read` | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `api_key:manage` | ❌ | ❌ | ❌ | ❌ | ✅ (Org) | ❌ | ❌ | ✅ | ❌ |
| `webhook:manage` | ❌ | ❌ | ❌ | ❌ | ✅ (Org) | ❌ | ❌ | ✅ | ✅ (Scope) |
| `organization:manage` | ❌ | ❌ | ❌ | ❌ | ✅ (Org) | ❌ | ❌ | ✅ | ❌ |
| `audit:read` | ❌ | ❌ | ❌ | ❌ | ✅ (Org) | ✅ | ✅ | ✅ | ❌ |
| `admin:system` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
