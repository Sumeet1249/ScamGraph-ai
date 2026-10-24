# Data License & Legal Assessment Report
**Phase 0D: India Data Platform**  
**Date:** October 24, 2026

---

## 1. External Dataset License Matrix

| Dataset ID | Upstream Provider / Repo | Declared License | Commercial Use Permitted? | Attribution Required? | Legal / Governance Risk | Recommended Status |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `scam-ham-india` | `anmolshrivastav/scam-ham-india` | **Apache-2.0** | **YES** | YES | LOW. Permissive open-source license; requires notice preservation. | `TRAINING_APPROVED` |
| `indian-scam-sms-synthetic-audited` | `Ridham115/indian-scam-sms-synthetic-audited` | **MIT** | **YES** | YES | LOW. Synthetic data; approved for augmentation and robustness. | `AUGMENTATION_APPROVED` |
| `scamgraph-canonical-journeys` | Internal ScamGraph Research | **Proprietary Internal** | **YES** | N/A | NONE. Owned internal asset. | `SCENARIO_APPROVED` |
| `sidzzz07-scamshield-dataset` | `sidzzz07/scamshield-dataset` | **Unspecified Community** | **UNKNOWN** | UNKNOWN | **HIGH**. Dataset card omits explicit license header. Training commercial enterprise models on unvetted community data creates copyright exposure. | **UNDER_REVIEW / LEGAL REVIEW REQUIRED** |
| `rishia2220-icfd-31k` | `rishia2220/icfd-31k` | **CC-BY-NC-4.0** | **NO** (Non-commercial only) | YES | **HIGH for Commercial Prod**. CC-BY-NC forbids commercial deployment. Permitted strictly for offline academic research, bench design, and synthetic dialogue study. | **BENCHMARK_ONLY** |
| `bolewara-hinglish-scam-text-dataset` | `bolewara/hinglish-scam-text-dataset` | **MIT** | **YES** | YES | LOW. Permissive MIT license. Suitable for Hinglish robustness benchmark. | `TRAINING_CANDIDATE` |

---

## 2. Policy: Commercial Derivative Models

> [!CAUTION]
> Models trained on datasets with Non-Commercial (`-NC`) clauses (such as `CC-BY-NC-4.0` in ICFD-31k) may inherit non-commercial encumbrance. Therefore, **ICFD-31k is approved strictly as a benchmark and synthetic scenario evaluation suite**, and must NOT be used directly to train commercial enterprise weights without explicit re-licensing from the author.
