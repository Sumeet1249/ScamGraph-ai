# ScamGraph India Gold Set Protocol
**Phase 0C: Benchmark Governance**  
**Date:** October 24, 2026

---

## 1. Governance Principles

The **ScamGraph India Gold Standard Set** represents the sacred, non-negotiable benchmark for evaluating fraud detection capability in Indian digital contexts.

### Strict Tenets
1. **Never Used for Training**: Gold data must NEVER enter training, fine-tuning, prompt engineering, or synthetic generation pipelines.
2. **Contamination Disqualification**: If any gold record is found in training data or hyperparameter optimization sets, it is immediately flagged as `CONTAMINATED` and purged from benchmark scoring.
3. **No Synthetic Shortcuts**: Synthetic samples (e.g. LLM-generated variations) are prohibited from the Gold Set.
4. **Human Multi-Review Ground Truth**: All gold annotations require consensus review from at least 2 independent human fraud analysts.

---

## 2. Target Composition

```
Total Target Size: 10,000 Verified Indian Telemetry Records
├── 50% Verified Real Scams (SMS, WhatsApp, Phishing links, UPI VPAs)
├── 30% Legitimate Banking, Utility, and Government Notifications
├── 10% Hard Negatives (legitimate alerts with scam-like urgency or keywords)
└── 10% Adversarial & Obfuscated Dialectical Variants
```

---

## 3. Directory Layout

- `data/gold/schema/`: Schema rules and annotation protocols.
- `data/gold/manifests/`: Versioned cryptographic manifests with checksums.
- `data/gold/private/`: Isolated, gitignored directory for confidential verified incident records.
