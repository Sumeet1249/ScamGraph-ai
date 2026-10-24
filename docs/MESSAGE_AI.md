# ScamGraph AI Message Intelligence (Step 21)

## 1. Overview & Constitutional Principles

The Message Intelligence layer provides linguistic signal extraction, semantic embedding representation, and scam classification for SMS, WhatsApp, and messaging payloads.

### Constitutional Rule 10 Compliance
**Message AI outputs structured evidence signals, NEVER an automated final fraud verdict.**
Single messages—no matter how suspicious—cannot autonomously block transactions or trigger intrusive interventions. Instead, Message Intelligence emits typed `EvidenceSignal` instances (`dimension=SignalDimension.SEMANTIC`) into the correlation engine for multi-modal convergence analysis.

---

## 2. Models & Evaluation Benchmark

### A. Baseline: TF-IDF + Logistic Regression
- **Vectorizer**: `TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)`
- **Classifier**: `LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000)`
- **Training Set**: 3,048 samples (partitioned with template-level isolation)
- **Test Set**: 809 samples (20.9% test split)
- **Performance**:
  - **Accuracy**: 95.67%
  - **Precision**: 94.84%
  - **Recall**: 95.11%
  - **F1 Score**: 94.98%
  - **False Positive Rate (FPR)**: **3.90%** (18 false positives on 461 negative samples)

### B. Transformer Baseline Reference: `anmolshrivastav/distilbert-scam-detector-india`
Evaluated on an identical 200-sample test partition:

| Metric | TF-IDF + Logistic Regression | DistilBERT Reference |
| :--- | :--- | :--- |
| **Accuracy** | **91.00%** | 55.50% |
| **Precision** | **86.79%** | 51.89% |
| **Recall** | 95.83% | **100.00%** |
| **F1 Score** | **0.9109** | 0.6833 |
| **False Positive Rate (FPR)** | **13.46%** | 85.58% |

> [!WARNING]
> The pretrained DistilBERT reference model triggers an **85.58% false-positive rate** on normal transactional and utility messages. Using it as a solitary detector would severely degrade the user experience and trigger massive alert fatigue. The TF-IDF + balanced Logistic Regression model serves as the primary detector, with embeddings provided by `SemanticEncoder` (E5/BGE-M3).

---

## 3. Extracted Semantic Signals

`MessageIntelligenceService` detects and extracts atomic linguistic markers:
1. `SCAM_MESSAGE_SEMANTIC_MATCH`: Classifier score exceeding confidence threshold (suppressed if routine transactional notification).
2. `URGENCY_PRESSURE_DETECTED`: Coercive deadlines (*"blocked within 2 hours"*, *"turant"*, *"jaldi"*).
3. `OFFICIAL_ENTITY_IMPERSONATION`: Recognized brand claims (SBI, HDFC, ICICI, PNB, Discom, TRAI, Police).
4. `SENSITIVE_CREDENTIAL_SOLICITATION`: OTP, PIN, CVV, or confidential netbanking requests.
5. `LEGITIMATE_TRANSACTION_NOTIFICATION` (*Counter-Evidence*): Routine credit/debit confirmation with absence of credential demands.

---

## 4. Architecture Artifacts

All training artifacts, configurations, and manifests are saved in `ml/message/artifacts/`:
- `model.joblib`: Serialized Logistic Regression model
- `vectorizer.joblib`: Serialized TF-IDF vectorizer
- `metrics.json`: Test split evaluation metrics
- `dataset_manifest.json`: Preprocessing stats and dataset distribution
- `model_metadata.json`: Architecture specs and intended scope
- `model_comparison.json`: Comparative benchmark vs transformer model
