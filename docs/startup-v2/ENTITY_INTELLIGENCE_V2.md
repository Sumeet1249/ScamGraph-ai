# ScamGraph AI — Advanced Entity Intelligence V2

> **Document Version**: 2.0.0  
> **Status**: APPROVED  
> **Phase**: 1A — Advanced Entity Intelligence & Cross-Channel Identity Foundation  

---

## 1. Executive Mission & Strategic Shift

In basic scam detection prototypes, an entity is treated as an isolated string check:
- `phone -> scam?`
- `URL -> scam?`
- `UPI -> scam?`

In **ScamGraph AI V2**, entities become versioned, evidence-backed, privacy-aware nodes connected to observations, journeys, and campaigns across incidents.

### The Network Effect Shift

```
OLD (Isolated Point Classifiers):
[Phone: 9876543210]  --->  [Scam: 87%?]
[UPI: worker@oksbi]  --->  [Scam: 92%?]

NEW (Cross-Incident Evidence Network):
                 Phone (+91******3210)
                          │
                   WhatsApp Account
                          │
Message ───────────── Incident A ───────────── Domain (jobs-verify.in)
                          │                          │
                       UPI VPA                  Host Server
                   (w****@oksbi)                     │
                          │                     Incident C
                      Incident B                    │
                       /      \                     │
                 Telegram    Domain ────────────────┘
               (@easyjob)  (jobs-verify.in)
                       \      /
                      Incident D
                          ↓
          Evidence-Backed Infrastructure Cluster
                          ↓
               POSSIBLY RELATED CAMPAIGN
```

An entity being reported, observed, or connected does **NOT** automatically mean it is fraudulent or malicious. ScamGraph enforces rigorous cognitive boundaries:
- **OBSERVATION**: The technical event of seeing an identifier in a channel or interaction.
- **SIGNAL**: A detected manipulation marker, urgency pattern, or impersonation tag.
- **CLAIM**: An assertion made by a user, model, or third party (e.g. *"This UPI belongs to an electricity officer"*).
- **EVIDENCE**: Cryptographically hashed, timestamped corroborating or contradictory facts.
- **ASSESSMENT**: Situational evaluation combining evidence, corroboration, and temporal decay.
- **VERIFICATION**: Authoritative corroboration from a sovereign or institutional directory.

---

## 2. Logical Dataflow Pipeline

```
+-----------------------------------------------------------------------------------+
| 1. RAW ARTIFACT (Message, Header, Link, VPA, Call Transcript)                     |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| 2. DETERMINISTIC & MODEL EXTRACTION (Regex spans, lexical tokens, NER)           |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| 3. TYPE VALIDATION (VALID, POSSIBLY_VALID, INVALID, UNKNOWN)                      |
|    Format validity != Fraud. Malformed syntax is recorded without malice bias.    |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| 4. NORMALIZATION & CANONICALIZATION                                               |
|    E.164 phones (+91), IDNA punycode, normalized URLs, lowercase UPI VPAs         |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| 5. PRIVACY PROCESSING (Display Masking & Cryptographic Correlation Hash)          |
|    Raw: +91 98765-43210  -->  Display: ******3210  -->  Hash: SHA-256(...)        |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| 6. ENTITY RESOLUTION (Exact Hash Match, Alias Index, Fuzzy Review Candidate)      |
|    Rule: Fuzzy candidates are NEVER auto-merged; flagged as REQUIRES_REVIEW.      |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| 7. CONTEXTUAL OBSERVATION (EntityObservation)                                     |
|    Roles: SENDER, PAYMENT_RECIPIENT, CLAIMED_AUTHORITY, REDIRECT_TARGET, HOST     |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| 8. EVIDENCE-BACKED RELATIONSHIPS (EntityRelationship)                             |
|    APPEARED_WITH, HOSTED_ON, REQUESTED_PAYMENT_TO, SHARES_INFRASTRUCTURE         |
|    Constitutional Rule: NEVER infer SAME_CRIMINAL without judicial evidence.      |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
| 9. TRUST INTELLIGENCE & REPUTATION DECAY                                          |
|    Known Legitimate, Likely Legitimate, Caution, Suspicious, High Risk, Disputed  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Supported Entity Types

| Entity Type | Definition | Normalization Rules | Safe Display Format |
| :--- | :--- | :--- | :--- |
| **`PHONE`** | Voice/SMS phone number | Indian E.164 (`+91` prefix for 10-digit mobiles starting 6-9) | `******3210` |
| **`EMAIL`** | Email address | Trim whitespace, lowercase domain, Unicode NFC | `s***@example.com` |
| **`URL`** | Web resource hyperlink | Lowercase scheme/host, strip default ports, canonical query sort | `https://sbi-kyc.top/update` |
| **`DOMAIN`** | Network hostname | Lowercase, strip `www.`, IDNA/Punycode homoglyph decoding | `secure-bank.example` |
| **`UPI_VPA`** | Virtual Payment Address | Lowercase `handle@psp`, validate PSP syntax | `s***@oksbi` |
| **`BANK_ACCOUNT_TOKEN`** | Tokenized account number | Digits only, HMAC-SHA256 correlation hash | `********9012` |
| **`IFSC`** | Indian Financial System Code | 11-character uppercase bank branch identifier | `SBIN0001234` |
| **`TELEGRAM_HANDLE`** | Telegram account/channel | Lowercase alphanumeric, strip `@` and `t.me/` | `@workindia` |
| **`WHATSAPP_NUMBER`** | WhatsApp identity | Verified phone number mapped to WhatsApp channel | `+91******8844` |
| **`BRAND`** | Commercial or banking entity | Canonical brand name mapping (`sbi` $\rightarrow$ State Bank of India) | State Bank of India |
| **`ORGANIZATION`** | Legal/gov institution | Real organization decoupled from claimed identity | CBI / Police |
| **`IP_ADDRESS`** | IPv4 or IPv6 address | Canonical zero-compressed IP address | `198.51.100.1` |
| **`CRYPTO_ADDRESS`** | Blockchain wallet address | Base58/Bech32/Hex canonical format | `bc1q***` |
| **`APP_PACKAGE`** | Android APK package ID | Reverse-domain string (`com.example.app`) | `com.sbi.yono` |
| **`DEVICE_TOKEN`** | Hardware/browser token | Pseudonymized hash token | `dev_***` |
| **`QR_PAYLOAD`** | Parsed QR string | UPI deep-link format validation | `upi://pay?pa=...` |
| **`OTHER`** | Fallback identifier | Trimmed string representation | Masked fallback |

---

## 4. Key Differentiator: Multi-Hop Cross-Channel Correlation

A scam campaign rarely operates on a single channel. An ordinary consumer check reveals only a single fragment:
- **Incident A (Consumer 1)**: Receives an SMS from WhatsApp `+91******1234` pointing to `jobs-verify.in`, requesting payment to `recruiter@upi`.
- **Incident B (Consumer 2)**: Contacted on Telegram `@easyjob`, requesting payment to `recruiter@upi`.
- **Incident C (Consumer 3)**: Browser redirected to `jobs-verify.in` with contact Telegram `@easyjob`.

### ScamGraph Intelligence Synthesis:
ScamGraph automatically traverses the relationship graph:
$$\text{Incident A} \xrightarrow{\text{UPI}} \text{recruiter@upi} \xleftarrow{\text{UPI}} \text{Incident B} \xrightarrow{\text{Telegram}} \text{@easyjob} \xleftarrow{\text{Telegram}} \text{Incident C}$$

The system infers: **`POSSIBLY_RELATED_CAMPAIGN`** sharing 1 payment identifier, 1 domain, and 1 social handle.  
When Consumer 4 encounters `jobs-verify.in`, ScamGraph immediately surfaces:
> *"This domain shares infrastructure with 3 independent incidents involving Telegram task fraud. Do not proceed or send deposits."*
