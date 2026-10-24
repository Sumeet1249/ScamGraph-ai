# SCAMGRAPH AI — INTERVENTION POLICY ENGINE SPECIFICATION (PHASE 4B)
## Rule Evaluation Order, Precedence, and Edge Cases

### 1. Priority Rule Precedence

The Intervention Policy Engine (`services/intervention_engine/policy.py`) executes 12 rules in strict descending priority:

```
[Rule 1] Already Paid / Post-Loss?           ──> EMERGENCY_RESPONSE (Level 6)
   │ No
[Rule 2] Remote Access Software / APK?       ──> DO_NOT_INSTALL_REMOTE_ACCESS (Level 4)
   │ No
[Rule 3] OTP / Credential Capture?           ──> DO_NOT_SHARE_OTP / CREDENTIALS (Level 4)
   │ No
[Rule 4] Digital Arrest (Secrecy + Fear)?    ──> TALK_TO_TRUSTED_PERSON (Level 4)
   │ No
[Rule 5] Task Scam (Reward + Deposit)?       ──> DELAY_PAYMENT (Level 5)
   │ No
[Rule 6] Campaign Outbreak Match?            ──> DELAY_PAYMENT / STRONG_WARNING
   │ No
[Rule 7] Authority Threat (Police / CBI)?     ──> BREAK_CONTACT_AND_VERIFY / VERIFY
   │ No
[Rule 8] High Risk Imminent Payment?         ──> DELAY_PAYMENT (Level 5)
   │ No
[Rule 9] Routine Legitimate Context?         ──> NO_ACTION (Level 0)
   │ No
[Rule 10] Zero-Day Behavioral Anomaly?       ──> PAUSE_AND_VERIFY / VERIFY (Level 3/2)
   │ No
[Rule 11] Low-Risk Educational Advisory?     ──> EDUCATE (Level 1)
   │ No
[Rule 12] Default Benign?                    ──> NO_ACTION (Level 0)
```

---

### 2. Edge Case Handling

1. **High Risk + Distant Stage**:
   - Risk is 0.85, but journey stage is `INITIAL_CONTACT` (e.g., initial spam pitch).
   - Policy: Do **not** trigger a full payment delay modal yet; issue `STRONG_WARNING` or `VERIFY_INDEPENDENTLY` to avoid alert fatigue before payment intent exists.
2. **Low Risk + High Urgency**:
   - E.g. Flight boarding or legitimate ticket booking.
   - Zero manipulation tactics $\implies$ `NO_ACTION` / `EDUCATE`.
3. **Ambiguous Zero-Day Scam**:
   - No known campaign ID, no matching graph nodes.
   - Coercive tactics and payment pressure alone trigger behavioral `PAUSE_AND_VERIFY` with independent verification.
