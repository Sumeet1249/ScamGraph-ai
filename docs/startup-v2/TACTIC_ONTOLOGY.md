# ScamGraph AI — Psychological Tactic & Action Ontology V2

## 1. Overview
The ScamGraph Tactic Ontology formally defines 20 psychological manipulation tactics and 17 explicit call-to-action types observed across cyber-fraud journeys in India.

---

## 2. Canonical Psychological Tactics (20 Types)

| # | Tactic Code | Severity | Description | Primary Call to Action |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `AUTHORITY` | HIGH | Actor invokes law enforcement, judicial, or regulatory status (CBI, Police, Court, TRAI, RBI). | `DO_NOT_DISCONNECT`, `REPLY` |
| 2 | `URGENCY` | MEDIUM | Actor imposes artificial time limits or deadlines (e.g., "within 2 hours", "today only"). | `CLICK_LINK`, `SEND_PAYMENT` |
| 3 | `FEAR` | HIGH | Actor threatens arrest, legal prosecution, account freezing, or power disconnection. | `DO_NOT_DISCONNECT`, `SEND_PAYMENT` |
| 4 | `GREED` | MEDIUM | Actor promises unrealistically high, guaranteed daily profits or lottery winnings. | `MOVE_PLATFORM`, `CLICK_LINK` |
| 5 | `SCARCITY` | LOW | Actor claims limited slots, exclusive quotas, or final opportunity to force swift action. | `CLICK_LINK`, `REPLY` |
| 6 | `SOCIAL_PROOF` | LOW | Actor displays fake group testimonials, withdrawal receipts, or claimed member profits. | `MOVE_PLATFORM` |
| 7 | `ROMANCE` | MEDIUM | Actor grooms emotional or matrimonial intimacy before claiming customs parcel fees. | `SEND_PAYMENT`, `PAY_FEE` |
| 8 | `TRUST_BUILDING` | LOW | Actor credits small legitimate-looking profits (₹150–₹500) to build false confidence. | `REPLY`, `INVEST_MORE` |
| 9 | `SECRECY` | HIGH | Actor demands confidentiality, instructing victim not to inform family or bank staff. | `KEEP_SECRET` |
| 10 | `ISOLATION` | CRITICAL | Actor commands victim to stay on video call, lock room door, and refuse outside communication. | `DO_NOT_DISCONNECT`, `KEEP_SECRET` |
| 11 | `RECIPROCITY` | MEDIUM | Actor offers small favors or refunds, then demands larger financial investments or deposits. | `SEND_PAYMENT`, `INVEST_MORE` |
| 12 | `LOSS_AVERSION` | HIGH | Actor warns that existing deposits will be forfeited permanently unless unlock fees are paid. | `SEND_PAYMENT`, `PAY_FEE` |
| 13 | `FAKE_REWARD` | MEDIUM | Actor announces unverified lottery prizes, cashback vouchers, or lucky draw wins. | `CLICK_LINK`, `SCAN_QR` |
| 14 | `THREAT` | CRITICAL | Actor blackmails victim with private photo leakage, home raids, or physical harm. | `SEND_PAYMENT`, `DO_NOT_DISCONNECT` |
| 15 | `IMPERSONATION` | HIGH | Actor poses as legitimate organizations (courier, discom, bank officer, company CEO). | `CALL_NUMBER`, `CLICK_LINK` |
| 16 | `PAYMENT_PRESSURE` | CRITICAL | Actor urgently pressures victim to execute UPI transfers, deposits, or approve collect requests. | `SEND_PAYMENT`, `APPROVE_UPI_REQUEST` |
| 17 | `CREDENTIAL_PRESSURE`| CRITICAL | Actor demands secret OTPs, netbanking passwords, ATM PINs, or CVV codes. | `SHARE_OTP`, `SHARE_CREDENTIAL` |
| 18 | `REMOTE_ACCESS_PRESSURE`| CRITICAL | Actor instructs victim to install AnyDesk, QuickSupport, screen share, or download APKs. | `INSTALL_APP`, `SHARE_SCREEN` |
| 19 | `PLATFORM_MIGRATION`| MEDIUM | Actor shifts communication from public job/matrimonial apps to WhatsApp or Telegram. | `MOVE_PLATFORM`, `ADD_CONTACT` |
| 20 | `COMPLIANCE_PRESSURE`| HIGH | Actor enforces rigid interrogation drills ("Answer only yes or no", "Obey the officer"). | `DO_NOT_DISCONNECT`, `REPLY` |

---

## 3. Explicit Calls to Action (17 Types)

| Action Code | Description | High-Risk Threat Context |
| :--- | :--- | :--- |
| `CLICK_LINK` | Visiting a URL or web portal | Phishing, malicious credential harvester |
| `CALL_NUMBER` | Dialing a provided phone number | Fake customer care, IVR routing |
| `REPLY` | Responding to initiate engagement | Lead qualification, conversational grooming |
| `INSTALL_APP` | Installing application (APK, remote tool) | AnyDesk, malicious banking trojan APK |
| `DOWNLOAD_FILE`| Downloading attachment or PDF | Malicious payload, fake arrest warrant |
| `SHARE_OTP` | Providing one-time authorization code | Account takeover, unauthorized debit |
| `SHARE_CREDENTIAL` | Providing password, PIN, or CVV | Direct netbanking compromise |
| `SHARE_SCREEN` | Activating mobile/desktop screen sharing | Live monitoring of banking passwords/OTP |
| `MOVE_PLATFORM` | Switching from job/ad portal to chat app | Evading marketplace detection |
| `ADD_CONTACT` | Saving unknown number to contacts | WhatsApp profile visibility, messaging |
| `SEND_PAYMENT` | Direct UPI, IMPS, or bank transfer | Irreversible financial loss |
| `SCAN_QR` | Scanning QR code using UPI app | Fraudulent collect transaction |
| `APPROVE_UPI_REQUEST` | Accepting UPI collect prompt | Direct deduction from victim's bank balance |
| `INVEST_MORE` | Depositing larger funds for task progression| Investment / task fraud escalation |
| `PAY_FEE` | Paying customs, legal, or unfreezing fee | Advanced-fee / loss-aversion trap |
| `KEEP_SECRET` | Maintaining strict non-disclosure | Preventing third-party intervention |
| `DO_NOT_DISCONNECT` | Refusing to end voice/video connection | Coercive psychological confinement |
| `UNKNOWN` | Call to action could not be resolved | Fallback |

---

## 4. Critical Safety Tactics
The following 6 tactics represent immediate, active physical or financial threats:
- `ISOLATION`
- `SECRECY`
- `PAYMENT_PRESSURE`
- `CREDENTIAL_PRESSURE`
- `REMOTE_ACCESS_PRESSURE`
- `THREAT`

When any critical tactic is identified with confidence $\ge 0.85$, the engine triggers an immediate protective intervention signal regardless of general message classification.
