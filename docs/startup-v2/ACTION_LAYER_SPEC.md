# SCAMGRAPH AI — ACTION LAYER SPECIFICATION (PHASE 4A)
## Definitive Operational Dispositions, Rules, and Partner Integration

### 1. Action Taxonomy and Semantics

The Action Layer translates the Tripartite state $(R, C, U)$ into one of seven clear operational decisions:

| Action Code | Name | Primary Target | Definition & Intent |
|---|---|---|---|
| `ALLOW` | Allow / Verified Benign | Consumer & Payment Gateway | Verified legitimate interaction or benign noise; no intervention needed. |
| `EDUCATE` | Educate / Awareness | Consumer | Low risk with mild indicators; highlight general hygiene without blocking. |
| `VERIFY_INDEPENDENTLY` | Verify Independently | Consumer | Ambiguous risk or low confidence; guide user to verify through official channels before acting. |
| `WARN` | Suspicious / Proceed with Caution | Consumer & Analyst | Moderate risk with sufficient confidence; explicit warning banner displayed. |
| `STRONG_WARNING` | Strong Warning / Likely Malicious | Consumer & Banking Shield | High risk; severe alert detailing known impersonation patterns. |
| `DELAY_PAYMENT` | Cooling-Off / Delay Payment | Banking App / UPI SDK | High risk + high urgency in pre-loss stage; impose 2-hour cooling-off delay on funds transfer. |
| `BLOCK_PRE_LOSS` | Automatic Block / Intercept | Gateway, Telco & App | Critical risk + high confidence or active campaign outbreak; block transaction or communication entirely. |

---

### 2. Decision Matrix & Precedence Rules

The engine applies rules in strict priority order:

1. **Rule 1: Active Campaign Outbreak Override**
   - **Condition**: Associated campaign status == `OUTBREAK` OR entity explicitly confirmed on active campaign infrastructure.
   - **Decision**: `BLOCK_PRE_LOSS`
   - **Rationale**: A confirmed circulating syndicate outbreak requires immediate circuit breaking.

2. **Rule 2: Pre-Loss Imminent Transfer (`DELAY_PAYMENT`)**
   - **Condition**: $R \ge 0.65$ AND $U \ge 0.60$ AND journey stage $\in \{\text{PAYMENT\_REQUEST}, \text{PAYMENT\_INTENT}, \text{CREDENTIAL\_HARVEST}\}$
   - **Decision**: `DELAY_PAYMENT`
   - **Rationale**: When social-engineering pressure is peaked right before payment, enforcing a 120-minute friction window allows adrenaline to fade and victims to consult family or bank officials.

3. **Rule 3: Critical Malice Intercept (`BLOCK_PRE_LOSS`)**
   - **Condition**: $R \ge 0.85$ AND $C \ge 0.70$ AND $U \ge 0.70$
   - **Decision**: `BLOCK_PRE_LOSS`

4. **Rule 4: Strong Warning**
   - **Condition**: $R \ge 0.65$ AND $C \ge 0.45$
   - **Decision**: `STRONG_WARNING`

5. **Rule 5: Moderate Warning**
   - **Condition**: $R \ge 0.45$ AND $C \ge 0.35$
   - **Decision**: `WARN`

6. **Rule 6: Ambiguous / Low Confidence Verification**
   - **Condition**: $R \ge 0.30$ OR $C < 0.40$
   - **Decision**: `VERIFY_INDEPENDENTLY`

7. **Rule 7: Low Risk Education**
   - **Condition**: $R \ge 0.15$
   - **Decision**: `EDUCATE`

8. **Default Fallback**:
   - **Decision**: `ALLOW`

---

### 3. Cooling-Off Window Specification

For `DELAY_PAYMENT`, ScamGraph recommends a configurable cooling-off window:
- **Default Window**: 120 minutes (2 hours).
- **Extreme Pressure Window**: 240 minutes (4 hours) if Tactic Score $\ge 0.85$.
- **Partner Action**: Banking SDK delays the UPI "Approve Payment" button, displaying the countdown timer and emergency bank contact hotline (`1930`).

---

### 4. Consumer Headline & Explanation Guidelines

To protect consumer trust and comprehension:
- **Prohibited in Consumer Outputs**:
  - Raw decimal floats (e.g., "0.8721").
  - Internal technical IDs (e.g., `ent_vpa_89231f`, `cluster_camp_01`).
  - Jargon (e.g., "Vector embedding cosine similarity exceeded 0.82").
- **Required in Consumer Outputs**:
  - Plain language summary of what is happening.
  - Clear next steps ("Do not click the link", "Call your bank's official number from their website").
  - National cybercrime helpline reference (`1930`).
