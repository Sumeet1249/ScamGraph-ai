# SCAMGRAPH AI — INTERVENTION UX CONTRACT (PHASE 4B)
## Consumer-Safe Warning Hierarchy, Content Structure & Components

### 1. Consumer Warning Hierarchy

| Tone / Level | Semantic Tone | Associated Interventions | Presentation Style |
|---|---|---|---|
| **Level 1 (Passive)** | Emerald / Info | `EDUCATE` | Inline educational notice; no interruption. |
| **Level 2 (Light)** | Cyan / Advisory | `VERIFY_INDEPENDENTLY` | Dismissible check recommendation with direct steps. |
| **Level 3 (Moderate)** | Yellow / Caution | `WARN`, `PAUSE_AND_VERIFY` | Highlighted caution banner with pause prompt. |
| **Level 4 (Strong)** | Orange / Strong Caution | `TALK_TO_TRUSTED_PERSON`, `DO_NOT_SHARE_OTP`, `DO_NOT_INSTALL_REMOTE_ACCESS` | Modal card requiring user acknowledgment before proceeding. |
| **Level 5 (Delay Payment)** | Amber / Mandatory Friction | `DELAY_PAYMENT`, `BREAK_CONTACT_AND_VERIFY` | Prominent countdown timer (120 minutes) and friction prompt. |
| **Level 6 (Emergency)** | Red / Emergency Response | `EMERGENCY_RESPONSE` | Urgent action card with immediate 1930 Cybercrime Helpline click-to-call and bank freeze instructions. |

---

### 2. Standard Warning Content Structure

Every intervention modal and card adheres strictly to a 3-part layout:
1. **WHAT DID WE NOTICE?**
   - E.g.: *"You have been asked to install screen-sharing software (AnyDesk) and transfer a small fee."*
2. **WHY DOES IT MATTER?**
   - E.g.: *"Screen-sharing gives the remote caller full view and control of your banking apps and OTP messages."*
3. **WHAT SHOULD I DO RIGHT NOW?**
   - E.g.:
     - *"1. Refuse to install screen-sharing tools."*
     - *"2. Call your bank using the phone number on your debit card."*
     - *"3. Contact someone you trust before proceeding."*

---

### 3. Reusable Frontend Component Contracts

- `InterventionBanner`: Displays in-line alerts for Levels 1–3 without obscuring main content.
- `InterventionModal`: Modal overlay for Levels 4–5 enforcing pause and verification steps.
- `PaymentGuardCard`: Pre-payment widget asking *"Why are you paying?"* and evaluating `PrePaymentContext`.
- `TrustedPersonPrompt`: Anti-isolation prompt generating a privacy-safe shareable summary for family/friends.
- `EmergencyActionCard`: Post-loss action card with 1930 National Cybercrime Helpline details.
