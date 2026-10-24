# Scam Check API & Pre-Payment Guard API

## 1. Scam Check API (`POST /api/v1/check`)

### Endpoint Overview
General-purpose multimodal analysis endpoint accepting suspicious message text, URLs, phone numbers, or VPAs. Evaluates content through language normalization, tactical classification, and cross-incident correlation.

### Request Contract
```json
{
  "message_text": "Sir verification complete karne ke liye abhi 5000 pay karo warna account block ho jayega.",
  "vpa": "fake.task@oksbi",
  "url": "https://secure-kyc-update.me/login",
  "external_reference": "TXN_CHECK_88921",
  "environment": "LIVE"
}
```

### Response Contract (Customer-Safe DTO)
```json
{
  "check_id": "chk_987654321",
  "request_id": "req_123456789",
  "risk_level": "HIGH",
  "risk_score": 88,
  "confidence": "HIGH",
  "urgency": "CRITICAL",
  "recommended_action": "PAUSE_BEFORE_PAYMENT",
  "reason_codes": ["PAYMENT_PRESSURE", "IMPERSONATION_OFFICIAL", "KNOWN_HIGH_RISK_VPA"],
  "journey_summary": {
    "current_stage": "CREDENTIAL_HARVESTING",
    "monetization_status": "PAYMENT_REQUESTED"
  },
  "network_signal": "ENTITY_REPORTED_ELSEWHERE",
  "campaign_signal": "DIGITAL_ARREST_CAMPAIGN_V2",
  "processing_ms": 142,
  "environment": "LIVE"
}
```

---

## 2. Pre-Payment Guard API (`POST /api/v1/guard/check`)

### Strategically Targeted For:
UPI Apps (GPay, PhonePe, Paytm, BHIM), Banking Portals, Payment Gateways, and Fintech Wallets.

### Fast-Path SLA & Non-Execution Contract
- **Fast-Path Latency Target**: <25ms
- **Deterministic Interventions**: Utilizes canonical Prompt 14 intervention categories:
  - `ALLOW_NORMAL_FLOW` (Friction: 0)
  - `SHOW_CAUTION` (Friction: 2)
  - `VERIFY_INDEPENDENTLY` (Friction: 3)
  - `PAUSE_BEFORE_PAYMENT` (Friction: 4)
  - `STRONG_WARNING` (Friction: 5)
  - `ESCALATE_REVIEW` (Friction: 6)
- **Zero Payment Execution**: ScamGraph provides intelligence and friction recommendations; the partner application retains total custody of payment authorization.
