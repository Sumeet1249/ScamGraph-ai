# Media Retention & Lifecycle Governance

## 1. Storage Tiers & Expiry Policies
Scam media files are subject to configurable retention policies governed by legal compliance and privacy standards:

| Artifact Modality | Retention Tier | Max Retention Period | Access Control |
| :--- | :--- | :--- | :--- |
| **Original Audio Recordings** | Sensitive Media | 30 Days (configurable) | Analyst Only (Pre-Signed URL) |
| **Original Screenshots** | Sensitive Media | 60 Days (configurable) | Analyst Only (Pre-Signed URL) |
| **Derived Transcripts** | Text Evidence | 180 Days | System + Authorized Analysts |
| **Derived OCR Text** | Text Evidence | 180 Days | System + Authorized Analysts |
| **Canonical Entities & DNA** | Intelligence Graph | Permanent (Pseudonymized) | Global Intelligence Pipeline |

## 2. Deletion Cascade Semantics
When a victim or tenant requests data erasure under data protection regulations (DPDP Act):
1. Original media blobs are hard-deleted from object storage.
2. Derived OCR and transcripts containing direct identifiers are pruned.
3. Graph relationships are anonymized (scrubbing personal references while preserving campaign-level aggregate structural patterns).
