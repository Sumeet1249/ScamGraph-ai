# SCAMGRAPH AI — TRIPARTITE RISK CALIBRATION SPECIFICATION (PHASE 4A)
## Risk, Confidence & Urgency Formulation and Calibration

### 1. The Tripartite Independence Principle

Single-score fraud detectors suffer from the **Confidence-Risk Conflation Bug**:
- A single score of `0.45` could mean "We are 99% confident this message has a low scam probability of 45%," OR "We have almost zero data and guessed 45%."
- A high-urgency benign message (e.g., flight gate closing) might score high on urgency detectors, while a slow-drip romance scam might score zero on urgency detectors despite critical risk.

ScamGraph isolates three orthogonal axes:
1. **Risk ($R \in [0.0, 1.0]$)**: "What is the expected loss / severity of malice if this proceeds unchecked?"
2. **Confidence ($C \in [0.0, 1.0]$)**: "How comprehensive and corroborative is the evidence supporting this assessment?"
3. **Urgency ($U \in [0.0, 1.0]$)**: "How immediately must action be taken to prevent irreversible harm?"

---

### 2. Dimension Weights and Signal Contributions

Configured in `config/decision.yaml`:

| Dimension Key | Base Weight ($w_d$) | Evaluates Subsystem | Primary Feature Inputs |
|---|---|---|---|
| `message_ml` | 0.15 | Fast NLP / LLM classifiers | Text spam/phishing probability, token perplexity |
| `url_intelligence` | 0.15 | Domain & URL Scanner | Domain age, brand typosquatting, blacklist match |
| `entity_trust` | 0.20 | Entity Intelligence V2 | VPA impersonation, burner mobile, mule bank token |
| `tactic_engine` | 0.15 | Social Engineering Engine | Urgency/fear tactics, isolation, fake authority |
| `journey_stage` | 0.15 | Journey Engine V1 | Temporal stage (`PAYMENT_REQUEST`, `CREDENTIAL_HARVEST`) |
| `scam_dna` | 0.10 | ScamDNA V3 | Structural/behavioral vector similarity to known templates |
| `campaign_outbreak` | 0.10 | Campaign & Radar V2 | Outbreak velocity, multi-victim cluster membership |

**Total Configured Weights**: $1.00$.

---

### 3. Confidence Calibration & Uncertainty Penalties

Confidence starts from the signal quality of evaluated dimensions and scales with multi-channel corroboration, penalized by missing intelligence:

$$C_{\text{base}} = \frac{1}{|D_{\text{evaluated}}|} \sum_{d \in D_{\text{evaluated}}} c_d$$

$$\text{Corroboration Bonus} = \min(0.20, (|D_{\text{evaluated}}| - 1) \times 0.05)$$

$$\text{Uncertainty Penalty} = (7 - |D_{\text{evaluated}}|) \times 0.08$$

$$C = \text{clamp}(C_{\text{base}} + \text{Bonus} - \text{Penalty}, 0.05, 0.99)$$

**Example**:
- If only an SMS text is submitted (1 evaluated dimension out of 7):
  - Base confidence = 0.85
  - Corroboration bonus = 0.0
  - Penalty = $6 \times 0.08 = 0.48$
  - Final confidence = $0.85 - 0.48 = 0.37 \implies$ Band: `LOW`. The user is warned not to rely purely on text analysis without checking the phone number or link.
- If text, URL, phone number, and UPI VPA are all evaluated (4 dimensions):
  - Corroboration bonus = $3 \times 0.05 = 0.15$
  - Penalty = $3 \times 0.08 = 0.24$
  - Final confidence = $0.88 + 0.15 - 0.24 = 0.79 \implies$ Band: `HIGH`.

---

### 4. Urgency Calibration & Journey Pre-Loss Escalation

Urgency measures the time-to-loss horizon. It combines explicit tactic pressure with temporal journey progression:

$$U = \text{clamp}(0.40 \cdot U_{\text{tactic}} + 0.40 \cdot M_{\text{stage}} + 0.20 \cdot U_{\text{campaign}}, 0.0, 1.0)$$

Stage Multipliers ($M_{\text{stage}}$):
- `APPROACH` / `INITIAL_CONTACT`: 0.15
- `RAPPORT_BUILDING`: 0.25
- `ISOLATION`: 0.45
- `CREDENTIAL_HARVEST`: 0.75
- `PAYMENT_REQUEST`: 0.90
- `PAYMENT_INTENT`: 0.95
- `EXTORTION` / `LOSS_CONFIRMATION`: 0.85

---

### 5. Tripartite Bands

| Range | Risk Band | Confidence Band | Urgency Band |
|---|---|---|---|
| `[0.00, 0.20)` | `VERY_LOW` | `VERY_LOW` | `VERY_LOW` |
| `[0.20, 0.45)` | `LOW` | `LOW` | `LOW` |
| `[0.45, 0.65)` | `MODERATE` | `MODERATE` | `MODERATE` |
| `[0.65, 0.85)` | `HIGH` | `HIGH` | `HIGH` |
| `[0.85, 1.00]` | `CRITICAL` | `CRITICAL` | `CRITICAL` |
