# Rescue Triage & Emergency Action Plan (Phase 5B)

## Triage Priority Matrix
The `RescueTriageEngine` computes severity based on active ongoing threats and time sensitivity:

| Threat Condition | Severity Band | Primary Immediate Trigger |
|---|---|---|
| Active Remote Screen Control | `EMERGENCY_CRITICAL` | Disconnect Wi-Fi/data, terminate remote tool, enable Airplane mode |
| Payment within Golden Window (< 48 hrs) | `EMERGENCY_CRITICAL` | Dial 1930 immediately, trigger inter-bank stop payment freeze alert |
| Compromised Netbanking Password / Active OTP | `URGENT` | Change credentials from clean secondary device, revoke active sessions |
| Identity Document Shared (Aadhaar / PAN) | `ELEVATED` | Lock biometric authentication on UIDAI portal (myaadhaar.uidai.gov.in) |
| Historical Payment (> 30 days) | `STANDARD` | File formal NCRP cybercrime portal report & bank dispute |

---

## Action Plan Taxonomy
Actions are grouped chronologically to prevent victim cognitive overload:

1. **DO NOW (First 15-30 Minutes)**:
   - Terminate remote access software immediately.
   - Dial 1930 Cyber Fraud Helpline with 12-digit UTR and bank account details.
   - Contact sending bank's 24x7 fraud desk to hotlist accounts and debit cards.
   - Cease all communication with the fraudster.

2. **DO NEXT (First 1-2 Hours)**:
   - Reset netbanking and UPI PIN from a trusted uncompromised device.
   - Lock Aadhaar biometrics on UIDAI portal to block AePS unauthorized debits.
   - Confide in a trusted family member or colleague to break isolation.

3. **PRESERVE**:
   - Save original payment PDF receipts showing 12-digit UTR numbers.
   - Preserve unedited full-chat screenshots with dates and phone headers.
   - Record beneficiary UPI VPAs, account numbers, and APK filenames.

4. **REPORT**:
   - File formal cyber financial fraud complaint at `https://cybercrime.gov.in` (NCRP).
   - Record official complaint acknowledgement number for police follow-up.

5. **MONITOR**:
   - Persistent Recovery Scam Warning: Never pay fees to recover lost funds.
   - Review bank statements and SMS notifications daily for unauthorized auto-debits.
