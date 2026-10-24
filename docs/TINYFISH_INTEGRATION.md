# ScamGraph AI — TinyFish Live WebInvestigator Integration (Step 17)

## 1. Executive Purpose & Architectural Principles

TinyFish is integrated as ScamGraph's live `WebInvestigator` provider.

> **Foundational Rule**:
> TinyFish is strictly an **OBSERVATION ENGINE**, not a fraud judge.
> * ScamGraph **never** prompts TinyFish with questions like *"Is this a scam?"* or requests a *"scam probability"*.
> * TinyFish is asked to inspect and report **pure objective observables** on the webpage (input fields, claimed brand names, displayed phone numbers, payment identifiers, urgency copy, redirect steps).
> * The core ScamGraph pipeline retains total responsibility for pattern sequence matching, threat indexing, and intervention decisions.

```
                    Target URL (from Message/Event)
                               │
                               ▼
                      [URLSafetyValidator]
                   (SSRF Guard Pre-Validation)
                               │ (Safe Public URL Only)
                               ▼
                    [TinyFishWebInvestigator]
              ┌────────────────┴────────────────┐
              │                                 │
     (TINYFISH_MODE=live)              (TINYFISH_MODE=mock)
      TinyFish Cloud API                Controlled JSON Fixtures
   (Strict 4s timeout + 2 retries)     (benign, kyc, investment, malformed)
              │                                 │
              └────────────────┬────────────────┘
                               │ Structured Observable JSON
                               ▼
                       [TinyFishParser]
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
   Canonical Evidence[]                   Canonical Entity[]
   (source = "TINYFISH")                  (BRAND, PHONE, EMAIL,
   • OTP_FIELD_PRESENT                     URL, DOMAIN, PAYMENT_ENTITY)
   • CREDENTIAL_COLLECTION
   • CLAIMED_BRAND
   • PAYMENT_IDENTIFIER_OBSERVED
   • URGENCY_LANGUAGE
```

---

## 2. Security & Credentials Management

1. **Environment-Only Secrets**: `TINYFISH_API_KEY` is loaded exclusively from the server-side environment (`os.getenv` / `services.api.app.core.config.settings`).
2. **Never Leaked**: The API key is never committed, never logged, never returned in API payloads, and never sent to frontend bundles.
3. **SSRF Guard Invariant**: No outbound request to TinyFish is permitted until the target URL passes `URLSafetyValidator.is_safe_public_url`. Prohibited local networks, loopback addresses (`127.0.0.0/8`, `::1`), private subnets (`10.0.0.0/8`, `192.168.0.0/16`), and cloud metadata (`169.254.169.254`) are blocked at the perimeter.

---

## 3. Resilience & Failure Degredation

* **Strict Timeouts**: 4.0-second network timeout per attempt with up to 2 retries on 5xx errors.
* **Non-Blocking Resilience**: If TinyFish experiences a timeout, network outage, rate limit, or returns malformed JSON:
  - The provider status is recorded as `"unavailable"`.
  - **Crucial Invariant**: TinyFish failure **NEVER** causes the incident risk to be downgraded to `LOW`.
  - Instead, the incident assessment proceeds using message and URL lexical evidence, while **Evidence Confidence is calibrated downward** to reflect missing DOM observations.

---

## 4. Live vs. Mock Modes

For offline hackathon reliability and automated continuous integration, ScamGraph supports:

```bash
# In .env:
TINYFISH_MODE=mock  # Uses deterministic fixtures under tests/fixtures/tinyfish/
# or
TINYFISH_MODE=live  # Sends live HTTPS queries to https://api.tinyfish.io/v1
```

Both modes execute the identical `TinyFishParser` and `Evidence` pipeline. Only the low-level HTTP transport is swapped.

---

## 5. Verification & Unit Tests

Unit tests in [tests/unit/test_tinyfish_investigator.py](file:///s:/ScamGraph-AI/tests/unit/test_tinyfish_investigator.py) validate all operational paths:
1. **KYC Test Site**: Successfully extracts OTP and credential harvesting fields $\rightarrow$ Canonical `Evidence(source="TINYFISH", signal="OTP_FIELD_PRESENT")`.
2. **Benign Portal**: Observes legitimate billing actions without flagging fraudulent OTP forms.
3. **Investment Scam Site**: Detects cryptocurrency and UPI deposit handles (`invest.pool@fakeupi`).
4. **Malformed Payload Handling**: Gracefully logs errors without crashing.
5. **Timeout Handling**: Returns `status="unavailable"` and allows assessment to continue.
6. **SSRF Guard**: Blocks requests to internal targets (`http://127.0.0.1:8000/secret`) before invoking TinyFish.
