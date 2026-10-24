# ScamGraph AI — Dataset Inventory & Data Provenance
**Phase 0A: Baseline Audit Artifact**  
**Date:** October 24, 2026

---

## 1. Dataset Inventory

| Dataset ID | Name | Source / Repo | Local Path | Row Count | Languages | Provenance Type | License | Intended Use | Known Limitations & Leakage Concerns | Recommended Action |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| `scam-ham-india` | Scam/Ham India Dataset | Hugging Face (`anmolshrivastav/scam-ham-india`) | Downloaded via script / cached | 2,272 | English, Indian English | Mixed (Real SMS + Synthetic variants) | Apache-2.0 | Baseline Indian scam SMS classification | Contains template redundancy where identical messages with only OTP/names changed appear in train and test sets. Weak labels. | Audit split boundaries; deduplicate templates before benchmark evaluations. |
| `indian-scam-sms-synthetic-audited` | Indian Scam SMS Synthetic Audited | Hugging Face (`Ridham115/indian-scam-sms-synthetic-audited`) | Downloaded via script | 1,580 | Hinglish, Hindi, English | Synthetic with human audit decisions | MIT | Robustness testing for multilingual/code-mixed text | Synthetic generator artifacts. Requires filtering out rejected/unreviewed entries. Risk of synthetic template leakage across splits. | Use exclusively as an out-of-distribution evaluation set; do not mix into training set. |
| `scamgraph-canonical-journeys` | ScamGraph Fraud Journey Scenarios | Internal curated | `data/scenarios/*.json` | 35 | English, Hinglish | Synthetic | Proprietary Internal | Multi-stage scam journey validation (KYC, electricity, job scam) | Hand-crafted progression stages; small sample size unsuitable for statistical generalization. | Keep for unit and integration regression tests. |

---

## 2. Directory Population Audit

- `data/raw/`: **Empty** (`.gitkeep` only). No raw raw datasets stored locally in version control.
- `data/processed/`: **Empty** (`.gitkeep` only). Cleaned/split parquet or CSV files are generated dynamically or absent.
- `data/synthetic/`: **Empty** (`.gitkeep` only).
- `data/patterns/`: **Active**. Contains 5 high-quality YAML pattern files (`digital_arrest.yaml`, `fake_support_refund.yaml`, `investment_scam.yaml`, `job_task_scam.yaml`, `kyc_impersonation.yaml`).
- `data/scenarios/`: **Active**. Contains 7 JSON scenarios and 1 comprehensive YAML simulator scenario (`simulator_electricity_bill.yaml`).
- `data/registry/`: **Active**. Contains `datasets.yaml` documenting repository data sources.
