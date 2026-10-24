# Recovery-Scam Protection & Secondary Fraud Defense (Phase 5B)

## Threat Anatomy
A **Recovery Scam** (or double-dip fraud) specifically targets individuals who have already incurred a financial loss. Attackers pose as:
- Fake "ethical hackers" or recovery agents on Telegram/Instagram.
- Fake "cyber law advocates" demanding an advance legal retainer.
- The original scammer claiming a "clearance tax" or "anti-money laundering voucher" must be paid to unfreeze the trapped wallet balance.

## Defense Engine
ScamGraph Rescue features an interactive and automated recovery scam defense:
1. **Rule Engine Patterns**:
   - `ADVANCE_RECOVERY_FEE`: Any demand for payment to retrieve or unfreeze previous funds.
   - `FAKE_HACKER_SOLICITATION`: Claims of "hacking back" or retrieving crypto/UPI transactions.
   - `UNFREEZE_PAYMENT_ESCALATION`: "Pay 20% tax before withdrawal can be released".
   - `OTP_REFUND_TRAP`: Demanding OTPs under the guise of processing a refund.
2. **Persistent Advisory**:
   - Every Rescue dashboard view displays an unambiguous warning: *No legitimate authority or bank charges fees to investigate fraud.*
3. **Interactive Message Screener**:
   - Allows users to paste any follow-up communication to evaluate whether they are being retargeted.
