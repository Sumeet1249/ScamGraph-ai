# Raw Data Directory (`data/raw/`)

## Intended Purpose
This directory is intended solely for local cache or staging of raw, unmodified datasets as downloaded directly from authoritative upstream providers (e.g. Hugging Face, government portals, or certified telecom partners).

## Privacy & Governance Rules
1. **NO RAW USER PII**: Never commit unmasked, un-redacted personal data (phone numbers, Aadhaar numbers, personal emails, or private chat histories) to version control.
2. **REPRODUCIBLE INGESTION**: Raw data files should be populated via reproducible download scripts rather than ad-hoc file drops.
3. **CHECKSUMS & LINEAGE**: All datasets must have their cryptographic checksums (SHA-256) and source revisions pinned in `data/registry/datasets.yaml`.
4. **PROVENANCE ENFORCEMENT**: Raw datasets must be tagged with their truthful provenance type (`PUBLIC_REAL`, `PUBLIC_MIXED`, `SYNTHETIC_LLM`, etc.). Mixed datasets must NEVER be assumed 100% real without per-record provenance validation.
5. **ISOLATION FROM GOLD SET**: Raw training sets must never overlap with, pollute, or share records with `data/gold/`.
