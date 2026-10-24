# COST ENGINEERING & FINANCIAL MODEL V3
**ScamGraph AI — Unit Economics & Scale Cost Analysis**
*Document Version: 4.0.0 | Date: 2026-10-24*

---

## 1. Unit Economics Summary

| Activity Class | Unit Cost (USD) | Primary Cost Driver | Optimization Applied |
| :--- | :--- | :--- | :--- |
| **Basic Text Check** | $0.0008 | Lightweight LLM token usage | Local regex/negation fast-path |
| **Screenshot OCR Check** | $0.0023 | Tesseract / Vision API CPU | Idempotent hash deduplication |
| **Voice / Audio Check** | $0.0068 | Whisper STT model runtime | Audio duration truncation (max 60s) |
| **Deep Investigation** | $0.0200 | TinyFish scraping probe | Multi-hop domain cache |
| **1,000 API Checks** | $1.80 | Aggregated cloud infrastructure | Keyset pagination & Redis caching |

---

## 2. Monthly Financial Projections by Scale Tier

```
                   [MONTHLY COST BREAKDOWN]
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Scale Tier   │ Infrastructure│ Third-Party  │ Total Cost   │
│              │ (Compute/DB) │ (AI/Vision)  │ (Monthly USD)│
├──────────────┼──────────────┼──────────────┼──────────────┤
│ 10K DAU      │ $340.00      │ $466.20      │ $806.20      │
│ 100K DAU     │ $1,170.00    │ $4,662.00    │ $5,832.00    │
│ 1M DAU       │ $6,000.00    │ $46,620.00   │ $52,620.00   │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

- **Cost per Active Consumer (10K DAU)**: ~$0.08 / month.
- **Cost per Active Consumer (100K DAU)**: ~$0.06 / month (scale efficiencies in fixed DB/compute).
- **Cost per Active Consumer (1M DAU)**: ~$0.05 / month.
