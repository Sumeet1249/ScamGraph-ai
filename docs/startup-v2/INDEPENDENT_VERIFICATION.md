# SCAMGRAPH AI — INDEPENDENT VERIFICATION SPECIFICATION (PHASE 4B)
## Anti-Loophole Identity Verification & Safe Verification Plans

### 1. The Golden Rule of Verification

> **Never verify legitimacy using contact details supplied by the suspicious party.**

Attackers routinely embed:
- Fake toll-free helpline numbers in phishing SMS.
- Compromised or lookalike customer service URLs in emails.
- Telegram handles of fake "officers" or "auditors" in WhatsApp messages.

If ScamGraph simply advised *"Call the support number in the message,"* it would deliver the victim straight into the attacker's hands.

---

### 2. VerificationPlan Schema

```python
class VerificationPlan(BaseModel):
    plan_id: str
    verification_type: str        # BANK_DIRECT, GOVERNMENT_PORTAL, EMPLOYER_HR, COURIER_DIRECT
    target_type: str              # FINANCIAL_INSTITUTION, GOVERNMENT_AGENCY, EMPLOYER, MARKETPLACE
    trusted_source_required: str  # E.g. Official app, backside debit card toll-free, .gov.in domain
    steps: List[str]              # 3-4 concrete verification instructions
    reason: str                   # Why this method breaks attacker's loop
    confidence: float
    metadata: Dict[str, Any]
```

---

### 3. Verification Plans by Institution

| Claimed Entity | Verification Type | Required Trusted Source | Concrete Action Steps |
|---|---|---|---|
| **Bank / KYC** | `BANK_DIRECT` | Backside of physical debit card or official mobile banking app. | 1. Open official banking app directly from home screen.<br>2. Check in-app alerts and notifications.<br>3. Call phone number printed on the back of your card. |
| **Police / CBI / Customs** | `GOVERNMENT_PORTAL` | 1930 Helpline or official `.gov.in` portal. | 1. Disconnect Skype/WhatsApp video immediately.<br>2. Call 1930 (National Cybercrime Helpline).<br>3. Visit local police station in person. |
| **Employer / Job Offer** | `EMPLOYER_HR` | Official corporate domain careers page. | 1. Type corporate domain manually in browser.<br>2. Verify job opening ID in official careers section.<br>3. Email HR using `@company.com` verified corporate domain. |
| **Courier / Delivery** | `COURIER_DIRECT` | Official courier tracking app/site. | 1. Visit official website (e.g. `indiapost.gov.in`).<br>2. Enter consignment tracking number manually.<br>3. Never click SMS link for address update. |
