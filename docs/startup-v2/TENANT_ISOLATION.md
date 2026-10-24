# Multi-Tenant Isolation Architecture (Prompt 21 / Phase 7A)

## 1. Zero Cross-Tenant Leakage Guarantee

ScamGraph enterprise architecture strictly isolates customer data:
- **Repository Scoping**: Queries enforce tenant boundaries directly at data-access time: `SELECT * FROM incidents WHERE id = ? AND org_id = ?`.
- **Cross-Tenant Attack Resistance**: Organization A cannot read or mutate Organization B's:
  - Incidents and analysis evaluations
  - Uploaded artifacts and media files
  - Asynchronous multimodal jobs
  - Generated export archives
  - API credentials and webhook configurations
  - Private analyst notes and internal case tickets

---

## 2. Global Intelligence vs. Private Tenant Isolation

```
Tenant A Private Evidence
          │
          ├── PRIVATE_ONLY ───────────────X Blocked from Global Graph
          │
          └── NETWORK_INTELLIGENCE_ALLOWED
                     │
               Privacy Transform (Strip PII & Tenant Attribution)
                     │
               Derived Evidence Signal (VPA / Phone / Host Domain)
                     │
          Global Scam Intelligence (Graph & Campaigns)
                     │
             Threshold Filtering (Minimum 3 reports)
                     │
             Tenant B Safe Intelligence ("Observed in multiple reports")
```

- **Rule 68**: Customer API traffic is **NEVER** automatically used for AI model training.
- **Rule 69**: Global network contribution requires explicit `NETWORK_INTELLIGENCE_ALLOWED` policy.
