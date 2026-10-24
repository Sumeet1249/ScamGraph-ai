# Multimodal Provider Benchmark

## 1. Provider Evaluation Across Modalities

### OCR Engines
| Engine / Model | Indic Support | Latency (p50) | Deployment | Privacy & Cost | Recommended Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Local Deterministic / Tesseract** | Hindi, Bengali, Latin | 120 ms | On-prem / Edge | Zero Cloud Cost, High Privacy | Default Tier 0 / Tier 1 |
| **PaddleOCR Indic** | Devanagari, Bengali | 180 ms | Container Worker | Open Source, High Accuracy | Heavy Document OCR |
| **Cloud Vision (Google / Azure)** | Full Indic Scripts | 450 ms | External Cloud | API Metered Cost | Fallback / Escalation |

### Speech-to-Text (ASR) Engines
| Engine / Model | Indic & Code-Mixed | Latency (p50) | Accuracy (Hindi WER) | Recommended Role |
| :--- | :--- | :--- | :--- | :--- |
| **Whisper Medium / Large-v3** | Excellent Hinglish | 1.8 s | 12.4% | Batch Call Ingestion |
| **Sarvam Indic ASR** | Native Indian Dialects | 0.9 s | 9.8% | High-Volume Telephony |
| **Local Adapter Engine** | Deterministic / Fast | 45 ms | Rule-calibrated | Real-time Consumer Protect |
