# ScamGraph AI — Universal Journey Stage Ontology V2

## 1. Overview
The Universal Journey Stage Ontology formally classifies the 15 canonical operational stages across Indian fraud journeys, structured into 5 coarse-grained lifecycle categories.

---

## 2. Canonical Stages & Lifecycle Categories

| # | Stage Name | Category | Primary Indicators & Triggering Signals | Exit / Progression Criteria |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `DISCOVERY` | PRE-MONETIZATION | Social media ad click, job vacancy lure, spoofed search engine result. | User clicks link or views contact point. |
| 2 | `CONTACT` | PRE-MONETIZATION | Cold SMS, WhatsApp outbound greeting, automated IVR call. | Reciprocal conversation turn initiated. |
| 3 | `TRUST_BUILDING` | PRE-MONETIZATION | Small free test task, returned ₹150 profit, forged ISO/Govt certificate. | User accepts validity of the actor. |
| 4 | `IMPERSONATION` | PRE-MONETIZATION | Posing as CBI, Police, FedEx customs, SBI security division. | Authority or brand identity established. |
| 5 | `PLATFORM_MIGRATION`| PRE-MONETIZATION | Requesting user to switch from marketplace/dating app to Telegram/WhatsApp. | User joins private chat or group. |
| 6 | `URGENCY` | PRE-MONETIZATION | Strict time limit ("2 hours left", "electricity disconnect at 9:30 PM"). | User compelled to act without delay. |
| 7 | `CREDENTIAL_REQUEST`| PRE-MONETIZATION | Requesting OTP, netbanking login, ATM PIN, or remote support app (AnyDesk).| Direct financial extraction attempt. |
| 8 | `INITIAL_PAYMENT` | MONETIZATION | First money transfer, small deposit (₹500–₹5,000), registration fee. | Money sent or collect request approved. |
| 9 | `REWARD_OR_FAKE_PROFIT`| REINFORCEMENT | Fabricated wallet balance credit, trading dashboard profit screenshot. | User convinced of profitable returns. |
| 10 | `PAYMENT_ESCALATION`| MONETIZATION | Demanding larger deposits (₹25,000–₹1,00,000) to unlock VIP tasks/tiers. | Multiple/higher-value payment demands. |
| 11 | `WITHDRAWAL_BLOCK` | CONTROL/RETENTION | Withdrawal locked citing capital gains tax, channel fee, or AML verification.| Victim attempts to withdraw balance. |
| 12 | `RECOVERY_FEE` | MONETIZATION | Demanding 20–30% fee to unfreeze balance or refund lost money. | Advanced fee requested under duress. |
| 13 | `THREAT_OR_PRESSURE`| CONTROL/RETENTION | Threat of arrest warrant, police raid, physical defamation, or blackmail. | Coercive pressure to maintain isolation. |
| 14 | `EXIT` | TERMINATION | Attacker ceases contact, deletes chat group, or blocks victim's number. | Communication permanently terminates. |
| 15 | `UNKNOWN` | UNKNOWN | Encounter does not contain sufficient evidence to resolve stage. | Insufficient context. |

---

## 3. Coarse-Grained Category Rules

- **`PRE_MONETIZATION`**: Discovery, contact, rapport building, credential harvest, and channel migration. High intervention efficacy with $0 financial loss.
- **`MONETIZATION`**: Initial payments, escalated recharges, and secondary recovery fees. Active financial extraction occurring.
- **`REINFORCEMENT`**: Fake balance increases, withdrawal illusions, and social proof reinforcement designed to deepen investment.
- **`CONTROL_RETENTION`**: Denial of exit, withdrawal freezes, and fear-based extortion to extract remaining assets.
- **`TERMINATION`**: End of engagement, loss realized.
