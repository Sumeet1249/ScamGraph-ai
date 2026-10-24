# Multimodal Evaluation Protocols & Metrics

## 1. Ground Truth Benchmark Sets
ScamGraph maintains independent evaluation sets across all supported modalities:
- **Screenshot Benchmark**: WhatsApp chat screenshots, Hindi digital arrest notices, SMS captures, and legitimate bank warnings.
- **QR Benchmark**: Person-to-person UPI QRs, merchant QRs, malformed QRs, and rotated low-resolution codes.
- **Audio Benchmark**: Phone-call compressed audio in English, Hindi, Hinglish, and Bengali, covering digital arrest calls and legitimate banking support inquiries.

## 2. Component-Level Metrics
Rather than solely evaluating end-to-end risk scores, each stage is measured independently:
- **OCR Quality**: Character Error Rate (CER), Word Error Rate (WER), token-level confidence calibration.
- **QR Decoding**: Payload parse accuracy, UPI VPA extraction recall, false auto-execution rate ($0\%$).
- **ASR & Tactic Extraction**: Segment timestamp precision, tactic classification F1, protective negation distinction rate ($100\%$).
- **Pre-Loss Detection Rate (PLDR)**: Anti-leakage compliance ensuring post-loss payment receipts are never credited as pre-loss warnings.
