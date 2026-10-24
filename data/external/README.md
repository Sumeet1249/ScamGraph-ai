# External Data Directory (`data/external/`)

## Staging & Normalization Structure
- `data/external/manifests/`: Cryptographic checksums and provenance manifests for retrieved datasets.
- `data/external/staging/`: Raw downloaded archives (gitignored).
- `data/external/normalized/`: Partitioned and PII-masked `ScamGraphRecordV2` JSON/Parquet outputs.

## Governance
1. Datasets must be registered in `data/registry/datasets.yaml` or `candidates.yaml` before retrieval.
2. Raw archives in `staging/` must NEVER be committed to Git.
