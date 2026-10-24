# Evidence Model & Dual-Axis Assessment Specification

## 1. Core Principle: Evidence Over Declarations

In ScamGraph AI:
- **No model declares fraud.**
- Individual models, extractors, and rules generate **Evidence Signals**.
- The system synthesizes these signals into a calibrated dual-axis assessment:
  - **Risk Level**: What is the severity and likelihood of harm?
  - **Evidence Confidence**: How reliable, corroborated, and complete is the supporting evidence?

```
                    ▲ Evidence Confidence
                    │
      [High Risk    │    [High Risk
       Low Conf]    │     High Conf]
                    │
  ──────────────────┼──────────────────► Risk Level
                    │
      [Low Risk     │    [Low Risk
       Low Conf]    │     High Conf]
                    │
```

---

## 2. Anatomy of an Evidence Signal

Every signal produced across any of the 7 correlation dimensions adheres to a uniform structure:

```json
{
  "signal_id": "sig_9f81a7b2-3c4d-4e5f",
  "incident_id": "inc_7a6b5c4d-1e2f-3a4b",
  "dimension": "URL",
  "signal_type": "TYPOSQUATTING_DOMAIN",
  "severity": "HIGH",
  "confidence": 0.92,
  "weight": 1.5,
  "observed_at": "2026-10-20T23:30:00Z",
  "provenance": {
    "source_service": "services/investigation",
    "provider": "TinyFish API",
    "target": "sbi-kyc-update.online",
    "raw_evidence": {
      "domain_age_days": 2,
      "free_ssl_issuer": "Let's Encrypt",
      "similar_legitimate_domain": "onlinesbi.sbi"
    }
  }
}
```

---

## 3. The Seven Correlation Dimensions

1. **Semantic Message Signals**:
   - `URGENCY_PRESSURE` (coercive timelines)
   - `IMPERSONATION_OFFICIAL` (spoofing trusted entities)
   - `THREAT_DISCONNECTION_OR_BLOCK` (punitive claims)
   - `UNSOLICITED_JOB_OFFER` (high compensation / low effort)

2. **URL / Web Evidence**:
   - `FRESH_DOMAIN` (registered < 30 days ago)
   - `TYPOSQUATTING` (lookalike brand names)
   - `REDIRECT_CHAIN_OBSFUCATION` (shortener nesting)
   - `MALICIOUS_APK_DOWNLOAD` (direct Android payload download)

3. **Payment Context**:
   - `VPA_ENTITY_MISMATCH` (e.g. claims to be Tata Power, VPA is personal `@ybl`)
   - `COLLECT_REQUEST_INITIATION` (tricking user into approving an outbound payment)
   - `QR_CODE_PAYMENT_SCAM` (claiming QR code is to *receive* funds)

4. **Temporal Event Sequence**:
   - `RAPID_STAGE_PROGRESSION` (grooming completed within minutes)
   - `CADENCE_HARASSMENT` (multiple rapid follow-up contacts)

5. **Infrastructure Relationships**:
   - `SHARED_HOSTING_WITH_KNOWN_MALWARE`
   - `REUSED_SENDER_ID_ACROSS_VICTIMS`
   - `BULK_VPA_GENERATION`

6. **Historical Incidents**:
   - `KNOWN_MODUS_OPERANDI_MATCH`
   - `CROSS_INCIDENT_HANDLE_REUSE`

7. **Campaign Similarity**:
   - `HIGH_COSINE_SIMILARITY_TO_ACTIVE_CAMPAIGN` (threshold > 0.82 via pgvector)

---

## 4. Dual-Axis Computation & Calibration

### 4.1 Risk Score ($R$)
$$R = \frac{\sum_{i=1}^{n} w_i \cdot s_i \cdot c_i}{\sum_{i=1}^{n} w_i}$$
Where:
- $w_i$: Dimension weight
- $s_i$: Normalized severity score (INFO: 0.1, LOW: 0.3, MEDIUM: 0.6, HIGH: 0.85, CRITICAL: 1.0)
- $c_i$: Local detector confidence $(0.0 - 1.0)$

### 4.2 Evidence Confidence ($C$)
Evidence confidence is determined by **cross-dimension corroboration**:
- **LOW Confidence**: Signals originate from only 1 dimension (e.g. semantic cues only, with no URL or payment context).
- **MEDIUM Confidence**: Signals verified across 2 independent dimensions.
- **HIGH Confidence**: Signals corroborated across 3 or more independent dimensions (e.g., semantic threat + brand-new lookalike domain + personal UPI handle mismatch).

### 4.3 Triggering `INSUFFICIENT_EVIDENCE`
The assessment engine explicitly outputs `INSUFFICIENT_EVIDENCE` when:
- Total observed signals < 2, AND
- No high-severity signal exists, OR
- Only benign / uncorroborated text messages have been observed without payment or link context.

---

## 5. Adaptive Intervention Matrix

To minimize alert fatigue, the user is never bombarded with generic warning popups. Instead, friction scales with Risk and Evidence Confidence:

| Risk Level | Confidence | Recommended Intervention |
|---|---|---|
| Any | LOW | **Passive Monitoring**: Log telemetry, no visible friction. |
| MEDIUM | MEDIUM | **Contextual Banner**: Non-blocking warning explaining the specific missing check. |
| HIGH | MEDIUM | **Identity / Payee Friction**: Display verified recipient name with confirmation prompt. |
| HIGH | HIGH | **Protective Delay / Step-up**: 10-second countdown friction before payment intent confirmation with explicit journey breakdown. |
