# ScamGraph AI — Persistent Workspace Rules

Before implementing ANY task on ScamGraph AI:

1. Read `docs/ARCHITECTURE.md`.
2. Read `docs/ARCHITECTURE_RULES.md`.
3. Read `docs/DATA_MODEL.md`.
4. Read `docs/INTEGRATION_PLAN.md`.
5. Read `docs/REFERENCE_ANALYSIS.md` when external projects are relevant.

## Core Domain Rules
- **LLMs generate evidence, not verdicts.**
- **TinyFish collects observable web evidence**, never asked if a site is a scam.
- **Risk and confidence are separate orthogonal values.**
- **All decisions require reason codes** linking back to specific Evidence IDs.
- **Missing evidence reduces confidence**, it does not silently become safe.
- **The system must support `INSUFFICIENT_EVIDENCE`.**
- **Never fabricate threat-intelligence data.**
- **Never store or mock real banking credentials, passwords, or live OTPs.**
- **Never automatically block a payment unilaterally.**
- **Cross-user demo relationships must use synthetic/pseudonymous data.**
- **Prefer deterministic/explainable methods before complex ML.**
- **Do not add GNNs until the baseline graph system works.**
- **Do not add a dependency if existing dependencies solve the problem.**
- **Never refactor working unrelated modules unless explicitly requested.**
