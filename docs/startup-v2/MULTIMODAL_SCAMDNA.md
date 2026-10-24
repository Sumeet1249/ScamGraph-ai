# Multimodal ScamDNA Specification

## 1. Modality-Invariant Behavioral Fingerprinting
Modality is an input transport format, not a behavioral identity. ScamDNA does not compute shallow scores like `screenshot_score` or `audio_score`. Instead, multimodal observations enrich canonical behavioral dimensions:
- **Semantic Vector**: Enriched from OCR text and ASR transcripts after Indic normalization.
- **Journey Vector**: Reconstructed stage sequences across all modalities (e.g., SMS contact $\to$ WhatsApp chat $\to$ Voice call $\to$ QR code $\to$ Payment).
- **Tactic Vector**: Cross-modal detection of psychological levers (`AUTHORITY`, `URGENCY`, `ISOLATION`, `SECRECY`).
- **Payment Vector**: UPI VPAs, payment amounts, and transaction rails extracted from receipts and QR payloads.
- **Infrastructure Vector**: Domains, IP hosts, APK links, and phone numbers discovered in OCR and audio.

This enables cross-modal similarity matching: an incident reported purely via text can match a campaign reported via voice calls and screenshots if their ScamDNA behavioral profiles align.
