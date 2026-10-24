# API Versioning Policy (Phase 6B)

## 1. Versioning Contract

ScamGraph Enterprise exposes public endpoints under immutable version prefixes:
- Current Active: `/api/v1/...`
- Experimental / Internal: `/api/internal/...`

### Breaking vs. Non-Breaking Evolution
1. **Non-Breaking Changes (Allowed within `/api/v1/`)**:
   - Adding new optional request fields
   - Adding new response attributes (e.g. additional diagnostic metadata)
   - Improving internal model calibration and detection accuracy
   - Adding new webhook event types
2. **Breaking Changes (Requires new major prefix `/api/v2/`)**:
   - Removing or renaming existing fields
   - Altering response type signatures
   - Modifying HTTP status codes for existing failure conditions
   - Changing webhook signing algorithms

### Internal Model Versioning vs. Public API Version
> **Rule 6: ENGINE VERSION != API VERSION**
> The public API remains `/api/v1/check` regardless of whether the backend executes Journey Engine V1, ScamDNA V3, or Campaign Intelligence V2. The API DTO encapsulates and stabilizes engine upgrades so enterprise partners do not suffer breaking SDK shifts upon model updates.
