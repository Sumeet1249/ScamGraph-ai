# Evidence Preservation & Integrity Architecture (Phase 5B)

## Evidence Immutability & Provenance
Preserving untampered digital evidence is critical for bank disputes and police prosecution.

1. **Original vs Derived Evidence**:
   - `is_original: True` — The unedited original screenshot, transaction receipt PDF, or raw exported chat file.
   - `derived_from_id: Optional[str]` — Extracted OCR text, normalized transcript, or masked screenshot.
2. **Cryptographic Hashing**:
   - Every preserved evidentiary artifact is assigned a SHA-256 integrity hash upon upload.
   - Allows verification by investigating officers that the file was not altered post-submission.
3. **Sensitive Secret Masking**:
   - Passwords, OTPs, ATM PINs, and full Aadhaar numbers are never stored in raw form.
   - PII is masked (`******3210`, `n***@oksbi`) prior to case package generation.
