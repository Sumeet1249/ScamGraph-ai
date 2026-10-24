# Network Intelligence API Contract

## Route: `POST /api/v1/network/check`

### Request
```json
{
  "entity_value": "fake.cbi.hq@oksbi",
  "entity_type": "UPI_VPA"
}
```

### Response
```json
{
  "network_signal": "ENTITY_REPORTED_ELSEWHERE",
  "connected_campaign_count": 2,
  "corroboration_bracket": "6-20",
  "shares_infrastructure_with": ["domain:fake-cbi-auth.in"],
  "confidence": 0.85
}
```
- No criminal attribution: only structural graph infrastructure links are exposed.
