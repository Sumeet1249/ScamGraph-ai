# PII Data Map & Classification (Prompt 21 / Phase 7A)

## 1. PII Inventory & Sensitivity Mapping

| Field / Asset | Classification Category | Sensitivity Tier | Retention Period | Access Roles | Logging Policy | Export Policy |
|:---|:---|:---|:---|:---|:---|:---|
| **Victim Real Name** | DIRECT_IDENTIFIER | HIGHLY_SENSITIVE | Configurable (90d default) | Consumer Owner, Senior Analyst | **REDACTED** | Sanitized |
| **Phone Number** | DIRECT_IDENTIFIER | CONFIDENTIAL | Configurable (180d) | Owner, Analyst, Org Admin | Masked (`+91 •••••• 4821`)| Sanitized |
| **Email Address** | DIRECT_IDENTIFIER | CONFIDENTIAL | Account Lifetime | Owner, Admin | Masked | Sanitized |
| **UPI VPA** | FINANCIAL_IDENTIFIER | CONFIDENTIAL | Correlated lifecycle | Analysts, Integrators | Masked (`s••••@oksbi`) | Sanitized |
| **Bank Account Token**| FINANCIAL_IDENTIFIER | RESTRICTED | 30d post-investigation | Senior Analyst, Owner | **REDACTED** | Blocked |
| **Screenshot Image** | SENSITIVE_MEDIA | HIGHLY_SENSITIVE | Configurable (60d default) | Owner, Senior Analyst, Org Analyst | Prohibited | Controlled Job |
| **Call Audio / Voice**| SENSITIVE_MEDIA | HIGHLY_SENSITIVE | Configurable (30d default) | Owner, Senior Analyst | Prohibited | Controlled Job |
| **Aadhaar / ID Card** | DIRECT_IDENTIFIER | RESTRICTED | Zero permanent storage | Owner, Senior Analyst | Prohibited | Blocked |
| **API Secret Token** | SECURITY_CREDENTIAL | RESTRICTED | Active key lifetime | Zero storage (Hashed only) | **REDACTED** | Blocked |
| **Webhook Secret** | SECURITY_CREDENTIAL | RESTRICTED | Active webhook lifetime | Zero plaintext in logs | **REDACTED** | Blocked |
| **Graph Path / Score**| OPERATIONAL_METADATA | INTERNAL | Permanent aggregate | All authenticated | Logged | Allowed |
