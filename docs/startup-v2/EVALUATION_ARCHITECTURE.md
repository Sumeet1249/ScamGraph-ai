# Evaluation Architecture Specification
**Phase 0C: Technical Framework**  
**Date:** October 24, 2026

---

## 1. Modular Architecture

The ScamGraph evaluation framework lives under `ml/evaluation/` with clear separation of responsibilities:

```
ml/evaluation/
├── __init__.py          # Canonical exports
├── runner.py            # EvaluationOrchestrator running end-to-end benchmark loops
├── metrics.py           # Core binary classification + Pre-Loss Detection Rate
├── splits.py            # Leakage-safe partitioners (Group, Template, Campaign, Temporal)
├── leakage.py           # LeakageAuditor detecting exact, near, and template overlaps
├── calibration.py       # Probability calibration, ECE, and reliability buckets
├── robustness.py        # Non-destructive defensive adversarial perturbations
├── multilingual.py      # Stratified evaluation by language, family, and provenance
├── adapters.py          # Model challenger interface (ModelAdapter) & latency profiling
└── cli.py               # Developer command-line benchmark runner
```

---

## 2. Leakage-Safe Splitting Policies

1. **`GROUP_BY_TEMPLATE`**:
   Abstracts entities into tokens (`<PHONE>`, `<URL>`, `<AMOUNT>`, `<BANK>`). All instances sharing the template are assigned to the same partition.
2. **`GROUP_BY_CAMPAIGN`**:
   Ensures threat campaign clusters never cross train/test boundaries.
3. **`SOURCE_HOLDOUT`**:
   Evaluates transferability across independent external datasets.
4. **`TEMPORAL`**:
   Evaluates historical training data against future chronologically occurring incidents.
