# Post-Loss Timeline & Incident Reconstruction (Phase 5B)

## Reconstruction Philosophy
Victims under severe stress rarely remember every transaction timestamp or interaction detail in chronological order. The `IncidentReconstructionService` provides:
1. **Progressive Questioning**: Minimal required entry followed by incremental detail expansion.
2. **Multiple Payment Tracking**: Sequential transfer aggregation (e.g., ₹500 task deposit → ₹5,000 upgrade → ₹20,000 withdrawal unlock fee).
3. **Deduplication Engine**: Uses cryptographic hashing of `(incident_id, amount, currency, UTR, recipient)` to prevent double-counting payments.
4. **Time Granularity Support**:
   - `EXACT`: Full ISO timestamp from bank SMS or receipt.
   - `APPROXIMATE`: Estimated time of day.
   - `DATE_ONLY`: Calendar date known, exact hour forgotten.
   - `ORDER_ONLY`: Sequence known, exact date forgotten.
   - `UNKNOWN`: Timestamp unrecorded.

---

## Canonical Journey Integration
Rescue timeline events map directly to ScamGraph Journey Engine stages:

```
[SCAM_CONTACT]              --> JourneyStage.CONTACT
[PLATFORM_MOVE]             --> JourneyStage.PLATFORM_MIGRATION
[PAYMENT_REQUEST]           --> JourneyStage.INITIAL_PAYMENT
[PAYMENT_SENT (First)]      --> JourneyStage.INITIAL_PAYMENT
[PAYMENT_SENT (Subsequent)] --> JourneyStage.PAYMENT_ESCALATION
[LOSS_DISCOVERED]           --> JourneyStage.WITHDRAWAL_BLOCK
[ADDITIONAL_DEMAND]         --> JourneyStage.PAYMENT_ESCALATION / RECOVERY_FEE
[RECOVERY_SCAM_CONTACT]     --> JourneyStage.RECOVERY_FEE
```
