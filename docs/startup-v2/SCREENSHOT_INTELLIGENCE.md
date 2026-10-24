# Screenshot Intelligence Specification

## 1. Scope & Ingestion
Screenshot intelligence extracts textual and layout evidence from chat logs (WhatsApp, Telegram, Signal), SMS screens, payment screens, social profiles, and fake documents without mutating or replacing the original image artifact.

## 2. Ingestion Flow
1. **Security & Integrity Gate**: Validate MIME type (`image/png`, `image/jpeg`, `image/webp`), verify magic bytes, check file size limits ($\le 15$ MB), and scan text against prompt injection patterns (`PROMPT_INJECTION_PATTERNS`).
2. **Deterministic & Vision OCR**: Compute structured `OCRResult` with bounding boxes, script tags, block layouts, and calibrated token confidence.
3. **Indic & Multilingual Normalization**: Seamlessly pipe extracted text into `LanguageIntelligenceService` (Prompt 17) for transliteration, code-mixed token unification, and Hindi/Hinglish handling.
4. **Entity & Tactic Derivation**:
   - Extract URLs, domains, phones, and UPI VPAs via canonical `EntityIntelligenceService`.
   - Extract manipulation tactics (`URGENCY`, `FEAR`, `ISOLATION`, `PAYMENT_PRESSURE`) with negation protection (*"Never share OTP"* $\to$ advisory, not `SHARE_OTP`).
5. **Lineage Preservation**: Every observation retains `lineage_parent_ids` pointing back to the root screenshot artifact.
