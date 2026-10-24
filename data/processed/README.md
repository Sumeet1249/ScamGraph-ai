# Processed Datasets (`data/processed/`)

## Intended Purpose
Contains normalized, PII-sanitized, and deduplicated datasets structured as `ScamGraphRecordV2` representations.

## Rules
1. All records must contain valid `LanguageMetadata`, `QualityMetadata`, and `SplitMetadata`.
2. All PII (phones, emails, UPI VPAs, bank accounts) must be replaced with their masked presentation copies and deterministic canonical hashes.
3. Split assignments (`TRAIN`, `VALIDATION`, `TEST`) must be deterministically partitioned using template and campaign grouping to eliminate split leakage.
