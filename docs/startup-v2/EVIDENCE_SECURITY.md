# Evidence Security & Secure Media Access (Prompt 21 / Phase 7A)

## 1. Sensitivity Classification

| Sensitivity Class | Resource Modalities | Access Control Rule | Redaction Required |
|:---|:---|:---|:---|
| **PUBLIC** | Whitelisted brand names, official bank IFSC, public domain URLs. | Open to all authenticated principals. | No |
| **INTERNAL** | System detector telemetry, model feature vectors, internal rule IDs. | Internal analysts & system admins. | No |
| **CONFIDENTIAL** | Masked phone numbers, obfuscated VPAs, normalized behavioral tactics. | Analysts and authorized org viewers. | Partial (Masked) |
| **HIGHLY_SENSITIVE**| Unmasked chat transcripts, payment screenshots, audio recordings. | Senior analysts, org analysts (own org), consumer owner. | Yes (for normal analysts) |
| **RESTRICTED** | Aadhaar/PAN cards, bank account tokens, OTPs, PINs. | Strictly restricted to owner and senior investigators. | Yes |

---

## 2. Derived Indicators vs. Raw Media Separation
- **Principle**: Access to a derived indicator (e.g. "VPA flagged as task scam mule") does **NOT** grant authorization to download or view the victim's raw screenshot or voice note.
- **Normal Analysts**: View extracted entities, tactics, and journey stage, with raw media URLs redacted.
- **Senior Investigators**: May stream raw media only with explicit `evidence:read_raw` permission and mandatory audit trail logging.
- **Zero Permanent Public URLs**: Media is never accessible through static public links.
