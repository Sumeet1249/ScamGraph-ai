# External Data Source Catalog
**Phase 0D: India Data Platform**  
**Date:** October 24, 2026

---

## 1. Catalog of Evaluated External Datasets

### 1. `scam-ham-india`
- **URL**: [https://huggingface.co/datasets/anmolshrivastav/scam-ham-india](https://huggingface.co/datasets/anmolshrivastav/scam-ham-india)
- **Description**: 2,272 English SMS messages with Indian keywords (KYC, OTP, Aadhaar, UPI).
- **Provenance**: `PUBLIC_MIXED` (Contains both real SMS and template variants).
- **ScamGraph Use**: Baseline model training & regression evaluation.
- **Status**: `NORMALIZED` / `ACTIVE_BASELINE`.

### 2. `indian-scam-sms-synthetic-audited`
- **URL**: [https://huggingface.co/datasets/Ridham115/indian-scam-sms-synthetic-audited](https://huggingface.co/datasets/Ridham115/indian-scam-sms-synthetic-audited)
- **Description**: 1,580 synthetic Hinglish and English SMS messages audited by humans.
- **Provenance**: `SYNTHETIC_LLM`.
- **ScamGraph Use**: Multilingual robustness and code-mixed stress-testing.
- **Status**: `NORMALIZED` / `AUGMENTATION_ONLY`.

### 3. `scamshield-dataset` (Candidate)
- **URL**: [https://huggingface.co/datasets/sidzzz07/scamshield-dataset](https://huggingface.co/datasets/sidzzz07/scamshield-dataset)
- **Description**: Claimed 85,000+ multilingual English/Hindi/Hinglish spam and scam samples.
- **Provenance**: `PUBLIC_MIXED`.
- **ScamGraph Use**: High-volume candidate for future multilingual transformer training.
- **Status**: `UNDER_REVIEW` (Awaiting license clarification and template deduplication).

### 4. `icfd-31k` (Candidate)
- **URL**: [https://huggingface.co/datasets/rishia2220/icfd-31k](https://huggingface.co/datasets/rishia2220/icfd-31k)
- **Description**: 31,000 synthetic multi-turn fraud dialogues with >1.1M streaming chunks.
- **Provenance**: `SYNTHETIC_LLM`.
- **ScamGraph Use**: Conversation intelligence, streaming speech detection, and Warning Lead Time benchmark simulation.
- **Status**: `BENCHMARK_ONLY` (Prohibited from real-world gold evaluations).

### 5. `hinglish-scam-text-dataset` (Candidate)
- **URL**: [https://huggingface.co/datasets/bolewara/hinglish-scam-text-dataset](https://huggingface.co/datasets/bolewara/hinglish-scam-text-dataset)
- **Description**: 3,787 messages with a specific subset written in colloquial Romanized Hinglish.
- **Provenance**: `PUBLIC_MIXED`.
- **ScamGraph Use**: Code-mixed Hinglish evaluation.
- **Status**: `TRAINING_CANDIDATE`.
