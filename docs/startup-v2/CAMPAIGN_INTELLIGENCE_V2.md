# Campaign Intelligence V2 Architecture

## Executive Overview
In ScamGraph AI, a **Scam Campaign** is not merely a collection of messages with similar text or identical keywords. It represents a coordinated, multi-incident operational network supported by independent corroborated intelligence:
- **Shared or Rotating Infrastructure**: Phone numbers, domains, hosting providers, IP addresses.
- **Payment Destination Networks**: UPI VPAs, mule bank accounts, merchant aggregators.
- **Behavioral ScamDNA**: Cross-incident similarity across linguistic markers, urgency levers, and psychological manipulation tactics.
- **Scam Journey Stage Alignment**: Common multi-step progression sequences (e.g., Unsolicited Contact $\to$ Micro-Reward Trust $\to$ Telegram/WhatsApp Migration $\to$ Prepaid Deposit $\to$ Withdrawal Block).

---

## 1. Multi-Signal Campaign Object Model (`ScamCampaign`)

```
                          ┌─────────────────────────────┐
                          │         ScamCampaign        │
                          │        (schema v2.0)        │
                          └──────────────┬──────────────┘
                                         │
        ┌───────────────────┬────────────┴───────┬───────────────────┐
        ▼                   ▼                    ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌────────────────┐   ┌───────────────┐
│ Lifecycle &   │   │ Velocity &    │   │ Multi-Profile  │   │ Lineage &     │
│ Review State  │   │ Acceleration  │   │ Intelligence   │   │ Drift History │
├───────────────┤   ├───────────────┤   ├────────────────┤   ├───────────────┤
│ CANDIDATE     │   │ Current Vel.  │   │ Journey Profile│   │ Merged From   │
│ EMERGING      │   │ Baseline Vel. │   │ Tactic Profile │   │ Split From    │
│ ACTIVE        │   │ Growth Mult.  │   │ Infrastructure │   │ Superseded By │
│ SURGING       │   │ Acceleration  │   │ Payment VPAs   │   │ Active Drift  │
│ OUTBREAK      │   │ Dedup Filter  │   │ Regional Scope │   │ Mutations     │
│ RESURGING     │   │ Observed Time │   │ Languages      │   │ Parent Group  │
└───────────────┘   └───────────────┘   └────────────────┘   └───────────────┘
```

---

## 2. Core Operational Principles

1. **Same Scam Family $\neq$ Same Campaign**: Ten independent task scams represent ten distinct operations. Shared family classification (`TASK_SCAM`) alone is strictly insufficient to link incidents into a campaign without corroborated entity, infrastructure, or ScamDNA evidence.
2. **Ingestion Spike Resistance**: Velocity calculations evaluate actual occurrence time (`observed_at`), completely isolating bulk dataset ingestion from real-world outbreak detection.
3. **Duplicate Report Deduplication**: Near-duplicate and sybil report spikes are deduplicated before calculating report velocity.
4. **Resurgence Detection**: Campaigns dormant for $>30$ days that reappear with fresh incidents are flagged as `RESURGING`, retaining historical lineage.
5. **Privacy-Safe Consumer Alerts**: Consumer protection warning contracts return high-level advisories without exposing raw victim identifiers, internal Neo4j node IDs, or analyst notes.
