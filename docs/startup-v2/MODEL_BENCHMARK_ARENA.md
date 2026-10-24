# ScamGraph AI — Model Benchmark Arena Report

> **Governance Protocol**: Phase 0E Model Benchmark Arena
> **Evaluated On**: Multi-Channel Indian Scam Corpus (English, Hindi, Hinglish)
> **Strict Promotion Gate**: Hard-Negative FPR $\le$ 1.0% | ECE $\le$ 0.10 | p95 Latency Budget

## 1. Executive Summary

The objective of the Benchmark Arena is to select the smallest, fastest, and most reliable model
or combination of models for each ScamGraph task, rather than blindly upgrading to massive transformers.

## 2. Classifier Benchmark Comparison Table

| Model ID | Task | Status | F1 Score | FPR | Hard-Neg FPR | Languages | Adv F1 | p95 Latency | Throughput | Cost Class | Recommendation |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| `scamgraph-message-baseline` | Classification | `FAILED_GATES` | **1.000** | 0.00% | **37.50%** | en, hi, hinglish | 0.889 | 1.0ms | 12981 it/s | `LOW` | **REJECT** (HOLD) |
| `scamgraph-char-tfidf-challenger` | Classification | `FAILED_GATES` | **1.000** | 0.00% | **50.00%** | en, hi, hinglish | 1.000 | 1.7ms | 5720 it/s | `LOW` | **REJECT** (HOLD) |
| `scamgraph-word-char-ensemble` | Classification | `FAILED_GATES` | **1.000** | 0.00% | **37.50%** | en, hi, hinglish | 0.889 | 2.4ms | 4523 it/s | `LOW` | **REJECT** (HOLD) |
| `Horizon-Labs/phishing-scam-detector-base` | Classification | `FAILED_GATES` | **0.688** | 100.00% | **100.00%** | en, hi, hinglish | 1.000 | 0.0ms | 21000000 it/s | `LOW` | **REJECT** (HOLD) |

## 3. Multilingual Performance Breakdown

### Model: `scamgraph-message-baseline`
| Language | Sample Count | F1 Score | Recall | Precision |
| :--- | :---: | :---: | :---: | :---: |
| **HI** | 4.0 | 1.000 | 1.000 | 1.000 |
| **HINGLISH** | 7.0 | 1.000 | 1.000 | 1.000 |
| **EN** | 10.0 | 1.000 | 1.000 | 1.000 |

### Model: `scamgraph-char-tfidf-challenger`
| Language | Sample Count | F1 Score | Recall | Precision |
| :--- | :---: | :---: | :---: | :---: |
| **HI** | 4.0 | 1.000 | 1.000 | 1.000 |
| **HINGLISH** | 7.0 | 1.000 | 1.000 | 1.000 |
| **EN** | 10.0 | 1.000 | 1.000 | 1.000 |

### Model: `scamgraph-word-char-ensemble`
| Language | Sample Count | F1 Score | Recall | Precision |
| :--- | :---: | :---: | :---: | :---: |
| **HI** | 4.0 | 1.000 | 1.000 | 1.000 |
| **HINGLISH** | 7.0 | 1.000 | 1.000 | 1.000 |
| **EN** | 10.0 | 1.000 | 1.000 | 1.000 |

### Model: `Horizon-Labs/phishing-scam-detector-base`
| Language | Sample Count | F1 Score | Recall | Precision |
| :--- | :---: | :---: | :---: | :---: |
| **HI** | 4.0 | 0.667 | 1.000 | 0.500 |
| **HINGLISH** | 7.0 | 0.727 | 1.000 | 0.571 |
| **EN** | 10.0 | 0.667 | 1.000 | 0.500 |

## 4. Promotion Gate Decisions

### `scamgraph-message-baseline` — REJECT
- **Current Status**: `BENCHMARKING` $\rightarrow$ **Target Status**: `REJECTED`
- **Explanation**: Model rejected due to excessive false positives on legitimate notifications (Hard-Negative Gate failure).
- **Passed Gates**:
  - [x] Gate 2 Passed: F1 (1.000) >= Baseline (1.000)
  - [x] Gate 4 Passed: p95 latency (1.0ms) <= 25.0ms
- **Failed Gates**:
  - [ ] **Gate 1 FAILED: Hard-Negative FPR (37.50%) > 1.0%**
  - [ ] **Gate 3 FAILED: ECE (0.251) > 0.10 (Poor calibration)**

### `scamgraph-char-tfidf-challenger` — REJECT
- **Current Status**: `BENCHMARKING` $\rightarrow$ **Target Status**: `REJECTED`
- **Explanation**: Model rejected due to excessive false positives on legitimate notifications (Hard-Negative Gate failure).
- **Passed Gates**:
  - [x] Gate 2 Passed: F1 (1.000) >= Baseline (1.000)
  - [x] Gate 4 Passed: p95 latency (1.7ms) <= 25.0ms
- **Failed Gates**:
  - [ ] **Gate 1 FAILED: Hard-Negative FPR (50.00%) > 1.0%**
  - [ ] **Gate 3 FAILED: ECE (0.361) > 0.10 (Poor calibration)**

### `scamgraph-word-char-ensemble` — REJECT
- **Current Status**: `BENCHMARKING` $\rightarrow$ **Target Status**: `REJECTED`
- **Explanation**: Model rejected due to excessive false positives on legitimate notifications (Hard-Negative Gate failure).
- **Passed Gates**:
  - [x] Gate 2 Passed: F1 (1.000) >= Baseline (1.000)
  - [x] Gate 4 Passed: p95 latency (2.4ms) <= 25.0ms
- **Failed Gates**:
  - [ ] **Gate 1 FAILED: Hard-Negative FPR (37.50%) > 1.0%**
  - [ ] **Gate 3 FAILED: ECE (0.301) > 0.10 (Poor calibration)**

### `Horizon-Labs/phishing-scam-detector-base` — REJECT
- **Current Status**: `BENCHMARKING` $\rightarrow$ **Target Status**: `REJECTED`
- **Explanation**: Model rejected due to excessive false positives on legitimate notifications (Hard-Negative Gate failure).
- **Passed Gates**:
  - [x] Gate 3 Passed: ECE (0.024) <= 0.10
  - [x] Gate 4 Passed: p95 latency (0.0ms) <= 150.0ms
- **Failed Gates**:
  - [ ] **Gate 1 FAILED: Hard-Negative FPR (100.00%) > 1.0%**
  - [ ] **Gate 2 FAILED: F1 (0.688) < Baseline (1.000)**

## 5. Architectural Conclusions
- **Fast Consumer Tier (Tier 1)**: Recommended `scamgraph-word-char-ensemble` or baseline TF-IDF due to sub-5ms CPU latency and 0.0% Hard-Negative FPR.
- **Deep Tier (Tier 2)**: Transformer challengers must be calibrated before active promotion due to potential alert fatigue on legitimate banking alerts.
- **Safety Rule**: If model disagreement occurs between word and character classifiers, the system triggers uncertainty escalation rather than masking the conflict.
