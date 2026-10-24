# ScamGraph AI — Entity Privacy & Anti-Enumeration Defense

> **Document Version**: 2.0.0  
> **Status**: APPROVED  
> **Phase**: 1A — Entity Privacy & Data Protection  

---

## 1. The Core Privacy Mandate

ScamGraph's mission is to protect citizens from fraud, not to build a public surveillance directory. An intelligence platform that exposes consumer phone numbers, UPI addresses, or banking details under the guise of fraud warnings creates severe secondary victimization.

### Separation of Values

| Value Category | Storage Location | Access Authorization | Example |
| :--- | :--- | :--- | :--- |
| **Raw Evidence** | Encrypted isolated vault | High-privilege analyst audit only | `+91 98765-43210` |
| **Normalized Value** | Internal memory / pipeline | Internal micro-services only | `+919876543210` |
| **Masked Display** | Database, API, UI | **Public & Consumer Safe** | `******3210` |
| **Canonical Hash** | PostgreSQL index & graph | Internal correlation engine | `sha256("...")` |

---

## 2. PII Display Masking Rules

| Entity Type | Masking Algorithm | Unmasked Example | Masked Display Output |
| :--- | :--- | :--- | :--- |
| **`PHONE`** | Retains last 4 digits; asterisks all preceding digits | `+919876543210` | `******3210` |
| **`EMAIL`** | First character of local part + `***` + domain | `sumeet@example.com` | `s***@example.com` |
| **`UPI_VPA`** | First character of handle + `***` + `@` + PSP handle | `rohit.kumar@oksbi` | `r***@oksbi` |
| **`BANK_ACCOUNT`**| Retains last 4 digits; asterisks all preceding digits | `123456789012` | `********9012` |
| **`SOCIAL_HANDLE`**| Lowercase handle with `@` prefix | `EasyJobOfficial` | `@easyjobofficial` |

---

## 3. Anti-Enumeration Defense (Rule 47)

### Threat Model
Malicious actors, scammers, or scraping bots may query ScamGraph APIs to test whether a victim's phone number has been reported, or scrape a directory of compromised bank accounts.

### Defensive Safeguards
1. **No Wildcard Queries**: Queries containing `*`, `%`, `?`, or SQL fragments are rejected at the edge with HTTP 400.
2. **Minimum Length Constraints**: Queries shorter than 3 characters are blocked.
3. **Strict Rate Limiting**: Max 60 queries/minute per client IP / API token.
4. **Aggregated Cross-Victim Output**: When Consumer A queries a suspicious UPI ID, ScamGraph displays:
   > *"This payment identifier has appeared in 8 confirmed scam reports associated with task deposit fraud."*
   The system **never** displays the names, phone numbers, or amounts lost by the 8 earlier victims.

---

## 4. Privacy Invariants in ML & Logs
- **No Raw PII in Logs**: Log formatters replace sensitive fields with opaque IDs (`ent_...`, `obs_...`).
- **No Raw PII in Graph Labels**: Neo4j node labels display `entity_id` and `masked_value`.
- **Tokenized ML Features**: Model training pipelines use `<PHONE>`, `<EMAIL>`, `<UPI_VPA>`, and `<ACCOUNT_TOKEN>` tokens.
