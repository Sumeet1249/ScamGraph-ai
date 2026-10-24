# ScamGraph AI — Model Inventory
**Phase 0A: Baseline Audit Artifact**  
**Date:** October 24, 2026

---

## 1. Machine Learning & Heuristic Model Inventory

| Component Name | File Path | Model Type | Task | Input | Output | Training Source | Stored Artifacts | Runtime Dependency | Status | Recommended Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **Message Classifier** | `ml/message/baseline.py`, `ml/message/service.py` | TF-IDF + Logistic Regression | Scam vs Ham SMS Classification | Raw message string | Scam probability (0.0 - 1.0) + Class label | `anmolshrivastav/scam-ham-india` | `model.joblib` (40KB), `vectorizer.joblib` (190KB) | `scikit-learn`, `joblib` | `PRODUCTION_CANDIDATE` | Retain as fast baseline model. Add multilingual benchmarking. |
| **URL Risk Classifier** | `ml/url/classifier.py` | Configured Linear Heuristic Scorer | URL Threat Tiering | Extracted URL features (entropy, IP, TLD, length) | Malicious probability + Risk tier | None (Hand-crafted YAML weights in `config/url_ml.yaml`) | None | `pydantic`, `pyyaml` | `BASELINE` (Heuristic) | Relabel as Heuristic Rules Engine. Plan future dataset training. |
| **Payment Risk Classifier** | `ml/payment/classifier.py` | Configured Linear Logistic Scorer | UPI Payment Anomaly Scoring | VPA features (impersonation, entropy, unverified handle) | Malicious probability + Risk tier | None (Hand-crafted YAML weights in `config/payment_ml.yaml`) | None | `pyyaml`, `math` | `BASELINE` (Heuristic) | Relabel as Rule-Based Heuristic Scorer. Remove false ML label. |
| **Semantic Vector Encoder** | `ml/embeddings/encoder.py` | SentenceTransformer (`intfloat/multilingual-e5-small` / `BAAI/bge-m3`) | Paraphrase and semantic vector embedding | Unstructured message / journey text | 384-dim or 1024-dim dense float vector | Hugging Face pretrained models | Downloaded model cache | `sentence-transformers`, `torch` | `CANDIDATE` | Keep `multilingual-e5-small` as CPU default. Maintain in-memory LRU cache. |
| **Campaign Clusterer** | `services/graph-engine/campaigns/clusterer.py` | DBSCAN Clustering | Group related scam incidents into emerging campaigns | High-dimensional embedding vectors | Cluster IDs + Campaign summaries | Dynamic incident stream | None | `scikit-learn` | `EXPERIMENTAL` | Transition from in-memory array clustering to incremental DB-backed clustering. |
| **Mule Account Classifier** | `services/mule_engine/model.py` | Logistic Heuristic Ensemble | Transaction ring / mule node detection | Transaction velocity, fan-in/fan-out graph metrics | Mule risk score (0.0 - 1.0) | Synthetic transaction graphs | `services/mule_engine/artifacts/` | `scikit-learn`, `numpy` | `EXPERIMENTAL` | Demote to enterprise backlog; keep code dormant. |
