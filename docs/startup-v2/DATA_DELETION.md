# Data Deletion, Retention & Export Security (Prompt 21 / Phase 7A)

## 1. Evidence Deletion & Dependent Intelligence Invalidation

When a piece of evidence or an incident is deleted:
- **Zero Phantom Claims**: Deletion must not leave unsupported graph edges, entity flags, or campaign memberships active.
- **Cascade Trigger**:
  1. Evidence asset is deleted from storage.
  2. Entity relationships referencing this evidence are updated; edges with zero remaining corroborating evidence are pruned from the Knowledge Graph.
  3. Incident correlations referencing this evidence have their confidence re-evaluated.
  4. Entity dispute reversals trigger reputation resets from `HIGH_RISK_MULE` to `VERIFIED_LEGITIMATE`.
  5. Audit trail records `EVIDENCE_DELETED` with count of invalidated edges.

---

## 2. Export Security & CSV Formula Injection Protection
- **Controlled Job**: Large exports operate through `ExportJob` with a 15-minute expiring download token.
- **Spreadsheet Formula Sanitization**: Any exported cell value starting with `=`, `+`, `-`, `@`, `\t`, or `\r` is prepended with a single quote (`'`), neutralizing DDE and macro injection attacks in Excel and Google Sheets.
- **Full Auditability**: Every export creation and download records an immutable `AuditEvent`.
