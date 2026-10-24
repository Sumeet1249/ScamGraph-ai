# SCAMGRAPH AI — CONTEXTUAL INTERVENTION ENGINE (PHASE 4B)
## Timely Pre-Loss Protection, Situational Context & Intervention Architecture

### 1. Philosophy: Risk Evaluation vs. Contextual Intervention

| Dimension | Risk Engine (Phase 4A) | Intervention Engine (Phase 4B) |
|---|---|---|
| **Primary Question** | "How dangerous is this interaction?" | "What protective action is appropriate right now?" |
| **Output Type** | Tripartite Scores ($R, C, U$) & Action Bands | Concrete Intervention Directive (`InterventionDecision`) |
| **Context Sensitivity** | Static or cumulative observable signals | Immediate temporal state (e.g. paying NOW vs. reading SMS yesterday) |
| **Friction Scale** | N/A (Analytical) | Progressive Friction Levels 0 through 6 |

---

### 2. Intervention Types & Progressive Friction

ScamGraph defines 14 categorical intervention types mapped across 7 progressive friction tiers:

| Friction Tier | Name | Target Interventions | User Experience |
|---|---|---|---|
| **Level 0** | `NONE` | `NO_ACTION` | Silent monitoring; zero user interruption. |
| **Level 1** | `PASSIVE` | `EDUCATE` | Subtle in-line advisory banner; non-blocking. |
| **Level 2** | `LIGHT` | `CAUTION`, `VERIFY_INDEPENDENTLY` | Dismissible caution notice; suggests independent check. |
| **Level 3** | `MODERATE` | `WARN`, `PAUSE_AND_VERIFY` | Interactive banner with verification action steps. |
| **Level 4** | `STRONG` | `STRONG_WARNING`, `DO_NOT_SHARE_CREDENTIALS`, `DO_NOT_SHARE_OTP`, `DO_NOT_INSTALL_REMOTE_ACCESS`, `TALK_TO_TRUSTED_PERSON` | Interruptive safety modal requiring explicit acknowledgment. |
| **Level 5** | `DELAY_PAYMENT` | `DELAY_PAYMENT`, `BREAK_CONTACT_AND_VERIFY` | Mandatory 120-minute cooling-off window on UPI/banking transfers. |
| **Level 6** | `EMERGENCY` | `EMERGENCY_RESPONSE` | Urgent post-loss recovery protocol (1930 / bank freeze prompt). |

---

### 3. Anti-Manipulation Interventions

1. **Digital Arrest & Anti-Isolation (`TALK_TO_TRUSTED_PERSON`)**:
   - *Trigger*: Authority or legal threats combined with secrecy or isolation.
   - *Mechanism*: Prominently urges victim to break communication with the suspect and consult a family member or independent police station.
2. **Credential & OTP Intercept (`DO_NOT_SHARE_OTP` / `DO_NOT_SHARE_CREDENTIALS`)**:
   - *Trigger*: Any request for OTP, PIN, password, or CVV.
   - *Mechanism*: Explains that banks and legitimate customer support never request authentication codes.
3. **Remote-Access Defense (`DO_NOT_INSTALL_REMOTE_ACCESS`)**:
   - *Trigger*: Demands to install screen-sharing software (AnyDesk, TeamViewer, RustDesk) or unknown APKs.
   - *Mechanism*: Instructs user to refuse installation and immediately disable internet connectivity if already installed.

---

### 4. Alert Fatigue Suppression & Escalation Logic

To prevent warning fatigue:
- Routine, repeated evaluations on identical evidence are suppressed to `PASSIVE`.
- Critical safety interventions (`EMERGENCY_RESPONSE`, `DELAY_PAYMENT`, `DO_NOT_SHARE_OTP`) are **never suppressed**.
- Alerts escalate immediately when situational context worsens:
  - Journey stage advances to `PAYMENT_REQUEST` or `CREDENTIAL_HARVEST`.
  - New coercive tactics appear.
  - Risk surges by $\ge 0.20$.
