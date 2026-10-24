# ScamGraph AI — Entity Trust Model & Reputation Decay

> **Document Version**: 2.0.0  
> **Status**: APPROVED  
> **Phase**: 1A — Trust Intelligence & Multi-Dimensional Reputation  

---

## 1. The Multi-Dimensional Trust Philosophy

A single static numeric score (e.g. *"UPI Score = 87"*) is dangerous and misleading:
- A legitimate business account whose details were spoofed in 1 phishing SMS would be permanently blacklisted.
- An attacker using a newly created UPI ID would be marked "safe" merely because it has 0 previous reports.

ScamGraph computes an **evidence-backed, time-decayed Trust Assessment** considering:
1. **Source Reliability**: Sovereign / banking feeds carry higher weight than unvetted crowdsourced reports.
2. **Temporal Decay**: Weak observations from 2 years ago carry significantly less weight than observations from yesterday.
3. **Observation Burst**: A sudden spike of reports across independent incidents within 48 hours indicates active campaign velocity.
4. **Counter-Evidence**: Legitimate salary credits, utility receipts, and merchant transactions counterbalance reports.

---

## 2. Source Reliability Weights

| Source Tier | Weight ($w_s$) | Criteria |
| :--- | :---: | :--- |
| **`AUTHORITATIVE`** | `1.00` | Sovereign directories (RBI, DoT, I4C, NIC, CERT-In, verified banks) |
| **`HIGH`** | `0.80` | Certified security researchers, verified analyst investigations, honeypots |
| **`MEDIUM`** | `0.50` | Corroborated telemetry, multi-signal algorithmic extractions |
| **`LOW`** | `0.20` | Single uncorroborated crowdsourced user report |
| **`UNKNOWN`** | `0.10` | Unvetted third-party web scrapes |

---

## 3. Temporal Decay Formulation (Half-Life Decay)

Older observations decay exponentially:
$$w_{\text{time}}(t) = 2^{-\frac{\Delta t}{T_{\text{half}}}}$$

Where:
- $\Delta t$ = Age of observation in days.
- $T_{\text{half}}$ = 180 days (configurable half-life).
- Min floor = $0.05$ (historical observations never completely disappear).

---

## 4. Trust Level Hierarchy

```
[Authoritative Verification]
       │
       ├── Verified Sovereign / Bank Portal  ─────────>  KNOWN_LEGITIMATE
       │
[Reputation & Evidence Assessment]
       │
       ├── Counter-Evidence > Supporting Evidence ────>  LIKELY_LEGITIMATE
       │
       ├── No Prior Sightings (New Identifier) ───────>  UNKNOWN
       │
       ├── 1 Weak Sighting / Low Confidence ──────────>  CAUTION
       │
       ├── Multi-Incident Corroboration ──────────────>  SUSPICIOUS
       │
       ├── Burst Velocity + Multi-Evidence ───────────>  HIGH_RISK
       │
[Dispute / Review Governance]
       │
       └── Active Governance Dispute ─────────────────>  DISPUTED
```

---

## 5. Separation: Entity Reputation vs Incident Risk

> [!IMPORTANT]
> **A newly created identifier used in an imminent threat has HIGH Incident Risk but LOW/UNKNOWN Entity Reputation.**

- **Incident Risk**: The immediate financial or emotional harm posed by the ongoing interaction (e.g., urgency, threat of arrest, request for Rs 50,000).
- **Entity Reputation**: The historical track record and corroboration of the specific identifier across all known incidents.

Consumer advice synthesizes both:
> *"Risk: HIGH. Why: Authority impersonation + urgent payment demand. Recipient: UNKNOWN (First observed UPI handle). Recommendation: Do not pay until independently verified."*
