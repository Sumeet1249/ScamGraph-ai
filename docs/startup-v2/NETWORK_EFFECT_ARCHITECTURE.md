# Network Effect Architecture & Long-Term Flywheel (Phase 3B)

## 1. The ScamGraph Intelligence Flywheel

```
             ┌────────────────────────────────────────────────────────┐
             │                   MORE USERS / VICTIMS                 │
             └───────────────────────────┬────────────────────────────┘
                                         │ Reports & Ingestion
                                         ▼
             ┌────────────────────────────────────────────────────────┐
             │              MORE ENTITIES & EVIDENCE                  │
             │   (Rare UPIs, Phones, Telegram Handles, Phish Domains) │
             └───────────────────────────┬────────────────────────────┘
                                         │ Structural Graph Projection
                                         ▼
             ┌────────────────────────────────────────────────────────┐
             │              SCAMDNA V3 & JOURNEY STAGES               │
             │   (Multi-step manipulation & coercion sequence memory) │
             └───────────────────────────┬────────────────────────────┘
                                         │ Two-Stage Sub-linear Retrieval
                                         ▼
             ┌────────────────────────────────────────────────────────┐
             │       CROSS-INCIDENT CORRELATION & LINKING             │
             │   (Multi-signal relationship scoring, anti-collision)  │
             └───────────────────────────┬────────────────────────────┘
                                         │ Campaign Grouping (Prompt 12)
                                         ▼
             ┌────────────────────────────────────────────────────────┐
             │           EARLY WARNINGS & ACTIVE OUTBREAK RADAR       │
             │   (Warns User N+1 before payment occurs on known infra)│
             └───────────────────────────┬────────────────────────────┘
                                         │ Viral Consumer Utility
                                         ▼
             ┌────────────────────────────────────────────────────────┐
             │           MORE USERS TRUST & USE SCAMGRAPH             │
             └────────────────────────────────────────────────────────┘
```

---

## 2. Competitive Moat Analysis

A commodity LLM wrapper can only inspect a single message: *"Is this message suspicious?"*
ScamGraph answers a fundamentally different, defensible question:
*"Has this specific payment destination, contact infrastructure, or behavioral progression appeared across other victims in the network, how far has this interaction progressed, and what evidence connects them?"*

Even when an attacker swaps the phone number, wording, and domain, ScamGraph links the new incident through ScamDNA behavioral fingerprints and payment progression, generating preemptive warnings before money is transferred.
