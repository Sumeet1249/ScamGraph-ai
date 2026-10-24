# Correlation Scoring & Decision Policies (Phase 3B)

## 1. Mathematical Scoring Formula

The overall correlation score is the sum of capped evidence groups:

$$S_{\text{raw}} = C_{\text{entity}} + C_{\text{behavioral}} + C_{\text{infrastructure}} + C_{\text{temporal}} + C_{\text{graph}}$$

Where each group contribution $C_g$ is:

$$C_g = \min\left(\text{Cap}_g, \text{RawScore}_g \times \frac{W_g}{W_{\text{base}}}\right)$$

### Multi-Signal Synergy Multiplier
If 3 or more independent evidence groups exhibit strong support ($\ge 50\%$ of their cap), a $1.15\times$ synergy bonus is applied:

$$S_{\text{boosted}} = \min(1.0, S_{\text{raw}} \times 1.15)$$

### Contradiction Penalty
If contradictory evidence is flagged:

$$S_{\text{final}} = \max\left(0.0, S_{\text{boosted}} \times (1.0 - \min(0.65, n_{\text{contradictions}} \times 0.40))\right)$$

---

## 2. Decision Tree & Hard Gates

```
               [ Pair Comparison ]
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
[ Only Generic Brands / CDNs? ]      [ Contradictions Detected? ]
       │                               │
      YES ──► NOT_RELATED (0.0)       YES ──► Apply 40-65% Penalty
       │                               │
       NO                             NO
       │                               │
       └───────────────┬───────────────┘
                       │
                       ▼
       [ Rare Payment ID + High DNA? ]
                       │
                      YES ──► STRONGLY_RELATED (>=0.85)
                       │
                      NO
                       │
       [ 100% Rotated IDs + High DNA? ]
                       │
                      YES ──► POSSIBLY_RELATED (0.50 - 0.64)
                       │
                      NO
                       │
                       ▼
            [ Threshold Scoring ]
             • >= 0.78: STRONGLY_RELATED
             • >= 0.62: LIKELY_RELATED_PATTERN
             • >= 0.45: POSSIBLY_RELATED
             • >= 0.28: WEAK_SIGNAL
             • <  0.28: NOT_RELATED
```
