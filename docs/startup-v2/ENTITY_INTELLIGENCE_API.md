# Entity & Network Intelligence API Specifications

## 1. Entity Intelligence API Contract

### Route: `POST /api/v1/entities/check`

```json
{
  "entity_type": "UPI_VPA",
  "value": "fake.cbi.hq@oksbi"
}
```

### Response
```json
{
  "entity_type": "UPI_VPA",
  "normalized_value": "fake.cbi.hq@oksbi",
  "verification_state": "SUSPICIOUS",
  "network_reputation": "HIGH_RISK_MULE",
  "incident_count_bracket": "6-20",
  "confidence": 0.88,
  "first_seen": "2026-10-15T08:12:00Z",
  "last_seen": "2026-10-24T18:30:00Z"
}
```

## 2. Privacy-Safe Guarantees
- Raw victim names, phone numbers, and chat logs are NEVER exposed.
- Anti-enumeration protection ensures automated scrapers cannot brute-force bank account or phone directories.
- Small cohorts (<3 reports) are bucketed as `1-5` to prevent targeted deanonymization.
