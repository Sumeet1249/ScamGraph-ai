# Source Inventory & Public Evidence Log

This document records the official public references, observed interface behaviors, published project documentation, and evidence boundaries reviewed for the reverse engineering and independent implementation of **ScamGraph AI (Smart Registry + Mule Intelligence + Graph Correlation Engine)**.

## Classification Taxonomy

Every architectural finding and capability in this project is classified using strict evidence labels:
- **`DOCUMENTED`**: Explicitly stated in public official documentation, whitepapers, press releases, or official project portals.
- **`OBSERVED`**: Directly observed through interaction with public interfaces, public documentation portals, or public metadata.
- **`INFERRED`**: A technical inference derived logically from known financial crime patterns, regulatory guidelines (RBI/I4C), or engineering necessities.
- **`PROPOSED`**: An explicit design and architectural decision implemented independently in ScamGraph AI.

---

## Public Sources Inventory

| Source ID | Source Title / Entity | URL | Reviewed Date | Documented Capabilities Supported | What it DOES NOT Establish (Evidence Limits) |
|---|---|---|---|---|---|
| **SRC-001** | Reserve Bank Innovation Hub (RBIH) Main Portal | `https://rbihub.in/` | October 2026 | Broad mission: Financial inclusion, digital payment security, fraud resilience, ecosystem collaboration. | Proprietary algorithms, model code, internal databases, specific API endpoints. |
| **SRC-002** | DPIP Project Overview | `https://rbihub.in/projects/digital-payments-intelligence-platform` | October 2026 | Purpose: National intelligence-sharing network and central repository of suspicious accounts/entities for digital transactions (UPI, IMPS, Wallets); inter-bank fraud intelligence sharing. | Database schemas, internal encryption keys, exact API request/response schemas, internal decision thresholds. |
| **SRC-003** | DPIP Public Documentation Portal | `https://docs.rbihub.in/digital-payments-intelligence-platform` | October 2026 | Core concepts: Smart Registry, identifier screening, feedback mechanism, dispute resolution, revocation workflow. | Production API keys, internal backend source code, production network topology, proprietary risk formulas. |
| **SRC-004** | MuleHunter Project Overview | `https://rbihub.in/projects/mulehunter` | October 2026 | Mule account risk detection; 19 behavioral patterns of mule accounts; multi-tier layering analysis; high reported accuracy (85%+); reducing false positives. | Internal model weights, feature parameter weights, production training dataset, proprietary neural/GBDT architecture. |
| **SRC-005** | MuleHunter Public Documentation Portal | `https://docs.rbihub.in/mule-hunter` | October 2026 | Integration with banking core, ingestion of account lifecycle & transaction metrics, real-time suspect registry integration (I4C coordination). | Bank-specific data schemas, live bank credentials, private endpoint paths. |
| **SRC-006** | RBIH Developer Documentation | `https://development.docs.rbihub.in/` | October 2026 | API development principles, authentication expectations (mutual TLS, API keys, HMAC signatures), sandbox environments. | Internal production secrets, private partner keys, proprietary backend implementations. |
| **SRC-007** | RBI Circulars & A.P. Hota Committee Recommendations | RBI Public Press Releases (2024-2026) | October 2026 | Recommendation for centralized Digital Payments Intelligence Platform (DPIP) and creation of IDPIC (Indian Digital Payments Intelligence Corporation) for systemic risk mitigation. | Software implementation details, code repositories. |
| **SRC-008** | Indian Cyber Crime Coordination Centre (I4C / Citizen Financial Cyber Fraud Reporting System - 1930) | MHA Public Cybercrime Portal (`cybercrime.gov.in`) | October 2026 | National Suspect Registry, lien-marking workflow, reporting of fraudulent bank accounts, mule SIM cards, and device IMEI indicators. | Live internal API contracts, internal case management database. |

---

## Evidence Boundary & Disclaimers

1. **Independent Implementation**: ScamGraph AI is an independent, clean-room implementation inspired by the publicly documented concepts and operational capabilities of RBIH DPIP and MuleHunter.
2. **No Proprietary Code/Weights**: This project does not contain, reproduce, or decompile proprietary RBIH source code, internal model weights, confidential schemas, private datasets, or production cryptographic keys.
3. **Synthetic Data Only**: All demo transactions, entity identifiers, bank account numbers, phone numbers, and VPAs used in tests and demonstrations are purely synthetic and follow standardized test formats.
4. **Transparent API Contracts**: All API endpoints implemented in ScamGraph AI are explicitly documented under the `/api/v1/` namespace and labeled as independent ScamGraph contracts.
