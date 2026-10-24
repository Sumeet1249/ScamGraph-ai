# Enterprise Data Contribution Policy

## 1. Zero Automatic Training Consent
> **Rule 68: CUSTOMER DATA != TRAINING DATA**
> Customer API traffic submitted to `/api/v1/check` and `/api/v1/guard/check` is NEVER automatically ingested into model training sets.

## 2. Contribution Policy Modes
Organizations configure their data sharing tier:
1. `PRIVATE_ONLY`:
   - Incident data is used exclusively to answer the active request.
   - Zero graph linkages are written. Zero network reputation contribution.
2. `AGGREGATE_ALLOWED`:
   - Anonymized token counts contribute to global statistical velocity and regional trend radar.
3. `NETWORK_INTELLIGENCE_ALLOWED` (Recommended for Banks):
   - Malicious infrastructure indicators (domain, VPA, phone) are contributed as privacy-safe graph nodes with source attribution stripped.
   - Allows reciprocal defense: bank benefits from fraud detected by telecom and fintech partners.
4. `TRAINING_OPT_IN`:
   - Requires explicit contractual authorization.
