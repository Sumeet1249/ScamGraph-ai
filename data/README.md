# data — Datasets & Seed Scenarios

## Overview
Stores seed datasets, sample scam journeys, and testing fixtures:
- `scenarios/`: Annotated multi-stage scam journeys (e.g. Electricity bill fraud, KYC suspension, Work-from-Home task scam) for integration testing and live demonstrations.
- `seeds/`: Initial campaign templates and vector clusters for bootstrapping `pgvector`.
- `synthetic/`: Generated adversarial and benign communication samples to test the `INSUFFICIENT_EVIDENCE` fallback mechanism.

> **Note**: Database volumes (`pgdata`, `neo4jdata`) and large training sets are excluded via `.gitignore`.
