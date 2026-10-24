# Official SDK Architecture (TypeScript & Python)

## 1. SDK Design Principles
- **No Direct Engine Duplication**: The SDKs are pure HTTP/REST wrappers.
- **Configurable Timeouts & Retries**: Exponential backoff with jitter on network drops and HTTP 429/503.
- **Idempotency Auto-Header**: Automatically embeds or passes custom `idempotency_key`.
- **HMAC Webhook Verification Helper**: One-line cryptographic verification helper with timestamp replay checks.

## 2. Python SDK (`packages/sdk_python/scamgraph`)
```python
from packages.sdk_python.scamgraph import ScamGraphClient, verify_webhook_signature

client = ScamGraphClient(api_key="sg_live_...")

# Pre-Payment Guard Check (<25ms)
guard_decision = client.guard_check(
    vpa="urgent.police@oksbi",
    amount=25000.0,
    message_text="Turant deposit pay karo"
)
if guard_decision["action"] == "STRONG_WARNING":
    trigger_payment_pause(guard_decision["safe_guidance"])

# Webhook verification
is_valid = client.verify_webhook(secret, signature_header, raw_bytes)
```

## 3. TypeScript SDK (`packages/sdk-typescript`)
```typescript
import { ScamGraphClient, verifyWebhookSignature } from "@scamgraph/sdk";

const client = new ScamGraphClient({ apiKey: "sg_live_..." });

const checkResult = await client.check({
  messageText: "Your bank account has been suspended. Click link.",
  url: "https://suspicious-bank-login.in"
});

console.log(checkResult.risk_level, checkResult.recommended_action);
```
