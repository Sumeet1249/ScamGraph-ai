# Privacy Test Matrix (Prompt 21 / Phase 7A)

| Resource / Action | ANONYMOUS | CONSUMER OWNER | OTHER CONSUMER | ORG VIEWER | ORG ANALYST | ORG ADMIN | SCAMGRAPH ANALYST | SENIOR ANALYST | ADMIN | API CLIENT |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Scam Check (Text / URL)** | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| **Own Incident History** | DENY | ALLOW | DENY | DENY | DENY | DENY | REDACT | ALLOW | ALLOW | DENY |
| **Org Incident History** | DENY | DENY | DENY | ALLOW | ALLOW | ALLOW | REDACT | ALLOW | ALLOW | ALLOW (Org) |
| **Other Org Incident** | DENY | DENY | DENY | DENY | DENY | DENY | REDACT | ALLOW | ALLOW | DENY |
| **Derived Indicators (Tactics/Stage)**| AGGREGATE | ALLOW | AGGREGATE | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| **Raw Screenshot Media** | DENY | ALLOW | DENY | DENY | ALLOW (Org) | ALLOW (Org)| REDACT | ALLOW | ALLOW | DENY |
| **Raw Voice / Audio Media** | DENY | ALLOW | DENY | DENY | DENY | DENY | REDACT | ALLOW | ALLOW | DENY |
| **Unmasked Bank Account / OTP** | DENY | REDACT | DENY | DENY | DENY | DENY | REDACT | ALLOW | ALLOW | DENY |
| **Case Package Export** | DENY | ALLOW (Own)| DENY | DENY | DENY | ALLOW (Org)| DENY | ALLOW | ALLOW | DENY |
| **Global Campaign Intelligence** | DENY | REDACT | REDACT | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW (Scope)|
| **Outbreak Radar Summary** | DENY | REDACT | REDACT | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW (Scope)|
| **Model Training Inclusion** | DENY | CONSENT_REQ| DENY | DENY | DENY | DENY | DENY | DENY | DENY | CONSENT_REQ |
| **Security Audit Trail** | DENY | DENY | DENY | DENY | DENY | ALLOW (Org)| ALLOW | ALLOW | ALLOW | DENY |
