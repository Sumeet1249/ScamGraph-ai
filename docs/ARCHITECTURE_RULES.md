# ScamGraph AI — Architectural Constitution & Mandatory Rules

> **Status**: ACTIVE & BINDING  
> **Applies to**: All AI coding agents (Antigravity), contributors, and subagents working on this codebase.  
> **Core Mandate**: These 25 rules represent an inviolable architectural contract. AI agents and developers MUST NOT alter, bypass, or drift from these principles during implementation.

---

## 1. Architectural Sovereignty & Code Lineage

1. **ScamGraph owns its architecture.**  
   The system design is custom-built for UPI, banking, and digital wallet scam-journey correlation. Do not contort ScamGraph's architecture to mirror external generic fraud frameworks.

2. **External GitHub repositories are references, not the application architecture.**  
   External tools and academic repos exist purely for pattern reference, algorithm ideas, or benchmarking. They do not dictate our service boundaries, folder layouts, or storage choices.

3. **Never copy an entire external repository into production code.**  
   Do not vendor or dump foreign codebases into this repo. Adapt only minimal, necessary, well-understood algorithms with explicit project styling and typing.

4. **Check the license before adapting any source code.**  
   Strictly verify the license (e.g., MIT, Apache 2.0, BSD) of any external reference code before porting logic. GPL or restrictive copyleft code must NEVER be introduced without explicit approval.

5. **Record every external reference in `docs/REFERENCE_REPOS.md`.**  
   Any external repository, paper, dataset, or library consulted during development must be formally cataloged with its URL, license type, and purpose in [REFERENCE_REPOS.md](file:///s:/ScamGraph-AI/docs/REFERENCE_REPOS.md).

---

## 2. Security, Credential Management & Network Isolation

6. **Keep TinyFish credentials server-side.**  
   All calls to the TinyFish API must originate strictly from `services/investigation`. API keys and tokens must never be passed to or handled by the frontend.

7. **Never expose API keys to Next.js client code.**  
   Do not prefix backend secrets, database passwords, or third-party threat intelligence keys with `NEXT_PUBLIC_`. The web client communicates exclusively with our FastAPI gateway.

8. **Never fetch an untrusted user URL directly from the browser.**  
   Client browsers must never trigger direct client-side HTTP/DOM requests to suspicious URLs submitted for inspection (which could execute attacker scripts or trigger tracking beacons). Inspection is strictly a sandboxed server-side operation.

9. **URL processing must protect against SSRF and private/internal IP access.**  
   All backend URL extractors and web fetchers must explicitly disallow private, loopback, link-local, and reserved IP ranges (e.g., `127.0.0.1`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`, IPv6 equivalents, and local hostnames).

---

## 3. Evidence, Risk & Inference Integrity

10. **LLM output is evidence, never final truth.**  
    Outputs from Large Language Models or ML classifiers represent probabilistic observations. They are treated as evidence signals, never authoritative judicial or forensic verdicts.

11. **Risk and evidence confidence are separate values.**  
    Every assessment must maintain strict orthogonality between **Risk Level** (`LOW` / `MEDIUM` / `HIGH`) and **Evidence Confidence** (`LOW` / `MEDIUM` / `HIGH`). Never collapse them into a single opaque score.

12. **Every risk reason should have provenance.**  
    Every finding presented to the user or downstream systems must cite its exact origin: source model/rule, observed artifact, timestamp, raw evidence snippet, and detector confidence.

13. **The system must support `INSUFFICIENT_EVIDENCE`.**  
    When data is incomplete, ambiguous, or lacks corroboration across independent dimensions, the system MUST return `INSUFFICIENT_EVIDENCE`. Guessing or hallucinating a risk verdict is strictly prohibited.

14. **Never claim a payment is fraudulent solely from one signal.**  
    A single signal (e.g., high urgency in text alone, or a new domain alone) is insufficient to classify an interaction as fraudulent. Multi-signal corroboration across at least two independent dimensions is mandatory.

---

## 4. Privacy, Data Ethics & Synthetic Fixtures

15. **Cross-user demo data must be synthetic/pseudonymous.**  
    All demonstration incidents, phone numbers, VPAs, and chat excerpts must be synthetic or rigorously pseudonymized using cryptographic hashes.

16. **No real banking credentials, OTPs or private financial data.**  
    Never store, log, ingest, or mock real bank account numbers, debit/credit card CVVs, NetBanking passwords, or live OTPs.

---

## 5. Engineering Pragmatism, ML & Complexity Limits

17. **Pattern detection should begin deterministic/explainable.**  
    Start with transparent, explainable heuristic pattern matchers, state transition checks, and deterministic regex/lexical extractors before layering complex statistical models.

18. **GNNs are experimental and not required for MVP.**  
    Graph Neural Networks (GNNs) are non-blocking research experiments. The MVP must function reliably on Neo4j Cypher path queries, pgvector cosine similarity, and deterministic sequence correlation.

19. **New dependencies require justification.**  
    Do not casually add npm or pip packages. Every dependency introduces maintenance overhead and attack surface. Explain why standard library or existing tools cannot solve the problem first.

---

## 6. Resilience, Provider Fallbacks & Observability

20. **Every major service requires tests.**  
    API endpoints, graph traversal queries, evidence fusion rules, and URL parsers must have corresponding unit or integration tests in `tests/`.

21. **Every external API requires timeout and failure handling.**  
    External calls (including TinyFish API or DNS queries) must enforce tight timeouts (e.g., 2–4s), retry limits, and circuit breakers.

22. **The application must continue with partial evidence when one provider fails.**  
    If an external threat provider is unreachable or times out, the correlation pipeline must gracefully degrade, log the outage, and compute assessments on available signals with adjusted Evidence Confidence.

23. **Never silently fabricate threat-intelligence results.**  
    If a lookup fails or an API key is missing, return a clear `UNAVAILABLE` or `PROVIDER_ERROR` status. Never invent fake telemetry or mock green-checks silently.

24. **Simulation results must be clearly labeled as simulated.**  
    Any synthetic scenario, test journey, or mock collect request displayed in the UI or returned by the API must carry an explicit `is_simulated: true` flag and visual watermark.

25. **Keep the project runnable locally with documented commands.**  
    Local execution via Docker Compose (`postgres`, `neo4j`), FastAPI (`uvicorn`), and Next.js (`npm run dev`) must remain functional and reproducible without proprietary cloud requirements.

---

## 7. Definition of Done (DoD)

A feature or sub-component in ScamGraph AI is considered **DONE** only if:

1. **Implementation Exists**: Clean, typed, modular code implemented in the appropriate service directory without business logic leaks.
2. **API & Schema Documented**: Request/response contracts defined in Pydantic v2 and documented in OpenAPI / TypeScript types.
3. **Errors Handled**: Explicit exception boundaries, network timeouts, and fallback logic implemented for edge cases.
4. **Tests Exist**: Corresponding unit or integration tests written and passing in `tests/`.
5. **UI Handles All States**: Any corresponding frontend interface cleanly handles:
   - **Loading State** (skeletons / spinners)
   - **Error State** (actionable retry prompts, non-crashing boundaries)
   - **Empty State** (informative placeholders when no data is present)
6. **Evidence Provenance Retained**: Every signal, risk score, and graph node created or modified retains complete traceability back to raw inputs and source extractors.
