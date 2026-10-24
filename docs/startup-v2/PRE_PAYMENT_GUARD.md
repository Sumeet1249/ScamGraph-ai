# SCAMGRAPH AI — PRE-PAYMENT GUARD SPECIFICATION (PHASE 4B)
## "Know the Scam Before You Pay" — Real-Time Transaction Pre-Loss Shield

### 1. Product Positioning

ScamGraph Guard is **not** a generic transaction-fraud or chargeback engine.
- Bank risk models ask: *"Is this transaction anomalous compared to past spending patterns?"*
- ScamGraph Guard asks: *"Does this payment represent the monetization stage of an ongoing psychological manipulation journey?"*

---

### 2. The PrePaymentContext Model

Captures contextual intelligence preceding a fund transfer without collecting sensitive banking secrets (PIN, password, CVV):

| Attribute | Type | Description |
|---|---|---|
| `incident_id` | `str` | Associated incident or session token. |
| `payment_intent` | `bool` | True if the user is currently on a checkout/transfer screen. |
| `payment_reason` | `PaymentReason` | Stated category: `JOB_OR_TASK`, `INVESTMENT`, `RENT`, `BILL`, `GOVERNMENT_OR_FINE`, `REFUND_OR_SUPPORT`, etc. |
| `amount_inr` | `Optional[float]` | Transfer value (INR). |
| `amount_band` | `Optional[str]` | `MICRO (<500)`, `LOW (500-2k)`, `MID (2k-10k)`, `HIGH (>10k)`. |
| `recipient_vpa` | `Optional[str]` | Destination UPI Virtual Payment Address. |
| `journey_stage` | `str` | Current journey progression stage (`PAYMENT_REQUEST`, `PAYMENT_INTENT`). |
| `payment_proximity` | `PaymentProximity` | `NONE`, `DISTANT`, `APPROACHING`, `IMMINENT`, `REQUESTED`. |
| `tactics_present` | `List[str]` | Active psychological coercion tactics. |
| `is_campaign_outbreak` | `bool` | True if matching an active circulating outbreak. |

---

### 3. "Why Are You Paying?" Decision Logic

Before executing a transfer to an unverified recipient under elevated risk, Guard evaluates the combination of Stated Reason + Journey Progression:

1. **Job / Task Deposit**:
   - Stated reason: `JOB_OR_TASK`.
   - Journey evidence: Small reward received earlier $\to$ larger deposit requested.
   - Guard Decision: **Impose 120-minute cooling-off window (`DELAY_PAYMENT`)**.

2. **Digital Arrest Fine / Clearance**:
   - Stated reason: `GOVERNMENT_OR_FINE`.
   - Journey evidence: Police/CBI claims + secrecy/isolation.
   - Guard Decision: **Block transfer intent + trigger `TALK_TO_TRUSTED_PERSON`**.

3. **Routine Rent / Family Transfer (Hard Negative)**:
   - Stated reason: `RENT` or `FAMILY_OR_FRIEND`.
   - Journey evidence: Zero manipulation tactics, risk $< 0.35$.
   - Guard Decision: **Allow transfer without disruption (`NO_ACTION`)**.

---

### 4. API Endpoint Contract

```http
POST /api/v1/payment-guard/check
Content-Type: application/json

{
  "incident_id": "inc_pay_check_01",
  "payment_intent": true,
  "payment_reason": "JOB_OR_TASK",
  "recipient_vpa": "taskvip.deposit@upi",
  "amount_inr": 10000.0,
  "journey_stage": "PAYMENT_REQUEST",
  "payment_proximity": "REQUESTED",
  "tactics_present": ["FAKE_REWARD", "URGENCY"]
}
```

Response:
```json
{
  "incident_id": "inc_pay_check_01",
  "can_proceed": false,
  "requires_cooling_off": true,
  "cooling_off_minutes": 120,
  "friction_level": "DELAY_PAYMENT",
  "intervention_decision": {
    "intervention_type": "DELAY_PAYMENT",
    "consumer_headline": "Task Scam Warning: Deposit Request After Small Reward",
    "recommended_steps": [
      "Do not deposit funds to withdraw previously earned bonuses.",
      "Stop communication with the Telegram or WhatsApp task coordinator.",
      "Legitimate employers never demand security fees to assign tasks."
    ]
  },
  "warning_summary": "Task Scam Warning: Deposit Request After Small Reward"
}
```
