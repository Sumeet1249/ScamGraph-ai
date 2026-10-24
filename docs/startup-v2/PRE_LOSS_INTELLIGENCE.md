# ScamGraph AI — Pre-Loss Intelligence & Early Warning Architecture

## 1. The Startup Mandate: Interruption Over Post-Mortem
A security system that informs a user they have been scammed **after** they lose ₹50,000 has failed in its primary duty. ScamGraph’s core differentiator is **Pre-Loss Detection**:
> Delivering a calibrated, high-friction intervention candidate **before** money leaves the victim's account.

---

## 2. Monetization Boundary Definition
The **Monetization Boundary** is defined as the first chronological event where an encounter attempts to extract:
1. **Direct Funds**: UPI transfer, IMPS, RTGS, cash deposit, collect request approval.
2. **High-Impact Credentials**: OTPs, ATM PINs, netbanking passwords, CVVs.
3. **Remote Control**: Installing AnyDesk, QuickSupport, TeamViewer, or enabling screen sharing.

### Pre-Loss Validation Equation:
$$\text{Pre-Loss Warning Valid} \iff T_{\text{warning}} \le \min(T_{\text{boundary}}, T_{\text{loss}})$$

---

## 3. Intervention Classes
ScamGraph avoids binary "block vs allow" decisions. The Journey Engine generates graduated candidate intervention classes:

1. **`INFORMATION`**: Educational context when entering unfamiliar channels (e.g., migrating to Telegram).
2. **`CAUTION`**: Soft friction when unverified business accounts initiate contact.
3. **`WARNING`**: Explicit warning when multiple grooming stages match known templates (`MULTI_STAGE_SCAM_PATTERN`).
4. **`STRONG_WARNING`**: High friction requiring explicit acknowledgement when authority claims or secrecy demands occur.
5. **`IMMEDIATE_PAUSE`**: Urgent pause prompt triggered on direct `PAYMENT_RISK`, `CREDENTIAL_RISK`, or `REMOTE_ACCESS_RISK`.

---

## 4. Consumer vs Analyst Views

### Consumer View (`ConsumerJourneyView`)
- Zero technical internal scores or ML probabilities.
- Plain-language chronology:
  1. *"You received an unsolicited contact about work."*
  2. *"The conversation moved to Telegram."*
  3. *"A small test reward was offered."*
  4. *"You are now being pressured to deposit ₹5,000."*
- Plain-language rationale and specific protective advice.
- Visual progress meter state (Completed steps, Current step, Possible future steps).

### Analyst View (`AnalystJourneyView`)
- Complete forensic trace:
  - Sequence alignment scores across all 5 templates,
  - Stage observations with supporting evidence IDs and reason codes,
  - Event timestamps, sequence numbers, and channels,
  - Monetization boundary event ID and warning lead time ($\Delta T$),
  - Privacy-safe `JourneyFeatureVector` for cross-incident graph correlation.
