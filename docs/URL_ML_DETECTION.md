# URL Machine Learning Detection (Step 27)

## Overview

The **URL Risk Machine Learning Detector** is a specialized tabular ML classification layer designed to evaluate suspect URLs in real-time. It operates as part of ScamGraph AI's Infrastructure & URL Safety pipeline, complementing static heuristics, DNS resolution, RDAP queries, and TinyFish live DOM extraction.

Its primary purpose is to distinguish between **high-risk deceptive phishing infrastructure** (typosquatting, brand spoofing, high-abuse TLDs, DGA hostnames, raw IP hosts) and **legitimate high-traffic enterprise portals** without introducing alert fatigue or high latency.

---

## 1. Feature Representation

The `URLFeatureExtractor` extracts a comprehensive 19-dimensional feature vector across structural, lexical, and behavioral dimensions:

| Feature | Type | Description |
|---|---|---|
| `has_ip_host` | Boolean | True if destination is a raw IPv4/IPv6 address instead of a domain name. |
| `suspicious_tld` | Boolean | Matches known high-abuse extensions (`.xyz`, `.top`, `.tk`, `.online`, `.site`, etc.). |
| `brand_in_subdomain_or_path` | Boolean | Detects targeted brand names (e.g. SBI, HDFC, ICICI, Tata Power) placed in subdomains, path segments, or hyphenated domains of untrusted registrars. |
| `suspicious_keyword_count` | Integer | Density of social engineering tokens (`login`, `verify`, `kyc`, `update`, `otp`, `claim`). |
| `entropy_excess` | Float | Shannon entropy of the hostname in excess of natural English domain baseline ($> 3.8$ bits), catching DGA/randomized domains. |
| `subdomain_count` | Integer | Subdomain hierarchy depth (excluding standard `www`). |
| `hyphen_count` | Integer | Hyphen count in the full URL string. |
| `non_https` | Boolean | True if unencrypted `http` scheme is used. |
| `https_discount` | Boolean | Protective discount factor for valid HTTPS destinations. |
| `has_punycode` | Boolean | True if homograph attack indicator `xn--` is present in hostname. |
| `digit_ratio` | Float | Ratio of numeric digits to URL length. |
| `encoded_char_count` | Integer | Hexadecimal `%xx` percent-encoded obfuscation count. |

---

## 2. Model Architecture & Calibration

The classifier (`URLRiskClassifier`) uses a calibrated logistic ensemble:

$$z = \text{bias} + \sum_{i=1}^{n} w_i \times x_i$$

$$P(\text{malicious}) = \frac{1}{1 + e^{-z}}$$

### Configuration (`config/url_ml.yaml`):
```yaml
thresholds:
  benign_threshold: 0.35
  suspicious_threshold: 0.65
  high_risk_threshold: 0.85

feature_weights:
  has_ip_host: 3.0
  suspicious_tld: 2.2
  brand_in_subdomain_or_path: 2.5
  suspicious_keyword_count: 0.8
  entropy_excess: 1.2
  subdomain_count: 0.5
  hyphen_count: 0.3
  non_https: 0.8
  https_discount: -1.2
  encoded_char_count: 0.7
  punycode: 2.0
  bias: -2.5
```

### Risk Tiers:
- **`MALICIOUS`** ($P \ge 0.85$): Emits critical `ML_HIGH_RISK_URL_DETECTED` signal.
- **`HIGH_RISK`** ($0.65 \le P < 0.85$): Emits high `ML_HIGH_RISK_URL_DETECTED` signal.
- **`SUSPICIOUS`** ($0.35 \le P < 0.65$): Emits medium `ML_SUSPICIOUS_URL_DETECTED` signal.
- **`BENIGN`** ($P < 0.35$): Suppressed from alerts to prevent alert fatigue.

---

## 3. Mathematical Explainability

Every prediction outputs explicit feature contributions:
$$\text{contribution}_i = w_i \times x_i$$

Example Explainable Output:
```json
{
  "raw_url": "http://sbi-kyc-verify-update.xyz/login.php?user=123",
  "malicious_probability": 0.9994,
  "risk_tier": "MALICIOUS",
  "is_malicious": true,
  "confidence": 0.98,
  "top_risk_factors": [
    "Targeted brand identity spoofed in subdomain or path (+2.50)",
    "High-abuse top-level domain extension (.xyz, .top, etc.) (+2.20)",
    "Presence of credential/phishing keywords (verify, login, kyc) (+2.40)"
  ],
  "explanation": "URL evaluated with 99.9% malicious likelihood (MALICIOUS). Primary risk drivers: Targeted brand identity spoofed in subdomain or path (+2.50); High-abuse top-level domain extension (.xyz, .top, etc.) (+2.20); Presence of credential/phishing keywords (verify, login, kyc) (+2.40)."
}
```

---

## 4. Performance & Integration

- **Inference Speed**: $< 1\text{ms}$ per URL ($> 1,000\text{ URLs/sec}$ on a single core).
- **Service Integration**: Embedded inside `URLInvestigationService.investigate_url(...)`, automatically attaching canonical `Evidence` and populating `result.ml_prediction`.
- **Evidence Signal Conversion**: `classifier.to_evidence_signal(incident_id, pred)` emits `EvidenceSignal(dimension=SignalDimension.URL, ...)` directly into the downstream Evidence Fusion Engine.

---

## 5. Test Suite

Unit tests in [tests/unit/test_url_ml_step27.py](file:///s:/ScamGraph-AI/tests/unit/test_url_ml_step27.py):
- Feature extraction accuracy across 19 dimensions.
- Phishing URL detection (SBI KYC phishing $\ge 99\%$).
- False-positive resistance (Google, OnlineSBI, HDFC Bank, Tata Power $\le 5\%$).
- Direct IP host and brand spoofing detection.
- Sub-millisecond latency benchmark.
