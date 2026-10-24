# Webhook Architecture & Event Delivery (Prompt 20)

## 1. Webhook Signing & HMAC-SHA256 Header Contract

ScamGraph delivers cryptographically signed webhooks to protect subscribers against spoofing and tampering.
Each webhook HTTP POST request includes the `X-ScamGraph-Signature` header:

```
X-ScamGraph-Signature: t=1730000000,v1=9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
```

### Signature Verification Algorithm
1. Extract timestamp `t` and signature `v1` from the header.
2. Form the signature payload: `{t}.{raw_request_body_bytes}`.
3. Compute HMAC-SHA256 using the organization's webhook secret `whsec_...`.
4. Validate using constant-time string comparison (`hmac.compare_digest`).
5. **Replay Defense**: Reject any request where `abs(current_time - t) > 300` seconds (5-minute tolerance).

---

## 2. Event Types & Payloads

Supported Events:
- `high_risk.detected`: Emitted when an enterprise check or guard assessment yields risk $\ge 80$.
- `campaign.emerging`: Emitted when an unclassified campaign cluster gains 5+ correlated incidents in 2 hours.
- `campaign.outbreak`: Emitted when outbreak velocity spikes $\ge 3\times$ standard deviation.
- `campaign.resurging`: Emitted when dormant infrastructure reactivates.
- `entity.network_signal_changed`: Emitted when an entity transitions to `SUSPICIOUS` or `HIGH_RISK_MULE`.
- `analysis.completed`: Emitted upon asynchronous multimodal job completion.
- `analysis.failed`: Emitted on processing error.

### Delivery Lifecycle
- Delivery status tracking: `PENDING` $\to$ `DELIVERED` $\to$ `RETRYING` $\to$ `FAILED`.
- Exponential backoff with jitter up to 5 attempts.
- Idempotency: Subscribers deduplicate delivery attempts using `event_id`.
