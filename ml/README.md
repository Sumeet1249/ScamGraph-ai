# ml — Machine Learning & Embeddings

## Overview
Machine learning models, pipelines, and evaluation utilities for ScamGraph AI:
- **Multilingual Embeddings**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` for cross-lingual scam message understanding (Hindi, Hinglish, English, etc.).
- **Signal Classifiers**: Lightweight scikit-learn models for urgency detection, psychological coercion, and impersonation detection.
- **Model Checkpoints**: Directory storage for serialized weights and vector projections (managed via `.gitignore`).
- **Evaluation Notebooks & Scripts**: Validation benchmarks against annotated scam datasets.
