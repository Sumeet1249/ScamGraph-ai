# Multimodal Intelligence V2 — Architectural Overview

## 1. Executive Summary & Canonical Architecture
In real scam workflows, victims rarely submit clean structured text. Evidence arrives as WhatsApp/Telegram screenshots, UPI QR codes, Google Pay / PhonePe transaction receipts, voice notes, fake court orders or police notices, and phone call recordings.

The fundamental design rule of ScamGraph Multimodal Intelligence is:
**ONE INCIDENT. MANY EVIDENCE TYPES. ONE INTELLIGENCE GRAPH.**

Rather than creating disconnected silo scanners (a standalone screenshot scanner, a QR app, a voice deepfake detector), every supported modality ingests into canonical `Artifact` records, decomposes into typed `DerivedObservation` objects, and feeds directly into the unified ScamGraph intelligence pipeline:

```
                  USER INPUT
                      │
         ┌────────────┼────────────┐
         │            │            │
        TEXT        IMAGE        AUDIO
         │            │            │
         │      ┌─────┼─────┐      │
         │      │     │     │      │
         │     OCR   QR   VISUAL   │
         │      │     │   SIGNALS  │
         │      │     │            │
         │      └─────┼────────────┤
         │            │            │
         │       TRANSCRIPT        │
         │            │            │
         └────────────┼────────────┘
                      │
            CANONICAL OBSERVATIONS
                      │
            ENTITY / CLAIM / EVIDENCE
                      │
               TACTIC ENGINE
                      │
               JOURNEY ENGINE
                      │
                  SCAMDNA
                      │
               KNOWLEDGE GRAPH
                      │
                CORRELATION
                      │
                 CAMPAIGN
                      │
            UNIFIED ASSESSMENT
                      │
                INTERVENTION
                      │
          PROTECT / GUARD / RESCUE
```

## 2. Lineage, Independence & Double-Counting Prevention
A key failure mode of naive multimodal systems is double-counting dependent evidence.
- A single screenshot artifact produces an OCR observation and an extracted phone number. These share the same root artifact ID (`art_screenshot_1`) and are **not** independent sources.
- An independent QR code image encoding the same UPI VPA constitutes genuine cross-source corroboration.
- `EvidenceFusionEngine` models root lineage trees and evaluates independent source groups to compute calibrated confidence.
