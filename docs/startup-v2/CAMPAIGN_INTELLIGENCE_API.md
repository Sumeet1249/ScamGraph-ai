# Campaign Intelligence API & Outbreak Radar

## 1. Outbreak Radar Feed (`GET /api/v1/outbreak/feed`)

Provides streaming awareness of active fraud campaigns across India and global digital channels.

### Feed Item Schema
```json
[
  {
    "campaign_id": "cmp_digital_arrest_v2",
    "campaign_name": "CBI Digital Arrest Coercion Ring",
    "lifecycle": "ACTIVE",
    "activity_level": "OUTBREAK",
    "incident_count_bracket": "20+",
    "severity": "CRITICAL",
    "top_tactics": ["AUTHORITY_IMPERSONATION", "PAYMENT_PRESSURE", "ISOLATION"],
    "primary_channels": ["WHATSAPP", "SKYPE", "UPI"],
    "first_detected": "2026-10-18T10:00:00Z",
    "last_escalation": "2026-10-24T18:00:00Z"
  }
]
```

## 2. Customer Privacy Boundary
Victim identities, specific transaction amounts, and internal graph embeddings are strictly filtered prior to feed generation.
