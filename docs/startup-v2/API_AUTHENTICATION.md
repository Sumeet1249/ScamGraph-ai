# API Authentication & Key Security

## 1. Key Formats
- Live Gateway: `sg_live_<random_base64_secret>`
- Sandbox / Testing: `sg_test_<random_base64_secret>`

## 2. Zero Raw Secret Storage
ScamGraph NEVER stores plaintext API keys:
- The raw secret is displayed ONCE during generation (`ApiKeyCreateResponse`).
- In backend storage, only `hashed_secret` (SHA-256) and `key_prefix` (e.g. `sg_live_apex`) are persisted.
- During authentication: Incoming header `X-API-Key` or `Authorization: Bearer <key>` is SHA-256 hashed and looked up in the index.

## 3. Scopes & Permissions
- `check:write`: Execute Scam Check API
- `guard:write`: Execute Pre-Payment Guard API
- `entity:read`: Read-only entity reputation queries
- `campaign:read`: Read-only campaign and outbreak intelligence
- `webhook:manage`: Configure and rotate webhook endpoints
